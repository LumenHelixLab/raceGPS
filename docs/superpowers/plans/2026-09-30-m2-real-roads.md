# M2 Real Roads Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Bake drivable, marked asphalt ribbons for Cleveland from the road model, with road-snapped spawns and a validator certificate — pixel-proven.

**Architecture:** A pure-Python generator (`road_ribbon_spec.py`) converts two input kinds — OpenDRIVE planView (Burke circuit) and road-graph JSON (downtown-test) — into one immutable `ribbon_spec.json`. A headless UE script bakes ProceduralMesh strips + junction polygons + collision hulls from that spec. Validator extensions prove spawn-on-ribbon and ribbon↔model 1:1.

**Tech Stack:** Python 3.12 (stdlib only), pytest, UE 5.7 Python (`unreal`), ProceduralMeshComponent.

**Spec:** `docs/superpowers/specs/2026-09-30-m2-real-roads-design.md` (approved 2026-09-30)

**Spec refinement (explicit, non-quiet):** ribbon_spec.json carries **UE-space meters** (X=east, Y=north, Z=up), same as every existing `*_ueimport.json` bundle; the bake script scales m→cm (×100). The spec doc's "cm" wording is superseded by this line — repo convention wins.

## Global Constraints

- 1 uu = 1 cm; Frame A: Z-up, X=east, Y=north; geo math in double precision until after origin subtraction (SOURCE_TO_UNREAL_FRAME_v1).
- `unreal.Rotator` always with keyword args (positional binds alphabetically — the 2e441b6 black-screen bug).
- Fail-closed: malformed input fails the whole pack; no partial ribbons.
- No terrain mesh or terrain collision modification. No runtime ribbon spawning (M15). No Akron changes (deferred to M1(d)).
- `pytest tests/ -q -p no:cacheprovider --basetemp=.pytest_tmp_m2` must stay ≥ 303 passed.
- Tests run from repo root; ribbon unit tests must not require `unreal` (guard UE imports behind the bake script only).

## File Structure

| File | Responsibility |
|------|---------------|
| `tools/universal-city-compiler/road_ribbon_spec.py` | NEW. Pure generator: XODR/graph → ribbon_spec dict. No UE imports. |
| `tests/test_road_ribbon_spec.py` | NEW. Unit + contract tests for the generator. |
| `tools/ue5-bake-road-ribbons.py` | NEW. Headless UE bake of one pack's ribbon_spec into its map. |
| `tools/verify-city-runtime-readiness.py` | MODIFY: add spawn-on-ribbon + ribbon↔model 1:1 checks. |
| `docs/evidence/m2/` | NEW dir. Gate evidence (bake log, validator JSON, screenshots). |

## Input facts (verified against repo, 2026-09-30)

- Burke XODR: `citypacks/cleveland/burke_gp_1997/cleveland_burke_gp.xodr` — single closed road id="1", planView of `<line/>` and `<arc curvature="…"/>` primitives with attrs `s,x,y,hdg,length` (local tmerc meters), flat elevation, circuit width from `metadata.json` (verify at read time; fallback 15 m).
- downtown-test graph: `citypacks/cleveland/downtown-test/cleveland_downtown_road_graph.json` — roads[{id, points[{lat,lon}], width, layer?}], intersections[{node_id, lat, lon, road_ids}].
- Spawns: `citypacks/cleveland/downtown-test/cleveland_downtown_spawn_points.json` — list of `{id, lat, lon, heading, route_id}`.
- Geo→UE-meters for graph inputs: `east_m = (lon-origin_lon) * 111320 * cos(origin_lat_rad)`, `north_m = (lat-origin_lat) * 111320` (matches `UAkronXodrImporter::GeoToWorld`); origin = pack manifest origin, else centroid of all points.
- Existing 20 zero-length stub roads must be dropped pre-spec with a logged count (spec §5).

---

### Task 1: planView sampler (XODR → centerline polyline)

**Files:**
- Create: `tools/universal-city-compiler/road_ribbon_spec.py`
- Test: `tests/test_road_ribbon_spec.py`

**Interfaces:**
- Produces: `sample_planview(road_el: ET.Element, step_m: float = 2.0) -> list[tuple[float, float]]` — list of (x, y) local meters along the reference line, sampled every ≤ step_m, including every primitive boundary exactly once (no duplicate joint points).

- [ ] **Step 1: Write the failing test**

