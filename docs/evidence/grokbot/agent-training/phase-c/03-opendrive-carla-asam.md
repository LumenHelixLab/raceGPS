# Phase C Pack 03 — CARLA OpenDRIVE + ASAM OpenDRIVE

**Lane focus:** Course Architect (primary) · ART1 composition literacy from Phase B  
**Date checked:** 2026-09-25  
**raceGPS weave:** UE 5.7 · Burke EZ + Cleveland skyline + Lake Erie · reuse packs · **no CARLA rebuild** · **no greenfield Cleveland** · Gate 1 HOLD · no editor during training

---

## Source URL(s) + license

| Field | Value |
|-------|-------|
| **Title** | CARLA — ASAM OpenDRIVE standalone mode |
| **URL** | https://carla.readthedocs.io/en/latest/adv_opendrive/ |
| **License** | Docs free; CARLA simulator code MIT (https://github.com/carla-simulator/carla) |
| **UE note** | CARLA’s own UE fork — **pattern cite only**, not a raceGPS runtime dependency |

| Field | Value |
|-------|-------|
| **Title** | ASAM OpenDRIVE® (official) |
| **URL** | https://www.asam.net/standards/detail/opendrive |
| **License** | ASAM: download of the standard free of charge (per ASAM page) |
| **Version note** | Datasheet listed **v1.9.0** when checked 2026-09-25 |

| Field | Value |
|-------|-------|
| **Title** | CARLA — Maps and navigation |
| **URL** | https://carla.readthedocs.io/en/latest/core_map/ |
| **License** | Free docs |
| **Use** | Waypoint / lane / junction mental model for arcade ribbon read |

| Field | Value |
|-------|-------|
| **Title** | Evenant — Painting Environment Concepts (Phase B ART1) |
| **URL** | https://www.evenant.com/articles/painting-environment-concepts-in-no-time |
| **License** | Free public article |
| **Use** | Value hierarchy for skyline / water / track stills — not a new fantasy city |

---

## What to read (sections)

**CARLA adv_opendrive:** Overview (XODR → procedural road mesh; void beyond roads; junction width padding; boundary walls); `generate_opendrive_world` / `OpendriveGenerationParameters` (`vertex_distance`, `max_road_length`, `wall_height`, `additional_width`, `smooth_junctions`, `enable_mesh_visibility`); Mesh generation notes (junction smoothing tradeoffs; sidewalk height caveats).

**ASAM page:** Reference line as core; roads/lanes/elevation attached to it; junctions via connecting-roads; lane links; static network only (OpenCRG / OpenSCENARIO are siblings — out of Gate 1 scope).

**CARLA core_map (skim):** Waypoints as directed lane samples; junctions; `next`/`previous` path thinking — as a **racing-line aid**, not an API you expect inside raceGPS.

**ART1:** Four-value thumbnails; hero focal; horizon hierarchy for Burke still judgment.

---

## Key lessons

- OpenDRIVE (`.xodr`) describes a **static road network**: reference line, lanes, junctions, signals — not full env art. Bad XODR (especially junctions) propagates into any mesh you generate from it.
- CARLA standalone mode’s safety knobs are transferable *ideas*: slightly wider junction lanes, boundary walls, and optional junction smoothing when uneven lanes fight each other. raceGPS already has pipelines — use the vocabulary to **QA shared XODR**, not to stand up CARLA as a second city builder.
- Mesh chunking (`max_road_length`) is about render/cull cost in CARLA; the lesson for Burke is “don’t treat the whole county as one undebuggable blob” when validating ribbon continuity.
- Waypoints ≈ sampling the racing line along lanes. Arcade ribbon read at speed cares about sightlines, braking zones, and checkpoint spacing — OpenDRIVE lane centerlines are a thinking aid, not NavMesh AI.
- ASAM explicitly scopes **static** roads; skyline, Lake Erie water, and dressing come from raceGPS/UE art reuse — OpenDRIVE will not paint Cleveland for you.
- Value thumbnails (ART1) judge whether EZ ribbon + skyline + water read in stills before arguing mesh density.

---

## Steal for raceGPS

| Target | Steal |
|--------|-------|
| **Burke / course** | Shared XODR for `cleveland_burke_gp_1997_ez`: check reference-line continuity, junction lane links, and “vehicles won’t fall off” barriers/width before art polish. EZ ~35% wider gates = readability pass, not a new city. |
| **Visual bar** | Compose stills so track is the hero value mass, skyline silhouette and Lake Erie horizon support mood — reuse existing skyline/water packs. |
| **Gate 1** | Course work supports a drivable lit route for the loop; do not block Gate 1 on ADAS-grade OpenDRIVE purity. |

---

## Do not steal / anti-patterns

- Rebuilding Cleveland inside CARLA; swapping raceGPS mesh pipeline for CARLA standalone void roads.
- Greenfield City Sample tourism; Workshop / OSM builder / two-app rgpack (outline non-goals).
- Treating OpenDRIVE as a full env-art pipeline or turning CA work into ADAS validation.
- Assuming CARLA Waypoint Python API exists in raceGPS.
- Cloning CARLA until Chris greens.

---

## Lane tips

### Course Architect
Version the course: v1 ribbon readability → v2 barriers/lighting → v3 landmarks. Validate known distances and spawn poses before importer scale-up (genre-car-racing GIS note). Prefer wrap/light on in-tree Burke/Cleveland pipelines.

### Unreal PM
Judge CLEVELAND_VISUAL_BAR stills with silhouette + water/skyline horizon; reject empty north-runway camera fails. Keep CARLA cites as pattern literacy in evidence writeups.

### Vehicle Arcade / Race Systems
Checkpoint placement should follow readable racing-line samples; reverse/skip gate tests remain RS acceptance (genre playbook) when game work reopens.

---

## Observable check — FUTURE (do not run now)

When editor reopens: Burke EZ PIE stills show continuous ribbon, junction barriers where needed, Cleveland skyline + Lake Erie readable in frame; XODR/junction notes in evidence cite ASAM/CARLA vocabulary. **No CARLA city rebuild screenshots as raceGPS progress. Black void = FAIL.**
