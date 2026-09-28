# Wave 1 — Annotations packs QA (Unreal PM)

**Date:** 2026-09-26 (America/New_York)  
**Role:** Unreal PM (raceGPS)  
**Status:** **FULL SET PASS**  
**Constraint / freeze reminder:** Still NO editor / PIE / `LaunchClevelandRace` / clones / Marketplace. Annotations + training docs only until Chris unlocks game work.

Prior Wave 1 training packs QA (`2026-09-26-WAVE1-TRAINING-QA.md`) was **FULL SET PASS** on Pack 01s; soft gaps claimed cleared. This document grades the **annotations** packs (WE / B&E / WW) and verifies those soft-gap clearances against lane READMEs + on-disk cites.

---

## Index — three lanes

| Lane | Annotations path (project prefer) | Parent Pack 01 (primary) | Grade |
|------|-----------------------------------|--------------------------|-------|
| World Environment | `docs/evidence/grokbot/world-environment-training/2026-09-26-PACK-01-CLEVELAND-VISUAL-FLOOR-ANNOTATIONS.md` | `…-CLEVELAND-VISUAL-FLOOR-STEAL-MAP.md` | **PASS** |
| Build & Engine | `docs/evidence/grokbot/build-engine-training/2026-09-26-PACK-01-WIN64-DEV-REBUILD-AND-LOG-FORENSICS-ANNOTATIONS.md` | `…-WIN64-DEV-REBUILD-AND-LOG-FORENSICS.md` | **PASS** |
| Workshop Web | `docs/evidence/grokbot/workshop-web-training/2026-09-26-PACK-01-TWO-APP-AND-RGPACK-ANNOTATIONS.md` | `…-TWO-APP-AND-RGPACK-CONTRACT-MAP.md` | **PASS** |

