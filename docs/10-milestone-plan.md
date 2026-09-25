# raceGPS — 10-Milestone Plan: Professional Racing Sim

**Status:** APPROVED by owner 2026-09-23. Supersedes sprint-by-sprint planning as the program north star.
**Methodology sources:** CARLA (OpenDRIVE canonical road model, Digital Twin OSM pipeline, TrafficManager, content attribution discipline), MathWorks RoadRunner (semantic road authoring), SUMO (microscopic traffic), Epic Chaos Vehicles + Vehicle Template, Unreal-CommonVehicle, ue5-ai-traffic.

## Core doctrine

1. **OpenDRIVE is the road truth.** Routes, traffic, spawns, and road meshes all derive from the lane-level road model — never ad-hoc geometry (CARLA method).
2. **Pixel-proven or it didn't happen.** Every milestone is gated by the runtime preflight + diagnostics + screenshot pipeline built during the black-screen campaign (Sprint 2).
3. **Real world, real scale.** 1 uu = 1 cm, Z-up, geo-true cities from OSM. No toy worlds.
4. **Attribution discipline.** CC-BY/CC0 assets only, attribution files committed (CARLA content model).

## Current baseline (end of Sprint 2)

- Universal city compiler: OSM → citypack (roads, closed-loop routes, water, buildings, POIs, heightmap, spawns); 234 tests green; CI citypack-qa job
- Headless UE5.7 baking: terrain, 120k/31k building instances (CLE/AKR), water, gates, splines, lighting rigs; real scale
- CARLA Dodge Charger hero (CC-BY 4.0), Chaos physics, arcade handling presets
- Runtime diagnostics: `[raceGPS-PREFLIGHT]` + `[raceGPS-DIAG]` + auto-screenshot + ShowFlag bisect
- Known gaps: no road ribbons (drive on terrain), flat building materials, spawn points not road-snapped, runtime BuildingMeshGenerator schema mismatch, no traffic, LAN hardcoded map, CARLA material deps missing

## Milestones

### M1 — Real Roads 🔴
Bake drivable asphalt ribbons from the road graph (lane-accurate from XODR), road-snapped spawn points, lane markings. Roads come from the lane model, not the terrain.
**Done when:** in-game screenshot shows marked asphalt under the car at every spawn; spawn rooftop incident class eliminated; validator asserts spawn-on-road.

### M2 — Visual Pass 1
Building materials by type (brick/glass/concrete buckets exist), CARLA material dependency repair, sidewalks/curbs, street furniture from compiled data.
**Done when:** downtown Cleveland reads as downtown in a screenshot; zero default-checkerboard surfaces in the play space.

### M3 — Handling & Input
Chaos tuning pass (suspension, tires, aero), Enhanced Input migration, gamepad + wheel/FFB, cockpit/hood/chase cams. CommonVehicle patterns (clutch, gears, engine state).
**Done when:** three handling presets (Arcade/Simcade/Sim) feel measurably distinct; wheel + pedals drive the car.

### M4 — The Race Loop
HUD (speed/gear/lap/delta/minimap from road graph), start lights, results, best-lap persistence, ghost polish.
**Done when:** a complete race runs start→finish→results with persisted records.

### M5 — Living Traffic
MassEntity staggered traffic (Sprint-2 T9 carry-over), lane-following AI on the road graph, OSM traffic signals, edge-of-world spawn/destroy lifecycle.
**Done when:** Cleveland streets have believable traffic at 60fps.

### M6 — Runtime Repair
Fix BuildingMeshGenerator schema mismatch (runtime spawning = bake parity), remove deprecated legacy paths, LANSessionManager map fix.
**Done when:** runtime-spawned city === baked city; one pipeline, no doubles.

### M7 — Performance Envelope
World Partition streaming for 10km+ cities, HLOD skylines, CI perf budget gate, shader-cache warmup.
**Done when:** 60fps on target hardware profile across both cities, measured not guessed.

### M8 — World Atmosphere
Day/night cycle (fix DayNightCycle 2.5-lux bug found in S2), CARLA-style weather presets, wet-asphalt physics materials.
**Done when:** same race, four moods — dawn/noon/dusk/night + rain that changes grip.

### M9 — Multiplayer & Competition
Flash-to-Challenge backend, LAN ServerTravel fix, online leaderboards, async player ghosts.
**Done when:** two players race the same Cleveland loop and see each other's times.

### M10 — Ship It
Cooked Shipping pipeline, installer, crash reporting, opt-in telemetry, player docs.
**Done when:** a friend can install and race without this repo.

## Sequencing

M1→M2→M3: "feels like a real racing game." M4: "is a game." M5/M8: alive. M6/M7: engineering scale. M9/M10: product.

## Governance

- Each milestone = one sprint branch (`sprint/mN-*`), orchestrated AI swarm, owner approves merges
- Dashboard (Sprint Command Center) tracks milestone status; sprint_status.py is the collector
- Every merge gate: 234+ tests green, 0 ensures, pixel-proven screenshot evidence, readiness PASSED both cities
