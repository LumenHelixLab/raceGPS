"""
Installer Integrity Tests
Validates that all onboarding/preflight artifacts exist and are well-formed.
"""
import json
import ast
import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
APP_DIR = PROJECT_ROOT / "apps" / "unreal-akron-beta"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
INSTALLER_DIR = PROJECT_ROOT / "installer"
CITYPACKS_DIR = PROJECT_ROOT / "citypacks"
GAME_EXE_REL = r"Binaries\Win64\raceGPS.exe"


def test_preflight_header_exists():
    path = APP_DIR / "Source/raceGPSAkronBeta/Public/PreflightSystem.h"
    assert path.exists(), f"Missing {path}"
    content = path.read_text()
    assert "UPreflightSystem" in content
    assert "FPreflightCheck" in content
    assert "EPreflightStatus" in content


def test_preflight_cpp_exists():
    path = APP_DIR / "Source/raceGPSAkronBeta/Private/PreflightSystem.cpp"
    assert path.exists(), f"Missing {path}"
    content = path.read_text()
    assert "RunAllChecks" in content
    assert "CheckRAM" in content
    assert "CheckGPU" in content
    assert "CheckCitypackIntegrity" in content


def test_onboarding_header_exists():
    path = APP_DIR / "Source/raceGPSAkronBeta/Public/OnboardingManager.h"
    assert path.exists(), f"Missing {path}"
    content = path.read_text()
    assert "UOnboardingManager" in content
    assert "StartOnboarding" in content
    assert "FinishAndSave" in content


def test_onboarding_cpp_exists():
    path = APP_DIR / "Source/raceGPSAkronBeta/Private/OnboardingManager.cpp"
    assert path.exists(), f"Missing {path}"
    content = path.read_text()
    assert "PlayerSettings.json" in content


def test_settings_auto_config_header():
    path = APP_DIR / "Source/raceGPSAkronBeta/Public/SettingsAutoConfigurator.h"
    assert path.exists(), f"Missing {path}"


def test_settings_auto_config_cpp():
    path = APP_DIR / "Source/raceGPSAkronBeta/Private/SettingsAutoConfigurator.cpp"
    assert path.exists(), f"Missing {path}"
    content = path.read_text()
    assert "ApplyPreset" in content
    assert "SetScalabilitySettings" in content


def test_installer_docs():
    path = APP_DIR / "docs/INSTALLER.md"
    assert path.exists(), f"Missing {path}"
    content = path.read_text()
    assert "Quick Start" in content
    assert "Preflight" in content
    assert "Onboarding" in content
    assert "Troubleshooting" in content


def test_nsis_script():
    """NSIS installer script must exist and reference the staged game exe path."""
    path = INSTALLER_DIR / "racegps-setup.nsi"
    if not path.exists():
        pytest.skip("NSIS installer not yet created")
    content = path.read_text()
    assert "OutFile" in content
    assert "Section" in content
    assert "MUI" in content
    assert 'GAME_EXE_REL "Binaries\\Win64\\raceGPS.exe"' in content
    assert f'"$INSTDIR\\${{GAME_EXE_REL}}"' in content
    assert "/nonfatal" not in content
    assert "GlobalMemoryStatusEx" in content
    assert "MUI_PAGE_FINISH" not in content, "Custom FinishPage should replace MUI finish page"


def test_windows_installer_pipeline_scripts():
    stage = SCRIPTS_DIR / "stage-windows-installer.ps1"
    build = SCRIPTS_DIR / "build-windows-installer.ps1"
    assert stage.exists(), f"Missing {stage}"
    assert build.exists(), f"Missing {build}"
    stage_content = stage.read_text()
    build_content = build.read_text()
    assert "installer-payload.json" in stage_content
    assert "akron-oh-beta-001" in stage_content
    assert "world-content-manifest.json" in stage_content
    assert "raceGPS.exe" in stage_content
    assert "makensis" in build_content
    assert "stage-windows-installer.ps1" in build_content


def test_akron_citypack_present():
    akron_routes = CITYPACKS_DIR / "akron-oh-beta-001" / "akron_routes.json"
    assert akron_routes.exists(), f"Bundled Akron citypack missing: {akron_routes}"


def test_game_target_names_racegps_exe():
    targets = [
        APP_DIR / "Source" / "raceGPSAkronBeta" / "raceGPSAkronBeta.Target.cs",
        APP_DIR / "Source" / "raceGPSAkronBeta.Target.cs",
    ]
    found = False
    for path in targets:
        if not path.exists():
            continue
        found = True
        assert 'TargetName = "raceGPS"' in path.read_text(), f"{path} must set TargetName = raceGPS"
    assert found, "No game Target.cs found"


def test_build_bat_stages_installer_payload():
    build_bat = APP_DIR / "Build.bat"
    content = build_bat.read_text()
    assert "stage-windows-installer.ps1" in content
    assert r"Windows\raceGPS" in content or "Windows\\raceGPS" in content


def test_setup_scripts_use_repo_relative_paths():
    bat = SCRIPTS_DIR / "setup-ue5-dev-env.bat"
    ps1 = SCRIPTS_DIR / "setup-ue5-dev-env.ps1"
    bat_content = bat.read_text()
    ps1_content = ps1.read_text()
    assert "%~dp0" in bat_content or "SCRIPT_DIR" in bat_content
    assert "D:\\projects\\scripts" not in bat_content
    assert "$PSScriptRoot" in ps1_content or "$ScriptDir" in ps1_content
    assert "Split-Path -Parent $PSScriptRoot" in ps1_content or "Split-Path -Parent $ScriptDir" in ps1_content
    assert "build-windows-installer.ps1" in ps1_content


def test_linux_installer_script():
    path = PROJECT_ROOT / "installer" / "install-linux.sh"
    if not path.exists():
        pytest.skip("Linux installer not yet created")
    content = path.read_text()
    assert any(shebang in content for shebang in ["#!/bin/bash", "#!/bin/sh", "#!/usr/bin/env bash", "#!/usr/bin/env sh"])


def test_ue5_setup_ps1_exists():
    path = SCRIPTS_DIR / "setup-ue5-dev-env.ps1"
    assert path.exists(), f"Missing {path}"
    content = path.read_text()
    assert "RunAs" in content or "Start-Process" in content


def test_ue5_setup_bat_exists():
    path = SCRIPTS_DIR / "setup-ue5-dev-env.bat"
    assert path.exists(), f"Missing {path}"
    content = path.read_text()
    assert ".ps1" in content


def test_build_cs_includes_json():
    path = APP_DIR / "Source/raceGPSAkronBeta/raceGPSAkronBeta.Build.cs"
    assert path.exists(), f"Missing {path}"
    content = path.read_text()
    assert '"Json"' in content
    assert '"JsonUtilities"' in content


def test_python_editor_widget_valid_syntax():
    path = APP_DIR / "Content/Python/editor_import_widget.py"
    if path.exists():
        source = path.read_text()
        try:
            ast.parse(source)
        except SyntaxError as e:
            pytest.fail(f"Syntax error in {path}: {e}")
    else:
        pytest.skip("editor_import_widget.py not found")


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
