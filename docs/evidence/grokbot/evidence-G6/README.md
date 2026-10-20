# G6 race-base MVP evidence — FAIL-CLOSED (2026-09-25)

**Gate 1 status: FAIL-CLOSED / HOLD.** Do not treat any file in this folder as Gate 1 PASS.

## Read first
- `2026-09-25-GATE1-RESUME-PLAYBOOK.md` — ViewportClosed RCA + reopen recipe
- Documents pack: `C:\Users\cgp22\Documents\raceGPS-handoff\2026-09-25-CHECKBACK-BRIEFING.md`

## Naming legend
| Pattern | Meaning |
|---------|---------|
| `*viewportclosed*` / `*windowed-fail*` | Human-path FAIL (Racing then viewport died ~2s) |
| `*nullrhi*` / `finish-r-proof-*` | Code-path ForceFinish under NullRHI — **NOT Gate 1 PASS** (Chris rejects) |
| `finish-r-PASS*` | Reserved for real windowed/fullscreen finish HUD + R with scene — **none yet** |
| void / black stills | Never PASS |

## Key FAIL artifacts (kept for RCA)
- `finish-r-windowed-fail-note.txt` + `finish-r-windowed-viewportclosed.log`
- `finish-r-attempt2-viewportclosed.log`
- `finish-r-attempt3-nullrhi-no-progress.log`
- `finish-r-proof-note.txt` — documents nullrhi ForceFinish logs; rejected as Gate 1 evidence

## Smoke / build (not Gate 1)
- `raceGPSAkronBeta-smoke.log`, `smoke-*`, `ue-*-build.log`, `review-20bada7-race-base.txt`

Updated by Prototyper freeze-safe grind.
