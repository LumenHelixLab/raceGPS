#!/usr/bin/env python3
"""
Generate AkronWorld_LevelSpec.json from semantic manifest, routes, spawn points, and POIs.
Produces a UE5-ready level description with world-space coordinates.

Usage:
    python tools/generate-level-spec.py
"""

import json
import math
from geo_frame import geo_to_unreal, compass_to_yaw, WORLD_FRAME, METERS_PER_DEGREE
from pathlib import Path


def meters_per_degree_lon(origin_lat: float) -> float:
    return METERS_PER_DEGREE * math.cos(math.radians(origin_lat))


def meters_per_degree_lat() -> float:
    return METERS_PER_DEGREE


def geo_to_world(lat: float, lon: float, origin_lat: float, origin_lon: float) -> dict:
    return {k: round(v, 3) for k, v in geo_to_unreal(lat, lon, origin_lat, origin_lon).items()}


def heading_to_rotation(heading: float) -> dict:
    return {"pitch": 0.0, "yaw": round(compass_to_yaw(heading), 2), "roll": 0.0}


def compute_bounding_box(points: list[dict], padding: float = 50000.0) -> dict:
    """Compute axis-aligned bounding box from a list of {x,y,z} points."""
    if not points:
        return {"min_x": -1000, "min_y": -100, "min_z": -1000,
                "max_x": 1000, "max_y": 100, "max_z": 1000}
    xs = [p["x"] for p in points]
    ys = [p["y"] for p in points]
    zs = [p["z"] for p in points]
    return {
        "min_x": round(min(xs) - padding, 2),
        "min_y": round(min(ys) - padding, 2),
        "min_z": round(min(zs) - padding, 2),
        "max_x": round(max(xs) + padding, 2),
        "max_y": round(max(ys) + padding, 2),
        "max_z": round(max(zs) + padding, 2),
    }


