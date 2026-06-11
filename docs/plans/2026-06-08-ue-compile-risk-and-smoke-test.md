# raceGPS Unreal Editor Compile-Risk Audit + Smoke Test

Goal
- Get to a fast yes/no on whether Akron Beta is editor-viable.
- Catch compile/setup issues before wasting time in PIE.

## Compile-Risk Audit

### Risk 1 — UMG bindings missing in Main Menu Blueprint
Impact
- High runtime risk, low compile risk.

Why
- C++ now expects optional widgets:
  - HandlingSelector
  - HandlingInfoText
- If the UMG blueprint is not updated, compile may succeed but the premium two-axis garage UX will be partially absent.

Check
- Open the MainMenu widget blueprint.
- Verify these named bindings exist exactly:
  - RouteSelector
  - VehicleSelector
  - HandlingSelector
  - VehicleInfoText
  - HandlingInfoText
  - PlayButton

Pass
- All bindings exist and populate in PIE.

Fail
- Missing handling widgets means menu still opens but the new garage path is not fully functional.

### Risk 2 — JSON handling preset files missing or malformed
Impact
- Medium runtime risk.

Expected files
- Content/Data/VehiclePresets/Arcade.json
- Content/Data/VehiclePresets/Drift.json
- Content/Data/VehiclePresets/Simulation.json

Symptoms if broken
- Log warnings from LoadHandlingModePresets()
- Vehicle loads with base preset only
- Handling selector appears but has no meaningful effect

### Risk 3 — AkronWorld map still missing
Impact
- Hard blocker.

Expected file
- Content/Maps/AkronWorld.umap

If absent
- The project is not fully proven no matter how green the repo tests are.

### Risk 4 — Runtime city data path mismatch
Impact
- High runtime risk.

Current systems rely on:
- citypacks/akron-oh-beta-001/akron_semantic_manifest.json
- citypacks/akron-oh-beta-001/akron_routes.json
- generated/AkronWorld_LevelSpec.json

If any are absent, preflight should now fail clearly.

### Risk 5 — Two-axis garage merge is first-pass, not final-balanced
Impact
- Medium gameplay risk, not compile risk.

Meaning
- The game should run, but feel-balance may still be rough.
- Sports/Simulation and Truck/Drift should work conceptually, but may need tuning refinement after smoke test.

## Recommended Editor Order

1. Open project
- apps/unreal-akron-beta/raceGPSAkronBeta.uproject

2. Compile immediately from Unreal Editor
Pass condition
- No C++ compile errors.

If compile fails, inspect first these files:
- Source/raceGPSAkronBeta/Private/OnboardingManager.cpp
- Source/raceGPSAkronBeta/Private/MainMenuWidget.cpp
- Source/raceGPSAkronBeta/Private/CruiseSprintGameMode.cpp
- Source/raceGPSAkronBeta/Public/MainMenuWidget.h
- Source/raceGPSAkronBeta/Public/CruiseSprintGameMode.h

3. Open MainMenu widget blueprint
Verify widget bindings:
- RouteSelector
- VehicleSelector
- HandlingSelector
- VehicleInfoText
- HandlingInfoText
- PlayButton

4. Open or create AkronWorld
- Save as Content/Maps/AkronWorld.umap if not already real.

5. Add minimum world shell
- DirectionalLight
- SkyLight
- atmosphere / sky actor
- PostProcessVolume
- PlayerStart fallback

## Ruthless Smoke Test

### Stage A — Menu proof
Launch PIE into menu.

Pass all of these:
- Route selector visible
- Vehicle selector visible
- Handling selector visible
- Handling info text changes when switching Arcade / Drift / Simulation
- Play does not proceed if route/vehicle state is invalid

### Stage B — Persistence proof
In menu:
- choose a non-default vehicle
- choose a non-default handling mode
- exit back / restart PIE if practical

Pass
- previous vehicle selection returns
- previous handling mode returns

### Stage C — World load proof
Start play into AkronWorld.

Pass all of these:
- no immediate crash
- map loads
- player pawn exists
- vehicle spawns at a sane location
- tutorial appears on first race start

### Stage D — Race-start proof
Trigger race start.

Pass all of these:
- route spline appears
- checkpoints appear
- countdown transitions into racing
- throttle/steer/basic movement function
- selected tuning is applied

### Stage E — Viability verdict
Clearly working if:
- compile succeeds
- MainMenu bindings are complete
- AkronWorld.umap exists
- player reaches drivable route with visible checkpoints

Clearly blocked if:
- compile fails in changed files
- MainMenu UMG lacks required bindings
- AkronWorld.umap cannot be saved / loaded
- route/checkpoints fail to appear in PIE

## Repo-side verification already completed
Run from repo root:
- python -m pytest tests/test_levelspec.py tests/test_racegps_garage_system.py tests/test_racegps_onboarding_viability.py -q

Current result
- 26 passed
