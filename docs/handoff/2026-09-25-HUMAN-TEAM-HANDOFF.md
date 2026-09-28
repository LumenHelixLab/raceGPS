# raceGPS — Human Game-Dev Team Handoff

**Date:** 2026-09-25 (~00:45 America/New_York)  
**From:** Unreal PM (agent) + Prototyper (overseer)  
**To:** Chris’s human Unreal / game-dev team  
**Worktree:** `C:\projects\raceGPS-grokbot-cleveland`  
**Branch:** `grokbot/cleveland-integration`  
**Tip at freeze notes:** `b5e1b4b` — `docs(evidence): G6 windowed Sunset finish+R FAIL-CLOSED ViewportClosed`  
**Engine:** Unreal Engine **5.7** on **omni**  
**Uproject:** `apps\unreal-akron-beta\raceGPSAkronBeta.uproject`

---

## 1. Product true north

**raceGPS** is an arcade street racer in the spirit of **Midnight Club / Midnight Run**:

- Human drives a car on real-feeling city streets
- Race loop: countdown → checkpoints → rivals → finish HUD → **R** restart
- Look: intentional camera, readable city, lake/skyline where Cleveland demands it
- Later: GPS / Workshop map packs — **after** the race loop feels like a game

**Not the product:** architecture scaffolding, NullRHI “proofs”, black-void screenshots, greenfield city rebuilds, or re-implementing CARLA.

### Standing preferences (Chris)

1. **Reuse existing sources** — wrap/light finished CARLA/UE street+vehicle pipelines and in-tree city packs. No CARLA rebuild. No greenfield Cleveland.
2. **No black void** — black / NullRHI / dead viewport is FAIL, never progress.
3. **Chris-facing bar before he reviews visuals again:** Burke Lakefront **EZ** track with **vivid Cleveland skyline + Lake Erie**.
4. **Gate 1 HOLD** (human finish HUD + R on Showcase) until he reopens — last agent path was blocked on `-game` ViewportClosed ~2s after Racing.

---

## 2. Why agents stopped

Chris ordered: hand off to human game-dev team, shut down all agent progress, leave an update in the project folder, write full handoff + tech/spec sheet.

All specialist agents were STOP/FREEZE’d (Course Architect, Vehicle Arcade, Race Systems, Prototyper). Omni UnrealEditor slot released. No agent should resume until Chris reopens.

---

## 3. What is actually done vs not

### Done (keep)

| Item | Notes |
|------|--------|
| Race-base MVP code commit lineage | `20bada7` era HUD / human bat / soft AI — Race Systems PASS on **code**; live human finish+R **not** proven |
| Vehicle Arcade V16 chase / Sunset lighting | Side/¾ capture and CARLA glass still open historically |
| Burke historic pack | `citypacks/cleveland/burke_gp_1997` (XODR, racing line, checkpoints, metadata) |
| Burke **EZ** data-plane | Variant `cleveland_burke_gp_1997_ez`: `racing_line_ez.json`, `checkpoints_ez.json` (~35% wider gates), `manifest_ez.json`; **shares source XODR**; reuses skyline/water/dressing/lighting JSON — no greenfield |
| Generation evidence | `docs/evidence/grokbot/burke-ez-ribbon/` — README, metrics.json, ribbon_overlay.svg |
| 2D preview tool | `tools/burke_ez_preview/` (+ omni copy noted at `C:\Users\cgp22\burke-ez-preview\preview.html`) — overhead verified; **fly-along screenshot QA failing at freeze** |
| Cleveland visual bar doc | `CLEVELAND_VISUAL_BAR.md` / in-tree playtest notes — Midnight Club framing (city left, Erie right, cars center) |
| Launch recipe (does not flip default GM) | `LaunchCleveland.bat` → map `Cleveland5_0KmWorld` + `ClevelandShowcaseGameMode` override; **GlobalDefaultGameMode stays CruiseSprint** |

