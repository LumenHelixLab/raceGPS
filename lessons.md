# Lessons

Append-only. One entry per correction. Review at session start. Do not duplicate the reject list; that lives in `AGENTS.md`.

## 2026-08-19 — Founding the agent OS

- `ROADMAP.md` and the master handoff mark Cruise Sprint, XODR import, and HUD as shipped. Section 2.2 is not passed: there is no real `AkronWorld.umap`. Treat STATUS gates as the only progress board.
- Three CityPack shapes already exist (Akron pointer bundle, batch `racegps-citypack-v1` schema, TypeScript protocol pack). Reaching around them is how drift starts. Freeze steel-thread CityPack v2 and refuse new consumers of the other shapes.
- World-Gen and Gameplay-Loop were coupled in both prior documents. Nothing requires that. They run in parallel; Control-Plane waits for both.
- CARLA embedding and a Java/Spring Boot backend were v4.0 rejects and are now explicit overrides. They are candidate implementations feeding existing gates, not a faster P0. CARLA’s documented failure modes (OSM overflow ~50MB, GUI crashes on dense areas, no bridges/overpasses, inverted spline normals) stay **open** until evidenced otherwise.
- Dual backends (TypeScript live + Java parallel) are themselves a risk. Same state machine, same idempotency rules, drift escalated — never resolved by the Java agent unilaterally.
- A sub-agent saying “done” is not a gate pass. Verification evidence only.

## 2026-08-19 — Week 1 corrections

- Universal compiler did not emit XODR at all; `generate_xodr` lived only in `tools/akron-semantic-compiler/osm_to_xodr.py`. Steel-thread wired that function. The XODR `<header name="akron_oh_beta">` is leftover from that helper — cosmetic, not a stats/schema fail; fix when Schema/Compiler is next open, do not treat as CARLA.
- Three CityPack shapes remain in the repo. Steel-thread v2 is the new consumer contract. Do not add protocol or UE readers of v1.
- `ACruiseSprintGameMode` no-op’d spawn/checkpoints when `LoadedRoutes` was empty. Placeholder loop had to own `GetTotalCheckpoints()` via `URaceLoopHarness`.
- Loop automation cannot be claimed green without running it under UE 5.5. Source tests exist; editor-absent is **not passed**, not passed.
- `bUsePlaceholderCourse` defaults true so Week 1 does not depend on Akron files. Flip it when merging onto a real map or the steel-thread pack — do not leave it true through Section 2.2 by accident.
- Week 1 workflow `.grok/workflows/week-1.rhai` smoke-check fail-closes when canned output lacks evidence (`pack_passed=false`). That is correct. Do not “fix” the workflow to pass validate_only by treating missing evidence as success.
