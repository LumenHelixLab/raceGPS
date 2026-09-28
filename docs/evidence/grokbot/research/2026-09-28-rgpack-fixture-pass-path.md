# Research brief: rgpack offline fixture PASS path (Workshop CLI wire)

**Date:** 2026-09-28 (America/New_York)  
**Author:** Grok Bot Task 7  
**Lane impacted:** Workshop

## Question

Does a freeze-safe, already-proven `python -m rgpack export-overpass --fixture` PASS path exist so Workshop Compile/Validate can call it over IPC without Unreal, live Overpass, or a Research & Training bot?

## Sources (with dates)

| Source | URL / path | Accessed | Notes |
|--------|------------|----------|-------|
| Overpass → rgpack export proof | `docs/evidence/grokbot/workshop-web-training/2026-09-27-OVERPASS-RGPACK-EXPORT-PROOF.md` | 2026-09-28 | Offline fixture RESULT PASS; Unreal not used |
| Semantic compiler pin | `docs/handoff/2026-09-27-SEMANTIC-COMPILER-PIN.md` | 2026-09-28 | Akron `tools/akron-semantic-compiler` pinned; rgpack contract |
| Offline fixture | `tests/fixtures/rgpack/overpass_burke_tiny/overpass.json` | 2026-09-28 | Burke ~41.51/-81.69 Overpass-like JSON |
| CLI entry | `tools/rgpack/__main__.py` | 2026-09-28 | `export-overpass` + `validate` subcommands |
| OUT OF SCOPE | `docs/evidence/grokbot/research/OUT-OF-SCOPE-research-training-bot.md` | 2026-09-28 | Do not create Research & Training bot |

## Findings

- Canonical offline proof (2026-09-27): `set PYTHONPATH=tools` then `python -m rgpack export-overpass --fixture --out Saved\raceGPS\packs\burke_overpass_proof_v1` → **RESULT PASS** (`packId` / `contentHash` recorded in proof doc).
- Re-validate: `python -m rgpack validate <packDir>` → same PASS.
- Fixture path resolves from worktree: `tests\fixtures\rgpack\overpass_burke_tiny\overpass.json`.
- Semantic pin keeps Akron compiler as golden reference; primary Workshop MVP happy-path remains **rgpack fixture export**, not Akron Unreal merge or live Overpass.
- Launcher settings already expose `paths.workshopPython` (`.venv-grokbot\Scripts\python.exe`) and `paths.worktreeRoot`.

## Recommend / Reject

**Recommend:** Wire IPC `workshop:cli` to `workshopPython -m rgpack …` with `cwd=worktreeRoot` and `PYTHONPATH=worktreeRoot\tools`; Compile = fixture export; Validate = `validate <packDir>`.  
**Reject:** Live Overpass as MVP gate; Unreal/cook/Gate1; creating Research & Training bot; full Akron Unreal shell merge.  
**Why:** Existing offline PASS path + pin cite unblocks Task 7 without violating CruiseSprint / freeze bans.
