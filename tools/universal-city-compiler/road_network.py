#!/usr/bin/env python3
"""Generic semantic road graph builder from OSM data."""

import xml.etree.ElementTree as ET
import math
from pathlib import Path
from typing import Any

# Meters of vertical offset applied per OSM layer level so the UE5 importer
# can render bridges above / tunnels below crossing roads.
LAYER_HEIGHT_M = 5.0

_FALSY_TAG_VALUES = ("", "no", "false", "0")


def _is_truthy_tag(val: str | None) -> bool:
    """OSM tag presence check: bridge=yes/viaduct/... vs bridge=no/absent."""
    return (val or "").strip().lower() not in _FALSY_TAG_VALUES


def _parse_layer(tags: dict) -> int:
    """Resolve the effective OSM layer for a way.

    An explicit numeric `layer` tag wins. Otherwise `bridge=*` implies +1 and
    `tunnel=*` implies -1. Untagged ways default to ground level (0), which
    keeps previously compiled citypacks (e.g. Akron) byte-compatible.
    """
    raw = (tags.get("layer") or "").strip()
    if raw:
        try:
            return int(raw)
        except ValueError:
            pass  # fall through to bridge/tunnel inference
    if _is_truthy_tag(tags.get("bridge")):
        return 1
    if _is_truthy_tag(tags.get("tunnel")):
        return -1
    return 0


