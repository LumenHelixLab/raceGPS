# G6 race-base MVP evidence

**Status at agent freeze (2026-09-25):** Gate 1 **FAIL-CLOSED**. Nothing in this folder is a PASS for human finish+R.

## Rule (Chris)
- Black void / NullRHI / ViewportClosed without finish HUD + R = **FAIL**
- PASS requires human Sunset Showcase: finish HUD + R restart + real scene stills + log

## Fail artifacts (do not rebrand as progress)
| File | Signal |
|------|--------|
| `finish-r-windowed-viewportclosed.log` / `finish-r-windowed-fail-note.txt` | Windowed Sunset → Racing → ViewportClosed ~2s |
| `finish-r-attempt2-viewportclosed.log` | ViewportClosed |
| `finish-r-attempt3-nullrhi-no-progress.log` | NullRHI - no progress (never PASS) |
| `finish-r-attempt1-died.log` | Process died |
| `finish-r-proof-note.txt` / `finish-r-proof-excerpt.txt` | Earlier proof attempts - not live human PASS |

## Code review vs live proof
- `review-20bada7-race-base.txt` = code-path review only
- Live human finish HUD + R remains **unproven**

## Resume
Only after Chris reopens agent game work / Gate 1. Prefer interactive human keep-alive viewport over short agent `-game` sessions.
