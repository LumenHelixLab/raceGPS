"""GPU lock helper for raceGPS Workshop vs Race launchers."""
from __future__ import annotations

import os
import sys
from pathlib import Path


class LockError(Exception):
    """Raised when a lock cannot be acquired or released by the requested owner."""


def is_held(lock_path: Path) -> str | None:
    """Return the owner string if the lock file exists and is readable, else None."""
    try:
        text = lock_path.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        return None
    except OSError:
        return None
    if not text:
        return None
    # Format: "{owner} {pid}" — owner is the first token
    return text.split(None, 1)[0]


def acquire(lock_path: Path, owner: str) -> None:
    """Acquire lock by writing "{owner} {pid}". Raise LockError if another owner holds it."""
    if not owner or any(c.isspace() for c in owner):
        raise LockError(f"invalid lock owner: {owner!r}")
    current = is_held(lock_path)
    if current is not None and current != owner:
        raise LockError(f"lock held by {current!r}; cannot acquire as {owner!r}")
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    lock_path.write_text(f"{owner} {os.getpid()}\n", encoding="utf-8")


def release(lock_path: Path, owner: str) -> None:
    """Delete lock only if current owner matches. Missing file is ok. Wrong owner raises."""
    current = is_held(lock_path)
    if current is None:
        return
    if current != owner:
        raise LockError(f"lock held by {current!r}; cannot release as {owner!r}")
    try:
        lock_path.unlink()
    except FileNotFoundError:
        return


def _main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(
            "usage: launcher_lock.py acquire|release|is_held <lock_path> [owner]",
            file=sys.stderr,
        )
        return 2
    cmd = argv[1]
    if cmd == "is_held":
        if len(argv) != 3:
            print("usage: launcher_lock.py is_held <lock_path>", file=sys.stderr)
            return 2
        owner = is_held(Path(argv[2]))
        if owner is None:
            print("")
            return 0
        print(owner)
        return 0
    if cmd in ("acquire", "release"):
        if len(argv) != 4:
            print(f"usage: launcher_lock.py {cmd} <lock_path> <owner>", file=sys.stderr)
            return 2
        path = Path(argv[2])
        owner = argv[3]
        try:
            if cmd == "acquire":
                acquire(path, owner)
            else:
                release(path, owner)
        except LockError as exc:
            print(str(exc), file=sys.stderr)
            return 1
        return 0
    print(f"unknown command: {cmd}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv))
