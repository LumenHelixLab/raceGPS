# Pack 01 — Win64 Dev rebuild + omni editor + LaunchClevelandRace + log greps

**Lane:** Build & Engine (primary)  
**Canonical filename:** `2026-09-26-PACK-01-WIN64-DEV-REBUILD-AND-LOG-FORENSICS.md` (sibling `.-REBUILD-AND-LOG-FORENSICS.md` is read-along stub only)  
**Date checked:** 2026-09-26  
**raceGPS weave:** rebuild hygiene → one-editor omni → human bat contract → ViewportClosed forensics → **docs only — do not launch editor / -game under freeze**

**Sources (cite these, do not invent):**
- `Documents\raceGPS-handoff\2026-09-25-GATE1-TRACK-B-PHASE-A-LANDED.md` (+ mirror under `docs/evidence/grokbot/G6-race-base-mvp/`)
- `docs/evidence/grokbot/G6-race-base-mvp/track-b-phase-a-build.log` ← concrete rebuild evidence
- `Documents\raceGPS-handoff\2026-09-25-GATE1-BOTH-TRACKS.md`
- `Documents\raceGPS-handoff\2026-09-25-GATE1-TRACK-B-DIG.md`
- `Documents\raceGPS-handoff\2026-09-25-GATE1-TRACK-B-PATCH-PLAN.md`
- `Documents\raceGPS-handoff\2026-09-25-GATE1-RESUME-PLAYBOOK.md`
- `Documents\raceGPS-handoff\2026-09-25-TECH-SPEC-SHEET.md`
- `Documents\raceGPS-handoff\2026-09-25-UNLOCK-CRITERIA.md`
- `apps/unreal-akron-beta/LaunchClevelandRace.bat`
- `docs/evidence/grokbot/G1-host-baseline/VERDICT.md` + `HOST_INVENTORY.md`

---

## 1. Win64 Development rebuild recipe (MaxParallelActions / NoUBA)

### Concrete G6 rebuild cite (Phase A)

From `docs/evidence/grokbot/G6-race-base-mvp/track-b-phase-a-build.log`:

```text
UnrealBuildTool.dll ... raceGPSAkronBetaEditor Win64 Development
  -Project=C:\projects\raceGPS-grokbot-cleveland\apps\unreal-akron-beta\raceGPSAkronBeta.uproject
  -WaitMutex -MaxParallelActions=1 -NoUBA -NoXGE
...
Result: Succeeded
Total execution time: 10.47 seconds
```

UBT line confirms **`-MaxParallelActions=1 -NoUBA -NoXGE`**. Log ends **`Result: Succeeded`** (process exit **0** for this Succeeded run). Contrast earlier UBA-path attempts that OOM-killed on omni (~31 GB RAM, iGPU Radeon 880M — see Phase A landed note + `G1-host-baseline/HOST_INVENTORY.md`).

| Field | Value |
|-------|--------|
| Target | `raceGPSAkronBetaEditor` |
| Platform / config | **Win64 Development** |
| Flags (logged) | `-WaitMutex -MaxParallelActions=1 -NoUBA -NoXGE` |
| Result | **Succeeded** (~10.5s this incremental) |
| Prior failure class | UBA OOM on omni |

### Canonical Build.bat shape (when Chris unlocks builds)

```bat
"%PROGRAMFILES%\Epic Games\UE_5.7\Engine\Build\BatchFiles\Build.bat" ^
  raceGPSAkronBetaEditor Win64 Development ^
  -Project="C:\projects\raceGPS-grokbot-cleveland\apps\unreal-akron-beta\raceGPSAkronBeta.uproject" ^
  -WaitMutex -MaxParallelActions=1 -NoUBA -NoXGE
```

### Lessons — apply on omni before re-enabling UBA

| Lesson | Why | Action |
|--------|-----|--------|
| **Prefer `-NoUBA` on omni for editor targets** | UBA already OOM-killed once | Default: `-NoUBA` until a measured UBA pass with headroom exists |
| **Cap parallelism (`-MaxParallelActions=1`)** | Logged on the Succeeded Phase A rebuild | Start at **1**; only raise after a clean NoUBA baseline |
| **Close UnrealEditor before Build.bat** | G1 host baseline: Live Coding active → Build exit **6** | One-editor rule; never fight Live Coding |
| **Path hygiene** | Bats/docs may point at `C:\projects\racegps` vs `raceGPS-grokbot-cleveland` | Grep `PROJ=` / worktree before claiming a rebuild |
| **Engine pin** | UE **5.7.4** CL 51494982 | Do not "fix" with another engine install under freeze |

