# G5 VERDICT — physical race demo (playable beta test run)

**Status: PASS**  
**Claim level: OBSERVED / REPRODUCED_LOCALLY only**  
**Updated: 2026-09-24T19:56:10-04:00 (America/New_York)**  
**Worktree:** `C:\projects\raceGPS-grokbot-cleveland` branch `grokbot/cleveland-integration`  
**Showcase source (READ-ONLY):** `C:\projects\racegps` @ `c1e4688`  
**Certification:** BLOCKED (inherits G3 provisional Burke pack — dated 2006 plan MISSING)

## Exit bar (Chris) — results

| Requirement | Result | Evidence |
|---|---|---|
| Provisional Burke course loads | PASS | `LoadCheckpointCourse count=12`, `track=327582.8 cm`, pack `burke_gp_1997` |
| 1 player + 2 physical AI (3 Chaos cars) | PASS | `grid spawned (3 pawns)`, slots 0/1/2 `BP_DodgeCharger2024_C`, AI `RaceAIDriverController_1/2`, player possessed + auto-drive |
| Checkpoints + EndRace / complete lap | PASS | all 11 named gates + S/F wrap; `EndRace place=1/3 nextCP=12`; report `outcome=finished` |
| Launchable without changing defaults | PASS | `LaunchClevelandRace.bat` / `LaunchCleveland.bat race` map+GameMode override only |
| GlobalDefaultGameMode stays CruiseSprint | PASS | `DefaultEngine.ini` unchanged |
| CityId stays akron-oh-beta-001 | PASS | `DefaultGame.ini` unchanged |
| Sunset/Twilight/Midnight usable | PASS | race GM resolves `-ClevelandPreset=` into G4 LookDirector |

## Launch

```
apps\unreal-akron-beta\LaunchClevelandRace.bat Sunset
apps\unreal-akron-beta\LaunchClevelandRace.bat playtest
apps\unreal-akron-beta\LaunchClevelandRace.bat nullrhi Sunset
apps\unreal-akron-beta\LaunchCleveland.bat race playtest
```

GameMode override: `/Script/raceGPSAkronBeta.ClevelandShowcaseGameMode`  
Map: `/Game/Maps/Cleveland5_0KmWorld`  
Playtest flags: `-ClevelandAutoLap -ClevelandSkipIntro`

## What was ported / adapted from showcase

- Race stack: `ClevelandShowcaseTypes`, `RacingLineComponent`, `RaceAIDriverController`, `RaceGridManager`, `ClevelandShowcaseGameMode`, `ClevelandEnvironmentActor`, `RaceGPSVehicleWheels`
- `ChaosVehiclePawn` showcase drive-override + distinct Front/Rear wheel CDOs (fixes shared-WheelClass thrash)
- Content: `BP_DodgeCharger2024` + Carla Static DodgeCharger2024 + GenericMaterials masters
- Additive `BuildingMeshGenerator::AddWorldBoxBuilding` / `GetBuildingMesh` for EnvironmentActor landmarks
- LookDirector kept from G4 (Sunset/Twilight/Midnight); Showcase MidnightRun hardcode removed
- G5 recovery tune: higher crawl threshold, faster recovery, snap advances ~25 m along racing line (playtest unblocks hairpin crawls)

## EndRace proof (REPRODUCED_LOCALLY)

NullRHI `-game` auto-lap attempt2 (`logs/race-nullrhi-autolap.*`):

- start 2026-09-24T19:50:47-04:00 → end 19:55:12-04:00, **exit 0**
- `EndRace place=1/3 nextCP=12`
- `playtest report finished` → `Temp/cleveland_playtest_lap.txt` (copied to `logs/`)
- `playtest EndRace complete - RequestExit`
- Checkpoints timed (elapsed sec): T1..T10 + Start/Finish wrap at 252.90 s
- Branding: `raceGPS / Cleveland Historic Circuit` (no historic title-sponsor strings)

Attempt1 killed after hairpin crawl (`logs/race-nullrhi-autolap-attempt1-hairpin.log`) — documented, not claimed as EndRace.

## Key exits

See `logs/exits.txt`:

- UE editor Development builds: 0
- pytest cleveland: 0; pytest full: 0
- akron citypack audit: **1** (preserved fail-closed)
- nullrhi autolap attempt2: **0**

## Honesty / remaining gaps

- Course remains **PROVISIONAL** (not certified 2006).
- Auto-lap uses aggressive recovery snaps after hairpin crawls; human drive / milder AI still may stall in T1 — not chased beyond playtest EndRace bar.
- Env skyline backdrop mesh missing (box fallback); named towers 0 in this nullrhi run — additive only.
- Package cook still G4 HARD_CAP (not re-attempted in G5).
- No separate GPU still campaign in G5 (nullrhi EndRace + spawn logs sufficient for this gate).

## Non-goals observed

- Video/AI mood pipeline: PARKED (not built)
- GlobalDefaultGameMode / Akron CityId: untouched