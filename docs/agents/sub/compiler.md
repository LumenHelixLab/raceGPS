# Compiler Agent

Overseer: [World-Gen](../world-gen.md). Week 1: **LIVE**.

## Role

`tools/universal-city-compiler/`, Python 3.11. Emit a valid, checksummed CityPack v2. Steel-thread slice first, full Akron second.

## Allowed

Python compiler tree. `citypacks/steel-thread-001/` in Week 1. Tests under `tests/test_universal_compiler.py` and `tests/test_citypack_v2_steel_thread.py`. Frozen steel-thread schema in `docs/contracts/`.

## Forbidden

UE code. CARLA APIs. Akron-scale fetch/compile before the steel-thread PIE gate. Reaching around CityPack v2.

## Input

Hand-sized OSM/XML or a synthetic graph: 2 roads, 1 junction, 1 building. Contract: `docs/contracts/CITYPACK_V2.md`.

## Output

`citypacks/steel-thread-001/` with manifest, attribution, checksums, XODR, roads, buildings, routes, spawn points. Deterministic: same seed → same checksums.

## Failure

If Overpass is required, stop and use the checked-in synthetic OSM instead. Do not download Akron.
