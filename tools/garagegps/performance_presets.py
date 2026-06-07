"""Performance preset loader and query module for garageGPS."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

_CATALOG_PATH = Path(__file__).resolve().parent.parent.parent / "assets" / "car-kit" / "catalogs" / "performance_presets.json"


def load_catalog(path: Path | None = None) -> dict[str, Any]:
    """Load the performance preset catalog from disk."""
    target = path or _CATALOG_PATH
    with open(target, encoding="utf-8") as f:
        return json.load(f)


def get_preset(catalog: dict[str, Any], preset_id: str) -> dict[str, Any] | None:
    """Return a performance preset by ID, or None if not found."""
    return catalog.get("presets", {}).get(preset_id)


def list_presets(catalog: dict[str, Any]) -> list[str]:
    """Return a sorted list of performance preset IDs."""
    return sorted(catalog.get("presets", {}).keys())


def get_preset_for_mode(catalog: dict[str, Any], mode: str) -> list[dict[str, Any]]:
    """Return all presets that support a given gameplay mode."""
    results: list[dict[str, Any]] = []
    for preset in catalog.get("presets", {}).values():
        if mode in preset.get("allowed_modes", []):
            results.append(preset)
    return results


def validate_preset_values(preset: dict[str, Any]) -> list[str]:
    """Validate numeric fields in a performance preset are within sensible bounds."""
    errors: list[str] = []
    checks = {
        "mass_kg": (500, 5000),
        "max_speed_kph": (50, 500),
        "steering_response": (0.0, 1.0),
        "drift_assist": (0.0, 1.0),
        "traction_assist": (0.0, 1.0),
        "brake_strength": (0.0, 1.0),
    }
    for key, (min_v, max_v) in checks.items():
        if key in preset:
            val = preset[key]
            if not isinstance(val, (int, float)) or not (min_v <= val <= max_v):
                errors.append(f"{key}={val} out of range [{min_v}, {max_v}]")
    return errors
