"""Overpass JSON → rgpack v1 geometry (Workshop writer; Race never calls this).

Accepts Overpass *JSON* elements (ways + nodes) or a small offline fixture with
the same shape. Emits streets / checkpoints / spawn / environment payloads and
a Manifest ready for ``save_pack`` + ``validate_pack_dir``.

Sibling compilers (cite, do not rewrite):
  - tools/akron-semantic-compiler/fetch_osm.py
  - tools/universal-city-compiler/fetch_overpass.py
  - tools/validate-citypack.py
Citypack XODR → rgpack remains a post-unlock adapter; this module is OSM JSON only.
"""
from __future__ import annotations

import json
import math
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from .schema import (
    Certification,
    Defaults,
    Frame,
    Manifest,
    RgpackValidationError,
    Source,
)

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
USER_AGENT = "raceGPS-rgpack-overpass-export/1.0 (Workshop; offline-first)"

# Highway classes kept for a raceable centerline (exclude footways/paths).
HIGHWAY_KEEP = frozenset(
    {
        "motorway",
        "trunk",
        "primary",
        "secondary",
        "tertiary",
        "unclassified",
        "residential",
        "service",
        "living_street",
        "motorway_link",
        "trunk_link",
        "primary_link",
        "secondary_link",
        "tertiary_link",
    }
)


def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371000.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlmb / 2) ** 2
    return 2 * r * math.asin(min(1.0, math.sqrt(a)))


def bearing_deg(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dlmb = math.radians(lon2 - lon1)
    y = math.sin(dlmb) * math.cos(p2)
    x = math.cos(p1) * math.sin(p2) - math.sin(p1) * math.cos(p2) * math.cos(dlmb)
    return (math.degrees(math.atan2(y, x)) + 360.0) % 360.0


def load_overpass_json(path: Path) -> dict[str, Any]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or "elements" not in raw:
        raise RgpackValidationError("Overpass JSON must be an object with 'elements'")
    if not isinstance(raw["elements"], list):
        raise RgpackValidationError("Overpass JSON 'elements' must be a list")
    return raw


def fetch_overpass_bbox(
    west: float,
    south: float,
    east: float,
    north: float,
    *,
    timeout_s: int = 45,
) -> dict[str, Any]:
    """Tiny live Overpass JSON pull. Fail-closed on network/HTTP errors."""
    query = f"""
[out:json][timeout:{timeout_s}];
(
  way["highway"~"^(motorway|trunk|primary|secondary|tertiary|unclassified|residential|service|living_street)$"]({south},{west},{north},{east});
  node(w);
);
out body;
"""
    data = urllib.parse.urlencode({"data": query}).encode("utf-8")
    req = urllib.request.Request(OVERPASS_URL, data=data, method="POST")
    req.add_header("User-Agent", USER_AGENT)
    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            body = resp.read().decode("utf-8")
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError) as exc:
        raise RgpackValidationError(f"Overpass fetch FAIL-CLOSED: {exc}") from exc
    raw = json.loads(body)
    if not isinstance(raw, dict) or "elements" not in raw:
        raise RgpackValidationError("Overpass response missing elements")
    return raw


def _index_nodes(elements: list[dict[str, Any]]) -> dict[int, tuple[float, float]]:
    nodes: dict[int, tuple[float, float]] = {}
    for el in elements:
        if el.get("type") != "node":
            continue
        nid = el.get("id")
        lat, lon = el.get("lat"), el.get("lon")
        if nid is None or lat is None or lon is None:
            continue
        nodes[int(nid)] = (float(lat), float(lon))
    return nodes


def _highway_ways(
    elements: list[dict[str, Any]], nodes: dict[int, tuple[float, float]]
) -> list[list[tuple[float, float]]]:
    ways: list[list[tuple[float, float]]] = []
    for el in elements:
        if el.get("type") != "way":
            continue
        tags = el.get("tags") or {}
        hwy = tags.get("highway")
        if hwy not in HIGHWAY_KEEP:
            continue
        pts: list[tuple[float, float]] = []
        for nid in el.get("nodes") or []:
            pt = nodes.get(int(nid))
            if pt is not None:
                pts.append(pt)
        if len(pts) >= 2:
            ways.append(pts)
    return ways


