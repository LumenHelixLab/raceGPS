# Wave 1 - Workshop Web export proof + semantic compiler QA (Unreal PM)

**Date:** 2026-09-27 ~20:49 EDT (America/New_York)  
**Role:** Unreal PM (raceGPS)  
**Gate:** WW Overpass→rgpack CLI export proof + SEMANTIC COMPILER PIN cite-and-path set  
**Status:** **PASS** (FAIL-CLOSED gate)  
**Constraint / freeze reminder:** Still NO unattended `LaunchClevelandRace` / Gate 1 spam / Tier A clones / multi-owner editor. Chris owns Track A Sunset. Mode B stills / Mode C / full agent game need letter unlock via Prototyper. One UnrealEditor on omni — Build & Engine owns the lock. This gate is **CLI/docs only** — no Unreal editor launch.

**Sources graded:**

| Doc | Project path | Claimed sha256 | Verify |
|-----|--------------|----------------|--------|
| Overpass→rgpack export proof | `docs/evidence/grokbot/workshop-web-training/2026-09-27-OVERPASS-RGPACK-EXPORT-PROOF.md` | `26157aa2d4347029302e955eedf190e0f2806396dfe1e21653061eae0f89779e` | **MATCH** (project + Documents) |
| Semantic compiler inventory | `docs/evidence/grokbot/semantic-compiler/2026-09-27-SEMANTIC-COMPILER-INVENTORY.md` | `8eccc3fd6fd534acbe82a74da53a36389c17149d07c03ac241ea058a49053b95` | **MATCH** (project + Documents) |
| GPS→rgpack expansion brief | `docs/evidence/grokbot/semantic-compiler/2026-09-27-GPS-TO-RGPACK-EXPANSION-BRIEF.md` | `6452a03c13331d151be978f6239f2f3a254276027ab8ff6986c5d25905106541` | **MATCH** (project + Documents) |

