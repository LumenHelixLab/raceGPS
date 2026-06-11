# raceGPS Windows Installer Validation Checklist

Target installer
- `D:\projects\racegps\installer\raceGPS-v0.2.0-Win64-Setup.exe`

Required build payload before compiling NSIS
- `D:\projects\racegps\Build\Windows\`
- `D:\projects\racegps\citypacks\`

## A. Before building the installer

1. Confirm packaged game payload exists
   - Verify `D:\projects\racegps\Build\Windows\` exists
   - Verify it contains the packaged game output and `raceGPS.exe`
2. Confirm citypacks exist
   - Verify `D:\projects\racegps\citypacks\akron-oh-beta-001\`
3. Confirm NSIS prerequisites
   - NSIS 3.x installed
   - `nsDialogs.nsh` available
4. Compile:
   - Open `D:\projects\racegps\installer\racegps-setup.nsi`
   - Build installer
5. Expected output name
   - `raceGPS-v0.2.0-Win64-Setup.exe`

## B. Install test on a clean Windows machine or VM

1. Copy installer to the target machine
2. Run as Administrator
3. On preflight page verify:
   - OS check renders
   - RAM check renders
   - Disk check renders
   - DirectX line renders
   - VC++ runtime line renders
4. Continue install
5. Verify installed files under:
   - `C:\Program Files\raceGPS\`
6. Confirm these exist after install:
   - `C:\Program Files\raceGPS\raceGPS.exe`
   - `C:\Program Files\raceGPS\citypacks\`
   - `C:\Program Files\raceGPS\uninst.exe`
7. Verify shortcuts
   - Desktop shortcut launches
   - Start menu shortcut launches
   - Uninstall shortcut exists

## C. First-launch validation

1. Launch `raceGPS.exe`
2. Verify app starts without missing-runtime error
3. Verify onboarding appears
4. Verify onboarding can reach city selection
5. Verify bundled Akron citypack is visible/selectable
6. Verify save/config path is created
   - `%LOCALAPPDATA%\raceGPS\Saved\Config\PlayerSettings.json`
7. Verify app reaches main menu

## D. Failure points to watch

1. Installer compiles but includes no game payload
   - Cause: `D:\projects\racegps\Build\Windows\` missing or wrong packaging layout
2. Shortcut created but launch fails
   - Cause: `raceGPS.exe` not present at `$INSTDIR`
3. Installer completes but citypack missing
   - Cause: repo `citypacks\` not copied
4. First launch fails on VC++ runtime
   - Cause: redistributable install/download failed
5. Preflight page compile error in NSIS
   - Cause: missing `nsDialogs.nsh`

## E. Pass / fail summary

Pass if all are true:
- installer builds successfully
- installer places `raceGPS.exe` in install dir
- shortcuts work
- bundled citypack is present
- first-run onboarding launches
- app reaches menu

Fail if any are false.