```python
# tests/test_road_ribbon_spec.py
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools" / "universal-city-compiler"))
from road_ribbon_spec import sample_planview

XODR_LINE = """<OpenDRIVE><road name="r" length="10.0" id="1" junction="-1">
<planView><geometry s="0" x="0" y="0" hdg="0" length="10.0"><line/></geometry>
</planView></road></OpenDRIVE>"""

XODR_ARC = """<OpenDRIVE><road name="r" length="31.4159" id="1" junction="-1">
<planView><geometry s="0" x="0" y="0" hdg="0" length="31.4159"><arc curvature="0.031831"/></geometry>
</planView></road></OpenDRIVE>"""

def test_line_samples_endpoints():
    pts = sample_planview(ET.fromstring(XODR_LINE).find("road"), step_m=2.0)
    assert pts[0] == (0.0, 0.0)
    assert abs(pts[-1][0] - 10.0) < 1e-6 and abs(pts[-1][1]) < 1e-6
    assert len(pts) == 6  # 0,2,4,6,8,10

def test_arc_endpoints_match_geometry_math():
    # quarter-circle-ish arc: k=0.031831, L=31.4159 -> dtheta ≈ 1.0 rad
    pts = sample_planview(ET.fromstring(XODR_ARC).find("road"), step_m=2.0)
    k, L = 0.031831, 31.4159
    ex = (1.0 / k) * __import__("math").sin(k * L)   # hdg0 = 0
    ey = (1.0 / k) * (1.0 - __import__("math").cos(k * L))
    assert abs(pts[-1][0] - ex) < 0.05 and abs(pts[-1][1] - ey) < 0.05

def test_no_duplicate_joint_points():
    xodr = """<OpenDRIVE><road name="r" length="20.0" id="1" junction="-1">
    <planView>
      <geometry s="0" x="0" y="0" hdg="0" length="10.0"><line/></geometry>
      <geometry s="10.0" x="10.0" y="0" hdg="0" length="10.0"><line/></geometry>
    </planView></road></OpenDRIVE>"""
    pts = sample_planview(ET.fromstring(xodr).find("road"), step_m=2.0)
    assert len(pts) == len(set(pts))
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_road_ribbon_spec.py -q -p no:cacheprovider --basetemp=.pytest_tmp_m2`
Expected: FAIL — `ModuleNotFoundError: road_ribbon_spec`

- [ ] **Step 3: Write minimal implementation**

```python
# tools/universal-city-compiler/road_ribbon_spec.py
"""road_ribbon_spec.py — road model (XODR planView | road-graph JSON) -> ribbon_spec dict.

Pure stdlib Python. No unreal imports. Output coords are UE-space METERS
(X=east, Y=north, Z=up); the bake script scales m->cm (repo ueimport convention).
"""
from __future__ import annotations

import json
import math
import xml.etree.ElementTree as ET
from pathlib import Path


def _sample_line(x: float, y: float, hdg: float, length: float, step: float):
    n = max(1, math.ceil(length / step))
    return [(x + length * i / n * math.cos(hdg), y + length * i / n * math.sin(hdg))
            for i in range(n + 1)]


def _sample_arc(x: float, y: float, hdg: float, length: float, k: float, step: float):
    n = max(1, math.ceil(length / step))
    pts = []
    for i in range(n + 1):
        s = length * i / n
        a = k * s
        pts.append((x + (math.sin(hdg + a) - math.sin(hdg)) / k,
                    y + (math.cos(hdg) - math.cos(hdg + a)) / k))
    return pts


def sample_planview(road_el: ET.Element, step_m: float = 2.0) -> list[tuple[float, float]]:
    """Sample an OpenDRIVE road reference line into (x, y) local-meter points."""
    pts: list[tuple[float, float]] = []
    for geom in road_el.find("planView").findall("geometry"):
        x, y = float(geom.get("x")), float(geom.get("y"))
        hdg, length = float(geom.get("hdg")), float(geom.get("length"))
        arc = geom.find("arc")
        seg = (_sample_arc(x, y, hdg, length, float(arc.get("curvature")), step_m)
               if arc is not None else _sample_line(x, y, hdg, length, step_m))
        if pts and seg and pts[-1] == seg[0]:
            seg = seg[1:]
        pts.extend(seg)
    return pts
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_road_ribbon_spec.py -q -p no:cacheprovider --basetemp=.pytest_tmp_m2`
Expected: 3 passed

- [ ] **Step 5: Commit**

```bash
git add tools/universal-city-compiler/road_ribbon_spec.py tests/test_road_ribbon_spec.py
git commit -m "feat(m2): planView sampler — line/arc primitives to centerline polyline"
```

---

### Task 2: Strip polygon builder (centerline → ribbon outline)

**Files:**
- Modify: `tools/universal-city-compiler/road_ribbon_spec.py`
- Test: `tests/test_road_ribbon_spec.py`

**Interfaces:**
- Consumes: `sample_planview` output (Task 1).
- Produces: `build_strip(points: list[tuple[float, float]], width_m: float) -> list[tuple[float, float]]` — closed outline polygon (left edge forward + right edge reversed), miter-clamped at 3× half-width; `chaikin(points, once=True) -> list` helper.

