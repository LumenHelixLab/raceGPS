# DodgeCharger2024 door static meshes (CARLA 0.10.0)

## Where the files actually live

Canonical copies are **siblings of the chassis**, not inside this folder:

```
Content/Carla/Static/Car/4Wheeled/DodgeCharger2024/
  SM_DodgeCharger2024_DoorFL.uasset
  SM_DodgeCharger2024_DoorFR.uasset
  SM_DodgeCharger2024_DoorRL.uasset
  SM_DodgeCharger2024_DoorRR.uasset
  SM_DodgeCharger2024_Lights.uasset
  Glass/...
```

SoftObjectPaths embed `/Game/Carla/Static/Car/4Wheeled/DodgeCharger2024/...`.
This `Doors/` directory is the attach checklist only.

Source (CC-BY 4.0): bitbucket.org/carla-simulator/carla-content @ tag **0.10.0**

## Runtime path (preferred for visual floor)

`AChaosVehiclePawn::EnsureCarlaChargerDoors()` (called from `CloseVehicleDoors` /
`ApplyVehicleLook`) `LoadObject`s the door/glass/lights static meshes and attaches
`UStaticMeshComponent`s to `Door_FL/FR/RL/RR` (alts: `Door_Front_*`) or `Vehicle_Base`.
No interactive BP edit required for PIE after a successful cook/load.

Verify log: `EnsureCarlaChargerDoors attached=N missing=0`.

## Optional editor bake into BP_DodgeCharger2024

1. Open `Content/Vehicles/DodgeCharger2024/BP_DodgeCharger2024`.
2. Confirm Mesh = `SK_DodgeCharger2024`; bones `Door_FL` / `Door_FR` / `Door_RL` / `Door_RR`
   (or CARLA Front/Back naming).
3. Add four Static Mesh components (or run `Content/Python/attach_charger_doors.py`
   via `-ExecutePythonScript=`):

   | Component | Static Mesh | Attach bone |
   |-----------|-------------|-------------|
   | Door_FL | SM_DodgeCharger2024_DoorFL | Door_FL |
   | Door_FR | SM_DodgeCharger2024_DoorFR | Door_FR |
   | Door_RL | SM_DodgeCharger2024_DoorRL | Door_RL |
   | Door_RR | SM_DodgeCharger2024_DoorRR | Door_RR |

4. Relative transform zero (closed). Collision NoCollision.
5. Compile + Save. PIE on dressed Cleveland map.
6. Do **not** change GlobalDefaultGameMode for this work.
