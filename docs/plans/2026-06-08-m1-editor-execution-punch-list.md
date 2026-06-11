# Milestone 1 Editor Execution Punch-List

Goal
- Open Unreal once.
- Get to a clear `WORKING` or `BLOCKED` verdict fast.
- Do not spend time polishing anything before the verdict.

Scope
- Project: `D:/projects/racegps/apps/unreal-akron-beta/raceGPSAkronBeta.uproject`
- Known blocker candidate: `Content/Maps/AkronWorld.umap` is missing.
- Placeholder only exists: `Content/Maps/AkronWorld.umap.placeholder`

## Stop Rules
- If compile fails: stop and capture the first real compiler error.
- If `AkronWorld.umap` cannot be created/saved: stop and capture the save/error dialog text.
- If PIE reaches menu but route/checkpoints never appear: stop and capture the first relevant Output Log error/warning.

## Ordered Operator Checklist

1. Open the project
- Open `D:/projects/racegps/apps/unreal-akron-beta/raceGPSAkronBeta.uproject` in UE 5.5.
Pass
- Project opens to editor.
Fail
- Capture: full startup error dialog text or missing-plugin/missing-module message.

2. Compile immediately
- Use the editor Compile button before opening blueprints or PIE.
Pass
- Compile completes with no C++ errors.
Fail
- Verdict: `BLOCKED - COMPILE`
- First evidence to capture:
  - first compiler error line
  - file path named in that first error
  - whether it is in one of these files:
    - `Source/raceGPSAkronBeta/Private/OnboardingManager.cpp`
    - `Source/raceGPSAkronBeta/Private/MainMenuWidget.cpp`
    - `Source/raceGPSAkronBeta/Private/CruiseSprintGameMode.cpp`
    - `Source/raceGPSAkronBeta/Public/MainMenuWidget.h`
    - `Source/raceGPSAkronBeta/Public/CruiseSprintGameMode.h`

3. Create the real AkronWorld map if it does not already exist
- Check Content Browser: `Content/Maps/AkronWorld.umap`
- If missing, create a new level and save exactly as `Content/Maps/AkronWorld.umap`.
Pass
- Real `AkronWorld.umap` now exists and opens.
Fail
- Verdict: `BLOCKED - MAP CREATION`
- First evidence to capture:
  - exact save path attempted
  - exact editor error dialog text

4. Assign the game mode on AkronWorld
- Open `AkronWorld`.
- In World Settings, set GameMode override to `CruiseSprintGameMode`.
Pass
- World Settings shows `CruiseSprintGameMode`.
Fail
- Verdict: `BLOCKED - GAMEMODE`
- First evidence to capture:
  - missing-class text or dropdown absence

5. Add only the minimum world shell if the level is empty
- Add:
  - `DirectionalLight`
  - `SkyLight`
  - sky/atmosphere actor
  - `PostProcessVolume`
  - `PlayerStart`
- Save.
Pass
- Level is saveable and not totally empty.
Fail
- Verdict: `BLOCKED - WORLD SHELL`
- First evidence to capture:
  - first actor/add/save error shown by editor

6. Verify MainMenu required bindings before PIE
- Open the MainMenu widget blueprint if it exists in content.
- Verify these widget bindings exist exactly:
  - `RouteSelector`
  - `VehicleSelector`
  - `HandlingSelector`
  - `VehicleInfoText`
  - `HandlingInfoText`
  - `PlayButton`
Pass
- All six exist.
Fail
- Verdict: `BLOCKED - MENU BINDINGS`
- First evidence to capture:
  - first missing binding name
  - blueprint compile error text if any

7. Run one PIE smoke test
- Start PIE.
Pass checkpoint A: menu
- Route selector visible
- Vehicle selector visible
- Handling selector visible
- Handling info text changes when switching `Arcade` / `Drift` / `Simulation`
Fail evidence
- first missing widget or first Output Log error

8. In the same PIE session, start gameplay
Pass checkpoint B: world load
- no immediate crash
- `AkronWorld` loads
- player pawn exists
- vehicle spawns at a sane location
Fail evidence
- first crash/assert/dialog text or first Output Log error

9. In the same PIE session, trigger race start
Pass checkpoint C: race proof
- route spline appears
- checkpoints appear
- countdown starts/finishes
- throttle and steering work
- tutorial appears on first race start
Fail evidence
- first missing runtime element
- first relevant Output Log error mentioning route/checkpoint/tutorial/data load

## Fast Verdict

Mark `WORKING` only if all are true
- project opens
- compile passes
- real `AkronWorld.umap` exists
- `CruiseSprintGameMode` is assigned
- menu shows route/vehicle/handling controls
- PIE reaches drivable gameplay
- route + checkpoints + tutorial appear

Mark `BLOCKED` at the first failed step with one of these labels
- `BLOCKED - OPEN`
- `BLOCKED - COMPILE`
- `BLOCKED - MAP CREATION`
- `BLOCKED - GAMEMODE`
- `BLOCKED - WORLD SHELL`
- `BLOCKED - MENU BINDINGS`
- `BLOCKED - PIE WORLD`
- `BLOCKED - RACE FLOW`

## Highest-Value Failure Evidence
- One screenshot only if needed, but text first.
- Capture the first real error, not the cascade.
- Prefer these sources in order:
  1. modal error dialog text
  2. first compiler error line
  3. first Output Log error/warning tied to the failing step
  4. exact missing asset/class/binding name

## Known Pre-Session Truth
- Present: `D:/projects/racegps/apps/unreal-akron-beta/Content/Maps/AkronWorld.umap.placeholder`
- Missing: `D:/projects/racegps/apps/unreal-akron-beta/Content/Maps/AkronWorld.umap`
- Repo-side tests were already green; Milestone 1 is blocked only on real editor validation.
