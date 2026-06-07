"""Extended validators for garageGPS builds, parts, and materials."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import jsonschema

from . import part_catalog, material_catalog, performance_presets

SCHEMA_DIR = Path(__file__).resolve().parent.parent.parent / "packages" / "car-kit-schema"


def load_schema(name: str) -> dict[str, Any]:
    path = SCHEMA_DIR / f"{name}.schema.json"
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def validate_build_against_schema(build: dict[str, Any]) -> list[str]:
    """Validate a car build dict against the JSON schema."""
    errors: list[str] = []
    schema = load_schema("car-build")
    try:
        jsonschema.validate(build, schema)
    except jsonschema.ValidationError as e:
        errors.append(f"Schema error: {e.message} at {list(e.path)}")
    return errors


def validate_build_parts(build: dict[str, Any], catalog: dict[str, Any] | None = None) -> list[str]:
    """Validate all visual parts in a build are compatible and within budget."""
    errors: list[str] = []
    if catalog is None:
        catalog = part_catalog.load_catalog()

    body_style = build.get("body_style")
    chassis = build.get("base_chassis")
    visual_parts = build.get("visual_parts", {})

    part_ids = []
    for slot, part_id in visual_parts.items():
        if not part_id or part_id == "none":
            continue
        part_ids.append(part_id)
        part = part_catalog.get_part(catalog, part_id)
        if part is None:
            errors.append(f"Unknown part '{part_id}' in slot '{slot}'")
            continue
        if part.get("slot") != slot:
            errors.append(
                f"Part '{part_id}' loaded into wrong slot '{slot}' (expected '{part.get('slot')}')"
            )
        if body_style and chassis:
            errors.extend(part_catalog.check_part_compatibility(catalog, part_id, body_style, chassis))

    # Budget check
    max_faces = build.get("validation", {}).get("max_faces", 100000)
    budget_errors = part_catalog.check_budget(catalog, part_ids, max_budget=max_faces)
    errors.extend(budget_errors)

    return errors


def validate_build_materials(build: dict[str, Any]) -> list[str]:
    """Validate material values in a build are within expected ranges."""
    errors: list[str] = []
    materials = build.get("materials", {})
    errors.extend(material_catalog.validate_material_values(materials))
    return errors


def validate_build_performance_preset(build: dict[str, Any], catalog: dict[str, Any] | None = None) -> list[str]:
    """Validate the physics preset exists and has sensible values."""
    errors: list[str] = []
    if catalog is None:
        catalog = performance_presets.load_catalog()

    preset_id = build.get("physics_preset")
    if not preset_id:
        errors.append("Missing physics_preset")
        return errors

    preset = performance_presets.get_preset(catalog, preset_id)
    if preset is None:
        errors.append(f"Unknown physics_preset '{preset_id}'")
        return errors

    errors.extend(performance_presets.validate_preset_values(preset))
    return errors


def validate_build(
    build: dict[str, Any],
    part_catalog_data: dict[str, Any] | None = None,
    perf_catalog_data: dict[str, Any] | None = None,
) -> list[str]:
    """Run full extended validation on a car build dict.

    Returns a list of error strings (empty if fully valid).
    """
    errors: list[str] = []
    errors.extend(validate_build_against_schema(build))
    errors.extend(validate_build_parts(build, catalog=part_catalog_data))
    errors.extend(validate_build_materials(build))
    errors.extend(validate_build_performance_preset(build, catalog=perf_catalog_data))

    # Extra semantic checks
    if "visual_parts" in build:
        parts = build["visual_parts"]
        if "wheels" not in parts or not parts["wheels"]:
            errors.append("Missing required visual part: wheels")

    mats = build.get("materials", {})
    if "body" not in mats:
        errors.append("Missing required material: body")
    else:
        body = mats["body"]
        if body.get("metallic", 0) > 0.9 and body.get("roughness", 1) < 0.1:
            errors.append("Warning: extreme metallic + low roughness may cause shader artifacts")

    return errors


def validate_build_file(build_path: Path) -> list[str]:
    """Load and fully validate a car build JSON file."""
    try:
        with open(build_path, encoding="utf-8") as f:
            build = json.load(f)
    except json.JSONDecodeError as e:
        return [f"Invalid JSON: {e}"]

    return validate_build(build)
