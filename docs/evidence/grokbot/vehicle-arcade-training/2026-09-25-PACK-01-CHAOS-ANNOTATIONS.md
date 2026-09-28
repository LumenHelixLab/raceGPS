# VA read-along -- Phase C Pack 01 (Epic Chaos vehicles)

**Annotator:** Vehicle Arcade
**Date:** 2026-09-25
**Parent pack:** `../agent-training/phase-c/01-epic-chaos-vehicles.md`
**Primary cite:** [How to Set up Vehicles in Unreal Engine](https://dev.epicgames.com/documentation/unreal-engine/how-to-set-up-vehicles-in-unreal-engine) (Epic docs; page family labeled 5.8 when fetched -- apply carefully to raceGPS **UE 5.7**)
**API cite:** [UChaosVehicleMovementComponent](https://dev.epicgames.com/documentation/unreal-engine/API/Plugins/ChaosVehicles/UChaosVehicleMovementComponent)
**Mode:** study notes only -- no editor, no PIE, no plugin toggles on omni

---

## What this pack is for (VA lane)

Own the **arcade Chaos feel** on the car we already have: throttle / steer / brake / handbrake that read as Midnight Club, plus a chase camera that stays locked to the car. Pack 01 is the official Chaos assembly checklist -- wheel BPs, torque curve, physics asset, Wheel Controller anim, wheeled pawn, movement setters.

Race Systems owns session / Enhanced Input wiring (pack 02). Course Architect owns OpenDRIVE / ribbon (pack 03). Do not freestyle into those lanes here.

---

## Steal (map to raceGPS)

1. **Plugin stack agreement** -- ChaosVehiclesPlugin + `ChaosVehicleWheel` BPs + torque Float Curve + Physics Asset + Anim BP Wheel Controller + `WheeledVehiclePawn` must agree on **bone names and wheel radii**. A radius / bone mismatch looks like "the track is wrong"; tune on a flat pad first, then re-check on Burke EZ when game work reopens.
2. **Axle flags are data** -- steering / drive / handbrake are per-wheel BP flags, not array order. Keep a fixed FL/FR/RL/RR convention so index access stays sane for AI cornering later.
3. **Chase camera** -- Spring Arm + Camera must **not** use Pawn Control Rotation if we want race-follow locked to the car (matches V16 race-follow intent: arm out, pitch down, yaw locked to vehicle).
4. **Arcade lives in Chaos params** -- mass, COM, friction, springs, torque curve. Change **one coherent set**, compare a fixed flat-pad scenario, then stop. No Chaos grind theater.
5. **Input path** -- Epic samples still show legacy Project Settings axes in places. raceGPS prefers **Enhanced Input** (pack 02 / RS) feeding the same throttle / steer / brake / handbrake setters on `UChaosVehicleMovementComponent`.
6. **GameMode** -- Default Pawn Class override is map/Showcase only. **Do not** flip GlobalDefaultGameMode away from CruiseSprint.

---

## Do not steal

- PhysX Vehicles path; motorcycle setups.
- Replacing the raceGPS Chaos stack with KinetiForge / NebulousVehicle / VehicularCombat (patterns-only -- see companion note).
- Paid Fab packs (R-Tune / AVS) -- kill-list.
- "Works" claims under NullRHI or black-void stills.
- Endless Chaos parameter thrash without a fixed comparison scenario.

---

## VA observables (FUTURE -- do not run now)

When Prototyper greens editor work again:

| Check | Pass looks like |
|-------|-----------------|
| Drive | Throttle moves car; steer turns fronts; handbrake locks rears |
| Camera | Chase readable; yaw follows car, not free-look PC |
| Visual floor | Lit Sunset + Lake Erie + Cleveland skyline in frame -- not black void |
| Log | No ChaosVehiclesPlugin missing; skeletal body materials not DefaultMaterial outline-only |
| Evidence land | `docs/evidence/grokbot/` PASS stills only (PM gates what Chris sees) |

---

## Tie-back to known raceGPS debt (docs only)

- Prior paint-floor miss: BasicShapeMaterial lacked skeletal-mesh usage flags -> DefaultMaterial outlines. Pack 01 does not fix materials; when visual work reopens, skeletal-safe body MI stays a VA prerequisite before any feel claim.
- AI cornering / crash-recovery stays **after** readable car + camera on a real Burke backdrop.
- Mild arcade handling only after the look is intentional (standing Prototyper / Unreal PM order).

---

## Hand-off

Unreal PM cross-cuts this into `agent-training/`. Optional KinetiForge README patterns: [2026-09-25-KINETIFORGE-README-PATTERNS.md](./2026-09-25-KINETIFORGE-README-PATTERNS.md).
