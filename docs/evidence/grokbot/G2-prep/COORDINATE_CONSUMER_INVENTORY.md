# G2 Prep — Coordinate / Transform Consumer Inventory

**Status:** READ-ONLY analysis (no C++/uasset edits, no Unreal build, no git commit)  
**Repo:** `C:\projects\racegps`  
**Branch / commit:** `feature/cleveland-showcase-demo` @ `f2a8ecd6c8112141e5297ec2cce640ab42db4014`  
**Machine:** omni (`14689435-c6b8-4643-bec2-a7b74d7e5dae`)  
**Date:** 2026-09-07 (America/New_York)

---

## 1. Inventory table (consumers)

| # | Path | Role | Assumes (axis / units / origin) |
|---|------|------|----------------------------------|
| 1 | `apps/unreal-akron-beta/Source/raceGPSAkronBeta/Private/AkronXodrImporter.cpp` (+ `.h`) | Canonical importer: GeoToWorld, XodrToWorld, manifest/XODR/road-graph/routes/spawns/POIs | **UE Z-up cm:** X=east, Y=north, Z=up; MetersToUU=100; origin from manifest/+lat_0/+lon_0 (default Akron 41.08,-81.52); lat m/deg=**110540**; lon m/deg=111320*cos(lat). Spawns/routes pack raw geo as FVector(lon, 0, -lat) |
| 2 | `.../Private/RacingLineComponent.cpp` (+ `.h`) | Cleveland racing line load + GeoToWorld + poses along S | **UE Z-up cm:** X=east, Y=north; lat m/deg=**111320** (differs from importer); origin from JSON or first sample; s meters auto-x100 if max S < 50000; curvature 1/m; lateral offset **cm** |
| 3 | `.../Private/ClevelandEnvironmentActor.cpp` (+ `.h`) | Water, barriers, cones, hangars, skyline, dressing via GeoToWorld | Same as RacingLine GeoToWorld; origin defaults Burke **41.51722, -81.68306**; *_m -> x100 to cm; yaw_deg/heading_deg applied as UE yaw in XY; Cesium height note meters AMSL/ellipsoid |
| 4 | `.../Public/ClevelandShowcaseTypes.h` | CTE/steering/progress types | WorldPos Z-up cm; CTE stored cm, steering law wants **meters** (/100); curvature 1/m; heading error rad in XY Z-up |
| 5 | `.../Private/ClevelandShowcaseGameMode.cpp` | Grid, intro camera, checkpoints on racing line | RacingLine poses (cm Z-up); checkpoint s meter->cm promote; camera offsets in world cm; comments: X=east Y=north, downtown -Y (south) |
| 6 | `.../Private/RaceGridManager.cpp` | Spawn grid along racing line | Slot spacing / stagger **cm**; poses from GetPoseAtS (tangent -> UE rotator) |
| 7 | `.../Private/CruiseSprintGameMode.cpp` | Legacy Akron cruise: load city, spawn player/route/ghost | Manifest origin -> WorldOrigin; spawn/waypoints: Lat=-Location.Z, Lon=Location.X then UAkronXodrImporter::GeoToWorld; notes furniture hard-Akron + legacy meter path |
| 8 | `.../Private/RoadMeshGenerator.cpp` | Road ribbon from XODR/graph WorldPoints | Already-converted world pts; WidthMeters * MetersToUU -> half-width **cm** |
| 9 | `.../Private/TrafficSpawner.cpp` | Traffic on XODR WorldPoints | World cm points; SpawnRadius vs UU distance |
| 10 | `.../Private/BuildingMeshGenerator.cpp` (+ `.h`) | Runtime building meshes from JSON | Footprint {x,y} used **as UU directly**; height as Z; default height 8.0 (meter-ish); AddWorldBoxBuilding labeled HeightCm — **mixed / no x100 on JSON path** |
| 11 | `.../Private/StreetFurnitureSpawner.cpp` (+ `.h`) | Intersections -> furniture | **Hardcoded Akron** origin (-81.52, 41.08); output **meters** (no x100); X=east Y=north Z=0; SpawnRadius=2000 |
| 12 | `.../Private/CheckpointGate.cpp` (+ `.h`) | Gate visuals / overlap | Defaults GateWidth=**1600**, GateHeight=**400** -> **cm** (16m x 4m); Z-up |
| 13 | `.../Private/MinimapWidget.cpp` (+ `.h`) | World->minimap | Rotates XY by player yaw; MinimapRadiusMeters=500 but deltas are actor locations (**cm** if GeoToWorld) -> **scale mismatch risk** |
| 14 | `.../Private/MinimapRenderer.cpp` | Top-down RT camera | Looks down; rotates with player yaw (Z-up world) |
| 15 | `.../Private/RuntimeCityLoader.cpp` | Experimental level-spec style spawn | StreamChunk RadiusMeters vs FVector::Distance (UU); expects level-spec {x,y,z} |
| 16 | `.../Private/PreflightSystem.cpp` | Pack file existence | Paths only; historically Akron-hardcoded filenames |
| 17 | `.../CLEVELAND_CPP_WIREUP.md`, `CLEVELAND_ENV_WIREUP.md` | Authoritative comments | Z-up, 1uu=1cm, X=east Y=north; racing_line s promote |
| 18 | `tools/generate-level-spec.py` | Manifest/routes/spawns -> LevelSpec JSON | Claims matches C++ GeoToWorld but emits **meters**, **X=east, Z=-north, Y=0** — **does NOT match current C++ Z-up cm** |
| 19 | `tools/ue5-import-level-spec.py` | Bake LevelSpec actors into map | _spec_to_ue: (x,y,z)_m -> (x,-z,y)*100 cm Z-up; reconciles legacy spec frame to UE |
| 20 | `tools/ue5-city-import-prep.py` | Citypack -> *_ueimport.json | Equirect to **UE meters** X=east Y=north; lat m/deg=110540 |
| 21 | `tools/ue5-headless-city-import.py` | T10 bake: terrain/buildings/water/POIs | Bundle meters Z-up; script **x100 -> cm**; 1uu=1cm |
| 22 | `tools/akron-semantic-compiler/osm_to_xodr.py` | OSM graph -> OpenDRIVE | Local meters X=east Y=north; lat m/deg=**111320** (!=110540); tmerc geoReference; hdg rad 0=+X CCW |
| 23 | `tools/akron-semantic-compiler/building_extractor.py` | Buildings local XY | _geo_to_local meters X=east Y=north; height meters |
| 24 | `tools/akron-semantic-compiler/export_unreal_bundle.py` / `compile_akron.py` | Manifest origin = bounds center | WGS84 origin only |
| 25 | `tools/universal-city-compiler/*` | City compile pipeline | WGS84 lat/lon; distances meters; origin=bounds center; buildings lat/lon + height_meters |
| 26 | `tools/validate-citypack.py`, `batch-citypack/batch_citypack.py`, `verify-city-runtime-readiness.py` | Validation / batch | Geo indexing ~111320 |
| 27 | `packages/renderer-3d-lite/src/map/coords.ts` | Web/Babylon local frame | **X=east, Y=up, Z=south, meters**; METERS_PER_DEG_LAT=111320; **not** UE Z-up cm |
| 28 | `packages/renderer-3d-lite/src/overlay/**` | Overlay placement | Consumes LocalCoords / meter Y-up frame |
| 29 | `packages/race-engine/src/physics.ts`, `index.ts`, `citypack.ts` | Sim in WGS84 | Lat/lon + heading compass deg 0=north CW; meters; 111320 |
| 30 | `apps/unreal-akron-beta/citypacks/cleveland/burke_gp_1997/*` | Cleveland data pack | frame wgs84; origin 41.51722,-81.68306; s meters; width_m; XODR tmerc meters; environment.json documents Z-up 1uu=1cm; yaw_deg~compass; barriers *_m |
| 31 | `citypacks/cleveland_5.0km/*`, `citypacks/akron-*` | Full-city OSM extracts | Compiler inputs |
| 32 | `docs/CITYPACK_CONTRACT.md` | Documented (stale vs branch) contract | Still X=east, Z=-north, Y=up; heading->yaw direct; lat m/deg=110540 — **conflicts with current C++ Z-up cm** |
| 33 | `docs/CLEVELAND_ENVIRONMENT.md` | Cleveland env notes | Matches RacingLine: Z-up, 1uu=1cm, X=east Y=north |
| 34 | `apps/unreal-akron-beta/docs/VehicleAssetStandard.md` | Vehicle mesh frame | Vehicle Y-forward, Z-up (asset), not geo |

