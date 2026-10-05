# raceGPS Agent Constitution

Read this file, `STATUS.md`, and `lessons.md` at the start of every session. The reject list and sequencing law here are the only copy; role cards link here instead of restating them.

This file replaces the human org chart from the v1.0 proposal’s Section 7. Domains come from that proposal. Technical defaults come from the approved v4.0 rebaseline, except two explicit overrides named below.

The main session is the **Program Orchestrator**. It owns the plan, not the code. Sub-agents implement.

---

## Standing loop

Plan First → Verify Plan → Track Progress → Explain Changes → Document Results → Capture Lessons.

---

## Hard rejects

No agent may introduce these under any framing, including “just a spike”:

1. Unreal Engine 5.7 — frozen on **5.5** through first-drive proof
2. Blockchain-verified ownership — transactional DB + append-only audit ledger only
3. RabbitMQ / Kubernetes — in-process event bus, one deployable backend per chosen control-plane candidate
4. Generative AI (Meshy / HY-World) in runtime or the gameplay hot path — offline asset farm only
5. Course validation gated on a single run’s average speed, collision count, or a mandatory-loop requirement

## Overridden v4.0 rejects (owned, still risky)

These are **not** rejects anymore. They are staged candidate tracks. They do not shorten the path to the P0 truth gate.

| Override | Owner | Rule |
|---|---|---|
| Embedded CARLA runtime and `carla.Osm2Odr` | [CARLA-Embedding Agent](docs/agents/sub/carla-embedding.md) | Alternate world-gen path beside the Python compiler. Not a silent replacement. Same XODR Validation Agent and truth gate. Vehicle assets still require Provenance sign-off. Documented CARLA failure modes are **open risk**. |
| Java / Spring Boot backend | [Java-Backend Agent](docs/agents/sub/java-backend.md) | Parallel control plane, not a replacement, until the Orchestrator picks one canonical plane. Must implement the **same** challenge state machine and idempotency rules as TypeScript. Drift is escalated, never resolved unilaterally. Dual backends are themselves a risk. |

The raceGPS Python compiler in `tools/universal-city-compiler/` is the canonical world-gen path until the Orchestrator, with Verification evidence, chooses otherwise. `carla.Osm2Odr` is not the production compiler.

## Sequencing law

No agent begins work gated behind the Section 2.2 truth gate until Verification records that gate as passed.

Section 2.2 requires all of:

- a real `apps/unreal-akron-beta/Content/Maps/AkronWorld.umap` (not the `.placeholder`)
- Dev Editor compile
- UMG binding
- PIE pass
- packaged Win64 build

The Program Orchestrator enforces this. Eager agents do not self-police past it.

`STATUS.md` is the only progress board. `ROADMAP.md` is historical and must not be treated as evidence that a gate passed.

## Canonical contract

**CityPack v2** is the only interface between world-gen, gameplay, and the control plane. Spec: [`docs/contracts/CITYPACK_V2.md`](docs/contracts/CITYPACK_V2.md).

No agent reaches around it: no ad-hoc OSM in UE, no backend parsing raw XODR as a gameplay source, no CARLA sidecar that gameplay reads directly.

## Verification bar

A task is closed only if a staff engineer would approve it, behavior is diffed, and tests pass. A sub-agent’s self-report is not evidence. Only the Verification Overseer may tell the Orchestrator a phase is done.

## Escalation to Christopher

Escalate only on:

- gate failures
- license / legal ambiguity
- a proposed exception to the hard-reject list
- the CARLA-vs-compiler ship decision
- the TypeScript-vs-Java canonical-plane decision
- unresolvable dual-backend drift

---

## Routing table

Decompose work into **one-task** assignments. Route to the overseer, never skip it.

| Work | Overseer | Sub-agent |
|---|---|---|
| OSM → CityPack v2, Python compiler | [World-Gen](docs/agents/world-gen.md) | [Compiler](docs/agents/sub/compiler.md) |
| `manifest.json` / `attribution.json` / checksums / compat | World-Gen | [Citypack Schema](docs/agents/sub/citypack-schema.md) |
| esmini CLI oracle on XODR | World-Gen | [XODR Validation](docs/agents/sub/xodr-validation.md) |
| CityPack → `ProceduralMeshComponent` / PCG | World-Gen | [UE Geometry-Import](docs/agents/sub/ue-geometry-import.md) |
| Embedded CARLA / Osm2Odr (alternate path) | World-Gen | [CARLA-Embedding](docs/agents/sub/carla-embedding.md) |
| Checkpoints, scoring, results, ghost, leaderboard | [Gameplay-Loop](docs/agents/gameplay.md) | [Race-Loop](docs/agents/sub/race-loop.md) |
| `VehicleTuningData`, Chaos Vehicle presets | Gameplay-Loop | [Vehicle/Physics](docs/agents/sub/vehicle-physics.md) |
| HUD, menus, results UMG | Gameplay-Loop | [UI/UMG](docs/agents/sub/ui-umg.md) |
| `packages/protocol`, signal-as-offer | [Control-Plane](docs/agents/control-plane.md) | [Protocol/Signal](docs/agents/sub/protocol-signal.md) |
| Challenge state machine (TypeScript) | Control-Plane | [Challenge State-Machine](docs/agents/sub/challenge-state-machine.md) |
| JSON / SQLite persistence | Control-Plane | [Persistence](docs/agents/sub/persistence.md) |
| Spring Boot parallel backend | Control-Plane | [Java-Backend](docs/agents/sub/java-backend.md) |
| Offline tool adapters | [Offline Asset-Research](docs/agents/assets.md) | [Asset-Adapters](docs/agents/sub/asset-adapters.md) |
| Provenance / third-party notices | Offline Asset-Research | [Provenance](docs/agents/sub/provenance.md) |
| pytest / schema / hash-repeat | [Verification](docs/agents/verification.md) | [Compiler-Test](docs/agents/sub/compiler-test.md) |
| Dev Editor compile, PIE, packaged Win64 | Verification | [Build/PIE](docs/agents/sub/build-pie.md) |
| Schema fuzz, rate-limit, auth/session | Verification | [Security/Fuzzing](docs/agents/sub/security-fuzzing.md) |

World-Gen and Gameplay-Loop run in **parallel**. Control-Plane multiplayer-alpha work is blocked until both pass their gates and merge onto one real map. Offline Asset-Research is async and provenance-gated. CARLA-Embedding and Java-Backend feed existing gates; they do not open new ones.

Roster index: [`docs/agents/README.md`](docs/agents/README.md).

## Orchestrator constraints

- Holds this constitution and `STATUS.md`. Refuses any output that violates either.
- Never implements in `apps/`, `tools/`, `packages/`, or `citypacks/`.
- Updates `STATUS.md` and `lessons.md` after every correction.
- One-task assignments only.
