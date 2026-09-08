# RETRIEVAL_MAP

**Claim level:** OBSERVED

## Canonical local paths
| Artifact | Path |
|---|---|
| Showcase repo | C:\projects\racegps |
| Integration worktree | C:\projects\raceGPS-grokbot-cleveland |
| Bundle | C:\Users\cgp22\AppData\Local\Temp\raceGPS-autonomous-gates.bundle |
| Handoff (temp) | C:\Users\cgp22\AppData\Local\Temp\raceGPS-grokbot-handoff.md |
| Handoff archive | docs/grokbot/ARCHIVE/raceGPS-grokbot-handoff.md |
| UE 5.7 | C:\Program Files\Epic Games\UE_5.7 |
| Build.bat | C:\Program Files\Epic Games\UE_5.7\Engine\Build\BatchFiles\Build.bat |
| uproject | apps/unreal-akron-beta/raceGPSAkronBeta.uproject |
| G1 evidence | docs/evidence/grokbot/G1-host-baseline/ |

## Branches / commits
| Name | Commit | Role |
|---|---|---|
| feature/cleveland-showcase-demo | f2a8ecd | Showcase truth — do not overwrite |
| grokbot/cleveland-integration | 0ad434c (+ local GameMode ini patch) | D1 integration worktree |
| codex/d1-cleveland-build-baseline | 0ad434c | Bundle import ref |
| master | b56b6c8 | Bundle prerequisite base |
| merge-base(f2a8ecd, 0ad434c) | ce18805 | Diverged histories |

## Required reading precedence
1. Owner mission / this CONSTITUTION
2. docs/plans/2026-09-07-cleveland-production-v5.1.md
3. docs/plans/NEXT_FIVE_GATES_EXECUTION.md + docs/evidence/next-five-gates/
4. docs/plans/D1_EXECUTION_REPORT.md, CLEVELAND_REFERENCE_CONTRACT.md, data/sources/cleveland-burke/
5. Showcase docs under C:\projects\racegps\docs\CLEVELAND_* (present on showcase, absent on D1)

## Tools observed
Python 3.11.15, Node 26.3.0, VS Build Tools 2022 17.14.31, UE 5.7.4, ChaosVehiclesPlugin, CesiumForUnreal
