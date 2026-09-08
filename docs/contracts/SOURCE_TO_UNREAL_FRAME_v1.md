# SOURCE_TO_UNREAL_FRAME_v1

**Contract id:** `SOURCE_TO_UNREAL_FRAME_v1`  
**Status:** ACCEPTED (G2)  
**Date:** 2026-09-07 (America/New_York)  
**Owner:** COORDINATES  
**Worktree:** `C:\projects\raceGPS-grokbot-cleveland` branch `grokbot/cleveland-integration`

This is the single versioned source→Unreal world frame for raceGPS runtime, bake, scenery, roads, spawns, checkpoints, and collision. New emitters MUST target this frame. Frame B is legacy only.

---

## 1. Identity

| Field | Value |
|-------|-------|
| Version id | `SOURCE_TO_UNREAL_FRAME_v1` |
| Alias | Frame A / G2 Frame |
| Geo CRS | WGS84 (EPSG:4326), lat/lon degrees |
| Origin | Per-citypack `origin.{lat,lon}` (required for shared helpers) |
| Projection | Equirectangular about pack origin |
| Runtime axes | **Z-up, X=east, Y=north** (UE left-handed) |
| Runtime units | **1 uu = 1 cm** (`MetersToUU = 100`) |
| Pack / authoring lengths | meters (`*_m`, `height`, `s`, `width_m`); convert **×100 at the boundary** |

---

## 2. Equirectangular constants (ONE lat scale)

```
METERS_PER_DEG_LAT = 111320
METERS_PER_DEG_LON(origin_lat) = 111320 * cos(radians(origin_lat))
```

**Chosen lat m/deg:** `111320` (Cleveland / RacingLine / osm_to_xodr majority).  
**Deprecated:** `110540` in new code (legacy importer/CITYPACK_CONTRACT value).

### Geo → world (cm)

```
X = (lon - origin_lon) * METERS_PER_DEG_LON(origin_lat) * 100
Y = (lat - origin_lat) * METERS_PER_DEG_LAT * 100
Z = 0   // callers add height in cm on +Z
```

### OpenDRIVE local meters → world (cm)

OpenDRIVE local: X=east, Y=north (meters, origin already in geoReference).

```
UE = (XodrX * 100, XodrY * 100, 0)
```

---

## 3. Heading / yaw (ONE mapping)

| Domain | Convention |
|--------|------------|
| Pack `heading_deg` / `yaw_deg` | **Compass:** 0=north, 90=east, CW positive |
| OpenDRIVE `hdg` | radians, 0=+X east, CCW |
| UE yaw (Frame A) | 0=+X east, +90=+Y north |

**Compass → UE yaw (degrees):**

```
yaw_ue = NormalizeDegrees(90 - compass_deg)
```

Examples: north 0→90, east 90→0, south 180→-90, west 270→-180.

Polyline / racing-line tangents in XY already produce UE yaw; prefer tangent for track-aligned actors. Use compass mapping for explicit spawn/barrier headings.

---

## 4. Packed geo in `FVector` (LEGACY)

Historical packing: `FVector(lon, 0, -lat)` (degrees, **not** world).

```
Lat = -Location.Z
Lon = Location.X
```

**Rules:**
- **Forbidden** for new emitters / new fields.
- Existing loaders may keep packing until a typed `Lat`/`Lon` migration.
- Consumers MUST unpack with the signs above, then call `GeoToWorld` — never treat packed geo as world cm.
- Silent reinterpretation of packed geo as Frame B world meters is forbidden.

---

## 5. Frame B (LEGACY) — bake bridge only

| Field | Frame B (legacy LevelSpec / web) |
|-------|----------------------------------|
| Axes | X=east, Y=up, Z=-north (south +Z) |
| Units | meters |
| Emitters | **Deprecated** for new code |

### Bake bridge B → A (`tools/ue5-import-level-spec.py::_spec_to_ue`)

```
UE_cm = (x_m * 100, -z_m * 100, y_m * 100)
```

- Spec without `frame` / `frame: legacy_level_spec_B` → apply bridge.
- Spec with `frame: SOURCE_TO_UNREAL_FRAME_v1` → already Frame A cm; **no remap, no extra ×100**.

---

## 6. Choke points

1. **C++:** `UAkronXodrImporter::GeoToWorld`, `MetersToUU`, `MetersPerDegreeLat`, `CompassHeadingDegToUeYaw`
2. **Python:** `tools/generate-level-spec.py` (emit v1), `tools/ue5-import-level-spec.py::_spec_to_ue` (legacy bridge)
3. **Scenery / roads / furniture / buildings / minimap:** convert meters→cm at boundary; share GeoToWorld
4. **Web renderer-3d-lite:** remains Frame B until explicitly renamed; not UE runtime truth

---

## 7. Tolerances (G2 proof)

| Check | Tolerance |
|-------|-----------|
| 100 m east/north line length | ± 1 cm |
| 7 m road width (half-width 3.5 m) | ± 1 cm |
| Angular (heading) | ± 0.1 deg |

---

## 8. Non-goals

- Does not claim G3–G5.
- Does not weaken Akron citypack validation.
- Does not auto-merge showcase Content/umaps.
