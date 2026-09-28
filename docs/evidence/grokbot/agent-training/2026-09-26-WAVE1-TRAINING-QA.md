# Wave 1 — Training packs QA (Unreal PM)

**Date:** 2026-09-26 (America/New_York)  
**Role:** Unreal PM (raceGPS)  
**Status:** **FULL SET PASS**  
**Constraint / freeze reminder:** Still NO editor / PIE / `LaunchClevelandRace` / clones / Marketplace. Training docs only until Chris unlocks game work.

Prior Phase C annotations (VA / RS / CA) remain **FULL SET PASS** — see `2026-09-25-PHASE-C-ANNOTATIONS-QA.md`. This document grades **Wave 1 specialist** packs only (WE / B&E / WW).

**Prototyper stub:** Overwrote prior OPEN stub at this path (same filename). Stub checklist named alternate Pack 01 filenames; grades below use the on-disk deepened Pack 01 set.

---

## Index — three lanes

| Lane | Pack paths (project prefer) | Grade |
|------|-----------------------------|-------|
| World Environment | `docs/evidence/grokbot/world-environment-training/README.md` + `2026-09-26-PACK-01-CLEVELAND-VISUAL-FLOOR-STEAL-MAP.md` (+ sibling `…-CLEVELAND-VISUAL-FLOOR.md`) | **PASS** |
| Build & Engine | `docs/evidence/grokbot/build-engine-training/README.md` + `2026-09-26-PACK-01-WIN64-DEV-REBUILD-AND-LOG-FORENSICS.md` (+ sibling `…-REBUILD-AND-LOG-FORENSICS.md`) | **PASS** |
| Workshop Web | `docs/evidence/grokbot/workshop-web-training/README.md` + `2026-09-26-PACK-01-RGPACK-AND-WORKSHOP-ROUTES.md` + `2026-09-26-PACK-01-TWO-APP-AND-RGPACK-CONTRACT-MAP.md` | **PASS** |

