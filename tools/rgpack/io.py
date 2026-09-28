from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .hashutil import content_hash
from .schema import Manifest, RgpackValidationError, validate_manifest

GEOMETRY_KEYS = ("streets", "checkpoints", "spawn", "environment")


def load_pack(pack_dir: Path) -> Manifest:
    pack_dir = Path(pack_dir)
    raw = json.loads((pack_dir / "manifest.json").read_text(encoding="utf-8"))
    return validate_manifest(raw)


def save_pack(pack_dir: Path, manifest: Manifest, files: dict[str, Any]) -> None:
    pack_dir = Path(pack_dir)
    pack_dir.mkdir(parents=True, exist_ok=True)
    names = [getattr(manifest, k) for k in GEOMETRY_KEYS]
    for key, name in zip(GEOMETRY_KEYS, names):
        # Accept filename keys (streets.json) or logical keys (streets).
        if name in files:
            payload = files[name]
        elif key in files:
            payload = files[key]
        else:
            raise RgpackValidationError(f"save_pack missing file payload: {key}")
        (pack_dir / name).write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    digest = content_hash(pack_dir, names)
    updated = Manifest(
        schema_version=manifest.schema_version,
        pack_id=manifest.pack_id,
        display_name=manifest.display_name,
        frame=manifest.frame,
        source=manifest.source,
        certification=manifest.certification,
        content_hash=digest,
        defaults=manifest.defaults,
        streets=manifest.streets,
        checkpoints=manifest.checkpoints,
        spawn=manifest.spawn,
        environment=manifest.environment,
    )
    (pack_dir / "manifest.json").write_text(
        json.dumps(updated.to_dict(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def validate_pack_dir(pack_dir: Path) -> bool:
    pack_dir = Path(pack_dir)
    m = load_pack(pack_dir)
    names = [getattr(m, k) for k in GEOMETRY_KEYS]
    for name in names:
        if not (pack_dir / name).is_file():
            raise RgpackValidationError(f"missing geometry file: {name}")
    digest = content_hash(pack_dir, names)
    if digest != m.content_hash:
        raise RgpackValidationError("contentHash mismatch")
    return True
