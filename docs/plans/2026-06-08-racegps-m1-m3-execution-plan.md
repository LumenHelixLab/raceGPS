# raceGPS Milestones 1–3 Execution Plan

> For Hermes: execute Milestones 1–3 in order. Milestone 1 is the hard viability gate. If it fails, stop and reassess before continuing.

**Goal:** Prove the Akron first-drive slice works, then immediately make the menu and onboarding feel premium and trustworthy.

**Architecture:** Use the existing Unreal gameplay path (`CruiseSprintGameMode`, `MainMenuWidget`, `OnboardingManager`, `PreflightSystem`) as the vertical slice spine. Keep code changes minimal and verification-heavy. Treat Unreal editor work as first-class, not an afterthought.

**Tech Stack:** Unreal Engine 5.5, C++, UMG, repo-side pytest contract tests, citypack JSON assets.

---

## Milestone 1 — Akron First-Drive Proof

**Objective:** Create the real Akron world and prove the full menu -> spawn -> drive -> checkpoints path in PIE.

**Hard gate:** This milestone determines whether raceGPS is clearly working or clearly blocked.

### Task 1.1: Verify the world blocker state

**Objective:** Confirm whether the project still lacks a real Akron world.

**Files:**
- Check: `apps/unreal-akron-beta/Content/Maps/AkronWorld.umap`
- Existing placeholder: `apps/unreal-akron-beta/Content/Maps/AkronWorld.umap.placeholder`

**Step 1: Verify current file state**
- Expected current state: placeholder exists, real `.umap` does not.

**Step 2: Record the outcome**
- If real `.umap` already exists, skip directly to Task 1.3.
- If only placeholder exists, proceed to Task 1.2.

**Verification:**
- Pass = exact file truth is known before editor work begins.

### Task 1.2: Create the real AkronWorld map in Unreal Editor

**Objective:** Replace the placeholder world with a real saved level.

**Files:**
- Create: `apps/unreal-akron-beta/Content/Maps/AkronWorld.umap`
- Reference: `apps/unreal-akron-beta/BUILD.md`

**Editor Steps:**
1. Open `apps/unreal-akron-beta/raceGPSAkronBeta.uproject`
2. File -> New Level -> Empty Open World
3. Save As `Content/Maps/AkronWorld`
4. In World Settings:
   - GameMode Override = `CruiseSprintGameMode`
   - Game Instance = `raceGPSGameInstance`
5. Add PlayerStart near origin
6. Save all

**Verification:**
- Pass = `AkronWorld.umap` exists as a real Unreal asset
- Fail = only placeholder remains or map cannot be saved

### Task 1.3: Compile immediately in Unreal

**Objective:** Surface code/integration breakage before any polish work.

**Files:**
- Inspect first on error:
  - `apps/unreal-akron-beta/Source/raceGPSAkronBeta/Private/OnboardingManager.cpp`
  - `apps/unreal-akron-beta/Source/raceGPSAkronBeta/Private/MainMenuWidget.cpp`
  - `apps/unreal-akron-beta/Source/raceGPSAkronBeta/Private/CruiseSprintGameMode.cpp`
  - `apps/unreal-akron-beta/Source/raceGPSAkronBeta/Public/MainMenuWidget.h`
  - `apps/unreal-akron-beta/Source/raceGPSAkronBeta/Public/CruiseSprintGameMode.h`

**Step 1: Compile from Unreal Editor**
**Step 2: If compile fails, use:**
- `docs/plans/2026-06-08-ue-compile-failure-triage.md`

**Verification:**
- Pass = no C++ compile errors
- Fail = compile errors in changed files or dependency/config issues

### Task 1.4: Add minimum viable world shell

**Objective:** Prevent the first drive from happening in an unreadable empty void.

**Files:**
- Modify in-editor: `apps/unreal-akron-beta/Content/Maps/AkronWorld.umap`

**Editor Steps:**
- Add DirectionalLight
- Add SkyLight
- Add sky/atmosphere actor
- Add PostProcessVolume
- Confirm PlayerStart placement

**Verification:**
- Pass = world is readable enough to drive and inspect route/checkpoint behavior

### Task 1.5: Run the ruthless PIE proof

**Objective:** Prove the actual first-drive slice.

**Files / Systems:**
- `CruiseSprintGameMode`
- `AkronXodrImporter`
- route/checkpoint spawn path
- tutorial path

**PIE Pass Conditions:**
- map loads
- player pawn exists
- vehicle spawns sanely
- route spline appears
- checkpoints appear
- tutorial appears
- throttle/steer/basic movement function
- user reaches controllable drive within one minute

**Verification:**
- Pass = milestone clears the hard viability gate
- Fail = stop roadmap and reassess root cause

---

## Milestone 2 — Main Menu Premium Pass

**Objective:** Turn the menu into a premium launch surface that clearly communicates the selected experience.

### Task 2.1: Verify widget binding completeness

**Objective:** Ensure the UMG blueprint exposes all required controls and texts.

