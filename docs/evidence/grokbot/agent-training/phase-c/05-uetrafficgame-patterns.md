# Phase C Pack 05 — UETrafficGame patterns (README + wiki hub)

**Lane focus:** Race Systems (primary) · Vehicle Arcade skim  
**Date checked:** 2026-09-25  
**raceGPS weave:** Chaos session playground habits · Gate 1 HOLD · **no traffic-sim as Gate 1** · **WebFetch only — do not clone**

---

## Source URL(s) + license

| Field | Value |
|-------|-------|
| **Title** | ScrappyCocco/UETrafficGame |
| **URL** | https://github.com/ScrappyCocco/UETrafficGame |
| **Wiki** | https://github.com/ScrappyCocco/UETrafficGame/wiki |
| **License** | **MIT** code (LICENSE verified 2026-09-25). README points to `ASSETS.md` for CC0 third-party assets — still verify before any future content copy. |
| **EngineAssociation** | **5.5** (`TrafficGame/TrafficGame.uproject`); ChaosVehiclesPlugin enabled; ChaosVehicles module dependency |
| **Fetched** | README.md + LICENSE + uproject via GitHub MCP; wiki hub via WebFetch (no clone) |

**Wiki fetch note:** Individual wiki article URLs (e.g. “How to set up a Vehicle”) returned the **wiki hub index** from this environment (GitHub wiki SPA). Hub lists useful Epic vehicle doc links + in-repo edit topics (Vehicles, Levels, Cheats). Treat hub + README as the verified public surface for this pack; deeper wiki pages need a browser pass later if Chris wants them — still no clone.

---

## What to read (sections)

**README:**
1. Description — playground for UE5 vehicles, Nanite/Lumen, Chaos; inspired by Epic **BP VehicleTemplate**.
2. Inspiration — round-based “avoid your past selves” traffic puzzle (Does Not Commute) **vs** free drive — know which mode is Gate 1–irrelevant.
3. Requirements / Engine Version — check uproject; ChaosVehiclesPlugin called experimental in README tone.
4. “How does it work” → points at Wiki.
5. ASSETS.md summary pointer (CC0 claim) — license hygiene for later.

**Wiki hub:**
- Vehicles: links out to Epic Vehicle Art Setup, How to set up a Vehicle, Chaos Vehicle setup/debug — good cross-link back to pack 01.
- Levels / Data Tables — session content structure *ideas*.
- Cheats for Development builds — evidence mindset (Dev + `-log` before Shipping).

---

## Key lessons

- Treat the project as a **Chaos vehicle playground + session/round shell**, not as Cleveland. README invites “take something to use on your own project” — that something is habits and structure, not their big map.
- Inspiration from Epic Vehicle Template reinforces pack 01: start from Chaos wheeled template patterns, then specialize.
- Round/session structure (drive A→B, then replay ghosts) shows how a **mode** can layer on driving without replacing the vehicle stack — raceGPS analog is countdown/racing/finished, **not** traffic ghosts for Gate 1.
- Engine **5.5** + ChaosVehicles is closer to raceGPS 5.7 than 5.1 simple-racer, but still note the delta; experimental Chaos caveats mean measure locally.
- Wiki’s “take vehicles to another project” topic (hub-listed) is the right mental checklist later: mesh, physics asset, wheel BPs, movement config travel together — do not half-port.
- Development vs Shipping builds in releases mirrors viewport-survival leads: debug with logs first.

---

## Steal for raceGPS

| Target | Steal |
|--------|-------|
| **Session / Gate 1** | Round/session framing; clear mode boundaries; Chaos playground test habits; Dev-build cheats/CVars mindset for diagnosis — applied to countdown→finish→R only. |
| **Vehicle** | Epic VehicleTemplate-oriented Chaos setup discipline; keep plugin + wheeled pawn coherent when touching cars. |
| **Burke** | Do **not** adopt their city; reuse Burke/Cleveland pipelines and visual bar. |

---

## Do not steal / anti-patterns

- Promoting the traffic-replay puzzle to Gate 1 scope.
- Shipping their large map as Cleveland or learning-tourism through Nanite city scale.
- Cloning before Chris greens; unpaid Marketplace peeks suggested by other threads (kill list).
- Assuming wiki deep pages were fully fetched this pass — do not invent wiki content.

---

## Lane tips

### Race Systems
Keep Gate 1 vertical slice: one vehicle, one short route, countdown, checkpoints, finish feedback, R. Traffic ghosts and multi-round economy stay deferred (MDA / genre playbook).

### Vehicle Arcade
Use this README as permission to **play in a Chaos sandbox mindset** on flat pads and EZ ribbon — not to import a second vehicle framework. Cross-read pack 01 Epic steps.

### Unreal PM
Phase B B2 pattern class. Evidence mapping: session structure citations → Gate 1 observables; city screenshots from this repo are not Burke PASS evidence.

---

## Observable check — FUTURE (do not run now)

When game work reopens: raceGPS session transitions are explicit in log/UI (countdown / racing / finished / restart) on a lit Burke map; Chaos vehicle still from raceGPS stack. Screenshot loop states — **not** UETrafficGame city. **NullRHI / black void = FAIL.**
