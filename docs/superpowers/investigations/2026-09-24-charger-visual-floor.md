# Charger visual floor - 2026-09-24

**Status:** DOOR ASSETS STAGED (disk); BP attach still required — NOT fixed in-game  
**Worktree:** `C:\projects\raceGPS-grokbot-cleveland` · `grokbot/cleveland-integration`  
**Evidence:** user screenshot (missing side doors, white seats, black void, blown bloom)

## OBSERVED

1. Content under `Content/Carla/Static/Car/4Wheeled/DodgeCharger2024/` originally had:
   - `SK_DodgeCharger2024`, `SM_DodgeCharger2024`, `Phys_*`, materials/textures
   - **Zero** `*Door*` static meshes (pre-fetch)
2. CARLA vehicle authoring (UE5 docs): door geometry is **exported/imported separately** and assembled on the vehicle Blueprint on `Door_*` bones. Chassis SK alone is expected to look doorless.
3. `AChaosVehiclePawn::CloseVehicleDoors` calls `SetMorphTarget` on bone names containing "door". That does **not** attach missing meshes and is the wrong API for CARLA door parts. Logs saying "closed 4 door bones" are misleading.
4. `EnsureShowcaseNightLights` adds point lights at 4500 intensity / 2400 cm radius per headlight; Sunset LookDirector sets `BloomIntensity = 1.85`. In a dark empty map that matches the flashbang screenshot.
5. Screenshot environment is a reflective grid + black void - not the Cleveland dressed map. Car-only / wrong map amplifies the failure.

## Attribution

`Content/Vehicles/CARLA-ATTRIBUTION.txt` - CARLA content tag **0.10.0**, CC-BY 4.0.

## Door asset obtain (2026-09-24 evening ET)

**Source:** `https://bitbucket.org/carla-simulator/carla-content` tag `0.10.0`  
(commit hash of tag: `518f45bd010c0dea7239b55eed27d01ba132934e`)

**Fetched via** Bitbucket API raw package download (same mechanism as `tools/carla-content-fetch.py` from T5):

| File | Bytes | Staged path |
|------|------:|-------------|
| SM_DodgeCharger2024_DoorFL.uasset | 718314 | `.../DodgeCharger2024/SM_DodgeCharger2024_DoorFL.uasset` |
| SM_DodgeCharger2024_DoorFR.uasset | 715772 | `.../DodgeCharger2024/SM_DodgeCharger2024_DoorFR.uasset` |
| SM_DodgeCharger2024_DoorRL.uasset | 408457 | `.../DodgeCharger2024/SM_DodgeCharger2024_DoorRL.uasset` |
| SM_DodgeCharger2024_DoorRR.uasset | 406944 | `.../DodgeCharger2024/SM_DodgeCharger2024_DoorRR.uasset` |

- UE package magic `\xc1\x83\x2a\x9e` verified on all four.
- Material SoftObjectPaths resolve to existing `Materials/MI_DodgeCharger2024_{BodyWork,Details1,Details2}`.
- **Layout note:** investigation plan said stage under `Doors/`; packages embed SoftObjectPaths at the **parent** CARLA path, so canonical files are siblings of SK (same as upstream). `Doors/README.md` holds the attach checklist.
- Asset class: **.uasset** (not FBX). Same 0.10.0 set as chassis; project EngineAssociation **5.7** — expect possible resave on first editor open (same class of issue as existing Charger assets).
- Door glass meshes exist upstream under `Glass/` but were **not** staged (optional polish).

**Blocked?** No — download succeeded. No auth wall.

## Fix plan (ordered)

### A. Doors (visual floor - required)
1. ~~Obtain Dodge Charger 2024 door static meshes from CARLA content 0.10.0~~ **DONE (disk)**
2. ~~Import under Content path~~ **DONE** (canonical sibling paths; see layout note)
3. On `BP_DodgeCharger2024`, attach FL/FR/RL/RR door meshes to door bones/sockets; closed pose by default. **→ NEXT EDITOR STEP** (see `Doors/README.md`)
4. Replace `CloseVehicleDoors` with bone-relative rotation close (or no-op if doors are static closed).
5. Verify with screenshot: no seat cavity, doors read as body panels.

### B. Lights / bloom (code - can land without door assets)
1. Cut showcase headlight intensity hard (e.g. ≤800, radius ≤800) unless Midnight preset.
2. Cap Sunset bloom ≤0.9 for playable launches.
3. Never enable showcase night lights on empty/grid maps without an environment actor.

### C. Environment
1. Playable launch must load dressed map + streets, not a void stage.
2. Next product beat: OSM downtown streets via known pipeline (Overpass → centerlines; CARLA lesson = Osm2Odr/OpenDRIVE for road logic, meshes from StreetMap or ribbon - **not** invent Chaos ribbon blind).

## Claims

| Claim | Grade |
|-------|-------|
| Door meshes absent from this worktree | WAS OBSERVED; now STAGED ON DISK |
| CARLA doors are separate assets | OBSERVED (docs + Bitbucket listing) |
| Morph CloseVehicleDoors cannot restore doors | OBSERVED |
| Lights+bloom explain void blowout | OBSERVED (code + screenshot) |
| Door .uassets obtained from tag 0.10.0 | OBSERVED |
| BP attach completed | NOT YET |
| Doors fixed in-game | **NOT YET** (fail-closed) |