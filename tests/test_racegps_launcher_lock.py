"""Tests for raceGPS launcher GPU lock (Workshop vs Race)."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from rgpack.launcher_lock import LockError, acquire, is_held, release  # noqa: E402


def test_acquire_release(tmp_path):
    lock = tmp_path / "gpu.lock"
    acquire(lock, "workshop")
    assert is_held(lock) == "workshop"
    with pytest.raises(LockError):
        acquire(lock, "race")
    release(lock, "workshop")
    assert is_held(lock) is None
    acquire(lock, "race")


def test_release_wrong_owner_raises(tmp_path):
    lock = tmp_path / "gpu.lock"
    acquire(lock, "workshop")
    with pytest.raises(LockError):
        release(lock, "race")
    assert is_held(lock) == "workshop"
    release(lock, "workshop")
    assert is_held(lock) is None


def test_release_missing_is_ok(tmp_path):
    lock = tmp_path / "gpu.lock"
    assert not lock.exists()
    release(lock, "workshop")
    assert is_held(lock) is None


def test_is_held_none_when_missing(tmp_path):
    lock = tmp_path / "missing.lock"
    assert is_held(lock) is None


def test_acquire_same_owner_ok(tmp_path):
    lock = tmp_path / "gpu.lock"
    acquire(lock, "workshop")
    acquire(lock, "workshop")
    assert is_held(lock) == "workshop"
    release(lock, "workshop")