### Not done (human team owns)

| Item | Blocker / last state |
|------|----------------------|
| Gate 1 unlock | Human Sunset Showcase finish HUD + R with **real scene**; evidence `finish-r-PASS.txt` + shot + log under `docs/evidence/grokbot/G6-race-base-mvp/`. Prior: ViewportClosed ~2s (`b5e1b4b`) |
| Burke EZ PIE stills | Overhead + driver proving EZ ribbon reads as a track — **not captured** |
| Burke visual floor stills | Sunset + Lake Erie + Cleveland skyline wrap/light — Vehicle Arcade never started |
| Chris-facing visual PASS | Blocked until stills exist and are not void |
| Two-app Workshop/Race + rgpack slice | Planned (`docs/superpowers/plans/2026-09-24-racegps-two-app-slice1-2.md`) but **held** behind race base / Burke bar |
| Course Architect / GPS OSM pipeline | Held |

---

## 4. Recommended human-team sequence

1. **Stabilize one editor on omni** — confirm only one UnrealEditor; project `raceGPSAkronBeta` on UE 5.7.
2. **Open Cleveland showcase without touching default GM:**
   - Prefer `apps\unreal-akron-beta\LaunchCleveland.bat` (or equivalent in this worktree)
   - Map: `/Game/Maps/Cleveland5_0KmWorld`
   - GameMode **override only:** `/Script/raceGPSAkronBeta.ClevelandShowcaseGameMode`
   - Confirm log: CruiseSprint remains GlobalDefaultGameMode
3. **Wire / verify EZ pack load** — `racing_line_ez.json` / `manifest_ez.json` beside `cleveland_burke_gp_1997`.
4. **Capture PASS stills** (Chris bar):
   - Overhead + driver: EZ ribbon readable
   - Framing: downtown/skyline south, Erie north (city left / water right / cars center per visual bar)
   - Land under `docs/evidence/grokbot/burke-ez-ribbon/` (and optional `burke-ez-visual/`)
5. **Only then** reopen Gate 1: human `LaunchClevelandRace.bat Sunset` (or current Showcase human bat), no `-ClevelandAutoLap`, prove finish HUD + R with live viewport.
6. **Defer** Workshop/rgpack/OSM until the lap feels like a game.

---

## 5. Hard constraints (do not violate)

- `GlobalDefaultGameMode` / Akron default stays **CruiseSprint** — never flip for Showcase experiments (use overrides).
- EngineAssociation **5.7**.
- One GPU / one UnrealEditor owner on omni when iterating.
- Evidence before claims — compile ≠ playable; NullRHI ≠ visual PASS.
- Reuse-only urban: wrap `burke_gp_1997` + in-tree skyline/water/Cesium-if-present; escalate only if zero reusable source.
- No merge to default branch without Chris approval.

---

## 6. Agent roster (frozen)

| Role | Responsibility when reopened |
|------|------------------------------|
| Prototyper | Overseer — priority locks |
| Unreal PM | Delivery plan, unlock criteria, specialist handoffs |
| Course Architect | Course layout / EZ ribbon / stills (not GPS pipeline) |
| Vehicle Arcade | Arcade handling, camera, visual floor, AI corners |
| Race Systems | Session/HUD/finish/restart/grid |

---

## 7. Skill / process reference

Installed agent skill: **unreal-game-dev v2.0.0** (Codex pack) — racing first playable = one vehicle, short route, countdown, checkpoints, timing, finish, restart; research-before-APIs; evidence matches claim.

---

## 8. Contacts for reopen

Ping Chris. If agents resume: Prototyper unlocks; Unreal PM re-assigns serialized editor work.
## Gate 1 resume (agent analysis, freeze-safe)
See `2026-09-25-GATE1-RESUME-PLAYBOOK.md` — windowed ViewportClosed ~2s after Racing; NullRHI ForceFinish is not PASS.

