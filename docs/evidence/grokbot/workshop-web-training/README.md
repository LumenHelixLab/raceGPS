# Workshop Web — training (Wave 1)

**Lane:** Workshop Web (OSM / map builder UX, Overpass→`.rgpack` CLI contract, pack schema/versioning shared with Race, local Workshop site/ops)
**Owner:** Workshop Web under Prototyper; Unreal PM gates evidence
**Rule:** cite-and-path only. No omni UnrealEditor, no PIE, no `LaunchClevelandRace`, no clones / installs until Chris unlocks.
**Checked:** 2026-09-26 · **Soft gaps cleared:** honest gaps locked (auth-less routes planned; Overpass CLI absent); citypack→rgpack adapter = **post-unlock only** · **Annotations landed**
**QA:** Wave 1 Pack 01 **PASS** — `docs/evidence/grokbot/agent-training/2026-09-26-WAVE1-TRAINING-QA.md`
**Worktree (when game work reopens):** `C:\projects\raceGPS-grokbot-cleveland` · branch `grokbot/cleveland-integration` · UE **5.7**

## Files

| File | Role |
|------|------|
| [2026-09-26-PACK-01-TWO-APP-AND-RGPACK-CONTRACT-MAP.md](./2026-09-26-PACK-01-TWO-APP-AND-RGPACK-CONTRACT-MAP.md) | **Primary Pack 01** — contract map, Overpass gap, citypack≠rgpack, export vs empty target, citations |
| [2026-09-26-PACK-01-TWO-APP-AND-RGPACK-ANNOTATIONS.md](./2026-09-26-PACK-01-TWO-APP-AND-RGPACK-ANNOTATIONS.md) | **Annotations** — steal/do-not, honest gaps, FUTURE export observables |
| [2026-09-26-PACK-01-RGPACK-AND-WORKSHOP-ROUTES.md](./2026-09-26-PACK-01-RGPACK-AND-WORKSHOP-ROUTES.md) | Read-along stub only — keep for PM lineage; do not treat as competing Pack 01 |

## Honest gaps (keep — do not paper over)

| Gap | Status under freeze |
|-----|---------------------|
| Auth-less local Workshop UI routes | **Planned / not found** on disk — deepen route table only when design lands (docs). Not a ship claim. |
| Overpass → rgpack CLI | **Absent** — slice 1–2 marks OSM bbox import out of scope. Reopen #1 stays **fixture / `tools/rgpack` pytest**, not network Overpass. |
| Citypack → rgpack adapter | **Post-unlock only.** Gap map in Pack 01 is training truth; do **not** write adapter code or claim Burke/EZ citypack is `validate_pack_dir` PASS. |
| G4/G5 evidence dirs | Local omni only vs GH tip — mirror when Chris wants parity; compile logs ≠ export PASS. |

## Hard constraints (raceGPS)

- **Packs are the contract.** Workshop **writes**; Race **only reads**. No live OSM / Overpass inside Race.
- Frame A only: `unitsPerMeter=100`, Z-up, X=east, Y=north; WGS84 in pack files (`SOURCE_TO_UNREAL_FRAME_v1`).
- Prefer finished OSS patterns as reference — **no** greenfield city rebuild; StreetMap / Landscape Combinator only after playable race unless Prototyper unlocks.
- `GlobalDefaultGameMode` stays **CruiseSprint**; pack launches use **override** only.
- One GPU owner: launcher lock under `Saved/raceGPS/` (Workshop vs Race).
- Empty Unreal Game targets / module stubs are **not** export evidence.
- Freeze: no editor / PIE / unattended launches for captures; cite-and-path OK.

## Scoreboard (Workshop lane)

Real progress = versioned on-disk pack a pytest can round-trip, plus a documented path from fixture (then later bbox/Overpass) → validated pack dir. Booting `raceGPSWorkshop` and logging `app=workshop` alone is scaffolding, not a ship.

## Evidence path

- Training / cite-and-path: this folder
- Accepted contract: `docs/contracts/RGPACK_v1.md`
- Golden fixture: `tests/fixtures/rgpack/minimal_v1/`
- Local build logs (omni, not always on GH tip): `docs/evidence/grokbot/G4-racegpspack/`, `docs/evidence/grokbot/G5-workshop-race-targets/`
- Future OSM export proof (when unlocked): pack dir under `Saved/raceGPS/packs/<packId>/` + `pytest` / `validate_pack_dir` transcript + short README — not a target compile alone

## Freeze posture

Stand down on editor / PIE / unattended launches. Annotations pack landed (docs deepen only). No Overpass / StreetMap / adapter implementation until Chris unlocks.