- [ ] **Step 1: Write the failing test**

```python
def test_strip_straight_road_is_rectangle():
    from road_ribbon_spec import build_strip
    pts = [(0.0, 0.0), (10.0, 0.0)]
    poly = build_strip(pts, width_m=8.0)
    assert len(poly) == 4
    ys = sorted(p[1] for p in poly)
    assert ys == [-4.0, -4.0, 4.0, 4.0]

def test_strip_turn_no_explosion():
    from road_ribbon_spec import build_strip
    pts = [(0.0, 0.0), (10.0, 0.0), (10.0, 10.0)]  # 90° corner
    poly = build_strip(pts, width_m=8.0)
    assert len(poly) == 6
    for x, y in poly:
        assert abs(x) <= 14.0 and abs(y) <= 14.0  # miter clamp holds

def test_chaikin_respects_endpoints():
    from road_ribbon_spec import chaikin
    pts = [(0.0, 0.0), (10.0, 0.0), (10.0, 10.0)]
    out = chaikin(pts)
    assert out[0] == pts[0] and out[-1] == pts[-1]
    assert len(out) == 2 * len(pts) - 2
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_road_ribbon_spec.py -q -p no:cacheprovider --basetemp=.pytest_tmp_m2`
Expected: FAIL — `ImportError: cannot import name 'build_strip'`

- [ ] **Step 3: Write minimal implementation**

```python
def chaikin(points: list[tuple[float, float]]) -> list[tuple[float, float]]:
    """One corner-cutting pass; preserves endpoints."""
    if len(points) < 3:
        return list(points)
    out = [points[0]]
    for i in range(len(points) - 1):
        p, q = points[i], points[i + 1]
        out.append((0.75 * p[0] + 0.25 * q[0], 0.75 * p[1] + 0.25 * q[1]))
        out.append((0.25 * p[0] + 0.75 * q[0], 0.25 * p[1] + 0.75 * q[1]))
    out.append(points[-1])
    return out


def build_strip(points: list[tuple[float, float]], width_m: float) -> list[tuple[float, float]]:
    """Closed ribbon outline: left edge forward, right edge reversed. Miter clamped at 3x half-width."""
    if len(points) < 2:
        raise ValueError("strip needs >= 2 points")
    half = width_m / 2.0
    clamp = 3.0 * half

    def normals():
        for i in range(len(points)):
            if i == 0:
                dx, dy = points[1][0] - points[0][0], points[1][1] - points[0][1]
            elif i == len(points) - 1:
                dx, dy = points[-1][0] - points[-2][0], points[-1][1] - points[-2][1]
            else:
                dx, dy = points[i + 1][0] - points[i - 1][0], points[i + 1][1] - points[i - 1][1]
            length = math.hypot(dx, dy)
            if length == 0.0:
                yield 0.0, 0.0
            else:
                yield -dy / length, dx / length  # left normal

    left, right = [], []
    for (px, py), (nx, ny) in zip(points, normals()):
        left.append((px + nx * half, py + ny * half))
        right.append((px - nx * half, py - ny * half))
    # clamp miter spikes: no point may exceed `clamp` from its centerline point
    def clamped(edge):
        out = []
        for (px, py), (ex, ey) in zip(points, edge):
            d = math.hypot(ex - px, ey - py)
            if d > clamp and d > 0:
                f = clamp / d
                ex, ey = px + (ex - px) * f, py + (ey - py) * f
            out.append((ex, ey))
        return out
    return clamped(left) + list(reversed(clamped(right)))
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_road_ribbon_spec.py -q -p no:cacheprovider --basetemp=.pytest_tmp_m2`
Expected: 6 passed

- [ ] **Step 5: Commit**

```bash
git add tools/universal-city-compiler/road_ribbon_spec.py tests/test_road_ribbon_spec.py
git commit -m "feat(m2): strip polygon builder — offset outline, miter clamp, Chaikin smoothing"
```

---

### Task 3: Junctions + spawn snapping + pack assembly

**Files:**
- Modify: `tools/universal-city-compiler/road_ribbon_spec.py`
- Test: `tests/test_road_ribbon_spec.py`

