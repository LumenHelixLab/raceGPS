# raceGPS Two-App Slice 1–2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship a versioned on-disk `rgpack` contract (schema + golden fixture + pytest round-trip), plus empty Workshop/Race Unreal game targets and a same-machine launcher that enforces one GPU owner.

**Architecture:** Python package `tools/rgpack` is the schema source of truth. Unreal module `raceGPSPack` provides a thin read-side API for later Race/Workshop use. One `.uproject` gains two Game targets (`raceGPSWorkshop`, `raceGPSRace`) that boot and log `app=workshop|race`. Launcher `raceGPS.bat` refuses Race while Workshop holds a lock under `Saved/raceGPS/`.

**Tech Stack:** Python 3.11 + pytest; Unreal Engine 5.7; C++20; Windows batch.

**Spec:** `docs/superpowers/specs/2026-09-24-racegps-two-app-gps-design.md` @ `de89789`  
**Worktree:** `C:\projects\raceGPS-grokbot-cleveland` on `grokbot/cleveland-integration`  
**Uproject:** `apps/unreal-akron-beta/raceGPSAkronBeta.uproject`

## Global Constraints

- Do **not** change GlobalDefaultGameMode / Akron default away from CruiseSprint / `CityId=akron-oh-beta-001`.
- Pack launches use **override** only.
- Frame A only: `unitsPerMeter=100`, Z-up, X=east, Y=north; WGS84 in pack files.
- Workshop writes packs; Race only reads; no live OSM inside Race.
- Only one of Workshop / Race may own the GPU (launcher lock).
- Cleveland G1–G5 is sample/reference; not a ship blocker.
- Fail-closed claims only when evidenced.
- EngineAssociation stays `"5.7"`. Existing `raceGPSAkronBeta` Game + Editor targets stay buildable.

## File map

| Path | Role |
|------|------|
| `tools/rgpack/__init__.py` | Package exports |
| `tools/rgpack/schema.py` | Dataclasses + validation |
| `tools/rgpack/hashutil.py` | SHA-256 over geometry files |
| `tools/rgpack/io.py` | load / save / validate_pack_dir |
| `tools/rgpack/launcher_lock.py` | GPU lock helper |
| `tests/fixtures/rgpack/minimal_v1/*` | Golden pack |
| `tests/test_rgpack_schema.py` | Schema + round-trip tests |
| `tests/test_racegps_launcher_lock.py` | Lock helper tests |
| `docs/contracts/RGPACK_v1.md` | Human contract |
| `apps/unreal-akron-beta/Source/raceGPSPack/*` | C++ read module |
| `apps/unreal-akron-beta/Source/raceGPSWorkshop/*` | Thin Workshop module |
| `apps/unreal-akron-beta/Source/raceGPSRace/*` | Thin Race module |
| `apps/unreal-akron-beta/Source/raceGPSWorkshop.Target.cs` | Workshop Game target |
| `apps/unreal-akron-beta/Source/raceGPSRace.Target.cs` | Race Game target |
| `apps/unreal-akron-beta/raceGPSAkronBeta.uproject` | Register modules |
| `apps/unreal-akron-beta/raceGPS.bat` | Launcher |

**Out of scope (later plans):** OSM bbox import, Race pawn on centerline, garage loadout, AI+EndRace, Cleveland re-export.

---

### Task 1: Python rgpack schema + golden fixture + round-trip tests

**Files:**
- Create: `tools/rgpack/__init__.py`, `schema.py`, `hashutil.py`, `io.py`
- Create: `tests/fixtures/rgpack/minimal_v1/manifest.json`
- Create: `tests/fixtures/rgpack/minimal_v1/streets.json`
- Create: `tests/fixtures/rgpack/minimal_v1/checkpoints.json`
- Create: `tests/fixtures/rgpack/minimal_v1/spawn.json`
- Create: `tests/fixtures/rgpack/minimal_v1/environment.json`
- Create: `tests/test_rgpack_schema.py`
- Create: `docs/contracts/RGPACK_v1.md`

**Interfaces:**
- Consumes: none
- Produces:
  - `validate_manifest(data: dict) -> Manifest` raises `RgpackValidationError`
  - `content_hash(pack_dir: Path, geometry_names: list[str]) -> str` (`sha256:` + hex)
  - `load_pack(pack_dir: Path) -> Manifest`
  - `save_pack(pack_dir: Path, manifest: Manifest, files: dict[str, object]) -> None`
  - `validate_pack_dir(pack_dir: Path) -> bool`
  - Golden `packId`: `fixture_minimal_v1`

- [ ] **Step 1: Write the failing test**

