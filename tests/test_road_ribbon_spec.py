# tests/test_road_ribbon_spec.py
import math
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

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
    # k=0.031831, L=31.4159 -> dtheta ~= 1.0 rad
    pts = sample_planview(ET.fromstring(XODR_ARC).find("road"), step_m=2.0)
    k, L = 0.031831, 31.4159
    ex = (1.0 / k) * math.sin(k * L)   # hdg0 = 0
    ey = (1.0 / k) * (1.0 - math.cos(k * L))
    assert abs(pts[-1][0] - ex) < 0.05 and abs(pts[-1][1] - ey) < 0.05


def test_no_duplicate_joint_points():
    xodr = """<OpenDRIVE><road name="r" length="20.0" id="1" junction="-1">
    <planView>
      <geometry s="0" x="0" y="0" hdg="0" length="10.0"><line/></geometry>
      <geometry s="10.0" x="10.0" y="0" hdg="0" length="10.0"><line/></geometry>
    </planView></road></OpenDRIVE>"""
    pts = sample_planview(ET.fromstring(xodr).find("road"), step_m=2.0)
    assert len(pts) == len(set(pts))


def test_strip_straight_road_is_rectangle():
    from road_ribbon_spec import build_strip
    pts = [(0.0, 0.0), (10.0, 0.0)]
    poly = build_strip(pts, width_m=8.0)
    assert len(poly) == 4
    ys = sorted(p[1] for p in poly)
    assert ys == [-4.0, -4.0, 4.0, 4.0]


def test_strip_turn_no_explosion():
    from road_ribbon_spec import build_strip
    pts = [(0.0, 0.0), (10.0, 0.0), (10.0, 10.0)]  # 90 deg corner
    poly = build_strip(pts, width_m=8.0)
    assert len(poly) == 6
    for x, y in poly:
        assert abs(x) <= 14.0 and abs(y) <= 14.0  # miter clamp holds


def test_chaikin_respects_endpoints():
    from road_ribbon_spec import chaikin
    pts = [(0.0, 0.0), (10.0, 0.0), (10.0, 10.0)]
    out = chaikin(pts)
    assert out[0] == pts[0] and out[-1] == pts[-1]
    assert len(out) == 2 * len(pts)  # 2 per segment + 2 endpoints


def test_snap_spawn_picks_nearest_lane():
    from road_ribbon_spec import snap_spawn
    roads_xy = {"a": [(0.0, 0.0), (100.0, 0.0)], "b": [(0.0, 50.0), (100.0, 50.0)]}
    out = snap_spawn({"id": "s1", "lat": 0.0, "lon": 0.0, "heading": 0.0},
                     roads_xy, origin={"lat": 0.0, "lon": 0.0})
    assert out["road_id"] == "a"
    assert abs(out["pos"][0]) < 1e-6 and abs(out["pos"][1]) < 1e-6
    assert out["heading_deg"] == 0.0  # road runs +X (east) -> atan2(0, +) = 0


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


def test_mixed_pack_emits_graph_junctions_in_xodr_frame(tmp_path):
    """XODR supplies ribbons; a sibling *_road_graph.json still supplies
    junction boxes, projected into the XODR local frame via its eqc geoReference."""
    import json
    from road_ribbon_spec import generate_for_pack
    pack = tmp_path / "pack"
    pack.mkdir()
    (pack / "mini.xodr").write_text(
        '<OpenDRIVE><header revMajor="1" revMinor="4" name="t" version="1">'
        '<geoReference>+proj=eqc +lat_0=41.5 +lat_ts=41.5 +lon_0=-81.6925 '
        '+R=6378166.0 +x_0=0 +y_0=0 +units=m +no_defs</geoReference>'
        '</header>'
        '<road name="r" length="100.0" id="a" junction="-1"><planView>'
        '<geometry s="0" x="0" y="0" hdg="0" length="100.0"><line /></geometry>'
        '</planView></road></OpenDRIVE>')
    (pack / "mini_road_graph.json").write_text(json.dumps({
        "roads": [{"id": "a", "points": [{"lat": 41.5, "lon": -81.6925},
                                          {"lat": 41.5, "lon": -81.69}], "width": 8}],
        "intersections": [{"node_id": "j1", "lat": 41.5, "lon": -81.6925,
                           "road_ids": ["a"]}],
    }))
    spec = generate_for_pack(pack)
    assert len(spec["junctions"]) == 1
    xs = [p[0] for p in spec["junctions"][0]["polygon"]]
    ys = [p[1] for p in spec["junctions"][0]["polygon"]]
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    assert abs(cx) < 0.01 and abs(cy) < 0.01  # lat_0/lon_0 projects to the origin


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
    import json
    import shutil
    import subprocess
    from road_ribbon_spec import main
    pack = Path(__file__).resolve().parent.parent / "citypacks" / "cleveland" / "burke_gp_1997"
    if not pack.exists():
        pytest.skip("burke pack not staged")
    out = tmp_path / "burke_ribbon_spec.json"
    assert main([str(pack), "--out", str(out)]) == 0
    spec = json.loads(out.read_text())
    assert spec["ribbons"], "burke circuit must produce at least one ribbon"
    total = sum(len(r["strip"]) for r in spec["ribbons"])
    assert total > 500  # ~3.3 km circuit at 2 m sampling


def test_ribbon_certificate_1to1(tmp_path):
    import json
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
    import json
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
