#!/usr/bin/env python3
"""Thin discoverable entry: Overpass JSON → rgpack v1.

Delegates to ``python -m rgpack export-overpass``. Prefer that form.
Race must not call Overpass; this is Workshop-only.
"""
from __future__ import annotations

import sys
from pathlib import Path

_TOOLS = Path(__file__).resolve().parent
if str(_TOOLS) not in sys.path:
    sys.path.insert(0, str(_TOOLS))

from rgpack.__main__ import main

if __name__ == "__main__":
    # Default subcommand when invoked as a script without one.
    argv = list(sys.argv[1:])
    if not argv or argv[0] not in ("export-overpass", "validate"):
        argv = ["export-overpass", *argv]
    raise SystemExit(main(argv))
