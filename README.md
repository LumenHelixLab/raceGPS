# raceGPS

<p align="center">
  <a href="https://lumenhelix.com">
    <img src="docs/assets/lumenhelix-logo.svg" alt="LumenHelix Solutions" width="180">
  </a>
</p>

<h3 align="center">Real-world arcade racing on OpenStreetMap roads in Unreal Engine 5</h3>

<p align="center">
  <a href="https://lumenhelixsolutions.github.io/raceGPS/">
    <img src="https://img.shields.io/badge/Launch_Page-raceGPS-00D4FF?style=flat-square&logo=githubpages&logoColor=white" alt="Launch Page">
  </a>
  <a href="https://lumenhelix.com">
    <img src="https://img.shields.io/badge/Built_by-LumenHelix-7C3AED?style=flat-square" alt="Built by LumenHelix">
  </a>
  <img src="https://img.shields.io/badge/license-MIT-8A95A8?style=flat-square" alt="License">
</p>

---

**raceGPS** is part of the [LumenHelix Solutions](https://lumenhelix.com) portfolio — applied symbolic dynamics & reversible computation for deterministic, traceable AI systems.

raceGPS is an open-source desktop arcade racing game built on real-world map data. Instead of fictional tracks, you race on actual city streets rendered in 3D from OpenStreetMap and OpenDRIVE semantic road networks. The project combines a UE5.5 C++ gameplay stack with a pure-Python semantic compiler that fetches OSM data, generates valid OpenDRIVE 1.4 road networks, builds cruise sprint routes, and exports game-ready citypacks.

## Why this exists

- **Race the real world.** Every route is grounded in actual road geometry, not handcrafted fantasy tracks.
- **Own the pipeline.** Open-source UE5 C++ gameplay plus a Python semantic compiler you can extend for any city.
- **Build locally.** No required cloud service; compile the game, compiler, and installer on your own machine.

## Quick start

Install and run raceGPS in under two minutes.

### macOS / Linux

```bash
# Clone
git clone https://github.com/lumenhelixsolutions/raceGPS.git
cd raceGPS

# Install & run
# Prerequisites: Unreal Engine 5.5, Xcode 15+, Python 3.10+
# 1. Generate Xcode project files
/Users/Shared/Epic\ Games/UE_5.5/Engine/Build/BatchFiles/Mac/GenerateProjectFiles.sh \
  -project="$(pwd)/apps/unreal-akron-beta/raceGPSAkronBeta.uproject" -game

# 2. Build Development Editor
cd apps/unreal-akron-beta
/Users/Shared/Epic\ Games/UE_5.5/Engine/Build/BatchFiles/Mac/Build.sh \
  raceGPSAkronBetaEditor Mac Development -project="$(pwd)/raceGPSAkronBeta.uproject"

# 3. Build Python semantic compiler
cd ../../tools/akron-semantic-compiler
python3 -m venv ../../../.venv
source ../../../.venv/bin/activate
pip install -r requirements.txt
python compile_akron.py
```

### Windows (PowerShell)

```powershell
# Clone
git clone https://github.com/lumenhelixsolutions/raceGPS.git
Set-Location raceGPS

# Install & run
# Prerequisites: Unreal Engine 5.5, Visual Studio 2022 + C++ game workload, Python 3.10+
# 1. One-time dev environment setup (run as Administrator)
.\scripts\setup-ue5-dev-env.ps1

# 2. Build UE5 C++ project + package
cd apps\unreal-akron-beta
.\Build.bat

# 3. Build Python semantic compiler
cd ..\..\tools\akron-semantic-compiler
py -m venv ..\..\..\.venv
..\..\..\.venv\Scripts\pip install -r requirements.txt
py compile_akron.py
```

### Windows (Git Bash / WSL)

```bash
git clone https://github.com/lumenhelixsolutions/raceGPS.git
cd raceGPS
# Prerequisites: Unreal Engine 5.5 Linux build, build-essential, clang, Python 3.10+
# 1. Generate Linux Makefiles
~/UnrealEngine/5.5/Engine/Build/BatchFiles/Linux/GenerateProjectFiles.sh \
  -project="$(pwd)/apps/unreal-akron-beta/raceGPSAkronBeta.uproject" -game

# 2. Build Development Editor
cd apps/unreal-akron-beta
~/UnrealEngine/5.5/Engine/Build/BatchFiles/Linux/Build.sh \
  raceGPSAkronBetaEditor Linux Development -project="$(pwd)/raceGPSAkronBeta.uproject"

# 3. Build Python semantic compiler
cd ../../tools/akron-semantic-compiler
python3 -m venv ../../../.venv
source ../../../.venv/bin/activate
pip install -r requirements.txt
python compile_akron.py
```

> **Device note:** raceGPS is tested on Windows 11, macOS Sonoma, Ubuntu 22.04/24.04, and modern mobile browsers.

## Full documentation

Visit the launch page for architecture, API reference, and deployment guides:  
**https://lumenhelixsolutions.github.io/raceGPS/**

## Features

| Feature | What it gives you |
|---------|-------------------|
| Real-world maps | Race on 1,370+ real Akron roads generated from OpenStreetMap and OpenDRIVE data. |
| Arcade physics | Chaos Vehicles tuned for drift-friendly, fun handling with ghost replay and leaderboards. |
| Cruise Sprint mode | Checkpoint-to-checkpoint racing with route ribbons, medals, and persistent achievements. |
| Cross-platform UE5 stack | C++ gameplay systems, Python semantic compiler, and build scripts for Windows, macOS, Linux, and WSL. |

## Architecture at a glance

```
raceGPS/
├── apps/unreal-akron-beta/   UE5.5 C++ project — gameplay, world, UI, systems
├── tools/akron-semantic-compiler/  Python OSM → OpenDRIVE → citypack pipeline
├── citypacks/                 Generated game-ready route and road data
└── scripts/                   Build, package, and installer automation
```

## Development

```bash
# Build the UE5 editor (Windows PowerShell)
cd apps\unreal-akron-beta
.\Build.bat

# Or generate project files manually
"C:\Program Files\Epic Games\UE_5.5\Engine\Binaries\DotNET\UnrealBuildTool\UnrealBuildTool.exe" \
  -projectfiles -project="$(pwd)\raceGPSAkronBeta.uproject" -game -engine

# Run the semantic compiler
cd tools\akron-semantic-compiler
py compile_akron.py
```

## Roadmap

- [ ] Additional citypacks beyond Akron, Ohio
- [ ] Cross-platform CI build for Windows, macOS, and Linux
- [ ] Multiplayer lobby and online leaderboards

## Support & consulting

Need deterministic AI systems with full traceability? LumenHelix builds reversible computation kernels, governance layers, and end-to-end AI integrations.

- **Website:** https://lumenhelix.com
- **Services:** AI diagnostics, B.Y.O. support packages, governance audits
- **Research:** TEN² kernel, R.U.B.I.C. boundary discipline, C.O.R.E. constraint lens

## License

Released under the MIT License. Map data © OpenStreetMap contributors.

---

<p align="center">
  <sub>Engineered by <a href="https://lumenhelix.com">LumenHelix Solutions</a> — Applied Symbolic Dynamics & Reversible Computation.</sub>
</p>
