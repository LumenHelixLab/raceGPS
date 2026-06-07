"""Material catalog loader and query module for garageGPS."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

_CATALOG_PATH = Path(__file__).resolve().parent.parent.parent / "assets" / "car-kit" / "catalogs" / "material_catalog.json"


def load_catalog(path: Path | None = None) -> dict[str, Any]:
    """Load the material catalog from disk."""
    target = path or _CATALOG_PATH
    with open(target, encoding="utf-8") as f:
        return json.load(f)


def get_paint_preset(catalog: dict[str, Any], preset_id: str) -> dict[str, Any] | None:
    """Return a paint preset by ID, or None if not found."""
    return catalog.get("paint_presets", {}).get(preset_id)


def get_glass_tint(catalog: dict[str, Any], preset_id: str) -> dict[str, Any] | None:
    """Return a glass tint preset by ID, or None if not found."""
    return catalog.get("glass_tints", {}).get(preset_id)


def get_underglow_color(catalog: dict[str, Any], preset_id: str) -> dict[str, Any] | None:
    """Return an underglow color preset by ID, or None if not found."""
    return catalog.get("underglow_colors", {}).get(preset_id)


def list_paint_presets(catalog: dict[str, Any]) -> list[str]:
    """Return a sorted list of paint preset IDs."""
    return sorted(catalog.get("paint_presets", {}).keys())


def list_glass_tints(catalog: dict[str, Any]) -> list[str]:
    """Return a sorted list of glass tint preset IDs."""
    return sorted(catalog.get("glass_tints", {}).keys())


def list_underglow_colors(catalog: dict[str, Any]) -> list[str]:
    """Return a sorted list of underglow color preset IDs."""
    return sorted(catalog.get("underglow_colors", {}).keys())


def validate_material_values(material: dict[str, Any]) -> list[str]:
    """Validate numeric material values are within expected ranges."""
    errors: list[str] = []
    if "body" in material:
        body = material["body"]
        for key, (min_v, max_v) in {
            "metallic": (0.0, 1.0),
            "roughness": (0.0, 1.0),
            "clearcoat": (0.0, 1.0),
        }.items():
            if key in body and not (min_v <= body[key] <= max_v):
                errors.append(f"body.{key}={body[key]} out of range [{min_v}, {max_v}]")
        if "base_color" in body:
            color = body["base_color"]
            if not isinstance(color, str) or len(color) != 7 or not color.startswith("#"):
                errors.append(f"body.base_color='{color}' is not a valid #RRGGBB hex color")
    if "glass" in material:
        glass = material["glass"]
        if "tint" in glass and not (0.0 <= glass["tint"] <= 1.0):
            errors.append(f"glass.tint={glass['tint']} out of range [0.0, 1.0]")
    if "underglow" in material:
        underglow = material["underglow"]
        if "color" in underglow:
            color = underglow["color"]
            if not isinstance(color, str) or len(color) != 7 or not color.startswith("#"):
                errors.append(f"underglow.color='{color}' is not a valid #RRGGBB hex color")
    return errors
