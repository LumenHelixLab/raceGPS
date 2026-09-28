# Unlock criteria cheat sheet - 2026-09-25

Use when Chris reopens agent or human game work. Freeze holds until then.

## A — Keep freeze (default)
- Agents: docs/training only
- No editor, no LaunchClevelandRace, no Gate 1 spam

## B — Reopen visual lane only
- Course Architect: Burke EZ overhead + driver stills (real UE, not void)
- Drop under `docs/evidence/grokbot/burke-ez-ribbon/`
- Vehicle Arcade visual floor after stills exist
- Race Systems / Gate 1 still HOLD

## C — Reopen Gate 1 (interactive)
1. Chris (or attended session) owns one Showcase window — keep focused
2. `LaunchClevelandRace.bat Sunset` (or current human bat) — **no** `-nullrhi`
3. Real lap or confirmed AutoDrive throttle (thr≠0); finish HUD; press R
4. Evidence: `finish-r-PASS` note + screenshot + log under G6
5. Follow `2026-09-25-GATE1-RESUME-PLAYBOOK.md`

## D — Full agent game work
- Requires explicit Chris unlock beyond B/C
- One UnrealEditor owner on omni
- Unreal PM owns unlock criteria + evidence QA

## Never PASS
NullRHI, black void, ViewportClosed early exit, ForceFinish without driven lap in real viewport.
## Gate 1 strategy lock (2026-09-25)
Chris answered unblock widget with **BOTH** — see `2026-09-25-GATE1-BOTH-TRACKS.md`.
Track A = interactive keep-alive (human). Track B = ViewportClosed dig. NullRHI still not PASS.
