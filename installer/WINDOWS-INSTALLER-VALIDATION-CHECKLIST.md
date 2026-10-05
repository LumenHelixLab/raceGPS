# raceGPS Windows Installer Validation Checklist

Target installer
- `installer/raceGPS-v0.2.0-Win64-Setup.exe`

Required build payload before compiling NSIS
- `Build/Windows/Binaries/Win64/raceGPS.exe`
- `citypacks/akron-oh-beta-001/`

## A. Before building the installer

1. Package the game (UE5.5 + VS2022 required)
   ```powershell
   cd apps\unreal-akron-beta
   .\Build.bat
   ```
   `Build.bat` runs `scripts/stage-windows-installer.ps1` as its final step.

2. Or stage + compile manually
   ```powershell
   .\scripts\stage-windows-installer.ps1
   .\scripts\build-windows-installer.ps1
   ```

3. Confirm staged payload
   - `Build/Windows/Binaries/Win64/raceGPS.exe` exists
   - `Build/Windows/citypacks/akron-oh-beta-001/akron_routes.json` exists
   - `Build/Windows/installer-payload.json` exists

4. Confirm NSIS prerequisites
   - NSIS 3.x installed (`makensis` on PATH or under `Program Files (x86)\NSIS`)
   - Stock includes: `MUI2.nsh`, `LogicLib.nsh`, `nsDialogs.nsh`, `x64.nsh`, `WinVer.nsh`
   - RAM preflight uses built-in System plugin (`GlobalMemoryStatusEx`) — no extra plugins required

5. Expected output name
   - `installer/raceGPS-v0.2.0-Win64-Setup.exe`

## B. Install test on a clean Windows machine or VM

1. Copy installer to the target machine
2. Run as Administrator
3. On preflight page verify:
   - OS check renders (blocks Next on Windows < 10)
   - RAM check renders (warning only if below 8 GB)
   - Disk check renders (warning only if below 5 GB free)
   - DirectX line renders
   - VC++ runtime line renders
4. Continue install
5. Verify installed files under:
   - `C:\Program Files\raceGPS\`
6. Confirm these exist after install:
   - `C:\Program Files\raceGPS\Binaries\Win64\raceGPS.exe`
   - `C:\Program Files\raceGPS\citypacks\akron-oh-beta-001\`
   - `C:\Program Files\raceGPS\uninst.exe`
7. Verify shortcuts
   - Desktop shortcut launches `Binaries\Win64\raceGPS.exe`
   - Start menu shortcut launches
   - Uninstall shortcut exists and removes the app

## C. First-launch validation

1. Launch from desktop shortcut (not raw folder browse)
2. Verify app starts without missing-runtime error
3. Verify onboarding appears
4. Verify onboarding can reach city selection
5. Verify bundled Akron citypack is visible/selectable
6. Verify save/config path is created
   - `%LOCALAPPDATA%\raceGPS\Saved\Config\PlayerSettings.json`
7. Verify app reaches main menu

### C.8 World map gate (when AkronWorld.umap not cooked into build)

1. Launch game after install
2. On onboarding Step 0, confirm **World Map** row appears in preflight list
3. If map missing: **Next** is blocked; blocker explains missing world
4. From main menu, **Play** opens world content gate (not black screen)
5. **Verify installation** writes `%LOCALAPPDATA%\raceGPS\logs\preflight.log`
6. **Open setup guide** and **Reinstall** links open in browser

Pass if user always gets guided remediation instead of silent level load failure.

## D. Failure points to watch

1. Installer compiles but includes no game payload
   - Cause: `Build/Windows/` missing — run `Build.bat` or `stage-windows-installer.ps1` first
   - Fix: NSIS `File` directive no longer uses `/nonfatal`; compile fails if payload absent
2. Shortcut created but launch fails
   - Cause: shortcut pointed at `$INSTDIR\raceGPS.exe` instead of `Binaries\Win64\raceGPS.exe`
3. Installer completes but citypack missing
   - Cause: repo `citypacks\` not copied during staging
4. First launch fails on VC++ runtime
   - Cause: redistributable install/download failed (check installer log)
5. Preflight page compile error in NSIS
   - Cause: missing `System.nsh` or `nsDialogs.nsh`
6. Two finish pages shown
   - Cause: both custom FinishPage and `MUI_PAGE_FINISH` enabled (fixed — custom only)
7. Play launches to black screen / missing level
   - Cause: AkronWorld.umap not cooked; gate should appear instead (check `world-content-manifest.json`)

## E. Pass / fail summary

Pass if all are true:
- installer builds successfully from staged payload
- installer places game at `Binaries\Win64\raceGPS.exe`
- shortcuts and App Paths registry point at `Binaries\Win64\raceGPS.exe`
- bundled citypack is present
- first-run onboarding launches
- app reaches menu

Fail if any are false.