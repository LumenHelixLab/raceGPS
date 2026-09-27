# Human team — first hour on raceGPS (freeze-aware) - 2026-09-25

Pair with `2026-09-25-HUMAN-TEAM-HANDOFF.md` and `2026-09-25-TECH-SPEC-SHEET.md`.

## Minute 0–10 — orient
1. Read `2026-09-25-CHECKBACK-BRIEFING.md` (agent while-away summary).
2. Confirm freeze / unlock mode with Chris (`2026-09-25-UNLOCK-CRITERIA.md` modes A/B/C/D).
3. Open G6 evidence README: Gate 1 is **FAIL-CLOSED**. `finish-r-proof-*` is NullRHI ForceFinish — **not** PASS.

## Minute 10–25 — Gate 1 (only if unlock mode C)
1. One machine owner on omni; no competing UnrealEditor.
2. Human Showcase / LaunchClevelandRace bat — windowed or fullscreen, **no** `-nullrhi`.
3. Keep window focused: Countdown → Racing → lap → finish HUD → R.
4. If viewport dies ~2s after Racing: known failure (`finish-r-windowed-viewportclosed*` / playbook). Capture one log+note; do not spam relaunches.
5. Write `finish-r-PASS*` only when real scene + finish HUD + R are proven.

## Minute 10–25 — Visual (only if unlock mode B)
1. Burke EZ data under handoff + `docs/evidence/grokbot/burke-ez-ribbon/`.
2. Capture overhead + driver stills with vivid skyline + Erie (not void).
3. Store stills under that evidence folder.

## Minute 25–45 — vehicle feel
- If cars sit thr=0/speed=0 at Racing release, fix AutoDrive/throttle before blaming HUD.
- Arcade-fun target, not sim fidelity.

## Minute 45–60 — evidence hygiene
- Compile ≠ playable. NullRHI ≠ visual PASS. Void ≠ PASS.
- Twin truth: `Documents\raceGPS-handoff` + project `docs\handoff` / `docs\evidence\grokbot`.
- Skills: `AGENT-SKILL-MAP.md` and fleet `unreal-game-dev`.

## Do not
- Treat NullRHI ForceFinish as Gate 1 done
- Flip GlobalDefaultGameMode away from the CruiseSprint / Showcase race mode
- Start GPS/Workshop map builder before race base feels like a game (unless Chris overrides)
