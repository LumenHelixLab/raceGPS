# Train-while-HOLD — synthesis outline (for Chris approval)

**Status:** OUTLINE ONLY — awaiting Chris green before any live GitHub/Reddit research pass  
**Owner:** Unreal PM  
**Date:** 2026-09-25  
**Constraint:** Gate 1 / Burke PIE stills / omni editor stay FROZEN. Docs only. Human handoff pack under `docs/handoff/` untouched.

## Why this exists

Chris asked, while holding game work: train the team (and Unreal PM) on game building, Unreal craft, digital art floor, game theory, and safe open sources — then brainstorm a plan for approval. Prototyper greened **Outline first**. Specialists hold their separate slice folders until this synthesis lands.

## Deliverable this round

One synthesis pack under:

`docs/evidence/grokbot/agent-training/`

| File | Purpose |
|------|---------|
| `2026-09-25-OUTLINE-FOR-APPROVAL.md` | This curriculum + ranked cite-and-path sources (approval gate) |
| `README.md` | Index + freeze rules |

**Not in this round:** live GitHub/Reddit scrapes, repo clones, marketplace installs, omni UnrealEditor, PIE stills, LaunchClevelandRace.

---

## Curriculum (four tracks)

Shared bar for every track: **research-before-build**, cite source + date checked, map every lesson to a raceGPS observable (no architecture theater). Prefer reuse of existing CARLA/UE street+vehicle pipelines and in-tree packs over greenfield.

### Track 0 — Prototyper + Unreal PM (meta)

| Module | Study focus | Observable for raceGPS |
|--------|-------------|------------------------|
| 0.1 MDA / core loop | Mechanics → Dynamics → Aesthetics; vertical slice before breadth | Countdown → racing → finish HUD → R restart is the loop; Workshop/OSM deferred |
| 0.2 Research protocol | UE version first (5.7); Epic docs → samples → community leads verified locally | No API from mismatched tutorial; record question / source / date |
| 0.3 Evidence gates | Compile ≠ playable; NullRHI/black void = FAIL; screenshot + log for visual claims | Gate 1 unlock criteria unchanged |
| 0.4 Sequencing craft | One UnrealEditor owner; specialist lanes; escalate only when blocked with zero reusable source | CA → VA visual stills → RS finish+R; Chris dark until PASS |
| 0.5 Digital art floor (PM literacy) | Readable silhouette, lighting mood, horizon/water/skyline composition — enough to judge stills, not replace CA/VA | Burke bar: EZ ribbon + Cleveland skyline + Lake Erie, no empty north-runway camera fails |

**Internal anchors (already installed):** `unreal-game-dev` v2.0.0 — `references/game-theory.md`, `research-protocol.md`, `genre-car-racing.md`, `ui-ux.md`, `physics.md`, `build-debug-test.md`.

### Track 1 — Course Architect

| Module | Study focus | Observable for raceGPS |
|--------|-------------|------------------------|
| 1.1 Racing flow craft | Racing line, braking zones, sightlines, elevation; checkpoint spacing for arcade read | Burke EZ ~35% wider gates; ribbon read at speed |
| 1.2 UE5 env / water+skyline | Composition: city / water / track; lighting that sells Sunset without void | CLEVELAND_VISUAL_BAR checklist; reuse skyline/water/dressing |
| 1.3 OpenDRIVE / street pipelines | Steal patterns from finished CARLA/UE street packs — cite-and-path only | Shared XODR for `cleveland_burke_gp_1997_ez`; no CARLA rebuild |
| 1.4 Course versioning | v1 ribbon → v2 barriers/lighting → v3 landmarks | EZ is v1 readability pass, not a new city |

**Planned slice folder (held until outline approved):** `docs/evidence/grokbot/course-architect-training/`

### Track 2 — Vehicle Arcade

| Module | Study focus | Observable for raceGPS |
|--------|-------------|------------------------|
| 2.1 Arcade vs sim Chaos | Arcade-fun handling goal; avoid sim traps on Chaos Vehicle | Feel target: Midnight Club / Midnight Run, not iRacing |
| 2.2 Camera + car visual floor | Chase/hood readability; skeletal-safe materials; Sunset-readable car | Side/¾ and chase stills only after CA frees editor |
| 2.3 AI cornering / recovery | Racing-line lookahead, brake planning, crash recovery — control layer, not NavMesh alone | Defer AI until race loop + visual floor green |
| 2.4 Chaos Vehicle samples | Epic Vehicle / Chaos patterns; open UE race kits cite-and-path | Extend existing stack; no new vehicle framework |

**Planned slice folder (held):** `docs/evidence/grokbot/vehicle-arcade-training/`

### Track 3 — Race Systems

