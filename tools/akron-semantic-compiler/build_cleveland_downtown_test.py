#!/usr/bin/env python3
"""Build citypacks/cleveland/downtown-test from OSM (no CARLA, no StreetMap).

Usage (from repo root):
  py -3 tools/akron-semantic-compiler/build_cleveland_downtown_test.py
"""
from __future__ import annotations

import json
import math
import sys
import urllib.parse  # noqa: F401  # required by fetch_osm
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from fetch_osm import fetch_osm_for_bounds
from osm_to_xodr import generate_xodr
from road_graph import build_road_graph

BOUNDS = {
    "west": -81.700,
    "south": 41.495,
    "east": -81.685,
    "north": 41.505,
}
ORIGIN = {
    "lat": (BOUNDS["south"] + BOUNDS["north"]) / 2.0,
    "lon": (BOUNDS["west"] + BOUNDS["east"]) / 2.0,
}
OUT = REPO / "citypacks" / "cleveland" / "downtown-test"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    osm_path = OUT / "cleveland_downtown.osm"
    graph_path = OUT / "cleveland_downtown_road_graph.json"
    xodr_path = OUT / "cleveland_downtown.xodr"

    print(f"[1/4] Fetching OSM {BOUNDS} ...")
    osm_xml = fetch_osm_for_bounds(**BOUNDS)
    osm_path.write_text(osm_xml, encoding="utf-8")
    print(f"      {osm_path.name}: {osm_path.stat().st_size} bytes")

    print("[2/4] Building road graph...")
    road_graph = build_road_graph(osm_path)
    road_graph["origin"] = ORIGIN
    road_graph["bounds"] = BOUNDS
    graph_path.write_text(json.dumps(road_graph, indent=2), encoding="utf-8")
    print(f"      roads={road_graph.get('road_count')} intersections={road_graph.get('intersection_count')}")

    print("[3/4] Generating OpenDRIVE...")
    generate_xodr(road_graph, xodr_path)
    print(f"      {xodr_path.name}: {xodr_path.stat().st_size} bytes")

    spawns = []
    routes = []
    if road_graph.get("roads"):
        r0 = road_graph["roads"][0]
        pts = r0["points"]
        mid = pts[len(pts) // 2]
        i = max(0, len(pts) // 2 - 1)
        j = min(len(pts) - 1, i + 1)
        dlat = pts[j]["lat"] - pts[i]["lat"]
        dlon = pts[j]["lon"] - pts[i]["lon"]
        heading = (math.degrees(math.atan2(dlon, dlat)) + 360.0) % 360.0
        spawns.append({
            "id": "spawn_cleveland_downtown_001",
            "lat": mid["lat"],
            "lon": mid["lon"],
            "heading": round(heading, 1),
            "route_id": "cleveland_downtown_probe_001",
        })
        routes.append({
            "route_id": "cleveland_downtown_probe_001",
            "display_name": "Downtown Probe",
            "distance_meters": 0,
            "num_checkpoints": 0,
            "start": {"lat": mid["lat"], "lon": mid["lon"]},
            "finish": {"lat": mid["lat"], "lon": mid["lon"]},
            "waypoints": [{"lat": p["lat"], "lon": p["lon"]} for p in pts[: min(8, len(pts))]],
            "checkpoints": [],
        })

    (OUT / "cleveland_downtown_spawn_points.json").write_text(json.dumps(spawns, indent=2) + "\n", encoding="utf-8")
    (OUT / "cleveland_downtown_routes.json").write_text(json.dumps(routes, indent=2) + "\n", encoding="utf-8")
    (OUT / "cleveland_downtown_gameplay_layer.json").write_text(json.dumps({
        "speed_zones": [
            {"type": "highway", "highways": ["motorway", "trunk"], "speed_kmh": 90},
            {"type": "arterial", "highways": ["primary", "secondary"], "speed_kmh": 65},
            {"type": "local", "highways": ["tertiary", "residential", "unclassified"], "speed_kmh": 45},
            {"type": "service", "highways": ["service"], "speed_kmh": 25},
        ],
        "pickup_zones": [],
        "objective_zones": [],
        "challenge_zones": [],
    }, indent=2) + "\n", encoding="utf-8")
    (OUT / "cleveland_downtown_pois.json").write_text("[]\n", encoding="utf-8")
    (OUT / "cleveland_downtown_buildings.json").write_text(json.dumps({"buildings": []}, indent=2) + "\n", encoding="utf-8")

    manifest = {
        "city_id": "cleveland-downtown-test",
        "display_name": "Cleveland Downtown (test)",
        "version": "0.1.0",
        "game_version_min": "0.1.0",
        "game_version_max": "0.2.0",
        "origin": ORIGIN,
        "bounds": BOUNDS,
        "opendrive_file": "cleveland_downtown.xodr",
        "routes": "cleveland_downtown_routes.json",
        "road_graph": "cleveland_downtown_road_graph.json",
        "spawn_points": "cleveland_downtown_spawn_points.json",
        "pois": "cleveland_downtown_pois.json",
        "buildings": "cleveland_downtown_buildings.json",
        "gameplay_layer": "cleveland_downtown_gameplay_layer.json",
        "route_count": len(routes),
        "poi_count": 0,
        "spawn_point_count": len(spawns),
        "building_count": 0,
        "pack_dir": "citypacks/cleveland/downtown-test",
        "offline": True,
        "carla_required": False,
        "cesium_required": False,
        "streetmap_required": False,
        "pipeline": "tools/akron-semantic-compiler (fetch_osm + road_graph + osm_to_xodr)",
        "notes": "Downtown OSM smoke pack for RoadMeshGenerator / AkronXodrImporter. No StreetMap plugin.",
    }
    (OUT / "cleveland_downtown_semantic_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"[4/4] Wrote pack under {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
