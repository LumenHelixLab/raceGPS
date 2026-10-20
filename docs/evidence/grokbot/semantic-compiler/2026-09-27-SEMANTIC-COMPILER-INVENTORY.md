# SEMANTIC COMPILER INVENTORY — Akron vs universal-city-compiler

**Date:** 2026-09-27 (America/New_York)  
**Lane:** Workshop Web (SEMANTIC COMPILER PIN)  
**Worktree:** `C:\projects\raceGPS-grokbot-cleveland`  
**Branch:** `grokbot/cleveland-integration`  
**Method:** cite-and-path only (no editor, no installs, no greenfield Cleveland compile)  
**Pin:** `docs/handoff/2026-09-27-SEMANTIC-COMPILER-PIN.md` / Documents `raceGPS-handoff\2026-09-27-SEMANTIC-COMPILER-PIN.md`

## Scope

Compare the **KEEP** reference tree `tools/akron-semantic-compiler/` against the city-agnostic sibling `tools/universal-city-compiler/`, and note how each touches Overpass/cache, XODR, routes/checkpoints/POIs, manifests, and rgpack/citypack compatibility. Related: `tools/rgpack/`, `docs/contracts/RGPACK_v1.md`, `apps/semantic-map-server/` (coordinate — do not fork a third compiler).

---

## 1. Module surface map

| Concern | Akron (`tools/akron-semantic-compiler/`) | Universal (`tools/universal-city-compiler/`) | Shared / related |
|---------|------------------------------------------|----------------------------------------------|------------------|
| Entry | `compile_akron.py` | `cli.py` → `city_compiler.compile_city` | — |
| Bounds / city resolve | Hardcoded `AKRON_BOUNDS` in `compile_akron.py` | `geocode.py` (`geocode_city`, `expand_bounds`, `bounds_from_center`) + CLI `--radius` | Pattern: west/south/east/north dict |
| Overpass fetch | `fetch_osm.py` → `fetch_osm_for_bounds` | `fetch_overpass.py` → `fetch_and_cache` / tiled fetch | Same Overpass URL; both stdlib urllib |
| Road graph | `road_graph.py` → `build_road_graph` | `road_network.py` → `build_road_graph` | Same role; separate implementations |
| OpenDRIVE (.xodr) | `osm_to_xodr.py` → `generate_xodr` / `convert_osm_to_xodr` | **None** (no XODR emitter in tree) | Akron-only golden for XODR today |
| Routes | `route_generator.py` → `generate_cruise_sprint` | `route_engine.py` → `generate_routes` | Both emit route JSON + checkpoints |
| Checkpoints | `checkpoint_generator.py` → `place_checkpoints` | `route_engine.place_checkpoints` | Same concept; universal spacing default 350 m |
| POIs | `poi_classifier.py` → `classify_pois` | `poi_engine.py` → `classify_pois` | Tag-classify OSM nodes |
| Buildings | `building_extractor.py` | `building_extractor.py` | Same filename; separate modules |
| Extra layers | `export_unreal_bundle.py` gameplay_layer | `water_extractor.py`, `vegetation_scatter.py`, `elevation.py`, `biome_engine.py` | Universal-only M2 procedural extras |
| Export / manifest | `export_unreal_bundle.export_bundle` → `akron_semantic_manifest.json` | `export_bundle.export_bundle` → `{city_id}_semantic_manifest.json` | Citypack-shaped JSON, not RGPACK_v1 |
| Side / stub scripts | `build_cleveland_downtown_test.py` → `citypacks/cleveland/downtown-test/` | CLI docstring examples only | Stub cite — do not rebuild tourism map |
| Serve | — | — | `apps/semantic-map-server/main.py` hardcodes Akron citypack |
| Pack contract | Consumed downstream | Consumed downstream | `tools/rgpack/`, `docs/contracts/RGPACK_v1.md` |

**Do not delete/rename/absorb** `tools/akron-semantic-compiler/`.

---

## 2. What is shared (conceptually)

