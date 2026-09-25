from __future__ import annotations

import hashlib
from pathlib import Path


def content_hash(pack_dir: Path, geometry_names: list[str]) -> str:
    h = hashlib.sha256()
    for name in geometry_names:
        path = Path(pack_dir) / name
        if not path.is_file():
            raise FileNotFoundError(path)
        h.update(name.encode("utf-8"))
        h.update(b"\0")
        h.update(path.read_bytes())
        h.update(b"\0")
    return "sha256:" + h.hexdigest()
