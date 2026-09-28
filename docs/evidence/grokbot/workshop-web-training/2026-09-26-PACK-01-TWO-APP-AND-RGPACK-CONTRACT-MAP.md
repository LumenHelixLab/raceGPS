# Pack 01 — Two-app split + `.rgpack` contract map

**Lane:** Workshop Web (primary)  
**Date checked:** 2026-09-26  
**raceGPS weave:** packs as contract · Race lean/read-only · docs only — do not launch editor / install Overpass stacks under freeze

---

## 1. Two-app split (steal map)

| Piece | Path / role | Status (omni `raceGPS-grokbot-cleveland` + GH `grokbot/cleveland-integration`) |
|-------|-------------|----------------------------------------------------------------------------------|
| Spec / plan | `docs/superpowers/specs/2026-09-24-racegps-two-app-gps-design.md` @ `de89789`; plan `docs/superpowers/plans/2026-09-24-racegps-two-app-slice1-2.md` (also mirrored under shared scratch `racegps-plans/`) | Slice 1–2 goal: schema + empty targets + GPU lock |
| Python SoT | `tools/rgpack/` (`schema.py`, `hashutil.py`, `io.py`, `launcher_lock.py`, `__init__.py`) | **Present** on omni and GH tip |
| Human contract | `docs/contracts/RGPACK_v1.md` | **ACCEPTED** (Slice 1 Task 1) — Workshop writes / Race reads |
| Frame helper | `docs/contracts/SOURCE_TO_UNREAL_FRAME_v1.md` | Present beside RGPACK on omni |
| Golden fixture | `tests/fixtures/rgpack/minimal_v1/` (`manifest.json`, `streets.json`, `checkpoints.json`, `spawn.json`, `environment.json`) | Present on omni |
| C++ read module | `apps/unreal-akron-beta/Source/raceGPSPack/` | Present (Build.cs + Public/Private) |
| Workshop Game | `Source/raceGPSWorkshop/` + `raceGPSWorkshop.Target.cs` | Thin module present on omni + GH |
| Race Game | `Source/raceGPSRace/` + `raceGPSRace.Target.cs` | Thin module present on omni + GH |
| Launcher | `apps/unreal-akron-beta/raceGPS.bat` | Present on omni (`HAS_RACEGPS_BAT`) |
| Uproject | `apps/unreal-akron-beta/raceGPSAkronBeta.uproject` | Existing Akron targets stay; Workshop/Race added in slice |

### Role cut (do not blur)

| App | Allowed | Forbidden |
|-----|---------|-----------|
| **Workshop** | Write packs; OSM / Overpass / bbox tooling; local site/ops; GPU lock owner when editing | Shipping Race gameplay loop inside Workshop |
| **Race** | Read packs; play countdown→checkpoints→finish; lean arcade | Live OSM / Overpass / network map fetch; owning pack schema |

---

## 2. `.rgpack` v1 contract (Frame A)

Disk layout (defaults):

```
<pack_dir>/
  manifest.json
  streets.json
  checkpoints.json
  spawn.json
  environment.json
```

| Manifest rule | Value |
|---------------|-------|
| `schemaVersion` | `1` |
| Frame A | `unitsPerMeter=100`, `zUp`, `xEast`, `yNorth` all required |
| `source.type` | `osm` \| `gps_trace` \| `provisional_circuit` |
| `contentHash` | `sha256:` + hex over geometry (filename + NUL + bytes + NUL, order streets→checkpoints→spawn→environment) |
| `certification.status` | `provisional` \| `certified` |
| Defaults preset | `Sunset` \| `Twilight` \| `Midnight` |
| Write root (planned) | `Saved/raceGPS/packs/<packId>/` |

Python API (exports from `tools/rgpack/__init__.py`): `validate_manifest`, `load_pack`, `save_pack`, `validate_pack_dir`, `RgpackValidationError`, `Manifest`.

**Cite:** GH `docs/contracts/RGPACK_v1.md` + `tools/rgpack/__init__.py` on `grokbot/cleveland-integration`.

---

## 3. Overpass → rgpack CLI surface

