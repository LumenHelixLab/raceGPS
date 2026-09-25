"""rgpack v1: manifest schema + golden fixture round-trip."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from rgpack.hashutil import content_hash  # noqa: E402
from rgpack.io import load_pack, save_pack, validate_pack_dir  # noqa: E402
from rgpack.schema import RgpackValidationError, validate_manifest  # noqa: E402

FIXTURE = ROOT / "tests" / "fixtures" / "rgpack" / "minimal_v1"
GEOMETRY = ["streets.json", "checkpoints.json", "spawn.json", "environment.json"]


def test_golden_fixture_loads():
    m = load_pack(FIXTURE)
    assert m.schema_version == 1
    assert m.pack_id == "fixture_minimal_v1"
    assert m.display_name == "Minimal Fixture"
    assert m.frame.units_per_meter == 100
    assert m.frame.z_up is True
    assert m.frame.x_east is True
    assert m.frame.y_north is True
    assert m.source.type == "osm"
    assert m.certification.status == "provisional"
    assert m.defaults.environment_preset == "Sunset"
    assert m.content_hash.startswith("sha256:")


def test_golden_content_hash_matches_geometry():
    m = load_pack(FIXTURE)
    assert content_hash(FIXTURE, GEOMETRY) == m.content_hash


def test_round_trip_tmp_dir(tmp_path: Path):
    m = load_pack(FIXTURE)
    files = {
        name: json.loads((FIXTURE / name).read_text(encoding="utf-8"))
        for name in GEOMETRY
    }
    out = tmp_path / "pack"
    save_pack(out, m, files)
    m2 = load_pack(out)
    assert m2.pack_id == m.pack_id
    assert m2.content_hash == content_hash(out, GEOMETRY)
    assert validate_pack_dir(out) is True


def test_missing_required_field_raises():
    raw = json.loads((FIXTURE / "manifest.json").read_text(encoding="utf-8"))
    del raw["packId"]
    with pytest.raises(RgpackValidationError, match="packId"):
        validate_manifest(raw)


def test_bad_frame_units_rejected():
    raw = json.loads((FIXTURE / "manifest.json").read_text(encoding="utf-8"))
    raw["frame"]["unitsPerMeter"] = 1
    with pytest.raises(RgpackValidationError, match="unitsPerMeter"):
        validate_manifest(raw)


def test_tampered_geometry_fails_validate_pack_dir(tmp_path: Path):
    m = load_pack(FIXTURE)
    files = {
        name: json.loads((FIXTURE / name).read_text(encoding="utf-8"))
        for name in GEOMETRY
    }
    out = tmp_path / "pack"
    save_pack(out, m, files)
    streets = json.loads((out / "streets.json").read_text(encoding="utf-8"))
    streets["centerline"][0]["lat"] = 99.0
    (out / "streets.json").write_text(json.dumps(streets), encoding="utf-8")
    with pytest.raises(RgpackValidationError, match="contentHash"):
        validate_pack_dir(out)
