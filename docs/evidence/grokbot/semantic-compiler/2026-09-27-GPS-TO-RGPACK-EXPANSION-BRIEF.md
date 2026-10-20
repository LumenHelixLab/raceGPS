# GPS bbox → semantic citypack → rgpack — expansion brief (one page)

**Date:** 2026-09-27 (America/New_York)  
**Lane:** Workshop Web · SEMANTIC COMPILER PIN  
**Worktree / branch:** `C:\projects\raceGPS-grokbot-cleveland` · `grokbot/cleveland-integration`  
**Status:** Cite-and-path planning only — no compile run, no Cleveland tourism map, no Unreal editor.

## Pipeline (target shape)

```text
GPS bbox / city query
        │
        ▼
 Overpass (XML city compilers) ──cache──► *_raw.osm
        │
        ▼
 Semantic road graph (+ optional buildings / POIs / water / biome)
        │
        ├──► [Akron path] OpenDRIVE .xodr via osm_to_xodr.py
        │
        ▼
 Semantic CITYPACK  (JSON family + optional .xodr)
        │
        ├──► semantic-map-server / UE level-spec helpers
        │
        ▼
 ★ ADAPTER (not built in this deliverable) ★
        │
        ▼
 RGPACK_v1  (manifest.json + streets/checkpoints/spawn/environment)
        │
        ▼
 Race load (Workshop writes; Race reads; Frame A)
```

**Alternate Workshop path (already exists):** Overpass **JSON** → `python -m rgpack export-overpass` → RGPACK_v1 directly (`tools/rgpack/overpass_export.py`). That path is **not** a citypack/XODR adapter.

## Fixture city — Akron (KEEP)

| Item | Path / cite |
|------|-------------|
| Compiler | `tools/akron-semantic-compiler/` entry `compile_akron.py` |
| Bounds | `AKRON_BOUNDS` in `compile_akron.py` |
| Output | `citypacks/akron-oh-beta-001/` (`akron.xodr`, `akron_*` JSON, `akron_semantic_manifest.json`) |
| README pipeline | `tools/akron-semantic-compiler/README.md` |
| Map server | `apps/semantic-map-server/main.py` → `/city/akron` |
| Design locks | Pure Python; WGS84→local meters; Overpass fail→cache; seed 42 |

Akron remains the **regression golden** and the only in-tree city compiler that emits OpenDRIVE today.

## Stub second city (name only — do not build)

| Kind | Id / query | Notes |
|------|------------|-------|
| Universal CLI example (docstring) | `"Cleveland, OH"` | `tools/universal-city-compiler/cli.py` — would derive `{name}_{radius}km` via `city_compiler.compile_city` |
| Lat/lon example | `"41.5,-81.7"` | Same CLI; `custom_{lat}_{lon}_{radius}km` pattern |
| Existing side stub (Akron script) | `citypacks/cleveland/downtown-test` | From `build_cleveland_downtown_test.py` — cite only |
| rgpack offline fixture | `overpass_burke_tiny` | `tests/fixtures/rgpack/overpass_burke_tiny/` |

**Non-goal:** greenfield Cleveland tourism map / absorbing Akron into Cleveland scaffolding.

## Role of each tree

| Tree | Role under pin |
|------|----------------|
| `tools/akron-semantic-compiler/` | Golden fixture city pipeline — KEEP |
| `tools/universal-city-compiler/` | City-agnostic expansion surface (`cli.py`, geocode, tiled Overpass, M2 layers) — evolve here |
| `tools/rgpack/` + `docs/contracts/RGPACK_v1.md` | On-disk Race pack contract; Workshop writer |
| `apps/semantic-map-server/` | Serve citypack JSON — coordinate; do not fork compiler #3 |

## Adapter honesty (citypack ≠ rgpack)

- Citypack semantic manifests (`*_semantic_manifest.json`, optional `opendrive_file`) ≠ RGPACK_v1 (`schemaVersion`, Frame A, `contentHash`, fixed geometry filenames).
- Universal export today: citypack JSON **without** XODR.
- rgpack Overpass exporter states citypack XODR→rgpack is a **post-unlock adapter**; current module is OSM JSON only.
- Until that adapter exists, treat: (1) Akron/universal → citypack, (2) rgpack CLI → Race packs, as **parallel** Workshop outputs.

## Next freeze-safe steps (docs/CLI only)

1. Keep Akron citypack as golden; re-run only behind explicit Workshop approval + cache-first.
2. Document universal CLI stub invocation for a non-Cleveland-tourism query when live Overpass is allowed; prefer offline fixtures for CI.
3. Spec citypack→rgpack adapter (XODR/road_graph → `streets.json` + checkpoints/spawn mapping) against `RGPACK_v1.md` — implement later.
4. Point semantic-map-server at parameterized citypack dir (still no third compiler).

## Companion

Full module matrix: `2026-09-27-SEMANTIC-COMPILER-INVENTORY.md`
