# Phase C Pack 01 — Epic Chaos vehicle setup

**Lane focus:** Vehicle Arcade (primary) · Race Systems skim  
**Date checked:** 2026-09-25  
**raceGPS weave:** UE 5.7 · CruiseSprint GlobalDefaultGameMode · Gate 1 HOLD · Burke EZ + skyline + Lake Erie bar · countdown→racing→finish HUD→R · no editor/PIE during training

---

## Source URL(s) + license

| Field | Value |
|-------|-------|
| **Title** | How to Set up Vehicles in Unreal Engine |
| **URL** | https://dev.epicgames.com/documentation/unreal-engine/how-to-set-up-vehicles-in-unreal-engine |
| **License** | Epic documentation (EULA for engine use) |
| **UE note** | Doc page labeled 5.8 family when fetched; apply to raceGPS **5.7** and verify locally when editor reopens |
| **Related API** | https://dev.epicgames.com/documentation/unreal-engine/API/Plugins/ChaosVehicles/UChaosVehicleMovementComponent |
| **Optional VA tip** | KinetiForge README (MIT) — https://github.com/myoozy/KinetiForge-Vehicle-System — tune *ideas* only; do not replace Chaos |

---

## What to read (sections)

1. Enabling the Chaos Vehicles Plugin (Physics category → ChaosVehiclesPlugin; restart editor; incompatible with PhysX Vehicles path).
2. Creating and Editing Chaos Wheel Blueprints (`ChaosVehicleWheel`: axle type, radius cm, handbrake / engine / steering flags, max steer angle).
3. Torque curve Float Curve (RPM on X, torque NM on Y; typical inverted-U).
4. Physics Asset for vehicle mesh (sphere wheel primitives; strip collision from suspension bones).
5. Animation Blueprint with **Wheel Controller** (parent `VehicleAnimationInstance`).
6. Vehicle Blueprint (`WheeledVehiclePawn`): mesh + anim class + Simulate Physics; Wheel Setups bone names; torque curve on movement component.
7. Control inputs: Set Throttle / Brake / Steering / Handbrake (and optional pitch/roll/yaw, gear up/down).
8. Game Mode Default Pawn Class — **read for pattern only**; raceGPS keeps **CruiseSprint** as GlobalDefaultGameMode (Showcase override only).

---

## Key lessons

- Chaos Vehicles is a **plugin stack**, not a single prefab: wheel BPs + torque curve + physics asset + anim Wheel Controller + wheeled pawn + movement inputs must agree on bone names and radii.
- Front vs rear axle behavior is data-driven per wheel BP (steering vs drive vs handbrake), not by array order — keep a fixed FL/FR/BL/BR convention so index access stays sane.
- Spring Arm + Camera on the pawn should **not** use Pawn Control Rotation if you want chase locked to the car, not free-look PC yaw.
- Official setup still shows legacy Project Settings **Input** axis wiring in places; raceGPS prefers **Enhanced Input** (see pack 02) feeding the same movement setters.
- Arcade feel still lives on Chaos properties (mass, COM, friction, springs, torque curve). Community Reddit tips are hypotheses — measure in-project later. KinetiForge’s “input smoothing matters” and LSD-lock feel are useful *mental models*, not a stack swap.

---

## Steal for raceGPS

| Target | Steal |
|--------|-------|
| **Vehicle** | Confirm ChaosVehiclesPlugin enabled; wheel radius/bone alignment; torque curve present; throttle/steer/brake/handbrake reach `UChaosVehicleMovementComponent`. |
| **Session / Gate 1** | Default pawn class for *race maps* can point at the wheeled pawn without changing GlobalDefaultGameMode away from CruiseSprint — use map/Showcase override only. |
| **Burke** | Tune on a flat pad first (genre-car-racing skill), then re-check on EZ ribbon; do not retune the whole city to hide a wheel radius mismatch. |

---

## Do not steal / anti-patterns

- PhysX Vehicles plugin path; motorcycle setups; wholesale replacement of the raceGPS vehicle stack.
- Marketplace / Fab paid packs (R-Tune, Advanced Vehicle System) — kill list.
- Treating KinetiForge, NebulousVehicle, or VehicularCombat as drop-in Chaos replacements.
- Claiming vehicle “works” under NullRHI / black void.

---

## Lane tips

### Vehicle Arcade
Extend the existing Chaos wheeled pawn. Feel target: Midnight Club / Midnight Run, not iRacing. Change one coherent set of params (mass/COM/friction/springs or torque curve) and compare a fixed flat-pad scenario before blaming the track.

### Race Systems
Ensure restart (R) restores a safe pose and clears unsuitable velocity/input without advancing checkpoints. Input authority should survive pawn respawn (pack 02).

### Unreal PM
Evidence later must show real rendered chase/side stills, not compile success. Plugin enable + restart is an editor step — **frozen now**.

---

## Observable check — FUTURE (do not run now)

When game work reopens: PIE or packaged Race on a lit map — throttle moves the car, steer turns front wheels, handbrake locks rears, camera stays readable; log shows no ChaosVehiclesPlugin missing. Screenshot chase + ¾ car on Burke EZ with skyline/Lake Erie in frame. **NullRHI / black void = FAIL.**
