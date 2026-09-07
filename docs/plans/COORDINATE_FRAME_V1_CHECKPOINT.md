# raceGPS — coordinate migration source checkpoint

2026-09-07 · follows `0ad434c2ba6d3f8c246c34fcf4d93f8653df57f3`

**Source migration and native math verification completed. Unreal compilation,
scene migration and playable acceptance remain pending.** The owner reports Unreal
5.7.4 installed and running on the Windows machine; this session cannot access that
machine directly. The declared project requirement is 5.7, so 5.7.4 satisfies the
build script's major/minor check. The local launcher records the actual Build.version.

## Contract

| Boundary | Representation |
|---|---|
| Geographic input | Latitude/longitude degrees; double precision retained through local subtraction |
| Local source frame | `racegps-eqc-enu-m-v1`: east/north/up meters, equirectangular approximation, 111320 meters/degree, longitude cosine at declared origin |
| Unreal world frame | `racegps-ue-esu-cm-v1`: X=east, Y=south, Z=up; centimeters |
| Position conversion | `(x,y,z) = (100 east, -100 north, 100 up)` |
| Compass heading | North=-90° yaw, east=0°, south=90°, west=-180°; normalized to [-180,180) |
| Distances in semantic data | Explicit `*_meters` values remain meters; convert at the rendering/physics boundary |
| Vertical reference | Local up only. No surveyed terrain or vertical-datum transform is claimed |

`tools/geo_frame.py` and the engine-independent production header
`RaceGPSGeoFrame.h` implement the boundary. The prior C++/level-spec latitude scale
110540 differed from the XODR exporter's 111320; those lanes now use the same declared
approximation. This removes internal mismatch, not geographic approximation error.

## Implemented migration

- Geographic roads, routes, checkpoints and spawns now produce horizontal X/Y
  centimeter positions. The negative-latitude storage sign at spawn is undone.
  Geographic values remain doubles in the importer and active origin.
- Road width becomes centimeters at mesh construction; the strip right vector and
  normals are corrected for positive-Z-facing triangle winding. XODR line geometry includes
  its final endpoint and rejects unsupported primitives, invalid lengths and joins
  discontinuous by more than 1 cm. Curves/elevation still require further work.
- Level specs declare world-frame v1/schema v3; traffic volumes use X/Y horizontally
  and Z vertically. Reflection-capture height adjustments use Z.
- Buildings carry explicit footprint space/frame/origin; supported geographic and
  declared local-meter footprints convert consistently, and heights become
  centimeters. Repeated closing polygon vertices are removed before mesh closure.
- Furniture uses its graph's origin and frame; meter radius/offset values are
  converted. The existing furniture functions still only log placements: no new
  physical furniture assets are claimed.
- Manifests, road graphs and building wrappers carry frame/origin metadata. Packaging
  checks reject unknown/missing/mismatched frames. Existing legacy packs need actual
  regeneration; do not add a label without converting and validating their contents.
- Editor/runtime spec import rejects old unlabelled world coordinates. Successful
  editor import stamps frame and origin tags; startup requires the matching marker.
  This prevents new roads from silently mixing with old map scenery. It does not
  certify the imported scenery's completeness, collision or visual quality.
- Headless map import now refuses to delete an existing map. Use a fresh level name
  for migration. Existing `.umap`/`.uasset` binaries were not modified here.
- The experimental runtime loader checks the frame and converts streaming radius
  from meters to centimeters.

## Verification

**236 Python tests passed; 5 skipped** for the absent historical Akron raw `.osm`.
This includes compiling the actual production math header with g++ C++17 using
`-Wall -Wextra -Werror`, then executing position, width, heading, line-endpoint and
geographic precision probes. No Unreal headers or UHT are included in that portable
probe, so it is not an Unreal build claim.

Independent control checks include 100 m → 10000 cm, 7 m width → 700 cm, all cardinal
headings, positive altitude, a complete line endpoint and a roughly 1.1 mm geographic
northward displacement that survives the double-precision conversion.

The pinned Cleveland extract rebuilt twice with identical new outputs. The old
rebuild hashes remain historical evidence; changed frame/building metadata produces
new hashes recorded under `docs/evidence/coordinate-frame/`. The context pack still
correctly fails race readiness because no certified course or starting grid exists.

## Important limits to verify next

1. Compile Unreal/UHT/Slate on the owner's installed 5.7.4 host. Blueprint-callable
   signatures changed from float to double; inspect and repair Blueprint pins.
2. Regenerate the intended pack and fresh scene together. Match origin/frame tags;
   inspect 100 m length, 7 m width, vehicle/wheel collision, spawns and checkpoint
   placement inside the editor and package. Do not enable legacy scenery by simply
   adding the marker to an old map.
3. Restore terrain elevation and grade profiles deliberately; source-layer estimates
   are not measured clearance. Curved XODR primitives are explicitly unsupported in
   this importer rather than silently flattened.
4. Audit older saved replays, minimap transforms, camera behavior and any Blueprint
   coordinate math against the versioned frame before reusing them. Legacy replay
   migration is not part of this source checkpoint.
5. Building meshes still need correct concave roof triangulation/normals/materials
   and actual skyline reconstruction. The coordinate repair is not finished art.
6. Package selection still needs a coherent Cleveland distribution manifest; the
   legacy mixed Akron inputs continue to fail. Two physical AI drivers, lighting
   acceptance, performance and independent playtests remain open.

## Build locally without Grok

`scripts/Build-RaceGPS-Local.ps1` is a Windows launcher prepared here. It has not been
executed on Windows in this session. The downloadable local-build ZIP includes it,
the current incremental Git bundle, a checksum and instructions.

First run `-CheckOnly` while the editor is open to discover the actual engine.
Before a real C++/header build, save and close the editor. The launcher checks for
running editors and stops rather than closing them. It imports the checkpoint into
a new worktree, preserves the original checkout, uses an isolated Python environment,
runs tests/audits and attempts the editor target build. It does not install a game,
push to GitHub or claim packaging success.

The bundle requires base commit `b56b6c814c23423d13b7683607d0da5ba89130f2` in the
existing local repository. Use `-Repo` if the checkout is not `D:\projects\raceGPS`;
use `-Engine` if the actual installation is not discovered. Git and Python 3.12 with
the Windows `py` launcher must already be available; missing dependencies are
reported explicitly. Security-policy restrictions are reported, not changed.

The launcher writes an evidence ZIP containing commands, logs, actual engine metadata,
exit codes and source revision. Attach it in this conversation to continue diagnosis
without transferring the task to another agent.
