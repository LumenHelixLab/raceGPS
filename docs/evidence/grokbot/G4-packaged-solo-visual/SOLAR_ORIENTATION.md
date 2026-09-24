# G4 solar orientation (declared)

Frame A: Z-up, X=east, Y=north, 1uu=1cm.

`ADayNightCycle` model: `SunAngle=(hour/24-0.25)*360`; `Pitch=-sin(SunAngle)*80`; `Yaw=SunAngle+90`.
Geometric sunset in this model ~18:00 (Pitch~0, Yaw~270 west). Not an arbitrary sun-behind-skyline from every camera.

Night presets use `bMoonAtNight`: pitch locked to -46°, yaw 35° (NE sidelight so downtown south of Burke is readable).

| Preset | Local hour | Model SunAngle° | Declared pitch/yaw (day model) | Observed FINAL (nullrhi) | Surface |
|---|---|---|---|---|---|
| Sunset | 18.75 | 191.25 | pitch≈15.6 yaw≈281.25 (UE may normalize yaw) | hour=18.75 sunI=2.10 sunPitch=15.6 sunYaw=-78.7 skyI=1.05 | dry unchanged |
| Twilight | 20.00 | 210.0 | day-model would be below horizon; moon override | hour=20.00 sunI=1.70 sunPitch=-46.0 sunYaw=35.0 skyI=1.60 | dry unchanged |
| Midnight | 22.00 | 240.0 | moon override | hour=22.00 sunI=2.40 sunPitch=-46.0 sunYaw=35.0 skyI=2.20 | dry unchanged |

Source of truth also in `citypacks/cleveland/burke_gp_1997/environment.json` → `lighting.presets`.
