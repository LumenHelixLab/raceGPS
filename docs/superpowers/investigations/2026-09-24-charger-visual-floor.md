# Charger visual floor - 2026-09-24

**Status:** DOOR+GLASS+LIGHTS MESHES STAGED; RUNTIME ATTACH CODE LANDED; **NOT visually verified**  
**Worktree:** `C:\projects\raceGPS-grokbot-cleveland` @ `grokbot/cleveland-integration`  
**Machine:** omni (`14689435-c6b8-4643-bec2-a7b74d7e5dae`)  
**Evidence:** user screenshot (missing side doors, white seats, black void, blown bloom)

## Fail-closed grades

| Claim | Grade |
|-------|-------|
| Chassis import was partial (SK/SM/Phys/mats only; no door SMs) | **OBSERVED** (disk listing pre-fetch) |
| CARLA doors are separate static meshes on Door_* bones | **OBSERVED** (CARLA UE5 content-authoring docs + Bitbucket 0.10.0 listing) |
| Morph/AnimBP `CloseVehicleDoors` cannot restore missing door geo | **OBSERVED** (code) |
| Skeleton has `Door_FL/FR/RL/RR` bones | **OBSERVED** (SK_Skeleton string dump) |
| Phys asset has no door bodies (base + 4 wheels only) | **OBSERVED** |
| Door/Lights/Glass `.uasset` obtained from tag 0.10.0 | **OBSERVED** (Bitbucket API download; UE magic `C1 83 2A 9E`) |
| Lights/bloom code reduced (700/600 head, Sunset bloom 0.85) | **OBSERVED** (commit `f596318`) |
| Runtime `EnsureCarlaChargerDoors` attaches SMs at spawn/look | **OBSERVED** (code on disk) |
| Doors fixed in PIE / packaged screenshot | **NOT YET** — needs rebuild + visual check |
| Empty-grid screenshot env vs dressed Cleveland | **OBSERVED** (screenshot + LookDirector) |

## Root cause hypothesis

1. **Primary (doors / white seats):** T5 CARLA Charger import copied chassis `SK_DodgeCharger2024` + materials but **omitted** the separate door static meshes (`SM_DodgeCharger2024_Door{FL,FR,RL,RR}`) that CARLA attaches on the vehicle BP. Chassis alone is authored doorless; interior seats read through the openings.
2. **Secondary (headlight bloom / red wheel glow):** `EnsureShowcaseNightLights` point lights + high Sunset bloom on a near-black void stage. Partially mitigated in code (`f596318`: 4500→700 lm, bloom 1.85→0.85). Not re-verified visually here.
3. **Rejected as primary:** opacity/mask materials alone (BodyWork MI still present); wrong skeletal mesh path (BP + C++ both point at `SK_DodgeCharger2024`); LOD stripping (no evidence without editor).

## Spawn path (Cleveland / Chaos)

- `ARaceGridManager` ConstructorHelpers → `/Game/Vehicles/DodgeCharger2024/BP_DodgeCharger2024` (`RaceGridManager.cpp`).
- Fallback LoadClass `BP_DodgeCharger2024_C`; else native `AChaosVehiclePawn`.
- On spawn: `CloseVehicleDoors()` → now calls `EnsureCarlaChargerDoors()`; then `ApplyVehicleLook(Look)` → `EnsureCarlaChargerMesh()` + `EnsureCarlaChargerDoors()` again (idempotent).
- Mesh: `SK_DodgeCharger2024` via CDO ConstructorHelpers + `EnsureCarlaChargerMesh`.
- Looks: Hellcat / ChargerAsphalt / ChargerSilver (grid SlotLooks).

## Inventory (Content)

```
Content/Carla/Static/Car/4Wheeled/DodgeCharger2024/
  SK_DodgeCharger2024.uasset (+ Skeleton, Phys, SM_DodgeCharger2024)
  SM_DodgeCharger2024_Door{FL,FR,RL,RR}.uasset   ← staged 2026-09-24
  SM_DodgeCharger2024_Lights.uasset              ← staged
  Glass/SM_Glass{Ext,Ext2,Int1,Int2}_Dodge2024 + door glass pieces
  Materials/MI_* BodyWork/Details/Glass/Lights + textures
  Doors/README.md (editor checklist)
Content/Vehicles/DodgeCharger2024/BP_DodgeCharger2024.uasset
Content/Vehicles/CARLA-ATTRIBUTION.txt  (keep; CC-BY 4.0)
```

Upstream listing (Bitbucket `carla-content` @ `0.10.0`): full tree includes Door SMs, Glass/, Lights, AnimBP, Parked, Cop variant.

## Code changes (this pass)

- `ChaosVehiclePawn.h/.cpp`: `EnsureCarlaChargerDoors()` runtime-attaches door/glass/lights `UStaticMeshComponent`s to `Door_*` / `Vehicle_Base` bones with `NoCollision`, closed relative transform.
- `CloseVehicleDoors()` calls Ensure + zeros door-mesh relative rotation (no longer claims morph-close success).
- Prior: showcase headlight/taillight intensity cut; Sunset bloom capped (`f596318`).

**Constraints honored:** no `GlobalDefaultGameMode` / CruiseSprint default change; CARLA attribution retained.

## What is still blocked / next human-or-agent step

1. **Rebuild** `raceGPSAkronBeta` editor target on omni (UE 5.7).
2. Launch Cleveland race via existing launcher (`LaunchClevelandRace.bat` / race override only — do not flip GlobalDefaultGameMode).
3. Confirm log: `EnsureCarlaChargerDoors attached=N missing=0` (expect N≈9 if glass+lights present; ≥4 for doors alone).
4. **Screenshot** side/3/4 view: seat cavity closed by door panels; bloom not flashbang on dressed map.
5. Optional editor polish: bake attaches into `BP_DodgeCharger2024` via `Content/Python/attach_charger_doors.py` or `Doors/README.md` click-path so CDO has doors without runtime NewObject.
6. If door meshes load but sit at wrong hinge: adjust relative transform in editor (asset pivot), not GameMode.

## Prior commits / docs

- `c14bbbe` T5 CARLA Charger import + attribution
- `d156a7d` Charger as default hero
- `c1e4688` V16 lights/ground; notes doors render open / morph fail
- `f596318` dim lights + bloom + first investigation writeup
- `e1926e8` stage door `.uasset`s + Doors/README + attrib update

## Triplanar note (paint)

`GenericMaterials/00_MastersOpt/Functions/README_TRIPLANAR_STUB.txt`: missing `MF Triplanar` can break `M_CarPaint_Master_New` samples. Runtime look swaps body onto `M_NightCarPaint` when present (often absent) or tints Body MIDs. Separate from missing-door geometry.