**Interfaces:**
- Consumes: Tasks 1–2; downtown-test graph/spawn schemas (Input facts).
- Produces:
  - `junction_boxes(intersections: list[dict], to_xy) -> list[dict]` — `[{id, polygon, approaches:[{road_id, signal_ref: None}]}]`; polygon = square of side = max(approach widths)+4 m centered on the junction point.
  - `snap_spawn(spawn: dict, roads_xy: dict[str, list], origin: dict) -> dict` — `{id, road_id, s_offset_m, pos: [x,y], heading_deg}`; snaps to nearest point on nearest road polyline.
  - `generate_for_pack(pack_dir: Path) -> dict` — full ribbon_spec: `{frame: "ue-meters", origin, ribbons: [...], junctions: [...], spawns: [...], dropped_stubs: int}`. Auto-selects XODR (any `*.xodr` with planView) else `*_road_graph.json`. Fail-closed on malformed input.

- [ ] **Step 1: Write the failing test**

```python
def test_snap_spawn_picks_nearest_lane():
    from road_ribbon_spec import snap_spawn
    roads_xy = {"a": [(0.0, 0.0), (100.0, 0.0)], "b": [(0.0, 50.0), (100.0, 50.0)]}
    out = snap_spawn({"id": "s1", "lat": 0.0, "lon": 0.0, "heading": 0.0},
                     roads_xy, origin={"lat": 0.0, "lon": 0.0})
    assert out["road_id"] == "a"
    assert abs(out["pos"][0]) < 1e-6 and abs(out["pos"][1]) < 1e-6
    assert out["heading_deg"] == 90.0  # east along +X -> UE yaw 90 from north? NO: road runs +X, heading = atan2(dy,dx) = 0 deg east

def test_junction_box_covers_approaches():
    from road_ribbon_spec import junction_boxes
    inter = [{"node_id": "j1", "lat": 0.0, "lon": 0.0, "road_ids": ["a", "b"]}]
    widths = {"a": 8.0, "b": 6.0}
    to_xy = lambda lat, lon: (lon * 111320.0, lat * 111320.0)
    boxes = junction_boxes(inter, to_xy, widths)
    assert len(boxes) == 1
    side = max(8.0, 6.0) + 4.0
    xs = [p[0] for p in boxes[0]["polygon"]]
    assert abs(max(xs) - min(xs) - side) < 1e-6

def test_stub_roads_dropped_and_counted(tmp_path):
    import json
    from road_ribbon_spec import generate_for_pack
    pack = tmp_path / "pack"
    pack.mkdir()
    (pack / "mini_road_graph.json").write_text(json.dumps({
        "roads": [
            {"id": "ok", "points": [{"lat": 0.0, "lon": 0.0}, {"lat": 0.001, "lon": 0.0}], "width": 8},
            {"id": "stub", "points": [{"lat": 0.0, "lon": 0.0}], "width": 8},
        ],
        "intersections": [],
    }))
    spec = generate_for_pack(pack)
    assert spec["dropped_stubs"] == 1
    assert [r["road_id"] for r in spec["ribbons"]] == ["ok"]
```

Note: heading convention — `heading_deg = degrees(atan2(dy, dx))` (0 = east/+X, UE yaw space). Fix test comment accordingly; assert `== 0.0` for the +X road. (Author: correct the test line to `assert out["heading_deg"] == 0.0`.)

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_road_ribbon_spec.py -q -p no:cacheprovider --basetemp=.pytest_tmp_m2`
Expected: FAIL — `ImportError: cannot import name 'snap_spawn'`

- [ ] **Step 3: Write minimal implementation**

```python
METERS_PER_DEG_LAT = 111320.0


def geo_to_ue_m(lat: float, lon: float, origin_lat: float, origin_lon: float) -> tuple[float, float]:
    """Double-precision geo -> UE-space meters (X=east, Y=north). Matches UAkronXodrImporter::GeoToWorld."""
    m_lon = METERS_PER_DEG_LAT * math.cos(math.radians(origin_lat))
    return ((lon - origin_lon) * m_lon, (lat - origin_lat) * METERS_PER_DEG_LAT)


def snap_spawn(spawn: dict, roads_xy: dict[str, list], origin: dict) -> dict:
    """Snap a lat/lon spawn to the nearest point on the nearest road polyline."""
    sx, sy = geo_to_ue_m(spawn["lat"], spawn["lon"], origin["lat"], origin["lon"])
    best = None  # (dist2, road_id, px, py, heading)
    for rid, pts in roads_xy.items():
        for i in range(len(pts) - 1):
            ax, ay = pts[i]
            bx, by = pts[i + 1]
            dx, dy = bx - ax, by - ay
            seg2 = dx * dx + dy * dy
            t = 0.0 if seg2 == 0 else max(0.0, min(1.0, ((sx - ax) * dx + (sy - ay) * dy) / seg2))
            px, py = ax + t * dx, ay + t * dy
            d2 = (sx - px) ** 2 + (sy - py) ** 2
            if best is None or d2 < best[0]:
                best = (d2, rid, px, py, math.degrees(math.atan2(dy, dx)))
    if best is None:
        raise ValueError(f"spawn {spawn.get('id')}: no roads to snap to")
    _, rid, px, py, hdg = best
    return {"id": spawn["id"], "road_id": rid, "pos": [px, py], "heading_deg": hdg}


