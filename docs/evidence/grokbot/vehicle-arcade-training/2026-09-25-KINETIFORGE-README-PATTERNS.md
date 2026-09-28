# VA optional note -- KinetiForge README patterns (not a stack swap)

**Annotator:** Vehicle Arcade
**Date:** 2026-09-25
**Cite:** https://github.com/myoozy/KinetiForge-Vehicle-System (MIT; README fetched 2026-09-25)
**Phase B keeper path (authoritative table):** `github.com/myoozy/KinetiForge-Vehicle-System`
**Mode:** README patterns only -- **no clone**, no plugin install, no Marketplace

---

## Why this note exists

Pack 01 already says: Chaos stays the vehicle stack. KinetiForge is an optional **mental-model** source for arcade-adjacent tuning ideas (input smoothing, LSD lock feel, async-physics discipline). It is **not** a drop-in replacement for Epic Chaos Vehicles.

---

## Steal as ideas only

| README idea | VA translation on Chaos |
|-------------|-------------------------|
| Input smoothing / curves matter more than raw tire model | Soften throttle and steer attack into Chaos setters (Enhanced Input modifiers / interp) -- Midnight Club readability |
| LSD lock ratio hugely changes feel | Approximate with Chaos differential / traction helpers if present; otherwise treat as how sticky power is to the driven axle and change one param set |
| Async physics + stable fixed dt | When editor reopens: prefer stable physics timing over thrashing substep knobs; measure before claiming |
| Componentized drive-assembly thinking | Keep our wheeled pawn coherent (wheels + torque + movement component) -- do not rebuild as a second vehicle framework |

---

## Explicitly do not steal

- Pacejka / TMeasy tire stack as the product goal -- that is **sim**, not Midnight Club arcade.
- Requiring 90-120 Hz async physics as a gate for fun -- arcade feel first on the existing Chaos pawn.
- Starter / stall / turbo / anti-lag fidelity -- out of VA race-base scope.
- Full suspension linkage solvers (MacPherson / wishbone) as a rewrite of Chaos wheels.
- Cloning the repo or enabling the plugin until Chris greens installs.

---

## Kill-list adjacency

Paid Fab R-Tune / AVS and cracked mirrors stay rejected (Phase B kill-list). KinetiForge is MIT and a keeper for **patterns**; keep it cite-and-path until an install gate opens.

---

## Observable (FUTURE)

If Chris ever greens a KinetiForge spike: one-page cite-and-path + A/B stills vs Chaos baseline on the same flat pad -- Chaos remains default unless Prototyper locks a swap. Until then: **Chaos only**.