- **Pipeline shape:** GPS/OSM bbox → road graph → routes/checkpoints/POIs/buildings → citypack-dir JSON manifest.
- **Pure Python Overpass client** against `https://overpass-api.de/api/interpreter` (Akron: `fetch_osm.py`; universal: `fetch_overpass.py`; rgpack writer: `tools/rgpack/overpass_export.py`).
- **Cache-first OSM on disk** under the citypack output dir (`*_raw.osm` and/or road-graph JSON).
- **Repro seed:** Akron README cites `random.Random(42)`; universal CLI `--seed` default `42`.
- **Citypack file family:** `*_routes.json`, `*_pois.json`, `*_buildings.json`, `*_spawn_points.json`, `*_road_graph.json`, `*_semantic_manifest.json`.
- **Coordinate origin:** midpoint of bounds lat/lon written into manifests (`export_unreal_bundle.py`, `export_bundle.py`).

Shared = sibling role/contracts, **not** a single imported library. Implementations are duplicated across trees.

---

## 3. What is Akron-hardcoded (KEEP as golden fixture)

| Hardcode | Path | Cite |
|----------|------|------|
| Output citypack id | `citypacks/akron-oh-beta-001/` | `compile_akron.py` `CITYPACK_DIR` |
| Bounds | `AKRON_BOUNDS` west/south/east/north | `compile_akron.py` |
| Filenames | `akron_raw.osm`, `akron_road_graph.json`, `akron.xodr`, `akron_routes.json`, `akron_pois.json`, `akron_buildings.json`, `akron_spawn_points.json`, `akron_gameplay_layer.json`, `akron_semantic_manifest.json` | orchestrator + `export_unreal_bundle.py` |
| Manifest identity | `city_id: "akron-oh-beta-001"`, `display_name: "Akron, Ohio"` | `export_unreal_bundle.py` |
| Route ids | `akron_cruise_sprint_00N` | `route_generator.py` |
| XODR default path in `__main__` | falls back to Akron road graph | `osm_to_xodr.py` |
| Map server | `CITYPACK_DIR = .../akron-oh-beta-001`, route `/city/akron` | `apps/semantic-map-server/main.py` |

On-disk golden output (present): `citypacks/akron-oh-beta-001/` with `akron.xodr`, routes, POIs, road graph, spawn points, semantic manifest, gameplay layer.

---

## 4. Touch points by subsystem

### 4.1 Overpass / cache

| | Akron | Universal |
|--|-------|-----------|
| Module | `fetch_osm.py` | `fetch_overpass.py` |
| Query | Highways + buildings (XML) | Detail tiers: `minimal` / `standard` / `full` (roads, buildings, POIs; full adds water/landuse/natural) |
| Retry | 3 attempts; 429 backoff | 3-retry 429 backoff; streamed body; **tile grid** if bbox > `TILE_THRESHOLD_DEG` (0.25°) |
| Cache | Prefer `akron_raw.osm`; else reuse `akron_road_graph.json`; abort if neither and fetch fails | `fetch_and_cache(bounds, cache_path)`: return existing `{city_id}_raw.osm` else fetch+write |
| Orchestrator | `compile_akron.py` steps 1/3 | `city_compiler.compile_city` step 2 |

**rgpack path (separate):** `tools/rgpack/overpass_export.py` pulls **Overpass JSON** (not XML citypack). Comments there explicitly list Akron + universal fetchers and state **citypack XODR → rgpack remains a post-unlock adapter**. Offline fixture: `tests/fixtures/rgpack/overpass_burke_tiny/overpass.json`.

### 4.2 XODR (OpenDRIVE)

| | Akron | Universal |
|--|-------|-----------|
| Emitter | `osm_to_xodr.py` (`generate_xodr`, `convert_osm_to_xodr`) | **Absent** — no `.xodr` write in `city_compiler.py` / `export_bundle.py` / `road_network.py` |
| Output | `citypacks/akron-oh-beta-001/akron.xodr` | N/A |
| Manifest field | `opendrive_file: "akron.xodr"` | No opendrive field |

**Honesty:** universal citypack ≠ OpenDRIVE pack today. XODR remains an Akron-compiler capability (also reused by `build_cleveland_downtown_test.py`).

### 4.3 Routes / checkpoints / POIs

