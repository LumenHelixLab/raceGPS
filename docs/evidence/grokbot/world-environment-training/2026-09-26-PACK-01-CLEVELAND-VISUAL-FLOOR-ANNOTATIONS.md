# WE read-along — Pack 01 annotations (Cleveland visual floor)

**Annotator:** World Environment  
**Date:** 2026-09-26  
**Parent pack (primary):** [2026-09-26-PACK-01-CLEVELAND-VISUAL-FLOOR-STEAL-MAP.md](./2026-09-26-PACK-01-CLEVELAND-VISUAL-FLOOR-STEAL-MAP.md)  
**Sibling stub:** [2026-09-26-PACK-01-CLEVELAND-VISUAL-FLOOR.md](./2026-09-26-PACK-01-CLEVELAND-VISUAL-FLOOR.md) (Prototyper seed — superseded for depth by this file + STEAL-MAP)  
**Mode:** study notes only — no editor, no PIE, no Cesium install, no CARLA, no City Sample greenfield

### Parent cites (in-tree / GH / handoff)

| Cite | Why it matters |
|------|----------------|
| GH `citypacks/cleveland/burke_gp_1997/manifest.json` @ `grokbot/cleveland-integration` | `id=cleveland_burke_gp_1997`, `offline=true`, `carla_required=false`, `cesium_required=false` |
| Same dir `skyline.json` / `water.json` / `environment.json` / `track_dressing.json` | Reuse sources for hero mass + Erie + lighting pointers |
| `docs/evidence/grokbot/visual-floor-2026-09-24/V16-NOTES.md` | Static-on-Movable void abort; Sunset sunI/skyI; chase V16 RACE-FOLLOW — steal diagnosis, not PASS claim |
| `CLEVELAND_VISUAL_BAR.md` | City left / Erie right / cars center; T10 HISM already in map |
| `CLEVELAND_ENV_WIREUP.md` / `CLEVELAND_ENVIRONMENT.md` | `AClevelandEnvironmentActor` after `LoadCityPack()`; PMC offline path |
| `ClevelandLookDirector` (MidnightRun default) | Bloom/light suppress + Epic CVars — caps in STEAL-MAP |
| Handoff freeze / unlock | `2026-09-25-AGENT-FREEZE-STATUS.md`, `2026-09-25-UNLOCK-CRITERIA.md`, Wave 1 specialists brief |
| CA sibling | `../course-architect-training/` — ribbon vs hero-mass split |

---

## What this pack is for (WE lane)

Own the **visual floor** that makes Burke Lakefront read as Cleveland: Lake Erie **north**, downtown skyline **south**, readable lighting under Sunset / MidnightRun. Wrap and light what is already inventoried. Do not rebuild the city.

Course Architect owns the **ribbon** (EZ racing line, gate widths, OpenDRIVE continuity). World Environment owns **hero mass** (skyline silhouette volumes, Erie nearfield water, bloom / exposure caps, material wrap). Vehicle Arcade owns chase arm / car photographability — coordinate stills, don’t dual-own the editor slot. Do not dual-edit the same JSON without Prototyper.

---

## Steal (map to raceGPS)

1. **Skyline as additive silhouette** — Pack `skyline.json` has **`buildings` length 45**. Distinct from T10 HISM (~119k building instances on `Cleveland5_0KmWorld`). Prefer framing + materials that reveal existing mass over “rebuild downtown.” Log target when unlocked: `skyline buildings=N` with N matching JSON (**not** `skyline=1`).
2. **Lake Erie water JSON** — `water.json` nearfield (`points` / `inner_shoreline`) is the reuse source. Keep Erie as the north horizon cue; expand/tint via existing `Water_Surface` MID params only — no new water stack under freeze.
3. **V16 lighting lessons (cite only)** — DayNightCycle SceneRoot must be **Movable** so SkyAtmosphere / SkySphere / Clouds attach (Static-on-Movable-Sun abort → black void). Sunset path historically: sunI≈4.20 skyI≈2.40 + AutoExposureBias lift + RecaptureSky. Steal the diagnosis; do not claim current stills PASS.
4. **MidnightRun / LookDirector caps** — One cycle owns the frame; suppress competing DirectionalLights. Steal CVar/post caps from STEAL-MAP (`r.BloomQuality 5`, MidnightRun BloomIntensity≈2.20 / Threshold≈0.65). Do not stack extra dir-lights “for drama.”
5. **Midnight Club still observables** — When Mode B unlocks, frames must read arcade place: Erie edge, skyline ridge, cars center, bloom capped so glow doesn’t wash the ribbon. Feel bar = Midnight Club / Midnight Run — not photoreal tourism.
6. **Axis / camera hygiene** — X=east, Y=north, 1 uu=1 cm. Empty north-runway frames are usually camera / spawn / lighting, not a missing city. Check framing before inventing content.
7. **Cesium wrap-light only if in-tree** — Manifest says `cesium_required=false`. Prefer non-Cesium skyline/water first. No speculative Cesium install until Chris greens.
8. **`cleveland_burke_gp_1997` wrap-light** — Canonical pack at `citypacks/cleveland/burke_gp_1997/`. EZ line files are **local/showcase** (not on GH tip yet) — reuse shared skyline/water; Course Architect owns EZ ribbon QA.
9. **Env actor wireup** — Spawn `AClevelandEnvironmentActor` after `LoadCityPack()`; barriers via env actor, **not** `AStreetFurnitureSpawner`. No new uassets required for PMC dress.

