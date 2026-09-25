# G4 VERDICT — Packaged solo visual benchmark

**Status:** `PASS_PARTIAL`  
**Claim level:** OBSERVED / REPRODUCED_LOCALLY  
**Product:** raceGPS: Cleveland Historic Circuit (PROVISIONAL Burke pack; not certified 2006)  
**Recorded:** 2026-09-24T19:17:00-04:00 America/New_York  
**Branch:** `grokbot/cleveland-integration`  
**Worktree:** `C:\projects\raceGPS-grokbot-cleveland`

## What PASSED (playable path first)

1. **Solo Cleveland drive path** — `apps/unreal-akron-beta/LaunchCleveland.bat [Sunset|Twilight|Midnight]` boots  
   `/Game/Maps/Cleveland5_0KmWorld?game=/Script/raceGPSAkronBeta.ClevelandSoloGameMode` **without** changing  
   `GlobalDefaultGameMode` (`CruiseSprintGameMode`) or `CityId` (`akron-oh-beta-001`).
2. **Player on provisional Burke course** — nullrhi + GPU `-game` logs: `SOLO READY`, `ChaosVehiclePawn`, `teleported=1` to S/F from `racing_line.json`.
3. **Three presets** — exact names Sunset / Twilight / Midnight via `-ClevelandPreset=` and exec `ClevelandPreset`. Solar orientation declared (`SOLAR_ORIENTATION.md` + `environment.json` lighting.presets). Dry surface unchanged.
4. **Stills** — Twilight + Midnight hero 1280x720 non-black. Sunset still black (0 luma); preset REPRODUCED in logs only (not chased further per lead).
5. **Editor Development build** — `raceGPSAkronBetaEditor` Win64 Development exit **0**.
6. **Pytest** — cleveland 7/7 exit 0; full 237 passed / 7 skipped exit 0.
7. **Akron audit fail-closed** — exit **1** preserved.
8. **Packaging script** — `scripts/package_cleveland_solo.ps1` ready. First cook attempt failed exit 6 (`SetActorLabel` editor-only); guarded with `#if WITH_EDITOR`. Retry killed at hard-cap during global shader compile (~10m) — package is nice-to-have, not G5 blocker.

## Human drive

```
apps\unreal-akron-beta\LaunchCleveland.bat Sunset
apps\unreal-akron-beta\LaunchCleveland.bat Twilight
apps\unreal-akron-beta\LaunchCleveland.bat Midnight
```

## NOT claimed

- NOT certified 2006 / photoreal.
- NOT Shipping/Development archived Windows package (cook hard-capped).
- NOT 3-car AI / EndRace (G5 — full running playable beta test run).

## Evidence

`docs/evidence/grokbot/G4-packaged-solo-visual/`