def _polyline_length_m(pts: list[tuple[float, float]]) -> float:
    total = 0.0
    for i in range(1, len(pts)):
        total += haversine_m(pts[i - 1][0], pts[i - 1][1], pts[i][0], pts[i][1])
    return total


def _stitch_primary_centerline(
    ways: list[list[tuple[float, float]]],
) -> list[tuple[float, float]]:
    """Pick longest way, then greedily append connecting ways (endpoint proximity)."""
    if not ways:
        raise RgpackValidationError("no highway ways with resolvable nodes")
    remaining = sorted(ways, key=_polyline_length_m, reverse=True)
    center = list(remaining.pop(0))
    # Cap stitching iterations for tiny proofs.
    for _ in range(min(32, len(remaining))):
        if not remaining:
            break
        end = center[-1]
        best_i = None
        best_d = 25.0  # meters — only stitch nearby ends
        reverse = False
        for i, w in enumerate(remaining):
            d0 = haversine_m(end[0], end[1], w[0][0], w[0][1])
            d1 = haversine_m(end[0], end[1], w[-1][0], w[-1][1])
            if d0 < best_d:
                best_d, best_i, reverse = d0, i, False
            if d1 < best_d:
                best_d, best_i, reverse = d1, i, True
        if best_i is None:
            break
        w = remaining.pop(best_i)
        if reverse:
            w = list(reversed(w))
        # Skip duplicate join vertex if nearly coincident.
        if haversine_m(center[-1][0], center[-1][1], w[0][0], w[0][1]) < 1.0:
            center.extend(w[1:])
        else:
            center.extend(w)
    return center


def _dedupe_near(pts: list[tuple[float, float]], min_m: float = 2.0) -> list[tuple[float, float]]:
    if not pts:
        return pts
    out = [pts[0]]
    for p in pts[1:]:
        if haversine_m(out[-1][0], out[-1][1], p[0], p[1]) >= min_m:
            out.append(p)
    if len(out) == 1 and len(pts) > 1:
        out.append(pts[-1])
    return out


def build_centerline(elements: list[dict[str, Any]]) -> list[dict[str, float]]:
    nodes = _index_nodes(elements)
    ways = _highway_ways(elements, nodes)
    raw = _stitch_primary_centerline(ways)
    pts = _dedupe_near(raw)
    if len(pts) < 2:
        raise RgpackValidationError("centerline needs at least 2 points")
    centerline: list[dict[str, float]] = []
    s = 0.0
    for i, (lat, lon) in enumerate(pts):
        if i > 0:
            s += haversine_m(pts[i - 1][0], pts[i - 1][1], lat, lon)
        centerline.append({"lat": lat, "lon": lon, "s": round(s, 3)})
    return centerline


def _sample_at_s(
    centerline: list[dict[str, float]], target_s: float
) -> tuple[float, float, float]:
    """Return (lat, lon, heading_deg) at distance target_s along centerline."""
    if target_s <= centerline[0]["s"]:
        a, b = centerline[0], centerline[min(1, len(centerline) - 1)]
        return a["lat"], a["lon"], bearing_deg(a["lat"], a["lon"], b["lat"], b["lon"])
    for i in range(1, len(centerline)):
        a, b = centerline[i - 1], centerline[i]
        if b["s"] >= target_s:
            span = max(1e-6, b["s"] - a["s"])
            t = (target_s - a["s"]) / span
            lat = a["lat"] + t * (b["lat"] - a["lat"])
            lon = a["lon"] + t * (b["lon"] - a["lon"])
            return lat, lon, bearing_deg(a["lat"], a["lon"], b["lat"], b["lon"])
    a, b = centerline[-2], centerline[-1]
    return b["lat"], b["lon"], bearing_deg(a["lat"], a["lon"], b["lat"], b["lon"])


