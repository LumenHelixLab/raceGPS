# RS read-along -- Phase C Pack 05 (UETrafficGame patterns)

**Annotator:** Race Systems
**Date:** 2026-09-25
**Parent pack:** `../agent-training/phase-c/05-uetrafficgame-patterns.md`
**Primary cites:**
- [ScrappyCocco/UETrafficGame](https://github.com/ScrappyCocco/UETrafficGame) -- **MIT** code; check `ASSETS.md` / CC0 claims before any future content copy
- [Wiki hub](https://github.com/ScrappyCocco/UETrafficGame/wiki) (deep wiki pages not fully fetched this pass -- do not invent content)
**EngineAssociation:** **5.5** (closer to raceGPS 5.7 than pack 04's 5.1; still note the delta)
**Mode:** README + wiki hub only -- **no clone**, no editor, no traffic-sim as Gate 1

---

## What this pack is for (RS lane)

Steal **session / round shell habits** and Chaos playground discipline -- explicit mode boundaries, Dev-build cheats/log mindset, "take the vehicle stack together" mental checklist. Gate 1 vertical slice stays: one short route, countdown, checkpoints, finish feedback, R. Traffic ghosts and multi-round economy stay deferred.

Vehicle Arcade skims Epic VehicleTemplate / Chaos setup cross-links back to pack 01. Course Architect does not adopt their city as Cleveland.

---

## Steal (map to raceGPS)

1. **Mode boundaries** -- Round/session framing shows a mode can layer on driving without replacing the vehicle stack. raceGPS analog: countdown / racing / finished / restart -- **not** Does-Not-Commute traffic ghosts for Gate 1.
2. **Chaos playground habits** -- Test transitions and input on a coherent wheeled stack before city-scale tourism. Flat pad / EZ ribbon first when editor reopens.
3. **Dev + `-log` before Shipping** -- Matches viewport-survival leads: diagnose with logs and human-visible HUD; do not sell NullRHI as PASS.
4. **Half-port ban** -- Wiki hub "take vehicles to another project" checklist (mesh, physics asset, wheel BPs, movement config travel together) -- RS respects VA ownership; do not half-port cars to "fix" session bugs.
5. **Inspiration, not map** -- README invites reuse for your own project: habits and structure, not their large map as Burke PASS evidence.

---

## Do not steal

- Promoting traffic-replay / avoid-past-selves puzzle to Gate 1 scope.
- Shipping their city screenshots as Cleveland / Lake Erie visual proof.
- Cloning before Chris greens; inventing deep wiki article content not fetched.
- Second vehicle frameworks or Marketplace peeks from kill-list threads.

---

## RS observables (FUTURE -- do not run now)

| Check | Pass looks like |
|-------|-----------------|
| Session states | Explicit in log/UI: countdown / racing / finished / restart |
| Stack | Chaos vehicle still raceGPS stack (VA), rules still RS |
| Evidence | Loop-state stills on lit Burke -- **not** UETrafficGame city shots |
| Failure mode | ViewportClosed / black void / NullRHI = FAIL, not partial |

---

## Tie-back to known raceGPS debt (docs only)

- Gate 1 HOLD remains until Prototyper greens a real Burke backdrop. Pack 05 does not reopen Showcase launches.
- Prior FAIL-closed windowed Sunset evidence stays the bar: living viewport through finish+R, not agent AutoLap / NullRHI substitutes.

---

## Hand-off

Unreal PM cross-cuts this into `agent-training/`. See also [02](./2026-09-25-PACK-02-PC-ENHANCED-INPUT-ANNOTATIONS.md), [04](./2026-09-25-PACK-04-SIMPLE-RACER-ANNOTATIONS.md).
