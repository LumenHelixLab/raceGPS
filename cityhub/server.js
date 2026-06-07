require('dotenv').config();
const express = require('express');
const helmet = require('helmet');
const cors = require('cors');
const rateLimit = require('express-rate-limit');
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const { db, initSchema, seedDemoData } = require('./lib/db');
const { validateManifest, validateZipEntries, validateFileSize } = require('./lib/validate');
const { generateFeed } = require('./lib/feed');

const PORT = parseInt(process.env.PORT, 10) || 7778;
const UPLOAD_DIR = process.env.UPLOAD_DIR || './uploads';

if (!fs.existsSync(UPLOAD_DIR)) {
  fs.mkdirSync(UPLOAD_DIR, { recursive: true });
}

initSchema();
seedDemoData();

const app = express();

app.use(helmet());
app.use(cors({ origin: true, credentials: true }));
app.use(express.json());
app.use('/uploads', express.static(path.resolve(UPLOAD_DIR)));

const uploadLimiter = rateLimit({
  windowMs: 60 * 60 * 1000,
  max: parseInt(process.env.RATE_LIMIT_UPLOAD, 10) || 1,
  standardHeaders: true,
  legacyHeaders: false,
  message: { error: 'Upload rate limit exceeded. Try again later.' }
});

const downloadLimiter = rateLimit({
  windowMs: 60 * 60 * 1000,
  max: parseInt(process.env.RATE_LIMIT_DOWNLOAD, 10) || 10,
  standardHeaders: true,
  legacyHeaders: false,
  message: { error: 'Download rate limit exceeded. Try again later.' }
});

const challengeLimiter = rateLimit({
  windowMs: 60 * 60 * 1000,
  max: parseInt(process.env.RATE_LIMIT_CHALLENGE, 10) || 3,
  standardHeaders: true,
  legacyHeaders: false,
  message: { error: 'Challenge rate limit exceeded. Try again later.' }
});

const storage = multer.diskStorage({
  destination: (_req, _file, cb) => cb(null, UPLOAD_DIR),
  filename: (_req, file, cb) => {
    const unique = Date.now() + '-' + Math.round(Math.random() * 1e9);
    cb(null, unique + path.extname(file.originalname));
  }
});

const upload = multer({
  storage,
  limits: { fileSize: 50 * 1024 * 1024 }
});

// Helper: update city avg_rating
function recalcCityRating(cityId) {
  const row = db.prepare('SELECT AVG(rating) as avg FROM ratings WHERE city_id = ?').get(cityId);
  const avg = row.avg ? Number(row.avg.toFixed(2)) : 0;
  db.prepare('UPDATE cities SET avg_rating = ? WHERE id = ?').run(avg, cityId);
  return avg;
}

// Helper: get local driver (most held routes in city)
function getLocalDriver(cityId) {
  const row = db.prepare(`
    SELECT o.user_id, u.username, COUNT(*) as route_count
    FROM ownership o
    JOIN routes r ON o.route_id = r.id
    JOIN users u ON o.user_id = u.id
    WHERE r.city_id = ? AND o.is_current = 1
    GROUP BY o.user_id
    ORDER BY route_count DESC
    LIMIT 1
  `).get(cityId);
  return row || null;
}

// --- Health ---
app.get('/health', (_req, res) => {
  res.json({ status: 'ok', uptime: process.uptime(), timestamp: new Date().toISOString() });
});

