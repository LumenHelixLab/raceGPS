"""Part catalog loader and query module for garageGPS."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

_CATALOG_PATH = Path(__file__).resolve().parent.parent.parent / "assets" / "car-kit" / "catalogs" / "part_catalog.json"


def load_catalog(path: Path | None = None) -> dict[str, Any]:
    """Load the part catalog from disk."""
    target = path or _CATALOG_PATH
    with open(target, encoding="utf-8") as f:
        return json.load(f)


def get_part(catalog: dict[str, Any], part_id: str) -> dict[str, Any] | None:
    """Return a part definition by ID, or None if not found."""
    return catalog.get("parts", {}).get(part_id)


def list_parts(catalog: dict[str, Any]) -> list[str]:
    """Return a sorted list of part IDs."""
    return sorted(catalog.get("parts", {}).keys())


def list_parts_by_slot(catalog: dict[str, Any], slot: str) -> list[dict[str, Any]]:
    """Return all parts that occupy a given slot."""
    return [p for p in catalog.get("parts", {}).values() if p.get("slot") == slot]


def list_compatible_parts(
    catalog: dict[str, Any],
    body_style: str | None = None,
    chassis: str | None = None,
    slot: str | None = None,
) -> list[dict[str, Any]]:
    """Return parts filtered by body style, chassis, and/or slot."""
    results: list[dict[str, Any]] = []
    for part in catalog.get("parts", {}).values():
        if body_style and body_style not in part.get("compatible_body_styles", []):
            continue
        if chassis and chassis not in part.get("compatible_chassis", []):
            continue
        if slot and part.get("slot") != slot:
            continue
        results.append(part)
    return results


def check_part_compatibility(
    catalog: dict[str, Any],
    part_id: str,
    body_style: str,
    chassis: str,
) -> list[str]:
    """Validate a part is compatible with the given body style and chassis.

    Returns a list of error strings (empty if compatible).
    """
    errors: list[str] = []
    part = get_part(catalog, part_id)
    if part is None:
        errors.append(f"Part '{part_id}' not found in catalog")
        return errors

    compatible_styles = part.get("compatible_body_styles", [])
    if body_style not in compatible_styles:
        errors.append(
            f"Part '{part_id}' is not compatible with body style '{body_style}' "
            f"(compatible: {compatible_styles})"
        )

    compatible_chassis = part.get("compatible_chassis", [])
    if chassis not in compatible_chassis:
        errors.append(
            f"Part '{part_id}' is not compatible with chassis '{chassis}' "
            f"(compatible: {compatible_chassis})"
        )
    return errors


def compute_total_triangle_budget(catalog: dict[str, Any], part_ids: list[str]) -> int:
    """Sum triangle budgets for a list of part IDs."""
    total = 0
    for pid in part_ids:
        part = get_part(catalog, pid)
        if part:
            total += part.get("triangle_budget", 0)
    return total


def check_budget(catalog: dict[str, Any], part_ids: list[str], max_budget: int = 100000) -> list[str]:
    """Check whether a list of parts stays within the triangle budget."""
    errors: list[str] = []
    total = compute_total_triangle_budget(catalog, part_ids)
    if total > max_budget:
        errors.append(f"Triangle budget exceeded: {total} > {max_budget}")
    return errors
