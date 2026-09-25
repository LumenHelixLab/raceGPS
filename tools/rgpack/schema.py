from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal, Optional


class RgpackValidationError(ValueError):
    pass


@dataclass(frozen=True)
class Frame:
    units_per_meter: int
    z_up: bool
    x_east: bool
    y_north: bool
    origin_lat: float
    origin_lon: float
    origin_alt_m: float


@dataclass(frozen=True)
class Source:
    type: Literal["osm", "gps_trace", "provisional_circuit"]
    attribution: str
    retrieved_at: str
    bbox: list[float]  # [minLon, minLat, maxLon, maxLat]


@dataclass(frozen=True)
class Certification:
    status: Literal["provisional", "certified"]
    notes: str


@dataclass(frozen=True)
class Defaults:
    environment_preset: Literal["Sunset", "Twilight", "Midnight"]
    loadout_id: Optional[str]


@dataclass(frozen=True)
class Manifest:
    schema_version: int
    pack_id: str
    display_name: str
    frame: Frame
    source: Source
    certification: Certification
    content_hash: str
    defaults: Defaults
    streets: str = "streets.json"
    checkpoints: str = "checkpoints.json"
    spawn: str = "spawn.json"
    environment: str = "environment.json"

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "schemaVersion": self.schema_version,
            "packId": self.pack_id,
            "displayName": self.display_name,
            "frame": {
                "unitsPerMeter": self.frame.units_per_meter,
                "zUp": self.frame.z_up,
                "xEast": self.frame.x_east,
                "yNorth": self.frame.y_north,
                "originLat": self.frame.origin_lat,
                "originLon": self.frame.origin_lon,
                "originAltM": self.frame.origin_alt_m,
            },
            "source": {
                "type": self.source.type,
                "attribution": self.source.attribution,
                "retrievedAt": self.source.retrieved_at,
                "bbox": list(self.source.bbox),
            },
            "certification": {
                "status": self.certification.status,
                "notes": self.certification.notes,
            },
            "contentHash": self.content_hash,
            "defaults": {"environmentPreset": self.defaults.environment_preset},
            "streets": self.streets,
            "checkpoints": self.checkpoints,
            "spawn": self.spawn,
            "environment": self.environment,
        }
        if self.defaults.loadout_id is not None:
            d["defaults"]["loadoutId"] = self.defaults.loadout_id
        return d


def _req(data: dict, key: str) -> Any:
    if key not in data:
        raise RgpackValidationError(f"missing required field: {key}")
    return data[key]


def validate_manifest(data: dict[str, Any]) -> Manifest:
    if not isinstance(data, dict):
        raise RgpackValidationError("manifest must be an object")
    schema_version = _req(data, "schemaVersion")
    if schema_version != 1:
        raise RgpackValidationError(f"unsupported schemaVersion: {schema_version}")

    frame_raw = _req(data, "frame")
    units = _req(frame_raw, "unitsPerMeter")
    if units != 100:
        raise RgpackValidationError("frame.unitsPerMeter must be 100 (Frame A)")
    for flag_key in ("zUp", "xEast", "yNorth"):
        if _req(frame_raw, flag_key) is not True:
            raise RgpackValidationError(f"frame.{flag_key} must be true (Frame A)")

    frame = Frame(
        units_per_meter=100,
        z_up=True,
        x_east=True,
        y_north=True,
        origin_lat=float(_req(frame_raw, "originLat")),
        origin_lon=float(_req(frame_raw, "originLon")),
        origin_alt_m=float(_req(frame_raw, "originAltM")),
    )

    source_raw = _req(data, "source")
    src_type = _req(source_raw, "type")
    if src_type not in ("osm", "gps_trace", "provisional_circuit"):
        raise RgpackValidationError(f"source.type invalid: {src_type}")
    bbox = _req(source_raw, "bbox")
    if not (isinstance(bbox, list) and len(bbox) == 4):
        raise RgpackValidationError("source.bbox must be [minLon,minLat,maxLon,maxLat]")
    source = Source(
        type=src_type,
        attribution=str(_req(source_raw, "attribution")),
        retrieved_at=str(_req(source_raw, "retrievedAt")),
        bbox=[float(x) for x in bbox],
    )

    cert_raw = _req(data, "certification")
    status = _req(cert_raw, "status")
    if status not in ("provisional", "certified"):
        raise RgpackValidationError(f"certification.status invalid: {status}")
    certification = Certification(status=status, notes=str(_req(cert_raw, "notes")))

    content_hash = _req(data, "contentHash")
    if not isinstance(content_hash, str) or not content_hash.startswith("sha256:"):
        raise RgpackValidationError("contentHash must start with sha256:")

    defaults_raw = _req(data, "defaults")
    preset = _req(defaults_raw, "environmentPreset")
    if preset not in ("Sunset", "Twilight", "Midnight"):
        raise RgpackValidationError(f"defaults.environmentPreset invalid: {preset}")
    defaults = Defaults(
        environment_preset=preset,
        loadout_id=defaults_raw.get("loadoutId"),
    )

    return Manifest(
        schema_version=1,
        pack_id=str(_req(data, "packId")),
        display_name=str(_req(data, "displayName")),
        frame=frame,
        source=source,
        certification=certification,
        content_hash=content_hash,
        defaults=defaults,
        streets=str(data.get("streets", "streets.json")),
        checkpoints=str(data.get("checkpoints", "checkpoints.json")),
        spawn=str(data.get("spawn", "spawn.json")),
        environment=str(data.get("environment", "environment.json")),
    )