Create `tests/test_rgpack_schema.py`:

```python
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
```

- [ ] **Step 2: Run test — expect fail**

```powershell
cd C:\projects\raceGPS-grokbot-cleveland
if (Test-Path .\.venv-grokbot\Scripts\python.exe) {
  .\.venv-grokbot\Scripts\python.exe -m pytest tests/test_rgpack_schema.py -v
} else {
  python -m pytest tests/test_rgpack_schema.py -v
}
```

Expected: `ModuleNotFoundError: No module named 'rgpack'` (or fixture missing).

- [ ] **Step 3: Implement package + fixture**

`tools/rgpack/__init__.py`:

```python
"""raceGPS shared pack (rgpack) v1 — schema + disk IO."""

from .io import load_pack, save_pack, validate_pack_dir
from .schema import Manifest, RgpackValidationError, validate_manifest

__all__ = [
    "Manifest",
    "RgpackValidationError",
    "load_pack",
    "save_pack",
    "validate_manifest",
    "validate_pack_dir",
]
```

`tools/rgpack/schema.py`:

```python
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal, Optional


class RgpackValidationError(ValueError):
    pass


@dataclass(frozen=True)
class Frame:
    units_per_meter: int
    z_up: bool
    x_east: bool
    y_north: bool
    origin_lat: float
    origin_lon: float
    origin_alt_m: float


@dataclass(frozen=True)
class Source:
    type: Literal["osm", "gps_trace", "provisional_circuit"]
    attribution: str
    retrieved_at: str
    bbox: list[float]  # [minLon, minLat, maxLon, maxLat]


@dataclass(frozen=True)
class Certification:
    status: Literal["provisional", "certified"]
    notes: str


@dataclass(frozen=True)
class Defaults:
    environment_preset: Literal["Sunset", "Twilight", "Midnight"]
    loadout_id: Optional[str]


@dataclass(frozen=True)
class Manifest:
    schema_version: int
    pack_id: str
    display_name: str
    frame: Frame
    source: Source
    certification: Certification
    content_hash: str
    defaults: Defaults
    streets: str = "streets.json"
    checkpoints: str = "checkpoints.json"
    spawn: str = "spawn.json"
    environment: str = "environment.json"

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "schemaVersion": self.schema_version,
            "packId": self.pack_id,
            "displayName": self.display_name,
            "frame": {
                "unitsPerMeter": self.frame.units_per_meter,
                "zUp": self.frame.z_up,
                "xEast": self.frame.x_east,
                "yNorth": self.frame.y_north,
                "originLat": self.frame.origin_lat,
                "originLon": self.frame.origin_lon,
                "originAltM": self.frame.origin_alt_m,
            },
            "source": {
                "type": self.source.type,
                "attribution": self.source.attribution,
                "retrievedAt": self.source.retrieved_at,
                "bbox": list(self.source.bbox),
            },
            "certification": {
                "status": self.certification.status,
                "notes": self.certification.notes,
            },
            "contentHash": self.content_hash,
            "defaults": {"environmentPreset": self.defaults.environment_preset},
            "streets": self.streets,
            "checkpoints": self.checkpoints,
            "spawn": self.spawn,
            "environment": self.environment,
        }
        if self.defaults.loadout_id is not None:
            d["defaults"]["loadoutId"] = self.defaults.loadout_id
        return d


def _req(data: dict, key: str) -> Any:
    if key not in data:
        raise RgpackValidationError(f"missing required field: {key}")
    return data[key]


def validate_manifest(data: dict[str, Any]) -> Manifest:
    if not isinstance(data, dict):
        raise RgpackValidationError("manifest must be an object")
    schema_version = _req(data, "schemaVersion")
    if schema_version != 1:
        raise RgpackValidationError(f"unsupported schemaVersion: {schema_version}")

    frame_raw = _req(data, "frame")
    units = _req(frame_raw, "unitsPerMeter")
    if units != 100:
        raise RgpackValidationError("frame.unitsPerMeter must be 100 (Frame A)")
    for flag_key in ("zUp", "xEast", "yNorth"):
        if _req(frame_raw, flag_key) is not True:
            raise RgpackValidationError(f"frame.{flag_key} must be true (Frame A)")

    frame = Frame(
        units_per_meter=100,
        z_up=True,
        x_east=True,
        y_north=True,
        origin_lat=float(_req(frame_raw, "originLat")),
        origin_lon=float(_req(frame_raw, "originLon")),
        origin_alt_m=float(_req(frame_raw, "originAltM")),
    )

    source_raw = _req(data, "source")
    src_type = _req(source_raw, "type")
    if src_type not in ("osm", "gps_trace", "provisional_circuit"):
        raise RgpackValidationError(f"source.type invalid: {src_type}")
    bbox = _req(source_raw, "bbox")
    if not (isinstance(bbox, list) and len(bbox) == 4):
        raise RgpackValidationError("source.bbox must be [minLon,minLat,maxLon,maxLat]")
    source = Source(
        type=src_type,
        attribution=str(_req(source_raw, "attribution")),
        retrieved_at=str(_req(source_raw, "retrievedAt")),
        bbox=[float(x) for x in bbox],
    )

    cert_raw = _req(data, "certification")
    status = _req(cert_raw, "status")
    if status not in ("provisional", "certified"):
        raise RgpackValidationError(f"certification.status invalid: {status}")
    certification = Certification(status=status, notes=str(_req(cert_raw, "notes")))

    content_hash = _req(data, "contentHash")
    if not isinstance(content_hash, str) or not content_hash.startswith("sha256:"):
        raise RgpackValidationError("contentHash must start with sha256:")

    defaults_raw = _req(data, "defaults")
    preset = _req(defaults_raw, "environmentPreset")
    if preset not in ("Sunset", "Twilight", "Midnight"):
        raise RgpackValidationError(f"defaults.environmentPreset invalid: {preset}")
    defaults = Defaults(
        environment_preset=preset,
        loadout_id=defaults_raw.get("loadoutId"),
    )

    return Manifest(
        schema_version=1,
        pack_id=str(_req(data, "packId")),
        display_name=str(_req(data, "displayName")),
        frame=frame,
        source=source,
        certification=certification,
        content_hash=content_hash,
        defaults=defaults,
        streets=str(data.get("streets", "streets.json")),
        checkpoints=str(data.get("checkpoints", "checkpoints.json")),
        spawn=str(data.get("spawn", "spawn.json")),
        environment=str(data.get("environment", "environment.json")),
    )
```

