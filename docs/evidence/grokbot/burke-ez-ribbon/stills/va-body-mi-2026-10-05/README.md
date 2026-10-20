# VA body MI slice — skeletal-safe Charger paint floor (2026-10-05)

**Verdict: PASS (VA body MI slice only — NOT Mode B visual PASS).**

Lit body panels on the Dodge Charger read as Hellcat-ish metallic orange in a D3D12 editor still. Not a black/DefaultMaterial silhouette / checker on the floor path. Ground / lake remain near-black (WE night mats `M_NightAsphalt` / `M_Water_Blue` / `M_NightWindow` still missing) — that does **not** fail this VA body MI slice.

## Cite (why this existed)

`docs/evidence/grokbot/burke-ez-ribbon/stills/recapture-2026-10-05/` log proves CARLA master fails SM6:

```
LogMaterial: Warning: ... M_CarPaint_Master_New.uasset: Failed to compile Material for platform PCD3D_SM6, Default Material will be used in game.
```

Prior floor fell back to `/Engine/BasicShapes/BasicShapeMaterial`, which lacks `UsedWithSkeletalMesh` → outline-only / illegal on skel. `/Game/Materials/M_NightCarPaint` was absent on disk.

## What changed

| Item | Path |
|------|------|
| Master mat | `/Game/Materials/M_BodyPaint_SkeletalSafe` — Opaque, Default Lit, `UsedWithSkeletalMesh=true`, params BaseColor / Metallic / Roughness |
| MI | `/Game/Materials/MI_ChargerBody_SkeletalSafe` — parent master, Hellcat-ish orange default |
| Creator | `apps/unreal-akron-beta/Content/Python/create_bodypaint_skeletal_safe.py` |
| C++ floor | `ChaosVehiclePawn::ApplyChargerVisualMaterialFloor` prefers MI → master → `M_NightCarPaint`; **never** assigns BasicShapeMaterial; ERROR + leave existing if all missing |
| C++ look | `ApplyVehicleLook` night-paint swap uses same preference |
| UFUNCTION | `ApplyChargerVisualMaterialFloor` now `BlueprintCallable` so editor Python can invoke + log |

**Hard locks honored:** no Chaos retune, no paint-master / Triplanar rabbit hole, no GlobalDefaultGameMode / CruiseSprint flip, no LaunchClevelandRace / Gate 1, no WE night mat edits, map not saved.

## Build

`raceGPSAkronBetaEditor Win64 Development -WaitMutex -MaxParallelActions=1 -NoUBA -NoXGE` — **Result: Succeeded** (see `ue-editor-build.log`, `ue-editor-build-ufn.log`).

Base commit during work: `9604d0b` (branch `grokbot/cleveland-integration`).

## Verify (D3D12 editor GUI, not -game / not NullRHI)

- Map: `/Game/Maps/Cleveland5_0KmWorld`
- Still: `S_car_body_paint_close.png` (1920×1080, ~393 KB)
- Log cues (from `raceGPSAkronBeta-verify2.log` / `capture_log_excerpt.txt`):
  - `raceGPS Cleveland: V17 paint floor using MI_ChargerBody_SkeletalSafe`
  - `V17 paint floor bodySlots=1 bodyMI=MI_ChargerBody_SkeletalSafe`
  - `[VA body-mi] master saved=True UsedWithSkeletalMesh=True`
  - **No** `Failed to compile Material` for `M_BodyPaint_SkeletalSafe` / `MI_ChargerBody_SkeletalSafe`
  - CARLA `M_CarPaint_Master_New` still fails SM6 (expected; not fixed by design)
- `verify_checks.json`: master_loaded, UsedWithSkeletalMesh, mi_loaded, floor_cpp_called, still ok

## Honest limitations

- Environment is pitch black (missing WE night asphalt/water/window mats + minimal lighting). Does not fail body MI if lit paint reads.
- Lower body in deep shadow in this framing; upper panels / roof / trunk show clear metallic orange specular.
- Nanite usage flag auto-set on MID at runtime (`bUsedWithNanite`) — display-only; not a compile failure.
- Packaged `raceGPSAkronBeta.exe` (cleveland-beta-20261001-r5) was still present on omni during verify (not Track A `-game`); editor released after quit.
- Local helpers `_va_body_mi_verify.py` remain untracked (leading underscore).

## Teardown

UnrealEditor / ShaderCompileWorker for this job quit via `RGPS_STILLS_QUIT=1`. Machine left with no UnrealEditor owner held by VA.
