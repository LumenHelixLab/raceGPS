const Database = require('better-sqlite3');
const path = require('path');

const DB_PATH = process.env.DB_PATH || './cityhub.db';
const db = new Database(DB_PATH);

db.pragma('journal_mode = WAL');
db.pragma('foreign_keys = ON');

function initSchema() {
  db.exec(`
    CREATE TABLE IF NOT EXISTS users (
      id INTEGER PRIMARY KEY,
      username TEXT UNIQUE,
      email TEXT,
      created_at TEXT,
      total_uploads INTEGER DEFAULT 0,
      total_races INTEGER DEFAULT 0,
      total_wins INTEGER DEFAULT 0
    );

    CREATE TABLE IF NOT EXISTS cities (
      id INTEGER PRIMARY KEY,
      name TEXT,
      country TEXT,
      lat REAL,
      lon REAL,
      uploader_id INTEGER,
      upload_date TEXT,
      download_count INTEGER DEFAULT 0,
      race_count INTEGER DEFAULT 0,
      avg_rating REAL DEFAULT 0,
      file_path TEXT,
      manifest_json TEXT
    );

    CREATE TABLE IF NOT EXISTS routes (
      id INTEGER PRIMARY KEY,
      city_id INTEGER,
      name TEXT,
      start_lat REAL,
      start_lon REAL,
      end_lat REAL,
      end_lon REAL,
      length_km REAL,
      creator_id INTEGER
    );

    CREATE TABLE IF NOT EXISTS ownership (
      id INTEGER PRIMARY KEY,
      route_id INTEGER,
      user_id INTEGER,
      acquired_at TEXT,
      held_for_seconds INTEGER DEFAULT 0,
      is_current INTEGER DEFAULT 1
    );

    CREATE TABLE IF NOT EXISTS leaderboards (
      id INTEGER PRIMARY KEY,
      route_id INTEGER,
      user_id INTEGER,
      lap_time REAL,
      drift_score REAL,
      vehicle_id TEXT,
      date TEXT
    );

    CREATE TABLE IF NOT EXISTS city_champions (
      id INTEGER PRIMARY KEY,
      city_id INTEGER,
      user_id INTEGER,
      week_start TEXT,
      points INTEGER DEFAULT 0,
      is_current INTEGER DEFAULT 1
    );

    CREATE TABLE IF NOT EXISTS ratings (
      id INTEGER PRIMARY KEY,
      city_id INTEGER,
      user_id INTEGER,
      rating INTEGER,
      date TEXT
    );

    CREATE TABLE IF NOT EXISTS challenges (
      id INTEGER PRIMARY KEY,
      route_id INTEGER,
      challenger_id INTEGER,
      defender_id INTEGER,
      status TEXT,
      date TEXT
    );

    CREATE TABLE IF NOT EXISTS events (
      id INTEGER PRIMARY KEY,
      name TEXT,
      city_id INTEGER,
      start_date TEXT,
      end_date TEXT,
      is_current INTEGER DEFAULT 1
    );

    CREATE TABLE IF NOT EXISTS event_scores (
      id INTEGER PRIMARY KEY,
      event_id INTEGER,
      user_id INTEGER,
      score INTEGER DEFAULT 0,
      date TEXT
    );
  `);
}

function seedDemoData() {
  const userCount = db.prepare('SELECT COUNT(*) as c FROM users').get().c;
  if (userCount > 0) return;

  const now = new Date().toISOString();
  const yesterday = new Date(Date.now() - 86400000).toISOString();
  const lastWeek = new Date(Date.now() - 7 * 86400000).toISOString();

  const insertUser = db.prepare('INSERT INTO users (username, email, created_at) VALUES (?, ?, ?)');
  const u1 = insertUser.run('SpeedDemon', 'speed@racegps.local', now).lastInsertRowid;
  const u2 = insertUser.run('DriftKing', 'dk@racegps.local', lastWeek).lastInsertRowid;

  const insertCity = db.prepare(`
    INSERT INTO cities (name, country, lat, lon, uploader_id, upload_date, download_count, race_count, avg_rating, file_path, manifest_json)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
  `);
  const c1 = insertCity.run('Akron', 'USA', 41.08, -81.52, u1, now, 42, 120, 4.5, 'uploads/akron.zip', '{"version":"1.0"}').lastInsertRowid;
  const c2 = insertCity.run('Kyoto', 'Japan', 35.01, 135.76, u2, yesterday, 128, 340, 4.8, 'uploads/kyoto.zip', '{"version":"1.0"}').lastInsertRowid;

  const insertRoute = db.prepare(`
    INSERT INTO routes (city_id, name, start_lat, start_lon, end_lat, end_lon, length_km, creator_id)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
  `);
  const r1 = insertRoute.run(c1, 'Highland Sweep', 41.08, -81.52, 41.09, -81.51, 3.2, u1).lastInsertRowid;
  const r2 = insertRoute.run(c2, 'Gion Drift', 35.01, 135.76, 35.02, 135.77, 2.8, u2).lastInsertRowid;

  db.prepare('INSERT INTO ownership (route_id, user_id, acquired_at, is_current) VALUES (?, ?, ?, 1)').run(r1, u1, now);
  db.prepare('INSERT INTO ownership (route_id, user_id, acquired_at, is_current) VALUES (?, ?, ?, 1)').run(r2, u2, now);

  db.prepare('INSERT INTO leaderboards (route_id, user_id, lap_time, drift_score, vehicle_id, date) VALUES (?, ?, ?, ?, ?, ?)')
    .run(r1, u1, 62.45, 1200, 'sport_01', now);
  db.prepare('INSERT INTO leaderboards (route_id, user_id, lap_time, drift_score, vehicle_id, date) VALUES (?, ?, ?, ?, ?, ?)')
    .run(r2, u2, 58.12, 3400, 'drift_02', now);

  db.prepare('INSERT INTO city_champions (city_id, user_id, week_start, points, is_current) VALUES (?, ?, ?, ?, 1)')
    .run(c1, u1, lastWeek, 450);
  db.prepare('INSERT INTO city_champions (city_id, user_id, week_start, points, is_current) VALUES (?, ?, ?, ?, 1)')
    .run(c2, u2, lastWeek, 620);

  db.prepare('INSERT INTO events (name, city_id, start_date, end_date, is_current) VALUES (?, ?, ?, ?, 1)')
    .run('Akron Takeover', c1, now, new Date(Date.now() + 7 * 86400000).toISOString());
}

module.exports = {
  db,
  initSchema,
  seedDemoData
};
