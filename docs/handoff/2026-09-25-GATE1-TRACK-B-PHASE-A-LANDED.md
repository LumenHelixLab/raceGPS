# Gate 1 Track B — Phase A TEMP probe LANDED (2026-09-25)

**Owner:** Race Systems  
**Prototyper green:** Phase A only (TEMP GameMode Tick probe). Phase B viewport subclass still HOLD.  
**Build:** `raceGPSAkronBetaEditor` Win64 Development — **Succeeded** (single-thread, `-NoUBA`; prior UBA attempt OOM-killed).

## Code
- File: `apps/unreal-akron-beta/Source/raceGPSAkronBeta/Private/ClevelandShowcaseGameMode.cpp`
- `#include "Misc/App.h"` // TEMP Track B dig
- TEMP block at start of `Tick` after `Super::Tick`:
  - 1 Hz heartbeat: `raceGPS TrackB: heartbeat worldVP=%d engineVP=%d focus=%d state=%s`
  - One-shot Warning on viewport edge while Racing: `raceGPS TrackB: VIEWPORT LOST while Racing ...`
- Showcase GameMode only. **CruiseSprint / GlobalDefaultGameMode untouched.**

## Grep after attended Track A
```
raceGPS TrackB:
ViewportClosed
```

## Next (Chris owns)
1. Explorer double-click `LaunchClevelandRace.bat Sunset` (human default — no AutoLap / nullrhi).
2. Keep window focused ≥60–120s after Racing (ideally finish+R).
3. Drop log excerpt as `docs/evidence/grokbot/G6-race-base-mvp/track-b-attended-*.log` + short note.

## Do not
- Unattended LaunchClevelandRace
- Claim nullrhi PASS
- Leave TEMP logs after dig closes