def build_road_graph(osm_path: Path, origin_lat: float = 0.0, origin_lon: float = 0.0) -> dict[str, Any]:
    """Parse OSM and build a semantic road graph with world-space coordinates."""
    tree = ET.parse(osm_path)
    root = tree.getroot()

    nodes: dict[str, tuple[float, float]] = {}
    ways: list[dict] = []
    relations: list[dict] = []

    for elem in root:
        if elem.tag == "node":
            nid = elem.get("id")
            if elem.get("lat") is None or elem.get("lon") is None:
                raise ValueError(f"OSM node {nid} has no coordinates; a metadata-only extract is not geometry")
            lat = float(elem.get("lat"))
            lon = float(elem.get("lon"))
            if not math.isfinite(lat) or not math.isfinite(lon) or not (-90 <= lat <= 90 and -180 <= lon <= 180):
                raise ValueError(f"OSM node {nid} has invalid coordinates")
            nodes[nid] = (lat, lon)
        elif elem.tag == "way":
            tags = {t.get("k"): t.get("v") for t in elem if t.tag == "tag"}
            nds = [n.get("ref") for n in elem if n.tag == "nd"]
            ways.append({"id": elem.get("id"), "tags": tags, "nodes": nds})
        elif elem.tag == "relation":
            tags = {t.get("k"): t.get("v") for t in elem if t.tag == "tag"}
            members = [{"type": m.get("type"), "ref": m.get("ref"), "role": m.get("role")}
                       for m in elem if m.tag == "member"]
            relations.append({"id": elem.get("id"), "tags": tags, "members": members})

    # Build roads from highway ways
    roads = []
    node_to_ways: dict[str, list[str]] = {}
    road_layers: dict[str, int] = {}
    road_endpoints = {}
    for w in sorted(ways, key=lambda w: w["id"]):
        if "highway" not in w["tags"]:
            continue

        highway = w["tags"]["highway"]
        if highway in ("footway", "cycleway", "path", "steps", "corridor", "track"):
            continue

        missing = [nid for nid in w["nodes"] if nid not in nodes]
        if missing:
            raise ValueError(f"Road {w['id']} references missing nodes: {missing[:5]}")
        points = []
        for nid in w["nodes"]:
            if nid in nodes:
                points.append({"lat": nodes[nid][0], "lon": nodes[nid][1]})

        if len(points) < 2:
            continue
        for nid in set(w["nodes"]):
            node_to_ways.setdefault(nid, []).append(w["id"])
        road_endpoints[w["id"]] = {w["nodes"][0], w["nodes"][-1]}

        oneway = w["tags"].get("oneway", "").lower()
        one_way = oneway in ("yes", "true", "1", "-1") or (
            not oneway and w["tags"].get("junction") == "roundabout")
        node_ids = list(w["nodes"])
        if oneway == "-1":
            points.reverse()
            node_ids.reverse()

        width_map = {
            "motorway": 14, "motorway_link": 10, "trunk": 12, "trunk_link": 9,
            "primary": 10, "primary_link": 9, "secondary": 9, "secondary_link": 8,
            "tertiary": 8, "tertiary_link": 7, "residential": 7,
            "unclassified": 7, "service": 5, "living_street": 6, "pedestrian": 6,
        }

        lanes = w["tags"].get("lanes", "")
        try:
            lane_count = int(lanes.split(";")[0])
        except ValueError:
            lane_count = 2 if highway in ("motorway", "trunk", "primary") else 1

        layer = _parse_layer(w["tags"])
        road_layers[w["id"]] = layer

        roads.append({
            "id": w["id"],
            "name": w["tags"].get("name", ""),
            "highway": highway,
            "points": points,
            "node_ids": node_ids,
            "width": width_map.get(highway, 7),
            "lane_count": lane_count,
            "one_way": one_way,
            "max_speed": _parse_maxspeed(w["tags"].get("maxspeed", "")),
            "surface": w["tags"].get("surface", "asphalt"),
            "layer": layer,
            "elevation_m": layer * LAYER_HEIGHT_M,
            "is_bridge": _is_truthy_tag(w["tags"].get("bridge")),
            "is_tunnel": _is_truthy_tag(w["tags"].get("tunnel")),
        })

    # Find intersections (nodes shared by 2+ roads on the SAME layer).
    # Roads at different layers (e.g. a bridge over a surface street) share a
    # node in OSM but do not physically connect, so they must not junction.
    intersections = []
    for nid, way_ids in sorted(node_to_ways.items()):
        if len(way_ids) >= 2 and nid in nodes:
            # A shared endpoint can be a deck-to-approach transition. Never
            # infer a junction merely from proximity or an interior crossing.
            if all(nid in road_endpoints[wid] for wid in way_ids):
                intersections.append({"node_id": nid, "lat": nodes[nid][0],
                    "lon": nodes[nid][1], "road_ids": sorted(way_ids),
                    "layer": min(road_layers[wid] for wid in way_ids),
                    "layer_transition": len({road_layers[wid] for wid in way_ids}) > 1})
                continue
            by_layer: dict[int, list[str]] = {}
            for wid in way_ids:
                by_layer.setdefault(road_layers.get(wid, 0), []).append(wid)
            for lyr, ids in by_layer.items():
                if len(ids) >= 2:
                    intersections.append({
                        "node_id": nid,
                        "lat": nodes[nid][0],
                        "lon": nodes[nid][1],
                        "road_ids": ids,
                        "layer": lyr,
                    })

    # Compute world bounds from all road points
    all_lats = [p["lat"] for r in roads for p in r["points"]]
    all_lons = [p["lon"] for r in roads for p in r["points"]]
    bounds = {
        "south": min(all_lats) if all_lats else -1,
        "north": max(all_lats) if all_lats else 1,
        "west": min(all_lons) if all_lons else -1,
        "east": max(all_lons) if all_lons else 1,
    }

    return {
        "roads": roads,
        "intersections": intersections,
        "bounds": bounds,
        "road_count": len(roads),
        "intersection_count": len(intersections),
        "origin": {"lat": origin_lat, "lon": origin_lon},
    }


def _parse_maxspeed(val: str) -> int:
    """Parse OSM maxspeed tag to km/h integer."""
    if not val:
        return 50
    val = val.strip().lower()
    if val == "none":
        return 250
    if "mph" in val:
        try:
            return int(float(val.replace("mph", "").strip()) * 1.60934)
        except ValueError:
            return 50
    try:
        return int(float(val))
    except ValueError:
        return 50