// --- Upload ---
app.post('/api/cities/upload', uploadLimiter, upload.single('file'), (req, res) => {
  try {
    if (!req.file) return res.status(400).json({ error: 'No file uploaded' });

    const sizeCheck = validateFileSize(req.file.size);
    if (!sizeCheck.valid) {
      fs.unlinkSync(req.file.path);
      return res.status(400).json({ error: sizeCheck.error });
    }

    // For server-side zip parsing we'd use adm-zip or similar; here we validate manifest from body
    let manifest = {};
    try {
      if (req.body.manifest) manifest = JSON.parse(req.body.manifest);
    } catch {
      fs.unlinkSync(req.file.path);
      return res.status(400).json({ error: 'Invalid manifest JSON' });
    }

    const manifestCheck = validateManifest(manifest);
    if (!manifestCheck.valid) {
      fs.unlinkSync(req.file.path);
      return res.status(400).json({ error: manifestCheck.error });
    }

    const uploaderId = req.body.uploader_id ? parseInt(req.body.uploader_id, 10) : 1;
    const now = new Date().toISOString();

    const result = db.prepare(`
      INSERT INTO cities (name, country, lat, lon, uploader_id, upload_date, file_path, manifest_json)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    `).run(
      manifest.name,
      manifest.country || 'Unknown',
      manifest.lat || 0,
      manifest.lon || 0,
      uploaderId,
      now,
      req.file.path,
      JSON.stringify(manifest)
    );

    const cityId = result.lastInsertRowid;

    if (Array.isArray(manifest.routes)) {
      const insertRoute = db.prepare(`
        INSERT INTO routes (city_id, name, start_lat, start_lon, end_lat, end_lon, length_km, creator_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
      `);
      for (const r of manifest.routes) {
        insertRoute.run(
          cityId,
          r.name || 'Unnamed Route',
          r.start_lat || 0,
          r.start_lon || 0,
          r.end_lat || 0,
          r.end_lon || 0,
          r.length_km || 0,
          uploaderId
        );
      }
    }

    db.prepare('UPDATE users SET total_uploads = total_uploads + 1 WHERE id = ?').run(uploaderId);

    res.status(201).json({ id: cityId, message: 'Citypack uploaded successfully' });
  } catch (err) {
    if (req.file && req.file.path && fs.existsSync(req.file.path)) {
      fs.unlinkSync(req.file.path);
    }
    res.status(500).json({ error: err.message });
  }
});

// --- List Cities ---
app.get('/api/cities', (req, res) => {
  const page = Math.max(1, parseInt(req.query.page, 10) || 1);
  const limit = Math.min(100, Math.max(1, parseInt(req.query.limit, 10) || 20));
  const offset = (page - 1) * limit;
  const sort = req.query.sort || 'trending';

  let orderBy = 'c.download_count DESC';
  if (sort === 'newest') orderBy = 'c.upload_date DESC';
  if (sort === 'top_rated') orderBy = 'c.avg_rating DESC';

  const rows = db.prepare(`
    SELECT c.*, u.username as uploader_name
    FROM cities c
    LEFT JOIN users u ON c.uploader_id = u.id
    ORDER BY ${orderBy}
    LIMIT ? OFFSET ?
  `).all(limit, offset);

  const total = db.prepare('SELECT COUNT(*) as c FROM cities').get().c;

  res.json({ data: rows, page, limit, total, pages: Math.ceil(total / limit) });
});

// --- City Detail ---
app.get('/api/cities/:id', (req, res) => {
  const id = parseInt(req.params.id, 10);
  const city = db.prepare(`
    SELECT c.*, u.username as uploader_name
    FROM cities c
    LEFT JOIN users u ON c.uploader_id = u.id
    WHERE c.id = ?
  `).get(id);
  if (!city) return res.status(404).json({ error: 'City not found' });

  city.local_driver = getLocalDriver(id);
  res.json(city);
});

// --- Download ---
app.get('/api/cities/:id/download', downloadLimiter, (req, res) => {
  const id = parseInt(req.params.id, 10);
  const city = db.prepare('SELECT file_path FROM cities WHERE id = ?').get(id);
  if (!city || !city.file_path || !fs.existsSync(city.file_path)) {
    return res.status(404).json({ error: 'Citypack not found' });
  }

  db.prepare('UPDATE cities SET download_count = download_count + 1 WHERE id = ?').run(id);
  res.download(city.file_path);
});

