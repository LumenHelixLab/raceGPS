#Requires -Version 5.1
# setup-ue5-dev-env.ps1
# One-time setup script for raceGPS UE5.5 development environment.
# RUN AS ADMINISTRATOR (Right-click → Run as PowerShell Administrator)
#
# What this does:
#   1. Downloads VS2022 Build Tools bootstrapper
#   2. Installs VS2022 + C++ Game Dev workload
#   3. Installs Epic Games Launcher
#   4. Sets environment variables for raceGPS build
#   5. Creates desktop shortcuts
#
# What YOU do:
#   1. Run this script as Admin
#   2. Open Epic Games Launcher → log in
#   3. Click Unreal Engine → Library → + Engine Version → 5.5
#   4. Let it download overnight (~30-40 GB)

$ErrorActionPreference = "Stop"

$ScriptDir = $PSScriptRoot
if (-not $ScriptDir) { $ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path }
$ProjectRoot = Split-Path -Parent $ScriptDir
$UeAppDir = Join-Path $ProjectRoot "apps\unreal-akron-beta"
$BuildBat = Join-Path $UeAppDir "Build.bat"

$InstallDrive = if (Test-Path "D:\") { "D:" } else { $env:SystemDrive }
$VsInstallPath = Join-Path $InstallDrive "Microsoft Visual Studio\2022\BuildTools"
$EpicInstallPath = Join-Path $InstallDrive "Epic Games"
$CacheDir = Join-Path $ProjectRoot ".setup-cache"
$LogDir = Join-Path $ProjectRoot "logs"
$LogFile = Join-Path $LogDir "setup-ue5-dev-env.log"

New-Item -ItemType Directory -Path $CacheDir, $LogDir -Force | Out-Null

function Write-Log($msg) {
    $ts = Get-Date -Format "HH:mm:ss"
    $line = "$ts  $msg"
    Write-Host $line
    $line | Out-File -FilePath $LogFile -Append
}

function Test-Admin {
    $currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
    return $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# ============================================================================
# PREAMBLE
# ============================================================================
Write-Log "========================================"
Write-Log "raceGPS UE5.5 Dev Environment Setup"
Write-Log "========================================"
Write-Log "Project root: $ProjectRoot"

if (-not (Test-Admin)) {
    Write-Log "Not running as Administrator. Auto-elevating..."
    Write-Log "Click YES on the UAC prompt."
    $ScriptPath = $PSCommandPath
    if (-not $ScriptPath) { $ScriptPath = Join-Path $ScriptDir "setup-ue5-dev-env.ps1" }
    Start-Process -FilePath "powershell.exe" -ArgumentList @(
        "-ExecutionPolicy", "Bypass",
        "-File", "`"$ScriptPath`""
    ) -Verb RunAs -Wait
    exit 0
}

Write-Log "Running as Administrator. OK."
Write-Log "Install drive: $InstallDrive"
Write-Log "Log file: $LogFile"
Write-Log ""

# ============================================================================
# STEP 1: VS2022 Build Tools + Game Dev Workload
# ============================================================================
Write-Log "[STEP 1/4] Visual Studio 2022 Build Tools"
$VsInstallerDir = Join-Path $CacheDir "vs2022"
$VsBootstrapper = Join-Path $VsInstallerDir "vs_buildtools.exe"

if (Test-Path (Join-Path $VsInstallPath "MSBuild\Current\Bin\MSBuild.exe")) {
    Write-Log "  VS2022 Build Tools already installed at $VsInstallPath"
} else {
    New-Item -ItemType Directory -Path $VsInstallerDir -Force | Out-Null

    if (-not (Test-Path $VsBootstrapper)) {
        Write-Log "  Downloading VS2022 Build Tools bootstrapper..."
        $VsUrl = "https://aka.ms/vs/17/release/vs_buildtools.exe"
        try {
            Invoke-WebRequest -Uri $VsUrl -OutFile $VsBootstrapper -UseBasicParsing
            Write-Log "  Downloaded: $VsBootstrapper"
        } catch {
            Write-Log "  ERROR: Failed to download VS2022 bootstrapper. $_"
            Read-Host "Press Enter to exit"
            exit 1
        }
    } else {
        Write-Log "  Using cached bootstrapper: $VsBootstrapper"
    }

    Write-Log "  Installing VS2022 Build Tools (this may take 15-30 minutes)..."
    Write-Log "  Workloads: VCTools, NativeGame, Windows10SDK, CMake"

    $proc = Start-Process -FilePath $VsBootstrapper -ArgumentList @(
        "--installPath", "`"$VsInstallPath`"",
        "--quiet",
        "--wait",
        "--norestart",
        "--nocache",
        "--add", "Microsoft.VisualStudio.Workload.VCTools",
        "--add", "Microsoft.VisualStudio.Workload.NativeGame",
        "--add", "Microsoft.VisualStudio.Component.Windows10SDK.20348",
        "--add", "Microsoft.VisualStudio.Component.VC.CMake.Project",
        "--add", "Microsoft.VisualStudio.Component.Git",
        "--add", "Microsoft.VisualStudio.Component.VC.Tools.x86.x64"
    ) -Wait -PassThru

    if ($proc.ExitCode -ne 0 -and $proc.ExitCode -ne 3010) {
        Write-Log "  WARNING: VS installer exited with code $($proc.ExitCode)"
        Write-Log "  Check logs at $env:TEMP\dd_setup_*.log for details"
    } else {
        Write-Log "  VS2022 Build Tools installed successfully (exit: $($proc.ExitCode))"
    }
}

# Verify MSBuild
$MsBuildPath = Join-Path $VsInstallPath "MSBuild\Current\Bin\MSBuild.exe"
if (Test-Path $MsBuildPath) {
    Write-Log "  MSBuild confirmed: $MsBuildPath"
} else {
    Write-Log "  WARNING: MSBuild not found at expected path"
}

# ============================================================================
# STEP 2: Epic Games Launcher
# ============================================================================
Write-Log ""
Write-Log "[STEP 2/4] Epic Games Launcher"
$EpicMsi = Join-Path $CacheDir "EpicGamesLauncherInstaller.msi"
$EpicExe = Join-Path $EpicInstallPath "Launcher\Portal\Binaries\Win64\EpicGamesLauncher.exe"

if (Test-Path $EpicExe) {
    Write-Log "  Epic Games Launcher already installed at $EpicInstallPath"
} else {
    if (-not (Test-Path $EpicMsi)) {
        Write-Log "  Downloading Epic Games Launcher installer..."
        $EpicUrl = "https://launcher-public-service-prod06.ol.epicgames.com/launcher/api/installer/download/EpicGamesLauncherInstaller.msi"
        try {
            Invoke-WebRequest -Uri $EpicUrl -OutFile $EpicMsi -UseBasicParsing
            Write-Log "  Downloaded: $EpicMsi"
        } catch {
            Write-Log "  ERROR: Failed to download Epic installer. $_"
        }
    } else {
        Write-Log "  Using cached installer: $EpicMsi"
    }

    if (Test-Path $EpicMsi) {
        Write-Log "  Installing Epic Games Launcher..."
        $EpicLog = Join-Path $LogDir "epic-install.log"
        $proc = Start-Process -FilePath "msiexec.exe" -ArgumentList @(
            "/i", "`"$EpicMsi`"",
            "INSTALLDIR=`"$EpicInstallPath`"",
            "/qn",
            "/norestart",
            "/log", "`"$EpicLog`""
        ) -Wait -PassThru

        if ($proc.ExitCode -eq 0 -or $proc.ExitCode -eq 3010) {
            Write-Log "  Epic Games Launcher installed successfully"
        } else {
            Write-Log "  WARNING: Epic installer exited with code $($proc.ExitCode)"
            Write-Log "  Check $EpicLog"
        }
    }
}

# ============================================================================
# STEP 3: Environment Variables
# ============================================================================
Write-Log ""
Write-Log "[STEP 3/4] Environment Variables"

[Environment]::SetEnvironmentVariable("RACEGPS_ROOT", $ProjectRoot, "User")
Write-Log "  RACEGPS_ROOT = $ProjectRoot"

[Environment]::SetEnvironmentVariable("RACEGPS_MSBUILD", $MsBuildPath, "User")
Write-Log "  RACEGPS_MSBUILD = $MsBuildPath"

$Ue55Path = "C:\Program Files\Epic Games\UE_5.5"
[Environment]::SetEnvironmentVariable("RACEGPS_UE5", $Ue55Path, "User")
Write-Log "  RACEGPS_UE5 = $Ue55Path (set now, available after UE5 install)"

$UserPath = [Environment]::GetEnvironmentVariable("Path", "User")
$VsBinDir = Join-Path $VsInstallPath "MSBuild\Current\Bin"
if ($UserPath -notlike "*$VsBinDir*") {
    [Environment]::SetEnvironmentVariable("Path", "$UserPath;$VsBinDir", "User")
    Write-Log "  Added MSBuild to user PATH"
}

Write-Log "  Environment variables set. Restart terminal to use them."

# ============================================================================
# STEP 4: Desktop Shortcuts
# ============================================================================
Write-Log ""
Write-Log "[STEP 4/4] Desktop Shortcuts"
$WshShell = New-Object -ComObject WScript.Shell
$DesktopPath = [Environment]::GetFolderPath("Desktop")

if (Test-Path $EpicExe) {
    $Shortcut = $WshShell.CreateShortcut((Join-Path $DesktopPath "Epic Games Launcher.lnk"))
    $Shortcut.TargetPath = $EpicExe
    $Shortcut.WorkingDirectory = Split-Path $EpicExe
    $Shortcut.Save()
    Write-Log "  Created: Epic Games Launcher shortcut"
}

if (Test-Path $BuildBat) {
    $Shortcut = $WshShell.CreateShortcut((Join-Path $DesktopPath "raceGPS Build.lnk"))
    $Shortcut.TargetPath = $BuildBat
    $Shortcut.WorkingDirectory = $UeAppDir
    $Shortcut.Save()
    Write-Log "  Created: raceGPS Build shortcut"
}

# ============================================================================
# DONE
# ============================================================================
Write-Log ""
Write-Log "========================================"
Write-Log "SETUP COMPLETE"
Write-Log "========================================"
Write-Log ""
Write-Log "NEXT STEPS (MANUAL - about 5 minutes):"
Write-Log ""
Write-Log "  1. Double-click 'Epic Games Launcher' on your desktop"
Write-Log "  2. Log in with your Epic account"
Write-Log "  3. Click 'Unreal Engine' tab → 'Library'"
Write-Log "  4. Click the '+' button next to 'Engine Versions'"
Write-Log "  5. Select '5.5' and click Install"
Write-Log "  6. Choose install location: C:\Program Files\Epic Games\UE_5.5"
Write-Log "  7. Let it download overnight (~30-40 GB)"
Write-Log ""
Write-Log "AFTER UE5.5 IS INSTALLED:"
Write-Log "  Double-click 'raceGPS Build' on your desktop"
Write-Log "  or run: $BuildBat"
Write-Log ""
Write-Log "BUILD WINDOWS INSTALLER:"
Write-Log "  .\scripts\build-windows-installer.ps1"
Write-Log ""
Write-Log "Full log: $LogFile"
Write-Log ""

if (Test-Path $EpicExe) {
    Write-Log "Launching Epic Games Launcher now..."
    Start-Process -FilePath $EpicExe
}

Read-Host "Press Enter to close this window"