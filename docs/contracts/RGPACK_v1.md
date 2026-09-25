# RGPACK_v1

**Contract id:** `RGPACK_v1`  
**Status:** ACCEPTED (Slice 1 Task 1)  
**Date:** 2026-09-24 (America/New_York)  
**Owner:** PACK  
**Worktree:** `C:\projects\raceGPS-grokbot-cleveland` branch `grokbot/cleveland-integration`  
**Spec:** `docs/superpowers/specs/2026-09-24-racegps-two-app-gps-design.md` @ `de89789`  
**Python package:** `tools/rgpack/`

This is the versioned on-disk raceGPS pack (rgpack) schema. Workshop writes packs; Race only reads. Geometry is WGS84 in pack files; Race converts once via Frame A (`SOURCE_TO_UNREAL_FRAME_v1`).

---

## 1. Disk layout

```
<pack_dir>/
  manifest.json
  streets.json
  checkpoints.json
  spawn.json
  environment.json
```

Filenames may be overridden in the manifest; defaults match the names above.

---

## 2. `manifest.json` fields

Python dataclass fields use snake_case; JSON uses camelCase.

| JSON | Python | Rules |
|------|--------|-------|
| `schemaVersion` | `schema_version` | Must be `1` |
| `packId` | `pack_id` | Non-empty string |
| `displayName` | `display_name` | Human label |
| `frame` | `frame` | Frame A only (below) |
| `source` | `source` | Provenance |
| `certification` | `certification` | provisional \| certified |
| `contentHash` | `content_hash` | `sha256:` + hex of geometry |
| `defaults` | `defaults` | Environment + optional loadout |
| `streets` | `streets` | Default `streets.json` |
| `checkpoints` | `checkpoints` | Default `checkpoints.json` |
| `spawn` | `spawn` | Default `spawn.json` |
| `environment` | `environment` | Default `environment.json` |

### Frame A (required)

| Field | Value |
|-------|-------|
| `unitsPerMeter` | **must be 100** |
| `zUp` | **must be true** |
| `xEast` | **must be true** |
| `yNorth` | **must be true** |
| `originLat` / `originLon` / `originAltM` | Pack local origin (WGS84 + meters) |

### Source

- `type`: `osm` \| `gps_trace` \| `provisional_circuit`
- `attribution`: string
- `retrievedAt`: ISO-8601 string
- `bbox`: `[minLon, minLat, maxLon, maxLat]`

### Certification

- `status`: `provisional` \| `certified`
- `notes`: string (v1 always allows provisional)

### Defaults

- `environmentPreset`: `Sunset` \| `Twilight` \| `Midnight`
- `loadoutId`: optional string

---

## 3. Content hash algorithm

For geometry names in order **`streets.json`, `checkpoints.json`, `spawn.json`, `environment.json`** (or the filenames named in the manifest, in that key order):

1. SHA-256 update with UTF-8 filename bytes
2. Update with a single NUL byte (`0x00`)
3. Update with raw file bytes
4. Update with a single NUL byte
5. Prefix digest hex with `sha256:`

Python: `rgpack.hashutil.content_hash(pack_dir, geometry_names)`.

Mismatch or missing geometry file fails closed (`RgpackValidationError`).

---

## 4. Python API (`tools/rgpack`)

| Symbol | Role |
|--------|------|
| `RgpackValidationError` | Validation / integrity failure |
| `validate_manifest(dict) -> Manifest` | Parse + validate JSON object |
| `content_hash(pack_dir, geometry_names) -> str` | Digest with `sha256:` prefix |
| `load_pack(pack_dir) -> Manifest` | Read `manifest.json` |
| `save_pack(pack_dir, manifest, files) -> None` | Write geometry + recompute hash |
| `validate_pack_dir(pack_dir) -> bool` | Load + verify files + hash; raises on failure |

---

## 5. Golden fixture

`tests/fixtures/rgpack/minimal_v1/` — `packId` `fixture_minimal_v1`, `displayName` `Minimal Fixture`. Round-trip coverage in `tests/test_rgpack_schema.py`.

---

## 6. Roles

- **Workshop** writes packs under `Saved/raceGPS/packs/<packId>/`.
- **Race** only reads packs; no live OSM network inside Race.
- Pack launches use **override** only; do not change GlobalDefaultGameMode / Akron CruiseSprint defaults.