def generate_traffic_volumes(routes: list[dict], origin_lat: float, origin_lon: float) -> list[dict]:
    """Generate traffic spawn volumes along route splines."""
    volumes = []
    for route in routes:
        pts = route.get("points", [])
        if len(pts) < 2:
            continue
        step = max(1, len(pts) // 4)
        for i in range(0, len(pts) - step, step):
            a = geo_to_world(pts[i]["lat"], pts[i]["lon"], origin_lat, origin_lon)
            b = geo_to_world(pts[i + step]["lat"], pts[i + step]["lon"], origin_lat, origin_lon)
            cx = (a["x"] + b["x"]) / 2
            cy = (a["y"] + b["y"]) / 2
            dx = abs(b["x"] - a["x"]) + 20000
            dy = abs(b["y"] - a["y"]) + 20000
            volumes.append({
                "id": f"traffic_{route['route_id']}_{i}",
                "bounds": {
                    "min": {"x": round(cx - dx / 2, 2), "y": round(cy - dy / 2, 2), "z": -1000.0},
                    "max": {"x": round(cx + dx / 2, 2), "y": round(cy + dy / 2, 2), "z": 3000.0},
                },
                "density": 0.25,
                "vehicle_types": ["sedan", "suv", "truck"],
            })
    return volumes


def main(citypack_dir: Path | None = None, output_dir: Path | None = None) -> int:
    project_root = Path(__file__).resolve().parents[1]
    if citypack_dir is None:
        citypack_dir = project_root / "citypacks" / "akron-oh-beta-001"
    generated_dir = output_dir or project_root / "generated"
    generated_dir.mkdir(parents=True, exist_ok=True)

    # Auto-detect city_id from manifest filename
    manifest_files = list(citypack_dir.glob("*_semantic_manifest.json"))
    if not manifest_files:
        print(f"No manifest found in {citypack_dir}")
        return 1
    manifest_path = manifest_files[0]
    city_id = manifest_path.stem.replace("_semantic_manifest", "")

    # Load inputs
    manifest = json.loads(manifest_path.read_text())
    # Support both new universal-compiler manifests (with files dict) and legacy akron manifests
    if "files" in manifest:
        routes = json.loads((citypack_dir / manifest["files"]["routes"]).read_text())
        spawn_points = json.loads((citypack_dir / manifest["files"]["spawn_points"]).read_text())
        pois = json.loads((citypack_dir / manifest["files"]["pois"]).read_text())
    else:
        # Legacy fallback for akron-oh-beta-001
        routes = json.loads((citypack_dir / "akron_routes.json").read_text())
        spawn_points = json.loads((citypack_dir / "akron_spawn_points.json").read_text())
        pois = json.loads((citypack_dir / "akron_pois.json").read_text())

    origin = manifest["origin"]
    origin_lat = origin["lat"]
    origin_lon = origin["lon"]

    # Convert spawn points
    spec_spawns = []
    for sp in spawn_points:
        spec_spawns.append({
            "id": sp["id"],
            "location": geo_to_world(sp["lat"], sp["lon"], origin_lat, origin_lon),
            "rotation": heading_to_rotation(sp.get("heading", 0)),
            "route_id": sp.get("route_id", ""),
        })

    # Convert routes
    spec_routes = []
    for route in routes:
        spline_points = [
            geo_to_world(p["lat"], p["lon"], origin_lat, origin_lon)
            for p in route.get("points", [])
        ]
        checkpoints = []
        for cp in route.get("checkpoints", []):
            checkpoints.append({
                "id": cp["id"],
                "location": geo_to_world(cp["lat"], cp["lon"], origin_lat, origin_lon),
                "rotation": heading_to_rotation(cp.get("heading", 0)),
                "radius_meters": cp.get("radius_meters", 18),
                "type": cp.get("type", "gate"),
            })
        spec_routes.append({
            "route_id": route["route_id"],
            "mode": route.get("mode", "cruise_sprint"),
            "name": route.get("name", ""),
            "distance_meters": route.get("distance_meters", 0),
            "spline_points": spline_points,
            "checkpoints": checkpoints,
        })

    # POI markers — include all landmarks + a representative mix of others
    landmark_pois = [p for p in pois if p.get("type") == "landmark"]
    other_pois = [p for p in pois if p.get("type") != "landmark"]
    selected_pois = landmark_pois[:50] + other_pois[:50]
    spec_pois = []
    for p in selected_pois:
        spec_pois.append({
            "id": p.get("id", ""),
            "name": p.get("name", ""),
            "type": p.get("type", ""),
            "location": geo_to_world(p["lat"], p["lon"], origin_lat, origin_lon),
        })

    # Traffic spawn volumes
    traffic_volumes = generate_traffic_volumes(routes, origin_lat, origin_lon)

    # Compute world bounding box from all placed points
    all_points = []
    for sp in spec_spawns:
        all_points.append(sp["location"])
    for r in spec_routes:
        all_points.extend(r["spline_points"])
        for cp in r["checkpoints"]:
            all_points.append(cp["location"])

    world_bounds = compute_bounding_box(all_points, padding=50000.0)

    # Load optional M2 procedural world data
    water_data = None
    vegetation_data = None
    heightmap_data = None
    biome_data = None
    if "files" in manifest:
        if "water" in manifest["files"]:
            try: water_data = json.loads((citypack_dir / manifest["files"]["water"]).read_text())
            except: pass
        if "vegetation" in manifest["files"]:
            try: vegetation_data = json.loads((citypack_dir / manifest["files"]["vegetation"]).read_text())
            except: pass
        if "heightmap" in manifest["files"]:
            try: heightmap_data = json.loads((citypack_dir / manifest["files"]["heightmap"]).read_text())
            except: pass
        if "biome" in manifest["files"]:
            try: biome_data = json.loads((citypack_dir / manifest["files"]["biome"]).read_text())
            except: pass

    level_spec = {
        "level_name": city_id.replace("_", " ").title().replace(" ", "") + "World",
        "city_id": manifest["city_id"],
        "origin": origin,
        "coordinate_frame": WORLD_FRAME,
        "world_bounds": world_bounds,
        "spawn_points": spec_spawns,
        "routes": spec_routes,
        "lighting": {
            "time_of_day": 14.0,
            "sun_rotation": {"pitch": -50.0, "yaw": 135.0, "roll": 0.0},
            "sky_atmosphere": "default",
            "exposure": {"method": "Manual", "compensation": 1.0},
        },
        "day_night_cycle": {
            "enabled": True,
            "cycle_duration_minutes": 20,
            "start_time": 14.0,
        },
        "traffic_spawn_volumes": traffic_volumes,
        "poi_markers": spec_pois,
        "terrain": {
            "heightmap": heightmap_data,
            "elevation_offset_m": heightmap_data["min_elevation"] if heightmap_data else 0.0,
        } if heightmap_data else None,
        "water_bodies": water_data,
        "vegetation_zones": vegetation_data,
        "biome": biome_data,
        "metadata": {
            "generated_by": "generate-level-spec.py",
            "spec_version": "3.0.0",
        },
    }

    canonical_level_name = level_spec["level_name"]
    output_path = generated_dir / f"{canonical_level_name}_LevelSpec.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(level_spec, f, indent=2)
    print(f"Generated: {output_path}")
    return 0


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--citypack", type=Path, default=None, help="Path to citypack directory")
    ap.add_argument("--output-dir", type=Path, default=None, help="Use a fresh directory for frame migration")
    args = ap.parse_args()
    raise SystemExit(main(args.citypack, args.output_dir))
