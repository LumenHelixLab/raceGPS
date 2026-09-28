> **READ-ALONG ONLY (Prototyper stub).** Canonical Pack 01 is `2026-09-26-PACK-01-WIN64-DEV-REBUILD-AND-LOG-FORENSICS.md`. Do not grade this file as a second Pack 01.
# BE read-along -- Pack 01 (rebuild recipe + log forensics)

**Annotator:** Build & Engine
**Date:** 2026-09-26
**Parent cites (in-tree / handoff):**
- `docs\handoff\2026-09-25-GATE1-TRACK-B-PHASE-A-LANDED.md` — Phase A TEMP probe landed; Win64 Dev Succeeded single-thread `-NoUBA`
- `docs\handoff\2026-09-25-GATE1-TRACK-B-DIG.md` — ViewportClosed timeline; playtest-only RequestExit sites
- `docs\handoff\2026-09-25-GATE1-TRACK-B-PATCH-PLAN.md` — Phase B instrumentation still HOLD
- `docs\handoff\2026-09-25-GATE1-BOTH-TRACKS.md` — Chris BOTH strategy; Track A human keep-alive
- `docs\handoff\2026-09-25-GATE1-RESUME-PLAYBOOK.md` — interactive reopen checklist
- `docs\handoff\2026-09-25-TECH-SPEC-SHEET.md` §§A–B, H — uproject, bat contract, sample Build.bat
- `docs\handoff\2026-09-25-UNLOCK-CRITERIA.md` — modes A–D; never-PASS list
- Code cite: `apps\unreal-akron-beta\Source\raceGPSAkronBeta\Private\ClevelandShowcaseGameMode.cpp` (TEMP Track B heartbeat; CruiseSprint untouched)
**Mode:** study notes only — no editor launch, no rebuild execution, no Gate 1 spam from this pack

---

## What this pack is for (BE lane)

Own **how omni builds and how logs prove exits**. When freeze lifts, Build & Engine keeps a single editor owner, a known-good Win64 Development recipe, and a grep cheat sheet that separates ViewportClosed / RequestExit / Track B probes from false PASS noise.

Race Systems owns race-loop semantics. Build & Engine owns whether the process stayed alive long enough for those semantics to matter.

---

## Steal (map to raceGPS)

1. **Win64 Development recipe after UBA OOM** — Phase A land note: `raceGPSAkronBetaEditor` Win64 Development **Succeeded** with single-thread / `MaxParallelActions=1` and `-NoUBA` after a prior UBA attempt OOM-killed. Prefer that mitigation on omni rebuilds until a cleaner UBA path is proven.
2. **One UnrealEditor on omni** — Unlock Criteria mode D and Wave 1 freeze: single editor owner. Do not stack agent-spawned editors against Chris's attended Showcase window.
3. **Human default launch contract** — `apps\unreal-akron-beta\LaunchClevelandRace.bat` with **Sunset** (or current human bat). No `-nullrhi`, no playtest / AutoLap flags as Gate 1 evidence. Showcase GameMode via URL / bat override only.
4. **CruiseSprint GlobalDefault never flip** — Default GameMode stays CruiseSprint / Akron. Cleveland Showcase is an override path, not a DefaultEngine.ini rewrite.
5. **Track B Phase A already landed** — TEMP 1 Hz `raceGPS TrackB:` heartbeat + one-shot VIEWPORT LOST Warning in Showcase `Tick` only. Phase B viewport subclass / deeper instrumentation = **HOLD**.
6. **Chris owns attended Track A Sunset** — Discriminating test for ViewportClosed: Explorer double-click bat, keep focus ≥60–120s after Racing (ideally finish+R). Agent unattended launches are not evidence.
7. **Grep cheat sheet (post-attended log)** — Search for:

```
raceGPS TrackB:
ViewportClosed
RequestExit
UGameEngine::Tick.ViewportClosed
```

Also note focus-keeper lifetime and whether `playtest=0` (rules out playtest-only RequestExit sites in Showcase GM).

---

## Do not steal

- Claiming NullRHI / `ClevelandProofFinishR` / ForceFinish without driven viewport as Gate 1 PASS.
- Unattended `Start-Process` LaunchClevelandRace spam from agents.
- Leaving TEMP Track B logs forever after the dig closes (Phase A note: remove when dig closes).
- Re-opening Phase B instrumentation without Prototyper / Chris green.
- Flipping GlobalDefaultGameMode or default CityId.
- Treating empty Workshop/Race target build logs (`G5-workshop-race-targets\`) as playable-race evidence.

---

## Example Build.bat shape (docs only — do not run from this pack)

```bat
"%PROGRAMFILES%\Epic Games\UE_5.7\Engine\Build\BatchFiles\Build.bat" ^
  raceGPSAkronBetaEditor Win64 Development ^
  -Project="C:\projects\raceGPS-grokbot-cleveland\apps\unreal-akron-beta\raceGPSAkronBeta.uproject" ^
  -MaxParallelActions=1 -NoUBA
```

Adjust Engine path if omni install differs. Path hygiene: bats may still mention `C:\projects\racegps\` — align `PROJ=` to the worktree you actually open (`raceGPS-grokbot-cleveland`).

---

## FUTURE observables (do not run now)

| Check | Pass looks like |
|-------|-----------------|
| Rebuild | Editor target Succeeded; exit code + log under evidence; no silent UBA OOM |
| Ownership | Exactly one UnrealEditor; Chris or named owner |
| Track A | Attended Sunset window survives ≫60s after Racing; finish HUD + R when claiming Gate 1 |
| Track B dig | Grep shows heartbeat through Racing; ViewportClosed classified (ownership vs slate) |
| Evidence | Log excerpts under `docs\evidence\grokbot\G6-race-base-mvp\` with PASS/FAIL note |
| Anti | No nullrhi PASS; no unattended ViewportClosed sold as product bug without Track A |

---

## Tie-back to known raceGPS debt (docs only)

- Windowed Sunset FAIL: Racing → `ViewportClosed` ~1.85s; focus-keeper DEAD ~16ms (`GATE1-TRACK-B-DIG.md`).
- Showcase GM `RequestExit` sites are playtest-only; FAIL log had `playtest=0`.
- Phase A TEMP probe is in Showcase only; CruiseSprint untouched.
- Freeze: docs/training only until unlock.

---

## Hand-off

Unreal PM QA stub: `../agent-training\2026-09-26-WAVE1-TRAINING-QA.md`. Race Systems owns finish+R semantics; Build & Engine owns build recipe + log forensics + editor mutex.
