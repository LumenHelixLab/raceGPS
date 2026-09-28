# Best of both — raceGPS worktree recipe (2026-09-27)

**Owner:** Prototyper / Chris  
**Status:** ACTIVE — grokbot is canonical; showcase keepers land next; reconcile stays local.

## Goal
Keep the best of showcase + agent race-base work without blind folder merges or force-push to `master`.

## Canonical line
| Role | Path | Branch |
|------|------|--------|
| **Daily driver / race-base** | `C:\projects\raceGPS-grokbot-cleveland` | `grokbot/cleveland-integration` |
| Showcase sandbox | `C:\projects\raceGPS` | `feature/cleveland-showcase-demo` |
| Local merge sandbox only | `C:\projects\racegps-reconcile` | `integration/reconciled` (no upstream) |

Do **not** robocopy between folders. Do **not** push `integration/reconciled` or merge to `master` until Gate 1 attended Sunset evidence lands.

## Keep from grokbot (this commit and forward)
- Gate 1 docs under `docs/evidence/grokbot/G6-race-base-mvp/` (markdown + compact excerpt; not full multi-MB logs)
- Wave 1 / Phase C training markdown under `docs/evidence/grokbot/*-training/` and `agent-training/`
- Durable `docs/handoff/*.md`
- `tests/test_burke_ez_recovery.py` + `tools/burke_ez_preview/`
- `docs/evidence/grokbot/burke-ez-ribbon/` metrics + README

## HOLD for Chris REVIEW (not in first clean commit)
- `apps/unreal-akron-beta/citypacks/` (~38MB) — already gitignored; decide LFS vs external vs selective add later
- Track B Phase A TEMP GameMode probe — **not present as dirty code on tip**; if re-landed, keep TEMP markers and strip after ViewportClosed dig closes
- Full `*.log` / pid / monitor dumps under G6 and visual-floor

## Bring from showcase next (second commit — not this one)
- `ClevelandEnvironmentActor` photo-skyline (+ related materials/textures if approved)
- G2/G3 evidence markdown + skyline Python / SourceImages
- Charger door / Glass / Lights `.uasset` visual-floor meshes
- Decide separately whether to push showcase's unpushed docs commit `5de52ac`

## Ignore forever (do not commit)
- `Temp/`, Cesium sqlite, SPA/bundle noise, duplicate `evidence-G6*` stub folders
- G4/G5 folders that only contain build logs
- `_launch_finish_r.ps1` and other local launcher helpers unless shared on purpose

## Sequence
1. **DONE (this pass):** clean ignore + one focused grokbot commit (docs/training/burke keepers)
2. **DONE (this pass):** skyline mat/tex/SourceImages/Python copied; EnvActor/doors/G2-G3 already matched tip — see `2026-09-27-SHOWCASE-KEEPERS-LANDED.md`
3. **Hold:** promote reconcile → origin or merge to `master` until Track A Sunset keep-alive evidence is filed

## Gate 1 reminder
NullRHI / ForceFinish is **not** Gate 1 PASS. Attended windowed Sunset → Racing keep-alive + ViewportClosed dig still open.

