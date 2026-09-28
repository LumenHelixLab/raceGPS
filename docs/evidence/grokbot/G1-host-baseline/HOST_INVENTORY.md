# G1 Host Baseline Inventory

**Claim level:** OBSERVED / REPRODUCED_LOCALLY
**Captured:** 2026-09-07 America/New_York (omni)

## OS
- Microsoft Windows 11 Home
- Version: 10.0.26200

## CPU
- AMD Ryzen AI 9 365 w/ Radeon 880M
- Cores: 10 physical / 20 logical

## GPU / VRAM
- AMD Radeon(TM) 880M Graphics (iGPU)
- Win32 AdapterRAM report: 536870912 (unreliable for shared GPU memory)
- nvidia-smi: NOT PRESENT (no discrete NVIDIA)

## RAM
- TotalVisibleMemory: ~31.31 GB
- Free at capture: ~12.10 GB

## Disk
- C: Used ~426.4 GB / Free ~376.3 GB

## Toolchain
- Python: 3.11.15
- Node: v26.3.0
- MSVC: Visual Studio Build Tools 2022 17.14.31
  - Path: C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools

## Unreal Engine
- InstalledDirectory: C:\Program Files\Epic Games\UE_5.7
- Engine\Build\Build.version exact:
  - MajorVersion: 5
  - MinorVersion: 7
  - PatchVersion: 4
  - Changelist: 51494982
  - CompatibleChangelist: 47537391
  - IsLicenseeVersion: 0
  - IsPromotedBuild: 1
  - BranchName: ++UE5+Release-5.7
- Build.bat present: YES

## Plugins of interest
- ChaosVehiclesPlugin: PRESENT (Experimental)
- CesiumForUnreal: PRESENT (Marketplace)
- Project Plugins/ folder: empty/absent in worktree

## Project
- uproject EngineAssociation: 5.7
- Enabled: ChaosVehiclesPlugin, ModelingToolsEditorMode, PythonScriptPlugin, EditorScriptingUtilities
