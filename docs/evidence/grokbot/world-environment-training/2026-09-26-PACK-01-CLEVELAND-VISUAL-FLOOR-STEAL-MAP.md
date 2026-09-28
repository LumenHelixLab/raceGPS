# Pack 01 — Cleveland visual floor steal map

**Lane:** World Environment (primary)  
**Date checked:** 2026-09-26  
**raceGPS weave:** Burke race base · wrap existing packs · Midnight Club still bar · **docs only — do not launch editor**

---

## Source map (in-tree / already shipped — steal these)

| Asset / path | Role | Steal note |
|--------------|------|------------|
| `citypacks/cleveland/burke_gp_1997/` | Historic Burke GP pack | Source of truth for XODR + line + dressing JSON |
| `racing_line.json` / `checkpoints.json` / `manifest.json` / `cleveland_burke_gp.xodr` | Course plane (Course Architect) | Env does **not** own line edits; wrap around them |
| `racing_line_ez.json` / `checkpoints_ez.json` / `manifest_ez.json` | EZ variant (accepted data-plane) | Shares source XODR; wider gates — still reuse skyline/water |
| `skyline.json` | Near-track downtown silhouette (~45–79 volumes) | **Additive** to T10 HISM city — do not replace 120k instances with boxes |
| `water.json` | Lake Erie near-field sheet (north of circuit) | `Water_Surface` MID; expand horizon from raised chase |
| `track_dressing.json` / `environment.json` | Grass, barriers, hangars, lighting pointers | Barriers via env actor — **not** `AStreetFurnitureSpawner` |
| `AClevelandEnvironmentActor` + `CLEVELAND_ENV_WIREUP.md` | PMC dress + DayNight spawn | Spawn after `LoadCityPack()`; no new uassets required |
| `AClevelandLookDirector` (`MidnightRun` default) | Night grade, light suppress, Epic console | Bloom / post caps below |
| `CLEVELAND_VISUAL_BAR.md` | Framing + V1–V10 milestones | Camera sells Cleveland; empty runway ≠ missing content |
| `CLEVELAND_ENVIRONMENT.md` | M5 dressing inventory | Offline path: **no Cesium required** for race-base floor |
| Map `Cleveland5_0KmWorld` | Showcase map | T10 HISM city already present (`building_instances≈119601`, `water_instances≈7256`) |
| Launch override | `LaunchCleveland.bat` → Showcase GM on Cleveland map | Does **not** flip GlobalDefaultGameMode |

### Repo tip vs local (sync note)

- GitHub branch `grokbot/cleveland-integration` @ `b5e1b4b` carries historic `burke_gp_1997` (skyline/water/environment included; `cesium_required: false`).
- **Not on that GH tip yet:** EZ files (`racing_line_ez.json` / `checkpoints_ez.json` / `manifest_ez.json`), `docs/handoff/*` freeze pack, and `docs/evidence/grokbot/burke-ez-ribbon/` (404 remotely). Local `/workspace/cleveland-showcase` + `handoff-pack` hold those — treat local as training truth until mirrored.
- Scratch still `midnight_fix_chase.png` is **near-void FAIL** (dark plane, no skyline/Erie) — use as negative example, not a bar claim.
- Older notes: GH `docs/evidence/grokbot/visual-floor-2026-09-24/` (V16 chase/Sunset attach); side/¾ stills still open — no skyline+Erie PASS claim there either.

### Cesium

- Handoff allows **Cesium-if-present** wrap.
- Offline env docs and wireup: **no Cesium plugin / no 3D Tiles** for the M5 dressing path.
- **Rule:** if Cesium is not already in this uproject, prefer non-Cesium skyline/water first. Do not install speculative Cesium stacks under freeze or as a “missing city” fix.

### Geo / axis (do not ignore)

- Place: Burke Lakefront (BKL) — Lake Erie **north**, downtown **south**
- World: Z-up, 1 uu = 1 cm, X=east, Y=north (matches `URacingLineComponent::GeoToWorld`)
- Intro / chase framing: city **left**, Erie **right**, cars **center** (see visual bar)

