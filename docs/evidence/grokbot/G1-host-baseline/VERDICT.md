# G1 VERDICT — Host baseline + D1 bundle reconcile

**Verdict:** PASS  
**Claim level:** REPRODUCED_LOCALLY / OBSERVED  
**Host:** omni (14689435-c6b8-4643-bec2-a7b74d7e5dae)  
**Completed (America/New_York):** 2026-09-07 ~18:00 ET  
**Gates claimed:** G1 only (G2–G5 not claimed)

## Exact commits
| Ref | Commit |
|---|---|
| Showcase truth (untouched) | f2a8ecd6c8112141e5297ec2cce640ab42db4014 `feature/cleveland-showcase-demo` |
| Integration worktree HEAD | 0ad434c2ba6d3f8c246c34fcf4d93f8653df57f3 `grokbot/cleveland-integration` |
| master | b56b6c814c23423d13b7683607d0da5ba89130f2 |
| merge-base(f2a8ecd, 0ad434c) | ce188051f253dc6910698ab71558645c43b3be89 |
| Bundle head | codex/d1-cleveland-build-baseline @ 0ad434c |

## Bundle
| Check | Result | Exit |
|---|---|---|
| Get-FileHash SHA256 | 9998A92C…C54592 MATCH expected | 0 |
| git bundle verify | OK (requires b56b6c8 present) | 0 |
| git fetch bundle ref | new branch fetched | 0 |

## Worktree
- Path: `C:\projects\raceGPS-grokbot-cleveland`
- Branch: `grokbot/cleveland-integration` @ `0ad434c`
- Showcase `C:\projects\racegps` left on `feature/cleveland-showcase-demo` @ `f2a8ecd`

## Host / UE
- Win11 Home 10.0.26200; Ryzen AI 9 365 10c/20t; Radeon 880M (no NVIDIA); ~31.3 GB RAM; C: ~376 GB free
- Python 3.11.15; Node v26.3.0; VS Build Tools 2022 17.14.31 (MSVC 14.44.35207)
- UE `C:\Program Files\Epic Games\UE_5.7` Build.version **5.7.4** CL 51494982 `++UE5+Release-5.7`
- Plugins: ChaosVehiclesPlugin (Experimental), CesiumForUnreal (Marketplace)

## Commands + exit codes
| Step | Exit | Notes |
|---|---|---|
| pytest tests -q | **0** | 222 passed, 7 skipped — `docs/evidence/grokbot/G1-host-baseline/pytest.log` |
| citypack_audit akron-oh-beta-001 | **1** | Known fail preserved — `akron-citypack-audit.*` (not weakened) |
| UE editor build (attempt 1) | **6** | Live Coding active (editor open) |
| Clear Live Coding + rebuild | **6** | C1083 missing WorldContentInstaller.h |
| After header + cpp API align | **0** | `ue-editor-build-final.log` Result: Succeeded |

## Bounded local fixes on worktree (not merged to showcase/master)
1. DefaultEngine.ini: added `GlobalDefaultGameMode=/Script/raceGPSAkronBeta.CruiseSprintGameMode` + GameInstanceClass (D1 lacked; showcase keep-rule)
2. Added `Public/WorldContentInstaller.h`; rewrote `WorldContentInstaller.cpp` to use existing PreflightSystem APIs (orphan cpp on D1)

## Reconcile (summary)
Diverged histories; ~270 files differ. Not clean FF either way. Showcase owns playable Cleveland C++/content/citypacks/docs; D1 owns pinned Burke OSM, build orchestration, route topology tests, next-five-gates plans/evidence. Integration order documented in `docs/grokbot/DECISION_LEDGER.md` — **no auto-merge**.

## Maps (inventory only — not playable claim)
- Worktree: AkronWorld.umap, Cleveland5_0KmWorld.umap
- Showcase also: Akron5_0KmWorld.umap

## Residual risks
- Worktree has uncommitted G1 docs + GameMode/WorldContentInstaller fixes
- iGPU-only host (Radeon 880M) may limit G4/G5 perf targets
- Akron citypack integrity still failing (expected; quarantine)
- Showcase vs D1 still diverged; cherry-pick plan not executed
- Optional remote push may fail if credentials missing
- Closed a running UnrealEditor to clear Live Coding lock during G1

## Evidence paths
- `C:\projects\raceGPS-grokbot-cleveland\docs\evidence\grokbot\G1-host-baseline\`
- `C:\projects\raceGPS-grokbot-cleveland\docs\grokbot\` (CONSTITUTION, CURRENT_STATE, RETRIEVAL_MAP, DECISION_LEDGER, GATES.json, ARCHIVE/handoff)
