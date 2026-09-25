#!/usr/bin/env python3
"""Generic route generator with multiple race modes and smart waypoint selection."""

import random
import math
from typing import Any


def _haversine(a: dict, b: dict) -> float:
    """Approximate distance in meters between two lat/lon points."""
    R = 6371000
    dlat = math.radians(b["lat"] - a["lat"])
    dlon = math.radians(b["lon"] - a["lon"])
    lat1 = math.radians(a["lat"])
    lat2 = math.radians(b["lat"])
    x = math.sin(dlon) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
    return math.atan2(math.sqrt(x*x + y*y), math.sin(lat1)*math.sin(lat2) + math.cos(lat1)*math.cos(lat2)*math.cos(dlon)) * R


def _route_length(points: list[dict]) -> float:
    return sum(_haversine(points[i], points[i+1]) for i in range(len(points)-1))


def _centroid(roads: list[dict]) -> dict:
    """Compute approximate city center from road points."""
    all_pts = [p for r in roads for p in r["points"]]
    if not all_pts:
        return {"lat": 0, "lon": 0}
    return {"lat": sum(p["lat"] for p in all_pts) / len(all_pts),
            "lon": sum(p["lon"] for p in all_pts) / len(all_pts)}


def directed_graph(road_graph: dict) -> tuple[dict, dict]:
    """Build source-segment edges; join roads only at declared intersections.

    Legacy graphs without node IDs require an exact point match at the declared
    junction. No rounding, nearest-neighbour snapping or invented connectors.
    """
    parent, points, road_nodes = {}, {}, {}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def join(a, b):
        a, b = find(a), find(b)
        parent[max(a, b)] = min(a, b)

    roads = sorted(road_graph.get("roads", []), key=lambda r: str(r["id"]))
    lookup = {}
    for road in roads:
        rid = str(road["id"])
        if rid in lookup:
            raise ValueError(f"Duplicate road ID: {rid}")
        lookup[rid] = road
        ids = road.get("node_ids")
        if ids is not None and len(ids) != len(road["points"]):
            raise ValueError(f"Node/point count mismatch: {rid}")
        keys = []
        for i, point in enumerate(road["points"]):
            token = str(ids[i]) if ids is not None else repr((point["lat"], point["lon"]))
            key = (rid, token)
            if key in points and points[key] != point:
                raise ValueError(f"Conflicting coordinates for node: {key}")
            parent[key] = key
            points[key] = point
            keys.append(key)
        road_nodes[rid] = keys
    for junction in road_graph.get("intersections", []):
        matches = []
        for rid in sorted(set(map(str, junction.get("road_ids", [])))):
            road = lookup.get(rid)
            if road is None:
                raise ValueError(f"Intersection references missing road: {rid}")
            for i, point in enumerate(road["points"]):
                ids = road.get("node_ids")
                match = (str(ids[i]) == str(junction["node_id"])) if ids is not None else (
                    point["lat"] == junction["lat"] and point["lon"] == junction["lon"])
                if match:
                    matches.append(road_nodes[rid][i])
        if matches:
            if any(points[k] != points[matches[0]] for k in matches):
                raise ValueError("Intersection has conflicting source coordinates")
            for key in matches[1:]:
                join(matches[0], key)
    adjacency = {}
    for road in roads:
        rid = str(road["id"])
        keys = road_nodes[rid]
        for i, (a, b) in enumerate(zip(keys, keys[1:])):
            a, b = find(a), find(b)
            if a == b:
                continue
            edge = {"road_id": rid, "segment_index": i, "direction": 1}
            adjacency.setdefault(a, []).append((b, edge))
            if not road.get("one_way", road.get("oneway", False)):
                adjacency.setdefault(b, []).append((a, dict(edge, direction=-1)))
    return adjacency, {find(k): p for k, p in points.items()}


def generate_routes(road_graph: dict[str, Any], city_id: str, mode: str = "all", count: int = 3, seed: int = 42) -> list[dict]:
    """Bounded deterministic search. An unsuccessful search emits no route.

    A connectivity certificate is not proof of geometric clearance, handling,
    historical accuracy or online competitive equity. Those require other gates.
    """
    minimum = {"cruise_sprint": 800, "time_trial": 1500, "circuit": 1000, "drift_run": 400}
    if mode != "all" and mode not in minimum:
        raise ValueError(f"Unknown route mode: {mode}")
    if count < 0:
        raise ValueError("Route count must be nonnegative")
    adjacency, points = directed_graph(road_graph)
    starts = sorted(adjacency)
    if not starts:
        return []
    rng = random.Random(seed)
    result, signatures = [], set()
    modes = list(minimum) if mode == "all" else [mode]
    for route_idx in range(count):
        target_mode = modes[route_idx % len(modes)]
        for attempt in range(64):
            start = rng.choice(starts)
            current, visited, vertices, edges, distance = start, {start}, [start], [], 0.0
            for step in range(256):
                candidates = [(n, e) for n, e in adjacency.get(current, [])
                              if n not in visited or (target_mode == "circuit" and n == start and len(edges) >= 2)]
                if not candidates:
                    break
                nxt, edge = rng.choice(candidates)
                distance += _haversine(points[current], points[nxt])
                edges.append(edge)
                vertices.append(nxt)
                visited.add(nxt)
                current = nxt
                if nxt == start or (target_mode != "circuit" and distance >= minimum[target_mode]):
                    break
            closed = len(edges) >= 3 and current == start
            if distance < minimum[target_mode] or (target_mode == "circuit" and not closed):
                continue
            signature = (target_mode, tuple((e["road_id"], e["segment_index"], e["direction"]) for e in edges))
            if signature in signatures:
                continue
            signatures.add(signature)
            route_points = [points[k] for k in vertices]
            result.append({
                "route_id": f"{city_id}_{target_mode}_{route_idx + 1:03d}", "mode": target_mode,
                "name": f"{city_id.replace('_', ' ').title()} {target_mode.replace('_', ' ').title()} {route_idx + 1}",
                "difficulty": "unrated", "distance_meters": round(distance),
                "start": route_points[0], "finish": route_points[-1], "points": route_points,
                "segments": edges, "closed": closed, "connectivity": "explicit_graph_v1",
                "competition_certified": False,
            })
            break
    return result


def place_checkpoints(route: dict, spacing_meters: float = 300.0, gate_radius: float = 18.0) -> list[dict]:
    """Place checkpoint gates along a route at regular intervals."""
    points = route.get("points", [])
    if len(points) < 2:
        return []

    checkpoints = []
    accumulated = 0.0
    cp_idx = 1

    for i in range(1, len(points)):
        a, b = points[i-1], points[i]
        seg_len = _haversine(a, b)
        accumulated += seg_len

        if accumulated >= spacing_meters:
            # Place checkpoint at point b
            heading = _heading(a, b)
            checkpoints.append({
                "id": f"{route['route_id']}_cp_{cp_idx:03d}",
                "lat": b["lat"],
                "lon": b["lon"],
                "heading": round(heading, 2),
                "radius_meters": gate_radius,
                "type": "gate",
                "distance_from_start_m": round(sum(_haversine(points[j], points[j+1]) for j in range(i)), 1),
            })
            accumulated = 0.0
            cp_idx += 1

    return checkpoints


def _heading(a: dict, b: dict) -> float:
    """Compute compass heading from a to b in degrees."""
    dlon = math.radians(b["lon"] - a["lon"])
    lat1 = math.radians(a["lat"])
    lat2 = math.radians(b["lat"])
    x = math.sin(dlon) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
    heading = math.degrees(math.atan2(x, y))
    return (heading + 360) % 360
