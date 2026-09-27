# Dirty Git Inventory — LumenHelixLab/raceGPS (ADVICE ONLY)

**Date:** 2026-09-26 (ET)  
**Machine:** omni (`14689435-c6b8-4643-bec2-a7b74d7e5dae`)  
**Scope:** three worktrees — read-only inventory. **No** `git add` / commit / push / stash / reset / clean / file modifications were performed while gathering this.

---

## Executive summary (counts)

| Worktree | Branch | Ahead/behind | COMMIT items | IGNORE items | STASH/REVIEW items |
|----------|--------|--------------|--------------|--------------|--------------------|
| `C:\projects\raceGPS` | `feature/cleveland-showcase-demo` | **ahead 1** of origin | ~6 | ~100+ (Temp/cache/noise) | ~12 (uassets, EnvActor, unpushed commit) |
| `C:\projects\raceGPS-grokbot-cleveland` | `grokbot/cleveland-integration` | up to date with origin | ~15 | ~40+ (logs/pids/dupes/Temp) | ~5 (citypacks binaries, GameMode probe keep-vs-strip) |
| `C:\projects\racegps-reconcile` | `integration/reconciled` | **no upstream** | 0 | 1 (pytest tmp) | 1 (`DayNightCycle.h`) |

Rough “bucket” counts below treat **logical commit units** (file groups), not every Temp script as a separate COMMIT candidate.

---

## 1. `C:\projects\raceGPS` — `feature/cleveland-showcase-demo`

### Branch / sync
- HEAD: `5de52ac` — *docs: approved 10-milestone program plan (M1 Real Roads next)*
- **Ahead of `origin/feature/cleveland-showcase-demo` by 1 commit** (unpushed local commit — STASH/REVIEW for push decision, not a working-tree change).

### `git status --short` (summary)
- **Modified (tracked):** 2  
  - `apps/unreal-akron-beta/Source/raceGPSAkronBeta/Private/ClevelandEnvironmentActor.cpp`  
  - `apps/unreal-akron-beta/Source/raceGPSAkronBeta/Public/ClevelandEnvironmentActor.h`
- **Untracked:** many (see table). Warning: could not open `.pytest_cache/` (Permission denied) — ignore.

### `git diff --stat` (tracked mods)
```
.../Private/ClevelandEnvironmentActor.cpp | 75 +++++++++++++++++++++-
.../Public/ClevelandEnvironmentActor.h    | 10 +++
 2 files changed, 84 insertions(+), 1 deletion(-)
```

**What changed (brief):**
- **Header:** adds `SkylineBackdropMesh`, `bUsePhotoSkylineBackdrop`, and `BuildSkylineBackdrop()`.
- **CPP:** implements photographic downtown skyline backdrop (procedural mesh arc, real Cleveland panorama CC BY 2.0 Erik Drost; view-only — no collision/shadow). Wired from `LoadAndBuild()`.

### Untracked by top-level (expanded file count ≈ 116)

| Top-level | Files (approx) | Size |
|-----------|----------------|------|
| `(root)` | 4 | ~0.73 MB |
| `apps/` | 109 | ~22 MB |
| `docs/` | 2 | ~0.02 MB |
| `generated/` | 1 listed (dir has more on disk) | ~0.3 MB listed / ~20 MB under `generated/` on disk |

#### Notable subdirectory sizes
| Path | Files | Size |
|------|-------|------|
| `apps/unreal-akron-beta/Temp/` | 98 | ~4.1 MB |
| `Content/SourceImages/` | 2 | ~7.3 MB |
| `Content/Textures/` | 1 | ~7.3 MB |
| `Content/Carla/.../Glass/` | 16 | ~1.1 MB |
| Door/Lights `.uasset` (5 new) | 5 | ~2.3 MB |
| `cesium-request-cache.sqlite*` | 3 | tiny + shm/wal |
| `docs/evidence/` | 2 md | tiny |
| Root: `raceGPS-autonomous-gates.bundle` | 1 | ~657 KB |

### COMMIT vs IGNORE vs STASH/REVIEW

#### COMMIT (when Chris later approves)
| Item | Why |
|------|-----|
| `docs/evidence/grokbot/G2-prep/COORDINATE_CONSUMER_INVENTORY.md` | Source/docs/evidence for branch |
| `docs/evidence/grokbot/G3-prep/BURKE_SOURCE_AUDIT.md` | Source/docs/evidence for branch |
| `Content/Python/create_skyline_backdrop_mat.py` | Meaningful tooling for skyline feature |
| `Content/Python/import_skyline_backdrop.py` | Same |
| `Content/Python/attach_charger_doors.py` | Product attach script (if doors ship) |
| `Content/SourceImages/` + `CREDITS.md` (if present) | Licensed panorama source for backdrop |
| Handoff markdowns if intended as repo docs: `raceGPS_Grokbot_Multiagent_Handoff_v1.0.md`, `unreal-game-dev-HANDOFF.md` | Only if Chris wants them in-tree (else keep under Documents handoff) |

