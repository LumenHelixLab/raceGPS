const { db } = require('./db');

function getNewCities(limit = 10) {
  const since = new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString();
  return db.prepare(`
    SELECT c.*, u.username as uploader_name
    FROM cities c
    LEFT JOIN users u ON c.uploader_id = u.id
    WHERE c.upload_date > ?
    ORDER BY c.upload_date DESC
    LIMIT ?
  `).all(since, limit);
}

function getTrendingCities(limit = 10) {
  const since = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString();
  return db.prepare(`
    SELECT c.*, u.username as uploader_name
    FROM cities c
    LEFT JOIN users u ON c.uploader_id = u.id
    WHERE c.upload_date > ?
    ORDER BY c.download_count DESC, c.race_count DESC
    LIMIT ?
  `).all(since, limit);
}

function getTopRatedCities(limit = 10) {
  return db.prepare(`
    SELECT c.*, u.username as uploader_name
    FROM cities c
    LEFT JOIN users u ON c.uploader_id = u.id
    WHERE c.avg_rating > 0
    ORDER BY c.avg_rating DESC, c.race_count DESC
    LIMIT ?
  `).all(limit);
}

function getRecentKingChanges(limit = 10) {
  return db.prepare(`
    SELECT o.*, r.name as route_name, r.city_id,
           u.username as king_name, c.name as city_name
    FROM ownership o
    JOIN routes r ON o.route_id = r.id
    JOIN users u ON o.user_id = u.id
    JOIN cities c ON r.city_id = c.id
    WHERE o.is_current = 1
    ORDER BY o.acquired_at DESC
    LIMIT ?
  `).all(limit);
}

function getCurrentChampions(limit = 10) {
  return db.prepare(`
    SELECT cc.*, u.username as champion_name, c.name as city_name
    FROM city_champions cc
    JOIN users u ON cc.user_id = u.id
    JOIN cities c ON cc.city_id = c.id
    WHERE cc.is_current = 1
    ORDER BY cc.points DESC
    LIMIT ?
  `).all(limit);
}

function generateFeed(type = 'all', limit = 10) {
  const feed = {};
  if (type === 'all' || type === 'new') {
    feed.new_cities = getNewCities(limit);
  }
  if (type === 'all' || type === 'trending') {
    feed.trending = getTrendingCities(limit);
  }
  if (type === 'all' || type === 'top_rated') {
    feed.top_rated = getTopRatedCities(limit);
  }
  if (type === 'all' || type === 'kings') {
    feed.recent_kings = getRecentKingChanges(limit);
  }
  if (type === 'all' || type === 'champions') {
    feed.current_champions = getCurrentChampions(limit);
  }
  return feed;
}

module.exports = {
  getNewCities,
  getTrendingCities,
  getTopRatedCities,
  getRecentKingChanges,
  getCurrentChampions,
  generateFeed
};
