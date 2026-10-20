# Wave 1 — Photo-skyline stills plan QA (Unreal PM)

**Date:** 2026-09-27 (America/New_York)  
**Role:** Unreal PM (raceGPS)  
**Gate:** WE photo-skyline stills plan (`2026-09-27-PHOTO-SKYLINE-STILLS-PLAN.md`)  
**Status:** **PASS** (FAIL-CLOSED gate)  
**Constraint / freeze reminder:** Still NO unattended `LaunchClevelandRace` / Gate 1 spam / Tier A clones / multi-owner editor. Chris owns Track A Sunset. Mode B stills / Mode C / full agent game need letter unlock from Chris via Prototyper. One UnrealEditor on omni — Build & Engine owns the lock.

**Source graded:**  
`docs/evidence/grokbot/world-environment-training/2026-09-27-PHOTO-SKYLINE-STILLS-PLAN.md`  
(Documents mirror: `C:\Users\cgp22\Documents\raceGPS-handoff\world-environment-training\2026-09-27-PHOTO-SKYLINE-STILLS-PLAN.md`)

**Branch / tips cited by plan:** `grokbot/cleveland-integration` — `5f420f6` (showcase skyline keepers); handoff/training sibling tip `2d9cf6d` noted in Wave 1 unlock.

---

## Gate rule (FAIL-CLOSED)

NullRHI / black void / pink missing mat / box skyline sold as photo PASS while mat exists ≠ PASS. No Cesium rebuild / CARLA rebuild / City Sample greenfield. Capture only under Chris Mode B or attended Track A. Cook/load claims belong to B&E under editor lock — WE does not self-claim cook PASS.

---

## Checklist grades

| # | Criterion | Grade | Notes |
|---|-----------|-------|-------|
| 1 | Reuse only — EnvActor `bUsePhotoSkylineBackdrop` / `BuildSkylineBackdrop`; no Cesium / CARLA / City Sample greenfield | **PASS** | Goal + EnvActor path + hard rule + out-of-scope all ban rebuilds; wrap/light existing path only. |
| 2 | Cite real tip assets from `5f420f6` (M_SkylineBackdrop, T_Cleveland_SkylineNight, SourceImages, import script) | **PASS** | Inventory table lists mat, tex, JPG + CREDITS, `import_skyline_backdrop.py`, `create_skyline_backdrop_mat.py`; commit SHA + keepers handoff cited. |
| 3 | Stills bar clear (S1/S2/S3); NullRHI / pink mat / box fallback = FAIL | **PASS** | Shot list S1–S3 with PASS-if framing; Automatic FAIL covers NullRHI, pink missing mat, box sold as photo PASS; optional S4 = FAIL-control only. |
| 4 | Evidence slot `burke-ez-ribbon/` only (no parallel `burke-ez-visual`) | **PASS** | Capture hygiene: prefer `docs/evidence/grokbot/burke-ez-ribbon/`; explicit "do not invent `burke-ez-visual/`". Fixes prior Pack 01 path-drift note. |
| 5 | Capture gated on Chris Mode B / attended Track A — no unattended LaunchClevelandRace as next step | **PASS** | Status, Preflight #5, Capture hygiene, Blockers all gate attended/Mode B; freeze line forbids unattended Launch / Gate 1 spam. |
| 6 | Soft note on `import_skyline_backdrop.py` hardcoded old path — do not reimport until patched; keepers already on tip | **PASS** | Inventory soft-warns old `racegps` path; out-of-scope = note only until reimport needed; keepers already on tip (no copy). |
| 7 | Cook/load handed to B&E correctly | **PASS** | Preflight + Blockers: B&E owns editor lock + cook/load; PASS table requires B&E log excerpt; WE ready inventory only — capture blocked until lock + attended/Mode B. |

---

## Overall

| Gate | Grade |
|------|-------|
| WE photo-skyline stills plan (2026-09-27) | **PASS** |

All seven FAIL-CLOSED criteria met. Plan is freeze-safe and ready for B&E cook/load under editor lock; stills capture remains blocked until Chris Mode B / attended Track A.

### Gaps (non-blocking / 1-line)

- No gaps that block PASS. Soft deepen later: when S1–S3 land, Unreal PM must re-gate stills evidence (log cue + SHA + framing) before any visual PASS claim — plan already states this; unlock note carries the freeze.

### Next action

- **B&E:** cook/load `M_SkylineBackdrop` / `T_Cleveland_SkylineNight` under one-editor lock; log forensics (`photo skyline backdrop built` vs missing-mat fallback); no Tier A clones.  
- **WE:** hold capture until Chris Mode B / attended Track A; do not reimport until import script path patched.  
- **WW:** freeze-safe Overpass→rgpack CLI export proof (no editor install).  
- **Unreal PM:** unlock note filed; re-gate when stills evidence lands.

---

## Paths written / mirrored

**Project**
- `C:\projects\raceGPS-grokbot-cleveland\docs\evidence\grokbot\agent-training\2026-09-27-WAVE1-PHOTO-SKYLINE-STILLS-PLAN-QA.md`
- `C:\projects\raceGPS-grokbot-cleveland\docs\evidence\grokbot\agent-training\WAVE1-INDEX.md` (row added)

**Documents mirror**
- `C:\Users\cgp22\Documents\raceGPS-handoff\agent-training\2026-09-27-WAVE1-PHOTO-SKYLINE-STILLS-PLAN-QA.md`
- `C:\Users\cgp22\Documents\raceGPS-handoff\agent-training\WAVE1-INDEX.md` (row added)