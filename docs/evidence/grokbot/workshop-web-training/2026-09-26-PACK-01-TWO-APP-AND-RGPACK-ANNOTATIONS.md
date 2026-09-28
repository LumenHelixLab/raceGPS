# WW read-along — Pack 01 annotations (two-app + rgpack)

**Annotator:** Workshop Web  
**Date:** 2026-09-26  
**Parent pack (primary):** [2026-09-26-PACK-01-TWO-APP-AND-RGPACK-CONTRACT-MAP.md](./2026-09-26-PACK-01-TWO-APP-AND-RGPACK-CONTRACT-MAP.md)  
**Sibling stub:** [2026-09-26-PACK-01-RGPACK-AND-WORKSHOP-ROUTES.md](./2026-09-26-PACK-01-RGPACK-AND-WORKSHOP-ROUTES.md) (Prototyper seed — read-along only)  
**Mode:** study notes only — no Overpass install, no StreetMap, no editor, no citypack→rgpack adapter code, no greenfield city

### Parent cites (in-tree / GH / handoff)

| Cite | Why it matters |
|------|----------------|
| GH `docs/contracts/RGPACK_v1.md` @ `grokbot/cleveland-integration` | ACCEPTED Slice 1 — Workshop writes / Race reads; Frame A; contentHash fail-closed |
| GH `tools/rgpack/__init__.py` + omni `tools/rgpack/{schema,io,hashutil,launcher_lock}.py` | Python SoT API: `validate_manifest` / `load_pack` / `save_pack` / `validate_pack_dir` |
| Omni `tests/fixtures/rgpack/minimal_v1/` | Golden `fixture_minimal_v1` — five JSON files; round-trip bar |
| `docs/contracts/SOURCE_TO_UNREAL_FRAME_v1.md` | Race converts WGS84 once (100 uu/m, Z-up, X-east, Y-north) |
| Plan `2026-09-24-racegps-two-app-slice1-2.md` | Slice goal + OSM bbox import **out of scope** for slice 1–2 |
| Omni Source `raceGPSPack` / `raceGPSWorkshop` / `raceGPSRace` + Targets | Thin modules present — scaffolding ≠ export PASS |
| Omni `apps/unreal-akron-beta/raceGPS.bat` | GPU lock launcher companion to `launcher_lock.py` |
| Local `docs/evidence/grokbot/G4-racegpspack/` + `G5-workshop-race-targets/` | Build logs only; not on GH tip listing — compile ≠ pack validate |
| Citypack `citypacks/cleveland/burke_gp_1997/manifest.json` (+ EZ local) | Legacy shape — gap map only until post-unlock adapter |
| Wave 1 QA | `../agent-training/2026-09-26-WAVE1-TRAINING-QA.md` — WW Pack 01 PASS; soft gaps locked |

---

## What this pack is for (WW lane)

Own **two-app + pack-contract literacy**: Workshop authors versioned on-disk `.rgpack` directories; Race consumes them lean (no live OSM). Keep export evidence honest (validated pack + hash) versus empty Game targets / compile logs. Auth-less local Workshop routes stay planned until a design exists — do not invent URLs.

Do not turn Workshop into a Cleveland rebuild factory while Gate 1 / race-base still HOLD. Course Architect owns ribbons; World Environment owns hero mass; Build & Engine owns Win64 rebuild when unlocked.

---

## Steal (map to raceGPS)