---

## 2. Conflicts found (esp. meter X/Z vs Z-up cm)

### C2.1 — Primary frame split (CRITICAL)

| Frame | Who | Axes | Units |
|-------|-----|------|-------|
| **A. UE runtime (Sprint-2 / Cleveland)** | AkronXodrImporter::GeoToWorld, RacingLineComponent, ClevelandEnvironmentActor, T10 headless after x100 | X=east, Y=north, Z=up | **cm** (1uu=1cm) |
| **B. Legacy level-spec / web** | generate-level-spec.py, renderer-3d-lite/coords.ts | X=east, Y=up, Z=south (-north) | **meters** |
| **C. Bake bridge** | ue5-import-level-spec._spec_to_ue | Remap B->A: (x,y,z)_m -> (x,-z,y)*100 | cm |

generate-level-spec.py still claims it matches C++ GeoToWorld; **false on this branch**. C++ is Frame A; LevelSpec is Frame B; bake adapter C bridges imported actors only.

### C2.2 — Meter consumers left on cm world (CRITICAL)

- StreetFurnitureSpawner: hard Akron origin; **meter** XY; no MetersToUU.
- BuildingMeshGenerator JSON path: footprint/height **not x100** while world is cm.
- MinimapWidget: MinimapRadiusMeters vs world deltas in **cm** -> ~100x zoom error if fed GeoToWorld points.
- RuntimeCityLoader::StreamChunk radius named meters vs UU distances.

