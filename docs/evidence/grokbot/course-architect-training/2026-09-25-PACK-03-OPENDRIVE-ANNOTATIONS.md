# CA read-along -- Phase C Pack 03 (CARLA OpenDRIVE + ASAM OpenDRIVE)

**Annotator:** Course Architect
**Date:** 2026-09-25
**Parent pack:** `../agent-training/phase-c/03-opendrive-carla-asam.md`
**Primary cites:**
- [CARLA — ASAM OpenDRIVE standalone mode](https://carla.readthedocs.io/en/latest/adv_opendrive/) (docs free; CARLA code MIT — **pattern cite only**, not a raceGPS runtime)
- [ASAM OpenDRIVE®](https://www.asam.net/standards/detail/opendrive) (standard download free of charge; datasheet **v1.9.0** when pack checked 2026-09-25)
- [CARLA — Maps and navigation](https://carla.readthedocs.io/en/latest/core_map/) (waypoint / lane / junction mental model)
- [Evenant — Painting Environment Concepts](https://www.evenant.com/articles/painting-environment-concepts-in-no-time) (ART1 value hierarchy for stills)
**Mode:** study notes only -- no editor, no PIE, no CARLA install, no XODR rewrite on omni

---

## What this pack is for (CA lane)

Own **Burke Lakefront EZ** as a forgiving ribbon that reads as a track: Lake Erie north, downtown/skyline south. Pack 03 is OpenDRIVE literacy so we can QA shared `.xodr` / racing-line continuity with the right vocabulary -- reference line, lane links, junctions -- without standing up CARLA as a second city builder.

Vehicle Arcade owns Chaos feel + camera (pack 01). Race Systems owns session / Enhanced Input / loop HUD (packs 02/04/05). Do not freestyle into those lanes here.

---

## Steal (map to raceGPS)

1. **Reference line first** -- OpenDRIVE roads hang off a reference line. For Burke EZ, treat the existing racing-line / XODR as the spine: check continuity and lap wrap before arguing barriers or landmarks.
2. **Junction lane links** -- Bad junction links in XODR propagate into any mesh generated from it. When validating `cleveland_burke_gp_1997` EZ, inspect chicane / hairpin connections (T1 Vortex, T9–T10) for unbroken lane connectivity -- vocabulary from ASAM/CARLA, fix stays in raceGPS pipelines.
3. **Safety knobs as QA ideas** -- CARLA's slightly wider junction lanes, boundary walls, junction smoothing are transferable *checks* for "vehicles won't fall off" and EZ ~35% wider gates = readability, not a new city.
4. **Mesh chunking lesson** -- `max_road_length` in CARLA is cull cost; for Burke: do not treat the whole lakefront as one undebuggable blob when validating ribbon continuity.
5. **Waypoints ≠ NavMesh AI** -- Directed lane samples are a **racing-line thinking aid** (sightlines, braking zones, checkpoint spacing). Do not assume CARLA Python Waypoint API exists in raceGPS.
6. **Static network only** -- OpenDRIVE will not paint Cleveland. Skyline volumes + Lake Erie water stay raceGPS/UE art reuse (env pack already inventoried). OpenCRG / OpenSCENARIO stay out of Gate 1 scope.
7. **ART1 still judgment** -- Four-value thumbnails: track = hero value mass; skyline silhouette + Erie horizon support mood. Reject empty-void / wrong-runway camera before claiming PASS.

---

## Do not steal

- Rebuilding Cleveland inside CARLA; swapping raceGPS mesh pipeline for CARLA standalone void roads.
- Greenfield City Sample / OSM tourism / Workshop two-app city builder.
- Treating OpenDRIVE as a full env-art pipeline or ADAS-grade purity gate for Gate 1.
- Cloning CARLA or installing ASAM tooling on omni until Chris greens.
- Starting Vehicle Arcade lighting or Race Systems session work from this lane.

---

## Course version ladder (docs only)

| Version | CA focus | Not yet |
|---------|----------|---------|
| **v1** | Ribbon readability / EZ forgiving line (data-plane accepted) | — |
| **v2** | Race-safe barriers + night-default lighting + track surface read | Landmarks |
| **v3** | Landmarks / skyline dress | — |

Prior standing order: approach A (verify-then-tighten). Burke EZ data-plane already accepted — stand down further ribbon edits unless Prototyper reopens.

---

## CA observables (FUTURE -- do not run now)

When Prototyper greens single-editor omni work again:

| Check | Pass looks like |
|-------|-----------------|
| Ribbon | Continuous EZ loop; junctions don't dump the car; lap wrap clear |
| Compose | Overhead + driver stills read as a **track**, not void / north runway |
| Visual bar | Lake Erie + Cleveland skyline readable in frame with Sunset/read light |
| Evidence | PASS stills only under `docs/evidence/grokbot/burke-ez-ribbon/` (PM gates Chris) |
| Anti | No CARLA city rebuild screenshots sold as raceGPS progress |

---

## Tie-back to known raceGPS debt (docs only)

- Pack `cleveland_burke_gp_1997` / EZ artifacts (`racing_line_ez`, checkpoints, env skyline/water JSON) stay the reuse source.
- Preview HTML fly-along had projection bugs when freeze hit — course truth remains pack JSON + UE stills when unlocked, not the broken fly view.
- Gate 1 HOLD + freeze: no omni editor, no PIE, no LaunchClevelandRace until Prototyper unlocks.

---

## Hand-off

Unreal PM cross-cuts this into `agent-training/`. Pack 03 is CA primary; ART1 composition literacy is shared with PM visual-bar judgment.
