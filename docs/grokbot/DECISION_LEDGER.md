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

## D-G3-001 — Provisional Burke citypack port (PASS_PROVISIONAL)

- **When:** 2026-09-24T18:20:14 EDT
- **Decision:** Ship G3 as `PASS_PROVISIONAL` with `certification: blocked`. Port showcase `burke_gp_1997` into worktree without claiming surveyed 2006 geometry.
- **Why:** Dated georeferenced 2006 course plan is MISSING (G3-prep audit). OSM reconstruction of 1997-2007 / 2.106 mi / 10-turn clockwise family is the only coherent deliverable under fail-closed claim discipline.
- **Paths:** Canonical `citypacks/cleveland/burke_gp_1997/`; apps tree is a junction (single source of truth).
- **Constraints honored:** GlobalDefaultGameMode / CityId stay Akron; no historical title-sponsor branding; Akron audit exit 1 preserved; Frame A contract referenced, not violated.
- **Evidence:** `docs/evidence/grokbot/G3-cleveland-course-citypack/`

## D-G3-002 — Dual path coherence via junction

- **When:** 2026-09-24T18:20:14 EDT
- **Decision:** Keep one writable pack at repo-root `citypacks/…` and mirror under `apps/unreal-akron-beta/citypacks/…` with `mklink /J` rather than two copies.
- **Why:** Pytest/build script expect root `citypacks/`; Unreal loader also resolves `../../citypacks/<id>`. Avoid divergent hashes (showcase previously had identical duplicate trees).

## D-G3-003 — Skip UE rebuild for pack-only G3

- **When:** 2026-09-24T18:20:14 EDT
- **Decision:** Do not run a UE editor build for G3.
- **Why:** Gate touched pack files, Python scripts/tests, and docs only — no C++ or Default*.ini changes. One-build-at-a-time policy; optional PIE/XODR load proof deferred; OBSERVED file presence + pytest recorded instead.

## D-G4-001 - Slim ClevelandSoloGameMode (not full showcase stack)

- **When:** 2026-09-24T19:10:00-04:00
- **Decision:** Port a **solo** `AClevelandSoloGameMode` + `AClevelandLookDirector` (Sunset/Twilight/Midnight) instead of full showcase RaceGrid/AI/EndRace stack.
- **Why:** G4 bar is packaged/solo visual + playable drive; G5 owns 3-car AI + EndRace beta test run. Avoid blind-merge of showcase.
- **Launch:** `apps/unreal-akron-beta/LaunchCleveland.bat` map/GameMode override only; GlobalDefaultGameMode stays CruiseSprint; CityId stays akron-oh-beta-001.

## D-G4-002 - DayNight moon floor for night presets

- **When:** 2026-09-24T19:10:00-04:00
- **Decision:** Port `bMoonAtNight` + `NightMoonIntensity` into worktree `ADayNightCycle` (from showcase behavior).
- **Why:** Below-horizon sun + suppressed competing lights yields a black void; Midnight/Twilight need a declared moon directional (pitch -46, yaw 35 NE).

## D-G4-003 - Package SetActorLabel WITH_EDITOR guard

- **When:** 2026-09-24T19:10:00-04:00
- **Decision:** Guard `AActor::SetActorLabel` calls in `RuntimeCityLoader.cpp` with `#if WITH_EDITOR`.
- **Why:** Development `BuildCookRun` game target failed (exit 6) on editor-only API; not Cleveland-specific but blocks G4 packaging.

## D-G4-004 - Sunset still black = document, do not block

- **When:** 2026-09-24T19:10:00-04:00
- **Decision:** Accept PASS_PARTIAL with Sunset still at 0 luma after GPU retry; keep Twilight/Midnight stills + all three preset log proofs.
- **Why:** User raise prioritizes playable LaunchCleveland over screenshot API churn before G5 beta test run.
## D-G5-001 - Port showcase race stack (not Solo-only)

- **When:** 2026-09-24T19:56:00-04:00
- **Decision:** Port ClevelandShowcaseGameMode + RaceGridManager + RaceAIDriverController + RacingLineComponent + showcase ChaosVehiclePawn/wheels + DodgeCharger BP/Carla assets into worktree; keep G4 ClevelandSoloGameMode and LookDirector presets.
- **Why:** G5 bar is 3 physical Chaos cars + checkpoint lap + EndRace. Solo path alone cannot prove AI possession / EndRace.
- **Constraints:** Launch overrides GameMode only; GlobalDefaultGameMode/CityId unchanged; provisional Burke pack; branding Cleveland Historic Circuit.

## D-G5-002 - Playtest recovery snap for hairpin crawls

- **When:** 2026-09-24T19:56:00-04:00
- **Decision:** Raise AI recovery crawl threshold to 18 km/h, shorten recovery phases, and advance snap ~25 m along racing line; GameMode crawl stuck threshold 12 km/h. Playtest RequestExit after EndRace.
- **Why:** Attempt1 hung forever at T1 Vortex (~5 km/h) without EndRace. Fail-closed EndRace proof required recovery that unblocks lap completion under `-ClevelandAutoLap`.
- **Evidence:** attempt1 hairpin kill log + attempt2 `outcome=finished` report.

## D-G5-003 - G5 PASS on nullrhi EndRace (no package re-cook)

- **When:** 2026-09-24T19:56:00-04:00
- **Decision:** Claim G5 PASS from nullrhi `-game` ClevelandAutoLap EndRace; do not re-open G4 package cook hard-cap.
- **Why:** Mission exit bar is playable beta test run with EndRace proof; packaging was G4-owned and still blocked.
