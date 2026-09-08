# FrameDiagnosticActor - how to place (G2)

1. Build/open `raceGPSAkronBetaEditor` (Win64 Development).
2. Open any map (e.g. `Content/Maps/AkronWorld`).
3. Place `FrameDiagnosticActor` (Place Actors panel search, or spawn).
4. With `bAutoDrawOnBeginPlay=true`, PIE or BeginPlay draws:
   - Red arm = +X east 100 m (10000 uu)
   - Green arm = +Y north 100 m
   - Blue arm = +Z up 100 m
   - Yellow lines = 7 m road edges (half-width 350 uu)
5. Editor ruler: lengths within **1 cm**; road width **700 uu +/-1**.
6. Log: `[raceGPS][FrameDiag] ... PASS` plus GeoToWorld 100m-east length.
7. Automation: Session Frontend -> Automation -> `raceGPS.Frame.A.*`
