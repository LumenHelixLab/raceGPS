# CityPack v2

Canonical contract between world-gen, gameplay, and the control plane. No agent reaches around this format.

`format` string: `racegps-citypack-v2`

This document freezes the **steel-thread slice** first. Fields marked “later” are not required for `steel-thread-001`.

Legacy shapes that must not gain new consumers:

- `tools/batch-citypack/schema/citypack.schema.json` (`racegps-citypack-v1`)
- `citypacks/akron-oh-beta-001/akron_semantic_manifest.json` (pointer bundle, no checksums)
- `packages/protocol` `CityPack` / `packages/race-engine` `CityPack` (inline lat/lon pack)

---

## Pack layout

A CityPack v2 is a **directory**, not a single JSON blob:

```
citypacks/<city_id>/
  manifest.json
  attribution.json
  checksums.json
  roads.xodr
  roads.json
  buildings.json
  routes.json
  spawn_points.json
```

Steel-thread city id: `steel-thread-001`.

## Coordinate system

All JSON geometry is **WGS84** `{ "lat", "lon" }`. `origin` in the manifest is the projection center. OpenDRIVE uses tmerc meters about that origin (same as `tools/akron-semantic-compiler/osm_to_xodr.py`). UE converts via existing `UAkronXodrImporter::GeoToWorld`. Do not emit local x/y in JSON (Akron `buildings.json` footprints are legacy).

## `manifest.json`

Required keys:

| Key | Steel-thread |
|---|---|
| `city_id` | `steel-thread-001` |
| `display_name` | string |
| `format` | `racegps-citypack-v2` |
| `version` | semver of the pack, e.g. `2.0.0` |
| `game_version_min` / `game_version_max` | strings; UE `IsVersionCompatible` matches major.minor |
| `origin` | `{ lat, lon }` |
| `bounds` | `{ west, south, east, north }` |
| `seed` | integer (hash-repeat) |
| `generated_by` | `universal-city-compiler` |
| `generated_at` | ISO-8601 UTC |
| `files` | map of logical name → filename (see layout) |
| `statistics` | `{ roads, junctions, buildings }` — steel-thread **must** be `2`, `1`, `1` |

Optional later: `pois`, `water`, `vegetation`, `heightmap`, `biome`, `gameplay_layer`.

## `attribution.json`

Required: OSM copyright/license (ODbL), toolchain list, a `notes` string. Steel-thread notes must say the OSM is synthetic / fixture, not a live Overpass pull.

## `checksums.json`

```json
{ "algo": "sha256", "files": { "manifest.json": "<hex>", "...": "<hex>" } }
```

Hash every file in the pack **except** `checksums.json`. Hex lowercase. Same seed + same fixture → same hashes (ignore `generated_at` by hashing a canonical copy with `generated_at` set to empty string, **or** exclude `generated_at` from the hashed manifest — pick one and test it; steel-thread tests must be deterministic).

Recommended: write `generated_at` into manifest, but hash a canonicalization that zeros `generated_at`. Tests compare checksums of payload files other than manifest time.

## `roads.json`

```json
{
  "roads": [
    {
      "id": "string",
      "name": "string",
      "highway": "string",
      "oneway": false,
      "width": 7,
      "lane_count": 2,
      "max_speed": 40,
      "points": [{ "lat": 0, "lon": 0 }]
    }
  ],
  "junctions": [
    { "id": "string", "lat": 0, "lon": 0, "road_ids": ["r1", "r2"] }
  ]
}
```

Steel-thread: **2** roads, **1** junction. Each road ≥ 2 points. Junction `road_ids` names both roads.

## `buildings.json`

```json
{
  "buildings": [
    {
      "id": "string",
      "name": "string",
      "height": 12,
      "levels": 3,
      "footprint": [{ "lat": 0, "lon": 0 }]
    }
  ]
}
```

Steel-thread: **1** building, footprint a closed ring (≥ 4 points, last may repeat first).

## `routes.json`

Array of routes. Steel-thread: **1** route with `route_id`, `name`, `mode` (`cruise_sprint`), `start`, `finish`, `points` (≥ 2), `checkpoints` (array of `{ lat, lon }`, at least 2). Do **not** validate the course by average speed, collision count, or a mandatory loop.

## `spawn_points.json`

Array of `{ id, lat, lon, heading, route_id }`. At least one, matching the steel-thread route.

## `roads.xodr`

OpenDRIVE 1.4 XML from the **Python** compiler path (`generate_xodr` in `tools/akron-semantic-compiler/osm_to_xodr.py` or an equivalent moved into `tools/universal-city-compiler/`). Not `carla.Osm2Odr`. Universal compiler does not emit XODR today — steel-thread must add that emission without calling CARLA.

---

## Steel-thread fixture

Input is a **checked-in** tiny OSM (or equivalent synthetic graph), not Overpass, not Akron:

- 2 highway ways that share one node (the junction)
- 1 building way
- Origin may sit near Akron coords for importer familiarity; bounds must be tiny

Path convention: `tools/universal-city-compiler/fixtures/steel_thread.osm`

Emit to `citypacks/steel-thread-001/`.

## Compatibility

UE and the TypeScript backend consume this directory through `manifest.json` `files` pointers. New protocol types must match these JSON keys; do not grow a fourth shape.

Machine-readable manifest schema: `docs/contracts/citypack-v2.manifest.schema.json`.