**Documents mirror root:** `C:\Users\cgp22\Documents\raceGPS-handoff\` (same folder names).  
**Project root:** `C:\projects\raceGPS-grokbot-cleveland\docs\evidence\grokbot\`

---

## Gate rule

No “done” on game work. Steal / do-not / FUTURE observables / honest gaps only until Chris unlocks Mode B (WE stills), Mode C (B&E Gate 1), or Workshop export (WW fixture-first). NullRHI ≠ visual PASS ≠ Gate 1. CruiseSprint `GlobalDefaultGameMode` stays. Packs are the WW contract (Workshop writes / Race reads).

---

## World Environment — **PASS**

### What passed
- **Steal vs do-not concrete + on-lane:** Nine steal items (skyline silhouette, Erie water JSON, V16 lighting diagnosis, MidnightRun/LookDirector caps, Midnight Club still bar, axis/camera hygiene, Cesium wrap-only-if-in-tree, `cleveland_burke_gp_1997` wrap-light, env-actor wireup). Do-not bans CARLA rebuild, City Sample greenfield, GlobalDefault flip, NullRHI/void PASS, CA ribbon / VA chase ownership, StreetMap-before-race, parallel `burke-ez-visual/`.
- **Cite-and-path:** Real cites (GH `burke_gp_1997` manifest/skyline/water, `V16-NOTES.md`, `CLEVELAND_VISUAL_BAR.md` / wireup, freeze/unlock handoff). Mode line forbids editor / PIE / Cesium install / CARLA / City Sample. No install/clone/editor as required next step.
- **FUTURE observables gated:** Mode B still checklist (Erie / skyline / lighting / compose / evidence under `burke-ez-ribbon/`) explicitly “do not run now”; not sold as current PASS. Scratch stills table = gap analysis only.
- **Hard bans present:** NullRHI≠PASS; no CARLA rebuild / City Sample greenfield; CruiseSprint stays; single evidence slot.
- **Evidence slot hygiene:** Single `burke-ez-ribbon/` (README + annotations ban `burke-ez-visual/`). On-disk: `burke-ez-ribbon/` exists; no parallel `burke-ez-visual/`.
- **Soft gaps from training QA cleared:** README primary → STEAL-MAP; evidence path → `burke-ez-ribbon/` only (verified in lane README Files + Evidence paths tables).
- **Freeze-safe:** Study notes only; Gate 1 Track A / Modes B/D ownership called correctly.

### Soft gaps (non-blocking, max 3)
1. GH tip @ `b5e1b4b` still missing EZ json / handoff / ribbon evidence remotely — local remains training truth (honest; keep until mirrored).
2. Historical scratch stills (`v14`/`v15`/`midnight_test_chase`) remain gap analysis only — correct under freeze; no Mode B set yet.
3. Launch contract when unlocked still defers bats to B&E — fine; do not let WE invent a second Showcase bat.

### Next action
None required for PASS. Park until Chris unlocks Mode B stills (then one-editor omni + B&E bats).

---

## Build & Engine — **PASS**

### What passed
- **Steal vs do-not concrete + on-lane:** Steal covers Phase A NoUBA recipe, one-editor omni, human-default bat contract, Track A discriminating test, grep sheet, Phase A landed / Phase B HOLD, evidence naming, path hygiene. Do-not bans unattended Launch as Gate 1 PASS, NullRHI/void, GlobalDefault flip, UBA-on without Succeeded companion, multi-editor, RS finish+R / WW rgpack ownership, empty packaging sold as progress.
- **Cite-and-path:** Real cites (`G6-race-base-mvp/track-b-phase-a-build.log` Succeeded, Gate1 Track B landed/DIG/PATCH/BOTH/RESUME, TECH-SPEC / UNLOCK, `LaunchClevelandRace.bat`, G1 host baseline). Mode forbids editor / PIE / Launch / UBA experiment / Gate 1 spam.
- **FUTURE observables gated:** Mode C interactive Gate 1 checklist (rebuild / one-editor / human Sunset bat / survive 60–120s / grep / evidence under G6) “do not run now”; Mode D separate unlock. Not sold as current PASS. FAIL artifacts table labeled docs-only.
- **Hard bans present:** NullRHI≠Gate 1; CruiseSprint GlobalDefault stays; no unattended agent spawn as PASS.
- **Evidence slot hygiene:** Concrete G6 cite `track-b-phase-a-build.log` (Verified on disk). FAIL vs Succeeded naming habit explicit; `ue-editor-build.log` distinguished from Phase A NoUBA default.
- **Soft gaps from training QA cleared:** Single Pack 01 filename (WIN64-DEV primary; sibling stub called out); G6 build-log cite in annotations + parent + README.
- **Freeze-safe:** Phase A LANDED / Phase B HOLD board preserved; Chris owns attended Track A.

### Soft gaps (non-blocking, max 3)
1. Cook/package recipe for Workshop/Race targets still light — correctly deferred; keep “coordinate WW when unlocked” only.
2. Sibling stub `…-REBUILD-AND-LOG-FORENSICS.md` remains on disk for lineage — README already demotes it; do not deepen as a second Pack 01.
3. Attended `finish-r-PASS-*.txt` evidence does not exist yet (correct FAIL-closed state) — do not invent PASS filenames under freeze.

### Next action
None required for PASS. Park until Chris unlocks Mode C (attended Track A / Gate 1).

---

## Workshop Web — **PASS**

### What passed
- **Steal vs do-not concrete + on-lane:** Steal covers two-app split, RGPACK_v1 disk layout + Frame A, contentHash fail-closed, `tools/rgpack` API, fixture-first reopen, launcher lock, export-vs-empty-target rubric, citypack gap-as-map-only, auth-less local ops when designed. Do-not bans live OSM in Race, empty-target ship claims, greenfield City Sample/CARLA/tourism OSM, StreetMap-before-race, GlobalDefault flip, rebranding citypack as RGPACK without adapter, Overpass installs under freeze, CA/WE ownership via Workshop mesh, NullRHI as export.
- **Cite-and-path:** Real cites (`RGPACK_v1.md`, `tools/rgpack/*`, `tests/fixtures/rgpack/minimal_v1/`, Frame contract, two-app plan, Source modules, `raceGPS.bat`, G4/G5 local-only honesty, citypack manifest as gap map). Mode forbids Overpass install / StreetMap / editor / adapter code / greenfield city.
- **Honest gaps preserved:** Auth-less Workshop UI routes = **planned / not found**; Overpass → rgpack CLI = **absent** (fixture-first reopen); citypack → rgpack adapter = **post-unlock**; G4/G5 compile-only. Matches lane README Honest gaps table — not papered over.
- **FUTURE observables gated:** Pytest / export / Race read / routes-later / adapter-post-unlock behind Chris unlock; anti-list explicit. Not sold as current PASS.
- **Hard bans present:** Packs as contract; Race lean / no live OSM; empty targets ≠ ship; NullRHI never PASS; CruiseSprint stays.
- **Evidence slot hygiene:** Fixture-first reopen (`fixture_minimal_v1` + `pytest tests/test_rgpack_schema.py`) before Overpass CLI or UI. Export evidence path named under `workshop-web-training/` (or PM-named slot) when unlocked.
- **Soft gaps from training QA cleared:** README primary → TWO-APP contract map; routes sibling = stub; honest gaps + post-unlock adapter locked (verified in lane README).
- **Freeze-safe:** Docs/training only; no Overpass / StreetMap / adapter implementation until unlock.

### Soft gaps (non-blocking, max 3)
1. Auth-less local Workshop UI routes still have no live route table — keep planned; deepen FAQ only when paths exist.
2. G4/G5 evidence dirs remain local-omni vs GH tip — mirror when Chris wants parity; still compile ≠ validate.
3. Older slice-plan checkboxes may still read unchecked in some mirrors — trust on-disk `tools/rgpack` + ACCEPTED `RGPACK_v1` over markdown theater (already noted).

### Next action
None required for PASS. Park until Chris unlocks Workshop implementation (pytest/fixture first; no unattended Launch).

---

## Overall

| Set | Grade |
|-----|-------|
| Wave 1 annotations (WE + B&E + WW) | **FULL SET PASS** |

All three annotations packs meet steal/do-not concreteness, cite-and-path (no install/clone/editor as next step), honest-gap preservation (esp WW), FUTURE observables gated behind Chris unlock, hard bans, evidence-slot hygiene, and freeze-safety. Soft gaps from `2026-09-26-WAVE1-TRAINING-QA.md` are verified cleared in lane READMEs; remaining soft gaps are deepen-later honesty, not FAIL/CONDITIONAL blockers.

**Chris decision ask (unchanged posture):**
1. Accept Wave 1 annotations as freeze-safe train-while-HOLD deepen? (QA says yes — FULL SET PASS.)
2. Keep clones / Marketplace / omni editor frozen until you reopen game work?
3. Park Wave 1 training+annotations until Gate 1 / Burke visual / Workshop export unlock, or deepen another docs-only lane?

---

## Paths written / mirrored

**Project**
- `C:\projects\raceGPS-grokbot-cleveland\docs\evidence\grokbot\agent-training\2026-09-26-WAVE1-ANNOTATIONS-QA.md`
- `C:\projects\raceGPS-grokbot-cleveland\docs\evidence\grokbot\agent-training\WAVE1-INDEX.md` (annotations QA status + WW primary = TWO-APP)
- `C:\projects\raceGPS-grokbot-cleveland\docs\evidence\grokbot\agent-training\README.md` (Wave 1 annotations QA row)

**Documents mirror**
- `C:\Users\cgp22\Documents\raceGPS-handoff\agent-training\2026-09-26-WAVE1-ANNOTATIONS-QA.md`
- `C:\Users\cgp22\Documents\raceGPS-handoff\agent-training\WAVE1-INDEX.md`
- `C:\Users\cgp22\Documents\raceGPS-handoff\agent-training\README.md`