---

## Bloom / light / post caps (from `ClevelandLookDirector`)

Console (Epic floor — MidnightRun path):

| CVar / feature | Value used in look director |
|----------------|-----------------------------|
| `r.VolumetricCloud` | 1 |
| `r.SkyAtmosphere` | 1 |
| `r.ShadowQuality` | 5 |
| `r.BloomQuality` | 5 |
| `r.ReflectionMethod` | 1 |
| `r.DynamicGlobalIlluminationMethod` | 1 |
| `r.Tonemapper.Quality` | 5 |
| `r.MotionBlurQuality` | 4 |
| `r.ViewDistanceScale` | 1.5 |
| Histogram Min/Max | −4 / 4 |

Post / lights (order-of-magnitude caps to keep stills readable, not washed):

| Mode | Sun intensity | Sky intensity | BloomIntensity | BloomThreshold | Notes |
|------|---------------|---------------|----------------|----------------|-------|
| SunnyDay-ish path | ~2.6 | ~1.15 | ~1.65 | ~0.75 | Extra directional lights **suppressed**; unbuilt reflection captures hidden |
| MidnightRun (default showcase) | ~1.55 (moon path) | ~1.85 | ~2.20 | ~0.65 | Cool night grade; vignette ~0.32; fringe mild |

**Do not** stack extra DirectionalLights “for drama.” Look director already disables competitors so one cycle owns the frame.

---

## Midnight Club still observables (PASS when Mode B unlocks)

A Chris-facing still is PASS only if **all** of these hold on a **real viewport** (not NullRHI):

1. **Place reads:** downtown / skyline mass visible (T10 and/or Karla ridge), not gray empty apron alone.
2. **Erie reads:** north water sheet fills horizon from intro or raised chase — not a postage-stamp plane.
3. **Cars center:** 3-car grid or chase subject readable as a race, not capsules in a void.
4. **Framing:** city left / water right / cars center (or proven equivalent after intentional camera change).
5. **Night grade (if MidnightRun):** bloom that sells wet apron + lights without clipping the whole frame white; competing dir-lights off.
6. **Log corroboration (when running):** `MidnightRun applied`, `skyline buildings=N` with N matching JSON count (**not** `skyline=1`), `lake verts=…`, intro/chase camera logs.
7. **Evidence lands** under `docs/evidence/grokbot/burke-ez-ribbon/` with still + short note — generation-only ribbon SVG is **not** visual PASS.

### Known still inventory on shared scratch (not PASS claims)

Local scratch holds `cleveland_v7`…`v15` hero/chase PNGs. Treat as **historical captures for gap analysis**, not Mode B unlock evidence, until Unreal PM accepts a new still set against this checklist. Night block-skyline shots without readable Erie / race-base Sunset framing stay **gap**, not done.

---

## Path policy (soft-gap fix 2026-09-26)

**Single evidence slot:** `docs/evidence/grokbot/burke-ez-ribbon/`  
Holds generation evidence now; holds Mode B hero/chase PASS stills when unlocked. Do **not** invent a parallel folder formerly floated as `burke-ez-visual/` — use `burke-ez-ribbon/` only.

## Explicit bans

| Ban | Why |
|-----|-----|
| **CARLA rebuild** | Standing lock — wrap finished pipelines only |
| **City Sample / greenfield Cleveland tourism map** | Standing lock — empty runway is framing/lighting, not a content hole |
| **NullRHI / ForceFinish / black void as visual PASS** | Never Gate 1 or Mode B evidence |
| **Flipping GlobalDefaultGameMode** away from CruiseSprint | Showcase override only |
| **Replacing T10 HISM city with Karla boxes** | Silhouette is additive near-track only |
| **Routing race barriers through `AStreetFurnitureSpawner`** | Dedicated env actor path |
| **Speculative Cesium install** when not already in-tree | Prefer skyline/water JSON first |
| **Unattended editor / PIE / LaunchClevelandRace under freeze** | Chris unlock required |
| **Selling compile / JSON generation as visual PASS** | Evidence = lit still + log |

