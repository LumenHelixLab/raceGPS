# RS read-along -- Phase C Pack 02 (PlayerController + Enhanced Input)

**Annotator:** Race Systems
**Date:** 2026-09-25
**Parent pack:** `../agent-training/phase-c/02-player-controller-enhanced-input.md`
**Primary cites:**
- [Player Controllers in Unreal Engine](https://dev.epicgames.com/documentation/unreal-engine/player-controllers-in-unreal-engine) (Epic; page family labeled 5.8 when fetched -- apply carefully to raceGPS **UE 5.7**)
- [Enhanced Input in Unreal Engine](https://dev.epicgames.com/documentation/en-us/unreal-engine/enhanced-input-in-unreal-engine)
**Mode:** study notes only -- no editor, no PIE, no Showcase launches

---

## What this pack is for (RS lane)

Own the **human will** side of the race loop: who accepts input, who owns timing/score across pawn churn, and how finish HUD + R restart stay on durable objects. Pack 02 is the Epic PC + Enhanced Input checklist -- Mapping Contexts, Input Actions, Modifiers/Triggers, restart as a discrete edge.

Vehicle Arcade owns Chaos movement setters (pack 01). Course Architect owns OpenDRIVE / ribbon (pack 03). Do not freestyle into those lanes here.

---

## Steal (map to raceGPS)

1. **Durable session objects** -- Lap time, place, checkpoint progress, and restart intent live on **PlayerController / GameMode / GameInstance** (or `URaceSessionManager`), not only on the wheeled Pawn. Epic's "PC persists, Pawn can be transient" is the racing analog for finish + R.
2. **IMC swap by mode** -- `RaceDriving` IMC while countdown/racing; lighter `RaceUI` / Finished context when finish HUD owns focus. Remove or deprioritize drive context so R does not also floor throttle.
3. **Restart is an edge** -- Bind R to Triggered/Completed, never Ongoing every tick. Restart clears velocity/input, restores safe pose, and must **not** advance checkpoint progress or free-lap best time.
4. **Single timing authority** -- One monotonic clock owner for countdown -> racing -> finished. BindHud / NeonHUD only displays what that authority publishes.
5. **Showcase override only** -- Race-specific PC / IMC / HUDClass can apply via Showcase GameMode. **Do not** flip GlobalDefaultGameMode away from CruiseSprint.
6. **Human bat hygiene** -- Default `LaunchClevelandRace.bat` stays without `-ClevelandAutoLap`. AutoLap / RequestExit stay playtest-only paths.

---

## Do not steal

- Keeping best time / CP progress only on a disposable Pawn.
- Mixing legacy Axis mappings and Enhanced Input on the same keys with no migration note.
- Claiming HUD/input PASS under NullRHI, black void, or ViewportClosed ~2s after Racing.
- Unlocking Gate 1 because "Enhanced Input compiled" or BindHud logged once.

---

## RS observables (FUTURE -- do not run now)

When Prototyper greens a real Burke backdrop and editor work again:

| Check | Pass looks like |
|-------|-----------------|
| Modes | Log/UI explicit: countdown / racing / finished / restart |
| Finish HUD | On-screen time / place / finish panel readable on lit Sunset |
| R restart | Restarts Showcase loop without RequestExit (human path) |
| Input | `showdebug enhancedinput` shows RaceDriving IMC while racing; Finished context after EndRace |
| Evidence | Screenshot finish HUD + log excerpt under `docs/evidence/grokbot/` -- PM gates Chris |

**Black void / NullRHI / dead viewport = FAIL.**

---

## Tie-back to known raceGPS debt (docs only)

- Gate 1 FAIL-closed (`b5e1b4b`): windowed Sunset reached Racing then ViewportClosed ~2s. Pack 02 does not fix viewport survival; when work reopens, RS still needs a living human `-game` viewport through finish+R.
- MVP `20bada7` BindHud -> NeonHUD + EndRace / RestartShowcase is the code baseline; these notes are the theory map, not a re-implement.
- Soft AI recovery vs aggressive AutoLap snaps stays playtest vs human bat separation.

---

## Hand-off

Unreal PM cross-cuts this into `agent-training/`. Companion packs: [04](./2026-09-25-PACK-04-SIMPLE-RACER-ANNOTATIONS.md), [05](./2026-09-25-PACK-05-UETRAFFICGAME-ANNOTATIONS.md).
