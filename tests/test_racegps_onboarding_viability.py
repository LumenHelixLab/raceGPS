from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PRE_H = PROJECT_ROOT / "apps" / "unreal-akron-beta" / "Source" / "raceGPSAkronBeta" / "Public" / "PreflightSystem.h"
PRE_CPP = PROJECT_ROOT / "apps" / "unreal-akron-beta" / "Source" / "raceGPSAkronBeta" / "Private" / "PreflightSystem.cpp"
ONBOARD_CPP = PROJECT_ROOT / "apps" / "unreal-akron-beta" / "Source" / "raceGPSAkronBeta" / "Private" / "OnboardingManager.cpp"
MENU_CPP = PROJECT_ROOT / "apps" / "unreal-akron-beta" / "Source" / "raceGPSAkronBeta" / "Private" / "MainMenuWidget.cpp"
CRUISE_CPP = PROJECT_ROOT / "apps" / "unreal-akron-beta" / "Source" / "raceGPSAkronBeta" / "Private" / "CruiseSprintGameMode.cpp"
GATE_H = PROJECT_ROOT / "apps" / "unreal-akron-beta" / "Source" / "raceGPSAkronBeta" / "Public" / "WorldContentGateWidget.h"
INSTALLER_CPP = PROJECT_ROOT / "apps" / "unreal-akron-beta" / "Source" / "raceGPSAkronBeta" / "Private" / "WorldContentInstaller.cpp"
BUILD_BAT = PROJECT_ROOT / "apps" / "unreal-akron-beta" / "Build.bat"
STAGE_PS1 = PROJECT_ROOT / "scripts" / "stage-windows-installer.ps1"
INSTALLER_MD = PROJECT_ROOT / "apps" / "unreal-akron-beta" / "docs" / "INSTALLER.md"
README = PROJECT_ROOT / "apps" / "unreal-akron-beta" / "README.md"


def test_preflight_summary_exposes_viability_gate_and_required_paths():
    header = PRE_H.read_text(encoding="utf-8")
    source = PRE_CPP.read_text(encoding="utf-8")

    assert 'bool bCanLaunch = false;' in header
    assert 'Summary.bCanLaunch = Summary.FailCount == 0;' in source
    assert 'akron_routes.json' in source
    assert 'AkronWorld_LevelSpec.json' in source


def test_save_directory_check_does_not_false_pass_not_writable():
    source = PRE_CPP.read_text(encoding="utf-8")
    assert 'Status.StartsWith(TEXT("Save directory writable:"))' in source
    assert 'Status.Contains(TEXT("writable"))' not in source


def test_mark_first_run_complete_creates_config_dir_before_save():
    source = PRE_CPP.read_text(encoding="utf-8")
    assert 'FString ConfigDir = FPaths::ProjectSavedDir() / TEXT("Config");' in source
    assert 'CreateDirectoryTree(*ConfigDir);' in source


def test_onboarding_finish_persists_preflight_summary_for_clear_pass_fail():
    source = ONBOARD_CPP.read_text(encoding="utf-8")
    assert 'const TArray<FPreflightCheck> Checks = UPreflightSystem::RunAllChecks();' in source
    assert 'const FPreflightSummary Summary = UPreflightSystem::GetSummary(Checks);' in source
    assert 'Root->SetBoolField(TEXT("preflight_can_launch"), Summary.bCanLaunch);' in source
    assert 'Root->SetNumberField(TEXT("preflight_fail_count"), Summary.FailCount);' in source
    assert 'Root->SetNumberField(TEXT("preflight_warning_count"), Summary.WarningCount);' in source


def test_main_menu_play_path_has_explicit_gate_for_missing_route_vehicle_or_handling():
    source = MENU_CPP.read_text(encoding="utf-8")
    assert 'RouteSelector->GetSelectedOption().IsEmpty()' in source
    assert 'GetSelectedVehicle()' in source
    assert 'GetSelectedHandlingMode().IsEmpty()' in source or 'GetSelectedHandlingMode()' in source
    assert 'UE_LOG(LogTemp, Warning, TEXT("[raceGPS] Cannot start play:' in source


def test_race_start_proof_points_exist_in_game_mode():
    source = CRUISE_CPP.read_text(encoding="utf-8")
    assert 'LoadCityData();' in source
    assert 'SpawnPlayerAtStart();' in source
    assert 'SpawnCheckpoints();' in source
    assert 'ApplyVehicleTuningToPlayer();' in source
    assert 'TutorialSystem->StartTutorial();' in source


def test_readme_has_clear_editor_blocker_language_for_akronworld():
    readme = README.read_text(encoding="utf-8")
    assert 'AkronWorld.umap' in readme
    assert 'must be finalized inside the Unreal Editor' in readme


def test_preflight_includes_world_map_check():
    header = PRE_H.read_text(encoding="utf-8")
    source = PRE_CPP.read_text(encoding="utf-8")
    assert "CheckWorldMap" in header
    assert "IsWorldMapReady" in header
    assert "Checks.Add(CheckWorldMap());" in source
    assert "AkronWorld.umap.placeholder" in source
    assert "DoesPackageExist" in source


def test_onboarding_step_zero_blocks_until_preflight_passes():
    source = ONBOARD_CPP.read_text(encoding="utf-8")
    assert "CanAdvanceFromCurrentStep" in source
    assert "Summary.FailCount == 0" in source
    assert 'world_map_ready' in source
    assert "AkronWorld map" in source


def test_main_menu_blocks_play_when_world_map_missing():
    source = MENU_CPP.read_text(encoding="utf-8")
    assert "IsWorldMapReady()" in source
    assert "ShowWorldContentGate()" in source
    assert "AkronWorld map not installed" in source


def test_world_content_gate_and_installer_exist():
    assert GATE_H.exists()
    gate = GATE_H.read_text(encoding="utf-8")
    installer = INSTALLER_CPP.read_text(encoding="utf-8")
    assert "OnVerifyInstallationClicked" in gate
    assert "OnOpenDocsClicked" in gate
    assert "VerifyInstallation" in installer
    assert "world-content-manifest.json" in installer


def test_build_bat_hard_fails_without_umap_unless_allow_placeholder():
    content = BUILD_BAT.read_text(encoding="utf-8")
    assert "AkronWorld.umap is required" in content
    assert "AllowPlaceholder" in content


def test_stage_script_emits_world_content_manifest():
    content = STAGE_PS1.read_text(encoding="utf-8")
    assert "world-content-manifest.json" in content
    assert "racegps.world_content.v1" in content
    assert "/Game/Maps/AkronWorld" in content


def test_installer_docs_mention_world_content_requirement():
    content = INSTALLER_MD.read_text(encoding="utf-8")
    assert "World Content Requirement" in content
    assert "AkronWorld" in content
    assert "world-content-manifest.json" in content
