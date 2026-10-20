# Wave 1 unlock note — 2026-09-27 (Unreal PM)

**Audience:** Chris + Wave 1 agents (WE / B&E / WW / Prototyper / Unreal PM)  
**Role filing:** Unreal PM (raceGPS) — FAIL-CLOSED gate  
**Date:** 2026-09-27 (America/New_York)

---

## Green light

**Chris green light 2026-09-27 → Wave 1 lanes live** (docs + limited lane work under Prototyper unlock scope).

Branch: `grokbot/cleveland-integration`  
Tip notes:
- `2d9cf6d` — handoff / training
- `5f420f6` — showcase skyline keepers (`M_SkylineBackdrop`, `T_Cleveland_SkylineNight`, SourceImages, import helpers)

Keepers handoff: `docs/handoff/2026-09-27-SHOWCASE-KEEPERS-LANDED.md`

---

## STILL FROZEN (do not treat Wave 1 green as full game unlock)

| Frozen | Owner / note |
|--------|----------------|
| Unattended `LaunchClevelandRace` | **Banned** — Chris owns Track A Sunset |
| Gate 1 agent spam | **Banned** |
| Tier A clones | **Banned** |
| Editor multi-owner | **Banned** — one UnrealEditor on omni; **Build & Engine** owns the lock |
| Mode B stills capture as agent next-step without letter | **Hold** until Chris Mode B / attended Track A |
| Mode C / full agent game | **Need letter unlock** from Chris via Prototyper |

NullRHI / black void / pink missing mat ≠ PASS. Box skyline sold as photo PASS while mat exists ≠ PASS.

---

## WE stills plan + QA

| Item | Path | Grade |
|------|------|-------|
| Stills plan | `docs/evidence/grokbot/world-environment-training/2026-09-27-PHOTO-SKYLINE-STILLS-PLAN.md` | PLAN LANDED |
| Unreal PM QA | `docs/evidence/grokbot/agent-training/2026-09-27-WAVE1-PHOTO-SKYLINE-STILLS-PLAN-QA.md` | **PASS** |
| Index row | `docs/evidence/grokbot/agent-training/WAVE1-INDEX.md` | gate row added |

Documents mirrors under `C:\Users\cgp22\Documents\raceGPS-handoff\` (same relative names under `world-environment-training/` and `agent-training/`).

Plan summary (reuse only): EnvActor `bUsePhotoSkylineBackdrop` / `BuildSkylineBackdrop` — no Cesium rebuild / CARLA rebuild / City Sample greenfield. Evidence slot `burke-ez-ribbon/` only. Soft note: do not reimport via `import_skyline_backdrop.py` until hardcoded old path patched; keepers already on tip.

---

## Lane next steps

| Lane | Next (freeze-safe) |
|------|--------------------|
| **@Build & Engine** | Cook/load skyline assets (`M_SkylineBackdrop`, `T_Cleveland_SkylineNight`) under editor lock; log forensics (`photo skyline backdrop built` vs missing-mat fallback); no Tier A clones |
| **@Workshop Web** | Overpass→rgpack CLI export proof; no editor install |
| **@World Environment** | Hold stills until Chris Mode B / attended Track A; call B&E when ready for cook/load (plan says WE ready inventory) |
| **@Unreal PM** | Gate FAIL-CLOSED; re-gate S1–S3 stills evidence when captured |

---

## FAIL-CLOSED reminder

- NullRHI / void / pink mat ≠ PASS  
- Unattended Launch / Gate 1 spam ≠ evidence  
- Cook PASS only from B&E log under one-editor lock  
- Visual PASS only from attended/Mode B stills in `burke-ez-ribbon/` with framing notes + commit SHA

---

## Related

- `docs/handoff/2026-09-26-WAVE1-SPECIALISTS.md` (lane roster; freeze lines still stand except docs + limited Wave 1 work per this unlock)  
- `docs/handoff/2026-09-27-BEST-OF-BOTH-RECIPE.md`  
- Prior freeze/status files under `docs/handoff/` (history kept; this file is the dated Wave 1 unlock pointer)
---

## WW gate (2026-09-27 ~20:49 EDT)

WW Overpass→rgpack CLI export proof + semantic compiler inventory/brief **gated PASS** (FAIL-CLOSED) — see `docs/evidence/grokbot/agent-training/2026-09-27-WAVE1-WW-EXPORT-AND-SEMANTIC-QA.md`. Citypack→rgpack adapter + Workshop UI routes remain post-unlock / not done.
