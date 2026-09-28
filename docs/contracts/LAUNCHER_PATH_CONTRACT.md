# Launcher Path Contract

This contract defines the Package and Dev paths consumed by the raceGPS launcher MVP. The Package path is intentionally honest about the current cook gate; Dev remains the team entry until a shipping build is available.

| Mode | Entry | Resolved default path |
|------|-------|-------------------------|
| Dev Race | `LaunchClevelandRace.bat` | `C:\projects\raceGPS-grokbot-cleveland\apps\unreal-akron-beta\LaunchClevelandRace.bat` |
| Dev map/game overrides (inside bat) | map `/Game/Maps/Cleveland5_0KmWorld` ; game `/Script/raceGPSAkronBeta.ClevelandShowcaseGameMode` ; UE `C:\Program Files\Epic Games\UE_5.7\Engine\Binaries\Win64\UnrealEditor.exe` ; uproject `...\raceGPSAkronBeta.uproject` | GlobalDefaultGameMode **unchanged** (CruiseSprint) |
| Package Race | Win64 shipping/game exe | `C:\projects\raceGPS-grokbot-cleveland\apps\unreal-akron-beta\PackagedBuilds\Win64\raceGPSRace.exe` |
| Package status (2026-09-28) | **awaiting build** | G4/Shipping archive empty until Chris unlocks cook |
| Workshop python | venv | `C:\projects\raceGPS-grokbot-cleveland\.venv-grokbot\Scripts\python.exe` |
| Workshop CLIs | rgpack / semantic | `python -m rgpack` with `PYTHONPATH`/`cwd` including `tools\`; `tools\akron-semantic-compiler\compile_akron.py`; `tools\universal-city-compiler\cli.py` |
| Logs | UE Saved/Logs | `C:\projects\raceGPS-grokbot-cleveland\apps\unreal-akron-beta\Saved\Logs` |
| Settings | AppData | `%AppData%\raceGPS\settings.json` |
| Legacy GPU lock bat (reference only) | `apps\unreal-akron-beta\raceGPS.bat` | Workshop vs Race lock under `Saved\raceGPS\gpu.lock` — launcher MVP navigates Workshop in-process and does not replace this bat yet |

## Forbidden launcher args

The human **Play Race** button must not pass:

- `nullrhi`
- `-unattended`
- `playtest` / `-ClevelandAutoLap`

These remain operator-only arguments on the bat CLI. The launcher must not use them for a human Play Race launch.

## Source notes

- [Wave 1 unlock note (2026-09-27)](../handoff/2026-09-27-WAVE1-UNLOCK.md) — unattended `LaunchClevelandRace` remains banned and the lane remains fail-closed.
- [Easy Test Beta launcher design (2026-09-27)](../handoff/2026-09-27-EASY-TEST-BETA-LAUNCHER-DESIGN.md) — Package vs Dev ownership, the empty G4/Shipping archive, and the documented Dev entry.
- [Easy Test Beta launcher implementation plan (2026-09-28)](../handoff/2026-09-28-EASY-TEST-BETA-LAUNCHER-PLAN.md) — Task 5 locked rows and verification commands.