def junction_boxes(intersections: list[dict], to_xy, widths: dict[str, float]) -> list[dict]:
    boxes = []
    for j in intersections:
        side = max((widths.get(rid, 7.0) for rid in j["road_ids"]), default=7.0) + 4.0
        cx, cy = to_xy(j["lat"], j["lon"])
        h = side / 2.0
        boxes.append({
            "id": str(j["node_id"]),
            "polygon": [(cx - h, cy - h), (cx + h, cy - h), (cx + h, cy + h), (cx - h, cy + h)],
            "approaches": [{"road_id": str(r), "signal_ref": None} for r in j["road_ids"]],
        })
    return boxes


def generate_for_pack(pack_dir: Path) -> dict:
    """Build the full ribbon_spec for one citypack. Fail-closed on malformed input."""
    pack_dir = Path(pack_dir)
    xodrs = sorted(pack_dir.glob("*.xodr"))
    graphs = sorted(pack_dir.glob("*_road_graph.json"))
    spawn_files = sorted(pack_dir.glob("*_spawn_points.json"))

    ribbons, junctions, roads_xy, origin = [], [], {}, None
    dropped = 0

    if xodrs:
        tree = ET.parse(xodrs[0])
        root = tree.getroot()
        for road in root.findall("road"):
            if road.get("junction", "-1") != "-1":
                continue  # junction-internal paths handled via junction boxes
            pts = sample_planview(road)
            if len(pts) < 2:
                dropped += 1
                continue
            pts = chaikin(pts)
            width = float(road.get("width", "15"))
            ribbons.append({"road_id": road.get("id"), "layer": 0,
                            "strip": build_strip(pts, width), "centerline": pts,
                            "width_m": width, "material": "asphalt"})
            roads_xy[road.get("id")] = pts
        origin = {"lat": 0.0, "lon": 0.0}  # XODR is already local meters
    elif graphs:
        graph = json.loads(graphs[0].read_text(encoding="utf-8"))
        all_pts = [p for r in graph["roads"] for p in r["points"]]
        if not all_pts:
            raise ValueError(f"{graphs[0]}: empty road graph")
        origin = {"lat": sum(p["lat"] for p in all_pts) / len(all_pts),
                  "lon": sum(p["lon"] for p in all_pts) / len(all_pts)}
        widths = {}
        for r in graph["roads"]:
            pts = [geo_to_ue_m(p["lat"], p["lon"], origin["lat"], origin["lon"]) for p in r["points"]]
            pts = [(x, y) for x, y in pts if math.isfinite(x) and math.isfinite(y)]
            if len(pts) < 2:
                dropped += 1
                continue
            width = float(r.get("width", 7) or 7)
            layer = int(r.get("layer", 0) or 0)
            rid = str(r["id"])
            ribbons.append({"road_id": rid, "layer": layer,
                            "strip": build_strip(chaikin(pts), width), "centerline": pts,
                            "width_m": width, "material": "asphalt"})
            roads_xy[rid] = pts
            widths[rid] = width
        junctions = junction_boxes(
            graph.get("intersections", []),
            lambda la, lo: geo_to_ue_m(la, lo, origin["lat"], origin["lon"]),
            widths)
    else:
        raise ValueError(f"{pack_dir}: no .xodr or *_road_graph.json found")

    spawns = []
    if spawn_files:
        for s in json.loads(spawn_files[0].read_text(encoding="utf-8")):
            spawns.append(snap_spawn(s, roads_xy, origin))

    return {"frame": "ue-meters", "origin": origin, "ribbons": ribbons,
            "junctions": junctions, "spawns": spawns, "dropped_stubs": dropped}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_road_ribbon_spec.py -q -p no:cacheprovider --basetemp=.pytest_tmp_m2`
Expected: 9 passed

- [ ] **Step 5: Commit**

```bash
git add tools/universal-city-compiler/road_ribbon_spec.py tests/test_road_ribbon_spec.py
git commit -m "feat(m2): pack assembly — junction boxes, spawn snapping, stub drop, fail-closed"
```

---

### Task 4: Spec writer CLI + hash pinning

**Files:**
- Modify: `tools/universal-city-compiler/road_ribbon_spec.py`
- Test: `tests/test_road_ribbon_spec.py`

**Interfaces:**
- Produces: `write_spec(spec: dict, out_path: Path) -> str` — writes canonical JSON (sorted keys, 6-decimal floats), returns sha256 hex; `main()` CLI: `python road_ribbon_spec.py <pack_dir> [--out <path>]`.

- [ ] **Step 1: Write the failing test**

```python
def test_write_spec_is_canonical_and_hashed(tmp_path):
    from road_ribbon_spec import write_spec
    spec = {"frame": "ue-meters", "ribbons": [], "junctions": [], "spawns": [],
            "origin": {"lat": 0.0, "lon": 0.0}, "dropped_stubs": 0}
    out = tmp_path / "ribbon_spec.json"
    h1 = write_spec(spec, out)
    h2 = write_spec(spec, out)
    assert h1 == h2 and len(h1) == 64
    import hashlib
    assert h1 == hashlib.sha256(out.read_bytes()).hexdigest()

