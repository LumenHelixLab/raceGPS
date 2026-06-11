# raceGPS Onboarding Viability — 5 Milestones

> Focus: smooth first-run experience, basic gameplay properties actually functioning, and a clear yes/no answer on whether the Akron Beta is viable.

Goal
- Make first launch deterministic enough that the user can tell whether raceGPS fundamentally works.
- Separate code-ready work from Unreal Editor-only blockers.

Architecture
- Gate first-run through preflight + sane menu defaults.
- Prove the basic play path with source-level contracts and executable tests.
- Treat AkronWorld.umap as the single editor-only blocker, not a fuzzy repo-wide uncertainty.

Tech Stack
- UE5.5 C++ gameplay code
- Python/pytest repo contract tests
- JSON-backed settings / generated level spec / citypack files

---

## Milestone 1 — Deterministic Preflight Gate

Outcome
- First-run knows whether the install is minimally viable before play starts.

Done when
- Save directory check cannot false-pass.
- Config directory is created before writing first-run completion.
- Citypack integrity requires:
  - akron_semantic_manifest.json
  - akron_routes.json
  - generated/AkronWorld_LevelSpec.json
- Onboarding save captures:
  - preflight_can_launch
  - preflight_fail_count
  - preflight_warning_count

Verification
- Run: python -m pytest tests/test_racegps_onboarding_viability.py -q

---

## Milestone 2 — Menu/Garage Onboarding Contract

Outcome
- Main menu cannot silently proceed with invalid defaults.

Done when
- Route must be selected.
- Vehicle preset must resolve.
- Handling mode must resolve.
- Vehicle + handling selections persist.
- Two-axis garage contract remains green.

Verification
- Run: python -m pytest tests/test_racegps_garage_system.py -q

---

## Milestone 3 — Basic Race-Start Proof

Outcome
- The source contract proves the intended race-start sequence exists.

Required sequence
- LoadCityData()
- SpawnPlayerAtStart()
- SpawnCheckpoints()
- ApplyVehicleTuningToPlayer()
- TutorialSystem->StartTutorial()

Meaning
- If runtime still fails after this, the blocker is no longer missing logic intent; it is data/editor/runtime integration.

Verification
- Run: python -m pytest tests/test_racegps_onboarding_viability.py -q

---

## Milestone 4 — AkronWorld Editor Blocker Made Explicit

Outcome
- The project clearly distinguishes code-ready from editor-required work.

Editor-only blocker
- Content/Maps/AkronWorld.umap must exist as a real saved UE map.

Editor checklist
1. Open apps/unreal-akron-beta/raceGPSAkronBeta.uproject
2. Create/open Content/Maps/AkronWorld
3. Save real AkronWorld.umap
4. Add baseline environment shell:
   - DirectionalLight
   - SkyLight
   - sky/atmosphere
   - PostProcessVolume
   - fallback PlayerStart
5. PIE verify:
   - route loads
   - player spawns
   - checkpoints appear
   - tuning applies
   - tutorial appears
6. Save all

Pass condition
- A real AkronWorld.umap exists and PIE reaches drivable gameplay.

Fail condition
- If the map cannot be saved or PIE cannot spatially assemble route/checkpoints, the concept is blocked at editor/world integration.

---

## Milestone 5 — Clear Viability Gate

The idea is clearly working if all of these are true:
- Preflight passes with zero fails
- Menu can only start with valid route/vehicle/handling state
- Canonical AkronWorld level spec exists
- Race-start contract is present and tested
- AkronWorld.umap exists and PIE reaches a drivable checkpoint sequence

The idea is clearly not working yet if either of these is true:
- preflight_can_launch is false
- AkronWorld.umap still does not exist as a real saved map

Repo verification commands
- python -m pytest tests/test_levelspec.py tests/test_racegps_garage_system.py tests/test_racegps_onboarding_viability.py -q

Current status after this pass
- Milestone 1: code-side done
- Milestone 2: code-side done
- Milestone 3: source-contract proof done
- Milestone 4: still editor-blocked until AkronWorld.umap is saved in UE
- Milestone 5: now measurable instead of ambiguous
