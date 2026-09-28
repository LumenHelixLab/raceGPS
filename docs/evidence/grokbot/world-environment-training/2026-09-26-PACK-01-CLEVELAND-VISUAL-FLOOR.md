# WE read-along -- Pack 01 (Cleveland visual floor)

**Annotator:** World Environment
**Date:** 2026-09-26
**Parent cites (in-tree / handoff):**
- `docs\evidence\grokbot\visual-floor-2026-09-24\V16-NOTES.md` — Sunset chase + DayNightCycle attach fix (void abort history)
- `docs\evidence\grokbot\G3-cleveland-course-citypack\VERDICT.md` — pack provenance; env reuse policy
- `docs\handoff\2026-09-25-TECH-SPEC-SHEET.md` §§B–D — map axis, skyline/water reuse, PASS/FAIL still rules
- `docs\CLEVELAND_ENVIRONMENT.md` (if present in worktree) — environment pointers
- Pack files: `citypacks\cleveland\burke_gp_1997\skyline.json`, `water.json`, `environment.json`, `track_dressing.json`
- Course Architect sibling: `../course-architect-training\2026-09-25-PACK-03-OPENDRIVE-ANNOTATIONS.md` (ribbon vs hero mass split)
**Mode:** study notes only — no editor, no PIE, no Cesium install, no CARLA, no City Sample greenfield

---

## What this pack is for (WE lane)

Own the **visual floor** that makes Burke Lakefront read as Cleveland: Lake Erie north, downtown skyline south, readable lighting under Sunset / Twilight / Midnight presets. Wrap and light what is already inventoried. Do not rebuild the city.

Course Architect owns the **ribbon** (EZ racing line, gate widths, OpenDRIVE continuity). World Environment owns **hero mass** (skyline silhouette volumes, Erie nearfield water, bloom / exposure caps, material wrap). Coordinate; do not dual-edit the same JSON without Prototyper.

---

## Steal (map to raceGPS)

1. **Skyline as additive silhouette volumes** — Pack `skyline.json` (~45 volumes) is distinct from any large T10 HISM city import already on `/Game/Maps/Cleveland5_0KmWorld`. Prefer lighting and camera framing that reveal existing mass over "rebuild downtown."
2. **Lake Erie water JSON** — `water.json` nearfield is the reuse source. Keep Erie as the north horizon cue; do not replace with a new water stack while freeze holds.
3. **V16 lighting lessons (cite only)** — From `visual-floor-2026-09-24\V16-NOTES.md`: SceneRoot Movable so SkyAtmosphere / SkySphere / Clouds attach (Static-on-Movable-Sun abort → black void); Sunset sunI/skyI + AutoExposureBias lift + RecaptureSky. Steal the *diagnosis*, not a claim that current stills PASS.
4. **Midnight Club still observables (docs bar)** — When stills reopen, frames should read arcade-night / vivid city: Erie water edge, skyline mass against sky, bloom capped so headlights / skyline glow do not wash the ribbon. Feel bar stays Midnight Club / Midnight Run — not photoreal tourism.
5. **Axis / camera hygiene** — Tech sheet: X=east, Y=north, 1 uu = 1 cm in documented Cleveland pipeline. Empty north-runway frames are often camera / spawn / lighting, not proof that downtown is missing. Check framing before inventing a city rebuild.
6. **Cesium wrap-light only if in-tree** — Prefer non-Cesium in-tree skyline/water first. Do not install speculative Cesium stacks until Chris greens. If Cesium is already present in the uproject, wrap-light only; no greenfield georef rebuild.
7. **`cleveland_burke_gp_1997` wrap-light** — Canonical pack at `citypacks\cleveland\burke_gp_1997\` (apps junction). Policy from G3 VERDICT: reuse / wrap / light; certification still blocked on missing 2006 plan — that does not authorize a new citypack.

---

## Do not steal

- CARLA Cleveland rebuild or CARLA screenshots sold as raceGPS visual progress.
- City Sample greenfield / OSM tourism / Workshop two-app city builder as the visual path.
- Flipping GlobalDefaultGameMode / default CityId away from CruiseSprint / Akron.
- NullRHI or black-void captures framed as PASS.
- Owning Burke EZ ribbon edits (Course Architect) or Chaos camera arms (Vehicle Arcade) from this lane.
- StreetMap / Landscape Combinator as visual-floor substitutes before playable race unlock.

---

## FUTURE observables (do not run now)

When Prototyper greens single-editor omni work and visual lane unlock (Unlock Criteria mode B):

| Check | Pass looks like |
|-------|-----------------|
| Erie | Lake Erie readable as north horizon / nearfield water in driver or ¾ still |
| Skyline | Downtown mass / silhouette readable south of ribbon; not empty void |
| Lighting | Sunset/Twilight/Midnight preset holds; bloom capped; no Static-on-Movable void abort |
| Compose | Track remains hero value mass (CA ribbon); env supports mood (WE) |
| Evidence | PASS stills under `docs\evidence\grokbot\burke-ez-ribbon\` (and optional `burke-ez-visual\`); PM gates Chris |
| Anti | No CARLA / City Sample / NullRHI stills as raceGPS PASS |

---

## Tie-back to known raceGPS debt (docs only)

- G3 pack env files present; G3 CERTIFIED still blocked — visual wrap does not claim certification.
- V16 chase + Sunset look landed in logs historically; side/¾ stills and CARLA glass LoadErrors remain open notes, not WE rebuild tickets.
- Gate 1 HOLD + freeze: no omni editor, no PIE, no `LaunchClevelandRace` until unlock.
- Preview HTML fly-along projection bugs: course truth remains pack JSON + UE stills when unlocked.

---

## Hand-off

Unreal PM cross-cuts Wave 1 training into `agent-training\2026-09-26-WAVE1-TRAINING-QA.md`. Pack 01 is WE primary. Ribbon continuity stays CA (`course-architect-training`). Build & Engine owns editor ownership when reconnecting stills capture.