---

## Steal vs defer

| Steal now (docs / when unlocked) | Defer |
|----------------------------------|-------|
| Wireup + JSON search paths for env actor | Workshop / OSM tourism streets |
| Look director MidnightRun + light suppress | Full V5–V10 cinematic / photo mode |
| Visual bar framing + still checklist | Gate 1 finish+R (Race Systems / Chris Track A) |
| Wrap EZ pack with shared skyline/water | Rebuilding XODR or greenfield downtown |

---

## Lane tips

### World Environment
Own hero mass: skyline materials (glass/concrete by height), Erie sheet, atmosphere, post grade, dressing density. Do not edit Course Architect’s EZ line. When Mode B opens: one attended still set, then stop for PM gate.

### Course Architect
Ribbon / EZ gates are theirs. Env wraps the accepted data-plane; do not “fix” the line by rebuilding city.

### Vehicle Arcade
Chase arm / 3/4 left framing and car lights are shared scoreboard with visual floor — coordinate stills, don’t fight for the same editor slot.

### Unreal PM
Gate Mode B on this checklist. Generation evidence in `burke-ez-ribbon/` ≠ visual PASS. Mirror this folder into `Documents\raceGPS-handoff` when you take the Wave 1 training QA pass.

### Build & Engine
No special env target required for training. When unlocked: one editor on omni; human-default bats only for capture.

---

## Observable check — FUTURE (do not run now)

When Chris unlocks Mode B: `LaunchCleveland.bat` (or documented Showcase override) on `Cleveland5_0KmWorld`, real viewport, capture overhead + driver/chase proving EZ ribbon + vivid skyline + Erie. Land stills + note under evidence path above. **NullRHI = FAIL. CARLA rebuild = FAIL. City Sample greenfield = FAIL.**

---

## Citations (checked 2026-09-26)

| Claim | Cite |
|-------|------|
| Pack id + offline flags | GH `citypacks/cleveland/burke_gp_1997/manifest.json` on `grokbot/cleveland-integration`: `id=cleveland_burke_gp_1997`, `offline=true`, `carla_required=false`, `cesium_required=false`; wires `environment` / `water` / `skyline` / `track_dressing` |
| Pack file set on tip | GH dir listing same path — README, xodr, racing_line, checkpoints, metadata, environment, water, skyline, track_dressing (**no** `*_ez.json` on tip) |
| Skyline volume count | Local `cleveland-env/.../skyline.json` → `buildings` length **45** (matches env doc); visual bar text may say ~79 historically — use JSON count as PASS log target |
| Erie sheet | Local + GH `water.json` (`material`, `points`, `inner_shoreline`) |
| Env non-goals | Local/GH `environment.json` keys include `offline`, `cesium_required`, `carla_required`, `non_goals` |
| Look / void fix | GH `docs/evidence/grokbot/visual-floor-2026-09-24/V16-NOTES.md` — DayNightCycle SceneRoot Movable (Static-on-Movable abort → black void); Sunset sunI=4.20 skyI=2.40; chase V16 RACE-FOLLOW; side/¾ stills still open |
| Visual bar framing | In-tree `CLEVELAND_VISUAL_BAR.md` — city left / Erie right / cars center; T10 HISM already in map; empty runway = framing not content hole |
| Wireup | `CLEVELAND_ENV_WIREUP.md` — spawn `AClevelandEnvironmentActor` after `LoadCityPack()`; no Cesium plugin; no new uassets |
| Freeze / Mode B | `Documents\raceGPS-handoff\2026-09-25-AGENT-FREEZE-STATUS.md` + `2026-09-25-UNLOCK-CRITERIA.md`; Wave 1 brief `2026-09-26-WAVE1-SPECIALISTS.md` |
| GH tip gaps | No `docs/handoff/*`, no `burke-ez-ribbon/`, no EZ json on tip @ `b5e1b4b` era — local showcase/handoff hold those |

Deepen status: beyond stub — citations + steal map + bans. Still **no** editor captures under freeze.
