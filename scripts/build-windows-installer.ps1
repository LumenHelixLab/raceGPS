# raceGPS Windows Installer Builder
# Packages a UE5 BuildCookRun archive into installer\raceGPS-v<version>-Win64-Setup.exe.
#
# Usage:
#   pwsh -File scripts\build-windows-installer.ps1                      # default payload: apps\unreal-akron-beta\Build\Windows
#   pwsh -File scripts\build-windows-installer.ps1 -PayloadDir <dir>    # explicit archive root (e.g. a build.py timestamped archive)
#   pwsh -File scripts\build-windows-installer.ps1 -AllowPlaceholder    # compile against the placeholder payload (CI/smoke only)
#   pwsh -File scripts\build-windows-installer.ps1 -Version 0.3.0
#
# A "real" payload is defined as: a runnable exe PLUS cooked content (*.pak).
# Anything else fails the build unless -AllowPlaceholder is given.

[CmdletBinding()]
param(
    [string]$PayloadDir,
    [string]$Version = "0.2.0",
    [switch]$AllowPlaceholder
)

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path | Split-Path -Parent
$InstallerDir = Join-Path $Root "installer"
$NSISScript = Join-Path $InstallerDir "racegps-setup.nsi"

Write-Host "raceGPS Windows Installer Builder" -ForegroundColor Cyan
Write-Host "=================================="

# ---------------------------------------------------------------
# 1. Resolve payload directory
# ---------------------------------------------------------------
if (-not $PayloadDir) {
    $defaultPayload = Join-Path $Root "apps\unreal-akron-beta\Build\Windows"
    $PayloadDir = $defaultPayload

    if (Test-Path $defaultPayload) {
        # build.py archives into Build\Windows\<timestamp>\; if the default root has no
        # exe but exactly one or more timestamped archives do, use the newest one.
        $rootHasExe = @(Get-ChildItem $defaultPayload -Filter "*.exe" -ErrorAction SilentlyContinue).Count -gt 0
        if (-not $rootHasExe) {
            $archives = @(Get-ChildItem $defaultPayload -Directory -ErrorAction SilentlyContinue |
                Where-Object { @(Get-ChildItem $_.FullName -Filter "*.exe" -Recurse -Depth 2 -ErrorAction SilentlyContinue).Count -gt 0 } |
                Sort-Object Name -Descending)
            if ($archives.Count -gt 0) {
                $PayloadDir = $archives[0].FullName
                Write-Host "Using newest timestamped archive: $PayloadDir" -ForegroundColor Yellow
            }
        }
    }
}

if (-not (Test-Path $PayloadDir)) {
    Write-Error "Payload not found at $PayloadDir. Run the UE5 build/packaging first (scripts\build.py or Build.bat)."
    exit 1
}
$PayloadDir = (Resolve-Path $PayloadDir).Path
Write-Host "Payload: $PayloadDir"

# ---------------------------------------------------------------
# 2. Locate the game exe and classify the payload
# ---------------------------------------------------------------
$exeCandidates = @(
    "Windows\raceGPSAkronBeta.exe",                       # UE bootstrap (standard UAT archive)
    "Windows\raceGPSAkronBeta\raceGPSAkronBeta.exe",      # shipping-style inner exe
    "raceGPS.exe"                                          # legacy flat placeholder layout
)

$GameExeRel = $null
foreach ($rel in $exeCandidates) {
    if (Test-Path (Join-Path $PayloadDir $rel)) { $GameExeRel = $rel; break }
}

if (-not $GameExeRel) {
    Write-Error "No game exe found in payload. Expected one of: $($exeCandidates -join ', '). Did BuildCookRun complete?"
    exit 1
}

$exeSize = (Get-Item (Join-Path $PayloadDir $GameExeRel)).Length
$pakCount = @(Get-ChildItem $PayloadDir -Recurse -Filter "*.pak" -ErrorAction SilentlyContinue).Count

Write-Host "`n--- Payload inspection ---" -ForegroundColor Cyan
Write-Host "  exe:  $GameExeRel ($([math]::Round($exeSize/1MB,1)) MB)"
Write-Host "  paks: $pakCount"

