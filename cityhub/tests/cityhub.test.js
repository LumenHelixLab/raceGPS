const { describe, it, before, after } = require('node:test');
const assert = require('node:assert');
const http = require('http');
const { app, server } = require('../server');

function request(method, path, body, headers = {}) {
  return new Promise((resolve, reject) => {
    const opts = {
      hostname: '127.0.0.1',
      port: server.address().port,
      path,
      method,
      headers: { 'Content-Type': 'application/json', ...headers }
    };
    const req = http.request(opts, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          resolve({ status: res.statusCode, headers: res.headers, body: JSON.parse(data) });
        } catch {
          resolve({ status: res.statusCode, headers: res.headers, body: data });
        }
      });
    });
    req.on('error', reject);
    if (body) req.write(typeof body === 'string' ? body : JSON.stringify(body));
    req.end();
  });
}

describe('CityHub Server', () => {
  before(() => {
    // server is already listening from server.js import
  });

  after(() => {
    server.close();
  });

  describe('Health', () => {
    it('should return ok', async () => {
      const res = await request('GET', '/health');
      assert.strictEqual(res.status, 200);
      assert.strictEqual(res.body.status, 'ok');
    });
  });

  describe('Cities', () => {
    it('should list cities', async () => {
      const res = await request('GET', '/api/cities');
      assert.strictEqual(res.status, 200);
      assert.ok(Array.isArray(res.body.data));
      assert.ok(res.body.data.length >= 2);
    });

    it('should paginate cities', async () => {
      const res = await request('GET', '/api/cities?page=1&limit=1');
      assert.strictEqual(res.status, 200);
      assert.strictEqual(res.body.limit, 1);
    });

    it('should get city detail', async () => {
      const res = await request('GET', '/api/cities/1');
      assert.strictEqual(res.status, 200);
      assert.ok(res.body.name);
    });

    it('should 404 for missing city', async () => {
      const res = await request('GET', '/api/cities/99999');
      assert.strictEqual(res.status, 404);
    });
  });

  describe('Routes', () => {
    it('should list routes for a city', async () => {
      const res = await request('GET', '/api/cities/1/routes');
      assert.strictEqual(res.status, 200);
      assert.ok(Array.isArray(res.body));
    });
  });

  describe('Leaderboard', () => {
    it('should get leaderboard', async () => {
      const res = await request('GET', '/api/routes/1/leaderboard');
      assert.strictEqual(res.status, 200);
      assert.ok(Array.isArray(res.body.entries));
    });

    it('should submit a lap', async () => {
      const res = await request('POST', '/api/routes/1/lap', {
        user_id: 1,
        lap_time: 55.5,
        drift_score: 2000,
        vehicle_id: 'sport_01'
      });
      assert.strictEqual(res.status, 201);
      assert.ok(typeof res.body.lap_time === 'number');
    });

    it('should reject invalid lap time', async () => {
      const res = await request('POST', '/api/routes/1/lap', {
        user_id: 1,
        lap_time: -5
      });
      assert.strictEqual(res.status, 400);
    });
  });

  describe('Rating', () => {
    it('should rate a city', async () => {
      const res = await request('POST', '/api/cities/1/rate', {
        user_id: 1,
        rating: 5
      });
      assert.strictEqual(res.status, 200);
      assert.strictEqual(res.body.rating, 5);
      assert.ok(typeof res.body.avg_rating === 'number');
    });

    it('should reject out-of-range rating', async () => {
      const res = await request('POST', '/api/cities/1/rate', {
        user_id: 1,
        rating: 6
      });
      assert.strictEqual(res.status, 400);
    });
  });

  describe('Challenge Flow', () => {
    it('should create a challenge', async () => {
      const res = await request('POST', '/api/routes/1/challenge', {
        challenger_id: 2
      });
      assert.strictEqual(res.status, 201);
      assert.strictEqual(res.body.status, 'pending');
    });
  });

  describe('User Profile', () => {
    it('should get profile with badges', async () => {
      const res = await request('GET', '/api/users/1/profile');
      assert.strictEqual(res.status, 200);
      assert.ok(Array.isArray(res.body.badges));
    });
  });

  describe('Feed', () => {
    it('should return discovery feed', async () => {
      const res = await request('GET', '/api/feed');
      assert.strictEqual(res.status, 200);
      assert.ok(Array.isArray(res.body.new_cities));
      assert.ok(Array.isArray(res.body.trending));
    });
  });

  describe('Events', () => {
    it('should get current event', async () => {
      const res = await request('GET', '/api/events/current');
      assert.strictEqual(res.status, 200);
      assert.ok(res.body.event);
    });

    it('should submit event score', async () => {
      const res = await request('POST', '/api/events/1/score', {
        user_id: 1,
        score: 1500
      });
      assert.strictEqual(res.status, 200);
      assert.strictEqual(res.body.score, 1500);
    });
  });

  describe('Validation', () => {
    it('should reject upload without file', async () => {
      // Can't easily test multipart without extra deps; test manifest validation via direct endpoint behavior
      const res = await request('POST', '/api/cities/upload', {});
      assert.strictEqual(res.status, 400);
    });
  });
});
