# raceGPS Unreal Compile-Failure Triage

Goal
- Fail fast when Unreal compile breaks.
- Check the highest-probability breakpoints first.

## First 60 seconds

1. Compile once.
2. Read the first real compiler error, not the cascade.
3. If the error mentions one of the files below, use the matching fix path immediately.

## Priority 1 — Changed files most likely to fail first

### A. OnboardingManager.cpp
Path
- Source/raceGPSAkronBeta/Private/OnboardingManager.cpp

Typical error shapes
- unknown type FJsonObject
- TJsonWriterFactory not declared
- FJsonSerializer not declared

Fast check
- Verify these includes exist at top of file:
  - Dom/JsonObject.h
  - Serialization/JsonWriter.h
  - Serialization/JsonSerializer.h

### B. MainMenuWidget.h / MainMenuWidget.cpp
Paths
- Source/raceGPSAkronBeta/Public/MainMenuWidget.h
- Source/raceGPSAkronBeta/Private/MainMenuWidget.cpp

Typical error shapes
- unresolved ESelectInfo type issues
- BindWidget property mismatch warnings in editor
- delegate signature mismatch for OnSelectionChanged

Fast checks
- GetSelectedHandlingMode() declared in header and defined in cpp
- OnHandlingSelectionChanged(...) declared in header and defined in cpp
- HandlingSelector and HandlingInfoText properties exist in header

Editor check after compile
- MainMenu widget blueprint must bind:
  - HandlingSelector
  - HandlingInfoText

### C. CruiseSprintGameMode.h / CruiseSprintGameMode.cpp
Paths
- Source/raceGPSAkronBeta/Public/CruiseSprintGameMode.h
- Source/raceGPSAkronBeta/Private/CruiseSprintGameMode.cpp

Typical error shapes
- JSON parsing symbols missing
- TObjectPtr / TMap signature mismatch
- duplicate / incompatible function declarations

Fast checks
- Header contains:
  - HandlingModePresets
  - LoadHandlingModePresets()
  - BuildMergedVehicleTuning(...)
- CPP includes:
  - Misc/FileHelper.h
  - Misc/Paths.h
  - Dom/JsonObject.h
  - Serialization/JsonSerializer.h

### D. raceGPSGameInstance.h / .cpp
Paths
- Source/raceGPSAkronBeta/Public/raceGPSGameInstance.h
- Source/raceGPSAkronBeta/Private/raceGPSGameInstance.cpp

Typical error shapes
- missing LastSelectedHandlingMode member
- save/load JSON field typos

Fast checks
- Header has:
  - FString LastSelectedHandlingMode = TEXT("Arcade");
- CPP save/load has:
  - LastSelectedHandlingMode write
  - LastSelectedHandlingMode read

## If compile succeeds but menu feels broken
That is probably not C++.
Check the UMG blueprint bindings next.

## If compile succeeds but play breaks immediately
Check runtime assets/files:
- Content/Data/VehiclePresets/Arcade.json
- Content/Data/VehiclePresets/Drift.json
- Content/Data/VehiclePresets/Simulation.json
- Content/Maps/AkronWorld.umap
- citypacks/akron-oh-beta-001/akron_semantic_manifest.json
- citypacks/akron-oh-beta-001/akron_routes.json
- generated/AkronWorld_LevelSpec.json

## Known non-issue
- LF/CRLF warnings in git diff are not compile blockers.

## Success condition
- clean compile
- MainMenu widget binds the new handling controls
- AkronWorld opens and PIE reaches drivable gameplay