Documents mirrors (flat): `C:\Users\cgp22\Documents\raceGPS-handoff\workshop-web-training\` and `...\semantic-compiler\`.

**Pin context:** `docs/handoff/2026-09-27-SEMANTIC-COMPILER-PIN.md` — Akron KEEP; universal = city-agnostic sibling; Cleveland race-base = gameplay scoreboard.

**Host re-check (omni, 2026-09-27 ~20:49 EDT):** `python -m rgpack validate` on offline + live packs → **RESULT PASS**; `pytest tests\test_rgpack_schema.py -q` → **6 passed**. No UnrealEditor.

---

## Gate rule (FAIL-CLOSED)

- Real export evidence required: CLI transcript + on-disk pack + `validate_pack_dir` / `python -m rgpack validate` **PASS** + contentHash. Empty Game target / module stub ≠ export PASS.
- Freeze-safe: no Unreal editor / PIE / `LaunchClevelandRace` as next step for this proof.
- `tools/rgpack` + `docs/contracts/RGPACK_v1.md` on-disk trust; Workshop writes, Race reads; Race must not call Overpass.
- Semantic: Akron compiler KEEP; universal-city-compiler = expansion shell; Cleveland race-base stays gameplay scoreboard; citypack→rgpack adapter = **post-unlock** only.
- Do **not** sell planned auth-less Workshop UI routes as done.

---

## A) Overpass→rgpack export proof — checklist

| # | Criterion | Grade | Notes |
|---|-----------|-------|-------|
| 1 | Real export evidence (commands + validate PASS), not empty target | **PASS** | Offline: `python -m rgpack export-overpass --fixture --out Saved\raceGPS\packs\burke_overpass_proof_v1` → RESULT PASS; re-validate PASS. Live tiny Burke bbox also PASS (optional). Pack files present: manifest/streets/checkpoints/spawn/environment. Unreal PM re-ran validate 2026-09-27 ~20:49 EDT — both packs PASS. |
| 2 | Freeze-safe / no Unreal editor required | **PASS** | Verdict table: Unreal / PIE / LaunchClevelandRace **Not used**. Honest limits #1. Python CLI only. |
| 3 | RGPACK_v1 / `tools/rgpack` on-disk trust | **PASS** | Package `tools/rgpack/` (`overpass_export.py`, `__main__.py`, schema/io); contract `docs/contracts/RGPACK_v1.md`; wrapper `tools/overpass_to_rgpack.py`; fixtures `tests/fixtures/rgpack/overpass_burke_tiny/` + `minimal_v1/`. Offline pack contentHash `sha256:8f8d9e02c300ff1c1556712c1ebabb99ed80642be8ef9db793a3fbc6659850dc` matches claim + re-validate. Live hash `sha256:015b37c1...` matches proof transcript (network-volatile; offline is SoT). |
| 4 | Regression / test evidence | **PASS** | Doc cites `pytest tests\test_rgpack_schema.py -q` → 6 passed. Unreal PM re-ran: **6 passed** in 0.10s. |
| 5 | Honest gaps (citypack adapter post-unlock; no UI-route ship claim) | **PASS** | Explicit: citypack XODR→rgpack still post-unlock; not a rebrand of Burke/EZ citypack; empty Game target ≠ export PASS; Workshop UI routes called out as planned/not found in sibling README. Certification `provisional`. |

**Export proof grade: PASS**

---

## B) Semantic compiler set — checklist

| # | Criterion | Grade | Notes |
|---|-----------|-------|-------|
| 1 | Akron KEEP (do not delete/absorb) | **PASS** | Inventory §1/§3/§6 + brief “Fixture city - Akron (KEEP)”; pin echoed. On-disk `tools/akron-semantic-compiler/` + `citypacks/akron-oh-beta-001/` (xodr + JSON family) present. |
| 2 | universal-city-compiler = city-agnostic expansion shell | **PASS** | Inventory module matrix + brief role table: evolve multi-city GPS→course here; no XODR today (honest). `tools/universal-city-compiler/` on disk (`cli.py`, geocode, tiled Overpass, M2 layers). |
| 3 | Cleveland race-base remains gameplay scoreboard | **PASS** | Pin §Parallel #1 stated; inventory/brief non-goals: no greenfield Cleveland tourism map; downtown-test stub cite-only. Race-base gameplay not sold as compiler theater. |
| 4 | citypack→rgpack adapter post-unlock; parallel Workshop outputs | **PASS** | Inventory §4.5 + brief “Adapter honesty”; rgpack Overpass JSON path separate from citypack/XODR. Do not claim citypack ≡ rgpack. |
| 5 | Freeze-safe cite-and-path (no editor install / no compile run as next step) | **PASS** | Method: cite-and-path only; no UnrealEditor / CARLA / City Sample / StreetMap; no greenfield Cleveland compile. Next steps = docs/CLI/spec only. |
| 6 | FAIL-CLOSED: no selling planned UI routes as done | **PASS** | Semantic set does not claim Workshop UI. Sibling WW README keeps “Auth-less local Workshop UI routes = Planned / not found”. |

**Semantic set grade: PASS**

---

## Overall

| Gate | Grade |
|------|-------|
| WW Overpass→rgpack CLI export proof (2026-09-27) | **PASS** |
| Semantic compiler inventory + expansion brief (2026-09-27) | **PASS** |
| **Combined WW export + semantic QA** | **PASS** |

All FAIL-CLOSED criteria met. Export proof is freeze-safe green-light for Overpass JSON→RGPACK_v1 CLI; citypack→rgpack adapter and Workshop UI routes remain **not done**. Semantic pin honored (Akron KEEP / universal expand / Cleveland race-base scoreboard).

### Gaps (non-blocking / honest)

- Live Overpass pack hash is network-volatile; cite offline fixture hash for stable SoT (proof already states this).
- Centerline stitch = provisional / not a full road-graph race-course certifier (proof honest limit #6).
- Universal still emits citypack **without** XODR; only Akron emits OpenDRIVE today.
- citypack→rgpack adapter not implemented — correctly gated post-unlock.
- Workshop auth-less UI routes still planned/not found — do not deepen as ship claim.

### Next action

- **WW:** optional deepen only behind unlock (citypack→rgpack adapter spec; UI routes when design lands). Do not claim Burke/EZ citypack as `validate_pack_dir` PASS without adapter.
- **B&E:** cook/load skyline under editor lock (separate gate).
- **WE:** hold stills until Chris Mode B / attended Track A.
- **Unreal PM:** this QA closes WW export + semantic cite-and-path gate; re-gate if adapter or UI claims appear.

---

## Hash verify summary

| Artifact | Claimed | Project | Documents | Match |
|----------|---------|---------|-----------|-------|
| EXPORT-PROOF.md | `26157aa2…89779e` | yes | yes | **yes** |
| SEMANTIC-INVENTORY.md | `8eccc3fd…053b95` | yes | yes | **yes** |
| GPS-EXPANSION-BRIEF.md | `6452a03c…06541` | yes | yes | **yes** |
| Offline pack contentHash | `8f8d9e02…9850dc` | validate PASS | n/a (pack on project) | **yes** |
| Live pack contentHash | `015b37c1…f6f118` | validate PASS | n/a | **yes** (volatile) |
| pytest `test_rgpack_schema.py` | 6 passed | 6 passed @ ~20:49 EDT | n/a | **yes** |

---

## Paths written / mirrored

**Project**
- `C:\projects\raceGPS-grokbot-cleveland\docs\evidence\grokbot\agent-training\2026-09-27-WAVE1-WW-EXPORT-AND-SEMANTIC-QA.md`
- `C:\projects\raceGPS-grokbot-cleveland\docs\evidence\grokbot\agent-training\WAVE1-INDEX.md` (WW export + semantic rows)
- `C:\projects\raceGPS-grokbot-cleveland\docs\handoff\2026-09-27-WAVE1-UNLOCK.md` (one-line WW gated append; not wiped)

**Documents mirror**
- `C:\Users\cgp22\Documents\raceGPS-handoff\agent-training\2026-09-27-WAVE1-WW-EXPORT-AND-SEMANTIC-QA.md`
- `C:\Users\cgp22\Documents\raceGPS-handoff\agent-training\WAVE1-INDEX.md` (rows)
- `C:\Users\cgp22\Documents\raceGPS-handoff\2026-09-27-WAVE1-UNLOCK.md` (one-line append)