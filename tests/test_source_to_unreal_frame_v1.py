"""G2: SOURCE_TO_UNREAL_FRAME_v1 transform proofs (1cm / 0.1deg)."""
from __future__ import annotations

import importlib.util
import math
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


genspec = _load("generate_level_spec_g2", ROOT / "tools" / "generate-level-spec.py")
impspec = _load("ue5_import_level_spec_g2", ROOT / "tools" / "ue5-import-level-spec.py")

ORIGIN_LAT = 41.51722
ORIGIN_LON = -81.68306
TOL_CM = 1.0
TOL_DEG = 0.1


def test_frame_constants():
    assert genspec.FRAME_ID == "SOURCE_TO_UNREAL_FRAME_v1"
    assert genspec.METERS_TO_UU == 100.0
    assert genspec.METERS_PER_DEG_LAT == 111320.0


def test_100m_east_line_within_1cm():
    # 100 m east ~= dlon such that easting = 100 m
    mplon = genspec.meters_per_degree_lon(ORIGIN_LAT)
    dlon = 100.0 / mplon
    a = genspec.geo_to_world(ORIGIN_LAT, ORIGIN_LON, ORIGIN_LAT, ORIGIN_LON)
    b = genspec.geo_to_world(ORIGIN_LAT, ORIGIN_LON + dlon, ORIGIN_LAT, ORIGIN_LON)
    dist = math.hypot(b["x"] - a["x"], b["y"] - a["y"], b["z"] - a["z"])
    assert abs(dist - 10000.0) <= TOL_CM  # 100 m = 10000 cm
    assert abs(b["y"] - a["y"]) <= TOL_CM
    assert b["x"] > a["x"]


def test_100m_north_line_within_1cm():
    mplat = genspec.meters_per_degree_lat()
    dlat = 100.0 / mplat
    a = genspec.geo_to_world(ORIGIN_LAT, ORIGIN_LON, ORIGIN_LAT, ORIGIN_LON)
    b = genspec.geo_to_world(ORIGIN_LAT + dlat, ORIGIN_LON, ORIGIN_LAT, ORIGIN_LON)
    dist = math.hypot(b["x"] - a["x"], b["y"] - a["y"], b["z"] - a["z"])
    assert abs(dist - 10000.0) <= TOL_CM
    assert abs(b["x"] - a["x"]) <= TOL_CM
    assert b["y"] > a["y"]


def test_7m_road_width_half_in_cm():
    width_m = 7.0
    half_uu = width_m * genspec.METERS_TO_UU * 0.5
    assert abs(half_uu - 350.0) <= TOL_CM


def test_compass_to_ue_yaw():
    cases = [(0.0, 90.0), (90.0, 0.0), (180.0, -90.0), (270.0, -180.0), (45.0, 45.0)]
    for compass, expected in cases:
        got = genspec.heading_to_rotation(compass)["yaw"]
        # normalize diff
        diff = (got - expected + 180.0) % 360.0 - 180.0
        assert abs(diff) <= TOL_DEG, (compass, got, expected)


def test_legacy_frame_b_bake_bridge():
    # Frame B meters: x=east, y=up, z=-north
    loc_b = {"x": 10.0, "y": 2.0, "z": -5.0}  # 10m east, 2m up, 5m north (z=-5)
    # Without unreal, _spec_to_ue returns dict for legacy
    out = impspec._spec_to_ue(loc_b, frame=None)
    assert abs(out["x"] - 1000.0) <= TOL_CM
    assert abs(out["y"] - 500.0) <= TOL_CM  # -z * 100
    assert abs(out["z"] - 200.0) <= TOL_CM  # y * 100


def test_frame_v1_passthrough_no_double_scale():
    loc = {"x": 10000.0, "y": 350.0, "z": 50.0}
    out = impspec._spec_to_ue(loc, frame=impspec.FRAME_V1)
    assert out["x"] == 10000.0
    assert out["y"] == 350.0
    assert out["z"] == 50.0


def test_no_silent_frame_b_reinterpretation_of_v1():
    # If someone wrongly applies B->A to v1 coords, easting blows up / axes flip
    loc = {"x": 10000.0, "y": 0.0, "z": 0.0}
    wrong = impspec._spec_to_ue(loc, frame=None)
    right = impspec._spec_to_ue(loc, frame=impspec.FRAME_V1)
    assert wrong["x"] != right["x"] or wrong["y"] != right["y"]
    assert right["x"] == 10000.0 and right["y"] == 0.0
