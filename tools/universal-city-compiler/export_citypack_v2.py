#!/usr/bin/env python3
"""Emit a CityPack v2 directory from a checked-in OSM fixture.

Does not fetch Overpass. XODR comes from generate_xodr (pure Python), not CARLA.
"""

from __future__ import annotations

import hashlib
import json
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from building_extractor import extract_buildings
from road_network import build_road_graph
from route_engine import _heading

CITY_ID = "steel-thread-001"
PACK_FORMAT = "racegps-citypack-v2"
DEFAULT_SEED = 42
FIXTURE_NAME = "steel_thread"

PACK_FILES = (
    "manifest.json",
    "attribution.json",
    "checksums.json",
    "roads.xodr",
    "roads.json",
    "buildings.json",
    "routes.json",
    "spawn_points.json",
)

HASHED_FILES = tuple(name for name in PACK_FILES if name != "checksums.json")

COMPILER_DIR = Path(__file__).resolve().parent
REPO_ROOT = COMPILER_DIR.parents[1]
FIXTURE_PATH = COMPILER_DIR / "fixtures" / "steel_thread.osm"
DEFAULT_PACK_DIR = REPO_ROOT / "citypacks" / CITY_ID


def _import_generate_xodr():
    xodr_dir = COMPILER_DIR.parent / "akron-semantic-compiler"
    xodr_str = str(xodr_dir)
    if xodr_str not in sys.path:
        sys.path.append(xodr_str)
    from osm_to_xodr import generate_xodr

    return generate_xodr


def _write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


def _write_json(path: Path, obj: Any) -> None:
    _write_text(path, json.dumps(obj, indent=2, ensure_ascii=False) + "\n")


def _osm_bounds(osm_path: Path) -> dict[str, float]:
    root = ET.parse(osm_path).getroot()
    bounds_el = root.find("bounds")
    if bounds_el is None:
        raise ValueError(f"OSM fixture missing <bounds>: {osm_path}")
    return {
        "west": float(bounds_el.get("minlon")),
        "south": float(bounds_el.get("minlat")),
        "east": float(bounds_el.get("maxlon")),
        "north": float(bounds_el.get("maxlat")),
    }


def _as_int_if_whole(value: float) -> int | float:
    if float(value) == int(float(value)):
        return int(value)
    return float(value)


def _roads_payload(road_graph: dict[str, Any]) -> dict[str, Any]:
    roads = []
    for road in road_graph["roads"]:
        roads.append({
            "id": str(road["id"]),
            "name": road.get("name") or "",
            "highway": road["highway"],
            "oneway": bool(road.get("one_way", road.get("oneway", False))),
            "width": road["width"],
            "lane_count": road["lane_count"],
            "max_speed": road["max_speed"],
            "points": [{"lat": p["lat"], "lon": p["lon"]} for p in road["points"]],
        })
    junctions = []
    for inter in road_graph["intersections"]:
        junctions.append({
            "id": str(inter["node_id"]),
            "lat": inter["lat"],
            "lon": inter["lon"],
            "road_ids": [str(rid) for rid in inter["road_ids"]],
        })
    return {"roads": roads, "junctions": junctions}


def _buildings_payload(buildings: list[dict[str, Any]]) -> dict[str, Any]:
    out = []
    for building in buildings:
        height = building.get("height_meters", 12)
        levels = building.get("levels")
        out.append({
            "id": str(building["id"]),
            "name": building.get("name") or "",
            "height": _as_int_if_whole(height),
            "levels": int(levels) if levels is not None else 3,
            "footprint": [{"lat": p["lat"], "lon": p["lon"]} for p in building["footprint"]],
        })
    return {"buildings": out}


def _endpoint_away_from(road: dict[str, Any], junction: dict[str, Any]) -> dict[str, float]:
    jlat, jlon = junction["lat"], junction["lon"]
    first, last = road["points"][0], road["points"][-1]
    d_first = abs(first["lat"] - jlat) + abs(first["lon"] - jlon)
    d_last = abs(last["lat"] - jlat) + abs(last["lon"] - jlon)
    chosen = first if d_first >= d_last else last
    return {"lat": chosen["lat"], "lon": chosen["lon"]}


def _steel_thread_route(roads: list[dict[str, Any]], junctions: list[dict[str, Any]]) -> dict[str, Any]:
    """One cruise_sprint along both roads through the shared junction. Not loop-validated."""
    start = _endpoint_away_from(roads[0], junctions[0])
    finish = _endpoint_away_from(roads[1], junctions[0])
    mid = {"lat": junctions[0]["lat"], "lon": junctions[0]["lon"]}
    points = [start, mid, finish]
    return {
        "route_id": f"{CITY_ID}_cruise_sprint_001",
        "name": "Steel Thread Cruise Sprint",
        "mode": "cruise_sprint",
        "start": dict(start),
        "finish": dict(finish),
        "points": [dict(p) for p in points],
        "checkpoints": [dict(mid), dict(finish)],
    }


def _spawn_points(route: dict[str, Any]) -> list[dict[str, Any]]:
    pts = route["points"]
    heading = _heading(pts[0], pts[1]) if len(pts) >= 2 else 0.0
    return [{
        "id": f"spawn_{route['route_id']}",
        "lat": route["start"]["lat"],
        "lon": route["start"]["lon"],
        "heading": round(heading, 2),
        "route_id": route["route_id"],
    }]


