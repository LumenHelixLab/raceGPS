"""
Tests for assets/audio/import_pipeline.py

Run with: pytest tests/test_import_pipeline.py -v
"""

import json
import os
import shutil
import struct
import wave
from pathlib import Path

import pytest

# Ensure the assets/audio directory is importable
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "assets" / "audio"))

import import_pipeline as pipeline


# ---------------------------------------------------------------------------
# Fixtures (local temp to avoid Windows temp permission issues)
# ---------------------------------------------------------------------------

LOCAL_TMP = Path(__file__).resolve().parent / ".pytest_tmp"


def _make_local_tmp(name: str) -> Path:
    LOCAL_TMP.mkdir(parents=True, exist_ok=True)
    d = LOCAL_TMP / name
    if d.exists():
        shutil.rmtree(d)
    d.mkdir()
    return d


@pytest.fixture
def tmp_audio_dir() -> Path:
    """Return a temporary directory for raw audio."""
    return _make_local_tmp("raw")


@pytest.fixture
def tmp_output_dir() -> Path:
    """Return a temporary output directory."""
    return _make_local_tmp("imported")


@pytest.fixture
def tmp_project_path() -> Path:
    """Return a temporary project directory."""
    return _make_local_tmp("project")


def _write_test_wav(path: Path, duration_sec: float = 1.0, sample_rate: int = 44100, channels: int = 2):
    """Generate a tiny silent WAV file for testing."""
    n_frames = int(sample_rate * duration_sec)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(channels)
        w.setsampwidth(2)  # 16-bit
        w.setframerate(sample_rate)
        # silence
        w.writeframes(b"\x00" * (n_frames * channels * 2))


# ---------------------------------------------------------------------------
# Unit tests
# ---------------------------------------------------------------------------

class TestValidation:
    def test_valid_engine_idle(self):
        groups = pipeline.validate_filename("S_Engine_Idle_01.wav")
        assert groups is not None
        assert groups["category"] == "Engine"
        assert groups["subcategory"] == "Idle"
        assert groups["variant"] is None
        assert groups["index"] == "01"

    def test_valid_tire_skid(self):
        groups = pipeline.validate_filename("S_Tire_Skid_Asphalt_02.wav")
        assert groups is not None
        assert groups["category"] == "Tire"
        assert groups["subcategory"] == "Skid"
        assert groups["variant"] == "Asphalt"

    def test_valid_ui_click(self):
        groups = pipeline.validate_filename("S_UI_Click_01.wav")
        assert groups is not None
        assert groups["category"] == "UI"

    def test_valid_ogg_extension(self):
        groups = pipeline.validate_filename("S_Music_Menu_01.ogg")
        assert groups is not None
        assert groups["ext"] == "ogg"

    def test_invalid_missing_prefix(self):
        assert pipeline.validate_filename("Engine_Idle_01.wav") is None

    def test_invalid_category(self):
        assert pipeline.validate_filename("S_Foo_Bar_01.wav") is None

    def test_invalid_index(self):
        assert pipeline.validate_filename("S_Engine_Idle_1.wav") is None  # needs 2 digits

    def test_folder_mapping(self):
        groups = pipeline.validate_filename("S_Engine_Idle_01.wav")
        assert pipeline.get_output_folder(groups) == "Vehicle"

    def test_folder_mapping_ui(self):
        groups = pipeline.validate_filename("S_UI_Click_01.wav")
        assert pipeline.get_output_folder(groups) == "UI"


class TestLoopMetadata:
    def test_loopable_long(self, tmp_project_path: Path):
        src = tmp_project_path / "S_Ambience_City_Day_01.wav"
        _write_test_wav(src, duration_sec=5.0)
        meta = pipeline._generate_loop_metadata(src, 5.0)
        assert meta["loopable"] is True
        assert meta["loop_points"]["crossfade_seconds"] == 0.05

    def test_non_loopable_short(self, tmp_project_path: Path):
        src = tmp_project_path / "S_UI_Click_01.wav"
        _write_test_wav(src, duration_sec=0.1)
        meta = pipeline._generate_loop_metadata(src, 0.1)
        assert meta["loopable"] is False
        assert meta["loop_points"]["crossfade_seconds"] == 0.0