### C2.3 — Spawn lat sign / packed geo (HIGH)

- Importer stores spawns/waypoints/checkpoints as FVector(lon, 0, -lat) (degrees, not world).
- CruiseSprintGameMode recovers Lat=-Location.Z, Lon=Location.X.
- Easy to double-negate or treat packed geo as world.
- Cleveland showcase mostly avoids via racing_line.json + GeoToWorld / GetPoseAtS.

### C2.4 — Meters-per-degree lat inconsistency (MEDIUM)

| Source | m/deg lat |
|--------|-----------|
| AkronXodrImporter, generate-level-spec, ue5-city-import-prep | **110540** |
| RacingLineComponent, ClevelandEnvironmentActor, osm_to_xodr, renderer, furniture, most JS | **111320** |

Same lat/lon -> ~0.7% world Y / XODR Y drift.

### C2.5 — Heading conventions (MEDIUM)

- Data heading_deg / yaw_deg look **compass** (0=north CW); Burke start ~247.
- OpenDRIVE hdg: rad, 0=+X east, CCW.
- UE yaw with X=east Y=north: 0=+X east, +90=+Y north.
- CruiseSprint / ParseSpawnArray: compass -> FRotator yaw **direct**.
- Cleveland grid uses polyline tangent (GetPoseAtS) — may disagree with compass yaw_deg on barriers.
- race-engine: compass 0=north CW.

### C2.6 — Docs drift (MEDIUM)