// --- Rate ---
app.post('/api/cities/:id/rate', (req, res) => {
  const cityId = parseInt(req.params.id, 10);
  const userId = req.body.user_id ? parseInt(req.body.user_id, 10) : 1;
  const rating = parseInt(req.body.rating, 10);

  if (!rating || rating < 1 || rating > 5) {
    return res.status(400).json({ error: 'Rating must be 1-5' });
  }

  const existing = db.prepare('SELECT id FROM ratings WHERE city_id = ? AND user_id = ?').get(cityId, userId);
  const now = new Date().toISOString();

  if (existing) {
    db.prepare('UPDATE ratings SET rating = ?, date = ? WHERE id = ?').run(rating, now, existing.id);
  } else {
    db.prepare('INSERT INTO ratings (city_id, user_id, rating, date) VALUES (?, ?, ?, ?)')
      .run(cityId, userId, rating, now);
  }

  const avg = recalcCityRating(cityId);
  res.json({ city_id: cityId, rating, avg_rating: avg });
});

// --- Routes in City ---
app.get('/api/cities/:id/routes', (req, res) => {
  const cityId = parseInt(req.params.id, 10);
  const rows = db.prepare(`
    SELECT r.*, u.username as creator_name
    FROM routes r
    LEFT JOIN users u ON r.creator_id = u.id
    WHERE r.city_id = ?
  `).all(cityId);
  res.json(rows);
});

// --- Submit Lap ---
app.post('/api/routes/:routeId/lap', (req, res) => {
  const routeId = parseInt(req.params.routeId, 10);
  const userId = req.body.user_id ? parseInt(req.body.user_id, 10) : 1;
  const lapTime = parseFloat(req.body.lap_time);
  const driftScore = parseFloat(req.body.drift_score || 0);
  const vehicleId = req.body.vehicle_id || 'default';

  if (isNaN(lapTime) || lapTime <= 0) {
    return res.status(400).json({ error: 'Invalid lap_time' });
  }

  const now = new Date().toISOString();
  db.prepare(`
    INSERT INTO leaderboards (route_id, user_id, lap_time, drift_score, vehicle_id, date)
    VALUES (?, ?, ?, ?, ?, ?)
  `).run(routeId, userId, lapTime, driftScore, vehicleId, now);

  // Update total races
  db.prepare('UPDATE users SET total_races = total_races + 1 WHERE id = ?').run(userId);

  // Update city race count
  const route = db.prepare('SELECT city_id FROM routes WHERE id = ?').get(routeId);
  if (route) {
    db.prepare('UPDATE cities SET race_count = race_count + 1 WHERE id = ?').run(route.city_id);
  }

  // Check if new Route King
  const best = db.prepare(`
    SELECT user_id, MIN(lap_time) as best_time
    FROM leaderboards
    WHERE route_id = ?
  `).get(routeId);

  if (best && best.user_id === userId) {
    const current = db.prepare('SELECT user_id FROM ownership WHERE route_id = ? AND is_current = 1').get(routeId);
    if (!current || current.user_id !== userId) {
      db.prepare('UPDATE ownership SET is_current = 0, held_for_seconds = ? WHERE route_id = ? AND is_current = 1')
        .run(Math.floor(Date.now() / 1000), routeId);
      db.prepare('INSERT INTO ownership (route_id, user_id, acquired_at, is_current) VALUES (?, ?, ?, 1)')
        .run(routeId, userId, now);
      db.prepare('UPDATE users SET total_wins = total_wins + 1 WHERE id = ?').run(userId);
    }
  }

  res.status(201).json({ route_id: routeId, lap_time: lapTime, is_king: best && best.user_id === userId });
});

// --- Leaderboard ---
app.get('/api/routes/:routeId/leaderboard', (req, res) => {
  const routeId = parseInt(req.params.routeId, 10);
  const rows = db.prepare(`
    SELECT l.*, u.username
    FROM leaderboards l
    JOIN users u ON l.user_id = u.id
    WHERE l.route_id = ?
    ORDER BY l.lap_time ASC
    LIMIT 100
  `).all(routeId);

  const king = db.prepare(`
    SELECT o.*, u.username
    FROM ownership o
    JOIN users u ON o.user_id = u.id
    WHERE o.route_id = ? AND o.is_current = 1
  `).get(routeId);

  res.json({ route_id: routeId, king, entries: rows });
});