**Documents mirror root:** `C:\Users\cgp22\Documents\raceGPS-handoff\` (same folder names).  
**Project root:** `C:\projects\raceGPS-grokbot-cleveland\docs\evidence\grokbot\`

---

## Gate rule

No “done” on game work. Training docs / cite-and-path only until Chris unlocks editor / Mode B / attended Track A. NullRHI ≠ visual PASS ≠ Gate 1. CruiseSprint `GlobalDefaultGameMode` stays.

---

## World Environment — **PASS**

### What passed
- **Cite-and-path only:** Study/steal map; FUTURE observables explicitly “do not run now”; no install/clone/editor as required next steps.
- **On-lane:** Visual floor reuse — `burke_gp_1997` skyline/water/environment wrap, LookDirector bloom caps, Midnight Club still bar; lane wall vs Course Architect ribbon.
- **Hard bans present:** CARLA rebuild; City Sample / greenfield Cleveland; NullRHI / black void ≠ PASS; no GlobalDefault flip; no speculative Cesium; no unattended Launch under freeze.
- **Real citations:** GH `grokbot/cleveland-integration` @ `b5e1b4b` manifest/skyline/water; `CLEVELAND_VISUAL_BAR.md` / wireup; `visual-floor-2026-09-24/V16-NOTES.md`; local vs tip sync honesty.
- **Freeze-safe:** Docs-only weave line; Mode B still checklist gated.
- **Annotation-ready:** Steal map + CVar tables + still observables + steal-vs-defer — not empty scaffolding.

### Gaps to deepen (non-blocking)
- README Files table still points primary link at `…-CLEVELAND-VISUAL-FLOOR.md`; STEAL-MAP is the deepened Pack 01 — align README primary link.
- Evidence path naming drift: pack says `burke-ez-visual/` vs existing `burke-ez-ribbon/` slot — pick one PM-named path before Mode B.
- GH tip still missing EZ json / handoff / ribbon evidence — keep local-as-truth note until mirrored.
- Historical scratch stills (`v7`–`v15`) remain gap analysis only; no accepted Mode B set yet (correct under freeze).

### Next action
Specialist **annotations pack** OK (docs deepen only). No fix required for PASS. Optional: README primary-link + evidence path name alignment.

---

## Build & Engine — **PASS**

### What passed
- **Cite-and-path only:** Rebuild recipe framed “when Chris unlocks”; freeze line forbids editor/`-game` now.
- **On-lane:** Win64 Dev rebuild hygiene (`-NoUBA`, MaxParallelActions=1), one-editor omni ownership, `LaunchClevelandRace.bat` human-default contract, ViewportClosed / TrackB grep forensics.
- **Hard bans present:** CruiseSprint GlobalDefault stays; NullRHI ≠ Gate 1; unattended Launch / `-game` spam banned; UBA-on without measured pass banned; second editor banned.
- **Real citations:** Track B Phase A landed / DIG / PATCH-PLAN / BOTH-TRACKS / RESUME / TECH-SPEC / UNLOCK; G1 `HOST_INVENTORY.md` / `VERDICT.md`; bat path under `apps/unreal-akron-beta/`.
- **Freeze-safe:** **Phase A LANDED** / **Phase B HOLD** status board explicit; Chris owns attended Track A.
- **Annotation-ready:** Grep cheat sheet + FAIL timeline + evidence naming — study-first.

### Gaps to deepen (non-blocking)
- Dual Pack 01 filenames (`…-WIN64-DEV-…` vs README-linked `…-REBUILD-AND-LOG-FORENSICS.md`) — consolidate or cross-link both as same content family.
- Light on cook/package recipe for Workshop/Race targets (correctly deferred; one short “when unlocked coordinate WW” note already present).
- Could cite one concrete G6 `*.meta.txt` / exitcode example path beside the habit note.

### Next action
Specialist **annotations pack** OK. No blocking fix. Optional: dual-filename README cleanup.

---

## Workshop Web — **PASS**

### What passed
- **Cite-and-path only:** No Overpass installs / editor; pytest/export framed FUTURE.
- **On-lane:** Two-app literacy, `RGPACK_v1` disk layout + Frame A, export-vs-empty-target rubric, auth-less local routes status, citypack→rgpack gap map.
- **Hard bans present:** Packs as contract (Workshop writes / Race reads); Race lean / no live OSM in Race; empty targets ≠ ship; no GlobalDefault flip; no greenfield city / StreetMap-before-race; NullRHI never PASS.
- **Real citations:** `tools/rgpack/*`, `docs/contracts/RGPACK_v1.md`, golden fixture `tests/fixtures/rgpack/minimal_v1/`, Source module paths, G4/G5 local-only honesty vs GH tip.
- **Freeze-safe:** Stand-down posture; Python-first reopen ship.
- **Annotation-ready:** Routes read-along + deepened contract map — not stubs.

### Gaps to deepen (non-blocking)
- Auth-less local Workshop UI routes still **Not found** / planned — deepen route table when design lands (docs only).
- Overpass CLI absent (honestly marked out-of-scope for slice 1–2) — keep fixture-first path as reopen #1.
- Citypack→rgpack adapter not written — gap map is enough for training; adapter is post-unlock.
- G4/G5 evidence dirs local-only — mirror/commit when Chris wants GH parity.

### Next action
Specialist **annotations pack** OK. No blocking fix.

---

## Overall

| Set | Grade |
|-----|-------|
| Wave 1 training packs (WE + B&E + WW) | **FULL SET PASS** |

All three lanes meet cite-and-path, on-lane scope, hard bans, real citations, freeze-safety (incl. B&E Phase A landed / Phase B HOLD), and annotation readiness. Gaps listed are deepen-later, not FAIL/CONDITIONAL blockers.

**Chris decision ask (unchanged posture):**
1. Accept Wave 1 packs as freeze-safe train-while-HOLD baseline? (QA says yes — FULL SET PASS.)
2. Keep clones / Marketplace / omni editor frozen until you reopen game work?
3. Any Wave 1 lane to deepen next (docs-only), or park until Gate 1 / Burke visual reopen?

---

## Paths written / mirrored

**Project**
- `C:\projects\raceGPS-grokbot-cleveland\docs\evidence\grokbot\agent-training\2026-09-26-WAVE1-TRAINING-QA.md`
- `C:\projects\raceGPS-grokbot-cleveland\docs\evidence\grokbot\agent-training\README.md` (Wave 1 section)
- `C:\projects\raceGPS-grokbot-cleveland\docs\evidence\grokbot\agent-training\WAVE1-INDEX.md`

**Documents mirror**
- `C:\Users\cgp22\Documents\raceGPS-handoff\agent-training\2026-09-26-WAVE1-TRAINING-QA.md`
- `C:\Users\cgp22\Documents\raceGPS-handoff\agent-training\README.md` (Wave 1 section)
- `C:\Users\cgp22\Documents\raceGPS-handoff\agent-training\WAVE1-INDEX.md`
