# raceGPS — Tech / Spec Sheet (Human Handoff)

**Freeze timestamp:** 2026-09-25 ~00:45 ET  
**Document type:** Engineering handoff spec (not a marketing brief)

---

## A. Repository & host

| Field | Value |
|-------|--------|
| Primary worktree | `C:\projects\raceGPS-grokbot-cleveland` |
| Also present on omni | `C:\projects\racegps` (note: some bats historically pointed here — verify before launch) |
| Branch | `grokbot/cleveland-integration` |
| Tracking | `origin/grokbot/cleveland-integration` |
| Notable commit (Gate 1 fail-closed) | `b5e1b4b` docs(evidence): G6 windowed Sunset finish+R FAIL-CLOSED ViewportClosed |
| Host | omni (Windows), UE 5.7 installed |
| Uproject | `apps\unreal-akron-beta\raceGPSAkronBeta.uproject` |
| Targets | `raceGPSAkronBeta`, `raceGPSAkronBetaEditor` (existing). Workshop/Race game targets were planned, not required for this handoff. |

### Path hygiene

Launch scripts and docs may disagree between `C:\projects\racegps\...` and `C:\projects\raceGPS-grokbot-cleveland\...`. **Human team should grep bats for `PROJ=` and align to the worktree you actually open.**

---

## B. Engine & launch contracts

| Field | Spec |
|-------|------|
| Engine | UE **5.7** (`C:\Program Files\Epic Games\UE_5.7\...` typical) |
| Default GameMode | **CruiseSprint** — immutable for GlobalDefaultGameMode / Akron default |
| Cleveland Showcase launch | Override GameMode **only** via URL or bat |
| Example bat contract | `UnrealEditor.exe <uproject> "/Game/Maps/Cleveland5_0KmWorld?game=/Script/raceGPSAkronBeta.ClevelandShowcaseGameMode" -game` |
| Human Gate 1 launch (when reopened) | Showcase human bat / `LaunchClevelandRace.bat Sunset` — **no** `-ClevelandAutoLap` |
| Auto-still hook (in-tree) | `CaptureHeroStill` / HighResShot style path → ScreenshotDir; copies historically to temp hero PNGs |

### Map / geo

| Field | Spec |
|-------|------|
| Map | `/Game/Maps/Cleveland5_0KmWorld` |
| Place | Burke Lakefront Airport (BKL), Cleveland OH — Lake Erie **north**, downtown skyline **south** |
| Pack coords (provenance) | ~41.51722 N, 81.68306 W |
| Axis note (visual bar) | X=east, Y=north, 1 uu = 1 cm in documented Cleveland pipeline |
| Content fact | Map may already contain large T10 HISM city import; empty-runway stills are often **camera/spawn/lighting**, not missing downtown — do not “rebuild T10 city” to fix a north-runway frame |

---

## C. City pack — Burke GP 1997 + EZ variant

### Source pack `cleveland_burke_gp_1997`

Typical files (under `citypacks/cleveland/burke_gp_1997/` or mirrored citypacks):

| File | Role |
|------|------|
| `cleveland_burke_gp.xodr` | OpenDRIVE / shared geometry |
| `racing_line.json` | Historic / source racing line |
| `checkpoints.json` | Gate definitions |
| `manifest.json` | Pack manifest |
| `metadata.json` | Provenance / lengths |

Official-ish length target historically ~3389 m (1997 2.106 mi); measured pack line ~3275–3280 m band.

### EZ variant `cleveland_burke_gp_1997_ez` (accepted data-plane)

| File | Role |
|------|------|
| `racing_line_ez.json` | Forgiving smoothed line (~410 samples) |
| `checkpoints_ez.json` | Same topology, ~**35% wider** gates (e.g. 22 → 29.7 m first gate) |
| `manifest_ez.json` | Variant manifest; **shares source XODR** |

**Metrics snapshot (generation evidence):**

| Metric | Source | EZ |
|--------|--------|-----|
| Measured length (m) | 3275.82 | 3268.99 (Δ −6.83) |
| Max \|κ\| | 0.03427 | 0.03247 |
| Mean target speed (m/s) | 68.5 | 59.88 |
| Checkpoint gates | 12 | 12 |
| First gate width (m) | 22.0 | 29.7 |

**Reused env (do not replace with greenfield):**

- `skyline.json` (~45 silhouette volumes additive; distinct from T10 HISM count)
- `water.json` (Lake Erie nearfield)
- `track_dressing.json`
- `environment.json` (lighting pointers)

Policy: **reuse / wrap / light only**.

---

## D. Evidence layout