// --- Challenge ---
app.post('/api/routes/:routeId/challenge', challengeLimiter, (req, res) => {
  const routeId = parseInt(req.params.routeId, 10);
  const challengerId = req.body.challenger_id ? parseInt(req.body.challenger_id, 10) : 1;

  const current = db.prepare('SELECT user_id FROM ownership WHERE route_id = ? AND is_current = 1').get(routeId);
  if (!current) {
    return res.status(404).json({ error: 'No current Route King for this route' });
  }

  const now = new Date().toISOString();
  const result = db.prepare(`
    INSERT INTO challenges (route_id, challenger_id, defender_id, status, date)
    VALUES (?, ?, ?, 'pending', ?)
  `).run(routeId, challengerId, current.user_id, now);

  res.status(201).json({ id: result.lastInsertRowid, route_id: routeId, challenger_id: challengerId, defender_id: current.user_id, status: 'pending' });
});

// --- User Profile ---
app.get('/api/users/:id/profile', (req, res) => {
  const userId = parseInt(req.params.id, 10);
  const user = db.prepare('SELECT * FROM users WHERE id = ?').get(userId);
  if (!user) return res.status(404).json({ error: 'User not found' });

  // Compute badges
  const badges = [];
  if (user.total_uploads >= 1) badges.push('city_builder');
  if (user.total_uploads >= 5) badges.push('metropolis');
  if (user.total_races >= 10) badges.push('road_warrior');
  if (user.total_wins >= 1) badges.push('route_king');
  if (user.total_wins >= 10) badges.push('dynasty');

  const heldRoutes = db.prepare(`
    SELECT r.*, c.name as city_name
    FROM ownership o
    JOIN routes r ON o.route_id = r.id
    JOIN cities c ON r.city_id = c.id
    WHERE o.user_id = ? AND o.is_current = 1
  `).all(userId);

  res.json({ ...user, badges, held_routes: heldRoutes });
});

// --- Feed ---
app.get('/api/feed', (req, res) => {
  const type = req.query.type || 'all';
  const limit = Math.min(50, parseInt(req.query.limit, 10) || 10);
  res.json(generateFeed(type, limit));
});

// --- Current Event ---
app.get('/api/events/current', (_req, res) => {
  const event = db.prepare(`
    SELECT e.*, c.name as city_name
    FROM events e
    JOIN cities c ON e.city_id = c.id
    WHERE e.is_current = 1
    ORDER BY e.start_date DESC
    LIMIT 1
  `).get();

  if (!event) return res.json({ event: null, leaderboard: [] });

  const scores = db.prepare(`
    SELECT es.*, u.username
    FROM event_scores es
    JOIN users u ON es.user_id = u.id
    WHERE es.event_id = ?
    ORDER BY es.score DESC
    LIMIT 50
  `).all(event.id);

  res.json({ event, leaderboard: scores });
});

// --- Submit Event Score ---
app.post('/api/events/:eventId/score', (req, res) => {
  const eventId = parseInt(req.params.eventId, 10);
  const userId = req.body.user_id ? parseInt(req.body.user_id, 10) : 1;
  const score = parseInt(req.body.score, 10);

  if (isNaN(score)) {
    return res.status(400).json({ error: 'Invalid score' });
  }

  const event = db.prepare('SELECT id FROM events WHERE id = ? AND is_current = 1').get(eventId);
  if (!event) return res.status(404).json({ error: 'Event not found or ended' });

  const now = new Date().toISOString();
  const existing = db.prepare('SELECT id, score FROM event_scores WHERE event_id = ? AND user_id = ?').get(eventId, userId);

  if (existing) {
    if (score > existing.score) {
      db.prepare('UPDATE event_scores SET score = ?, date = ? WHERE id = ?').run(score, now, existing.id);
    }
  } else {
    db.prepare('INSERT INTO event_scores (event_id, user_id, score, date) VALUES (?, ?, ?, ?)')
      .run(eventId, userId, score, now);
  }

  res.json({ event_id: eventId, user_id: userId, score });
});

app.use((err, _req, res, _next) => {
  console.error(err);
  res.status(500).json({ error: err.message || 'Internal server error' });
});

const server = app.listen(PORT, () => {
  console.log(`CityHub Server listening on port ${PORT}`);
});

module.exports = { app, server, db };