---

## Do not steal

- CARLA Cleveland rebuild or CARLA screenshots sold as raceGPS visual progress.
- City Sample greenfield / OSM tourism / Workshop city builder as the visual path.
- Flipping `GlobalDefaultGameMode` away from CruiseSprint.
- NullRHI or black-void captures framed as PASS (incl. scratch `midnight_fix_chase.png` as negative example).
- Owning Burke EZ ribbon edits (CA) or Chaos chase arms (VA) from this lane.
- StreetMap / Landscape Combinator as visual-floor substitutes before playable-race unlock.
- Parallel evidence folder `burke-ez-visual/` — **single slot** is `burke-ez-ribbon/`.

---

## Scratch still gap notes (docs only — not PASS)

| Still class | Read |
|-------------|------|
| `cleveland_v15` hero/chase | HAS_CONTENT: night block-skyline + wet apron + lit cars; **Erie not readable**; ground undercooked — gap analysis only |
| `cleveland_v14_cesium_*` | Label ≠ Cesium terrain; silhouette era |
| `midnight_fix_chase` | Near-void FAIL — dark plane, no skyline/Erie |
| `burke-ez-ribbon/` on disk | Generation (metrics/SVG/README) only — **not** visual PASS |
| GH tip @ `b5e1b4b` | Historic pack present; EZ json / handoff / ribbon evidence **missing** remotely — local is training truth until mirrored |

---

## FUTURE observables (do not run now)

When Chris unlocks Mode B (Burke stills) and single-editor omni is free:

| Check | Pass looks like |
|-------|-----------------|
| Erie | Lake Erie readable as north horizon / nearfield in hero or chase still |
| Skyline | Downtown mass / silhouette readable south; not empty void |
| Lighting | MidnightRun or Sunset holds; bloom capped; no Static-on-Movable void abort |
| Compose | City left / Erie right / cars center (visual bar); EZ ribbon readable (CA) |
| Evidence | Hero + chase + short PASS note under `docs/evidence/grokbot/burke-ez-ribbon/` |
| Anti | No CARLA / City Sample / NullRHI stills as raceGPS PASS |

Launch contract when unlocked (Build & Engine owns bats): Showcase override only — `LaunchCleveland.bat` / documented `ClevelandShowcaseGameMode` on `Cleveland5_0KmWorld`; CruiseSprint stays GlobalDefault.

---

## Tie-back to known raceGPS debt (docs only)

- Soft gaps cleared 2026-09-26: README primary → STEAL-MAP; evidence path → `burke-ez-ribbon/` only.
- V16 chase + Sunset look landed in logs historically; side/¾ stills and CARLA glass LoadErrors remain open notes, not WE rebuild tickets.
- Gate 1 Track A = Chris attended Sunset; Modes B/D need separate unlock — WE does not spam `LaunchClevelandRace`.
- G3 env files present; visual wrap does not claim pack certification.

---

## Hand-off

Unreal PM cross-cuts Wave 1 into `agent-training/2026-09-26-WAVE1-TRAINING-QA.md`. This annotations file is WE Pack 01 study depth. Ribbon continuity stays CA. Build & Engine owns editor ownership when reconnecting stills capture. Vehicle Arcade pairs on chase framing for the same Mode B still set.
