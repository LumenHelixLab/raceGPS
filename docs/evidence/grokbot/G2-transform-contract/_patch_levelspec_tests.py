from pathlib import Path
p = Path(r"C:\projects\raceGPS-grokbot-cleveland\tests\test_levelspec.py")
t = p.read_text(encoding="utf-8")

old_helpers = '''def meters_per_degree_lon(origin_lat: float) -> float:
    return 111320.0 * math.cos(math.radians(origin_lat))


def meters_per_degree_lat() -> float:
    return 110540.0


def geo_to_world(lat: float, lon: float, origin_lat: float, origin_lon: float) -> dict:
    mpdlon = meters_per_degree_lon(origin_lat)
    mpdlat = meters_per_degree_lat()
    x = (lon - origin_lon) * mpdlon
    z = -(lat - origin_lat) * mpdlat
    return {"x": x, "y": 0.0, "z": z}'''

new_helpers = '''METERS_TO_UU = 100.0  # SOURCE_TO_UNREAL_FRAME_v1


def meters_per_degree_lon(origin_lat: float) -> float:
    return 111320.0 * math.cos(math.radians(origin_lat))


def meters_per_degree_lat() -> float:
    return 111320.0


def geo_to_world(lat: float, lon: float, origin_lat: float, origin_lon: float) -> dict:
    """Frame A cm: X=east Y=north Z=up (matches tools/generate-level-spec.py)."""
    mpdlon = meters_per_degree_lon(origin_lat)
    mpdlat = meters_per_degree_lat()
    x = (lon - origin_lon) * mpdlon * METERS_TO_UU
    y = (lat - origin_lat) * mpdlat * METERS_TO_UU
    return {"x": x, "y": y, "z": 0.0}'''

if old_helpers not in t:
    raise SystemExit("helpers not found")
t = t.replace(old_helpers, new_helpers, 1)

# manifest bounds inverse (world cm -> lat/lon)
old_inv = '''        for sp in level_spec["spawn_points"]:
            loc = sp["location"]
            lon = loc["x"] / mpdlon + origin_lon
            lat = -loc["z"] / mpdlat + origin_lat
            assert bounds["west"] <= lon <= bounds["east"]
            assert bounds["south"] <= lat <= bounds["north"]'''
new_inv = '''        for sp in level_spec["spawn_points"]:
            loc = sp["location"]
            lon = loc["x"] / (mpdlon * METERS_TO_UU) + origin_lon
            lat = loc["y"] / (mpdlat * METERS_TO_UU) + origin_lat
            assert bounds["west"] <= lon <= bounds["east"]
            assert bounds["south"] <= lat <= bounds["north"]'''
if old_inv not in t:
    raise SystemExit("inverse block not found")
t = t.replace(old_inv, new_inv, 1)

old_len = '''            total = 0.0
            for i in range(len(pts) - 1):
                a, b = pts[i], pts[i + 1]
                dx = b["x"] - a["x"]
                dz = b["z"] - a["z"]
                total += math.hypot(dx, dz)
            stated = route["distance_meters"]
            variance = abs(total - stated) / max(stated, 1)
            assert variance <= 0.15, (
                f"Route {route['route_id']} spline length {total:.0f}m "
                f"differs from stated {stated}m by {variance * 100:.1f}%"
            )'''
new_len = '''            total_cm = 0.0
            for i in range(len(pts) - 1):
                a, b = pts[i], pts[i + 1]
                dx = b["x"] - a["x"]
                dy = b["y"] - a["y"]
                total_cm += math.hypot(dx, dy)
            total_m = total_cm / METERS_TO_UU
            stated = route["distance_meters"]
            variance = abs(total_m - stated) / max(stated, 1)
            assert variance <= 0.15, (
                f"Route {route['route_id']} spline length {total_m:.0f}m "
                f"differs from stated {stated}m by {variance * 100:.1f}%"
            )'''
if old_len not in t:
    raise SystemExit("length block not found")
t = t.replace(old_len, new_len, 1)

old_cp = '''                min_dist = min(
                    math.hypot(loc["x"] - p["x"], loc["z"] - p["z"])
                    for p in pts
                )
                assert min_dist <= 100, (
                    f"Checkpoint {cp['id']} is {min_dist:.0f}m from nearest spline point"
                )'''
new_cp = '''                min_dist_m = min(
                    math.hypot(loc["x"] - p["x"], loc["y"] - p["y"]) / METERS_TO_UU
                    for p in pts
                )
                assert min_dist_m <= 100, (
                    f"Checkpoint {cp['id']} is {min_dist_m:.0f}m from nearest spline point"
                )'''
if old_cp not in t:
    raise SystemExit("cp block not found")
t = t.replace(old_cp, new_cp, 1)

old_sp = '''            dist = math.hypot(loc["x"] - start["x"], loc["z"] - start["z"])
            assert dist <= 1.0, (
                f"Spawn point {sp['id']} is {dist:.1f}m from route {route_id} start"
            )'''
new_sp = '''            dist_m = math.hypot(loc["x"] - start["x"], loc["y"] - start["y"]) / METERS_TO_UU
            assert dist_m <= 1.0, (
                f"Spawn point {sp['id']} is {dist_m:.1f}m from route {route_id} start"
            )'''
if old_sp not in t:
    raise SystemExit("spawn match block not found")
t = t.replace(old_sp, new_sp, 1)

# schema: require frame field
if '"frame"' not in t.split("class TestLevelSpecSchema")[1][:800]:
    t = t.replace(
        '''        required = [
            "level_name",
            "city_id",
            "origin",
            "world_bounds",''',
        '''        required = [
            "frame",
            "level_name",
            "city_id",
            "origin",
            "world_bounds",''',
        1,
    )

p.write_text(t, encoding="utf-8")
print("test_levelspec patched for Frame A")