#### IGNORE / do not commit
| Item | Why |
|------|-----|
| `apps/unreal-akron-beta/Temp/**` (all `apply_m2_fix*.py`, `patch_*.py`, `p_*.py`, pids, markers, `.log.bak_pre`, PNGs, sentinels) | Intermediate patch scripts / noise |
| `cesium-request-cache.sqlite*` | Cesium cache — local |
| `Content/Python/_door_probe.py`, `_ground_probe.py` | Probe/scratch |
| `generated/diag_live_window.png` | Transient diagnostic |
| `32_c_u_b_i_t_24_point_atlas_infographic_spa.html` | Unrelated SPA dump at root |
| `raceGPS-autonomous-gates.bundle` | Large binary bundle — not a product asset unless explicitly adopted |
| `.pytest_cache/` (permission-denied noise) | Cache |

#### STASH/REVIEW (Chris decide)
| Item | Why |
|------|-----|
| **Unpushed commit `5de52ac`** (ahead 1) | Already committed locally; push or leave |
| `ClevelandEnvironmentActor.cpp/.h` photo skyline | Feature code — meaningful, but pairs with Content binaries |
| `SM_DodgeCharger2024_Door*.uasset`, `Lights.uasset`, `Glass/` | `.uasset` / CARLA door meshes / Glass |
| `M_SkylineBackdrop.uasset`, `Content/Textures/` | Content binaries for skyline |
| `Content/CesiumSettings/` | Editor-local settings? Review before commit |

---

## 2. `C:\projects\raceGPS-grokbot-cleveland` — `grokbot/cleveland-integration`

### Branch / sync
- HEAD: `b5e1b4b` — *docs(evidence): G6 windowed Sunset finish+R FAIL-CLOSED ViewportClosed*
- **Up to date** with `origin/grokbot/cleveland-integration`.

### `git status --short` (summary)
- **Modified (tracked):** 2  
  - `apps/unreal-akron-beta/Source/raceGPSAkronBeta/Private/ClevelandShowcaseGameMode.cpp` (+37 lines)  
  - `docs/evidence/grokbot/G6-race-base-mvp/finish-r-proof-note.txt` (+3 lines banner)
- **Untracked:** large evidence/docs tree, `Temp/`, `citypacks/`, tests/tools, handoffs.

### `git diff --stat` (tracked mods)
```
.../Private/ClevelandShowcaseGameMode.cpp          | 37 ++++++++++++++++++++++
.../G6-race-base-mvp/finish-r-proof-note.txt       |  3 ++
 2 files changed, 40 insertions(+)
```

**What changed (brief):**
- **GameMode:** **Track B Phase A probe** in `Tick` — viewport/focus heartbeat + “VIEWPORT LOST while Racing” warning (`Misc/App.h`). Marked `TEMP Track B dig (Phase A) — strip after Gate 1 ViewportClosed dig closes`.
- **finish-r-proof-note.txt:** banner clarifying NullRHI/ForceFinish path is **NOT Gate 1 PASS**.

### Untracked by top-level (expanded ≈ 152 files)

| Top-level | Files | Size |
|-----------|-------|------|
| `(root)` | 1 (`HANDOFF_TO_HUMAN_TEAM.md`) | ~0 |
| `Temp/` | 6 | ~0.02 MB |
| `apps/` (mostly `citypacks/`) | 29 | ~37 MB |
| `docs/` | 113 | ~19.6 MB |
| `tests/` | 1 | ~0.01 MB |
| `tools/` | 2 | ~0.01 MB |

#### Notable dirs
| Path | Files | Size |
|------|-------|------|
| `apps/unreal-akron-beta/citypacks/` | 30 | ~38 MB (json/osm/xodr) |
| `docs/evidence/grokbot/G6-race-base-mvp/` | 32 | ~19.2 MB (mostly logs) |
| Training folders under `docs/evidence/grokbot/*-training/` | ~40 | small |
| Duplicate stubs: `evidence-G6/`, `evidence-G6-mvp/`, `evidence-G6-race-base-mvp/` | few | tiny duplicates of G6 README/playbook |
| `docs/handoff/` | 21 | ~0.05 MB |
| `Temp/` | patch scripts + `commit-msg.txt` | noise |

### COMMIT vs IGNORE vs STASH/REVIEW