| | Akron | Universal |
|--|-------|-----------|
| Routes | `generate_cruise_sprint` → cruise-sprint style, Akron-prefixed ids | `generate_routes(..., mode="all", count=route_count, seed=seed)` |
| Checkpoints | `place_checkpoints(route, road_graph)` | `place_checkpoints(route, spacing_meters=350.0)` |
| POIs | `poi_classifier.classify_pois` | `poi_engine.classify_pois` |
| Buildings | `building_extractor` + local meters origin | `building_extractor` + origin |
| Extras | `akron_gameplay_layer.json` speed zones | water / vegetation / heightmap / biome JSON |

### 4.4 Manifests

- **Akron citypack manifest:** `akron_semantic_manifest.json` via `export_unreal_bundle.export_bundle` — fixed `city_id`, opendrive + file pointers, gameplay_layer.
- **Universal citypack manifest:** `{city_id}_semantic_manifest.json` via `export_bundle.export_bundle` — dynamic `city_id`, `files{}` map, version `2.0.0`, `generated_by: "universal-city-compiler-v2"`, optional water/vegetation/heightmap/biome. **No XODR pointer.**
- **RGPACK_v1:** `docs/contracts/RGPACK_v1.md` — `manifest.json` + `streets.json` / `checkpoints.json` / `spawn.json` / `environment.json`, Frame A, `contentHash`. Different schema from citypack semantic manifests.

### 4.5 Citypack vs rgpack compatibility (adapter honesty)

**citypack ≠ rgpack.** Do not claim equivalence without an adapter.

| Artifact | Producer | Consumer intent |
|----------|----------|-----------------|
| Semantic citypack (`citypacks/<id>/`) | Akron compiler / universal compiler | Unreal beta / semantic-map-server / level-spec helpers |
| RGPACK_v1 pack | `python -m rgpack export-overpass` (`tools/rgpack/`) | Race reads packs only; Workshop writes |
| Adapter status | Documented gap | `rgpack/overpass_export.py` header: *"Citypack XODR → rgpack remains a post-unlock adapter; this module is OSM JSON only."* CLI notes: *"Not a citypack XODR adapter."* |
| Validate helper | `tools/validate-citypack.py` | Citypack-side (sibling to compilers) |
| Golden rgpack fixtures | `tests/fixtures/rgpack/minimal_v1/`, `overpass_burke_tiny/` | Schema / export tests |

Related (do not fork compiler): `apps/semantic-map-server/` serves **Akron** citypack only today. Universal may call `tools/generate-level-spec.py --citypack` after export.

---

## 5. Stub second city (cite only — not built here)

Universal CLI has **no hardcoded stub city constant**. Docstring examples in `cli.py`:

```text
python cli.py "Cleveland, OH" --radius 8 --routes 6
python cli.py "41.5,-81.7" --radius 5 --detail full
```

Derived id pattern (`city_compiler.py`): `{geocoded_name}_{radius_km}km` (spaces/commas/dots stripped from Nominatim short name).

**Existing on-disk stub (Akron-tree side script, not universal):**  
`citypacks/cleveland/downtown-test/` produced by `tools/akron-semantic-compiler/build_cleveland_downtown_test.py` (includes `cleveland_downtown.xodr` + semantic JSON). **Cite only — do not rebuild / do not expand into Cleveland tourism map under this pin.**

**rgpack offline stub:** pack export fixture `overpass_burke_tiny` (`tests/fixtures/rgpack/overpass_burke_tiny/`).

---

## 6. Freeze-safe rules (restate)

1. Keep `tools/akron-semantic-compiler/` as golden fixture; do not gut while evolving universal.
2. Grow multi-city GPS→course from `tools/universal-city-compiler/` + `tools/rgpack/` contract.
3. Coordinate with `apps/semantic-map-server/`; do not fork a third compiler.
4. No UnrealEditor / CARLA / City Sample / StreetMap installs for this deliverable.
5. Citypack → rgpack requires an explicit adapter; Overpass→rgpack JSON path already exists separately.

---

## 7. Evidence links

- Companion brief: `2026-09-27-GPS-TO-RGPACK-EXPANSION-BRIEF.md`
- Folder index: `README.md` (this directory)
