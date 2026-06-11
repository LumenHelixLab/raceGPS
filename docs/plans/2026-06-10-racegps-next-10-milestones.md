# raceGPS — Next 10 Milestones (Phase 2)

> Date: 2026-06-10  
> Supersedes the execution queue after the June 8 viability plan (M1–M10).  
> Grounded in live repo state: **140 pytest passing**, v0.2.0 tag, CityHub + garageGPS + universal compiler shipped in source.

---

## Executive Summary

raceGPS is past “architecture demo” and into “product proof” territory. The C++ gameplay stack is broad (35+ classes), the Python toolchain is tested, and onboarding/menu/garage contracts are repo-verified. The single largest truth gap remains unchanged: **no real `AkronWorld.umap` and no verified PIE first drive**.

Phase 2 milestones close that gate first, then turn repo-complete systems into player-visible product, then prove scale (second city, community loop, LAN).

| Signal | State |
|--------|-------|
| Pytest suite | 140 passed (local, 2026-06-10) |
| June 8 M2 (premium menu) | Repo-side complete |
| June 8 M3 (onboarding flow) | Repo-side complete |
| June 8 M1 (first-drive proof) | **Editor-blocked** — `.umap.placeholder` only |
| June 8 M4–M10 | Not executed; folded into Phase 2 where still relevant |
| ROADMAP v0.2.0 items | Mostly source-ready, not editor-verified |
| CI | Python green; UE5 build workflow present but depends on runner UE install |

**Rule:** Do not treat M11+ as started until **Milestone 11** (first-drive proof) passes on a real editor session.

---

## Milestone 11 — Akron First-Drive Proof (Close the Gate)

**Goal:** Create real `Content/Maps/AkronWorld.umap` and prove the full play path in PIE.

**Why first:** Every other milestone is polish or scale on top of an unproven runtime.

**Deliverables:**
- Saved `AkronWorld.umap` with `CruiseSprintGameMode` assigned
- Successful compile via `apps/unreal-akron-beta/Build.bat`
- PIE smoke: main menu → route select → spawn → drive → hit checkpoints → tutorial (first run) → finish
- Screenshot/video capture + `docs/plans/ue-pie-smoke-evidence.md`

**Success test:**
- Fresh editor launch → controllable driving on an Akron route within 60 seconds
- No crash between Loading → Finished on both sample routes

**Verification:**
- Manual PIE checklist (`docs/plans/2026-06-08-ue-compile-risk-and-smoke-test.md`)
- `python -m pytest tests/test_racegps_onboarding_viability.py tests/test_levelspec.py -q`

**Carries forward:** June 8 Milestone 1

---

## Milestone 12 — Playable Vertical Slice (Drive Feel + Route + World)

**Goal:** Make the first drive feel like a product, not a test map.

**Deliverables:**
- **Vehicle identity pass:** Sedan / Sports / Truck × Arcade / Drift / Simulation presets feel distinct on Akron tarmac
- **Route readability pass:** spline materials, checkpoint spacing, start/finish clarity on both Akron routes
- **Basic world polish:** sky/lighting/fog/post-process, road framing, minimal environmental anchors at start zones
- **Race feedback loop:** post-race stats, medals, retry/next-route flow confirmed in live build (not dead-end)

**Success test:**
- A new player finishes a route without getting lost
- Three vehicle classes are distinguishable within 30 seconds of driving
- Finishing a route lands on a satisfying result screen with clear next action

**Verification:**
- `python -m pytest tests/test_racegps_garage_system.py tests/test_racegps_ux_polish.py -q`
- Manual playtest script (2 routes × 3 vehicle classes × 3 handling modes = 18 spot checks; document top 3 issues)

**Carries forward:** June 8 Milestones 4, 5, 6, 7

---

## Milestone 13 — UMG Blueprint Binding + Audio Pass

**Goal:** Connect C++ widget classes to real Editor assets and ship the documented sound layer.

**Deliverables:**
- Create/bind UMG blueprints from `Content/UI/**/*.txt` specs (MainMenu, Pause, Settings, Leaderboard, Loading, Tutorial, Save slots)
- Wire `NeonHUD` + minimap/compass to live data in PIE (no stub text)
- Import CC0 audio catalog (engine, UI, ambient) per audio design docs
- Smoke: menu navigation, pause, settings persist across restart

**Success test:**
- No visible “debug placeholder” copy in primary UI surfaces
- Settings changes survive game restart
- Vehicle audio responds to throttle/brake/collision in PIE

**Verification:**
- `docs/plans/2026-06-08-ux-polish-punch-list.md` checklist ≥ 90% checked
- `python -m pytest tests/test_racegps_ux_polish.py -q`

