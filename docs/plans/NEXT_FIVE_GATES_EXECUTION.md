# raceGPS — next five gates, execution record

2026-09-07 · follows D1 commit `a341e87853f2466316280a2640d67bb501869e5c`

**Local engineering and evidence work completed; publication and playable-demo
acceptance remain blocked.** The five dependency gates below do not replace the
approved D1–D4 demo sprints and do not mean five production milestones passed.

## Gate results

| Gate | Delivered | Acceptance state |
|---|---|---|
| 1. Publish foundation and reconcile inputs | Local branch retained; actual Akron source/artifact comparison recorded | **Partial.** Source diagnosis complete. Git has no write credentials; connected GitHub reports `push: false`. No branch push or draft PR succeeded. Matching legacy raw OSM is absent. |
| 2. Prove route connectivity | Explicit directed source-segment traversal; true circuit closure; one-way/reverse-one-way/roundabout handling; bridge approach continuity; deterministic bounded search; route certificates and audit | **Portable checks pass.** Legacy Akron routes have no source-segment certificates. Competitive equity, turn restrictions, width, elevation and clearance are not certified by connectivity. |
| 3. Establish Cleveland input pipeline | Real source bytes and provenance retained; offline compiler; separate aeroways; matching graph/XODR road identities and shared origin; two byte-identical builds | **Context-data proof passes. Historical race gate stays open.** 607 roads, 1,502 building records, 47 airfield features. No historical route, starting grid, measured terrain, skyline reconstruction or release-ready Cleveland pack. |
| 4. Prevent false startup/package success | Build audits city inputs before editor/UAT execution; game rejects unresolved/incomplete packs and empty routes/spawns; native recovery panel; start/restart guards; waits for actual road generation; explicit failure/timeout | **Implemented, not Unreal-verified.** C++/Slate changes must compile and run on UE 5.7. Existing incoherent Akron pack now blocks the build intentionally. |
| 5. Verify and hand off | 224 Python tests passed, 5 skipped; real data audit failures retained; Unreal preflight attempted; patchable local commits and transfer bundle prepared | **Portable verification passes. Unreal gate blocked.** No engine, editor, game package, controller run, frame capture or physical-AI demonstration available on this host. |

## What the source audit established

The old `akron_raw.json` contains 48,109 nodes without coordinates and 5,305 ways
without node references. It cannot reconstruct the old map. The root backend pack
has 1,370 roads, while the semantic graph has 35,828. Comparing source road IDs against
`akron.xodr` finds 34,506 graph-only roads and 48 XODR-only roads. This is mixed input,
not just an inaccurate count. The declared building file is also missing.

The graph's 52 connected components are diagnostic. They are not automatically an
error: real clipping, isolated infrastructure and grade separation exist. Do not
snap near endpoints to make the number smaller. Prove each selected course's ordered
source segments instead. Legacy routes without those references fail the new audit.

The generator now refuses invented joins and open circuits. It may return fewer
routes than requested when bounded search finds no qualifying route. It is an offline
candidate generator, not the deployed online ZIP selection/ownership service. The
requester still gets no route choice, reroll or automatic ownership in that future
service; none of those online rules were weakened or implemented prematurely.

## Cleveland reconstruction evidence

The exact OSM response, source URL, retrieval timestamp, attribution and checksum
are in `data/sources/cleveland-burke/`. Two clean offline compiles matched all ten
files byte for byte, including the manifest. Present-day roads and airport aeroways
remain distinguishable; the compiler deliberately emits no invented historical lap.

The prototype XODR exporter now uses the declared graph origin, supports the
`one_way` field and labels its equirectangular math correctly instead of declaring
Transverse Mercator. Bounds are local meters. Its lane/junction semantics still
need proper ASAM/CARLA validation. Equal IDs and hashes are integrity checks, not
proof that a road is physically drivable or historically accurate.

