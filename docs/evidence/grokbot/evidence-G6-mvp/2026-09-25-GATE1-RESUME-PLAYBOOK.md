**Strategy lock:** BOTH — see `2026-09-25-GATE1-BOTH-TRACKS.md`.

# Gate 1 resume playbook (freeze-safe analysis) - 2026-09-25

**Status:** FAIL-CLOSED. Do not reopen agent -game spam until Chris unlocks AND viewport keep-alive is solved.

## What is proven
1. **Code path (nullrhi + ProofFinishR):** ForceFinish → finish HUD → R RestartShowcase without RequestExit can log PASS under nullrhi (inish-r-proof-note.txt). Chris rejects nullrhi as Gate 1 evidence.
2. **Windowed Sunset human path:** Countdown → Racing succeeds, then **ViewportClosed ~2s after Racing** via `UGameEngine::Tick.ViewportClosed` → RequestExit. Never reaches EndRace / finish HUD / R.
3. **AutoDrive stuck:** even when alive longer, drive-dump shows thr=0/speed=0 at Racing release (cars not moving) - separate Vehicle Arcade issue; ForceFinish was a workaround, not the product proof.

## What is NOT Gate 1 PASS
- Any nullrhi / NullRHI / -unattended proof
- Black void stills
- ForceFinish without a driven lap in a real windowed/fullscreen viewport
- Agent sessions that die on ViewportClosed

## Likely causes of ViewportClosed (ordered for next debug when unlocked)
1. **Session/focus loss on omni** - remote agent -game window not treated as focused; OS or UE closes viewport (focus-keeper was tried; still died ~2s after Racing).
2. **-game without a durable interactive owner** - needs Chris (or a human-attended session) to keep the window open through a full lap.
3. **Less likely:** intentional RequestExit from playtest (logs show playtest=0 on the failing windowed run).

## Resume recipe (when Chris unlocks)
1. One UnrealEditor/game owner on omni only.
2. Human launches `LaunchClevelandRace.bat Sunset` (or current Showcase human bat) **windowed or fullscreen**, NO `-nullrhi`, NO `-ClevelandAutoLap` unless debugging.
3. Keep window focused; complete a real lap (or confirm AutoDrive actually throttles - if thr stays 0, Vehicle Arcade owns that before Gate 1).
4. Capture: finish HUD screenshot, R restart screenshot, log excerpt showing EndRace + RestartShowcase without RequestExit.
5. Drop evidence under `docs/evidence/grokbot/G6-race-base-mvp/` with `finish-r-PASS` naming - never overwrite FAIL notes.

## Parallel visual gate (also frozen)
Burke EZ data-plane accepted; stills empty. Visual PASS = EZ ribbon + vivid skyline + Erie stills under `docs/evidence/grokbot/burke-ez-ribbon/`. Prefer that backdrop before celebrating Gate 1.

## Owner split on reopen
| Lane | First job |
|------|-----------|
| Chris / interactive | Keep viewport alive for one real Sunset run |
| Race Systems | Wire evidence naming; confirm finish HUD + R logs on live run |
| Vehicle Arcade | If thr=0 at Racing release, fix AutoDrive/throttle before blaming HUD |
| Course Architect | EZ stills once editor allowed |
| Unreal PM | Gate unlock criteria + evidence QA |

Evidence roots: `docs/evidence/grokbot/G6-race-base-mvp/`, Documents handoff pack.

