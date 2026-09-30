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