| Layer | Intended surface | Present now? |
|-------|------------------|--------------|
| Schema / IO | `tools/rgpack` load/save/validate | **Yes** |
| Overpass fetch / bbox → streets centerline | CLI (later plan; slice 1–2 marks OSM bbox import **out of scope**) | **No** dedicated Overpass CLI in `tools/` listing (omni: rgpack, validate-citypack, batch-citypack, burke_ez_preview, … — no `overpass*` tool found) |
| Citypack legacy | `citypacks/cleveland/burke_gp_1997/` + EZ variant | **Yes** — different shape (XODR + racing_line + checkpoints; `id` not `packId`/`schemaVersion`) |
| 2D preview | `tools/burke_ez_preview/` | Generation / preview only — not rgpack export |

**Freeze-safe rule:** document the CLI contract; do not add network Overpass clients or new installs until Chris unlocks. Prefer fixture / offline citypack wrap as training truth.

### Citypack → rgpack gap (honest)

| Legacy citypack field | rgpack v1 |
|-----------------------|-----------|
| `id` | `packId` + `schemaVersion` |
| `xodr` + `racing_line` | `streets.json` centerline (WGS84) — not OpenDRIVE-as-SoT in v1 |
| `checkpoints.json` (gates) | `checkpoints.json` (gates + lap) — shape differs; need adapter |
| (often missing) spawn grid | `spawn.json` required |
| `environment.json` dressing pointers | `environment.json` presets list + preset default |
| no `contentHash` | fail-closed `contentHash` |
| `offline` / `carla_required` / `cesium_required` flags | certification + source provenance instead |

Burke EZ (`manifest_ez.json`, shared XODR) is **Course Architect data-plane**, not a passed `validate_pack_dir` evidence pack.

---

## 4. Local Workshop routes (auth-less)

| Route / surface | Intent | Status |
|-----------------|--------|--------|
| Local Workshop UI (map bbox, export, pack list) | Auth-less local-only ops; webmaster-clear routes | **Not found** as a shipped local site under this worktree evidence check — treat as **planned**, not live |
| Pack write path | `Saved/raceGPS/packs/<packId>/` | Contract-named; export proof = files + hash validate |
| Launcher | `raceGPS.bat` | GPU lock helper in `tools/rgpack/launcher_lock.py`; refuse Race while Workshop holds lock |
| Race read | Override pack load only | No GlobalDefaultGameMode flip |

**Clarity bar when UI lands:** every export action must show pack path, `packId`, `contentHash`, and pass/fail of `validate_pack_dir` — not just “Build succeeded.”

---

## 5. What counts as real export evidence vs empty target

### PASS (Workshop export / contract)

1. Golden fixture round-trip: `python -m pytest tests/test_rgpack_schema.py -v` all green (when Chris allows running tests; no editor required).
2. Or: a pack directory on disk with `manifest.json` + four geometry files where `validate_pack_dir` returns true and `contentHash` matches.
3. Contract doc matches code (`RGPACK_v1.md` ↔ `tools/rgpack`).
4. Evidence note under this folder (or PM-named path) with command transcript + pack path — fail-closed claims only.

### NOT PASS (empty / scaffolding)

| Claim | Why it fails |
|-------|--------------|
| `raceGPSWorkshop` / `raceGPSRace` Target.cs exists | Empty Game targets are slice scaffolding |
| Module boots and logs `app=workshop` | Boot ≠ pack export |
| G4/G5 UE build logs alone | Compile proof ≠ validated pack on disk |
| Burke citypack / EZ JSON present | Legacy shape; no `schemaVersion` / `contentHash` |
| Ribbon SVG / 2D preview | Generation / Course evidence, not Workshop export |
| NullRHI / black void Capture | Never PASS for any lane |
| “We’ll Overpass later” without CLI + fixture path | Theater |

### Local omni build logs (context only)

- `docs/evidence/grokbot/G4-racegpspack/` — `ue-editor-build.log` + exitcode (raceGPSPack wireup era)
- `docs/evidence/grokbot/G5-workshop-race-targets/` — `ue-build-workshop.log`, `ue-build-race.log`

These folders exist on **omni worktree**; they are **not** in the GH tip `docs/evidence/grokbot/` listing checked 2026-09-26 (tip still shows G1–G6 classic set + visual-floor). Treat as local evidence until mirrored / committed.

---

## 6. Explicit bans

| Ban | Why |
|-----|-----|
| Live OSM / Overpass inside **Race** | Standing lock — Race lean/read-only |
| Selling empty Workshop/Race targets as “two-app shipped” | Empty target ≠ export contract |
| Greenfield Cleveland / City Sample tourism map for streets | Prefer wrap + packs after playable race |
| Flipping GlobalDefaultGameMode from CruiseSprint | Pack / Showcase override only |
| Unattended editor / PIE / LaunchClevelandRace under freeze | Chris unlock required |
| Speculative Overpass / web stack installs under freeze | Cite-and-path only |
| Calling citypack XODR a v1 rgpack without adapter + hash | Fail-closed integrity |