def _attribution() -> dict[str, Any]:
    return {
        "copyright": "© OpenStreetMap contributors",
        "license": "ODbL",
        "license_url": "https://opendatacommons.org/licenses/odbl/1-0/",
        "toolchain": [
            "universal-city-compiler",
            "akron-semantic-compiler/osm_to_xodr.generate_xodr",
        ],
        "notes": (
            "OSM input is a synthetic checked-in fixture "
            "(tools/universal-city-compiler/fixtures/steel_thread.osm), "
            "not a live Overpass pull."
        ),
    }


def canonicalize_manifest_bytes(raw: bytes) -> bytes:
    """Zero generated_at so checksums are independent of clock time."""
    payload = json.loads(raw.decode("utf-8"))
    payload["generated_at"] = ""
    text = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return text.encode("utf-8")


def file_sha256(path: Path) -> str:
    raw = path.read_bytes()
    if path.name == "manifest.json":
        raw = canonicalize_manifest_bytes(raw)
    return hashlib.sha256(raw).hexdigest()


def write_checksums(pack_dir: Path) -> dict[str, Any]:
    files = {name: file_sha256(pack_dir / name) for name in HASHED_FILES}
    payload = {"algo": "sha256", "files": files}
    _write_json(pack_dir / "checksums.json", payload)
    return payload


def export_citypack_v2(
    osm_path: Path,
    output_dir: Path,
    *,
    city_id: str = CITY_ID,
    display_name: str = "Steel Thread",
    seed: int = DEFAULT_SEED,
    generated_at: str | None = None,
) -> dict[str, Any]:
    """Compile one OSM file into a CityPack v2 directory."""
    osm_path = Path(osm_path)
    output_dir = Path(output_dir)
    if not osm_path.is_file():
        raise FileNotFoundError(f"OSM fixture not found: {osm_path}")

    bounds = _osm_bounds(osm_path)
    origin = {
        "lat": (bounds["south"] + bounds["north"]) / 2.0,
        "lon": (bounds["west"] + bounds["east"]) / 2.0,
    }

    road_graph = build_road_graph(osm_path, origin["lat"], origin["lon"])
    buildings_raw = extract_buildings(osm_path, origin["lat"], origin["lon"])
    roads_json = _roads_payload(road_graph)
    buildings_json = _buildings_payload(buildings_raw)

    if (
        len(roads_json["roads"]) != 2
        or len(roads_json["junctions"]) != 1
        or len(buildings_json["buildings"]) != 1
    ):
        raise ValueError(
            "Steel-thread pack requires roads=2, junctions=1, buildings=1; "
            f"got roads={len(roads_json['roads'])}, "
            f"junctions={len(roads_json['junctions'])}, "
            f"buildings={len(buildings_json['buildings'])}"
        )

    for road in roads_json["roads"]:
        if len(road["points"]) < 2:
            raise ValueError(f"Road {road['id']} has fewer than 2 points")
    if len(buildings_json["buildings"][0]["footprint"]) < 4:
        raise ValueError("Building footprint must have >= 4 lat/lon points")

    route = _steel_thread_route(roads_json["roads"], roads_json["junctions"])
    spawn_points = _spawn_points(route)

    generate_xodr = _import_generate_xodr()
    xodr_graph = {
        "roads": [
            {**road, "oneway": bool(road.get("one_way", road.get("oneway", False)))}
            for road in road_graph["roads"]
        ],
        "intersections": road_graph["intersections"],
    }
    xodr_xml = generate_xodr(xodr_graph)

    if generated_at is None:
        generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    files_map = {
        "opendrive": "roads.xodr",
        "roads": "roads.json",
        "buildings": "buildings.json",
        "routes": "routes.json",
        "spawn_points": "spawn_points.json",
        "attribution": "attribution.json",
        "checksums": "checksums.json",
    }

    manifest = {
        "city_id": city_id,
        "display_name": display_name,
        "format": PACK_FORMAT,
        "version": "2.0.0",
        "game_version_min": "0.1.0",
        "game_version_max": "1.0.0",
        "origin": origin,
        "bounds": bounds,
        "seed": seed,
        "generated_by": "universal-city-compiler",
        "generated_at": generated_at,
        "files": files_map,
        "statistics": {
            "roads": 2,
            "junctions": 1,
            "buildings": 1,
        },
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    _write_json(output_dir / "manifest.json", manifest)
    _write_json(output_dir / "attribution.json", _attribution())
    _write_json(output_dir / "roads.json", roads_json)
    _write_json(output_dir / "buildings.json", buildings_json)
    _write_json(output_dir / "routes.json", [route])
    _write_json(output_dir / "spawn_points.json", spawn_points)
    _write_text(output_dir / "roads.xodr", xodr_xml)
    checksums = write_checksums(output_dir)

    return {
        "success": True,
        "citypack_dir": str(output_dir),
        "manifest": manifest,
        "checksums": checksums,
    }


def compile_steel_thread(
    output_dir: Path | None = None,
    seed: int = DEFAULT_SEED,
) -> dict[str, Any]:
    """Compile the checked-in steel_thread.osm fixture to CityPack v2."""
    return export_citypack_v2(
        FIXTURE_PATH,
        Path(output_dir) if output_dir is not None else DEFAULT_PACK_DIR,
        city_id=CITY_ID,
        display_name="Steel Thread",
        seed=seed,
    )


if __name__ == "__main__":
    result = compile_steel_thread()
    print(f"Wrote CityPack v2 -> {result['citypack_dir']}")
