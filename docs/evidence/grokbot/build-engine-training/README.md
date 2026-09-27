# Build & Engine — training (Wave 1)

**Lane:** Build & Engine (Win64 Dev/Shipping targets, packaging, omni single-editor, UBA hygiene, bat launchers, crash/log forensics)
**Owner:** Build & Engine under Prototyper; Unreal PM gates evidence
**Rule:** cite-and-path only. No omni UnrealEditor, no PIE, no `LaunchClevelandRace`, no clones / installs until Chris unlocks.
**Checked:** 2026-09-26 — soft gaps cleared (single Pack 01 filename + G6 build-log cite); annotations pack landed
**Worktree (when game work reopens):** `C:\projects\raceGPS-grokbot-cleveland` — branch `grokbot/cleveland-integration` — UE **5.7.4**
**QA:** Wave 1 pack 01 **PASS** — `docs/evidence/grokbot/agent-training/2026-09-26-WAVE1-TRAINING-QA.md`

## Files

| File | Role |
|------|------|
| [2026-09-26-PACK-01-WIN64-DEV-REBUILD-AND-LOG-FORENSICS.md](./2026-09-26-PACK-01-WIN64-DEV-REBUILD-AND-LOG-FORENSICS.md) | **Primary Pack 01** — Win64 Dev recipe (`-MaxParallelActions=1 -NoUBA`), one-editor omni, LaunchClevelandRace human-default, ViewportClosed / RequestExit greps; Track B Phase A landed / Phase B HOLD |
| [2026-09-26-PACK-01-WIN64-DEV-REBUILD-AND-LOG-FORENSICS-ANNOTATIONS.md](./2026-09-26-PACK-01-WIN64-DEV-REBUILD-AND-LOG-FORENSICS-ANNOTATIONS.md) | **Annotations** — BE read-along steal/do-not/FUTURE observables + G6 FAIL/Succeeded notes |
| [2026-09-26-PACK-01-REBUILD-AND-LOG-FORENSICS.md](./2026-09-26-PACK-01-REBUILD-AND-LOG-FORENSICS.md) | Read-along only (Prototyper stub) — do not treat as a second Pack 01 |

## Hard constraints (raceGPS)

- **One UnrealEditor / one `-game` owner on omni.** Kill other editors/games before a build or Gate 1 launch (Live Coding lock exits Build.bat with **6** when an editor is already open — G1 host baseline).
- **Never** flip `GlobalDefaultGameMode` off **CruiseSprint**. Showcase GameMode is URL / bat override only.
- **NullRHI / `-nullrhi` / black void ≠ Gate 1 PASS.**
- **No unattended `LaunchClevelandRace`** while Chris owns attended Track A / freeze holds.
- Deliver **build logs + reproduce steps**, not vibes. Pair Race Systems on session-exit bugs; Unreal PM on evidence gates.

## Gate 1 posture

| Track | Status |
|-------|--------|
| **A — Chris attended Sunset** | Human-owned |
| **B Phase A** | **LANDED** (TEMP Showcase Tick probe; rebuild used `-MaxParallelActions=1 -NoUBA`) |
| **B Phase B** | **HOLD** |
| NullRHI proofs | **Not PASS** |

## Evidence paths

| Role | Path |
|------|------|
| This lane | `docs/evidence/grokbot/build-engine-training/` |
| Documents mirror | `Documents\raceGPS-handoff\build-engine-training\` |
| Gate 1 / G6 | `docs/evidence/grokbot/G6-race-base-mvp/` |
| Phase A rebuild log (Succeeded) | `docs/evidence/grokbot/G6-race-base-mvp/track-b-phase-a-build.log` |
| Host / Live Coding baseline | `docs/evidence/grokbot/G1-host-baseline/` |

## Freeze posture

Stand down on editor / PIE / unattended launches. Cite-and-path and annotations only until Chris unlocks Mode C or Mode D.