---

## 7. Steal vs defer

| Steal now (docs / when unlocked) | Defer |
|----------------------------------|-------|
| `tools/rgpack` + `RGPACK_v1.md` + golden fixture | Live Overpass network importer |
| Citypack→rgpack field gap map (this pack) | Workshop auth-less local UI routes (until designed/shipped) |
| Launcher lock semantics | StreetMap + Landscape Combinator city rebuild |
| pytest round-trip as first reopen ship | Full OSM bbox product UX |

---

## Lane tips

### Workshop Web
Own schema, CLI contract, local site clarity, export evidence. Coordinate Course Architect on map truth (ribbons stay theirs; packs consume centerlines). Coordinate Build & Engine on Workshop packaging target when Chris unlocks builds — not before.

### Course Architect
Burke / EZ lines are inputs to a future adapter; do not rename citypack to rgpack without validation.

### Race Systems / Vehicle Arcade
Consume packs read-only after race base; do not embed Overpass.

### Unreal PM
Gate Workshop “done” on validated pack + transcript, not Target.cs presence. Mirror this folder into `Documents\raceGPS-handoff\workshop-web-training\` for Wave 1 QA.

### Build & Engine
G4/G5 logs are supporting; Workshop reopen ship is Python-first (Task 1 already on disk — verify tests, then Overpass CLI / UI next).

---

## Observable check — FUTURE (do not run editor now)

When Chris unlocks Workshop implementation (still no unattended `-game` spam):

1. `python -m pytest tests/test_rgpack_schema.py -v` → PASS  
2. Optional: adapter dry-run citypack→temp rgpack dir → `validate_pack_dir` true  
3. Land transcript + paths under this evidence folder  

**Empty target build ≠ PASS. Citypack without `contentHash` ≠ PASS. Live OSM in Race = FAIL.**

---

## Citations (checked 2026-09-26)

| Claim | Cite |
|-------|------|
| RGPACK_v1 ACCEPTED + Workshop writes / Race reads | GH `docs/contracts/RGPACK_v1.md` @ `grokbot/cleveland-integration` |
| Python package exports | GH `tools/rgpack/__init__.py` |
| Package files on disk | Omni `C:\projects\raceGPS-grokbot-cleveland\tools\rgpack\` — schema/io/hashutil/launcher_lock |
| Golden fixture files | Omni `tests\fixtures\rgpack\minimal_v1\` — five JSON files |
| Workshop/Race/Pack modules | Omni Source dirs + GH `apps/unreal-akron-beta/Source/raceGPSWorkshop/` listing |
| `raceGPS.bat` | Omni path exists |
| Slice plan + OSM bbox out of scope for slice 1–2 | Shared plan `2026-09-24-racegps-two-app-slice1-2.md` / in-tree superpowers plan |
| Legacy citypack shape | Local/GH `citypacks/cleveland/burke_gp_1997/manifest.json` (`id`, xodr, offline flags) + handoff EZ `manifest_ez.json` |
| G4/G5 local only | Omni evidence dirs present; GH tip evidence listing lacks `G4-racegpspack` / `G5-workshop-race-targets` / this training folder |
| Freeze / Wave 1 | `Documents\raceGPS-handoff\2026-09-26-WAVE1-SPECIALISTS.md` + freeze status docs |

Deepen status: beyond stub — contract map + Overpass gap + evidence vs empty-target rubric. Still **no** editor / Overpass installs under freeze.

---

## Soft-gap lock (Wave 1 QA — 2026-09-26)

Unreal PM FULL SET PASS soft gaps — **keep honest, do not close with theater**:

1. **Auth-less local Workshop routes** remain **planned / not on disk**. Route table deepens only when a design exists (docs). No invented URLs sold as live.
2. **Overpass CLI remains absent.** Fixture-first `tools/rgpack` + `pytest tests/test_rgpack_schema.py` is reopen #1. No Overpass install under freeze.
3. **Citypack→rgpack adapter is post-unlock.** The gap map in §3 is enough for training. Do not implement adapter or rebrand `burke_gp_1997` / EZ manifests as `RGPACK_v1` without `contentHash` + `validate_pack_dir`.

Soft gaps cleared for QA follow-up: README primary = this file; routes sibling = read-along only.