**Maps to:** ROADMAP v0.2.0 — UMG binding, sound design

---

## Milestone 14 — Visual FX + Materials Slice

**Goal:** Eliminate “greybox prototype” energy without waiting for full Cesium integration.

**Deliverables:**
- Road/sidewalk material pass (not flat grey ProceduralMesh default)
- Niagara hooks live: tire smoke, exhaust, checkpoint gate FX (ghost trail already referenced in source)
- Day/night readability pass on Akron routes at night
- Optional: evaluate Cesium/Google 3D Tiles spike as **documented spike only** if frame budget allows

**Success test:**
- Roads and gates read clearly at 120+ km/h
- At least two Niagara FX visible during normal driving
- Night run remains playable (checkpoint/route visible)

**Verification:**
- `python -m pytest tests/test_visuals.py -q`
- Capture 1080p footage at day + night on Route 1

**Maps to:** ROADMAP v0.2.0 — Niagara FX, materials, lighting

---

## Milestone 15 — garageGPS Runtime + Feature Surfaces

**Goal:** Promote garageGPS from toolchain to in-game vehicle identity.

**Deliverables:**
- Import `assets/car-kit/builds/*_001.unreal.json` manifests into UE content
- Vehicle selection screen uses garage builds (Street Coupe, Pursuit Sedan, Rally Hatch)
- Photo mode entry from pause menu (`PhotoModeController` wired)
- Drift score HUD hookup (`DriftScoreSystem` visible during Drift handling mode)
- Ghost replay toggle with clear UX entry (beat-your-own-line loop)

**Success test:**
- Player selects a garage car before launch and sees distinct visuals + handling
- Photo mode captures a screenshot to `Saved/Screenshots/`
- Ghost replay plays on second run of same route

**Verification:**
- `python -m pytest tests/test_garagegps.py tests/test_garagegps_extended.py -q`
- Manual: garage car → race → ghost → photo mode

**Maps to:** ROADMAP v0.3.0 — vehicle selection, photo mode; June 8 Milestone 8

---

## Milestone 16 — Installer + Clean-Machine Onboarding

**Goal:** Prove a non-developer can install and reach first drive.

**Deliverables:**
- Build `raceGPS-v0.2.0-Win64-Setup.exe` from packaged `Binaries/Win64/raceGPS.exe`
- Run `installer/WINDOWS-INSTALLER-VALIDATION-CHECKLIST.md` on a clean Windows 10/11 VM
- Preflight gate works in installed build (blocked states are actionable, not cryptic)
- Document contributor setup path (`scripts/setup-ue5-dev-env.ps1`) with success/fail notes

**Success test:**
- Clean VM: download installer → install → launch → onboarding → first drive (or explicit blocked verdict with fix steps)
- Uninstall removes install dir and registry keys

**Verification:**
- `python -m pytest tests/test_installer_integrity.py tests/test_racegps_onboarding_viability.py -q`
- Completed validation checklist committed under `docs/plans/`

**Maps to:** ROADMAP v1.0 installer item (early delivery)

---

## Milestone 17 — CityHub Client Integration Slice

**Goal:** Prove the community loop is real, not a separate server science project.

**Deliverables:**
- UE client (or thin launcher companion) fetches CityHub city list + route leaderboard
- Submit lap time to `POST /api/routes/:routeId/lap` after local race
- Display remote leaderboard alongside local JSON leaderboard
- One scripted demo: local race → upload → fetch → show rank

**Success test:**
- With CityHub running locally, finishing Akron Route 1 updates remote leaderboard
- Offline mode degrades gracefully (local-only leaderboard, no crash)

**Verification:**
- CityHub `npm test` or API integration test script
- `python -m pytest tests/test_gameplay.py -q` (extend with CityHub contract test if added)

**Carries forward:** June 8 Milestone 9

---

## Milestone 18 — Second City Proof (Cleveland)

**Goal:** Validate “drive your actual city” beyond Akron.

**Deliverables:**
- Compile `citypacks/cleveland_2.0km/` through universal city compiler CLI
- Generate level spec + import path for Cleveland map (or shared world loader with city switch)
- At least one drivable Cleveland route in PIE
- Document `tools/universal-city-compiler/` as the canonical non-Akron path

**Success test:**
- `python tools/universal-city-compiler/cli.py` produces valid citypack
- Player can select Cleveland from menu (or citypack loader) and complete one route

**Verification:**
- `python -m pytest tests/test_universal_compiler.py -q`
- `python tools/validate-citypack.py` on Cleveland output

