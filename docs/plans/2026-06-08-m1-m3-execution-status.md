# raceGPS Milestones 1–3 Execution Status

Date: 2026-06-08

## Outcome Summary

Milestones 1–3 were executed to the maximum autonomous extent available from this machine.

Result:
- Milestone 2: repo-side complete and verified
- Milestone 3: repo-side complete and verified
- Milestone 1: blocked only on Unreal Editor world creation / PIE execution

This is not a vague blocker. The exact remaining blocker is:
- `apps/unreal-akron-beta/Content/Maps/AkronWorld.umap` does not yet exist as a real Unreal asset
- this machine does not currently have a usable UE 5.5 editor installation exposed at `/c/Program Files/Epic Games/UE_5.5`
- this machine does not currently expose `MSBuild` or `devenv`

## Verified Facts

### Hard blocker state
- Present: `apps/unreal-akron-beta/Content/Maps/AkronWorld.umap.placeholder`
- Missing: `apps/unreal-akron-beta/Content/Maps/AkronWorld.umap`

### Tooling state on this machine
- UE 5.5 path checked: missing
- `msbuild`: missing
- `devenv`: missing
- `cmd.exe`: present
- `powershell.exe`: present

### Repo-side validation
Command run:
`python -m pytest tests/test_levelspec.py tests/test_racegps_garage_system.py tests/test_racegps_onboarding_viability.py tests/test_racegps_ux_polish.py -q`

Result:
- `28 passed in 1.36s`

## Milestone 1 — Akron First-Drive Proof

### Completed
- verified blocker state
- verified citypack/handling preset assets exist:
  - `Content/Data/VehiclePresets/Arcade.json`
  - `Content/Data/VehiclePresets/Drift.json`
  - `Content/Data/VehiclePresets/Simulation.json`
- verified source contract for:
  - city data load path
  - route/checkpoint spawn path
  - player tuning application path
  - tutorial startup path
- prepared compile-risk and smoke-test docs
- prepared compile-failure triage doc

### Remaining
The following must be completed inside a real Unreal Editor session:
1. create/save `Content/Maps/AkronWorld.umap`
2. assign `CruiseSprintGameMode`
3. compile/open the project in Unreal
4. PIE verify menu -> spawn -> drive -> checkpoints -> tutorial

### Status
- `CONDITIONALLY READY / EDITOR BLOCKED`

## Milestone 2 — Main Menu Premium Pass

### Completed
- premium menu helper surface implemented in code
- title framing improved
- launch CTA summary support added
- drive summary support added
- vehicle class labeling support added
- version line support added
- menu binding punch-list written
- garage two-axis flow already wired and validated

### Verified by tests
- `tests/test_racegps_garage_system.py`
- `tests/test_racegps_ux_polish.py`

### Status
- `REPO-SIDE COMPLETE`

## Milestone 3 — First-Run Onboarding Completion Flow

### Completed
- preflight viability gate improved
- save-dir false-pass fixed
- onboarding completion now persists viability summary
- onboarding step subtitles exposed
- final readiness / blocked-state completion message exposed
- config directory creation before save ensured
- onboarding / compile-risk / UX docs written

### Verified by tests
- `tests/test_racegps_onboarding_viability.py`
- `tests/test_racegps_ux_polish.py`

### Status
- `REPO-SIDE COMPLETE`

## Exact Next Action To Finish Phase A

Open Unreal on a machine with UE 5.5 installed and complete these in order:
1. `docs/plans/2026-06-08-ue-compile-failure-triage.md`
2. `docs/plans/2026-06-08-ue-compile-risk-and-smoke-test.md`
3. `docs/plans/2026-06-08-ux-polish-punch-list.md`
4. create/save real `AkronWorld.umap`
5. compile
6. run PIE smoke test

## Final Phase A Verdict

- If Unreal compile + PIE succeeds after `AkronWorld.umap` creation: Phase A is complete.
- If Unreal compile or PIE fails there: the project is blocked specifically at editor/world integration, not at repo architecture or onboarding/menu code.
