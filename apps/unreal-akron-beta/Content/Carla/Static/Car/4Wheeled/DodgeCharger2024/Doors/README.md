# DodgeCharger2024 door static meshes (CARLA 0.10.0)

## Where the files actually live

Canonical copies are **siblings of the chassis**, not inside this folder:

```
Content/Carla/Static/Car/4Wheeled/DodgeCharger2024/
  SM_DodgeCharger2024_DoorFL.uasset
  SM_DodgeCharger2024_DoorFR.uasset
  SM_DodgeCharger2024_DoorRL.uasset
  SM_DodgeCharger2024_DoorRR.uasset
```

Reason: each package embeds SoftObjectPaths at
`/Game/Carla/Static/Car/4Wheeled/DodgeCharger2024/SM_DodgeCharger2024_DoorXX`
(CARLA content layout). Putting them under `Doors/` would break package identity
and material soft refs. This `Doors/` directory is the investigation staging
marker + attach checklist only.

Source (CC-BY 4.0): bitbucket.org/carla-simulator/carla-content @ tag **0.10.0**
- Static/Car/4Wheeled/DodgeCharger2024/SM_DodgeCharger2024_Door{FL,FR,RL,RR}.uasset

Asset type: **.uasset** (same CARLA 0.10.0 / UE5.5-era packages as the
already-imported chassis). Not FBX. Same UE version constraints as
`SK_DodgeCharger2024` — open/resave in UE **5.7** editor if redirectors warn.

Material deps already present under `Materials/`:
MI_DodgeCharger2024_BodyWork, Details1, Details2.

Door glass (optional polish, not staged): `Glass/SM_DoorGlass_*_{FL,FR,RL,RR}.uasset`
still only on Bitbucket.

## Editor attach steps — BP_DodgeCharger2024

Doors are **not** fixed in-game until these steps are done in Unreal Editor.

1. Open `Content/Vehicles/DodgeCharger2024/BP_DodgeCharger2024`.
2. Confirm Mesh uses `SK_DodgeCharger2024` and skeleton has bones:
   - `Door_Front_Left`, `Door_Front_Right`, `Door_Back_Left`, `Door_Back_Right`
   (CARLA naming; if bone names differ, use skeleton tree / Physics asset).
3. Add four **Static Mesh** components parented to the vehicle Mesh (or to the
   matching door bones via Attach Parent / Socket):

   | Component name   | Static Mesh                         | Attach bone / socket |
   |------------------|-------------------------------------|----------------------|
   | Door_FL          | SM_DodgeCharger2024_DoorFL          | Door_Front_Left      |
   | Door_FR          | SM_DodgeCharger2024_DoorFR          | Door_Front_Right     |
   | Door_RL          | SM_DodgeCharger2024_DoorRL          | Door_Back_Left       |
   | Door_RR          | SM_DodgeCharger2024_DoorRR          | Door_Back_Right      |

4. Relative transform: location/rotation **zero** (closed pose). Snap visually
   if hinge pivot needs a small offset.
5. Collision: QueryOnly or NoCollision for visual floor; do not double-collide
   with chassis physics.
6. Compile + Save BP. PIE on dressed Cleveland map (not empty grid).
7. Verify screenshot: side panels close the seat cavity; no missing-door holes.
8. Code follow-up (separate): replace morph-based `CloseVehicleDoors` with
   bone-relative rotation or no-op if doors stay statically closed.

Do **not** change GlobalDefaultGameMode for this work.
