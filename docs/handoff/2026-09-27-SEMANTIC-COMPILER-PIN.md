# SEMANTIC COMPILER PIN — GPS → race-course map compiler (2026-09-27)

**Owner lane:** Workshop Web (under Prototyper)  
**Status:** PINNED — do not delete, rename away, or absorb into Cleveland-only scaffolding  
**Chris intent:** Akron semantic street builder is the reference for a **general-purpose** semantic GPS → race-course map compiler; Cleveland race-base and older Akron work run in parallel.

## Canonical trees (race-base worktree)

Worktree: `C:\projects\raceGPS-grokbot-cleveland`  
Branch: `grokbot/cleveland-integration` (origin tip includes handoff + skyline keepers)

| Role | Path | Rule |
|------|------|------|
| **Reference implementation (Akron)** | `tools/akron-semantic-compiler/` | Keep as golden fixture city pipeline. Pure Python. Entry: `compile_akron.py`. Output: `citypacks/akron-oh-beta-001/` |
| **General-purpose expansion** | `tools/universal-city-compiler/` | City-agnostic sibling (Overpass, road/route/POI, `cli.py`). Evolve this toward multi-city GPS→course; do not gut Akron while doing so |
| Pack contract | `tools/rgpack/`, `docs/contracts/RGPACK_v1.md`, Unreal `raceGPSPack` | Compiler outputs must stay compatible with `.rgpack` / citypack manifests Race loads |
| Related | `apps/semantic-map-server/` | Supporting map service — coordinate, do not fork a third compiler |

## Akron reference pipeline (do not break)

```
fetch_osm (or cache) → road graph → OpenDRIVE (.xodr) → routes/checkpoints/POIs → export manifest
```

Documented in `tools/akron-semantic-compiler/README.md`. Design locks: pure Python (no CARLA/OSMnx), WGS84→local meters, Overpass 504→cache fallback, fixed RNG for repro.

## Parallel development rules

1. **Cleveland race-base** (playable Burke / Gate 1 / visual floor) stays the gameplay scoreboard on this branch.  
2. **Akron semantic compiler** stays pinned for expansion — not “legacy to delete after Cleveland.”  
3. **General compiler** grows from `universal-city-compiler` + rgpack contract; Akron remains the regression golden city.  
4. Do **not** blind-robocopy worktrees or merge `integration/reconciled` / `master` without Prototyper + Chris.  
5. Untracked `apps/unreal-akron-beta/citypacks/` on grokbot remains HOLD until Chris decides LFS vs selective add.

## Workshop Web next (freeze-aware)

- Cite-and-path inventory: Akron compiler modules vs universal-city-compiler surface (what is shared, what is Akron-hardcoded).  
- One-page expansion brief: “GPS bbox → semantic citypack → rgpack” with Akron as fixture and a second city as stub only (no greenfield Cleveland tourism map).  
- Evidence under `docs/evidence/grokbot/workshop-web-training/` or a dated `docs/evidence/grokbot/semantic-compiler/` folder.  
- No Unreal editor spam; CLI/docs OK. Unreal PM gates FAIL-CLOSED.

## Non-goals (for this pin)

- Replacing Race Chaos / Gate 1 work with map-compiler theater  
- Rebuilding CARLA or a City Sample Cleveland  
- Force-push / master merge

## Sign-off

Pinned by Prototyper per Chris (2026-09-27). Workshop Web owns day-to-day; Course Architect consults on course truth; Build & Engine only if packaging the Workshop target.
