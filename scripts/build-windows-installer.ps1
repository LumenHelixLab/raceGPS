#Requires -Version 5.1
# build-windows-installer.ps1
# Stage packaged game + compile NSIS installer.

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$StageScript = Join-Path $PSScriptRoot "stage-windows-installer.ps1"
$Nsi = Join-Path $ProjectRoot "installer\racegps-setup.nsi"
$OutDir = Join-Path $ProjectRoot "installer"

Write-Host "raceGPS — build Windows installer" -ForegroundColor Cyan

& $StageScript
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

$gameExe = Join-Path $ProjectRoot "Build\Windows\Binaries\Win64\raceGPS.exe"
if (-not (Test-Path $gameExe)) {
    Write-Host "ERROR: Staged game exe missing at $gameExe" -ForegroundColor Red
    exit 1
}

$makensis = $null
foreach ($candidate in @(
    "${env:ProgramFiles(x86)}\NSIS\makensis.exe",
    "${env:ProgramFiles}\NSIS\makensis.exe",
    "makensis"
)) {
    if ($candidate -eq "makensis") {
        $cmd = Get-Command makensis -ErrorAction SilentlyContinue
        if ($cmd) { $makensis = $cmd.Source; break }
    } elseif (Test-Path $candidate) {
        $makensis = $candidate
        break
    }
}

if (-not $makensis) {
    Write-Host "WARN: NSIS (makensis) not found. Payload staged; compile manually:" -ForegroundColor Yellow
    Write-Host "  Open $Nsi in NSIS Compile GUI, or install NSIS 3.x" -ForegroundColor Gray
    exit 0
}

Write-Host "Compiling NSIS installer..." -ForegroundColor Green
Push-Location $OutDir
try {
    & $makensis "/V2" "racegps-setup.nsi"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: makensis failed with exit code $LASTEXITCODE" -ForegroundColor Red
        exit $LASTEXITCODE
    }
} finally {
    Pop-Location
}

$installer = Get-ChildItem -Path $OutDir -Filter "raceGPS-v*-Win64-Setup.exe" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
if ($installer) {
    Write-Host "Installer built: $($installer.FullName) [$([math]::Round($installer.Length/1MB, 1)) MB]" -ForegroundColor Cyan
} else {
    Write-Host "WARN: Expected raceGPS-v*-Win64-Setup.exe not found in $OutDir" -ForegroundColor Yellow
}
exit 0