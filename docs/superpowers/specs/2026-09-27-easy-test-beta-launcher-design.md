# Easy Test Beta — Desktop Launcher Design

**Date:** 2026-09-27  
**Owner:** Prototyper (overseer) / Unreal PM (day-to-day)  
**Status:** Draft for Chris review — do not implement until approved  
**Worktree:** `C:\projects\raceGPS-grokbot-cleveland` (`grokbot/cleveland-integration`)

## Goal

Ship an easier keep-alive **test beta** that does not require re-cooking Unreal for every polish pass: a desktop launcher for install/setup/settings that starts **Race** and **Workshop**, with real UI polish, combining Cleveland race-base content with Akron map-compiler tools. Prefer **robust** solutions backed by **modern open-source research at every stage** over clever one-offs.

## Decisions locked with Chris (2026-09-27)

| Topic | Choice |
|-------|--------|
| Shell | Small desktop launcher (install/setup/settings) that starts Race + Workshop |
| Race modes | Package mode default for testers; Dev mode for team; same settings shell |
| Akron + Cleveland | Cleveland = packaged Race content (visuals + playable loop); Akron = `akron-semantic-compiler` + `universal-city-compiler` into Workshop under rgpack; **no** full Akron Unreal shell merge |
| Milestone bar | Launcher MVP + polished Workshop onboarding/routes + in-Race HUD/settings in **one** milestone |
| Approach | **A — Parallel three-lane** under Unreal PM |
| Quality bar | Robust; modern OSS researched at every stage; PM researches when not managing; when PM stops managing, a **research & training bot** spins up |

Data-flow / success-criteria widgets were skipped — defaults below apply: Race `.rgpack` load is **later** (not required for launcher MVP); Package mode may stay "awaiting build" until cook unlock.

## Architecture

```
┌─────────────────────────────────────┐
│  raceGPS Launcher (Electron/Vite)   │
│  onboarding · paths · settings      │
│  Package / Dev toggle · launch      │
└───────────┬─────────────┬───────────┘
            │             │
            ▼             ▼
   ┌──────────────┐  ┌────────────────────┐
   │ Race         │  │ Workshop (local)   │
   │ Cleveland    │  │ routes + semantic  │
   │ race-base    │  │ → .rgpack          │
   └──────────────┘  └────────────────────┘
```

- Launcher owns first-run onboarding, path discovery, persistent settings, Package vs Dev.
- Workshop owns map/tooling UI and Akron compilers under `docs/contracts/RGPACK_v1.md`.
- Race owns Cleveland playable loop + HUD/settings; `GlobalDefaultGameMode` stays CruiseSprint; Cleveland via map/game-mode overrides only.
- Prototyper overseer: goal locks only. Unreal PM sequences lanes and FAIL-CLOSED evidence.

### Out of scope (this milestone)

- Full Akron Unreal shell merge / `racegps-reconcile` promotion / master merge / blind robocopy
- StreetMap + Landscape Combinator tourism Cleveland
- Unattended Gate 1 / LaunchClevelandRace spam
- Claiming NullRHI or black void as visual PASS

## Components

### Launcher (Workshop Web)

- First-run wizard: Race package path, Workshop path, GPU/adapter note, Package vs Dev default
- Home: Play Race, Open Workshop, Settings, status chips (paths OK / missing package / Dev bat found)
- Settings: mode, paths, reveal logs, reset defaults
- Does **not** cook Unreal — validate + launch only
- Tech lean: **Electron + Vite** (web UI craft shared with Workshop polish). Alternative Tauri only if Electron blocked.

### Workshop (Workshop Web)

- Auth-less local routes: landing → create/open pack → Overpass/semantic compile → validate rgpack → export
- Spine: `tools/akron-semantic-compiler/` (reference) + `tools/universal-city-compiler/` (expansion)
- Reuse offline Burke fixture / `python -m rgpack` paths already proven
- Honest empty states; citypack→rgpack adapter remains post-unlock soft item

### Race (Race Systems + Vehicle Arcade as needed)

- HUD pass: speed, race state, checkpoint/lap clarity at arcade speed
- In-Race settings: graphics presets, camera if present, input hints, apply/resume
- Borrow **patterns** from Akron `MainMenuWidget` / `SettingsWidget` / `OnboardingManager` in `apps/unreal-akron-beta/` — port ideas, do not merge the shell
- Content = Cleveland race-base (`Cleveland5_0KmWorld`, burke pack, skyline keepers already on grokbot tip `5f420f6`)

### Build & Engine

- Document Package-mode exe layout + Dev-mode contract (`LaunchClevelandRace.bat` / worktree paths)
- Reference existing `raceGPS.bat` + GPU lock pattern under Akron binaries as launcher contract inspiration
- One Win64 package when Chris unlocks cook — not every polish pass. G4 package archive is currently empty (prior UAT failures); Package mode UI must say so honestly

