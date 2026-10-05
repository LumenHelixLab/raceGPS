# Race-Loop Agent

Overseer: [Gameplay-Loop](../gameplay.md). Week 1: **LIVE**.

## Role

Prove `CruiseSprintGameMode` end-to-end on a stock placeholder level: checkpoints, scoring, results, ghost/leaderboard. Independent of real Akron geometry.

## Allowed

`CruiseSprintGameMode`, `CheckpointGate`, `RaceScoringSystem`, `LeaderboardSystem`, `RaceReplayManager` / `GhostVehicle`. A hardcoded placeholder checkpoint course when no CityPack is loaded. Automation tests in `Private/Tests/raceGPSGameplayTests.cpp`.

## Forbidden

Real Akron geometry. CARLA assets. Course validation gated on average speed, collision count, or a mandatory loop. Requiring `AkronWorld.umap` (Section 2.2, still closed).

## Input

Existing C++ game mode. Placeholder / box level.

## Output

Placeholder-safe spawn → countdown → racing → checkpoints → finish → results. Tests that exercise the **loop**, not only scoring math.

## Failure

If the UE editor is missing, ship the automation slice and record PIE as not passed in STATUS. Do not claim Section 2.2.
