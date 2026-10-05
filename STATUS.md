# STATUS

Canonical progress board. Reviewed at the start of every session. Updated after every correction. `ROADMAP.md` is not evidence.

Last updated: 2026-08-19 (Week 1 Compiler evidence accepted; Race-Loop source tests present, PIE/editor still closed)

---

## Live agents (Week 1)

| Agent | Assignment | State |
|---|---|---|
| Compiler | Emit checksummed `citypacks/steel-thread-001/` CityPack v2 | **evidence accepted** (Compiler-Test pytest, independent re-run) |
| Race-Loop | Prove `CruiseSprintGameMode` on a stock placeholder level | **source complete, editor-unverified** |

Everyone else stays **idle** except Compiler-Test (ran). Build/PIE stays idle: UE 5.5 editor was not used.

---

## Gates

| Gate | State | Evidence |
|---|---|---|
| Steel-thread CityPack v2 (2 roads, 1 junction, 1 building) | **PASSED** | Pack at `citypacks/steel-thread-001/`. `format=racegps-citypack-v2`. stats 2/1/1. Independent `python -m pytest tests/test_citypack_v2_steel_thread.py -q` → **10 passed**. Hash-repeat covered by those tests. XODR root `OpenDRIVE` from Python `generate_xodr`, not CARLA |
| Placeholder gameplay loop (spawn → drive → checkpoints → finish → results) | **PARTIAL** | `URaceLoopHarness` + `bUsePlaceholderCourse` (default true). Automation tests added: `raceGPS.Gameplay.RaceLoop.*` (4 cases). **Not executed**: no UE 5.5 editor / PIE this session. Not a Section 2.2 pass |
| Steel-thread drives in PIE | BLOCKED | Geometry-Import idle |
| Section 2.2 truth gate | OPEN / not passed | `AkronWorld.umap` still `.placeholder`. No Dev Editor compile, UMG binding, PIE, or packaged Win64 |
| Canonical world-gen path | Python compiler (default) | CARLA-Embedding idle |
| Canonical control plane | TypeScript backend (live) | Java-Backend idle |
| Control-Plane multiplayer-alpha | BLOCKED | Requires World-Gen PIE gate + Gameplay-Loop PIE, then merge on real `AkronWorld.umap` |

## Idle (do not start)

Geometry-Import, XODR Validation (esmini; XODR now exists but this agent is not Week 1), Citypack Schema, CARLA-Embedding, Vehicle/Physics, UI/UMG, Protocol/Signal, Challenge State-Machine, Persistence, Java-Backend, Asset-Adapters, Provenance, Security/Fuzzing, Build/PIE.

---

## Facts on the ground

- Engine: UE **5.5** (`apps/unreal-akron-beta/raceGPSAkronBeta.uproject`)
- Map: `Content/Maps/AkronWorld.umap.placeholder` only
- CityPack v2 steel-thread: `citypacks/steel-thread-001/`
- Recompile fixture: `python tools/universal-city-compiler/cli.py --fixture steel_thread`
- Placeholder loop: `ACruiseSprintGameMode` owns `URaceLoopHarness`; route id `placeholder_sprint`
- Workflow: `.grok/workflows/week-1.rhai` (smoke-checked; live Week 1 work was issued as one-task assignments instead of a second workflow run)

## Next assignment

Do **not** start Geometry-Import, CARLA, Java, or Control-Plane.

1. Build/PIE — only when a UE 5.5 Dev Editor is available: compile + PIE the placeholder loop. Packaged Win64 stays closed.
2. XODR Validation — esmini on `citypacks/steel-thread-001/roads.xodr` when Orchestrator opens it.
3. Geometry-Import — one intersection from the steel-thread pack, after Build/PIE can host it.