| Path | Contents / rule |
|------|-----------------|
| `docs/evidence/grokbot/burke-ez-ribbon/` | Generation evidence (README, metrics.json, ribbon_overlay.svg). **Stills slot empty at freeze.** PASS = overhead + driver UE frames that read as a track + eventually skyline/Erie |
| `docs/evidence/grokbot/burke-ez-visual/` | Optional Vehicle Arcade Sunset/Erie/skyline stills (never started) |
| `docs/evidence/grokbot/G6-race-base-mvp/` | Gate 1 attempts; `finish-r-PASS.txt` or FAIL + screenshot + log. Prior fails: viewport died, NullRHI no progress, ViewportClosed ~2s |
| `tools/burke_ez_preview/` | Zero-dep 2D overhead + fly-along preview. Overhead OK; fly-along screenshot QA **failing** at freeze |
| Omni preview copy | `C:\Users\cgp22\burke-ez-preview\preview.html` (if still present) |

### PASS / FAIL rules (Chris)

- **FAIL:** black void, NullRHI framed as success, empty north runway sold as “city missing” without checking camera
- **PASS (Burke visual):** readable EZ ribbon + vivid skyline + Lake Erie in stills
- **PASS (Gate 1):** human finishes, finish HUD, R restarts cleanly, real scene behind car, log+shot in G6 folder

---

## E. Race systems (Gate 1) — frozen contract

| Field | Spec |
|-------|------|
| Goal | Human-playable Showcase lap: finish HUD + R restart + intentional look |
| Code baseline | Race-base MVP (~`20bada7`) — session/HUD/soft AI on code path |
| Live proof | **Open** — blocked on keeping `-game` viewport alive through Racing→Finish→R |
| Last fail | Windowed Sunset → Racing → ViewportClosed ~2s; commit `b5e1b4b` |
| Chris hold | No new Gate 1 agent runs until he says otherwise (then freeze superseded this entirely for agents) |

---

## F. Vehicle / look (frozen)

| Field | Spec |
|-------|------|
| Handling goal | Arcade-fun (Midnight Club), not sim |
| Camera | Chase / hood; V16 chase + Sunset historically landed |
| Open | Side/¾ stills; CARLA glass; Burke Sunset+Erie+skyline wrap on EZ scene |
| Look director notes | MidnightRun / ClevelandLookDirector patterns in visual bar — night default for showcase photography |

---

## G. Held future work (do not start as “progress”)

1. **Two-app slice** — versioned `rgpack` Python schema + golden fixture; Unreal `raceGPSPack` read module; empty `raceGPSWorkshop` / `raceGPSRace` targets; `raceGPS.bat` GPU lock. Plan: `docs/superpowers/plans/2026-09-24-racegps-two-app-slice1-2.md` (tasks unchecked at last agent read).
2. OSM bbox import, Race pawn on centerline from pack, garage loadout, full AI+EndRace polish beyond MVP.
3. Course Architect versioned upgrades v2 barriers/lighting v3 landmarks — only after EZ visual PASS.

---

## H. Suggested verification commands (human)

```bat
REM 1) Editor build (example — adjust Engine path)
"%PROGRAMFILES%\Epic Games\UE_5.7\Engine\Build\BatchFiles\Build.bat" raceGPSAkronBetaEditor Win64 Development -Project="C:\projects\raceGPS-grokbot-cleveland\apps\unreal-akron-beta\raceGPSAkronBeta.uproject"

REM 2) Showcase launch without flipping GlobalDefaultGameMode
apps\unreal-akron-beta\LaunchCleveland.bat
```

Then capture stills to `docs\evidence\grokbot\burke-ez-ribbon\` with filenames that state PASS/FAIL and camera (e.g. `ez-overhead-PASS.png`, `ez-driver-PASS.png`).

---

## I. Open questions for human team (not blockers to reading code)

1. Canonical disk root: `raceGPS-grokbot-cleveland` vs `racegps` — unify bats.
2. Whether Cesium is already in-tree for this uproject; if not, prefer non-Cesium in-tree skyline/water first (Chris: reuse, don’t install speculative stacks).
3. Whether Gate 1 viewport-close is agent-session lifetime vs game bug — human interactive run is the fastest discriminator.

---

## J. File index for this freeze pack

| File | Purpose |
|------|---------|
| `docs/handoff/2026-09-25-AGENT-FREEZE-STATUS.md` | Short stop-the-line status |
| `docs/handoff/2026-09-25-HUMAN-TEAM-HANDOFF.md` | Narrative handoff |
| `docs/handoff/2026-09-25-TECH-SPEC-SHEET.md` | This tech/spec sheet |
### Gate 1 resume playbook
`docs/handoff/2026-09-25-GATE1-RESUME-PLAYBOOK.md` (mirrored from Documents). FAIL-CLOSED until interactive viewport keep-alive + real finish HUD + R evidence.

