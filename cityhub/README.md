# CityHub Server

Lightweight Node.js/Express backend for the raceGPS viral citypack system.

## Setup

```bash
cd cityhub
npm install
cp .env.example .env
npm start
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `7778` | Server port |
| `DB_PATH` | `./cityhub.db` | SQLite database path |
| `UPLOAD_DIR` | `./uploads` | Citypack upload directory |
| `RATE_LIMIT_UPLOAD` | `1` | Uploads per hour |
| `RATE_LIMIT_DOWNLOAD` | `10` | Downloads per hour |
| `RATE_LIMIT_CHALLENGE` | `3` | Challenges per hour |

## API Endpoints

### Cities

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/cities/upload` | Upload citypack `.zip` |
| `GET` | `/api/cities` | List cities (paginated) |
| `GET` | `/api/cities/:id` | City detail + Local Driver |
| `GET` | `/api/cities/:id/download` | Download citypack `.zip` |
| `POST` | `/api/cities/:id/rate` | Rate city 1–5 stars |
| `GET` | `/api/cities/:id/routes` | List routes in city |

### Routes & Leaderboards

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/routes/:routeId/lap` | Submit lap time |
| `GET` | `/api/routes/:routeId/leaderboard` | Get leaderboard |
| `POST` | `/api/routes/:routeId/challenge` | Challenge Route King |

### Users & Feed

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/users/:id/profile` | User profile + badges |
| `GET` | `/api/feed` | Discovery feed |
| `GET` | `/api/events/current` | Current City Takeover event |
| `POST` | `/api/events/:eventId/score` | Submit event score |

### Health

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |

## Query Parameters

### `GET /api/cities`

- `page` — page number (default: 1)
- `limit` — items per page (default: 20)
- `sort` — `trending` | `newest` | `top_rated` (default: `trending`)

### `GET /api/feed`

- `type` — `new` | `trending` | `kings` | `champions` | `all` (default: `all`)
- `limit` — items per section (default: 10)

## Rate Limits

- **Upload**: 1 per hour
- **Download**: 10 per hour
- **Challenge**: 3 per hour

## License

MIT — free and open source forever. No monetization.
