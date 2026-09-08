# CURRENT_STATE — G1

**Updated:** 2026-09-07 (America/New_York)
**Claim level:** OBSERVED / REPRODUCED_LOCALLY

## Paths
| Role | Path | HEAD / note |
|---|---|---|
| Showcase truth (untouched) | C:\projects\racegps | f2a8ecd feature/cleveland-showcase-demo |
| Integration worktree | C:\projects\raceGPS-grokbot-cleveland | 0ad434c grokbot/cleveland-integration |
| Bundle | C:\Users\cgp22\AppData\Local\Temp\raceGPS-autonomous-gates.bundle | SHA-256 matched |
| master | C:\projects\racegps | b56b6c8 |

## Bundle
- SHA-256: 9998a92c3f9e57576001cd595c93fdd62abc95bbcf24447d57494a36b8c54592 — MATCH (REPRODUCED_LOCALLY)
- git bundle verify OK; requires b56b6c8 (present)
- Fetched codex/d1-cleveland-build-baseline -> 0ad434c2ba6d3f8c246c34fcf4d93f8653df57f3

## Dirty leftovers on showcase checkout (not deleted)
Untracked Temp scripts/caches, Cesium sqlite, pytest_cache permission warning, local handoff/bundle copies under repo root. Left in place per G1 rules.

## Host (OBSERVED)
- Windows 11 Home 10.0.26200
- AMD Ryzen AI 9 365 (10c/20t) + Radeon 880M (no discrete NVIDIA / nvidia-smi absent)
- RAM ~31.3 GB total; C: ~376 GB free
- Python 3.11.15, Node v26.3.0
- VS Build Tools 2022 17.14.31
- UE: C:\Program Files\Epic Games\UE_5.7 -> Build.version 5.7.4 (CL 51494982, ++UE5+Release-5.7)
- Plugins: ChaosVehiclesPlugin (Experimental), CesiumForUnreal (Marketplace) present
- uproject EngineAssociation 5.7; ChaosVehiclesPlugin enabled

## GameMode
D1 baseline lacked GlobalDefaultGameMode. Patched in worktree DefaultEngine.ini to CruiseSprintGameMode (+ GameInstanceClass) to preserve showcase contract. Not auto-merged into showcase.

## Maps present (worktree Content)
- Content/Maps/AkronWorld.umap
- Content/Maps/Cleveland5_0KmWorld.umap
Showcase additionally has Akron5_0KmWorld.umap. No playability claimed.

## G1 results (REPRODUCED_LOCALLY)
- pytest exit 0 (222 passed, 7 skipped)
- akron citypack audit exit 1 (preserved)
- UE raceGPSAkronBetaEditor Win64 Development final exit 0
- Verdict: PASS — see docs/evidence/grokbot/G1-host-baseline/VERDICT.md
- GATES.json G1=PASS; G2-G5=PENDING
