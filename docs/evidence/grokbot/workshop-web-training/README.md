# Workshop Web — training (Wave 1)

**Lane:** Workshop Web (OSM / map builder UX, Overpass→`.rgpack` CLI contract, pack schema/versioning shared with Race, local Workshop site/ops)
**Owner:** Workshop Web under Prototyper; Unreal PM gates evidence
**Rule:** cite-and-path only for editor. No omni UnrealEditor, no PIE, no `LaunchClevelandRace`, no StreetMap / Landscape Combinator / greenfield city rebuilds until Chris unlocks.
**Checked:** 2026-09-27 · **Overpass→rgpack CLI proof landed** (offline fixture PASS; live tiny Burke PASS) · citypack→rgpack adapter = **post-unlock only**
**QA:** Wave 1 Pack 01 **PASS** — `docs/evidence/grokbot/agent-training/2026-09-26-WAVE1-TRAINING-QA.md`
**Worktree:** `C:\projects\raceGPS-grokbot-cleveland` · branch `grokbot/cleveland-integration` · UE **5.7** (editor not required for this proof)

## Files

| File | Role |
|------|------|
| [2026-09-27-OVERPASS-RGPACK-EXPORT-PROOF.md](./2026-09-27-OVERPASS-RGPACK-EXPORT-PROOF.md) | **Green-light export proof** — CLI transcript, pack path, contentHash, offline + live |
| [2026-09-26-PACK-01-TWO-APP-AND-RGPACK-CONTRACT-MAP.md](./2026-09-26-PACK-01-TWO-APP-AND-RGPACK-CONTRACT-MAP.md) | **Primary Pack 01** — contract map, citypack≠rgpack, export vs empty target, citations |
| [2026-09-26-PACK-01-TWO-APP-AND-RGPACK-ANNOTATIONS.md](./2026-09-26-PACK-01-TWO-APP-AND-RGPACK-ANNOTATIONS.md) | **Annotations** — steal/do-not, honest gaps, FUTURE export observables |
| [2026-09-26-PACK-01-RGPACK-AND-WORKSHOP-ROUTES.md](./2026-09-26-PACK-01-RGPACK-AND-WORKSHOP-ROUTES.md) | Read-along stub only — keep for PM lineage; do not treat as competing Pack 01 |

## Honest gaps (keep — do not paper over)

| Gap | Status |
|-----|--------|
| Auth-less local Workshop UI routes | **Planned / not found** on disk — deepen route table only when design lands (docs). Not a ship claim. |
| Overpass → rgpack CLI | **Shipped 2026-09-27** — `python -m rgpack export-overpass` (+ `tools/overpass_to_rgpack.py`). Offline fixture is freeze-safe SoT; live bbox optional / fail-closed. |
| Citypack → rgpack adapter | **Post-unlock only.** Do **not** claim Burke/EZ citypack is `validate_pack_dir` PASS without adapter. |
| G4/G5 evidence dirs | Local omni only vs GH tip — mirror when Chris wants parity; compile logs ≠ export PASS. |

## Hard constraints (raceGPS)

- **Packs are the contract.** Workshop **writes**; Race **only reads**. No live OSM / Overpass inside Race.
- Frame A only: `unitsPerMeter=100`, Z-up, X=east, Y=north; WGS84 in pack files (`SOURCE_TO_UNREAL_FRAME_v1`).
- Prefer finished OSS patterns as reference — **no** greenfield city rebuild; StreetMap / Landscape Combinator only after playable race unless Prototyper unlocks.
- `GlobalDefaultGameMode` stays **CruiseSprint**; pack launches use **override** only.
- One GPU owner: launcher lock under `Saved/raceGPS/` (Workshop vs Race).
- Empty Unreal Game targets / module stubs are **not** export evidence.
- Freeze: no editor / PIE / unattended launches for captures; CLI export proof OK.

## Scoreboard (Workshop lane)

Real progress = versioned on-disk pack `validate_pack_dir` PASS + contentHash + transcript. Offline Overpass fixture → pack is green-light. Booting `raceGPSWorkshop` alone remains scaffolding.

## Evidence path

- Training / cite-and-path: this folder
- Accepted contract: `docs/contracts/RGPACK_v1.md`
- Golden fixture: `tests/fixtures/rgpack/minimal_v1/`
- Offline Overpass fixture: `tests/fixtures/rgpack/overpass_burke_tiny/`
- CLI: `python -m rgpack export-overpass --fixture --out Saved\raceGPS\packs\<packId>`
- Local build logs (omni, not always on GH tip): `docs/evidence/grokbot/G4-racegpspack/`, `docs/evidence/grokbot/G5-workshop-race-targets/`

## Freeze posture

Stand down on editor / PIE / unattended launches. Overpass→rgpack **CLI** is unlocked for Workshop evidence; no StreetMap / city rebuild / citypack adapter until Chris unlocks those specifically.
