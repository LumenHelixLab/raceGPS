# G3 VERDICT — Cleveland course citypack

**Status:** `PASS_PROVISIONAL`  
**Claim level:** OBSERVED / REPRODUCED_LOCALLY  
**Certification:** **blocked** (dated georeferenced 2006 course plan MISSING — see `docs/evidence/grokbot/G3-prep/BURKE_SOURCE_AUDIT.md`)  
**Recorded:** 2026-09-24T18:20:14 EDT  
**Worktree HEAD (pre-commit):** `d51e5bfef04a8c0e464f3f3814cf45b8c918cd19`  
**Branch:** `grokbot/cleveland-integration`  
**Product name:** raceGPS: Cleveland Historic Circuit

## What PASSED (provisional)

- Ported Burke GP 1997 citypack from showcase (read-only source at tip `c1e4688`) into worktree.
- **Canonical path:** `citypacks/cleveland/burke_gp_1997/`
- **Apps mirror:** `apps/unreal-akron-beta/citypacks/cleveland/burke_gp_1997/` → Windows junction to canonical (single source of truth).
- Supporting artifacts ported/adapted:
  - `scripts/build_cleveland_circuit.py` (provisional metadata fields + Windows `build_info.json` path)
  - `tests/test_cleveland_circuit.py` (+ G3 provisional/coherence assertions)
  - `docs/CLEVELAND_TRACK_PROVENANCE.md` (+ G3 gate note)
  - `docs/CLEVELAND_DEMO.md`, `CLEVELAND_DEMO_TEST_PLAN.md`, `CLEVELAND_ENVIRONMENT.md`
- Pack files present: xodr, racing_line.json, checkpoints.json, metadata.json, manifest.json, environment/skyline/water/track_dressing.
- `metadata.json` marks `status=PROVISIONAL`, `certification=blocked`, years `1997-2007`, length target `3389` m, clockwise 10 turns, display_name `Cleveland Historic Circuit`; explicitly not 1982 / not certified 2006.
- Pinned contemporary OSM remains at `data/sources/cleveland-burke/` (context-only).
- Frame A contract honored by reference (`docs/contracts/SOURCE_TO_UNREAL_FRAME_v1.md`); pack stores WGS84 lon/lat; no meter leftovers introduced into cm world wiring in this gate.
- **Default GameMode / CityId unchanged:** `CruiseSprintGameMode` / `akron-oh-beta-001`.
- Akron citypack audit still fails closed with **exit 1** (by design; not weakened).

## Verification (REPRODUCED_LOCALLY)

| Check | Exit | Notes |
|---|---|---|
| `pytest tests/test_cleveland_circuit.py -v` | **0** | 7 passed |
| `pytest -q` (full suite) | **0** | 237 passed, 7 skipped |
| `python scripts/citypack_audit.py citypacks/akron-oh-beta-001` | **1** | Preserved fail-closed Akron audit |
| UE editor build | **SKIPPED** | No C++/Default*.ini changes in G3 |
| PIE / XODR import automation | **SKIPPED** | Documented OBSERVED file presence + pytest only |

Logs: `pytest_cleveland.log`, `pytest_full.log`, `citypack_audit_akron.log`, `pack_inventory.json`, `path_coherence.txt`, `exits.txt`.

## What is NOT claimed

- **NOT** G3 CERTIFIED / surveyed 2006 racing line.
- **NOT** photoreal skyline / certified geometry.
- **NOT** a change of global default citypack away from Akron.
- **NOT** G4 packaging / lighting benchmarks.
- **NOT** G5 EndRace / multi-car AI scope.

## Blockers remaining for full certification

Dated georeferenced 2006 course plan remains **MISSING**. Cross-link: `docs/evidence/grokbot/G3-prep/BURKE_SOURCE_AUDIT.md`.

## Pack path policy

One source of truth at repo-root `citypacks/cleveland/burke_gp_1997/`. Unreal apps tree uses a directory junction; do not maintain a second divergent copy. Runtime CityId stays Akron unless explicitly overridden via `racegps.CityId` / `CitypackDir` (opt-in; not part of this gate's default).