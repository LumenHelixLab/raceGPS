# G5 Launch path - Cleveland race (PROVISIONAL)

## Product
raceGPS: Cleveland Historic Circuit (provisional Burke 1997 pack; not certified 2006).

## Defaults unchanged
- `GlobalDefaultGameMode=/Script/raceGPSAkronBeta.CruiseSprintGameMode`
- `CityId=akron-oh-beta-001`
Cleveland race is **map override + LaunchClevelandRace only**.

## Commands
```
apps\unreal-akron-beta\LaunchClevelandRace.bat Sunset
apps\unreal-akron-beta\LaunchClevelandRace.bat Twilight
apps\unreal-akron-beta\LaunchClevelandRace.bat Midnight
apps\unreal-akron-beta\LaunchClevelandRace.bat playtest
apps\unreal-akron-beta\LaunchClevelandRace.bat nullrhi Sunset
apps\unreal-akron-beta\LaunchCleveland.bat race playtest
```

Equivalent:
```
UnrealEditor.exe raceGPSAkronBeta.uproject /Game/Maps/Cleveland5_0KmWorld?game=/Script/raceGPSAkronBeta.ClevelandShowcaseGameMode -game -ClevelandPreset=Sunset -ClevelandAutoLap -ClevelandSkipIntro
```

## What loads
- Map: Cleveland5_0KmWorld
- GameMode: AClevelandShowcaseGameMode (3-slot grid: 1 player + 2 RaceAIDriverController)
- Vehicles: BP_DodgeCharger2024 Chaos pawns
- Pack: citypacks/cleveland/burke_gp_1997 racing_line + checkpoints
- Look: AClevelandLookDirector Sunset/Twilight/Midnight