$isPlaceholder = ($pakCount -eq 0 -and $exeSize -lt 5MB)
if ($isPlaceholder) {
    if (-not $AllowPlaceholder) {
        Write-Host "`n*** PLACEHOLDER / INCOMPLETE PAYLOAD - REFUSING TO BUILD ***" -ForegroundColor Red
        Write-Host "No cooked .pak content found and the exe is only $([math]::Round($exeSize/1KB)) KB." -ForegroundColor Red
        Write-Host "Produce a real package first:" -ForegroundColor Yellow
        Write-Host "   cd apps\unreal-akron-beta ; .\Build.bat" -ForegroundColor Yellow
        Write-Host "   (or: python scripts\build.py --engine `"C:\Program Files\Epic Games\UE_5.7`" --config Development)" -ForegroundColor Yellow
        Write-Host "Then re-run this script. To compile a demo installer anyway: -AllowPlaceholder" -ForegroundColor Yellow
        exit 2
    }
    Write-Host "`n*** PLACEHOLDER PAYLOAD - building demo installer anyway (-AllowPlaceholder) ***" -ForegroundColor Yellow
} else {
    Write-Host "Real payload confirmed (cooked content present)." -ForegroundColor Green
}

# ---------------------------------------------------------------
# 3. Runtime data
# ---------------------------------------------------------------
$CitypacksDir = Join-Path $Root "citypacks"
if (-not (Test-Path $CitypacksDir)) {
    Write-Error "citypacks directory missing at $CitypacksDir"
    exit 1
}

# ---------------------------------------------------------------
# 4. Find makensis
# ---------------------------------------------------------------
$makensis = $null
$possible = @(
    "C:\Program Files (x86)\NSIS\makensis.exe",
    "C:\Program Files\NSIS\makensis.exe",
    (Get-Command makensis.exe -ErrorAction SilentlyContinue).Source
)
foreach ($p in $possible) {
    if ($p -and (Test-Path $p)) { $makensis = $p; break }
}
if (-not $makensis) {
    Write-Error "makensis.exe not found. Install NSIS 3.x from https://nsis.sourceforge.io/Download"
    exit 1
}
Write-Host "`nUsing makensis: $makensis" -ForegroundColor Green

# ---------------------------------------------------------------
# 5. Compile (paths passed to NSIS are relative to installer\)
# ---------------------------------------------------------------
$payloadRel = ([System.Uri]($InstallerDir + '\')).MakeRelativeUri([System.Uri]($PayloadDir + '\')).ToString().TrimEnd('/') -replace '/', '\'

Write-Host "Compiling installer (version $Version, exe $GameExeRel)..." -ForegroundColor Yellow
Push-Location $InstallerDir
& $makensis /V2 /DPRODUCT_VERSION=$Version /DGAME_EXE_REL="$GameExeRel" /DPAYLOAD_REL="$payloadRel" $NSISScript
$compileExit = $LASTEXITCODE
Pop-Location

$outExe = Join-Path $InstallerDir "raceGPS-v$Version-Win64-Setup.exe"
if ($compileExit -ne 0) {
    Write-Error "NSIS compile failed (exit $compileExit). Check output above."
    exit $compileExit
}
if (-not (Test-Path $outExe)) {
    Write-Error "Compile returned 0 but $outExe was not produced."
    exit 1
}

# ---------------------------------------------------------------
# 6. Post-build sanity check
# ---------------------------------------------------------------
$outSize = (Get-Item $outExe).Length
if (-not $isPlaceholder -and $outSize -lt 10MB) {
    Write-Error "Installer is only $([math]::Round($outSize/1MB,1)) MB but the payload was classified as real - something was not bundled. Refusing to call this a success."
    exit 1
}

Write-Host "`nSUCCESS! Installer created: $outExe ($([math]::Round($outSize/1MB,1)) MB)" -ForegroundColor Green
if ($isPlaceholder) {
    Write-Host "NOTE: this is a placeholder/demo installer; the installed 'game' is not playable." -ForegroundColor Yellow
}
Write-Host "Next: validate per installer\WINDOWS-INSTALLER-VALIDATION-CHECKLIST.md" -ForegroundColor Green
