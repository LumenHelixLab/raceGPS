# G2 VERDICT — Coordinates / transform truth

**Verdict:** PASS (automation contract)
**Claim level:** REPRODUCED_LOCALLY
**Host:** omni (14689435-c6b8-4643-bec2-a7b74d7e5dae), Windows 11, UE 5.7.4
**Completed (America/New_York):** 2026-09-07 ~20:03 ET
**Contract:** docs/contracts/SOURCE_TO_UNREAL_FRAME_v1.md

## Results

| Check | Result | Evidence |
|---|---|---|
| pytest full suite | 230 passed, 7 skipped (exit 0) | run in worktree, 2026-09-07 |
| UE editor build (after double-precision fix) | Result: Succeeded | ue-editor-build-double-fix.log |
| raceGPS.Frame.A.GeoToWorld.100mEast | Success | ue-automation-frame.log |
| raceGPS.Frame.A.GeoToWorld.100mNorth | Success | ue-automation-frame.log |
| raceGPS.Frame.A.RoadWidth.7m | Success | ue-automation-frame.log |
| raceGPS.Frame.A.CompassToUeYaw | Success | ue-automation-frame.log |
| raceGPS.Frame.A.PackedGeoSign | Success | ue-automation-frame.log |

Command: `UnrealEditor-Cmd.exe raceGPSAkronBeta.uproject -unattended -nop4 -nullrhi -nosound -stdout -FullStdOutLogOutput -ExecCmds="Automation RunTests raceGPS.Frame" -TestExit="Automation Test Queue Empty"` (exit 0, 5 tests performed).

## Fix applied over grok bot's uncommitted state

The 100mEast / 100mNorth tests initially FAILED. Root cause: float32 quantization.
A longitude near -81.7 has a float32 ULP of ~7.6e-6 deg (~32 cm at 41.5 deg N), so
adding a 100 m delta-longitude in float lost far more than the contract's +/-1 cm
tolerance. Fix: `UAkronXodrImporter::GeoToWorld`, `MetersPerDegreeLon/Lat` and
`GeoToWorldFromPacked` now take and compute in `double` (FVector is double-based in
UE5); the two automation tests and `FrameDiagnosticActor`'s geo cross-check compute
the delta in double. Matches the contract rule "retain double precision until the
local-coordinate subtraction". Existing float call sites promote implicitly.

## Not claimed

- Editor-ruler visual verification of `FrameDiagnosticActor` arms in PIE
  (manual step per FRAME_DIAGNOSTIC_HOWTO.md — actor compiled, not yet measured in-editor).
- G3–G5. Akron citypack audit still fails by design (exit 1, preserved).