def build_geometry_files(
    centerline: list[dict[str, float]],
    *,
    track_id: str,
    width_m: float = 8.0,
    gate_width_m: float = 10.0,
    environment_preset: str = "Sunset",
) -> dict[str, Any]:
    total_s = centerline[-1]["s"]
    # Start/Finish + mid + near-end (or 2 gates if very short).
    gate_targets = [0.0]
    if total_s >= 80.0:
        gate_targets.extend([total_s * 0.5, max(0.0, total_s - 5.0)])
    elif total_s >= 30.0:
        gate_targets.append(total_s * 0.5)
    else:
        gate_targets.append(total_s)

    gates = []
    for idx, gs in enumerate(gate_targets):
        lat, lon, _hdg = _sample_at_s(centerline, gs)
        name = "Start/Finish" if idx == 0 else f"CP{idx}"
        gates.append(
            {
                "index": idx,
                "name": name,
                "lat": round(lat, 7),
                "lon": round(lon, 7),
                "s": round(gs, 3),
                "width_m": gate_width_m,
            }
        )

    plat, plon, phd = _sample_at_s(centerline, 0.0)
    # Small grid offset ~3 m west of spawn using crude lon delta.
    dlon = 3.0 / (111320.0 * max(0.2, math.cos(math.radians(plat))))
    spawn = {
        "player": {
            "lat": round(plat, 7),
            "lon": round(plon, 7),
            "heading_deg": round(phd, 2),
        },
        "grid": [
            {
                "slot": 0,
                "lat": round(plat, 7),
                "lon": round(plon, 7),
                "heading_deg": round(phd, 2),
            },
            {
                "slot": 1,
                "lat": round(plat, 7),
                "lon": round(plon - dlon, 7),
                "heading_deg": round(phd, 2),
            },
        ],
    }
    streets = {"centerline": centerline, "width_m": width_m}
    checkpoints = {"track_id": track_id, "lap_count": 1, "gates": gates}
    environment = {
        "default_preset": environment_preset,
        "presets": ["Sunset", "Twilight", "Midnight"],
    }
    return {
        "streets": streets,
        "checkpoints": checkpoints,
        "spawn": spawn,
        "environment": environment,
    }


def _bbox_from_centerline(centerline: list[dict[str, float]]) -> list[float]:
    lats = [p["lat"] for p in centerline]
    lons = [p["lon"] for p in centerline]
    pad = 0.0005
    return [
        round(min(lons) - pad, 6),
        round(min(lats) - pad, 6),
        round(max(lons) + pad, 6),
        round(max(lats) + pad, 6),
    ]


def build_manifest(
    *,
    pack_id: str,
    display_name: str,
    centerline: list[dict[str, float]],
    source_type: str = "osm",
    attribution: str = "© OpenStreetMap contributors",
    retrieved_at: Optional[str] = None,
    bbox: Optional[list[float]] = None,
    certification_notes: str = "Workshop Overpass→rgpack export; provisional.",
    environment_preset: str = "Sunset",
) -> Manifest:
    origin = centerline[0]
    return Manifest(
        schema_version=1,
        pack_id=pack_id,
        display_name=display_name,
        frame=Frame(
            units_per_meter=100,
            z_up=True,
            x_east=True,
            y_north=True,
            origin_lat=float(origin["lat"]),
            origin_lon=float(origin["lon"]),
            origin_alt_m=0.0,
        ),
        source=Source(
            type=source_type,  # type: ignore[arg-type]
            attribution=attribution,
            retrieved_at=retrieved_at
            or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            bbox=bbox or _bbox_from_centerline(centerline),
        ),
        certification=Certification(status="provisional", notes=certification_notes),
        content_hash="sha256:pending",
        defaults=Defaults(environment_preset=environment_preset, loadout_id=None),  # type: ignore[arg-type]
    )


def export_overpass_to_pack(
    overpass: dict[str, Any],
    out_dir: Path,
    *,
    pack_id: str,
    display_name: str,
    attribution: str = "© OpenStreetMap contributors",
    retrieved_at: Optional[str] = None,
    bbox: Optional[list[float]] = None,
    certification_notes: str = "Workshop Overpass→rgpack export; provisional.",
    environment_preset: str = "Sunset",
) -> Manifest:
    """Convert Overpass JSON → pack dir; save + validate fail-closed. Returns Manifest."""
    from .io import save_pack, validate_pack_dir

    elements = overpass["elements"]
    centerline = build_centerline(elements)
    files = build_geometry_files(
        centerline, track_id=pack_id, environment_preset=environment_preset
    )
    manifest = build_manifest(
        pack_id=pack_id,
        display_name=display_name,
        centerline=centerline,
        attribution=attribution,
        retrieved_at=retrieved_at,
        bbox=bbox,
        certification_notes=certification_notes,
        environment_preset=environment_preset,
    )
    out_dir = Path(out_dir)
    save_pack(out_dir, manifest, files)
    validate_pack_dir(out_dir)
    from .io import load_pack

    return load_pack(out_dir)
