# Agent roster

Constitution: [`AGENTS.md`](../../AGENTS.md). Live board: [`STATUS.md`](../../STATUS.md). Lessons: [`lessons.md`](../../lessons.md). Contract: [`docs/contracts/CITYPACK_V2.md`](../contracts/CITYPACK_V2.md).

Reject list and sequencing law live only in `AGENTS.md`. These cards add allowed / forbidden / idle-until for one role.

## Tier 0

- [Program Orchestrator](orchestrator.md)

## Tier 1 — overseers

| Overseer | Gate | Week 1 |
|---|---|---|
| [World-Gen](world-gen.md) | Steel-thread micro-citypack drives in PIE before Akron-scale work | Compiler live |
| [Gameplay-Loop](gameplay.md) | `CruiseSprintGameMode` on a placeholder box level | Race-Loop live |
| [Control-Plane](control-plane.md) | Blocked until both above gates pass and merge on real `AkronWorld.umap` | idle |
| [Offline Asset-Research](assets.md) | Per-asset provenance; async | idle |
| [Verification](verification.md) | Veto on every gate | Compiler-Test / Build/PIE wake on artifacts |

## Sub-agents

**World-Gen:** [Compiler](sub/compiler.md) · [Citypack Schema](sub/citypack-schema.md) · [XODR Validation](sub/xodr-validation.md) · [UE Geometry-Import](sub/ue-geometry-import.md) · [CARLA-Embedding](sub/carla-embedding.md)

**Gameplay-Loop:** [Race-Loop](sub/race-loop.md) · [Vehicle/Physics](sub/vehicle-physics.md) · [UI/UMG](sub/ui-umg.md)

**Control-Plane:** [Protocol/Signal](sub/protocol-signal.md) · [Challenge State-Machine](sub/challenge-state-machine.md) · [Persistence](sub/persistence.md) · [Java-Backend](sub/java-backend.md)

**Assets:** [Asset-Adapters](sub/asset-adapters.md) · [Provenance](sub/provenance.md)

**Verification:** [Compiler-Test](sub/compiler-test.md) · [Build/PIE](sub/build-pie.md) · [Security/Fuzzing](sub/security-fuzzing.md)
