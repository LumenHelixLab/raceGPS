"""
garageGPS Extended Validation Tests
Tests for catalogs, part compatibility, material ranges, budget checks,
and full build validation across all sample builds.
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
GARAGEGPS = PROJECT_ROOT / "tools" / "garagegps" / "garagegps.py"
CATALOG_DIR = PROJECT_ROOT / "assets" / "car-kit" / "catalogs"
BUILD_DIR = PROJECT_ROOT / "assets" / "car-kit" / "builds"
SCHEMA_DIR = PROJECT_ROOT / "packages" / "car-kit-schema"

from tools.garagegps.part_catalog import (
    load_catalog as load_part_catalog,
    get_part,
    list_parts,
    list_parts_by_slot,
    list_compatible_parts,
    check_part_compatibility,
    compute_total_triangle_budget,
    check_budget,
)
from tools.garagegps.material_catalog import (
    load_catalog as load_material_catalog,
    get_paint_preset,
    get_glass_tint,
    get_underglow_color,
    list_paint_presets,
    list_glass_tints,
    list_underglow_colors,
    validate_material_values,
)
from tools.garagegps.performance_presets import (
    load_catalog as load_perf_catalog,
    get_preset,
    list_presets,
    validate_preset_values,
)
from tools.garagegps.validators import validate_build_file, validate_build


# ---------------------------------------------------------------------------
# Catalog loading helpers
# ---------------------------------------------------------------------------


@pytest.fixture
def part_catalog():
    return load_part_catalog()


@pytest.fixture
def material_catalog():
    return load_material_catalog()


@pytest.fixture
def perf_catalog():
    return load_perf_catalog()


# ---------------------------------------------------------------------------
# Part catalog tests
# ---------------------------------------------------------------------------


def test_part_catalog_loads(part_catalog):
    assert "parts" in part_catalog
    assert len(part_catalog["parts"]) > 0


def test_part_catalog_has_required_slots(part_catalog):
    required_slots = {"front_bumper", "rear_bumper", "side_skirts", "hood", "spoiler", "wheels", "decals"}
    found_slots = {p["slot"] for p in part_catalog["parts"].values()}
    assert required_slots.issubset(found_slots), f"Missing slots: {required_slots - found_slots}"


def test_part_catalog_triangle_budgets_positive(part_catalog):
    for part_id, part in part_catalog["parts"].items():
        assert part["triangle_budget"] >= 0, f"{part_id} has negative budget"


def test_part_catalog_ids_match_keys(part_catalog):
    for key, part in part_catalog["parts"].items():
        assert part["part_id"] == key, f"Key mismatch for {key}"


def test_part_lookup(part_catalog):
    part = get_part(part_catalog, "ducktail_01")
    assert part is not None
    assert part["display_name"] == "Ducktail Spoiler"


def test_part_lookup_missing(part_catalog):
    assert get_part(part_catalog, "nonexistent") is None


def test_list_parts_by_slot(part_catalog):
    wheels = list_parts_by_slot(part_catalog, "wheels")
    assert len(wheels) >= 3
    for w in wheels:
        assert w["slot"] == "wheels"


def test_list_compatible_parts_coupe(part_catalog):
    parts = list_compatible_parts(part_catalog, body_style="coupe", chassis="rgps_chassis_4w_sport")
    assert len(parts) > 0
    ids = {p["part_id"] for p in parts}
    assert "ducktail_01" in ids
    assert "five_spoke_01" in ids


def test_list_compatible_parts_sedan_pursuit(part_catalog):
    parts = list_compatible_parts(part_catalog, body_style="sedan", chassis="rgps_chassis_4w_sedan")
    ids = {p["part_id"] for p in parts}
    assert "kit_pursuit_front_01" in ids
    assert "pursuit_steelie_01" in ids


def test_check_part_compatibility_ok(part_catalog):
    errors = check_part_compatibility(part_catalog, "ducktail_01", "coupe", "rgps_chassis_4w_sport")
    assert errors == []


def test_check_part_compatibility_bad_style(part_catalog):
    errors = check_part_compatibility(part_catalog, "kit_pursuit_front_01", "coupe", "rgps_chassis_4w_sport")
    assert any("not compatible with body style" in e for e in errors)


def test_check_part_compatibility_bad_chassis(part_catalog):
    errors = check_part_compatibility(part_catalog, "kit_pursuit_front_01", "sedan", "rgps_chassis_4w_sport")
    assert any("not compatible with chassis" in e for e in errors)


def test_triangle_budget_sum(part_catalog):
    total = compute_total_triangle_budget(part_catalog, ["ducktail_01", "five_spoke_01"])
    assert total == 2500 + 3600


def test_budget_check_pass(part_catalog):
    errors = check_budget(part_catalog, ["ducktail_01", "five_spoke_01"], max_budget=100000)
    assert errors == []


def test_budget_check_fail(part_catalog):
    errors = check_budget(part_catalog, list_parts(part_catalog), max_budget=1)
    assert len(errors) == 1
    assert "budget exceeded" in errors[0].lower()


# ---------------------------------------------------------------------------
# Material catalog tests
# ---------------------------------------------------------------------------


def test_material_catalog_loads(material_catalog):
    assert "paint_presets" in material_catalog
    assert "glass_tints" in material_catalog
    assert "underglow_colors" in material_catalog


def test_paint_presets_count(material_catalog):
    presets = list_paint_presets(material_catalog)
    assert len(presets) == 5


def test_paint_preset_fields(material_catalog):
    for pid, preset in material_catalog["paint_presets"].items():
        assert "base_color" in preset
        assert "metallic" in preset
        assert "roughness" in preset
        assert "clearcoat" in preset
        assert 0.0 <= preset["metallic"] <= 1.0
        assert 0.0 <= preset["roughness"] <= 1.0
        assert 0.0 <= preset["clearcoat"] <= 1.0
        assert preset["base_color"].startswith("#")


def test_glass_tints_count(material_catalog):
    assert len(list_glass_tints(material_catalog)) == 5


def test_underglow_colors_count(material_catalog):
    assert len(list_underglow_colors(material_catalog)) == 5


def test_get_paint_preset(material_catalog):
    preset = get_paint_preset(material_catalog, "midnight_black")
    assert preset is not None
    assert preset["base_color"] == "#111827"


def test_validate_material_values_ok(material_catalog):
    sample = {
        "body": {"base_color": "#111827", "metallic": 0.7, "roughness": 0.24, "clearcoat": 0.9},
        "glass": {"tint": 0.35},
        "underglow": {"enabled": True, "color": "#00E5FF"},
    }
    assert validate_material_values(sample) == []


def test_validate_material_values_out_of_range(material_catalog):
    sample = {"body": {"base_color": "#111827", "metallic": 1.5, "roughness": -0.1, "clearcoat": 2.0}}
    errors = validate_material_values(sample)
    assert len(errors) == 3


def test_validate_material_values_bad_color(material_catalog):
    sample = {"body": {"base_color": "red", "metallic": 0.5, "roughness": 0.5, "clearcoat": 0.5}}
    errors = validate_material_values(sample)
    assert any("not a valid" in e for e in errors)


# ---------------------------------------------------------------------------
# Performance preset catalog tests
# ---------------------------------------------------------------------------


def test_perf_catalog_loads(perf_catalog):
    assert "presets" in perf_catalog
    assert len(perf_catalog["presets"]) == 5


def test_perf_presets_list(perf_catalog):
    presets = list_presets(perf_catalog)
    expected = {"arcade_street", "arcade_sprint", "arcade_drift", "arcade_pursuit", "arcade_heavy"}
    assert set(presets) == expected


def test_get_preset(perf_catalog):
    preset = get_preset(perf_catalog, "arcade_sprint")
    assert preset is not None
    assert preset["display_name"] == "Sprint"


def test_validate_preset_values_ok(perf_catalog):
    preset = get_preset(perf_catalog, "arcade_street")
    assert validate_preset_values(preset) == []


def test_validate_preset_values_bad_mass(perf_catalog):
    preset = dict(get_preset(perf_catalog, "arcade_street"))
    preset["mass_kg"] = 10000
    errors = validate_preset_values(preset)
    assert any("mass_kg" in e for e in errors)


# ---------------------------------------------------------------------------
# Build validation tests
# ---------------------------------------------------------------------------

BUILD_NAMES = [
    "akron_street_coupe_001.json",
    "akron_pursuit_sedan_001.json",
    "akron_rally_hatch_001.json",
]


def test_all_builds_exist():
    for name in BUILD_NAMES:
        assert (BUILD_DIR / name).exists()


def test_all_builds_valid():
    for name in BUILD_NAMES:
        errors = validate_build_file(BUILD_DIR / name)
        assert errors == [], f"{name} validation errors: {errors}"


def test_build_pursuit_sedan_has_pursuit_parts(part_catalog):
    path = BUILD_DIR / "akron_pursuit_sedan_001.json"
    build = json.loads(path.read_text())
    assert build["visual_parts"]["wheels"] == "pursuit_steelie_01"
    errors = check_part_compatibility(
        part_catalog,
        "pursuit_steelie_01",
        build["body_style"],
        build["base_chassis"],
    )
    assert errors == []


def test_build_rally_hatch_sprint_kit_compatible(part_catalog):
    path = BUILD_DIR / "akron_rally_hatch_001.json"
    build = json.loads(path.read_text())
    for slot, part_id in build["visual_parts"].items():
        if not part_id or part_id == "none":
            continue
        errors = check_part_compatibility(
            part_catalog,
            part_id,
            build["body_style"],
            build["base_chassis"],
        )
        assert errors == [], f"{slot}={part_id} incompatible: {errors}"


def test_build_budgets_under_limit(part_catalog):
    for name in BUILD_NAMES:
        path = BUILD_DIR / name
        build = json.loads(path.read_text())
        part_ids = [pid for pid in build.get("visual_parts", {}).values() if pid and pid != "none"]
        total = compute_total_triangle_budget(part_catalog, part_ids)
        max_faces = build.get("validation", {}).get("max_faces", 100000)
        assert total <= max_faces, f"{name} budget {total} > {max_faces}"


# ---------------------------------------------------------------------------
# CLI integration tests for new builds
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("build_name", BUILD_NAMES)
def test_cli_validate(build_name):
    path = BUILD_DIR / build_name
    result = subprocess.run(
        [sys.executable, str(GARAGEGPS), "validate", str(path)],
        capture_output=True, text=True
    )
    assert result.returncode == 0, f"Validation failed: {result.stdout}{result.stderr}"
    assert "is valid" in result.stdout


@pytest.mark.parametrize("build_name", BUILD_NAMES)
def test_cli_build(build_name):
    path = BUILD_DIR / build_name
    result = subprocess.run(
        [sys.executable, str(GARAGEGPS), "build", str(path)],
        capture_output=True, text=True
    )
    assert result.returncode == 0
    assert "Built manifest" in result.stdout
    built_path = path.with_suffix(".built.json")
    assert built_path.exists()
    data = json.loads(built_path.read_text())
    assert "_computed" in data


@pytest.mark.parametrize("build_name", BUILD_NAMES)
def test_cli_export_unreal(build_name):
    path = BUILD_DIR / build_name
    result = subprocess.run(
        [sys.executable, str(GARAGEGPS), "export-unreal", str(path)],
        capture_output=True, text=True
    )
    assert result.returncode == 0
    assert "Unreal manifest" in result.stdout
    manifest_path = path.with_suffix(".unreal.json")
    assert manifest_path.exists()
    data = json.loads(manifest_path.read_text())
    assert "content_paths" in data
    assert "blueprint_class" in data


@pytest.mark.parametrize("build_name", BUILD_NAMES)
def test_cli_export_carla(build_name):
    path = BUILD_DIR / build_name
    result = subprocess.run(
        [sys.executable, str(GARAGEGPS), "export-carla", str(path)],
        capture_output=True, text=True
    )
    assert result.returncode == 0
    assert "CARLA manifest" in result.stdout
    manifest_path = path.with_suffix(".carla.json")
    assert manifest_path.exists()
    data = json.loads(manifest_path.read_text())
    assert "wheel_blueprints" in data
    assert data["make"] == "raceGPS"


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