### Shared config

- `%AppData%\raceGPS\settings.json` (or project-adjacent equivalent): paths, Race mode, GPU note
- Launcher is source of truth for install/setup; Race/Workshop read what they need

## Data flow

1. First run → wizard writes settings JSON
2. Home validates Package exe **or** Dev bat for chosen mode; Workshop entrypoint exists
3. Play Race → Package exe **or** documented Dev entry; never flip GlobalDefaultGameMode
4. Open Workshop → local UI → pack → semantic/Overpass → validate → `.rgpack`
5. Race `.rgpack` consumption = **later** (Cleveland in-tree course OK for this milestone)
6. In-Race settings → Unreal user settings; launcher prefs stay in shared JSON

### Failure behavior

- Missing package → CTA: switch Dev / point at build / "not built yet"
- Missing Dev bat → show expected `raceGPS-grokbot-cleveland` paths
- Workshop fail → surface CLI/log path
- Race crash → Open logs; NullRHI ≠ PASS
- Cook frozen → Package mode "awaiting build"; Dev is team path

## Research & training ops (Chris 2026-09-27)

**Principle:** At every stage (launcher stack, Workshop UI patterns, Race HUD/CommonUI, packaging), Unreal PM and lane owners **research modern open-source** before implementing. Cite sources with dates. Prefer finished OSS patterns (Electron game launchers, UE CommonUI samples, Epic Chaos Vehicle / open racers already in unreal-game-dev skill) over inventing scaffolding.

**Unreal PM dual mode**

1. **Managing:** sequencing, FAIL-CLOSED gates, unlock notes, specialist handoffs
2. **Researching (when not managing):** short researched briefs into `docs/evidence/grokbot/research/` (or handoff mirror) — launcher frameworks, Workshop UX refs, HUD/settings refs, packaging recipes — with links, dates, and a recommend/reject line

**When PM stops managing → Research & Training bot spins up**

- New teammate (to create after this spec is approved): **Research & Training** under Prototyper
- Trigger: Unreal PM posts "managing stop" / board locked / idle after a gate, **or** a standing routine if PM goes quiet while Wave 1 / easy-beta is active
- Bot duties: (1) deepen OSS research queues PM left, (2) freeze-safe training packs / annotations for Wave 1 + this beta, (3) write cite-and-path notes specialists can execute without re-deriving sources
- Bot does **not** own Gate 1 launches, cook spam, or goal-lock overrides
- When PM resumes managing, bot stands down or switches to backlog-only research; Unreal PM re-takes sequencing

## Success criteria (milestone done)

| Lane | Done when | Evidence |
|------|-----------|----------|
| Launcher | Wizard + restore; launches Race (mode) + Workshop; clear missing-path CTAs | Screenshots + short note under `docs/evidence/` |
| Workshop | Auth-less routes through export; Akron compilers wired; honest errors | Export proof + route checklist |
| Race | HUD + pause/settings playable on Cleveland (Dev OK if no package) | PIE/`-game` log + screenshots (not NullRHI) |
| Build contract | Written Package vs Dev layout launcher reads | Doc path cited in unlock note |
| Research ops | PM research notes exist for chosen stacks; R&T bot briefed/created | Research folder + agent brief |

Unreal PM FAIL-CLOSED grades lanes. Prototyper blocks only on goal-risk. Mode B stills / attended Track A remain Chris unlocks — not required for launcher + Workshop route "done."

## Lane ownership

| Lane | Owner |
|------|--------|
| Launcher + Workshop UI | Workshop Web |
| Package/Dev contract + rare package | Build & Engine |
| Race HUD/settings | Race Systems (Vehicle Arcade assist) |
| Visual floor / stills | World Environment (Mode B when Chris unlocks) |
| Sequencing + research-when-idle | Unreal PM |
| Research/training when PM stops | Research & Training (new) |
| Goal locks | Prototyper |

## Inventory anchors (2026-09-27 read-only)

- Grokbot tip includes skyline keepers `5f420f6`; no completed Cleveland Shipping/Dev package archive
- `Content/UI/**` Blueprint stubs only; live menu/settings C++ lives under Akron beta (patterns only)
- `raceGPSWorkshop` / `WorkshopAppSubsystem` = scaffolding; `cityhub/` API has no frontend
- Overpass→rgpack fixture path already PASS; semantic pin docs exist

## Open items after Chris approves this spec

1. Invoke writing-plans → implementation plan
2. Create **Research & Training** agent + seat/brief
3. Unreal PM unlock note for easy-test-beta milestone
4. Workshop Web starts launcher scaffold (Electron+Vite) freeze-safe
5. Race Systems starts HUD/settings plan citing OSS + Akron patterns (no unattended launch)