# M2 — Real Roads: Design Spec

**Status:** PENDING OWNER REVIEW · 2026-09-30
**Milestone:** M2 (Phase I) of `docs/20-milestone-plan.md`
**Branch:** `sprint/m2-real-roads` off `integration/reconciled`

## 1. Problem

Roads exist only as graph data (centerlines, widths, lanes). The car drives on raw terrain; there is no visible asphalt, no markings, and spawn points are "near a road" rather than on one (the Sprint-2 rooftop/embedded-spawn incident class). M2 turns the road graph into baked, drivable, pixel-proven road geometry.

## 2. Decisions (owner-delegated, made 2026-09-30)

| # | Decision | Choice | Rationale |
|---|----------|--------|-----------|
| D1 | Ribbon strategy | **Hybrid**: baked ribbons for city core; runtime path reserved for drop-pin routes (M15) | Doctrine: baked, pixel-proven, one pipeline. Runtime spawning already carries M8 parity debt — don't grow it. |
| D2 | Terrain & collision | **Drape + own collision hull**: ribbon conforms to terrain visually; wheels read the ribbon's simplified collision, never terrain noise | Keeps Chaos tuning predictable (M4) without a terrain-carve pass. Zero runtime cost; terrain mesh untouched. |
| D3 | Intersections | **Clip & cap + junction metadata**: ribbons stop at junction boundary; flat unmarked junction polygon fills the box and carries approach-lane/signal refs for M3/M6 | A-level simplicity; metadata leaves the door open so traffic (M6) and markup (M3) don't need geometry regen. Turn-lane geometry is YAGNI. |
| D4 | Lane markings | **Material-based**: UV-mapped dashed center lines + solid edge lines in the ribbon material; no marking geometry | Zero extra triangles, trivially restylable. Crosswalks/stop bars deferred to M3 via junction metadata. |
| D5 | Elevation | **Drape to terrain** sampled every 2 m along centerline, lightly smoothed; **layer ≠ 0 (bridges/tunnels) keep absolute elevation** — never drape a bridge onto the ground below it | Terrain-following for surface streets; structurally correct for grade separations. |
| D6 | Spawn snapping | **Compiler-side**: spawns snap to nearest lane center with road heading; validator asserts on-ribbon + clearance | Fixes the incident class at the source, not at runtime. |
| D7 | Scope | **Cleveland first** (showcase + gates exist). Akron gate runs only after M1(d) regen unblocks; M2 closes with Cleveland green + Akron gate explicitly deferred-or-green | Honest scoping: Akron's pack currently fails audit for reasons outside M2's control. |

## 3. Architecture

```
citypack (compile time)                UE bake (headless import)              runtime
─────────────────────                  ──────────────────────────             ───────
road graph (nodes/edges)   ──►  road_ribbon_spec.py  ──►  ribbon_spec.json ──► ue5 script:
lanes, widths, layers,              (NEW: derives strip      per citypack          builds ProceduralMesh
junctions, per-road IDs             polygons, junction       (immutable,           per road segment +
                                    boxes, spawn snaps)      hash-pinned)          junction polygons,
                                                                                   collision hulls,
                                                                                   marking material
                                                                                        │
                                                                     validator: spawn-on-ribbon,
                                                                     ribbon↔graph 1:1 certificate,
                                                                     screenshot pack per spawn
```

**Units (each independently testable):**

1. **`tools/universal-city-compiler/road_ribbon_spec.py`** — pure function: road graph + junctions → ribbon spec JSON (strip polygons, junction boxes, snapped spawns). No UE dependency; fully unit-tested.
2. **`tools/ue5-bake-road-ribbons.py`** (headless) — reads ribbon spec, builds `UProceduralMeshComponent` strips + junction polygons, assigns asphalt/marking material, writes collision hulls into the baked map. Follows the existing headless-bake pattern from Sprint 2.
3. **Validator extension** — `tools/validate-citypack.py` + `verify-city-runtime-readiness.py`: spawn-on-ribbon assertion, ribbon↔graph 1:1 certificate (every graph edge has exactly one ribbon, by road ID).
4. **Evidence harness** — reuses the Sprint-2 diagnostics/screenshot pipeline: one screenshot per spawn, saved to `docs/evidence/m2/`.

**Runtime drop-pin ribbon path:** explicitly NOT built in M2. `RoadMeshGenerator` runtime code stays untouched; M15 will design against the same ribbon-spec schema so baked and runtime ribbons share one format.

## 4. Data flow details

- **Ribbon spec schema (v1):** `{ road_id, layer, strip: [[x,y,z]…], width_m, lanes, junction_ids: [], material: "asphalt" }` + `{ junctions: [{ id, polygon: [[x,y,z]…], approaches: [{road_id, lane_count, signal_ref}] }] }` + `{ spawns: [{ id, road_id, s_offset, pos, heading_deg }] }`. Coordinates in Frame A (Z-up, cm, X=east Y=north) — the bake does no geo math.
- **Collision hull:** simplified convex strips per segment (≤ 8 tris per 10 m), `ECC_Vehicle` responses on, overlap-only for pawns. Terrain keeps its own collision for off-road.
- **Material:** one master `M_RoadRibbon` (asphalt base + UV-scaled dash/edge lines); per-road variant only via scalar params (wear, tint). No per-road material instances in v1.
- **Smoothing:** Chaikin corner-cut, one pass, 2 m sample — kills stairstep without drifting off the graph (validator checks max deviation ≤ 30 cm).

## 5. Error handling

- Spec generation is **fail-closed**: any road with < 2 points, NaN coords, or a junction referencing a missing road → whole pack fails, no partial ribbons (matches grokbot gate culture).
- Bake logs `[raceGPS-PREFLIGHT]` ribbon counts per layer; a layer with 0 ribbons where graph edges exist = FAIL.
- Degenerate stub roads (the 20 zero-length stubs from Sprint-2 snapping) are dropped pre-spec with a count logged — not silently kept.

## 6. Testing

- **Unit (pytest):** strip width math, drape sampling incl. bridge-layer exemption, junction clip boxes, spawn snap picks nearest lane + heading, Chaikin deviation bound, schema round-trip.
- **Contract:** ribbon↔graph 1:1 certificate against the Cleveland pack; validator fails on injected missing ribbon.
- **Gate (pixel-proven):** headless Cleveland bake → screenshot per spawn shows marked asphalt under the car; evidence pack in `docs/evidence/m2/`.
- **Regression:** full suite ≥ 303 passed; existing Cleveland gates unchanged.

## 7. Gate (machine-decidable, per 20-milestone-plan)

- **Done when:** `pytest tests/ -q` ≥ 303 with new ribbon tests; `python tools/validate-citypack.py citypacks/cleveland` PASS incl. spawn-on-ribbon; evidence pack committed with screenshots at every spawn.
- **Must NOT:** modify terrain mesh or its collision; add runtime ribbon spawning; touch Akron pack (deferred to M1(d)); weaken any existing gate.
- **Anchor:** Cleveland road-graph road-ID set === ribbon road-ID set (1:1 certificate in evidence JSON).
- **Retry:** 3 failed gate attempts → stop, escalate to owner with failure diff.

## 8. Explicitly out of scope

Turn-lane geometry, crosswalk/stop-bar paint (M3), terrain carving, Akron, runtime drop-pin ribbons (M15), traffic signal logic (M6), wet-grip physics materials (M7).
