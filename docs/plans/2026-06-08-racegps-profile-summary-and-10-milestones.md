# raceGPS Profile Summary + 10 Proposed Milestones

> Approval draft focused on smooth onboarding, basic functionality, and a clear viability verdict.

## Project Profile Summary

raceGPS is shaping up as a local-first street-racing product built around real-world city data, with Akron as the current proof city. The repo already supports a credible product stack:
- Unreal 5 gameplay client (`apps/unreal-akron-beta`)
- citypack/compiler pipeline for roads, routes, manifests, and checkpoints
- first-run onboarding + preflight system
- garage model with vehicle class + handling mode split
- route-based race flow with route splines and checkpoints
- leaderboard / replay / ghost / traffic systems
- CityHub backend for citypack distribution and route/community features

What the project wants to be:
- “Midnight Club on real roads”
- clean onboarding
- selectable citypacks
- route-based arcade/sim driving
- eventual community loop around routes, replays, leaderboards, and city sharing

What is already strong:
- architecture breadth
- clear citypack concept
- meaningful gameplay-support systems already in source
- local-first / modular framing
- now-improved onboarding, garage, and UX copy contract

What is still the main truth gap:
- the real Unreal editor world proof
- `Content/Maps/AkronWorld.umap` as a functioning saved map
- end-to-end PIE validation of: menu -> route -> spawn -> drive -> checkpoints -> tutorial

Bottom line:
- the concept is credible
- the repo is not vaporware
- but the product is not yet fully proven until the Akron world exists and the first drive works cleanly

## Current State Snapshot

| Area | Status | Notes |
|---|---|---|
| Citypack concept | Strong | Manifest + routes + generated level spec are present |
| Garage model | Stronger now | Vehicle class + handling mode split implemented |
| Onboarding/preflight | Stronger now | Better gating, persistence, and readiness messaging |
| UX/menu copy | Improved | More product-facing, less debug-like |
| Route/race contract | Present | Source path exists for load/spawn/checkpoints/tuning/tutorial |
| Unreal world proof | Blocked pending editor | Real `AkronWorld.umap` still the key truth step |
| Community/backend vision | Present | CityHub APIs exist, but not the immediate viability gate |

## Approval Goal

Approve a 10-milestone push that turns raceGPS from a promising systems repo into a clearly working or clearly blocked first-playable vertical slice.

---

## Proposed 10 Milestones

### Milestone 1 — Akron First-Drive Proof
Goal: Create the real `AkronWorld.umap` and prove the first drivable route works in PIE.

Deliverables:
- real saved AkronWorld map
- correct game mode assignment
- successful player spawn
- visible route spline and checkpoints
- drivable first run in editor

Success test:
- fresh launch reaches controllable driving within one minute

Why first:
- this is the single biggest truth gate in the whole project

### Milestone 2 — Main Menu Premium Pass
Goal: Turn the menu from functional prototype to premium launch surface.

Deliverables:
- bind title/version/vehicle/handling summary copy
- clean hero layout for selected route + car + handling mode
- clear “Drive Akron” CTA
- remove any leftover ambiguous/empty first-run states

Success test:
- a first-time user instantly understands what they are about to drive

### Milestone 3 — First-Run Onboarding Completion Flow
Goal: Make onboarding feel intentional and trustworthy instead of diagnostic.

Deliverables:
- bind step subtitles in blueprint
- show final readiness verdict message
- confirm save/profile persistence works after restart
- clean blocked-state messaging when preflight fails

Success test:
- onboarding ends in a simple yes/no launch decision with no confusion

### Milestone 4 — Vehicle Identity Pass
Goal: Make Sedan / Sports / Truck feel distinct even after handling-mode overlays.

Deliverables:
- editor tuning pass across the merged presets
- validate Arcade / Drift / Simulation per vehicle class
- remove “same car, different label” feeling

Success test:
- three vehicle classes feel visibly and physically different on first drive

### Milestone 5 — Route Readability Pass
Goal: Ensure players can actually read and follow the route at speed.

Deliverables:
- checkpoint spacing sanity pass
- spline visibility/material tuning
- better start/finish clarity
- corner readability pass on the two Akron sample routes

Success test:
- a new player can finish a route without getting lost or second-guessing the course

### Milestone 6 — Basic World Polish Pass
Goal: Eliminate “empty prototype map” energy.

Deliverables:
- minimal sky / lighting / fog / post process pass
- believable road framing
- basic environmental anchors around start areas
- cleaner sense of place for Akron proof routes

Success test:
- the world no longer feels like a blank test scene

### Milestone 7 — Race Result / Feedback Loop
Goal: Close the loop after a run so the player gets payoff.

Deliverables:
- route completion summary
- medal/placement feedback
- leaderboard display hookup for current route
- retry / next-drive flow

Success test:
- finishing a route produces a satisfying result screen instead of a dead end

### Milestone 8 — Replay / Ghost Slice
Goal: Add one “this is real” feature that raises confidence and stickiness.

Deliverables:
- ghost vehicle replay for at least one route
- local best-time replay path
- ghost toggle and simple UX entry point

Success test:
- player can beat their own line on repeat runs

### Milestone 9 — CityHub Integration Slice
Goal: Prove the project can grow beyond a single local toy.

Deliverables:
- basic city list / route leaderboard connectivity
- one working fetch path from client to CityHub or a tightly documented mocked integration path
- route/community architecture verified

Success test:
- external route/community loop is no longer theoretical

### Milestone 10 — Go / No-Go Vertical Slice Review
Goal: End ambiguity and force a product verdict.

Deliverables:
- one explicit acceptance checklist
- performance sanity on target machine
- onboarding-to-finish-run smoke test
- list of what still blocks commercial-grade confidence

Success test:
- final outcome is one of:
  - GO: first slice works and is worth scaling
  - CONDITIONAL GO: core works but needs contained polish
  - NO-GO: core fantasy is not landing and needs redesign

---

## Recommended Execution Order

| Priority | Milestone | Why |
|---|---|---|
| P0 | 1. Akron First-Drive Proof | Hardest truth gate |
| P0 | 2. Main Menu Premium Pass | First impression |
| P0 | 3. First-Run Onboarding Completion Flow | Smooth onboarding requirement |
| P1 | 4. Vehicle Identity Pass | Basic driving credibility |
| P1 | 5. Route Readability Pass | Basic functionality clarity |
| P1 | 6. Basic World Polish Pass | Removes prototype feel |
| P2 | 7. Race Result / Feedback Loop | Player payoff |
| P2 | 8. Replay / Ghost Slice | Confidence + retention |
| P2 | 9. CityHub Integration Slice | Future-proofing proof |
| P3 | 10. Go / No-Go Vertical Slice Review | Final product decision |

## Approval Ask

Approve these 10 milestones as the working roadmap for raceGPS Akron Beta.

Suggested execution grouping:
- Phase A: Milestones 1–3 (proof + onboarding + menu)
- Phase B: Milestones 4–6 (drive feel + route readability + world polish)
- Phase C: Milestones 7–9 (feedback loop + ghost + backend proof)
- Phase D: Milestone 10 (go/no-go review)

## My Recommendation

Approve the roadmap, but treat Milestone 1 as the real gate.
If Milestone 1 fails, do not continue pretending the rest matters yet.
If Milestone 1 succeeds, the rest becomes polishable product work rather than speculative architecture.
