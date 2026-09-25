# Charger visual floor — 2026-09-24

**Status:** ROOT CAUSE IDENTIFIED (doors); lights/bloom partial code fix  
**Worktree:** `C:\projects\raceGPS-grokbot-cleveland` · `grokbot/cleveland-integration`  
**Evidence:** user screenshot (missing side doors, white seats, black void, blown bloom)

## OBSERVED

1. Content under `Content/Carla/Static/Car/4Wheeled/DodgeCharger2024/` has:
   - `SK_DodgeCharger2024`, `SM_DodgeCharger2024`, `Phys_*`, materials/textures
   - **Zero** `*Door*` static meshes
2. CARLA vehicle authoring (UE5 docs): door geometry is **exported/imported separately** and assembled on the vehicle Blueprint on `Door_*` bones. Chassis SK alone is expected to look doorless.
3. `AChaosVehiclePawn::CloseVehicleDoors` calls `SetMorphTarget` on bone names containing "door". That does **not** attach missing meshes and is the wrong API for CARLA door parts. Logs saying "closed 4 door bones" are misleading.
4. `EnsureShowcaseNightLights` adds point lights at 4500 intensity / 2400 cm radius per headlight; Sunset LookDirector sets `BloomIntensity = 1.85`. In a dark empty map that matches the flashbang screenshot.
5. Screenshot environment is a reflective grid + black void — not the Cleveland dressed map. Car-only / wrong map amplifies the failure.

## Attribution

`Content/Vehicles/CARLA-ATTRIBUTION.txt` — CARLA content tag **0.10.0**, CC-BY 4.0.

## Fix plan (ordered)

### A. Doors (visual floor — required)
1. Obtain Dodge Charger 2024 **door static meshes** from CARLA content 0.10.0 (same tag as attribution).
2. Import under `Content/Carla/Static/Car/4Wheeled/DodgeCharger2024/Doors/`.
3. On `BP_DodgeCharger2024`, attach FL/FR/RL/RR door meshes to door bones/sockets; closed pose by default.
4. Replace `CloseVehicleDoors` with bone-relative rotation close (or no-op if doors are static closed).
5. Verify with screenshot: no seat cavity, doors read as body panels.

### B. Lights / bloom (code — can land without door assets)
1. Cut showcase headlight intensity hard (e.g. ≤800, radius ≤800) unless Midnight preset.
2. Cap Sunset bloom ≤0.9 for playable launches.
3. Never enable showcase night lights on empty/grid maps without an environment actor.

### C. Environment
1. Playable launch must load dressed map + streets, not a void stage.
2. Next product beat: OSM downtown streets via known pipeline (Overpass → centerlines; CARLA lesson = Osm2Odr/OpenDRIVE for road logic, meshes from StreetMap or ribbon — **not** invent Chaos ribbon blind).

## Claims

| Claim | Grade |
|-------|-------|
| Door meshes absent from this worktree | OBSERVED |
| CARLA doors are separate assets | OBSERVED (docs) |
| Morph CloseVehicleDoors cannot restore doors | OBSERVED |
| Lights+bloom explain void blowout | OBSERVED (code + screenshot) |
| Doors fixed in-game | NOT YET |

