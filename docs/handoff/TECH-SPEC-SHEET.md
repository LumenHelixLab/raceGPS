# raceGPS — Tech Spec Sheet (pause pointer) — 2026-09-29

**Document type:** Short engineering pointer for the 2026-09-29 development pause.  
**Do not invent engine facts.** Fuller sheet already exists — cite it.

---

## Canonical fuller sheet

| Location | File |
|----------|------|
| Primary worktree | `C:\projects\raceGPS-grokbot-cleveland\docs\handoff\2026-09-25-TECH-SPEC-SHEET.md` |
| Documents mirror | `C:\Users\cgp22\Documents\raceGPS-handoff\2026-09-25-TECH-SPEC-SHEET.md` |

That sheet covers: repo/host, UE 5.7, CruiseSprint default, Cleveland Showcase URL/bat override, Burke GP 1997 + EZ pack files/metrics, map/geo notes, launch contracts. **Use it as the detailed reference.** This file only restates pause-critical locks and path facts as of 2026-09-29.

---

## Repository & host (pause facts)

| Field | Value |
|-------|--------|
| Pause drop (this tree) | `C:\projects\racegps` — branch `feature/cleveland-showcase-demo` (sibling / older) |
| **Primary live worktree** | `C:\projects\raceGPS-grokbot-cleveland` — branch **`grokbot/cleveland-integration`** |
| Tip noted at pause write | `9604d0b` (2026-09-28) — docs(easy-test-beta) evidence templates |
| Host | omni (Windows) |
| Engine | UE **5.7** |
| Uproject | `apps\unreal-akron-beta\raceGPSAkronBeta.uproject` |
| Evidence root | `docs\evidence\grokbot\` under grokbot-cleveland (+ Documents mirrors) |

**Path hygiene:** bats/docs may disagree between `racegps` and `raceGPS-grokbot-cleveland`. Grep `PROJ=` before launch after unlock.

---

## Hard locks (cite — do not weaken)

| Lock | Spec |
|------|------|
| Default GameMode | **CruiseSprint** immutable for GlobalDefaultGameMode / Akron default |
| Showcase launch | Override GameMode **only** via URL or bat — never flip default |
| Gate 1 PASS | NullRHI / black void / ForceFinish **≠ PASS** |
| Human Gate 1 bat | `LaunchClevelandRace.bat Sunset` — attended; no `-ClevelandAutoLap` for PASS path per Gate 1 BOTH tracks |
| Unattended Launch / Gate 1 spam | **Banned** |
| Mode B stills | Wait Chris |
| Skyline assets | Load-only **PASS**; targeted cook **ABORT** (FTSR) — not cook PASS |
| City rebuild | No CARLA rebuild / City Sample greenfield Cleveland |
| Semantic | Akron KEEP (`tools/akron-semantic-compiler`); universal-city-compiler sibling; citypack→rgpack adapter post-unlock |
| Skills | Phase C held; `unreal-game-dev` only |

---

## Map / launch (from known locks — see fuller sheet)

| Field | Known value |
|-------|-------------|
| Map | `/Game/Maps/Cleveland5_0KmWorld` |
| Place | Burke Lakefront Airport (BKL), Cleveland OH |
| Showcase GameMode (override) | `ClevelandShowcaseGameMode` (script path as in fuller sheet / bats) |
| Pack | `cleveland_burke_gp_1997` + EZ variant (shared XODR) |

Do not “rebuild T10 city” to fix a north-runway frame — see fuller sheet Content fact.

---

## Wave 1 evidence pins (grades)

| Artifact | Grade |
|----------|-------|
| `world-environment-training/2026-09-27-PHOTO-SKYLINE-STILLS-PLAN.md` | Plan / QA **PASS** |
| `build-engine-training/2026-09-27-SKYLINE-ASSET-LOAD-CHECK.md` | Load **PASS** |
| `build-engine-training/2026-09-27-SKYLINE-ASSET-COOK-ABORT.md` | Cook **ABORT** |
| `agent-training/2026-09-27-WAVE1-WW-EXPORT-AND-SEMANTIC-QA.md` | WW+semantic **PASS** |
| `docs/handoff/2026-09-27-WAVE1-UNLOCK.md` | Unlock note (then later full pause) |
| `docs/handoff/2026-09-25-GATE1-BOTH-TRACKS.md` | Track A human / Track B dig |

---

## Related handoff (this pause set)

- `C:\projects\racegps\HANDOFF_PAUSE.md`
- `docs/handoff/STATUS-PAUSE-2026-09-29.md`
- `docs/handoff/HUMAN-TEAM-HANDOFF-2026-09-29.md`

**Development paused until Chris unlocks.**
