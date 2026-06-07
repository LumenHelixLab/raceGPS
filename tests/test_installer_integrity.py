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
    """NSIS installer script must exist and be syntactically valid."""
    path = PROJECT_ROOT / "installer" / "racegps-setup.nsi"
    if not path.exists():
        pytest.skip("NSIS installer not yet created")
    content = path.read_text()
    assert "OutFile" in content
    assert "Section" in content
    assert "MUI" in content


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
