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
