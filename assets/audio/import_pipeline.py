#!/usr/bin/env python3
"""
raceGPS Audio Import Pipeline
=============================

Downloads, normalizes, validates, and organizes CC0 audio assets for UE5.

Dependencies:
    - Python 3.9+
    - ffmpeg (installed and on PATH)
    - requests (optional; for direct HTTP downloads)

Usage:
    python import_pipeline.py validate --input assets/audio/raw/
    python import_pipeline.py normalize --input assets/audio/raw/ --output assets/audio/imported/
    python import_pipeline.py full-pipeline --catalog assets/audio/catalog.json --output assets/audio/imported/
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import wave
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

TARGET_SAMPLE_RATE = 48000
TARGET_BIT_DEPTH = 24
TARGET_CHANNELS = 2  # stereo preferred for ambient; mono acceptable for UI

VALID_CATEGORIES = {
    "Engine", "Tire", "UI", "Music", "Ambience", "Weather", "Ghost",
    "Gear", "Turbo", "Exhaust", "Environment", "Vehicle",
}

# S_Category_Subcategory_Variant_Index.ext  (variant is optional)
NAME_RE = re.compile(
    r"^S_(?P<category>[A-Za-z]+)_"
    r"(?P<subcategory>[A-Za-z0-9]+)"
    r"(_(?P<variant>[A-Za-z0-9]+))?"
    r"_(?P<index>\d{2,3})"
    r"\.(?P<ext>wav|ogg)$",
    re.IGNORECASE,
)

CATEGORY_FOLDER_MAP = {
    "Engine": "Vehicle",
    "Gear": "Vehicle",
    "Turbo": "Vehicle",
    "Exhaust": "Vehicle",
    "Vehicle": "Vehicle",
    "Tire": "Tire",
    "UI": "UI",
    "Music": "Music",
    "Ambience": "Environment",
    "Environment": "Environment",
    "Weather": "Weather",
    "Ghost": "Ghost",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

class PipelineError(Exception):
    """Recoverable pipeline error."""


def _ffmpeg_available() -> bool:
    try:
        subprocess.run(
            ["ffmpeg", "-version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )
        return True
    except Exception:
        return False


def _probe_audio(path: Path) -> dict[str, Any]:
    """Use ffprobe to extract stream info."""
    cmd = [
        "ffprobe",
        "-v", "error",
        "-select_streams", "a:0",
        "-show_entries", "stream=sample_rate,bits_per_raw_sample,channels,duration",
        "-of", "json",
        str(path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    data = json.loads(result.stdout)
    stream = data.get("streams", [{}])[0]
    return {
        "sample_rate": int(stream.get("sample_rate", 0)),
        "bit_depth": int(stream.get("bits_per_raw_sample", 0) or 0),
        "channels": int(stream.get("channels", 0)),
        "duration": float(stream.get("duration", 0.0) or 0.0),
    }


def _parse_wav_info(path: Path) -> dict[str, Any]:
    """Pure-Python WAV probe (no external deps). Falls back to ffprobe."""
    try:
        with wave.open(str(path), "rb") as w:
            return {
                "sample_rate": w.getframerate(),
                "bit_depth": w.getsampwidth() * 8,
                "channels": w.getnchannels(),
                "duration": w.getnframes() / w.getframerate(),
            }
    except Exception:
        return _probe_audio(path)


def _normalize_name(filename: str) -> str:
    """Ensure consistent casing and extension."""
    base, ext = os.path.splitext(filename)
    return f"{base}{ext.lower()}"


def validate_filename(filename: str) -> dict[str, str] | None:
    """
    Validate naming convention.

    Returns dict with extracted groups on success, None on failure.
    """
    name = _normalize_name(filename)
    m = NAME_RE.match(name)
    if not m:
        return None
    groups = m.groupdict()
    if groups["category"] not in VALID_CATEGORIES:
        return None
    return groups


def get_output_folder(groups: dict[str, str]) -> str:
    """Map validated name groups to output folder."""
    cat = groups["category"]
    return CATEGORY_FOLDER_MAP.get(cat, cat)


def _generate_loop_metadata(src_path: Path, duration: float) -> dict[str, Any]:
    """Generate loop metadata JSON for seamless looping assets."""
    # Heuristic: if duration >= 2.0 s, assume loopable with crossfade
    loopable = duration >= 2.0
    return {
        "source_file": src_path.name,
        "duration_seconds": round(duration, 3),
        "loopable": loopable,
        "loop_points": {
            "start_seconds": 0.0,
            "end_seconds": round(duration, 3) if loopable else 0.0,
            "crossfade_seconds": 0.05 if loopable else 0.0,
        },
        "recommendation": (
            "Trim to stable section and align zero-crossings for seamless loop."
            if loopable
            else "One-shot asset; no loop required."
        ),
    }


def normalize_audio(
    src: Path,
    dst: Path,
    sample_rate: int = TARGET_SAMPLE_RATE,
    bit_depth: int = TARGET_BIT_DEPTH,
) -> None:
    """Normalize audio file to target spec using ffmpeg."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg",
        "-y",
        "-i", str(src),
        "-ar", str(sample_rate),
        "-ac", "2",  # stereo
        "-c:a", "pcm_s24le" if bit_depth == 24 else "pcm_s16le",
        "-af", "loudnorm=I=-23:LRA=7:tp=-2",  # broadcast loudness normalization
        str(dst),
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


