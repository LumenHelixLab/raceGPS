# Gate 1 Track B dig — ViewportClosed (~2026-09-25)

**Owner:** Race Systems  
**Companion:** `2026-09-25-GATE1-BOTH-TRACKS.md` (Chris unlocked BOTH)  
**Rule:** nullrhi / ForceFinish ≠ Gate 1 PASS. No unattended LaunchClevelandRace spam.

## Smoking-gun timeline (windowed Sunset FAIL)

From windowed fail excerpt / note:

| Time (log) | Event |
|---|---|
| 03:21:17.470 | flags `playtest=0 autodive=1 skipIntro=1 proofFinishR=0` |
| 03:21:17.582 | Countdown armed |
| 03:21:21.398 | **Racing** |
| 03:21:23.246 | `FPlatformMisc::RequestExit(..., UGameEngine::Tick.ViewportClosed)` (~**1.85s** after Racing) |
| focus-keeper | start then **DEAD ~16ms** — HWND keep failed |

No EndRace / finish HUD / RestartShowcase in that session.

## Ruled out (code-backed)

`ClevelandShowcaseGameMode.cpp` `RequestExit` sites are **playtest-only**:
- ~L415 — stuck speed0 playtest quit (`bPlaytestLap`)
- ~L620 — playtest EndRace complete → RequestExit

FAIL log has `playtest=0` and **no** playtest quit line → GameMode did not request exit.

`RestartShowcase` (~L646) explicitly logs no RequestExit — never reached.

`GameViewportClient` include in Showcase GM is used for **CaptureStill** screenshot (~L527), not close handling. No project `UGameViewportClient` subclass found under `Source/`.

## Ranked hypotheses

1. **HIGH — session / HWND ownership (agent-spawned `-game`)**  
   Unattended `Start-Process` / remote agent session: viewport destroyed when focus/session drops → engine Tick sees null GameViewport → ViewportClosed exit. Focus-keeper dying in ~16ms supports this.  
   **Discriminating test:** Track A attended (Chris double-clicks `LaunchClevelandRace.bat Sunset`, keeps focus 2–3 min). If survives ≫60s after Racing → ownership, not race logic.

2. **MED — `start "title" UnrealEditor … -game` parent/console lifetime**  
   Human bat uses `start "raceGPS Cleveland Race" … -game`. Usually detaches; verify attended Explorer launch vs agent-spawned still differs.

3. **LOW-MED — slate/window deactivate under `-windowed` without durable owner**  
   Deactivate/close message path nulls viewport. Instrumentation (patch plan) stamps deactivate vs destroy vs GameViewport null.

4. **LOW — intentional game quit** — ruled out for playtest=0 path.

5. **OUT OF SCOPE for ViewportClosed** — AutoDrive thr/speed 0 (Vehicle Arcade). Explains stuck cars, not ViewportClosed.

## Engine note

Exit reason string is `UGameEngine::Tick.ViewportClosed` — standard UE path when the game viewport is gone during Tick. Prefer temporary viewport/deactivate logs over guessing bat flags.

## Attended A/B (Track A owns reproduce)

| Result after Racing | Conclusion |
|---|---|
| Window lives ≥60–120s (ideally through finish+R) | Root cause = session/ownership; stop agent unattended Gate 1 launches |
| Still ViewportClosed ~2s while Chris focused | Escalate slate/window/DPI; apply instrumentation; try one fullscreen attended run |

## Do not

- Spam LaunchClevelandRace from unattended sessions
- Claim nullrhi / ClevelandProofFinishR as Gate 1 PASS
- Flip GlobalDefaultGameMode away from CruiseSprint
- Unfreeze Burke stills / Course Architect / Vehicle Arcade without Chris

## Evidence pointers

- `finish-r-windowed-fail-note.txt` / viewportclosed excerpt / focuskeeper
- Prior nullrhi proof note (explicitly **not** Gate 1)
- Patch plan: `2026-09-25-GATE1-TRACK-B-PATCH-PLAN.md`
