# raceGPS — Human / Agent Team Handoff — DEVELOPMENT PAUSE

**Date:** 2026-09-29 (America/New_York)  
**Order:** Chris — pause **ALL** development; leave handoff in `C:\projects\racegps`  
**From:** Unreal PM (Wave 1 day-to-day) + Prototyper (goal-risk overseer)  
**To:** Chris, human Unreal / game-dev team, and any agent that reloads later  
**FAIL-CLOSED:** Do **not** resume work until Chris unlocks.

---

## 0. Where to open the project

| Path | Role at pause |
|------|----------------|
| `C:\projects\racegps` | **Required pause drop** (this file lives here under `docs\handoff\`). Sibling / older checkout. Branch: `feature/cleveland-showcase-demo`. |
| `C:\projects\raceGPS-grokbot-cleveland` | **Primary evidence / active worktree.** Branch: `grokbot/cleveland-integration`. Prefer this tree for latest docs, evidence, and launch bats. Tip noted at pause write: `9604d0b` (2026-09-28) docs(easy-test-beta). |
| `C:\Users\cgp22\Documents\raceGPS-handoff\` | Documents mirror of handoff + training evidence |

**Path hygiene:** Launch scripts and older docs may still say `C:\projects\racegps\...`. Before any launch after unlock, grep bats for `PROJ=` and align to the worktree you actually open (prefer **grokbot-cleveland**).

**Uproject:** `apps\unreal-akron-beta\raceGPSAkronBeta.uproject`  
**Engine:** Unreal Engine **5.7** on **omni**

---

## 1. Product true north

**raceGPS** = arcade street racer in the spirit of **Midnight Club / Midnight Run**:

- Human drives on real-feeling city streets
- Race loop: countdown → checkpoints → rivals → finish HUD → **R** restart
- Look: intentional camera, readable city, Lake Erie / downtown skyline where Cleveland demands it
- Later: GPS / Workshop map packs — **after** the race loop feels like a game

**Visual floor + playable race = scoreboard. Race base first.**

**Not the product:** architecture scaffolding, NullRHI “proofs”, black-void screenshots, greenfield city rebuilds, or re-implementing CARLA / City Sample Cleveland.

### Standing preferences (Chris)

1. **Reuse existing sources** — wrap/light finished CARLA/UE street+vehicle pipelines and in-tree city packs. No CARLA rebuild. No greenfield Cleveland.
2. **No black void** — black / NullRHI / dead viewport is FAIL, never progress (except Cmd asset-load tooling where NullRHI is explicitly scoped and **not** Gate 1 evidence).
3. **Chris-facing visual bar:** Burke Lakefront **EZ** with vivid Cleveland skyline + Lake Erie (Mode B stills wait Chris).
4. **Gate 1** remains human Track A + Track B dig; NullRHI / ForceFinish ≠ PASS.

---

## 2. Why everything stopped (2026-09-29)

Chris ordered a **full development pause** and a durable handoff left in `C:\projects\racegps` (with mirrors).

Wave 1 had reached a gated PASS set (training pack, stills **plan**, skyline **load-only**, WW export+semantic). Cook was **ABORT**. Build-room Gate 1 tracks remain human / HOLD. Easy-test-beta launcher research (docs-only Task 0) is paused with everything else.

**No agent should resume Unreal, editor, LaunchClevelandRace, Gate 1 spam, or code work until Chris unlocks.**

---

## 3. Ownership

| Role | Authority |
|------|-----------|
| **Unreal PM** | Owns Wave 1 day-to-day (granted **2026-09-27** by Prototyper / Chris) |
| **Prototyper** | Overseer on **goal-risk only** |
| **Chris** | Unlock; Track A Sunset keep-alive; Mode B stills letter |

Skill surface: Phase C skill **held**; use **`unreal-game-dev` only**.

---

## 4. Hard locks

| Lock | Rule |
|------|------|
| **GlobalDefaultGameMode** | Stays **CruiseSprint** — never flip. Showcase overrides via URL / bat only. |
| **Gate 1 PASS** | NullRHI / black void / ForceFinish **≠ PASS** |
| **Unattended launch** | No unattended `LaunchClevelandRace` / Gate 1 spam |
| **Track A** | Chris owns attended `LaunchClevelandRace.bat Sunset` keep-alive |
| **Mode B stills** | Wait Chris |
| **Skyline cook** | **ABORT** not PASS (FTSRRejectShadingCS stall; killed). Load-only PASS stands. |
| **City rebuild** | No CARLA rebuild / City Sample greenfield Cleveland |
| **Semantic** | Akron **KEEP** (`tools/akron-semantic-compiler`); `tools/universal-city-compiler` = sibling; citypack→rgpack adapter **post-unlock**; Cleveland race-base = gameplay scoreboard |
| **Editor lock** | One UnrealEditor on omni when work resumes; Build & Engine owns lock historically |

---

## 5. Wave 1 — what gated PASS vs not

### PASS (keep; cite evidence)

| Item | Evidence (prefer grokbot-cleveland `docs/evidence/grokbot/`) |
|------|------|
| Training pack 01 + annotations FULL SET (WE/B&E/WW) | `agent-training/WAVE1-INDEX.md` + pack artifacts |
| Photo-skyline stills **plan** | `world-environment-training/2026-09-27-PHOTO-SKYLINE-STILLS-PLAN.md` (+ QA under agent-training) |
| Skyline asset **load-only** | `build-engine-training/2026-09-27-SKYLINE-ASSET-LOAD-CHECK.md` (`M_SkylineBackdrop`, `T_Cleveland_SkylineNight`) |
| WW Overpass→rgpack + semantic inventory/brief | `agent-training/2026-09-27-WAVE1-WW-EXPORT-AND-SEMANTIC-QA.md` |
| Wave 1 unlock note | `docs/handoff/2026-09-27-WAVE1-UNLOCK.md` |

### NOT PASS / HOLD

| Item | State |
|------|--------|
| Skyline targeted cook | **ABORT** — `build-engine-training/2026-09-27-SKYLINE-ASSET-COOK-ABORT.md` (full cook / FTSR Vulkan SM5; killed; **not** cook PASS) |
| Mode B photo stills capture | **HOLD** — wait Chris |
| Gate 1 finish HUD + R (live human) | **Not proven PASS** — Track A human; Track B Phase B HOLD |
| citypack→rgpack adapter + Workshop UI routes | Post-unlock / not done |
| CA / VA Burke EZ editor stills / Chaos retune | Frozen |

---

## 6. Build room / Gate 1

Decision record: `docs/handoff/2026-09-25-GATE1-BOTH-TRACKS.md`

| Track | State at pause |
|-------|----------------|
| **A — Interactive keep-alive** | Chris attended session owns the window. Human bat: `LaunchClevelandRace.bat Sunset` (`-log -windowed`; no playtest / nullrhi / ClevelandAutoLap for PASS). |
| **B — ViewportClosed dig** | Phase A TEMP viewport probe **compiled in**; Phase B **HOLD**. Prior FAIL: Racing → ~2s → `UGameEngine::Tick.ViewportClosed`. |

Related: `2026-09-25-GATE1-TRACK-B-PHASE-A-LANDED.md`, dig / patch-plan / resume playbook under same `docs/handoff/`.

---

## 7. What was already done (carry forward; do not rebuild)

Keep (summarized from prior human handoff + Wave 1):

- Race-base MVP code lineage (HUD / human bat / soft AI) — code work existed; **live** human finish+R not Gate 1 PASS
- Vehicle Arcade V16 chase / Sunset lighting lineage (open items historically: Side/_ capture, CARLA glass)
- Burke historic pack `citypacks/cleveland/burke_gp_1997` + EZ data-plane (`racing_line_ez`, `checkpoints_ez` ~35% wider gates, shared XODR)
- Generation evidence under `docs/evidence/grokbot/burke-ez-ribbon/`
- Showcase skyline keepers on tip lineage (`M_SkylineBackdrop`, `T_Cleveland_SkylineNight`, SourceImages / import helpers) — see `2026-09-27-SHOWCASE-KEEPERS-LANDED.md`
- Launch recipe that does **not** flip default GM: map `Cleveland5_0KmWorld` + `ClevelandShowcaseGameMode` override
- Semantic compiler pin: `docs/handoff/2026-09-27-SEMANTIC-COMPILER-PIN.md`

---

## 8. Semantic / compiler stance

| Tree | Rule |
|------|------|
| `tools/akron-semantic-compiler/` | **KEEP** — golden Akron reference |
| `tools/universal-city-compiler/` | Sibling general-purpose expansion |
| citypack→rgpack adapter | **Post-unlock** |
| Cleveland race-base | Gameplay scoreboard (parallel to compiler work, not a reason to delete Akron) |

---

## 9. Prototyper FYI (also paused)

easy-test-beta launcher research **Task 0** was docs-only under `docs/evidence/grokbot/research/` (design/plan also under `docs/handoff/2026-09-27-EASY-TEST-BETA-LAUNCHER-DESIGN.md` and `2026-09-28-EASY-TEST-BETA-LAUNCHER-PLAN.md`). **Paused with everything else** — no launcher implementation push during freeze.

---

## 10. Reload after Chris unlock

1. Read `HANDOFF_PAUSE.md` (root of racegps) + this file + `STATUS-PAUSE-2026-09-29.md` + `TECH-SPEC-SHEET.md`
2. Read `2026-09-27-WAVE1-UNLOCK.md` and `2026-09-25-GATE1-BOTH-TRACKS.md` on **grokbot-cleveland**
3. Confirm branch/worktree; prefer `C:\projects\raceGPS-grokbot-cleveland` @ `grokbot/cleveland-integration`
4. Re-check WAVE1 evidence grades (load PASS ≠ cook PASS; Mode B still Chris)
5. Respect hard locks; Unreal PM FAIL-CLOSED gates

**Until Chris unlocks: STOP. No Unreal launches, no editor, no code changes beyond docs already written for this pause.**