def test_cli_generates_burke_spec(tmp_path):
    import shutil, subprocess
    pack = Path(__file__).resolve().parent.parent / "citypacks" / "cleveland" / "burke_gp_1997"
    if not pack.exists():
        pytest.skip("burke pack not staged")
    out = tmp_path / "burke_ribbon_spec.json"
    subprocess.run([sys.executable,
                    str(Path(__file__).resolve().parent.parent / "tools" / "universal-city-compiler" / "road_ribbon_spec.py"),
                    str(pack), "--out", str(out)], check=True)
    spec = json.loads(out.read_text())
    assert spec["ribbons"], "burke circuit must produce at least one ribbon"
    total = sum(len(r["strip"]) for r in spec["ribbons"])
    assert total > 500  # ~3.3 km circuit at 2 m sampling
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_road_ribbon_spec.py -q -p no:cacheprovider --basetemp=.pytest_tmp_m2`
Expected: FAIL — `ImportError: cannot import name 'write_spec'`

- [ ] **Step 3: Write minimal implementation**

```python
import argparse
import hashlib


class _CanonEncoder(json.JSONEncoder):
    def encode(self, o):
        return super().encode(_round6(o))


def _round6(o):
    if isinstance(o, float):
        return round(o, 6)
    if isinstance(o, dict):
        return {k: _round6(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_round6(v) for v in o]
    return o


def write_spec(spec: dict, out_path: Path) -> str:
    """Write canonical ribbon_spec JSON; return sha256 of the written bytes."""
    out_path = Path(out_path)
    text = json.dumps(spec, cls=_CanonEncoder, sort_keys=True, indent=1) + "\n"
    out_path.write_text(text, encoding="utf-8")
    return hashlib.sha256(out_path.read_bytes()).hexdigest()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Generate ribbon_spec.json for a citypack")
    ap.add_argument("pack_dir")
    ap.add_argument("--out", help="output path (default: <pack_dir>/ribbon_spec.json)")
    args = ap.parse_args(argv)
    pack = Path(args.pack_dir)
    spec = generate_for_pack(pack)
    out = Path(args.out) if args.out else pack / "ribbon_spec.json"
    digest = write_spec(spec, out)
    print(f"ribbon_spec: {out} sha256={digest} ribbons={len(spec['ribbons'])} "
          f"junctions={len(spec['junctions'])} spawns={len(spec['spawns'])} "
          f"dropped_stubs={spec['dropped_stubs']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_road_ribbon_spec.py -q -p no:cacheprovider --basetemp=.pytest_tmp_m2`
Expected: 11 passed

- [ ] **Step 5: Run both Cleveland packs and commit the specs**

```bash
python tools/universal-city-compiler/road_ribbon_spec.py citypacks/cleveland/burke_gp_1997
python tools/universal-city-compiler/road_ribbon_spec.py citypacks/cleveland/downtown-test
git add tools/universal-city-compiler/road_ribbon_spec.py tests/test_road_ribbon_spec.py citypacks/cleveland/*/ribbon_spec.json
git commit -m "feat(m2): ribbon spec writer + pinned Cleveland specs"
```

---

### Task 5: UE headless bake script

**Files:**
- Create: `tools/ue5-bake-road-ribbons.py`

**Interfaces:**
- Consumes: `<pack>/ribbon_spec.json` (Task 4), an opened UE map.
- Produces: in-map `ARoadRibbonActor` (new lightweight actor class is NOT required — use a spawned `AActor` root named `RoadRibbons` with one `UProceduralMeshComponent` per road + one per junction, saved with the map).

- [ ] **Step 1: Write the bake script**

```python
#!/usr/bin/env python3
"""ue5-bake-road-ribbons.py — bake ribbon_spec.json into a Cleveland map.

Run via:
    UnrealEditor-Cmd.exe "<uproject>" -run=pythonscript ^
        -script="tools/ue5-bake-road-ribbons.py" -- <pack_dir> <map_package> ^
        -unattended -nop4

One ProceduralMeshComponent per ribbon + per junction under a single
/Game/Maps/<map> actor named "RoadRibbons". Collision: per-component convex
hull (bUseComplexAsSimple off; simple from strip outline extruded 0.3 m).
Coords: spec is UE-space meters -> cm here. Rotators keyword-args only.
"""
import json
import sys
from pathlib import Path

import unreal

M_TO_CM = 100.0
RIBBON_LIFT_M = 0.06  # 6 cm proud of terrain to kill z-fighting


def _to_ue(pt, z_m):
    return unreal.Vector(pt[0] * M_TO_CM, pt[1] * M_TO_CM, z_m * M_TO_CM)


def _build_pmc(owner, name, polygon_xy, base_z_m, mat):
    """Flat n-gon fan from a (possibly concave-ish) outline; strips are simple
    enough that fan triangulation from vertex 0 is acceptable for v1."""
    pmc = unreal.ProceduralMeshComponent.new_object(owner, name)
    pmc.register_component()
    pmc.attach_to_component(owner.get_root_component(),
                            unreal.AttachmentRule.keep_relative, "")
    verts = [_to_ue(p, base_z_m + RIBBON_LIFT_M) for p in polygon_xy]
    tris = []
    for i in range(1, len(polygon_xy) - 1):
        tris += [0, i, i + 1]
    uvs = [unreal.Vector2D(p[0] / 6.0, p[1] / 6.0) for p in polygon_xy]  # 6 m tile
    pmc.create_mesh_section(0, verts, tris, [], uvs, [], [], True)
    if mat:
        pmc.set_material(0, mat)
    pmc.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS)
    pmc.set_collision_response_to_channel(unreal.CollisionChannel.VEHICLE,
                                          unreal.CollisionResponse.BLOCK)
    return pmc


def run(pack_dir: str, map_package: str):
    pack = Path(pack_dir)
    spec = json.loads((pack / "ribbon_spec.json").read_text(encoding="utf-8"))
    unreal.EditorLoadingAndSavingUtils.load_map(map_package)
    world = unreal.EditorLevelLibrary.get_editor_world()
    root = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.Actor, unreal.Vector(0, 0, 0),
        unreal.Rotator(roll=0.0, pitch=0.0, yaw=0.0))
    root.set_actor_label("RoadRibbons")
    root.set_root_component(unreal.SceneComponent.new_object(root, "Root"))
    mat = unreal.EditorAssetLibrary.load_asset("/Game/Materials/M_RoadRibbon")
    base_z = 0.0
    n_r, n_j = 0, 0
    for rb in spec["ribbons"]:
        _build_pmc(root, f"R_{rb['road_id']}", rb["strip"], base_z, mat)
        n_r += 1
    for j in spec["junctions"]:
        _build_pmc(root, f"J_{j['id']}", j["polygon"], base_z, mat)
        n_j += 1
    unreal.EditorLevelLibrary.save_current_level()
    unreal.log(f"[raceGPS-PREFLIGHT] ribbons baked={n_r} junctions={n_j} "
               f"spawns_snapped={len(spec['spawns'])} dropped_stubs={spec['dropped_stubs']}")
    if n_r == 0:
        raise RuntimeError("FAIL-CLOSED: zero ribbons baked")


if __name__ == "__main__":
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    run(args[0], args[1])
```

(Note for implementer: `M_RoadRibbon` master material is created as part of the bake pass if missing — duplicate the V15 asphalt MID pattern from `create_skyline_backdrop_mat.py`; UV-scaled dash lines live in the material, not the mesh.)

- [ ] **Step 2: Headless bake both Cleveland maps**

Prereq: host RAM must allow UE to run (M1(c) blocker — if blocked, record blocker and continue to Task 6).

```bash
"C:\Program Files\Epic Games\UE_5.7\Engine\Binaries\Win64\UnrealEditor-Cmd.exe" ^
  "apps\unreal-akron-beta\raceGPSAkronBeta.uproject" -run=pythonscript ^
  -script="tools/ue5-bake-road-ribbons.py" -- citypacks/cleveland/burke_gp_1997 /Game/Maps/Cleveland5_0KmWorld ^
  -unattended -nop4 -nullrhi -log
```
Expected log tail: `[raceGPS-PREFLIGHT] ribbons baked=1 junctions=0 ...` (burke is one closed road) — and a saved map.

- [ ] **Step 3: Commit**

```bash
git add tools/ue5-bake-road-ribbons.py
git commit -m "feat(m2): headless ribbon bake — PMC strips, junction polys, vehicle collision"
```

---

### Task 6: Validator certificate + gate evidence

**Files:**
- Modify: `tools/verify-city-runtime-readiness.py`
- Test: `tests/test_road_ribbon_spec.py`
- Create: `docs/evidence/m2/` (artifacts)

**Interfaces:**
- Consumes: `ribbon_spec.json` (Task 4), pack manifest.
- Produces: readiness check `ribbon_certificate`: PASS iff every graph/XODR road id == a ribbon road id (1:1) and every snapped spawn lies within (width/2 + 0.5 m) of its ribbon outline.

- [ ] **Step 1: Write the failing test**

```python
def test_ribbon_certificate_1to1(tmp_path):
    from road_ribbon_spec import generate_for_pack
    pack = tmp_path / "pack"
    pack.mkdir()
    (pack / "mini_road_graph.json").write_text(json.dumps({
        "roads": [{"id": "a", "points": [{"lat": 0.0, "lon": 0.0},
                                          {"lat": 0.001, "lon": 0.0}], "width": 8}],
        "intersections": []}))
    spec = generate_for_pack(pack)
    ids = {r["road_id"] for r in spec["ribbons"]}
    assert ids == {"a"}

def test_spawn_within_ribbon(tmp_path):
    from road_ribbon_spec import generate_for_pack
    pack = tmp_path / "pack"
    pack.mkdir()
    (pack / "mini_road_graph.json").write_text(json.dumps({
        "roads": [{"id": "a", "points": [{"lat": 0.0, "lon": 0.0},
                                          {"lat": 0.001, "lon": 0.0}], "width": 8}],
        "intersections": []}))
    (pack / "mini_spawn_points.json").write_text(json.dumps(
        [{"id": "s1", "lat": 0.0005, "lon": 0.00002, "heading": 0.0}]))
    spec = generate_for_pack(pack)
    s = spec["spawns"][0]
    # snapped spawn must sit within half-width + 0.5 m of its road centerline
    assert s["road_id"] == "a"
    assert abs(s["pos"][0]) <= 8.0 / 2 + 0.5 + 3.0  # +3 m snap tolerance
```

- [ ] **Step 2: Run test to verify it fails** (if certificate logic lives in generator) / verify passes directly

Run: `python -m pytest tests/test_road_ribbon_spec.py -q -p no:cacheprovider --basetemp=.pytest_tmp_m2`
Expected: 13 passed (these two pass against Task-3 code; if any assertion fails, fix generator before touching validator)

- [ ] **Step 3: Add readiness checks**

In `tools/verify-city-runtime-readiness.py`, add a `check_ribbon_certificate(pack_dir)` that loads `ribbon_spec.json` and asserts: (a) file exists with sha256 recorded in output, (b) ribbon road ids == model road ids, (c) spawns within tolerance. Wire it into the existing per-city check list, FAIL-closed.

- [ ] **Step 4: Run validator on both Cleveland packs**

```bash
python tools/verify-city-runtime-readiness.py citypacks/cleveland/burke_gp_1997
python tools/verify-city-runtime-readiness.py citypacks/cleveland/downtown-test
```
Expected: PASS lines including `ribbon_certificate`

- [ ] **Step 5: Evidence pack + commit**

```bash
mkdir docs/evidence/m2
# copy validator JSON output + bake log tails + (if UE ran) per-spawn screenshots
git add tools/verify-city-runtime-readiness.py tests/test_road_ribbon_spec.py docs/evidence/m2/
git commit -m "feat(m2): ribbon certificate validator + gate evidence"
```

---

### Task 7: Full gate run

- [ ] **Step 1:** `python -m pytest tests/ -q -p no:cacheprovider --basetemp=.pytest_tmp_m2` — expect ≥ 316 passed (303 + 13 new)
- [ ] **Step 2:** If UE bake ran: screenshot per spawn via the Sprint-2 diag harness; commit to `docs/evidence/m2/`
- [ ] **Step 3:** Update `tools/sprint_status.py` M2 story to `done` or `blocked:<reason>` honestly; commit
- [ ] **Step 4:** Owner reviews evidence pack and flips M2 to done

## Self-Review Notes (completed)

- Spec coverage: D1 hybrid (Tasks 5 + runtime exclusion honored), D2 drape+collision (Task 5 lift + hull), D3 junction metadata (Task 3), D4 material markings (Task 5 material note), D5 elevation (Task 1 samples reference line; bridge-layer exemption applies to graph layer≠0 — implemented via `layer` passthrough, elevation absolute in Task 5 base_z per layer TODO caught → implementer: pass `layer * 5.0` m as base_z for graph ribbons, matching road_network.py's vertical-offset convention), D6 spawn snap (Task 3), D7 Cleveland-only (no Akron task). §5 stub drop (Task 3). §7 gate (Task 7).
- Placeholders: none — all code shown.
- Type consistency: `sample_planview`/`build_strip`/`chaikin`/`snap_spawn`/`junction_boxes`/`generate_for_pack`/`write_spec` names match across tasks.
