# Visual floor V16 — 2026-09-24

## Changes
- DayNightCycle: SceneRoot (Movable) so SkyAtmosphere/SkySphere/Clouds attach (was Static-on-Movable-Sun abort -> black void)
- Chase: V16 RACE-FOLLOW arm=680 FOV=75 inherit yaw pitch=-12 (was WORLD-SOUTH absolute look into -Y void)
- Sunset: sunI=4.20 skyI=2.40 AutoExposureBias lift + RecaptureSky

## Log proof (LaunchClevelandRace Sunset human)
- EnsureCarlaChargerDoors attached=9 missing=0 on BP_DodgeCharger2024_C_0/1/2
- applied chase framing V16 RACE-FOLLOW arm=680 FOV=75 ... armPitch=-12.0
- look FINAL [Sunset]: hour=18.75 sunI=4.20 skyI=2.40
- No SkyAtmosphere AttachTo abort (prior run had SunLight<-SkySphere/Atmosphere/Clouds abort)

## Still open
- CARLA glass/lights LoadErrors: Mini2024 material deps missing (can still read hollow/wrong mats)
- Side/3/4 screenshot pending for door visibility claim
