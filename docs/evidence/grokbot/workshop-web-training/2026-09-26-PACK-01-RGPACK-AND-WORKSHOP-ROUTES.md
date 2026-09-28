<!-- READ-ALONG STUB ONLY — primary Pack 01 is 2026-09-26-PACK-01-TWO-APP-AND-RGPACK-CONTRACT-MAP.md -->

# WW read-along -- Pack 01 (rgpack + Workshop routes)

**Annotator:** Workshop Web
**Date:** 2026-09-26
**Parent cites (in-tree / handoff):**
- `docs\contracts\RGPACK_v1.md` — ACCEPTED Slice 1 schema; Workshop writes, Race reads
- `docs\contracts\SOURCE_TO_UNREAL_FRAME_v1.md` — Frame A (100 uu/m, Z-up, X-east, Y-north)
- `tools\rgpack\` — `schema.py`, `io.py`, `hashutil.py`, `launcher_lock.py`
- `tests\fixtures\rgpack\minimal_v1\` + `tests\test_rgpack_schema.py`
- `docs\superpowers\plans\2026-09-24-racegps-two-app-slice1-2.md` — tasks still largely unchecked at freeze
- `docs\superpowers\specs\2026-09-24-racegps-two-app-gps-design.md`
- `apps\unreal-akron-beta\Source\raceGPSPack\Public\RgpackManifest.h` (+ Private `.cpp`)
- `docs\handoff\2026-09-25-TECH-SPEC-SHEET.md` §G — held two-app slice; race base first
- `docs\evidence\grokbot\G5-workshop-race-targets\` — build logs only, not playable PASS
**Mode:** study notes only — no live Overpass pulls as product claims, no StreetMap install, no editor, no greenfield city

---

## What this pack is for (WW lane)

Own the **two-app split** literacy: Workshop is the map builder that **writes** versioned `.rgpack` directories; Race is the lean player that **reads** packs and converts WGS84 once via Frame A. Keep auth-less local Workshop routes understandable. Know what counts as real export evidence versus an empty target scaffold.

Do not turn Workshop into a Cleveland rebuild factory while Gate 1 / race-base still HOLD.

---

## Steal (map to raceGPS)

1. **Two-app split** — Workshop = authoring (OSM/Overpass → pack files under `Saved/raceGPS/packs/<packId>/`). Race = consume-only. No live OSM network inside Race.
2. **RGPACK_v1 disk layout** — `manifest.json`, `streets.json`, `checkpoints.json`, `spawn.json`, `environment.json` (filenames overridable in manifest). `schemaVersion` must be `1`. Frame A fields locked (`unitsPerMeter=100`, `zUp`, `xEast`, `yNorth`).
3. **Content hash fail-closed** — `sha256:` digest over geometry filenames + NUL + bytes in streets → checkpoints → spawn → environment order (`rgpack.hashutil.content_hash`). Mismatch raises `RgpackValidationError`.
4. **Python API surface** — `validate_manifest`, `load_pack`, `save_pack`, `validate_pack_dir` from `tools\rgpack`. Golden fixture `fixture_minimal_v1` is the round-trip bar via pytest.
5. **Overpass → rgpack CLI surface (docs)** — Treat Overpass/OSM bbox import as a **Workshop writer pipeline** into rgpack, not as Race runtime. Cite plan/spec tasks; do not claim a greenfield Cleveland city from Overpass while freeze holds.
6. **Auth-less local Workshop routes** — Local Workshop should stay reachable without production auth for authoring loops on omni. Document routes as local-dev contracts; do not invent cloud auth as a Gate 1 dependency.
7. **Unreal read module already sketched** — `raceGPSPack` / `RgpackManifest` exists under the Akron Beta source tree. Race reads; Workshop does not push live network into the game target.
8. **Launch override only** — Pack launches override GameMode / citypack via launcher; never rewrite GlobalDefaultGameMode away from CruiseSprint.

---

## What counts as real export evidence vs empty target

| Evidence | Real? | Notes |
|----------|-------|-------|
| `pytest tests/test_rgpack_schema.py` green + fixture pack on disk | **Yes (schema)** | Contract integrity only |
| Pack dir under `Saved/raceGPS/packs/<packId>/` with valid hash + non-empty geometry | **Yes (export)** | Workshop write proof |
| `docs\evidence\grokbot\G5-workshop-race-targets\ue-build-*.log` alone | **No** | Target may compile empty; not playable race |
| Empty `raceGPSWorkshop` / `raceGPSRace` target stubs | **No** | Plan held work, not product PASS |
| Overpass dump without rgpack validate | **No** | Raw OSM ≠ pack |
| StreetMap / Landscape Combinator screenshots | **No (pre-unlock)** | After playable race unless Chris unlocks |
| NullRHI / void stills labeled Workshop | **Never** | FAIL |

---

## Do not steal

- Greenfield City Sample / CARLA / tourism OSM rebuild sold as raceGPS Cleveland.
- StreetMap or Landscape Combinator **before** playable race unlock (standing freeze).
- Live OSM inside Race binaries.
- Flipping CruiseSprint GlobalDefault from Workshop bats.
- Claiming plan markdown checkboxes as shipped product.
- Owning Burke ribbon (CA) or Erie/skyline hero mass (WE) via Workshop mesh tools.

---

## FUTURE observables (do not run now)

| Check | Pass looks like |
|-------|-----------------|
| Schema | `validate_pack_dir` on a real pack; pytest fixture still green |
| Export | Non-empty streets/checkpoints/spawn/environment; contentHash matches |
| Routes | Auth-less local Workshop route returns builder UI / export action without prod auth |
| Race read | Race loads pack read-only; Frame A conversion once; no OSM call in Race |
| Evidence | Pack tree + validate log under `docs\evidence\grokbot\` with WW note |
| Anti | No empty-target PASS; no StreetMap-before-race; no greenfield city |

---

## Tie-back to known raceGPS debt (docs only)

- Two-app slice plan tasks largely unchecked at freeze (`TECH-SPEC-SHEET` §G).
- Burke / Showcase race-base remains the human Gate 1 path; Workshop streets are sequenced after.
- G3 Cleveland citypack is a **provisional circuit pack**, not an excuse to rebuild via Overpass.
- Freeze: docs/training only until unlock.

---

## Hand-off

Unreal PM QA stub: `../agent-training\2026-09-26-WAVE1-TRAINING-QA.md`. Build & Engine compiles targets when unlocked; Workshop Web owns contract literacy and route/export evidence definitions.
