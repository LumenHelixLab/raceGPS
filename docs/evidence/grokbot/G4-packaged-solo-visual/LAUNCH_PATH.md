# G4 Launch path — Cleveland solo (PROVISIONAL)

## Product
raceGPS: Cleveland Historic Circuit (provisional Burke 1997 pack; not certified 2006).

## Defaults unchanged
- `GlobalDefaultGameMode=/Script/raceGPSAkronBeta.CruiseSprintGameMode`
- `CityId=akron-oh-beta-001`
Cleveland is **map override + LaunchCleveland only**.

## Editor / -game
```
apps\unreal-akron-beta\LaunchCleveland.bat Sunset
apps\unreal-akron-beta\LaunchCleveland.bat Twilight
apps\unreal-akron-beta\LaunchCleveland.bat Midnight
apps\unreal-akron-beta\LaunchCleveland.bat nullrhi Sunset
```

Equivalent:
```
UnrealEditor.exe raceGPSAkronBeta.uproject /Game/Maps/Cleveland5_0KmWorld?game=/Script/raceGPSAkronBeta.ClevelandSoloGameMode -game -ClevelandPreset=Sunset
```

## What loads
- Map: `Cleveland5_0KmWorld` (baked T10 city + water)
- GameMode: `AClevelandSoloGameMode` (solo ChaosVehiclePawn; no AI grid — G5)
- Look: `AClevelandLookDirector` presets Sunset / Twilight / Midnight
- Pack: `citypacks/cleveland/burke_gp_1997` (junction under apps) for S/F teleport from `racing_line.json`

## Packaging
`scripts\package_cleveland_solo.ps1 -Config Development` (or `-Config Shipping`).
Cooks Win64 archive under `docs/evidence/grokbot/G4-packaged-solo-visual/package/`.
