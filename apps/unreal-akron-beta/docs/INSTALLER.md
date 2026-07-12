# raceGPS Installer & Onboarding Guide

> **Version:** 0.2.0  
> **Platforms:** Windows 10/11 (x64), Linux (Ubuntu 22.04+)

---

## Quick Start (Recommended)

### Windows
1. Download `raceGPS-v0.2.0-Win64-Setup.exe` from [Releases](https://github.com/LumenHelixLab/raceGPS/releases)
2. Double-click → UAC prompt → follow wizard (preflight checks RAM, disk, VC++ runtimes)
3. Launch from desktop shortcut (points at `Binaries\Win64\raceGPS.exe`)

**Build the installer from source:**
```powershell
# After UE5 packaging (or full Build.bat):
.\scripts\stage-windows-installer.ps1    # normalize payload → Build/Windows/
.\scripts\build-windows-installer.ps1    # stage + makensis → installer/raceGPS-v0.2.0-Win64-Setup.exe
```
Or run `apps\unreal-akron-beta\Build.bat` which stages automatically at the end.

### Linux
```bash
chmod +x raceGPS-v0.2.0-Linux-Setup.run
./raceGPS-v0.2.0-Linux-Setup.run
# Follow prompts; script will install UE5.5 via Epic Online Services if needed
```

---

## World Content Requirement

The Windows installer ships citypack **data** (`citypacks/akron-oh-beta-001/`) but the playable **3D world** requires a cooked `AkronWorld` map asset (`Content/Maps/AkronWorld.umap`). If that map was not included in the build:

1. Onboarding **Step 0** shows a failing **World Map** preflight row and blocks **Next**
2. **Play** on the main menu opens the **Akron world not installed** gate with:
   - **Verify installation** — re-scan install files and write `%LOCALAPPDATA%\raceGPS\logs\preflight.log`
   - **Open setup guide** — GitHub README (Level Setup Guide)
   - **Reinstall** — GitHub Releases page

Release builds must create `AkronWorld.umap` in UE 5.5 Editor before running `Build.bat`. Dev/CI may pass `AllowPlaceholder`:

```bat
Build.bat AllowPlaceholder
```

Staged installers include `Build/Windows/world-content-manifest.json` listing required world packages.

---

## Preflight Checks

On first launch, the game runs a **Preflight System** that validates:

| Check | Minimum | Recommended | Action on Fail |
|---|---|---|---|
| OS | Windows 10 64-bit | Windows 11 64-bit | Block launch |
| RAM | 8 GB | 16 GB | Warn / suggest close apps |
| GPU | DX12 compatible | GTX 1060 / RX 580+ | Auto-set Low preset |
| Disk | 5 GB free | 20 GB free | Block launch |
| Citypack | `akron-oh-beta-001` present | Any compiled citypack | Offer download |
| World Map | `AkronWorld` cooked package or `.umap` | Real saved UE map | Block launch; show install gate |
| Save Dir | Writable | SSD preferred | Suggest Admin mode |
| Network | Optional | For leaderboards | Skip silently |

If any check **Fails**, the player is shown a guided fix screen before reaching the main menu.

---

## Onboarding Flow (First Run)

The **Onboarding Manager** walks new players through 5 steps:

1. **Hardware Check** -- runs preflight, shows GPU/RAM summary
2. **Graphics Settings** -- auto-applies recommended preset (Low/Medium/High/Ultra)
3. **Select City** -- choose from installed citypacks or open Universal City Compiler
4. **Controls** -- select Arcade / Simulation / Custom layout
5. **Create Profile** -- player name + save slot

After step 5, settings are written to:
```
%LOCALAPPDATA%\raceGPS\Saved\Config\PlayerSettings.json
```

---

## Manual Installation (Advanced)

If the installer cannot run (e.g., no admin rights, unusual path requirements):

### Prerequisites
- **Visual Studio 2022 Build Tools** with "Desktop development with C++" workload
- **Unreal Engine 5.5** via Epic Games Launcher
- **Python 3.12** (for city compiler)

### Build from Source
```powershell
# 1. Clone
git clone https://github.com/LumenHelixLab/racegps.git
cd racegps/apps/unreal-akron-beta

# 2. Generate project
& "C:\Program Files\Epic Games\UE_5.5\Engine\Binaries\DotNET\UnrealBuildTool\UnrealBuildTool.exe" `
    -projectfiles -project="$PWD\raceGPSAkronBeta.uproject" -game -engine -progress

# 3. Build
& "C:\Program Files\Epic Games\UE_5.5\Engine\Build\BatchFiles\Build.bat" `
    raceGPSAkronBetaEditor Win64 Development "$PWD\raceGPSAkronBeta.uproject"

# 4. Cook & stage
& "C:\Program Files\Epic Games\UE_5.5\Engine\Build\BatchFiles\RunUAT.bat" `
    BuildCookRun -project="$PWD\raceGPSAkronBeta.uproject" `
    -noP4 -platform=Win64 -clientconfig=Shipping -cook -stage -pak -archive `
    -archivedirectory="$PWD\..\..\Build\Windows"
```

---

## Citypack Installation

The current Windows installer is configured to bundle repo citypacks into the installed `citypacks/` directory.

After install:

1. Launch game -> Onboarding Step 3 prompts for city selection
2. Use a bundled citypack if one is present under `citypacks/`
3. Or click **"Compile New City"** to generate an additional pack
4. Runtime-generated citypacks can be saved to `Saved/citypacks/<city-id>/`

Pre-compiled citypacks can also be dropped into either `citypacks/` (installer-managed) or `Saved/citypacks/` (runtime-managed).

---

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---|---|---|
| "UE5.5 not found" during install | Epic Launcher not installed | Run `scripts/setup-ue5-dev-env.bat` as Admin |
| "Citypack manifest missing" | Git LFS or install incomplete | Re-install or compile city |
| Game launches to black screen | GPU below min spec | Delete `PlayerSettings.json` to re-run onboarding |
| Save fails silently | Directory not writable | Run as Admin or change `Saved/` path in launcher args |
| Controls not responding | Enhanced Input not initialized | Verify `DefaultInput.ini` exists in `Saved/Config/Windows/` |

---

## Silent / Headless Install

For IT administrators:

```powershell
# Windows silent
raceGPS-v0.2.0-Win64-Setup.exe /S /D=D:\Games\raceGPS

# Linux unattended
./raceGPS-v0.2.0-Linux-Setup.run -- --accept-licenses --default-answer --confirm-command install \
    --root ~/games/racegps
```

---

## Support

- **Issues:** https://github.com/LumenHelixLab/racegps/issues
- **Discussions:** https://github.com/LumenHelixLab/racegps/discussions
- **Docs:** https://lumenhelixlab.github.io/racegps
