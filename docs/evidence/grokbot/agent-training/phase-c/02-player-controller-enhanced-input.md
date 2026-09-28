# Phase C Pack 02 — Player Controllers + Enhanced Input

**Lane focus:** Race Systems (primary) · Unreal PM  
**Date checked:** 2026-09-25  
**raceGPS weave:** UE 5.7 · CruiseSprint GlobalDefaultGameMode · Gate 1 HOLD · race loop countdown→racing→finish HUD→R · no editor/PIE during training

---

## Source URL(s) + license

| Field | Value |
|-------|-------|
| **Title** | Player Controllers in Unreal Engine |
| **URL** | https://dev.epicgames.com/documentation/unreal-engine/player-controllers-in-unreal-engine |
| **License** | Epic documentation |
| **UE note** | Page labeled 5.8; concepts apply to 5.7 |

| Field | Value |
|-------|-------|
| **Title** | Enhanced Input in Unreal Engine |
| **URL** | https://dev.epicgames.com/documentation/en-us/unreal-engine/enhanced-input-in-unreal-engine |
| **License** | Epic documentation |
| **UE note** | Official overview (Input Actions, Mapping Contexts, Modifiers, Triggers) |

| Field | Value |
|-------|-------|
| **Title** | BP Getting started with Enhanced Input (Epic Community) |
| **URL** | https://dev.epicgames.com/community/learning/tutorials/1w4K/unreal-engine-bp-gettting-started-with-enhanced-input |
| **License** | Epic community learning |
| **Fetch note** | **Thin/empty body returned 2026-09-25** from this environment (Epic slug typo `gettting` is real). Use the official Enhanced Input doc above as the verified alternate. |

---

## What to read (sections)

**Player Controllers page (short — read all):** PC as interface between human will and Pawn; when input lives on PC vs Pawn; **PC persists, Pawn can be transient** (score/restart on durable objects).

**Enhanced Input official doc:**
1. Dynamic / contextual Mapping Contexts (add/remove at runtime; priority).
2. Core concepts: Input Actions (bool / Axis1D / Axis2D / Axis3D), trigger states (Started, Ongoing, Triggered, Completed, Canceled).
3. Input Mapping Contexts hierarchy (Action → keys → Triggers/Modifiers).
4. Modifiers (dead zone, negate, swizzle — WASD → 2D steer/throttle patterns).
5. Triggers (press, hold, chorded); Player Mappable Input Config overview.
6. Debug: `showdebug enhancedinput`; inject input for tests later.

---

## Key lessons

- Put race **score, lap timing ownership pointers, and restart intent** on objects that survive pawn death/respawn — typically **PlayerController** and/or **GameInstance**, not only the wheeled Pawn. Epic’s deathmatch score example is the racing analog.
- Complex input (drive vs UI vs pause) belongs on the PC issuing commands to the pawn (“set throttle”, “restart race”), especially if possession can change.
- Enhanced Input is **asset-based**: create Input Actions for Throttle, Steer, Brake, Handbrake, Restart; bind keys in an IMC; `AddMappingContext` on possess / begin play with a clear priority.
- Prefer a **RaceDriving** IMC while racing and a lighter **RaceUI/Finished** context when the finish HUD owns focus — remove or deprioritize drive context so R restart does not also floor the throttle.
- Legacy Action/Axis Project Settings can coexist during migration; leave an explicit note and do not bind the same key through both systems without a plan.
- Triggered vs Completed matters for Restart (R): bind restart to a discrete Triggered/Completed edge, not Ongoing every tick.

---

## Steal for raceGPS

| Target | Steal |
|--------|-------|
| **Session / Gate 1** | Single timing authority; finish HUD + R restart owned by PC/GameMode/GameInstance path that outlives the pawn. Countdown→racing→finished transitions clear about who accepts input. |
| **Vehicle** | Drive actions call Chaos movement setters; dead zones / sensitivity via Modifiers, not ad-hoc Tick hacks. |
| **CruiseSprint** | Do not replace GlobalDefaultGameMode; race-specific PC/IMC can still apply via map or game-mode override used only for Showcase/race maps. |

---

## Do not steal / anti-patterns

- Keeping best time / checkpoint progress only on a disposable Pawn.
- Mixing legacy Axis mappings and Enhanced Input on the same keys with no migration note.
- Claiming HUD/input PASS under NullRHI or a black void viewport.
- Unlocking Gate 1 because “input compiled.”

---

## Lane tips

### Race Systems
Model the loop as waiting → countdown → racing → finished → restart. Accept only expected checkpoint order and direction. Restart restores safe pose, clears velocity/input, and must not advance checkpoint progress.

### Unreal PM
Evidence for Gate 1 needs human-visible finish HUD + R on a real lit scene. Map Enhanced Input debug (`showdebug enhancedinput`) into future failure checklists.

### Vehicle Arcade
Coordinate with RS so steer/throttle Axis2D or separate Axis1D actions match Chaos expectations (usually −1…1). Input smoothing (optional KinetiForge tip) is a Modifier/curve concern, not a new physics plugin.

---

## Observable check — FUTURE (do not run now)

When game work reopens: on a real rendered Race map, finish shows HUD; pressing R restarts countdown/racing without losing session high-score storage; `showdebug enhancedinput` lists RaceDriving IMC while racing. Screenshot finish HUD + log excerpt. **Black void / NullRHI = FAIL.**