- CITYPACK_CONTRACT.md §3 still Frame B.
- CLEVELAND_ENVIRONMENT.md + pack environment.json Frame A.
- Treat CITYPACK_CONTRACT geo section as stale pending G2 acceptance.

### C2.7 — Origin defaults (LOW-MEDIUM)

- Importer/XODR/graph fallback: Akron 41.08, -81.52.
- Cleveland actors/pack: Burke 41.51722, -81.68306.
- Furniture ignores active citypack origin.

### C2.8 — Arc-length dual units (LOW-MEDIUM)

- Pack s in meters; runtime x100 if max S < 50000.
- Heuristic can mis-detect if data already cm.

---

## 3. Draft frame contract outline — PROPOSED (not accepted)

> Everything below is **PROPOSED** for overseer review. Not project law until accepted.

### PROPOSED name: raceGPS World Frame v1 (aka G2 Frame)

| Field | PROPOSED value | Notes |
|-------|----------------|-------|
| CRS (geo) | WGS84 (EPSG:4326) lat/lon degrees | Pack JSON frame: wgs84 |
| Origin | Per-citypack origin.{lat,lon} required; no silent Akron default in shared helpers | Cleveland Burke: 41.51722, -81.68306 |
| Projection | Equirectangular about origin | Document constants once |
| m/deg lat | PROPOSED: pick **one** — prefer 111320 (majority + RacingLine) or 110540 (importer/CITYPACK_CONTRACT); sync all | Dual constants forbidden after accept |
| m/deg lon | 111320 * cos(origin_lat_rad) | |
| World axes | **Z-up, X=east, Y=north** | UE left-handed |
| World units | **1 uu = 1 cm** (MetersToUU=100) | All runtime world lengths cm |
| Authoring / pack units | Geo degrees; lengths **meters** (*_m, s meters, height_meters); convert at boundary x100 | |
| Intermediate spec meters Y-up | PROPOSED **deprecate** for new code; keep _spec_to_ue as legacy adapter only | New emitters write Frame A or raw WGS84 |
| OpenDRIVE | Local meters X=east Y=north; geoReference tmerc +lat_0/+lon_0; XodrToWorld = x100 into Frame A | |
| Heading (data) | PROPOSED: heading_deg / yaw_deg = **compass** (0=north, CW) | |
| Heading (UE) | PROPOSED: compass->UE yaw: yaw_ue = compass_deg - 90 (normalize) **or** polyline tangent only | Pick one policy for spawns vs barriers |
| Packed geo in FVector | PROPOSED: **forbid** new (lon,0,-lat) packing; keep explicit lat/lon until GeoToWorld | Migrate CruiseSprint path |
| Web / renderer-3d-lite | PROPOSED: adopt Frame A or keep Frame B but rename toSpecLocal and document != UE | |
| Cesium (if re-enabled) | OriginHeight meters on WGS84 ellipsoid; horizontal still Frame A | Pack cesium_required: false today |

### PROPOSED choke points

1. C++: one GeoToWorld / MetersToUU / m-per-deg (shared header).
2. Python: one module for generate-level-spec, city-import-prep, osm_to_xodr.
3. TS: LocalCoords wraps same math or is explicitly web-only Frame B.

---

## 4. Suggested overseer follow-ups (not executed)

1. Accept or amend section 3; update CITYPACK_CONTRACT.md section 3.
2. Align generate-level-spec.geo_to_world with Frame A or keep Frame B but fix the matches-C++ claim.
3. Fix/gate meter-scale runtime leftovers: furniture, building JSON path, minimap radius.
4. Unify m/deg lat constant.
5. Document compass<->UE yaw once; audit barrier yaw_deg vs track tangent.
6. Remove Akron hard defaults from shared Cleveland path.

---

## 5. Method notes

- Read-only scans of Source/raceGPSAkronBeta, tools/*, packages/*, citypacks, docs.
- No Unreal build; no C++/uasset edits; no git commit.
- Evidence path written because docs/evidence/grokbot exists.
