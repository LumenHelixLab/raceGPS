# M2 Real Roads — Evidence Pack

Branch: `sprint/m2-real-roads` · Plan: `docs/superpowers/plans/2026-09-30-m2-real-roads.md`

## Certificate results

| Pack | ribbons | junctions | spawns | dropped_stubs | sha256 (prefix) | Validator |
|---|---|---|---|---|---|---|
| burke_gp_1997 | 1 | 0 | 0 | 0 | `584cf14dc9a5` | PASS (exit 0) |
| downtown-test | 432 | 392 | 1 | 0 | `fcffa1f86060` | ribbon_certificate PASS; pack overall FAIL on 2 pre-existing non-M2 checks |

Full outputs: `validator-burke_gp_1997.txt`, `validator-downtown-test.txt`,
`validator-akron-regression.txt`, `spec-hashes.json`.

## Mixed-pack junction fix (T4 deviation)

downtown-test has both `cleveland_downtown.xodr` and `*_road_graph.json`.
The generator prefers XODR for ribbon geometry; junctions were silently 0
because `junction_boxes` only ran in the graph branch. Fix: when a graph
sits alongside the XODR, junction boxes are emitted from the graph and
projected into the XODR local frame via the header's eqc geoReference
(projection verified to sub-millimetre against XODR road start coordinates).
All 392 junction boxes verified within 15 m of a road centerline.

## Pre-existing failures NOT introduced by M2 (downtown-test)

1. `cleveland_downtown_routes.json` uses a `waypoints` array; the validator's
   route check only accepts `points`. Routes file predates this branch
   (commit 939dc88).
2. No `generated/*_LevelSpec.json` with city_id `cleveland-downtown-test`.

Akron regression check: only pre-existing AkronWorld lighting-rig FAIL
remains; missing ribbon_spec downgraded to WARN so out-of-scope cities do
not regress (M2 is Cleveland-only per spec D7).

## UE bake (T5) — BLOCKED, not verified

`tools/ue5-bake-road-ribbons.py` is committed and py_compile-clean but the
headless bake was NOT executed: host had 6.0 GB free / 31.3 GB total RAM at
attempt time (M1(c) blocker — UBT/editor processes are OOM-killed well above
that). No in-map evidence exists. Do not claim M2 visuals until the bake
runs and per-spawn screenshots are captured.

Run when RAM allows:

```
UnrealEditor-Cmd.exe apps\unreal-akron-beta\raceGPSAkronBeta.uproject ^
  -run=pythonscript -script="tools/ue5-bake-road-ribbons.py" -- ^
  citypacks/cleveland/burke_gp_1997 /Game/Maps/Cleveland5_0KmWorld ^
  -unattended -nop4 -nullrhi -log
```

## Plan deviations log

- T2: Chaikin output count is `2*len(pts)` (2 per segment + 2 endpoints),
  not the plan's `2n-2`; test corrected.
- T4: mixed-pack junction emission added (above).
- T5: per-ribbon `base_z = layer * 5.0` m; fail-closed check moved BEFORE
  map save; spawned actor's default root reused; `M_RoadRibbon` created via
  `create_night_mats_v13.py` idioms (`create_skyline_backdrop_mat.py` does
  not exist in this worktree).
- T6: validator gained an optional positional pack-dir arg (plan's step-4
  usage); positional packs without a semantic manifest run pack-level checks
  only; missing ribbon_spec = WARN instead of FAIL for out-of-scope cities.
