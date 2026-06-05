# raceGPS 🏎️🌍

> **Real-world arcade racing.** Drive actual streets. Race your city. No simulators — just you, your car, and the real world rendered in 3D.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.6-blue.svg)](https://www.typescriptlang.org/)
[![MapLibre](https://img.shields.io/badge/MapLibre-GL%20JS-green.svg)](https://maplibre.org/)
[![Babylon.js](https://img.shields.io/badge/Babylon.js-7.x-orange.svg)](https://www.babylonjs.com/)

---

## What is raceGPS?

raceGPS is an **open-source, browser-based arcade racing game** built on top of real-world map data. Instead of fictional tracks, you race on actual city streets rendered in 3D from OpenStreetMap vector tiles and satellite imagery.

### Key Features

- 🗺️ **Real-world maps** — Drive actual roads, past real buildings, through real cities
- 🏎️ **Arcade physics** — Kinematic car model tuned for drift-friendly, fun handling
- 🎮 **Multiple game modes** — Cruise, Race, Challenge, Hot Pursuit, Explore
- 🌐 **Multiplayer** — WebSocket-powered rooms with live player positions
- 🏗️ **3D city rendering** — Extruded buildings, satellite ground, road networks
- ✨ **Neon visual style** — Dark, cinematic HUD with glowing effects
- 📱 **Mobile-friendly** — Adaptive quality tiers from low-end phones to desktop

---

## Architecture

```
raceGPS
├── apps/
│   └── web-client/          # Vite + TypeScript browser client
│       ├── src/
│       │   ├── main.ts      # Entry point, WebSocket, game loop
│       │   ├── arcade-car.ts # Kinematic car physics (no engine!)
│       │   └── styles.css   # Neon HUD styling
│       └── package.json
├── packages/
│   ├── renderer-3d-lite/    # MapLibre + Babylon.js 3D renderer
│   │   ├── src/
│   │   │   ├── map/         # MapLibre basemap, PMTiles, coords
│   │   │   ├── overlay/     # Babylon.js game layers
│   │   │   │   ├── cars/    # Car loading, driving, ghost
│   │   │   │   ├── env/     # Roads, buildings, satellite ground
│   │   │   │   ├── gameplay/# Pickups, tokens, collectibles
│   │   │   │   └── route/   # Route ribbons, checkpoint gates
│   │   │   ├── semantic/    # LOD rules, mode filters
│   │   │   └── realtime/    # Player interpolation
│   │   └── package.json
│   ├── map-adapters/        # Legacy map adapters (deprecated)
│   ├── protocol/            # Shared WebSocket message types
│   ├── race-engine/         # Server-side race logic
│   └── ui-kit/              # Shared CSS variables
├── backend/                 # Hono + Cloudflare Workers API
├── public/models/           # Kenney Car Kit GLB models (CC0)
└── package.json             # npm workspaces monorepo
```

### Renderer Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Basemap | MapLibre GL JS + OpenFreeMap | Dark vector tiles, 3D buildings, terrain |
| Data | PMTiles | Single-file city packs, fast range requests |
| Overlay | Babylon.js | Cars, pickups, checkpoints, particles, glow |
| Physics | Kinematic Arcade Car | No physics engine — pure fun math |
| Semantics | H3 hex cells | LOD, clustering, mode-based filtering |
| Network | WebSocket | 10–20 Hz player sync with client interpolation |

---

## Quick Start

### Prerequisites

- Node.js 20+
- npm 10+

### Install

```bash
git clone https://github.com/your-org/racegps.git
cd racegps
npm install
```

### Run the stack

```bash
# Terminal 1: Backend
npm run dev --workspace @racegps/backend

# Terminal 2: Web client
npm run dev --workspace @racegps/web-client
```

Open `http://localhost:5173` in your browser.

### Build for production

```bash
npm run build
```

---

## Game Modes

| Mode | Description |
|------|-------------|
| **Cruise** | Free roam, explore the city, meet other drivers |
| **Race** | Checkpoint-to-checkpoint racing with route ribbon |
| **Challenge** | Time trials, collectible tokens, score chasing |
| **Hot Pursuit** | Cops vs. runners with heat zones and extraction |
| **Explore** | Landmark discovery, scenic routes, photo mode |

---

## Car Models

raceGPS ships with the [Kenney Car Kit](https://kenney.nl/assets/car-kit) (CC0):

- Sedan Sports
- Race Car
- SUV
- Taxi
- Police
- Hatchback Sports

All models are low-poly (~1–5k triangles), GLB format, ready for web rendering.

---

## City Packs

City packs are JSON files containing:
- Road network (lat/lon polylines)
- Building footprints with heights
- Center point and bounding box

Load a city pack from the backend or drop a local JSON file.

---

## Performance Targets

| Metric | Target |
|--------|--------|
| Initial load | < 3s on broadband |
| Frame rate | 60 FPS desktop, 30–60 FPS mobile |
| Player markers | 50 per room (v0.1), 100+ with clustering |
| 3D objects | 200 lightweight objects max |
| Position updates | 10 Hz (cruise), 20 Hz (race) |

---

## Development

```bash
# Type-check everything
npm run typecheck

# Build all packages
npm run build

# Run tests
npm run test
```

---

## License

MIT — Free for personal and commercial use.

Car models by [Kenney](https://kenney.nl) (CC0). Map data © OpenStreetMap contributors.

---

## Roadmap

- [x] MapLibre + Babylon.js renderer foundation
- [x] Kinematic arcade car physics
- [x] GLB car loading with wheel animation
- [x] Procedural road/building meshes from citypack
- [x] Satellite tile ground
- [ ] Route ribbons + checkpoint gates
- [ ] Pickup objects + collectible system
- [ ] Ghost car replay
- [ ] Player interpolation + 3D markers
- [ ] PMTiles city pack streaming
- [ ] H3 semantic LOD
- [ ] Mobile quality tiers
- [ ] Cesium / Unreal premium client (future)
