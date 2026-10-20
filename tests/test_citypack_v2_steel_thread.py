#!/usr/bin/env python3
"""CityPack v2 steel-thread pack: layout, schema, statistics, checksums, hash-repeat."""

from __future__ import annotations

import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
COMPILER_DIR = PROJECT_ROOT / "tools" / "universal-city-compiler"
PACK_DIR = PROJECT_ROOT / "citypacks" / "steel-thread-001"
SCHEMA_PATH = PROJECT_ROOT / "docs" / "contracts" / "citypack-v2.manifest.schema.json"
MANIFEST_REQUIRED = [
    "city_id",
    "display_name",
    "format",
    "version",
    "game_version_min",
    "game_version_max",
    "origin",
    "bounds",
    "seed",
    "generated_by",
    "generated_at",
    "files",
    "statistics",
]
PACK_FILES = [
    "manifest.json",
    "attribution.json",
    "checksums.json",
    "roads.xodr",
    "roads.json",
    "buildings.json",
    "routes.json",
    "spawn_points.json",
]

sys.path.insert(0, str(COMPILER_DIR))

from export_citypack_v2 import HASHED_FILES, compile_steel_thread, file_sha256


@pytest.fixture(scope="module")
def pack_dir() -> Path:
    result = compile_steel_thread()
    assert result["success"]
    return Path(result["citypack_dir"])


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_pack_exists(pack_dir: Path):
    assert pack_dir == PACK_DIR
    assert pack_dir.is_dir()
    for name in PACK_FILES:
        assert (pack_dir / name).is_file(), f"missing {name}"


def test_manifest_format_and_schema_keys(pack_dir: Path):
    manifest = _load(pack_dir / "manifest.json")
    assert manifest["format"] == "racegps-citypack-v2"
    for key in MANIFEST_REQUIRED:
        assert key in manifest, f"missing manifest key {key}"
    schema = _load(SCHEMA_PATH)
    assert schema["required"] == MANIFEST_REQUIRED
    jsonschema = pytest.importorskip("jsonschema")
    jsonschema.validate(manifest, schema)


def test_statistics_2_1_1(pack_dir: Path):
    stats = _load(pack_dir / "manifest.json")["statistics"]
    assert stats["roads"] == 2
    assert stats["junctions"] == 1
    assert stats["buildings"] == 1


def test_roads_json_two_roads_one_junction(pack_dir: Path):
    payload = _load(pack_dir / "roads.json")
    assert len(payload["roads"]) == 2
    assert len(payload["junctions"]) == 1
    road_ids = []
    for road in payload["roads"]:
        assert len(road["points"]) >= 2
        for point in road["points"]:
            assert "lat" in point and "lon" in point
            assert "x" not in point and "y" not in point
        road_ids.append(str(road["id"]))
    junction = payload["junctions"][0]
    assert "lat" in junction and "lon" in junction
    assert set(junction["road_ids"]) == set(road_ids)


def test_buildings_json_one_wgs84_footprint(pack_dir: Path):
    payload = _load(pack_dir / "buildings.json")
    assert len(payload["buildings"]) == 1
    building = payload["buildings"][0]
    assert len(building["footprint"]) >= 4
    for point in building["footprint"]:
        assert "lat" in point and "lon" in point
        assert "x" not in point and "y" not in point


def test_routes_one_cruise_sprint(pack_dir: Path):
    routes = _load(pack_dir / "routes.json")
    assert isinstance(routes, list)
    assert len(routes) == 1
    route = routes[0]
    assert route["mode"] == "cruise_sprint"
    assert "route_id" in route and "name" in route
    assert "start" in route and "finish" in route
    assert len(route["points"]) >= 2
    assert len(route["checkpoints"]) >= 2
    for point in route["checkpoints"]:
        assert "lat" in point and "lon" in point


def test_spawn_points_at_least_one(pack_dir: Path):
    spawns = _load(pack_dir / "spawn_points.json")
    assert isinstance(spawns, list)
    assert len(spawns) >= 1
    route = _load(pack_dir / "routes.json")[0]
    spawn = spawns[0]
    for key in ("id", "lat", "lon", "heading", "route_id"):
        assert key in spawn
    assert spawn["route_id"] == route["route_id"]


def test_roads_xodr_opendrive(pack_dir: Path):
    root = ET.parse(pack_dir / "roads.xodr").getroot()
    assert root.tag == "OpenDRIVE"
    roads = root.findall("road")
    assert len(roads) >= 1


def test_checksums_cover_and_match(pack_dir: Path):
    checksums = _load(pack_dir / "checksums.json")
    assert checksums["algo"] == "sha256"
    assert set(checksums["files"]) == set(HASHED_FILES)
    assert "checksums.json" not in checksums["files"]
    for name, digest in checksums["files"].items():
        assert digest == digest.lower()
        assert len(digest) == 64
        assert file_sha256(pack_dir / name) == digest


def test_hash_repeat_same_checksums(pack_dir: Path):
    first = _load(pack_dir / "checksums.json")
    compile_steel_thread()
    second = _load(pack_dir / "checksums.json")
    assert first == second