**Maps to:** ROADMAP v1.0 — additional cities; semantic compiler generalization

---

## Milestone 19 — LAN Multiplayer Vertical Slice

**Goal:** Ship the smallest credible multiplayer moment.

**Deliverables:**
- `ULANSessionManager` + `ULANBrowserWidget` bound in UI
- Host/join on LAN (2 players minimum)
- Synchronized countdown + race start
- Post-race results for both players (times visible, local leaderboard updated)

**Success test:**
- Two machines on same subnet: host → join → both race → both finish → results shown
- Disconnect mid-race does not crash host

**Verification:**
- Manual LAN test protocol (2 PCs or 2 PIE instances if supported)
- Existing multiplayer source paths in `CruiseSprintGameMode.cpp` exercised

**Maps to:** ROADMAP v0.4.0 — LAN hosting, join/discovery, synchronized starts

---

## Milestone 20 — Commercial Readiness Review (Go / No-Go v1.0)

**Goal:** Force an explicit product verdict and produce the v1.0 punch list.

**Deliverables:**
- Acceptance checklist covering: onboarding → drive → result → ghost → installer → optional online
- Performance sanity on min-spec machine (GTX 1060 class): ≥ 30 FPS on Akron Route 1
- CI status report: pytest + UE build workflow green on `master`
- Ranked blocker list for Steam/v1.0 (Cesium, Steamworks, anti-cheat, content volume, etc.)
- Update `ROADMAP.md` and `CHANGELOG.md` with Phase 2 outcomes

**Success test — one of:**
- **GO:** Core fantasy lands; scale content + Steam
- **CONDITIONAL GO:** Core works; contained polish blockers (< 4 weeks)
- **NO-GO:** First drive fantasy fails; redesign scope required

**Verification:**
- Full smoke test recorded
- `python -m pytest tests/ -q` (full suite)
- Stakeholder sign-off section in this doc

**Carries forward:** June 8 Milestone 10

---

## Recommended Execution Order

| Priority | Milestone | Phase | Depends on |
|----------|-----------|-------|------------|
| P0 | 11. First-Drive Proof | Gate | UE 5.5 editor |
| P0 | 12. Playable Vertical Slice | Product | 11 |
| P1 | 13. UMG + Audio | Polish | 11 |
| P1 | 14. Visual FX + Materials | Polish | 11 |
| P1 | 15. garageGPS Runtime | Content | 11, 13 |
| P2 | 16. Installer E2E | Distribution | 11, 12 |
| P2 | 17. CityHub Client | Community | 11, 12 |
| P2 | 18. Second City (Cleveland) | Scale | 11, compiler |
| P3 | 19. LAN Multiplayer | Multiplayer | 11, 12 |
| P3 | 20. Commercial Review | Decision | 11–19 as applicable |

### Suggested grouping

- **Phase A (Gate):** 11  
- **Phase B (Akron product):** 12–15  
- **Phase C (Ship + community):** 16–18  
- **Phase D (Multiplayer + verdict):** 19–20  

---

## Relationship to June 8 Plan (M1–M10)

| June 8 Milestone | Phase 2 disposition |
|------------------|---------------------|
| M1 First-Drive Proof | **M11** — still blocking |
| M2 Premium Menu | Done (repo); validated in M11 PIE |
| M3 Onboarding Flow | Done (repo); validated in M16 installer |
| M4 Vehicle Identity | **M12** |
| M5 Route Readability | **M12** |
| M6 World Polish | **M12** + **M14** |
| M7 Race Result Loop | **M12** |
| M8 Ghost Slice | **M15** |
| M9 CityHub Slice | **M17** (expanded) |
| M10 Go/No-Go Review | **M20** |

---

## New Work Not in Original Plan

These repo additions justify milestones beyond the June 8 list:

- **garageGPS** custom car kit → M15
- **Universal city compiler** + Cleveland pack → M18
- **NSIS installer** + preflight → M16
- **LAN session manager** (source only) → M19
- **Photo mode / drift score** (C++ present, unverified) → M15
- **UMG `.txt` blueprint specs** → M13
- **CI/CD workflows** → validated in M20

---

## Optional Enabler (Not a Milestone)

**Graphify project brain** (`docs/plans/2026-06-10-graphify-knowledge-graph-integration-plan.md`): run as a parallel docs/tooling task to reduce re-entry cost. Does not substitute for M11 PIE proof.

---

## Approval Ask

Approve Milestones 11–20 as the Phase 2 roadmap for raceGPS Akron Beta → v1.0 path.

**Hard rule:** If M11 fails, pause M12–M20 and fix editor/world integration first.