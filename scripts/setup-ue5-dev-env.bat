@echo off
REM setup-ue5-dev-env.bat
REM Auto-elevating launcher for the PowerShell setup script.
REM Double-click this file — it will request Administrator permissions automatically.

set "SCRIPT_DIR=%~dp0"
set "PS_SCRIPT=%SCRIPT_DIR%setup-ue5-dev-env.ps1"

echo ==========================================
echo raceGPS UE5.5 Dev Environment Setup
echo ==========================================
echo.

net session >nul 2>&1
if %errorLevel% == 0 (
    echo Running as Administrator. Launching PowerShell script...
    powershell -ExecutionPolicy Bypass -File "%PS_SCRIPT%"
) else (
    echo Not running as Administrator. Requesting elevation...
    echo Click YES on the UAC prompt.
    echo.
    powershell -Command "Start-Process -FilePath 'cmd.exe' -ArgumentList '/c \"\"\"%~f0\"\"\"' -Verb RunAs"
)

pause