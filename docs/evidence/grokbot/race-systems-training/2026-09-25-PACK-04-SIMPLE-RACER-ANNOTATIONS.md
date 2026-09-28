# RS read-along -- Phase C Pack 04 (unreal-simple-racer patterns)

**Annotator:** Race Systems
**Date:** 2026-09-25
**Parent pack:** `../agent-training/phase-c/04-unreal-simple-racer-patterns.md`
**Primary cite:** [ChrisVifzack/unreal-simple-racer](https://github.com/ChrisVifzack/unreal-simple-racer) -- **MIT** code; README warns Marketplace assets (do **not** redistribute). EngineAssociation **5.1** (note delta vs raceGPS **5.7**).
**Mode:** README / docs patterns only -- **no clone**, no Marketplace peeks, no editor

---

## What this pack is for (RS lane)

Steal the **minimal race-mode shape**: ordered checkpoints, lap validation, time stored off the pawn, finish/restart UX. This is pattern class B1 from Phase B -- framework literacy (Game Instance, Game Modes, widgets, Save Game), not a city or AI project.

Vehicle Arcade may later skim PID / RacingAI as deferred control ideas. Course Architect does not steal their track content for Burke.

---

## Steal (map to raceGPS)

1. **Checkpoint race GameMode pattern** -- Drive ordered CPs ASAP; full lap validates; time lands on **Game Instance** (or raceGPS session manager equivalent). Matches pack 02 durable-object lesson.
2. **Loop, not content** -- Steal timing + mode boundaries. Do **not** import their maps, Marketplace meshes, or city gen as Cleveland / Burke.
3. **Finish HUD + R as UX class** -- Map-selection / overlay widgets are a pattern for finish + restart UX under Showcase override -- adapt, do not wholesale-replace CruiseSprint.
4. **ChaosVehiclesPlugin presence** -- Confirms small Chaos racers separate movement (VA) from race rules (RS). Version is 5.1; re-verify locally only after Chris greens installs.
5. **Defer AI** -- README PID spline / Behavior Tree demo stays after human countdown -> finish -> R works on a lit Burke scene.

---

## Do not steal

- Cloning the repo or copying Marketplace-bundled Content.
- Treating MIT license as covering Epic Marketplace redistributables.
- Shipping their maps as Burke Lakefront EZ.
- Behavior Tree / PID AI complexity before Gate 1 human loop + visual floor.
- Silent 5.1 -> 5.7 upgrades without a version note (research-before-build).

---

## RS observables (FUTURE -- do not run now)

| Check | Pass looks like |
|-------|-----------------|
| CP order | Only expected checkpoint order/direction advances progress |
| Lap store | Best/lap time survives R via GameInstance/PC/session path |
| Restart | Restores pose, clears input/velocity, does **not** free-advance a lap |
| Evidence | Finish HUD still + log -- not a clone of their sample map |

**NullRHI / black void = FAIL.**

---

## Tie-back to known raceGPS debt (docs only)

- Showcase already has Menu -> Countdown -> Racing -> Finished via `URaceSessionManager` and `RaceGridManager` (3-car PLAYER/AI/AI). Pack 04 validates that shape against an OSS README -- it is not a rewrite brief.
- Any future clone needs Chris-green install list + asset-license checklist (PM owns that gate).

---

## Hand-off

Unreal PM cross-cuts this into `agent-training/`. See also [02](./2026-09-25-PACK-02-PC-ENHANCED-INPUT-ANNOTATIONS.md), [05](./2026-09-25-PACK-05-UETRAFFICGAME-ANNOTATIONS.md).
