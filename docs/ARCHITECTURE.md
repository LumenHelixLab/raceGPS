# Architecture

raceGPS is a modular multiplayer world layer.

```text
Cookies handle identity.
WebSockets handle the world.
Database handles memory.
Adapters handle maps.
```

## Layers

1. **Identity Layer** — cookie/session for web, token-based auth later for mobile/Unreal.
2. **Realtime Layer** — WebSocket rooms for positions, chat, signals, checkpoints, pickups, captures.
3. **World Layer** — global passport, world cells, city rooms, room discovery, leaderboards.
4. **Gameplay Layer** — cruise, race, challenge, hot pursuit, explore.
5. **Map Adapter Layer** — provider-independent rendering and geospatial operations.
6. **Client Layer** — web-first now, mobile and Unreal later.