`tools/rgpack/hashutil.py`:

```python
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
```

`tools/rgpack/io.py`:

```python
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
        if key not in files:
            raise RgpackValidationError(f"save_pack missing file payload: {key}")
        (pack_dir / name).write_text(
            json.dumps(files[key], indent=2, sort_keys=True) + "\n",
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
```

Geometry fixtures:

`tests/fixtures/rgpack/minimal_v1/streets.json`:

```json
{
  "centerline": [
    {"lat": 41.51722, "lon": -81.68306, "s": 0.0},
    {"lat": 41.5175, "lon": -81.6825, "s": 55.0},
    {"lat": 41.51722, "lon": -81.68306, "s": 110.0}
  ],
  "width_m": 8.0
}
```

`tests/fixtures/rgpack/minimal_v1/checkpoints.json`:

```json
{
  "track_id": "fixture_minimal_v1",
  "lap_count": 1,
  "gates": [
    {"index": 0, "name": "Start/Finish", "lat": 41.51722, "lon": -81.68306, "s": 0.0, "width_m": 10.0},
    {"index": 1, "name": "CP1", "lat": 41.5175, "lon": -81.6825, "s": 55.0, "width_m": 10.0}
  ]
}
```

`tests/fixtures/rgpack/minimal_v1/spawn.json`:

```json
{
  "player": {"lat": 41.51722, "lon": -81.68306, "heading_deg": 45.0},
  "grid": [
    {"slot": 0, "lat": 41.51722, "lon": -81.68306, "heading_deg": 45.0},
    {"slot": 1, "lat": 41.5172, "lon": -81.6831, "heading_deg": 45.0}
  ]
}
```

`tests/fixtures/rgpack/minimal_v1/environment.json`:

```json
{
  "default_preset": "Sunset",
  "presets": ["Sunset", "Twilight", "Midnight"]
}
```

After writing those four files, compute hash:

```powershell
cd C:\projects\raceGPS-grokbot-cleveland
python -c "import sys; from pathlib import Path; sys.path.insert(0,'tools'); from rgpack.hashutil import content_hash; print(content_hash(Path('tests/fixtures/rgpack/minimal_v1'), ['streets.json','checkpoints.json','spawn.json','environment.json']))"
```

Write `tests/fixtures/rgpack/minimal_v1/manifest.json` with that digest as `contentHash`:

```json
{
  "schemaVersion": 1,
  "packId": "fixture_minimal_v1",
  "displayName": "Minimal Fixture",
  "frame": {
    "unitsPerMeter": 100,
    "zUp": true,
    "xEast": true,
    "yNorth": true,
    "originLat": 41.51722,
    "originLon": -81.68306,
    "originAltM": 0.0
  },
  "source": {
    "type": "osm",
    "attribution": "OpenStreetMap contributors (fixture)",
    "retrievedAt": "2026-09-24T00:00:00Z",
    "bbox": [-81.684, 41.5165, -81.682, 41.518]
  },
  "certification": {
    "status": "provisional",
    "notes": "Synthetic golden fixture; not a real circuit."
  },
  "contentHash": "sha256:PASTE_COMPUTED_DIGEST",
  "defaults": {
    "environmentPreset": "Sunset"
  },
  "streets": "streets.json",
  "checkpoints": "checkpoints.json",
  "spawn": "spawn.json",
  "environment": "environment.json"
}
```

`docs/contracts/RGPACK_v1.md` — document the fields above, Frame A rules, hash algorithm (concat each geometry filename + NUL + file bytes + NUL in order streets→checkpoints→spawn→environment), Workshop-writes / Race-reads.

- [ ] **Step 4: Run tests — expect pass**

```powershell
cd C:\projects\raceGPS-grokbot-cleveland
python -m pytest tests/test_rgpack_schema.py -v
```

Expected: all PASS.

- [ ] **Step 5: Commit**

```powershell
git add tools/rgpack tests/fixtures/rgpack tests/test_rgpack_schema.py docs/contracts/RGPACK_v1.md
git commit -m "feat(rgpack): v1 schema, golden fixture, pytest round-trip"
```

---

### Task 2: Unreal `raceGPSPack` read-side module

**Files:**
- Create: `apps/unreal-akron-beta/Source/raceGPSPack/raceGPSPack.Build.cs`
- Create: `apps/unreal-akron-beta/Source/raceGPSPack/Public/raceGPSPack.h`
- Create: `apps/unreal-akron-beta/Source/raceGPSPack/Private/raceGPSPack.cpp`
- Create: `apps/unreal-akron-beta/Source/raceGPSPack/Public/RgpackManifest.h`
- Create: `apps/unreal-akron-beta/Source/raceGPSPack/Private/RgpackManifest.cpp`
- Modify: `apps/unreal-akron-beta/raceGPSAkronBeta.uproject` (add module)
- Modify: `apps/unreal-akron-beta/Source/raceGPSAkronBeta/raceGPSAkronBeta.Build.cs` (depend on `raceGPSPack`)

**Interfaces:**
- Consumes: Task 1 golden fixture on disk
- Produces: `bool TryLoadManifest(const FString& PackDir, FRgpackManifest& Out, FString& OutError)` on `URgpackBlueprintLibrary`
- `FRgpackManifest`: SchemaVersion, PackId, DisplayName, ContentHash, EnvironmentPreset

- [ ] **Step 1: Add module stubs that fail to link until implemented**

`raceGPSPack.Build.cs`:

```csharp
using UnrealBuildTool;

public class raceGPSPack : ModuleRules
{
    public raceGPSPack(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
        CppStandard = CppStandardVersion.Cpp20;
        PublicDependencyModuleNames.AddRange(new string[] {
            "Core", "CoreUObject", "Engine", "Json", "JsonUtilities"
        });
    }
}
```

Standard `IMPLEMENT_MODULE` in `raceGPSPack.cpp`. Add to uproject Modules:

```json
{
  "Name": "raceGPSPack",
  "Type": "Runtime",
  "LoadingPhase": "Default"
}
```

Add `"raceGPSPack"` to `raceGPSAkronBeta` PublicDependencyModuleNames.

- [ ] **Step 2: Build editor — expect fail until TryLoadManifest exists if referenced; otherwise build once stubs compile**

```powershell
cd C:\projects\raceGPS-grokbot-cleveland\apps\unreal-akron-beta
.\Build.bat raceGPSAkronBetaEditor Win64 Development
```

- [ ] **Step 3: Implement `TryLoadManifest`**

Parse `manifest.json` with `FJsonSerializer`. Require `schemaVersion==1`, `packId`, `contentHash` starting with `sha256:`, `defaults.environmentPreset` in {Sunset, Twilight, Midnight}. On missing file or bad JSON, return false and set OutError.

- [ ] **Step 4: Rebuild editor — expect SUCCESS**

- [ ] **Step 5: Commit**

```powershell
git add apps/unreal-akron-beta/Source/raceGPSPack apps/unreal-akron-beta/raceGPSAkronBeta.uproject apps/unreal-akron-beta/Source/raceGPSAkronBeta/raceGPSAkronBeta.Build.cs
git commit -m "feat(unreal): raceGPSPack module reads rgpack manifest"
```

---

### Task 3: Empty Workshop + Race game targets