| Module | Study focus | Observable for raceGPS |
|--------|-------------|------------------------|
| 3.1 Session loop craft | Waiting → countdown → racing → finished → restart; single timing authority | Gate 1: human finish HUD + R |
| 3.2 HUD / UMG race UX | Checkpoint feedback, finish screen, focus for packaged Race target | Readable on real scene — not NullRHI |
| 3.3 Viewport survival | Why windowed `-game` died (~2s ViewportClosed); how humans keep viewport alive | Prior FAIL evidence stays FAIL; no unlock on void |
| 3.4 Race-loop open patterns | unreal-simple-racer / UETrafficGame-class session+HUD — cite-and-path | Steal loop patterns; do not invent scaffolding |

**Planned slice folder (held):** `docs/evidence/grokbot/race-systems-training/`

---

## Ranked sources (cite-and-path only — no installs this round)

Checked / nominated **2026-09-25**. Live GitHub/Reddit enrichment = **Phase B** after Chris approves.

### Tier A — Prefer first (safe, versioned, known-good for raceGPS)

| # | Source | Why | Track |
|---|--------|-----|-------|
| A1 | Epic Chaos Vehicles / Vehicle template docs (UE 5.x matching 5.7) | Official handling + sample stack | 2, 3 |
| A2 | Epic Gameplay Framework + Enhanced Input docs | Session ownership, input for race loop | 0, 3 |
| A3 | In-tree raceGPS + CARLA/UE street packs already on disk (e.g. Burke / Cleveland pipelines) | Chris reuse bar — wrap/light, don't rebuild | 1, 0 |
| A4 | Installed `unreal-game-dev` skill v2.0.0 (racing playbook, MDA, research protocol) | Shared team language | 0–3 |
| A5 | OpenDRIVE / CARLA map pipeline docs (patterns only) | Street continuity, XODR → mesh lessons | 1 |

### Tier B — Cite-and-path open race kits (verify license + UE version before any clone)

| # | Pattern class | Steal | Do not |
|---|---------------|-------|--------|
| B1 | unreal-simple-racer–class repos | Countdown, checkpoints, timing, restart | City generation, economy |
| B2 | UETrafficGame–class / traffic race samples | Session+HUD patterns | Full traffic sim as Gate 1 |
| B3 | KinetiForge / R-Tune–class Chaos spikes | Arcade tune ideas | Replace project vehicle stack |
| B4 | Epic sample Content / Learning kit vehicle maps | Camera + flat-pad tune scenarios | Marketplace paid packs without Chris OK |

### Tier C — Community leads (Phase B only; verify against A/B)

| # | Venue | Use for | Risk |
|---|-------|---------|------|
| C1 | GitHub topics: unreal-engine, chaos-vehicle, open-drive | Discover B-class repos with stars/license/date | Stale UE4 / abandoned |
| C2 | r/unrealengine, r/gamedev (read-only) | Failure modes, viewport/packaged-game tips | Anecdote ≠ API truth |
| C3 | Digital art / env-art free learning (composition, value, skyline read) | Still judgment literacy for PM/CA | Style drift away from Midnight Club bar |

**Safety rules for Phase B:** MIT/Apache/BSD or Epic sample license preferred; no cracked assets; no unpaid Marketplace; no credentialed scrapers; record URL + license + last commit/date + UE version in the pack before anyone clones.

---

## Proposed sprint (after Chris approves outline)

| Phase | Who | Output | Editor? |
|-------|-----|--------|---------|
| **A — Outline** (now) | Unreal PM | This pack | No |
| **B — Live research** (if Chris greens) | Unreal PM leads; CA/VA/RS pull lane sources | Ranked repo table with license/date/UE ver under `agent-training/sources/` | No |
| **C — Study packs** | CA / VA / RS write short packs in their `*-training/` folders from approved list | One-pager + 3 cited lessons each mapped to raceGPS | No |
| **D — Resume game work** | Only when Chris reopens | Burke EZ PIE stills → visual PASS → Gate 1 | Yes (one owner) |

---

## Explicit non-goals (until Chris reopens game work)

- omni UnrealEditor / PIE / HighResShot / LaunchClevelandRace / LaunchCleveland.bat
- Gate 1 finish+R attempts
- CARLA rebuild or greenfield Cleveland
- Two-app rgpack / Workshop / OSM builder
- Touching `docs/handoff/` human pack
- Installing or cloning repos before Phase B green

---

## Approval ask (Chris)

1. **Green this outline** as the train-while-HOLD curriculum?  
2. **Green Phase B** live GitHub/Reddit cite-and-path pass (still no installs), or stay on Tier A/B known pipelines only?  
3. Any source class to **ban** (e.g. Reddit off, Marketplace always off)?

When Chris answers, Unreal PM updates this file and unlocks Phase B or C accordingly. Specialists stay held on slices until then.
