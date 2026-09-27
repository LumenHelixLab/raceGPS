# Race Systems -- training annotations

**Lane:** Race Systems (session flow, HUD, scoring, grid, checkpoints, packaged Race UX)
**Rule:** cite-and-note only. No clones, no Marketplace, no omni UnrealEditor / PIE / LaunchClevelandRace.
**Source of truth (synthesis):** `../agent-training/` (Unreal PM owns cross-cut)
**Checked:** 2026-09-25

## Files

| File | Covers |
|------|--------|
| [2026-09-25-PACK-02-PC-ENHANCED-INPUT-ANNOTATIONS.md](./2026-09-25-PACK-02-PC-ENHANCED-INPUT-ANNOTATIONS.md) | Phase C pack 02 -- PlayerController + Enhanced Input |
| [2026-09-25-PACK-04-SIMPLE-RACER-ANNOTATIONS.md](./2026-09-25-PACK-04-SIMPLE-RACER-ANNOTATIONS.md) | Phase C pack 04 -- unreal-simple-racer patterns (README only) |
| [2026-09-25-PACK-05-UETRAFFICGAME-ANNOTATIONS.md](./2026-09-25-PACK-05-UETRAFFICGAME-ANNOTATIONS.md) | Phase C pack 05 -- UETrafficGame patterns (README + wiki hub) |

## Hard constraints (raceGPS)

- Own countdown -> racing -> finish HUD -> R restart; grid + ordered checkpoints; NeonHUD bind path.
- GlobalDefaultGameMode stays CruiseSprint (Showcase override only).
- Gate 1 / Burke visual path stays HOLD -- annotations are docs only.
- Human Race bat: no default `-ClevelandAutoLap`; RequestExit only for playtest AutoLap paths.
- Black void / NullRHI / ViewportClosed-as-PASS = FAIL when game work reopens.