**Files:**
- Create Workshop module under `Source/raceGPSWorkshop/` (Build.cs, Public/Private, `UWorkshopAppSubsystem` logs `app=workshop` in `Initialize`)
- Create Race module under `Source/raceGPSRace/` (same pattern, logs `app=race`)
- Create `Source/raceGPSWorkshop.Target.cs` and `Source/raceGPSRace.Target.cs` matching existing Target style (`BuildSettingsVersion.V6`, `EngineIncludeOrderVersion.Unreal5_7`)
- ExtraModuleNames: `raceGPSAkronBeta`, `raceGPSPack`, plus workshop or race module
- Register both modules in uproject
- **Do not** change DefaultEngine GlobalDefaultGameMode

- [ ] **Step 1: Write Target.cs files**

```csharp
using UnrealBuildTool;
using System.Collections.Generic;

public class raceGPSWorkshopTarget : TargetRules
{
    public raceGPSWorkshopTarget(TargetInfo Target) : base(Target)
    {
        Type = TargetType.Game;
        DefaultBuildSettings = BuildSettingsVersion.V6;
        IncludeOrderVersion = EngineIncludeOrderVersion.Unreal5_7;
        ExtraModuleNames.AddRange(new string[] {
            "raceGPSAkronBeta", "raceGPSPack", "raceGPSWorkshop"
        });
    }
}
```

(Race target identical with `raceGPSRace`.)

- [ ] **Step 2: Build before modules exist — expect fail**

```powershell
.\Build.bat raceGPSWorkshop Win64 Development
```

- [ ] **Step 3: Implement thin modules + subsystems that UE_LOG Display `app=workshop` / `app=race`**

- [ ] **Step 4: Build both targets — expect SUCCESS**

```powershell
.\Build.bat raceGPSWorkshop Win64 Development
.\Build.bat raceGPSRace Win64 Development
```

- [ ] **Step 5: Commit**

```powershell
git commit -am "feat(unreal): empty raceGPSWorkshop and raceGPSRace game targets"
```

---

### Task 4: Launcher GPU lock

**Files:**
- Create: `tools/rgpack/launcher_lock.py`
- Create: `tests/test_racegps_launcher_lock.py`
- Create: `apps/unreal-akron-beta/raceGPS.bat`

**Interfaces:**
- `acquire(lock_path, owner)`, `release(lock_path, owner)`, `is_held(lock_path) -> str | None`
- `raceGPS.bat workshop|race` — Race exits 1 if lock held by workshop

- [ ] **Step 1: Failing test**

```python
from pathlib import Path
import sys
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from rgpack.launcher_lock import LockError, acquire, is_held, release


def test_acquire_release(tmp_path: Path):
    lock = tmp_path / "gpu.lock"
    acquire(lock, "workshop")
    assert is_held(lock) == "workshop"
    with pytest.raises(LockError):
        acquire(lock, "race")
    release(lock, "workshop")
    assert is_held(lock) is None
    acquire(lock, "race")
```

- [ ] **Step 2: Run — expect import fail**

- [ ] **Step 3: Implement `launcher_lock.py` + `raceGPS.bat`**

Lock file: one line owner (`workshop` or `race`) and PID. Bat creates `Saved\raceGPS\`, writes lock for workshop, deletes on exit; race refuses if lock exists. Point exe paths at the same pattern existing `LaunchCleveland.bat` uses for locating the built binary / editor; document the resolved path in the commit body.

- [ ] **Step 4: pytest pass + manual refuse check**

```powershell
python -m pytest tests/test_racegps_launcher_lock.py -v
# Manual: echo workshop> Saved\raceGPS\gpu.lock then raceGPS.bat race → exit 1
```

- [ ] **Step 5: Commit**

```powershell
git add tools/rgpack/launcher_lock.py tests/test_racegps_launcher_lock.py apps/unreal-akron-beta/raceGPS.bat
git commit -m "feat(launcher): raceGPS.bat GPU lock for Workshop vs Race"
```

---

## Self-review

1. **Spec coverage:** Design §8 slices 1–2 covered. Slices 3–7 deferred. Frame A enforced. Akron default untouched. GPU split via lock.
2. **Placeholders:** Hash paste is an explicit compute step, not TBD.
3. **Names:** `fixture_minimal_v1`, `packId`, `contentHash`, `environmentPreset` consistent across Python and C++.

## Follow-on (separate plans)

3. Workshop bbox→OSM→minimal pack  
4. Race load pack→solo drive  
5. Garage loadout on Race boot  
6. AI+EndRace on arbitrary packs  
7. Re-export Cleveland as sample pack  

