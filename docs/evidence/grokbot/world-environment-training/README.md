# World Environment — training (Wave 1)

**Lane:** World Environment (Cleveland visual floor: skyline, Lake Erie, lighting, post, materials, atmosphere)
**Owner agent:** World Environment (`436d7892-1036-40de-8ca1-4732a34864ea`)
**Owner:** World Environment under Prototyper; Unreal PM gates evidence
**Rule:** cite-and-path only. No omni UnrealEditor, no PIE, no `LaunchClevelandRace`, no clones / installs until Chris unlocks.
**Source of truth (synthesis):** `../agent-training/` (Unreal PM owns cross-cut)
**Wave:** Wave 1 specialists — see `Documents\raceGPS-handoff\2026-09-26-WAVE1-SPECIALISTS.md`
**Checked:** 2026-09-26 · **Soft-gap fix:** README primary → STEAL-MAP; evidence path = `burke-ez-ribbon/` only
**Worktree (when game work reopens):** `C:\projects\raceGPS-grokbot-cleveland` · branch `grokbot/cleveland-integration` · UE **5.7**

## Files

| File | Covers |
|------|--------|
| [2026-09-26-PACK-01-CLEVELAND-VISUAL-FLOOR-STEAL-MAP.md](./2026-09-26-PACK-01-CLEVELAND-VISUAL-FLOOR-STEAL-MAP.md) | **Pack 01 (primary)** — steal map, bloom/light caps, Midnight Club still observables, citations, hard bans |
| [2026-09-26-PACK-01-CLEVELAND-VISUAL-FLOOR-ANNOTATIONS.md](./2026-09-26-PACK-01-CLEVELAND-VISUAL-FLOOR-ANNOTATIONS.md) | **Annotations** — WE read-along steal/do-not/FUTURE observables + still gap notes |
| [2026-09-26-PACK-01-CLEVELAND-VISUAL-FLOOR.md](./2026-09-26-PACK-01-CLEVELAND-VISUAL-FLOOR.md) | Sibling read-along stub (Prototyper seed) — keep for study notes; do not treat as deeper than STEAL-MAP |

## Hard constraints (raceGPS)

- **Reuse / wrap / light only.** Prefer finished CARLA/UE street+vehicle pipelines and in-tree packs (`cleveland_burke_gp_1997`, skyline/water JSON, T10 HISM already in `Cleveland5_0KmWorld`).
- **Never** rebuild CARLA. **Never** greenfield a Cleveland / City Sample tourism map.
- **NullRHI / black void / dead viewport = FAIL** — never sell as visual PASS.
- Race base / Burke bar first. GPS / Workshop streets after playable race unless Prototyper unlocks.
- `GlobalDefaultGameMode` stays **CruiseSprint**; Showcase uses documented GameMode **override** only.
- Coordinate with Course Architect on ribbons (they own racing line / EZ layout; we own env hero mass around it).
- Pair Vehicle Arcade on chase framing + car photographability when Mode B unlocks.

## Chris visual bar (scoreboard)

Burke Lakefront EZ still must read **Midnight Club / Midnight Run**: downtown/skyline **south (left of frame)**, Lake Erie **north (right)**, cars **center**. Empty north-facing runway stills are almost always **camera / spawn / lighting**, not a missing city (map already has ~120k T10 building instances + water).

## Evidence paths

| Role | Path |
|------|------|
| This lane (project) | `docs/evidence/grokbot/world-environment-training/` |
| Documents mirror | `Documents\raceGPS-handoff\world-environment-training\` |
| **Burke EZ generation + Mode B visual PASS (single slot)** | `docs/evidence/grokbot/burke-ez-ribbon/` |
| Visual floor history | `docs/evidence/grokbot/visual-floor-2026-09-24/` |
| Pack env reuse | `citypacks/cleveland/burke_gp_1997/` (`skyline.json`, `water.json`, `environment.json`, `track_dressing.json`) |

Do **not** invent a parallel `burke-ez-visual/` folder. Generation evidence already lives under `burke-ez-ribbon/`; when Mode B unlocks, land hero/chase stills + short PASS note in that same folder (Unreal PM gate).

## Freeze posture

Stand down on editor / PIE / unattended launches. Cite-and-path and annotations only until Chris (or Prototyper with Chris approval) unlocks Mode B (Burke visual stills) or full agent game.
