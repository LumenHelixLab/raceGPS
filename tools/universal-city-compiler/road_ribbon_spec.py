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