**Files:**
- Blueprint to inspect: MainMenu widget
- Code references:
  - `apps/unreal-akron-beta/Source/raceGPSAkronBeta/Public/MainMenuWidget.h`
  - `apps/unreal-akron-beta/Source/raceGPSAkronBeta/Private/MainMenuWidget.cpp`

**Required bindings:**
- `TitleText`
- `VersionText`
- `RouteSelector`
- `VehicleSelector`
- `HandlingSelector`
- `VehicleInfoText`
- `HandlingInfoText`
- `PlayButton`

**Verification:**
- Pass = all names exist and populate in PIE

### Task 2.2: Bind the premium-facing copy surfaces

**Objective:** Make the menu read like a product, not a debug tool.

**Files:**
- Uses existing code helpers from `MainMenuWidget`
- Reference: `docs/plans/2026-06-08-ux-polish-punch-list.md`

**Bind/Show:**
- TitleText -> `raceGPS — Midnight Club on real roads`
- VersionText -> `BuildVersionLine()` output
- Hero or subheading -> `BuildDriveSummaryText()`
- Play CTA/tooltip area -> `BuildLaunchButtonText()`
- Vehicle card -> vehicle + class + description + summary
- Handling card -> mode + description + launch framing

**Verification:**
- Pass = first screen immediately explains what is being driven and where

### Task 2.3: Remove ambiguous first-run states

**Objective:** Ensure the menu never looks half-filled or directionless.

**Files:**
- `MainMenuWidget.cpp`
- MainMenu blueprint

**Checks:**
- route defaults valid
- vehicle defaults valid
- handling defaults valid
- invalid selections do not silently proceed

**Verification:**
- Pass = no empty/unclear launch state for a first-time user

### Task 2.4: Run menu-only UX proof in PIE

**Objective:** Validate the menu as a user-facing surface.

**PIE Pass Conditions:**
- selected route is obvious
- selected car is obvious
- selected handling mode is obvious
- changing handling mode updates its explanation
- CTA is clear
- no debug-ish dead text or unexplained controls

**Verification:**
- Pass = user can understand the run setup at a glance

---

## Milestone 3 — First-Run Onboarding Completion Flow

**Objective:** Make onboarding feel intentional, save correctly, and end with a clean yes/no readiness verdict.

### Task 3.1: Verify onboarding blueprint can surface the new copy

**Objective:** Expose the human-quality step framing already present in code.

**Files:**
- Blueprint to inspect: Onboarding flow widget(s)
- Code references:
  - `apps/unreal-akron-beta/Source/raceGPSAkronBeta/Public/OnboardingManager.h`
  - `apps/unreal-akron-beta/Source/raceGPSAkronBeta/Private/OnboardingManager.cpp`

**Bind/Show:**
- step title
- `GetStepSubtitle(CurrentStep)` under each step
- final readiness/completion message at finish

**Verification:**
- Pass = onboarding reads like a guided flow, not an installer log

### Task 3.2: Confirm preflight verdict path is visible to the player

**Objective:** Ensure the final onboarding state is understandable.

**Files / systems:**
- `PreflightSystem`
- `OnboardingManager`
- saved `PlayerSettings.json`

**Checks:**
- success state says ready to drive
- blocked state says the build needs attention before first drive
- warnings are explained without sounding catastrophic

**Verification:**
- Pass = onboarding ends in a simple launch/no-launch understanding

### Task 3.3: Verify persistence after restart

**Objective:** Confirm first-run setup survives relaunch.

**Checks:**
- selected player/profile data persists
- selected route persists if intended
- selected vehicle persists
- selected handling mode persists
- onboarding completion does not regress on restart

**Verification:**
- Pass = user does not have to repeat setup every run

### Task 3.4: Validate blocked-state experience

**Objective:** Make failure feel clear, not broken.

**Method:**
- Use a controlled broken state if practical (e.g. missing required citypack file in a safe test branch/session)
- confirm preflight blocks launch cleanly
- confirm final message explains the issue directionally

**Verification:**
- Pass = the user gets a clean blocked message instead of a silent or confusing failure

---

## Existing Repo-Side Verification

Already green:
- `python -m pytest tests/test_levelspec.py tests/test_racegps_garage_system.py tests/test_racegps_onboarding_viability.py tests/test_racegps_ux_polish.py -q`

Current known result from repo work:
- 28 passed

These tests prove the source contract is much stronger now, but they do **not** replace Milestone 1 editor truth.

---

## Final Approval Logic

Approve Milestones 1–3 as the immediate execution phase.

Decision rule:
- If Milestone 1 fails -> stop and reassess
- If Milestone 1 passes -> execute Milestones 2 and 3 immediately

## Recommended Deliverable Sequence

1. Real `AkronWorld.umap`
2. Successful compile
3. Successful first drive in PIE
4. Premium menu binding pass
5. Premium onboarding completion pass
6. Final Phase A verdict: working / conditionally working / blocked
