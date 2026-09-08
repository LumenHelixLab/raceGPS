# DECISION_LEDGER

**Updated:** 2026-09-07 ET  
**Claim level:** OBSERVED / PROPOSED

## D-G1-001 — Bundle import
- Decision: Import bundle into C:\projects\racegps and create isolated worktree; leave showcase checkout on feature/cleveland-showcase-demo @ f2a8ecd.
- Result: REPRODUCED_LOCALLY. Worktree C:\projects\raceGPS-grokbot-cleveland @ 0ad434c on grokbot/cleveland-integration.

## D-G1-002 — Do not auto-merge showcase ↔ D1
- Observation: Histories diverged after merge-base ce18805.
  - D1-only tip lineage includes: 0ad434c, a341e87, b56b6c8, … brand/docs commits.
  - Showcase-only tip lineage includes: f2a8ecd and many Cleveland demo/runtime fixes (GameMode default, scale, lighting, spawn clearance, Chaos drive, V15 visuals, CARLA Charger, citypack tools, etc.).
- Diff magnitude: ~270 files, large generated LevelSpec churn; not a clean fast-forward either direction.
- Decision: **No auto-merge.** Document + cherry-pick plan only.

## Reconcile summary — f2a8ecd (showcase) vs 0ad434c (D1)

### Showcase has that D1 lacks (high value)
- Cleveland showcase race loop C++ (ClevelandShowcaseGameMode, ClevelandEnvironmentActor, LookDirector, RaceAIDriverController, RaceGridManager, RacingLineComponent, wheels)
- Content assets: BP_CheckpointGate, city buildings/water BPs, CARLA DodgeCharger materials/BP, Python content tools, LaunchCleveland.bat
- Citypacks: cleveland/burke_gp_1997, cleveland_5.0km, templates
- Docs: AGENTIC_HANDOFF_CLEVELAND, CLEVELAND_DEMO*, ENVIRONMENT, TRACK_PROVENANCE, VEHICLES, VISUAL_BAR, STACK
- Runtime config: GlobalDefaultGameMode=CruiseSprintGameMode, GameInstanceClass, diagnostics
- Scripts/tests for circuit/environment/water/endpoint snapping/AI control
- Map Akron5_0KmWorld.umap

### D1 has that showcase lacks (high value)
- Pinned Cleveland Burke OSM inputs under data/sources/cleveland-burke/
- Build orchestration + citypack_audit + compile_snapshot + test_build_orchestration + test_route_topology
- requirements-dev.txt
- D1 / next-five-gates evidence and plans (2026-09-07-cleveland-production-v5.1, D1_EXECUTION_REPORT, CLEVELAND_REFERENCE_CONTRACT)
- LumenHelix brand docs/site assets
- WorldContentInstaller.cpp and related importer/build.cs changes
- Regenerated Cleveland5.0KmWorld_LevelSpec.json (different content)

### Shared / conflict risk
- CruiseSprintGameMode, ChaosVehiclePawn, Road/Building mesh generators, RaceSessionManager, DefaultEngine.ini, uproject, universal-city-compiler, generated LevelSpecs
- Integration must reconcile C++ class sets carefully (showcase adds many Cleveland-specific classes D1 deleted relative to showcase tip).

## Proposed integration order (PROPOSED — do not execute until G1 closed + owner OK for merge work)
1. Keep grokbot/cleveland-integration rooted at 0ad434c as data/orchestration baseline.
2. Cherry-pick or manually port from showcase (f2a8ecd), in order:
   a. Config: GlobalDefaultGameMode + GameInstanceClass (DONE locally on worktree for G1 keep-rule)
   b. Non-conflicting docs from showcase CLEVELAND_* into docs/ (archive, do not delete D1 plans)
   c. Vehicle/race C++ modules that D1 removed but showcase needs for playable loop — only after compile baseline green
   d. Content/citypack assets via LFS/copy with provenance notes (not blind merge of generated giants)
   e. Showcase tests that still apply; quarantine obsolete fixtures
3. Prefer small topic commits on grokbot/cleveland-integration; no merge to master; no force-push.
4. Fast-forward only if ancestry becomes linear later; today it is NOT.

## D-G1-003 — GameMode keep
- Applied worktree-only DefaultEngine.ini GameMapsSettings with GlobalDefaultGameMode=CruiseSprintGameMode.