class TestProbeAudio:
    def test_probe_wav_python(self, tmp_project_path: Path):
        src = tmp_project_path / "S_Engine_Idle_01.wav"
        _write_test_wav(src, duration_sec=1.0, sample_rate=44100, channels=2)
        info = pipeline._parse_wav_info(src)
        assert info["sample_rate"] == 44100
        assert info["channels"] == 2
        assert pytest.approx(info["duration"], rel=0.01) == 1.0


class TestNormalizeAudio:
    @pytest.mark.skipif(not pipeline._ffmpeg_available(), reason="ffmpeg not available")
    def test_normalize_changes_format(self, tmp_project_path: Path):
        src = tmp_project_path / "S_Engine_Idle_01.wav"
        dst = tmp_project_path / "out" / "S_Engine_Idle_01.wav"
        _write_test_wav(src, duration_sec=1.0, sample_rate=22050, channels=1)
        pipeline.normalize_audio(src, dst)
        assert dst.exists()
        info = pipeline._parse_wav_info(dst)
        assert info["sample_rate"] == pipeline.TARGET_SAMPLE_RATE
        assert info["channels"] == 2


class TestStageValidate:
    def test_validate_directory(self, tmp_audio_dir: Path):
        _write_test_wav(tmp_audio_dir / "S_Engine_Idle_01.wav")
        _write_test_wav(tmp_audio_dir / "bad_name.wav")
        valid = pipeline.stage_validate(tmp_audio_dir)
        assert len(valid) == 1
        assert valid[0].name == "S_Engine_Idle_01.wav"


class TestStageNormalize:
    @pytest.mark.skipif(not pipeline._ffmpeg_available(), reason="ffmpeg not available")
    def test_normalize_directory(self, tmp_audio_dir: Path, tmp_output_dir: Path):
        _write_test_wav(tmp_audio_dir / "S_Engine_Idle_01.wav", duration_sec=2.0)
        _write_test_wav(tmp_audio_dir / "S_Tire_Skid_Asphalt_01.wav", duration_sec=2.0)
        outputs = pipeline.stage_normalize(tmp_audio_dir, tmp_output_dir)
        assert len(outputs) == 2
        # Check folder structure
        assert (tmp_output_dir / "Vehicle" / "S_Engine_Idle_01.wav").exists()
        assert (tmp_output_dir / "Tire" / "S_Tire_Skid_Asphalt_01.wav").exists()
        # Check sidecar metadata
        assert (tmp_output_dir / "Vehicle" / "S_Engine_Idle_01.wav.loop.json").exists()


class TestFullPipeline:
    def test_full_pipeline_creates_manifest(self, tmp_project_path: Path, tmp_output_dir: Path):
        catalog = {
            "version": "1.0.0",
            "project": "raceGPS",
            "format_standard": {"sample_rate_hz": 48000, "bit_depth": 24},
            "sources": [],
            "recommended_packs": [],
            "assets": [],
        }
        catalog_path = tmp_project_path / "catalog.json"
        with open(catalog_path, "w") as fh:
            json.dump(catalog, fh)
        pipeline.stage_full_pipeline(catalog_path, tmp_output_dir)
        manifest = tmp_output_dir / "manifest.json"
        assert manifest.exists()
        with open(manifest) as fh:
            data = json.load(fh)
        assert data["project"] == "raceGPS"


class TestCLI:
    def test_cli_validate(self, tmp_audio_dir: Path):
        _write_test_wav(tmp_audio_dir / "S_Engine_Idle_01.wav")
        rc = pipeline.main(["validate", "--input", str(tmp_audio_dir)])
        assert rc == 0

    @pytest.mark.skipif(not pipeline._ffmpeg_available(), reason="ffmpeg not available")
    def test_cli_normalize(self, tmp_audio_dir: Path, tmp_output_dir: Path):
        _write_test_wav(tmp_audio_dir / "S_Engine_Idle_01.wav")
        rc = pipeline.main(["normalize", "--input", str(tmp_audio_dir), "--output", str(tmp_output_dir)])
        assert rc == 0
        assert (tmp_output_dir / "Vehicle" / "S_Engine_Idle_01.wav").exists()
