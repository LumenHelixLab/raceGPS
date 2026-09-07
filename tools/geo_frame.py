"""Versioned city-local projection and Unreal renderer boundary.

Source: equirectangular east/north/up meters, matching the prototype XODR
exporter. Renderer: X east, Y south, Z up, centimeters (left-handed).
This approximation is not a surveyed terrain/vertical-datum transform.
"""
import math

SOURCE_FRAME = 'racegps-eqc-enu-m-v1'
WORLD_FRAME = 'racegps-ue-esu-cm-v1'
METERS_PER_DEGREE = 111320.0
CM_PER_METER = 100.0


def local_meters(lat, lon, origin_lat, origin_lon):
    values = (lat, lon, origin_lat, origin_lon)
    if not all(math.isfinite(v) for v in values):
        raise ValueError('Coordinates must be finite')
    if not (-90 < origin_lat < 90 and -90 <= lat <= 90 and -180 <= lon <= 180 and -180 <= origin_lon <= 180):
        raise ValueError('Unsupported geographic coordinates')
    return ((lon - origin_lon) * METERS_PER_DEGREE * math.cos(math.radians(origin_lat)),
            (lat - origin_lat) * METERS_PER_DEGREE)


def to_unreal(east, north, up=0.0):
    if not all(math.isfinite(v) for v in (east, north, up)):
        raise ValueError('Local coordinates must be finite')
    return {'x': east * CM_PER_METER, 'y': -north * CM_PER_METER, 'z': up * CM_PER_METER}


def geo_to_unreal(lat, lon, origin_lat, origin_lon, up=0.0):
    return to_unreal(*local_meters(lat, lon, origin_lat, origin_lon), up)


def compass_to_yaw(heading):
    if not math.isfinite(heading):
        raise ValueError('Heading must be finite')
    return (heading + 90.0) % 360.0 - 180.0


def require_world_frame(document):
    if document.get('coordinate_frame') != WORLD_FRAME:
        raise ValueError('Unsupported or missing world coordinate frame; regenerate and reimport the scene')


def scene_tags(document):
    require_world_frame(document)
    origin = document['origin']
    local_meters(origin['lat'], origin['lon'], origin['lat'], origin['lon'])
    return [f'racegps.frame:{WORLD_FRAME}',
            f"racegps.origin.lat={origin['lat']:.9f}", f"racegps.origin.lon={origin['lon']:.9f}"]
