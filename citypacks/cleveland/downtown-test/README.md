# Cleveland downtown-test citypack

**Canonical path:** `citypacks/cleveland/downtown-test/`  
**Apps mirror:** `apps/unreal-akron-beta/citypacks/` is a junction to repo `citypacks/`, so this pack is visible to the UE project with no copy step.  
**Pipeline:** OSM Overpass → `road_graph.py` → `osm_to_xodr.py` (pure Python). **No StreetMap plugin. No CARLA server.**

| Artifact | Role |
|----------|------|
| `cleveland_downtown.osm` | Raw Overpass extract (highways + buildings) |
| `cleveland_downtown_road_graph.json` | Semantic roads / intersections |
| `cleveland_downtown.xodr` | OpenDRIVE 1.4 for `AkronXodrImporter` / `RoadMeshGenerator` |
| `cleveland_downtown_semantic_manifest.json` | Dialect A manifest (`*_semantic_manifest.json`) |
| `cleveland_downtown_routes.json` / `_spawn_points.json` / `_gameplay_layer.json` | Minimal gameplay stubs |

**Bounds (WGS84):** south 41.495, north 41.505, west -81.700, east -81.685  
**Origin:** bbox center (41.50, -81.6925)  
**Status:** smoke / test pack — not a certified downtown course.

## Regenerate

```powershell
cd C:\projects\raceGPS-grokbot-cleveland
py -3 tools\akron-semantic-compiler\build_cleveland_downtown_test.py
```

## Point the importer / generate road meshes

Nested pack dir ≠ flat `city_id`, so select it via **CityId path under `citypacks/`** (UE joins `../../citypacks` + CityId in editor):

### A) PIE / `-game` with CruiseSprint (auto `GenerateRoadMeshAsync`)

```powershell
# From a shell that can launch the editor binary you already use for Akron:
# CityId "cleveland/downtown-test" resolves to ../../citypacks/cleveland/downtown-test/
& "C:\Program Files\Epic Games\UE_5.7\Engine\Binaries\Win64\UnrealEditor-Cmd.exe" `
  "C:\projects\raceGPS-grokbot-cleveland\apps\unreal-akron-beta\raceGPSAkronBeta.uproject" `
  -racegps.city=cleveland/downtown-test
```

Or in DefaultGame.ini (do not commit unless you want this as the default):

```ini
[RaceGPS.CitySelection]
CityId=cleveland/downtown-test
; equivalently:
;CitypackDir=../../citypacks/cleveland/downtown-test
```

Console at runtime: `racegps.CityId cleveland/downtown-test`

### B) Editor: RoadMeshGenerator actor only

1. Open `raceGPSAkronBeta.uproject`, place / select an `ARoadMeshGenerator`.
2. Set **Xodr Path** to:

   `../../citypacks/cleveland/downtown-test/cleveland_downtown.xodr`

3. Call **Generate Road Meshes** (or `GenerateRoadMeshAsync`) on the actor.

Exact next command (mesh via PIE game mode path):

```powershell
& "C:\Program Files\Epic Games\UE_5.7\Engine\Binaries\Win64\UnrealEditor.exe" `
  "C:\projects\raceGPS-grokbot-cleveland\apps\unreal-akron-beta\raceGPSAkronBeta.uproject" `
  -game -racegps.city=cleveland/downtown-test
```

`CruiseSprintGameMode` resolves the pack, sets `RoadMeshGenerator->XodrPath`, then calls `GenerateRoadMeshAsync()`.

## Notes

- Do **not** enable StreetMap / Cesium / CARLA for this pack.
- OSM + XODR are ~1 MB each — fine as ordinary Git blobs (no LFS required).
- Sibling Cleveland pack: `citypacks/cleveland/burke_gp_1997/` (historic circuit; different dialect).