# ---------------------------------------------------------------------------
# Pipeline stages
# ---------------------------------------------------------------------------

def stage_validate(input_dir: Path) -> list[Path]:
    """Validate all audio files in input directory. Returns valid paths."""
    valid: list[Path] = []
    invalid: list[str] = []
    for f in sorted(input_dir.iterdir()):
        if f.is_file() and f.suffix.lower() in (".wav", ".ogg"):
            groups = validate_filename(f.name)
            if groups:
                valid.append(f)
                print(f"[OK] {f.name} -> {get_output_folder(groups)}/")
            else:
                invalid.append(f.name)
                print(f"[FAIL] {f.name}")
    if invalid:
        print(f"\nValidation complete: {len(valid)} passed, {len(invalid)} failed.")
    else:
        print(f"\nValidation complete: {len(valid)} passed.")
    return valid


def stage_normalize(
    input_dir: Path,
    output_dir: Path,
    rename: bool = True,
) -> list[Path]:
    """Normalize all valid audio files and copy to structured output."""
    if not _ffmpeg_available():
        raise PipelineError("ffmpeg is not available on PATH. Install ffmpeg and retry.")

    valid = stage_validate(input_dir)
    outputs: list[Path] = []
    for src in valid:
        groups = validate_filename(src.name)
        if not groups:
            continue
        folder = output_dir / get_output_folder(groups)
        folder.mkdir(parents=True, exist_ok=True)
        dst_name = _normalize_name(src.name)
        dst = folder / dst_name
        print(f"Normalizing {src.name} -> {dst}")
        normalize_audio(src, dst)
        # Write sidecar metadata
        info = _parse_wav_info(dst)
        meta = _generate_loop_metadata(dst, info.get("duration", 0.0))
        meta_path = dst.with_suffix(dst.suffix + ".loop.json")
        with open(meta_path, "w", encoding="utf-8") as fh:
            json.dump(meta, fh, indent=2)
        outputs.append(dst)
    return outputs


def stage_full_pipeline(catalog_path: Path, output_dir: Path, raw_dir: Path | None = None) -> None:
    """
    Run the full pipeline using catalog.json as the manifest.

    This stage:
      1. Reads catalog.json
      2. Ensures output folder structure exists
      3. If --raw-dir is provided, normalizes files from it
      4. Writes a processed manifest with resolved paths
    """
    if not catalog_path.exists():
        raise PipelineError(f"Catalog not found: {catalog_path}")
    with open(catalog_path, "r", encoding="utf-8") as fh:
        catalog = json.load(fh)

    print(f"Loaded catalog '{catalog.get('project')}' v{catalog.get('version')}")

    # Ensure category folders exist
    for cat in set(CATEGORY_FOLDER_MAP.values()):
        (output_dir / cat).mkdir(parents=True, exist_ok=True)
        print(f"  {output_dir / cat}/")

    if raw_dir and raw_dir.exists():
        print("\n--- Normalization from raw dir ---")
        stage_normalize(raw_dir, output_dir)

    # Write resolved manifest
    manifest_path = output_dir / "manifest.json"
    manifest = {
        "project": catalog.get("project"),
        "version": catalog.get("version"),
        "format_standard": catalog.get("format_standard"),
        "output_root": str(output_dir.resolve()),
        "generated_at": "__TIMESTAMP__",  # caller can replace
        "notes": "Run 'python import_pipeline.py normalize --input <raw> --output <out>' to process raw recordings.",
    }
    with open(manifest_path, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2)
    print(f"\nManifest written: {manifest_path}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="import_pipeline.py",
        description="raceGPS CC0 audio import pipeline",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_validate = sub.add_parser("validate", help="Validate filenames in a directory")
    p_validate.add_argument("--input", "-i", type=Path, required=True, help="Input directory")

    p_normalize = sub.add_parser("normalize", help="Normalize audio to 48kHz/24bit")
    p_normalize.add_argument("--input", "-i", type=Path, required=True, help="Input directory")
    p_normalize.add_argument("--output", "-o", type=Path, required=True, help="Output directory")

    p_full = sub.add_parser("full-pipeline", help="Run full pipeline from catalog")
    p_full.add_argument("--catalog", "-c", type=Path, default=Path("catalog.json"), help="Catalog JSON path")
    p_full.add_argument("--output", "-o", type=Path, required=True, help="Output directory")
    p_full.add_argument("--raw-dir", "-r", type=Path, default=None, help="Optional raw audio dir")

    args = parser.parse_args(argv)

    try:
        if args.command == "validate":
            stage_validate(args.input)
        elif args.command == "normalize":
            stage_normalize(args.input, args.output)
        elif args.command == "full-pipeline":
            stage_full_pipeline(args.catalog, args.output, args.raw_dir)
    except PipelineError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1
    except subprocess.CalledProcessError as exc:
        print(f"[ERROR] External command failed: {exc}", file=sys.stderr)
        return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
