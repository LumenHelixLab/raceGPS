# Phase C Pack 04 — unreal-simple-racer patterns (README / docs only)

**Lane focus:** Race Systems (primary)  
**Date checked:** 2026-09-25  
**raceGPS weave:** countdown→racing→finish HUD→R · CruiseSprint default GM · Gate 1 HOLD · **WebFetch / GitHub file read only — do not clone**

---

## Source URL(s) + license

| Field | Value |
|-------|-------|
| **Title** | ChrisVifzack/unreal-simple-racer |
| **URL** | https://github.com/ChrisVifzack/unreal-simple-racer |
| **License** | **MIT** (LICENSE verified 2026-09-25). README: *assets from Marketplace* — do **not** redistribute those assets. |
| **EngineAssociation** | **5.1** (`SimpleRacer.uproject`); plugins: ChaosVehiclesPlugin, RacingAI |
| **Fetched** | README.md + LICENSE + uproject via GitHub MCP `get_file_contents` (no clone) |

---

## What to read (sections)

From the public **README** only (this Phase C pass):

1. Project intent: simplistic vehicle movement + PID AI demo; reference for **Game Instance, Game Modes, Data Assets, Save Game**, map-selection widgets, AI Controller + Behavior Trees.
2. **Checkpoint Racing** bullet list: drive checkpoints ASAP; full lap saves time on **Game Instance**; local high score.
3. **AI with PID Control**: RacingAI plugin; dual PID for steering/speed; spline follow; Spline Selection Service — **read as deferred ideas**, not Gate 1 scope.
4. LICENSE + README asset warning before any future content copy.

Do **not** clone the repo or open Marketplace-bundled Content until Chris greens installs **and** asset licenses are re-checked.

---

## Key lessons

- A minimal race mode is **checkpoint sequence + lap validation + time stored off the pawn**. README explicitly stores lap time on the **Game Instance** — aligns with pack 02 (durable session objects).
- Framework literacy the README advertises (Game Instance, Game Modes, widgets, Save Game) is the right steal class for Gate 1’s finish HUD + R restart, not city generation.
- ChaosVehiclesPlugin appears in the uproject — same family as raceGPS vehicle direction; still verify 5.7 locally later (their association is 5.1).
- AI (PID spline follow, Behavior Trees) is packaged as a **plugin-shaped** teaching demo. Genre playbook: defer AI until loop + visual floor are green.
- Marketplace assets in an MIT repo are a common trap: **MIT covers author code**, not Epic Marketplace redistributables.

---

## Steal for raceGPS

| Target | Steal |
|--------|-------|
| **Session / Gate 1** | Checkpoint race GameMode pattern; persist best/lap time on GameInstance (or equivalent durable object); map/menu widgets as a pattern for restart/finish UX — adapted to CruiseSprint + Showcase override, not their project’s default GM wholesale. |
| **Vehicle** | Confirmation that a small Chaos-based racer separates movement from race rules. |
| **Burke** | Steal loop/timing, **not** their track/city content. |

---

## Do not steal / anti-patterns

- City generation, economy, or shipping their maps as Cleveland.
- Copying Marketplace meshes/materials from the repo.
- Behavior Tree / PID AI complexity before human countdown→finish→R works on a lit Burke scene.
- Cloning now; treating 5.1 tutorials as silent 5.7 upgrades (research-protocol: note version delta).

---

## Lane tips

### Race Systems
Map README “full lap → save time on GameInstance” onto raceGPS finish HUD + persistent best time only after valid finish. Restart must not count as a free lap advance. Keep a single timing authority (monotonic clock — genre playbook).

### Unreal PM
Cite this repo as pattern class B1 from Phase B. Any future clone goes on an explicit Chris-green install list with asset-license checklist.

### Vehicle Arcade
Ignore AI PID until asked; if studying later, treat it as control-layer lookahead, not NavMesh-as-racing-line.

---

## Observable check — FUTURE (do not run now)

When game work reopens: human drives Burke EZ, passes ordered checkpoints, finish HUD shows time, R restarts loop; best time survives restart via GameInstance/PC path. Evidence: screenshot finish HUD + log. **No Marketplace asset dump. NullRHI = FAIL.**