1. **Two-app split** — Workshop = write packs under `Saved/raceGPS/packs/<packId>/` (planned). Race = read-only + Frame A conversion once. Never put Overpass/OSM network inside Race.
2. **RGPACK_v1 disk layout** — `manifest.json` + `streets.json` + `checkpoints.json` + `spawn.json` + `environment.json`. `schemaVersion` must be `1`. Frame A locks: `unitsPerMeter=100`, `zUp`, `xEast`, `yNorth`.
3. **Content hash fail-closed** — `sha256:` over geometry names in streets→checkpoints→spawn→environment order (`rgpack.hashutil.content_hash`). Tamper or missing file → `RgpackValidationError`.
4. **Python API surface** — Prefer `tools/rgpack` over inventing a second schema. Golden fixture `fixture_minimal_v1` is the round-trip bar via `pytest tests/test_rgpack_schema.py`.
5. **Fixture-first reopen** — When Chris unlocks Workshop implementation (still no unattended `-game`), ship/verify Task 1 pytest **before** Overpass CLI or local UI.
6. **Launcher lock literacy** — `launcher_lock.py` + `raceGPS.bat`: only one of Workshop / Race owns the GPU under `Saved/raceGPS/`. Pair with Build & Engine one-editor rule.
7. **Export vs empty-target rubric** — Real export = validated pack dir (+ transcript). Empty `raceGPSWorkshop`/`raceGPSRace` targets, G4/G5 UE logs alone, Burke citypack without `contentHash` = **not** PASS.
8. **Citypack gap as map only** — Legacy `id` / XODR / racing_line ≠ `packId` / `schemaVersion` / `streets.json`. Steal the field map from parent Pack 01; adapter stays **post-unlock**.
9. **Auth-less local ops (when designed)** — Local Workshop should stay reachable without production auth for authoring on omni. Document routes as local-dev contracts; deepen FAQ only when paths exist.

---

## Do not steal

- Live OSM / Overpass inside Race binaries.
- Selling empty Workshop/Race Target.cs or “boots and logs `app=workshop`” as two-app shipped.
- Greenfield City Sample / CARLA / tourism OSM rebuild sold as Workshop streets.
- StreetMap / Landscape Combinator **before** playable-race unlock (standing freeze).
- Flipping CruiseSprint `GlobalDefaultGameMode` from Workshop bats.
- Rebranding `burke_gp_1997` / EZ manifests as `RGPACK_v1` without adapter + `validate_pack_dir`.
- Overpass / web-stack installs under freeze.
- Owning Burke ribbon (CA) or Erie/skyline hero mass (WE) via Workshop mesh tools.
- NullRHI / void stills labeled Workshop export.

---

## Honest gaps / debt notes (docs only — keep)

| Gap | Read |
|-----|------|
| Auth-less Workshop UI routes | **Planned / not found** — no live route table to cite yet |
| Overpass → rgpack CLI | **Absent** — out of scope for slice 1–2; fixture-first reopen |
| Citypack → rgpack adapter | **Post-unlock** — gap map enough for training |
| G4/G5 evidence | Local omni only vs GH tip — mirror when Chris wants parity; still compile-only |
| Plan checkboxes | Slice plan tasks may still read unchecked in older mirrors — trust on-disk `tools/rgpack` + `RGPACK_v1` ACCEPTED over markdown theater |

---

## FUTURE observables (do not run editor / Overpass now)

When Chris unlocks Workshop implementation (docs/pytest first; no unattended Launch spam):

| Check | Pass looks like |
|-------|-----------------|
| Schema | `python -m pytest tests/test_rgpack_schema.py -v` all green |
| Export | Pack under `Saved/raceGPS/packs/<packId>/` (or fixture path) with `validate_pack_dir` true + matching `contentHash` |
| Evidence | Command transcript + pack path note under `docs/evidence/grokbot/workshop-web-training/` (or PM-named slot) |
| Race read | Race loads pack read-only; Frame A once; **no** OSM call in Race |
| Routes (later) | Auth-less local builder/export action documented with real path — not invented |
| Adapter (post-unlock) | Citypack→temp rgpack dry-run passes validate — only after Chris greens |
| Anti | No empty-target PASS; no Overpass-before-fixture; no greenfield city; no live OSM in Race |

Coordinate Build & Engine for any Win64 Workshop/Race target rebuild when unlocked. Coordinate Course Architect if consuming Burke centerlines into streets.json.

---

## Tie-back to known raceGPS debt (docs only)

- Soft gaps cleared 2026-09-26: README primary → TWO-APP contract map; routes sibling = stub; honest gaps + post-unlock adapter locked.
- Two-app slice held behind race base / Burke bar at freeze (`TECH-SPEC-SHEET` §G / handoff).
- G3 Cleveland citypack is a **provisional circuit pack**, not an excuse to rebuild via Overpass.
- Freeze: docs/training only until unlock.

---

## Hand-off

Unreal PM cross-cuts Wave 1 into `agent-training/2026-09-26-WAVE1-TRAINING-QA.md`. This annotations file is WW Pack 01 study depth. Ribbon continuity stays CA. Visual floor stays WE. Build & Engine owns editor/target ownership when reconnecting. Race Systems / Vehicle Arcade consume packs read-only after race base.