Data acquisition follows the [OSM map API](https://wiki.openstreetmap.org/wiki/API_v0.6).
The projection declaration follows [PROJ's equidistant cylindrical definition](https://proj.org/en/stable/operations/projections/eqc.html).
The historical reference remains [INDYCAR's 2006 Cleveland replay](https://www.indycar.com/videos/2024/12/12-06-FullRaceReplay-Cleveland-2006).

## Newly identified P0: coordinate migration before driving acceptance

`AkronXodrImporter::GeoToWorld` and `XodrToWorld` return meter-scale X/Z planar values,
while the road mesh code adds height to Z and crosses with Unreal's Z-up vector.
`tools/generate-level-spec.py` repeats the X/Z convention; street furniture separately
uses X/Y and hard-coded Akron origin. Road width also remains in meters when written
to mesh vertices. `SpawnPlayerAtStart` passes a stored negative latitude without
undoing the sign. The XODR reader collects geometry starts but omits the final line
endpoint. These source observations block any claim of a scale-correct playable map.

Epic documents [Z-up axes](https://dev.epicgames.com/documentation/unreal-engine/coordinate-system-and-spaces-in-unreal-engine) and [centimeter units](https://dev.epicgames.com/documentation/unreal-engine/unity-to-unreal-engine-frequently-asked-questions-faq).

Coordinate repair is deliberately not reduced to a one-function edit. Establish one
versioned frame (local east/north/up in meters for source, explicit Unreal X/Y/Z
centimeters at the renderer boundary), then migrate roads, widths, route/checkpoint
positions, spawns/headings, building footprints, furniture, level specs and imported
scene assets together. Avoid modifying existing `.umap` binaries without the editor.
Add known east/north/up control vectors, a 100-meter segment and a 7-meter road-width
fixture; compare world and collision transforms in the engine. Handle legacy frame
versions explicitly. Retain double precision until the local-coordinate subtraction.

## Runtime changes and remaining limits

The game previously advanced to countdown after three seconds regardless of loading.
It now waits for the road generator, rejects zero roads, and times out explicitly.
Runtime tick enable/disable now uses `SetActorTickEnabled`; setting the initial tick
flag after actor startup did not reliably enable work. Batched meshes cook collision
synchronously before signaling completion; profile the batch size and loading stalls
on target hardware. Constructor-only material lookup was removed from mesh generation.

Failures display a native panel with Restart and Exit actions, independent of an
assigned HUD blueprint. Pawn input and race/restart entry points are gated. This is
a functional failure-flow implementation, not completed premium UI or a tested
controller-accessibility pass. Buildings/furniture completion, coordinate migration,
route-to-collision alignment and all final scene checks remain open.

The input audit rejects missing files, escaping manifest paths, available hash
mismatches, mismatched source road identities and illegal route segment sequences.
It does not replace full schemas, OpenDRIVE geometry/lane validation, terrain clearance,
asset dependency inspection or in-engine testing. `--check` remains engine/tool
preflight only; real build commands also run the citypack audit before compilation.

## Exact next execution order

1. Restore GitHub write access for `LumenHelixLab/raceGPS`, then push the existing
   reviewed branch and create the prepared draft PR. User authorization is already
   granted; the remaining problem is credentials/connection capability.
2. On a Windows UE 5.7 host, compile the startup fixes and inspect the existing maps
   and actual asset dependencies. Preserve logs even when the city-data gate blocks
   packaging. A compile is not yet an acceptable race.
3. Migrate the coordinate contract end to end; certify a bounded Cleveland course
   overlay with source-dated controls and terrain. Generate a fresh coherent runtime
   pack, route certificates, starting grid and level spec from that contract.
4. Execute D2: collision-correct solo package, one production car, skyline benchmark,
   sunset/twilight/midnight capture and frame-time profile. The current context bundle
   must not be promoted to pass this gate without those changes.
5. Execute D3/D4: two physical rivals and recovery evidence, complete race/UI/audio,
   urban diagnostic fixture, replay, independent-machine install and external playtest.
   Keep online championship work behind accepted offline delivery.

## Commands and evidence

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest tests -q
python scripts/citypack_audit.py citypacks/akron-oh-beta-001 --report build-evidence/akron-audit.json
python scripts/build.py --check --engine "C:\Program Files\Epic Games\UE_5.7" --report build-evidence/preflight.json
```

The Akron audit is currently expected to return exit 1. Do not remove the gate or
make dummy files to proceed. To compile C++ independently while source repair is
under way, from the repository root on the Unreal host:

```powershell
& "C:\Program Files\Epic Games\UE_5.7\Engine\Build\BatchFiles\Build.bat" raceGPSAkronBetaEditor Win64 Development "-project=$((Get-Location).Path)\apps\unreal-akron-beta\raceGPSAkronBeta.uproject" -waitmutex
```

After coherent city data is accepted:

```powershell
python scripts/build.py --engine "C:\Program Files\Epic Games\UE_5.7" --config Development --report build-evidence/build.json
```

Engine acceptance must cover missing Cleveland, missing building file, malformed
route, invalid selected index, corrupt/empty XODR, a road build taking over three
seconds, timeout, Retry/Exit cleanup and a valid race. Confirm no countdown before
collision readiness, installed-data resolution without the source checkout, correct
axes/scale, and checkpoint/starting-grid alignment. Record the exact branch commit,
engine patch, machine specification, package hash, logs and actual video results.

Evidence: `docs/evidence/next-five-gates/`. Five Python skips still require the missing
historical Akron `.osm`. C++ source-inspection tests in the existing suite are not
compiler or gameplay evidence. No Unreal download or demo completion is claimed.
