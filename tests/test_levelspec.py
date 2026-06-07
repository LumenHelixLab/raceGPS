#!/usr/bin/env python3
"""
Pytest validation for level spec generation.

Usage:
    python -m pytest tests/test_levelspec.py -v
"""

import json
import math
import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CITYPACK_DIR = PROJECT_ROOT / "citypacks" / "akron-oh-beta-001"
GENERATED_DIR = PROJECT_ROOT / "generated"
SPEC_PATH = GENERATED_DIR / "AkronWorld_LevelSpec.json"


def meters_per_degree_lon(origin_lat: float) -> float:
    return 111320.0 * math.cos(math.radians(origin_lat))


def meters_per_degree_lat() -> float:
    return 110540.0


def geo_to_world(lat: float, lon: float, origin_lat: float, origin_lon: float) -> dict:
    mpdlon = meters_per_degree_lon(origin_lat)
    mpdlat = meters_per_degree_lat()
    x = (lon - origin_lon) * mpdlon
    z = -(lat - origin_lat) * mpdlat
    return {"x": x, "y": 0.0, "z": z}


@pytest.fixture(scope="module")
def level_spec():
    """Ensure generate-level-spec.py has run and return the parsed spec."""
    result = subprocess.run(
        [sys.executable, str(PROJECT_ROOT / "tools" / "generate-level-spec.py")],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"generate-level-spec.py failed:\n{result.stderr}"
    assert SPEC_PATH.exists(), f"Level spec not generated at {SPEC_PATH}"
    return json.loads(SPEC_PATH.read_text())


@pytest.fixture(scope="module")
def manifest():
    path = CITYPACK_DIR / "akron_semantic_manifest.json"
    assert path.exists()
    return json.loads(path.read_text())


@pytest.fixture(scope="module")
def routes():
    path = CITYPACK_DIR / "akron_routes.json"
    assert path.exists()
    return json.loads(path.read_text())


class TestLevelSpecSchema:
    def test_top_level_fields(self, level_spec):
        required = [
            "level_name",
            "city_id",
            "origin",
            "world_bounds",
            "spawn_points",
            "routes",
            "lighting",
            "day_night_cycle",
            "traffic_spawn_volumes",
            "poi_markers",
            "metadata",
        ]
        for field in required:
            assert field in level_spec, f"Missing required field: {field}"

    def test_origin_matches_manifest(self, level_spec, manifest):
        assert level_spec["origin"]["lat"] == pytest.approx(manifest["origin"]["lat"])
        assert level_spec["origin"]["lon"] == pytest.approx(manifest["origin"]["lon"])

    def test_spawn_points_count(self, level_spec, manifest):
        spawns = level_spec["spawn_points"]
        assert isinstance(spawns, list)
        assert len(spawns) == manifest.get("spawn_point_count", 0)

    def test_routes_count(self, level_spec, manifest):
        routes = level_spec["routes"]
        assert isinstance(routes, list)
        assert len(routes) == manifest.get("route_count", 0)

    def test_route_fields(self, level_spec):
        for route in level_spec["routes"]:
            assert "route_id" in route
            assert "spline_points" in route
            assert "checkpoints" in route
            assert isinstance(route["spline_points"], list)
            assert len(route["spline_points"]) >= 2

    def test_lighting_fields(self, level_spec):
        lighting = level_spec["lighting"]
        assert "time_of_day" in lighting
        assert "sun_rotation" in lighting
        assert "exposure" in lighting

    def test_day_night_cycle_fields(self, level_spec):
        dnc = level_spec["day_night_cycle"]
        assert "enabled" in dnc
        assert "cycle_duration_minutes" in dnc

    def test_metadata(self, level_spec):
        meta = level_spec["metadata"]
        assert meta.get("generated_by") == "generate-level-spec.py"
        assert "spec_version" in meta


class TestSpawnPointsInBounds:
    def test_all_spawns_inside_world_bounds(self, level_spec):
        bounds = level_spec["world_bounds"]
        for sp in level_spec["spawn_points"]:
            loc = sp["location"]
            assert bounds["min_x"] <= loc["x"] <= bounds["max_x"]
            assert bounds["min_y"] <= loc["y"] <= bounds["max_y"]
            assert bounds["min_z"] <= loc["z"] <= bounds["max_z"]

    def test_all_spawns_inside_manifest_bounds(self, level_spec, manifest):
        """Verify spawn points are within the city's lat/lon bounding box."""
        bounds = manifest["bounds"]
        origin_lat = manifest["origin"]["lat"]
        origin_lon = manifest["origin"]["lon"]
        mpdlon = meters_per_degree_lon(origin_lat)
        mpdlat = meters_per_degree_lat()
        for sp in level_spec["spawn_points"]:
            loc = sp["location"]
            lon = loc["x"] / mpdlon + origin_lon
            lat = -loc["z"] / mpdlat + origin_lat
            assert bounds["west"] <= lon <= bounds["east"]
            assert bounds["south"] <= lat <= bounds["north"]


class TestRouteDistances:
    def test_route_distances_match_manifest(self, level_spec, routes):
        for spec_route, src_route in zip(level_spec["routes"], routes):
            spec_dist = spec_route["distance_meters"]
            src_dist = src_route.get("distance_meters", 0)
            assert spec_dist == src_dist, (
                f"Route {spec_route['route_id']} distance mismatch: "
                f"spec={spec_dist}, source={src_dist}"
            )

    def test_spline_path_length_approximates_distance(self, level_spec):
        for route in level_spec["routes"]:
            pts = route["spline_points"]
            if len(pts) < 2:
                continue
            total = 0.0
            for i in range(len(pts) - 1):
                a, b = pts[i], pts[i + 1]
                dx = b["x"] - a["x"]
                dz = b["z"] - a["z"]
                total += math.hypot(dx, dz)
            stated = route["distance_meters"]
            variance = abs(total - stated) / max(stated, 1)
            assert variance <= 0.15, (
                f"Route {route['route_id']} spline length {total:.0f}m "
                f"differs from stated {stated}m by {variance * 100:.1f}%"
            )

    def test_checkpoints_near_spline(self, level_spec):
        for route in level_spec["routes"]:
            pts = route["spline_points"]
            if not pts:
                continue
            for cp in route.get("checkpoints", []):
                loc = cp["location"]
                min_dist = min(
                    math.hypot(loc["x"] - p["x"], loc["z"] - p["z"])
                    for p in pts
                )
                assert min_dist <= 100, (
                    f"Checkpoint {cp['id']} is {min_dist:.0f}m from nearest spline point"
                )

    def test_spawn_point_matches_route_start(self, level_spec):
        for sp in level_spec["spawn_points"]:
            route_id = sp.get("route_id", "")
            matching = [r for r in level_spec["routes"] if r["route_id"] == route_id]
            assert matching, f"No route found for spawn point {sp['id']}"
            route = matching[0]
            start = route["spline_points"][0]
            loc = sp["location"]
            dist = math.hypot(loc["x"] - start["x"], loc["z"] - start["z"])
            assert dist <= 1.0, (
                f"Spawn point {sp['id']} is {dist:.1f}m from route {route_id} start"
            )
