# Cleveland beta stabilization — November 16, 2026

**Status: source fixes verified; Windows Unreal build and playable-beta acceptance remain open.**

Base: consolidated `master`, `61d0e463b7bca39f7ee8d1c926390fcf844c1be3`.
Scope: the approved Cleveland course, one player, one physical rival, contact, correct results and repeatable rematches. The earlier October 17 review predates the October 20 consolidation; its missing-merge and missing-rgpack-entry-point findings do not describe this base.

## Implemented

- One racing clock and physical progress tracker for both cars. Actual start/finish crossings determine results; finished times and final standings are frozen. Removed the player's four-metre early-finish allowance and countdown-time contamination. Rematch clears timing, progress, results and intro-camera state.
- Oriented vehicle clearance replaces double-projected world bounds, avoiding false braking during diagonal parallel passes. Recovery uses actual reverse gear and rear clearance, handles stalled/overturned cars near the racing line, and preserves occupied-space checks. Physical recovery stationing cannot jump ahead at the grid; backward displacement subtracts progress. Input mode settings are restored after override control, and braking/coasting clears additive wheel torque for both driver paths.
- An explicit `cleveland-beta` build profile validates and stages the Burke course inputs in the packaged project's lookup location, selects the Cleveland map, limits compilation to two parallel actions, and emits `Windows/Play-raceGPS.bat` for the human two-car Sunset race. It does not depend on unrelated unfinished citypacks. Dynamically loaded Charger/material asset directories are explicitly cooked.
- The installer selects the same race, rejects a missing cooked payload, uses actual filesystem paths for archives containing spaces/on another drive, and installs the already-staged payload. Explicit placeholder/demo behavior remains distinguishable.
- Portable CI covers integration branches and Linux/Windows. The launcher path test is portable; a real Node-to-Python Workshop export/validate/tamper test passes. The secret scanner no longer matches its own detection expressions and still checks tracked files, including its workflow.

## Verification on Linux

| Check | Result |
|---|---|
| Baseline Python suite before changes | 346 passed, 6 skipped |
| Final full Python suite | **379 passed, 6 skipped** |
| Native production result policy | 14 scenarios passed, compiled with C++17 and warnings as errors |
| Native production AI policy | 9 scenarios passed, compiled with C++17 and warnings as errors |
| Build orchestration tests | 20 passed; fake build executables verify command/data flow, not Unreal |
| Node workspace tests | **22 passed, 0 failed** |
| Node workspace typecheck and build | Passed |
| Changed Python files: Ruff check | Passed |
| Whitespace/error diff check | Passed |
| Secret scanner | Repository passes; 7 synthetic credential cases blocked without printing credentials |
| Unreal prerequisite check | **Blocked: Unreal 5.7 is not installed in this environment** |

Five existing skips require `akron_raw.osm`; one requires the Cleveland OSM cache. Independent cross-review found and corrected additional recovery, torque-clear, executable-selection and installer-path issues. Regression tests were observed failing before their fixes; the AI tests also rejected temporary versions reinstating the original bugs.

Whole-repository lint/format checks remain red. At this verification, Ruff reports 472 diagnostics and 128 files needing formatting (baseline lint had 482 diagnostics). These gates were retained; no repository-wide cleanup or suppressed failure is claimed. Linux tests do not certify the configured Windows jobs.

## Run the exact candidate on the Windows Unreal host

Use an isolated checkout of the candidate branch to preserve any current local work. From an existing raceGPS checkout:

```powershell
git fetch origin
git worktree add ..\racegps-beta origin/codex/beta-stabilization-2026-11-16
Set-Location ..\racegps-beta
.\BuildClevelandBeta.bat
```

Python 3.11 or later and the project's UE 5.7 toolchain/plugins are required. The batch entry point prefers the existing `.venv-grokbot` interpreter, then the Windows Python launcher. The Cleveland build path uses Python's standard library. To override engine location:

```powershell
.\BuildClevelandBeta.bat --engine "D:\Epic Games\UE_5.7"
```

The command prints the retained JSON evidence/log locations. On successful packaging, start `Windows\Play-raceGPS.bat` inside the fresh archive. The source checkout, its junctions and Unreal Editor must not be needed by that package.

Release acceptance still requires:

1. Compile the exact candidate with UE 5.7 and retain the build logs/package hash.
2. Complete a visible race with each possible winner; results must remain unchanged after the finish.
3. Exercise a parallel pass, stopped rival, rollover, reverse recovery and occupied reset location with the real car/course assets.
4. Complete five rematches, inspect car/road/material/audio presentation, and record performance on identified hardware.
5. Validate the Windows installer and launch on a machine without the source checkout.

No Windows executable, Unreal compile, installer execution, physical driving result, frame-rate figure or public-beta completion is claimed by this work record.
