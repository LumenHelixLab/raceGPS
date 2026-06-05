# raceGPS Akron Beta — Build & Packaging Guide

## Prerequisites

- **Unreal Engine 5.5** (installed via Epic Games Launcher)
- **Visual Studio 2022** with "Game development with C++" workload
- **Windows SDK 10.0.22000+**
- **Python 3.10+** (for semantic compiler)
- **Git** (with LFS recommended for large assets)

## Quick Build

### Option 1: Batch Script

```powershell
cd apps\unreal-akron-beta
.\Build.bat
```

### Option 2: Manual Steps

#### 1. Generate Project Files

Right-click `raceGPSAkronBeta.uproject` → **Generate Visual Studio project files**

Or via command line:
```powershell
"C:\Program Files\Epic Games\UE_5.5\Engine\Binaries\DotNET\UnrealBuildTool\UnrealBuildTool.exe" `
  -projectfiles -project="D:\projects\racegps\apps\unreal-akron-beta\raceGPSAkronBeta.uproject" `
  -game -engine -progress
```

#### 2. Build Editor

Open `raceGPSAkronBeta.sln` in Visual Studio:
- Set configuration: **Development Editor**
- Set platform: **Win64**
- Build: `raceGPSAkronBeta` project

#### 3. Open in UE5 Editor

Double-click `raceGPSAkronBeta.uproject`

#### 4. Create AkronWorld Level

1. File → New Level → Empty Open World
2. Save As: `Content/Maps/AkronWorld`
3. World Settings:
   - GameMode Override: `CruiseSprintGameMode`
   - Game Instance: `raceGPSGameInstance`
4. Place PlayerStart actor near origin
5. Save

#### 5. Cook & Package

File → Package Project → Windows (64-bit)

Output: `Build/Windows/`

## Configuration

### Default Paths

| Setting | Default Value |
|---------|---------------|
| CityPack Path | `citypacks/akron-oh-beta-001/` |
| OpenDRIVE File | `akron.xodr` |
| Manifest | `akron_semantic_manifest.json` |
| Routes | `akron_routes.json` |

### Build Modes

| Mode | Use Case |
|------|----------|
| Development | Iteration, debugging |
| Development Editor | Editor features |
| Shipping | Final release |
| Test | Automated testing |

### Command-Line Packaging

```powershell
"C:\Program Files\Epic Games\UE_5.5\Engine\Build\BatchFiles\RunUAT.bat" `
  BuildCookRun `
  -project="D:\projects\racegps\apps\unreal-akron-beta\raceGPSAkronBeta.uproject" `
  -noP4 -platform=Win64 -clientconfig=Shipping `
  -cook -allmaps -stage -pak -archive `
  -archivedirectory="D:\projects\racegps\Build\Windows"
```

## Troubleshooting

### "CARLA Python API not found"

Not required. The project uses pure-Python OpenDRIVE generation (`osm_to_xodr.py`).

### "raceGPSAkronBeta module could not be found"

Regenerate project files after adding new `.cpp`/`.h` files.

### Missing `AkronWorld.umap`

The placeholder `.umap.placeholder` must be replaced with a real level created in-editor.

### City data not loading in packaged build

Ensure `citypacks/` directory is copied to the package output. The batch script handles this automatically.

## CI/CD (Future)

A GitHub Actions workflow could:
1. Check out repo
2. Cache UE5 build tools
3. Run `Build.bat`
4. Upload artifact as release

See `.github/workflows/build.yml` (to be created).
