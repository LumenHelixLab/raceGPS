# raceGPS Windows Installer Validation Checklist

Target installer
- `installer\raceGPS-v0.2.0-Win64-Setup.exe` (relative to racegps repo root)

Required build payload before compiling NSIS
- `apps/unreal-akron-beta/Build/Windows\` (full cooked/staged output from Build.bat or `python scripts\build.py`), containing the game exe (see B.2) and cooked `.pak` content
- `citypacks\` (akron-oh-beta-001 and templates)

## A. Before building the installer

1. Confirm packaged game payload exists (user: run Build.bat or equivalent until complete)
   - Verify `apps/unreal-akron-beta/Build/Windows\` exists
   - Verify it contains the packaged game output and cooked `.pak` files
2. Confirm citypacks exist
   - Verify `citypacks\akron-oh-beta-001\` (has .xodr + json manifests)
3. Confirm NSIS prerequisites on build machine
   - NSIS 3.x installed (https://nsis.sourceforge.io/Download)
   - makensis in PATH or at standard `C:\Program Files (x86)\NSIS\makensis.exe`
4. Compile (recommended):
   - From repo root: `pwsh -File scripts\build-windows-installer.ps1`
   - The script **hard-fails (exit 2) on a placeholder/incomplete payload** (no `.pak` + tiny exe). Use `-AllowPlaceholder` only for installer-UI smoke tests.
   - To package a timestamped build.py archive: `-PayloadDir apps\unreal-akron-beta\Build\Windows\<timestamp>`
   - Or manually: `cd installer; makensis /V2 racegps-setup.nsi`
5. Expected output name
   - `installer\raceGPS-v0.2.0-Win64-Setup.exe`

## B. Install test on a clean Windows machine or VM

1. Copy installer to the target machine
2. Run as Administrator
3. There is **no in-installer preflight page** (removed for stability; payload validation happens in the build script). The wizard is: Welcome → License → Components → Install Dir → Install → Finish (with "Launch raceGPS" checkbox).
4. Continue install
5. Verify installed files under:
   - `C:\Program Files\raceGPS\`
6. Confirm these exist after install:
   - `C:\Program Files\raceGPS\Windows\raceGPSAkronBeta.exe` (UE bootstrap; exact subpath is auto-detected by the build script and baked into shortcuts — check the desktop shortcut target if unsure)
   - `C:\Program Files\raceGPS\citypacks\`
   - `C:\Program Files\raceGPS\generated\` (level specs, when present in repo)
   - `C:\Program Files\raceGPS\uninst.exe`
7. Verify shortcuts
   - Desktop shortcut launches
   - Start menu shortcut launches
   - Uninstall shortcut exists

## C. First-launch validation

1. Launch via the desktop shortcut
2. Verify app starts without missing-runtime error
3. Verify onboarding appears
4. Verify onboarding can reach city selection
5. Verify bundled Akron citypack is visible/selectable
6. Verify save/config path is created
   - `<install>\Windows\raceGPSAkronBeta\Saved\Config\PlayerSettings.json` (packaged builds write under the install tree, not `%LOCALAPPDATA%`)
7. Verify app reaches main menu

## D. Failure points to watch

1. Build script exits 2 ("placeholder / incomplete payload")
   - Cause: no cooked `.pak` content in `apps/unreal-akron-beta/Build/Windows\`. Re-run the full UE package step. Do not ship a placeholder build.
2. Shortcut created but launch fails
   - Cause: exe path baked at compile time doesn't match the archive layout. The build script auto-detects `Windows\raceGPSAkronBeta.exe` → `Windows\raceGPSAkronBeta\raceGPSAkronBeta.exe` → `raceGPS.exe`; if your archive differs, pass `-PayloadDir` at the correct archive root or check `GAME_EXE_REL` in the makensis output.
3. Installer completes but citypack missing
   - Cause: repo `citypacks\` not copied (NSIS has explicit copy from root citypacks)
4. First launch fails on VC++ runtime
   - Cause: redistributable download/install failed at install time (exit code is now logged in install details). Manual install of vc_redist.x64.exe as fallback.
5. Menu never offers Cleveland / non-Akron city
   - Cause: `generated\*_LevelSpec.json` missing from the install tree (NSI copies them from the repo `generated\` folder).

## E. Pass / fail summary

Pass if all are true:
- build script succeeds and produces the .exe **without** `-AllowPlaceholder`
- installed `C:\Program Files\raceGPS\` contains the game exe (shortcut target) + citypacks\ + generated\
- desktop + start menu shortcuts created and point correctly
- bundled akron citypack visible
- first launch reaches onboarding without missing-runtime popup
- reaches main menu and can select/start a race with the included citypack

Fail if any are false.