### Targets (existing — do not invent empty progress)

| Target | Role |
|--------|------|
| `raceGPSAkronBeta` | Game / cook when packaging reopens |
| `raceGPSAkronBetaEditor` | Editor target used for Track B Phase A rebuild |
| Workshop / Race game targets | Planned in two-app slice — coordinate with Workshop Web later |

---

## 2. One-editor omni rule

**Rule:** Exactly **one** UnrealEditor **or** one `-game` process owns the GPU on omni.

| Check | Cite |
|-------|------|
| Kill other editors/games **before** build or Gate 1 | BOTH-TRACKS Track A; RESUME playbook |
| Host is **iGPU-only** (Radeon 880M) | `G1-host-baseline/HOST_INVENTORY.md` |
| Live Coding lock → Build exit **6** | `G1-host-baseline/VERDICT.md` |
| Agents do not steal the window while Chris owns Track A | BOTH-TRACKS agent rule; UNLOCK mode C |

---

## 3. `LaunchClevelandRace.bat` — human-default contract

**Path:** `apps/unreal-akron-beta/LaunchClevelandRace.bat`

| Mode | EXTRA | Gate 1? |
|------|-------|---------|
| **HUMAN DEFAULT** `LaunchClevelandRace.bat [Sunset\|Twilight\|Midnight]` | `-ClevelandPreset=<preset> -log -windowed -ResX=1600 -ResY=900` | **YES** (Track A) |
| `playtest` | adds `-ClevelandAutoLap -ClevelandSkipIntro` | Debug only — not Gate 1 default |
| `nullrhi` | `-nullrhi -unattended ...` | **NEVER Gate 1 PASS** |

Always: Showcase GM via URL (`?game=/Script/raceGPSAkronBeta.ClevelandShowcaseGameMode`); **GlobalDefaultGameMode unchanged (CruiseSprint)**.

---

## 4. ViewportClosed / RequestExit — log grep cheat sheet

```text
raceGPS TrackB:
ViewportClosed
RequestExit
EndRace
RestartShowcase
UGameEngine::Tick.ViewportClosed
playtest=
```

| Hit | Meaning |
|-----|---------|
| `UGameEngine::Tick.ViewportClosed` → `RequestExit` | Engine null GameViewport (~**1.85s** after Racing on windowed FAIL) |
| `raceGPS TrackB: heartbeat ...` | Phase A TEMP probe |
| GameMode `RequestExit` ~L415 / ~L620 | **playtest-only** — ruled out when `playtest=0` |
| `EndRace` + finish HUD + R, **no** ViewportClosed | Attended PASS shape |

Smoking-gun FAIL (Track B dig): Racing @ 03:21:21.398 → ViewportClosed RequestExit @ 03:21:23.246; focus-keeper DEAD ~16ms.

---

## 5. Track B status board

| Phase | Status |
|-------|--------|
| **A — GameMode Tick probe** | **LANDED** — rebuild logged Succeeded with `-MaxParallelActions=1 -NoUBA` |
| **B — Viewport client subclass** | **HOLD** |
| Strip TEMP logs | After dig closes |

---

## 6. Hard bans

- Unattended `LaunchClevelandRace` / `-game` spam for Gate 1
- Claiming **NullRHI** / black void as Gate 1 PASS
- Flipping **GlobalDefaultGameMode** off CruiseSprint
- Second UnrealEditor on omni while another lane owns the GPU
- Re-enabling **UBA** as default without a measured non-OOM pass
- Selling empty Workshop/Race packaging targets as progress

---

## 7. Evidence drop naming (when Mode C unlocks)

Under `docs/evidence/grokbot/G6-race-base-mvp/`:

| Artifact | Naming / example |
|----------|------------------|
| Phase A rebuild (already on disk) | `track-b-phase-a-build.log` — UBT flags + `Result: Succeeded` |
| Attended Track B log | `track-b-attended-*.log` |
| Finish+R PASS note | `finish-r-PASS-*.txt` (+ shots) |
| FAIL notes | keep; **never overwrite** |