#### COMMIT (when Chris later approves)
| Item | Why |
|------|-----|
| **Track B Phase A GameMode probe** (`ClevelandShowcaseGameMode.cpp`) | Explicitly called out — commit while dig is active *or* strip later; recommendation: **commit with TEMP markers** if still debugging, else strip before long-term |
| Wave1/G6 evidence markdown: `docs/evidence/grokbot/G6-race-base-mvp/2026-09-25-GATE1-*.md`, `README.md` | Should be in repo |
| `docs/evidence/grokbot/README.md` | Index |
| `finish-r-proof-note.txt` (modified banner) | Corrects readiness narrative |
| `finish-r-windowed-viewportclosed-excerpt.txt` | Compact proof excerpt (not full multi-MB logs) |
| `HANDOFF_TO_HUMAN_TEAM.md` | Team-facing handoff |
| Selected `docs/handoff/*.md` that are durable | Keep durable notes; skip ephemeral |
| `tests/test_burke_ez_recovery.py` + `tools/burke_ez_preview/` | Meaningful feature/test code |
| Training markdown under `docs/evidence/grokbot/*-training/` (small) | Source/docs if intentional curriculum |
| `G4-racegpspack/`, `G5-workshop-race-targets/` (if small md/json evidence) | Gate evidence folders |

#### IGNORE / do not commit
| Item | Why |
|------|-----|
| `Temp/**` | Intermediate Python patch scripts |
| `*.log` under G1/G2/G3/G6/visual-floor (`ue-editor-build*.log`, `finish-r-*.log`, `pytest.log`, `pip-*.log`, `push.log`, etc.) | Log noise |
| `*-pid.txt`, `finish-r-monitor.txt*`, `smoke-stderr.txt`, `smoke-pid.txt` | Pids / markers |
| `track-b-phase-a-build.log`, `finish-r-proof-full.log` | Large/redundant build dumps |
| Duplicate folders `evidence-G6/`, `evidence-G6-mvp/`, `evidence-G6-race-base-mvp/` | Redundant vs canonical `G6-race-base-mvp/` |
| `_launch_finish_r.ps1` | Local launcher helpers (optional — review if shared) |

#### STASH/REVIEW (Chris decide)
| Item | Why |
|------|-----|
| `apps/unreal-akron-beta/citypacks/` (~38 MB json/osm/xodr) | Large data — product course packs vs LFS vs external |
| GameMode TEMP probe longevity | Keep for Gate 1 dig vs strip after close |
| Full vs excerpt logs for archival | Prefer excerpts in git; full logs outside |

---

## 3. `C:\projects\racegps-reconcile` — `integration/reconciled`

### Branch / sync
- HEAD: `472400c` — *test: drop route_loop_closure suite — superseded by graph engine + test_route_topology contract tests*
- **No upstream configured** for `integration/reconciled` (cannot report ahead/behind vs origin).

### `git status --short`
```
 M apps/unreal-akron-beta/Source/raceGPSAkronBeta/Public/DayNightCycle.h
?? .pytest_tmp_reconcile/
```

### `git diff --stat`
```
.../Public/DayNightCycle.h | 8 --------
 1 file changed, 8 deletions(-)
```

**What changed (brief):**
- Working tree **removes a duplicate** pair of `NightMoonIntensity` / `bMoonAtNight` UPROPERTY declarations. HEAD still has the members declared twice (identical names — would be invalid C++ if both compiled as-is). Working copy keeps one pair. Looks like a merge-dedup fix.

### Untracked
| Path | Files | Size |
|------|-------|------|
| `.pytest_tmp_reconcile/` | ~224 | ~0.05 MB |

### COMMIT vs IGNORE vs STASH/REVIEW

#### COMMIT
- None recommended without Chris review of the header dedup.

#### IGNORE
| Item | Why |
|------|-----|
| `.pytest_tmp_reconcile/` | Pytest cache/tmp — add to `.gitignore` later |

#### STASH/REVIEW
| Item | Why |
|------|-----|
| `DayNightCycle.h` duplicate-member removal | Correctness fix (dedup) — almost certainly should land, but flagged per instruction as **STASH/REVIEW** on reconcile tree |

---

## Cross-worktree notes

1. All three are linked worktrees of the same repo (`raceGPS`, `raceGPS-grokbot-cleveland`, `racegps-reconcile`).
2. Showcase is the only branch **ahead of origin** (1 commit: program-plan docs).
3. Grokbot holds the active **Track B Phase A GameMode probe** + richest G6 evidence set.
4. Reconcile is nearly clean except DayNightCycle dedup + pytest tmp.
5. **Do not** commit Cesium sqlite, Temp patch farms, pids, or duplicate `evidence-G6*` stubs.
6. Prefer committing **markdown evidence + excerpts**; keep multi-MB UE logs / citypack dumps out of git unless LFS/policy says otherwise.

---

## Suggested later `.gitignore` candidates (advice only — not applied)
```
apps/unreal-akron-beta/Temp/
apps/unreal-akron-beta/cesium-request-cache.sqlite*
.pytest_tmp_reconcile/
.pytest_cache/
**/finish-r-*-pid.txt
**/smoke-pid.txt
**/playtest_pid.txt
```

---

*Generated read-only on omni, 2026-09-26 ET. No git mutations.*
