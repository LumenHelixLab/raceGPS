# STATUS — DEVELOPMENT PAUSE — 2026-09-29

**Authority:** Chris order 2026-09-29 — pause **ALL** development; leave handoff in `C:\projects\racegps`.  
**Timezone:** America/New_York  
**FAIL-CLOSED:** Do **not** resume until Chris unlocks. Reload from this board + Wave 1 unlock + Gate 1 BOTH tracks.

---

## Ownership

| Role | Scope |
|------|--------|
| **Unreal PM** | Owns Wave 1 day-to-day (granted 2026-09-27 by Prototyper / Chris) |
| **Prototyper** | Overseer on **goal-risk only** — not day-to-day Wave 1 |
| **Chris** | Unlock authority; owns Track A Sunset keep-alive; Mode B stills |

---

## True north

**Midnight Club / Midnight Run** arcade GPS street racing that **looks like a game**.  
Visual floor + playable race = scoreboard. **Race base first.**

Not the product: NullRHI proofs, black-void screenshots, architecture scaffolding sold as progress, CARLA rebuilds, or City Sample greenfield Cleveland.

---

## Hard locks (do not violate)

| Lock | Rule |
|------|------|
| GlobalDefaultGameMode | Stays **CruiseSprint** — never flip |
| Gate 1 PASS | NullRHI / black void / ForceFinish **≠ PASS** |
| Launch / Gate 1 | No unattended `LaunchClevelandRace` / Gate 1 spam; **Chris owns Track A Sunset** |
| Mode B stills | Wait Chris |
| Skyline cook | **ABORT** — not PASS (FTSR stall / killed); load-only PASS stands |
| City rebuild | No CARLA rebuild / City Sample greenfield Cleveland |
| Semantic | Akron **KEEP** (`tools/akron-semantic-compiler`); `universal-city-compiler` = sibling; citypack→rgpack adapter **post-unlock**; Cleveland race-base = gameplay scoreboard |
| Skills | Phase C skill **held**; `unreal-game-dev` only |

---

## Wave 1 status (gated PASS, then pause)

| Item | Grade | Evidence |
|------|-------|----------|
| Training pack 01 + annotations FULL SET | **PASS** | WE / B&E / WW (see WAVE1-INDEX + agent-training) |
| Photo-skyline stills plan | **PASS** | `docs/evidence/grokbot/world-environment-training/2026-09-27-PHOTO-SKYLINE-STILLS-PLAN.md` |
| Skyline asset load-only | **PASS** | `docs/evidence/grokbot/build-engine-training/2026-09-27-SKYLINE-ASSET-LOAD-CHECK.md` |
| Skyline targeted cook | **ABORT** (not PASS) | `docs/evidence/grokbot/build-engine-training/2026-09-27-SKYLINE-ASSET-COOK-ABORT.md` (FTSR / killed) |
| WW Overpass→rgpack + semantic | **PASS** | `docs/evidence/grokbot/agent-training/2026-09-27-WAVE1-WW-EXPORT-AND-SEMANTIC-QA.md` |
| Wave 1 unlock note | Landed 2026-09-27 | `docs/handoff/2026-09-27-WAVE1-UNLOCK.md` (grokbot-cleveland + Documents) |

**Prefer evidence under** `C:\projects\raceGPS-grokbot-cleveland\docs\evidence\grokbot\` (mirrors under Documents).

---

## Build room / Gate 1

| Track | State |
|-------|--------|
| **Track A** | Chris attended `LaunchClevelandRace.bat Sunset` keep-alive — **human-owned**; agents banned from unattended spam |
| **Track B** | Phase A TEMP viewport probe **compiled in**; Phase B **HOLD** |
| **CA / VA** | Freeze on Burke EZ editor/stills / Chaos retune |

See: `docs/handoff/2026-09-25-GATE1-BOTH-TRACKS.md` (primary worktree).

---

## Paths

| Role | Path | Branch / note |
|------|------|----------------|
| **This pause drop (required)** | `C:\projects\racegps` | Sibling / older; branch `feature/cleveland-showcase-demo` |
| **Primary evidence / active worktree** | `C:\projects\raceGPS-grokbot-cleveland` | `grokbot/cleveland-integration` (ahead of origin at pause write; tip ~`9604d0b`) |
| Documents mirror | `C:\Users\cgp22\Documents\raceGPS-handoff\` | Handoff + evidence copies |

Uproject (primary tree): `apps\unreal-akron-beta\raceGPSAkronBeta.uproject` · Engine UE **5.7** on omni.

---

## Prototyper FYI (paused with everything else)

easy-test-beta launcher research Task 0 was **docs-only** under `docs/evidence/grokbot/research/` — also paused.

---

## Reload checklist (when Chris unlocks)

1. This STATUS + `HUMAN-TEAM-HANDOFF-2026-09-29.md` + `TECH-SPEC-SHEET.md`
2. `2026-09-27-WAVE1-UNLOCK.md`
3. `2026-09-25-GATE1-BOTH-TRACKS.md` (+ Track B Phase A landed / dig if needed)
4. WAVE1 evidence rows above (load PASS ≠ cook PASS; Mode B still Chris)
5. Confirm worktree: open **grokbot-cleveland** for latest, not only this sibling folder

**Until then: STOP.**
