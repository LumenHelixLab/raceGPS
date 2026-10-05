#Requires -Version 5.1
# stage-windows-installer.ps1
# Normalize UE packaged output into repo-root Build/Windows for NSIS.

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$StageDir = Join-Path $ProjectRoot "Build\Windows"
$CitypackSource = Join-Path $ProjectRoot "citypacks"
$SearchRoots = @(
    (Join-Path $ProjectRoot "apps\unreal-akron-beta\Build\Windows"),
    (Join-Path $ProjectRoot "Build\Windows")
)

function Find-GameRoot {
    param([string[]]$Roots)
    $candidates = @()
    foreach ($root in $Roots) {
        if (-not (Test-Path $root)) { continue }
        $exes = Get-ChildItem -Path $root -Recurse -Filter "*.exe" -ErrorAction SilentlyContinue |
            Where-Object {
                $_.FullName -match "\\Binaries\\Win64\\" -and
                $_.Name -notmatch "^(Unreal|Crash|Epic|Shader)" -and
                $_.Name -notmatch "Editor"
            }
        foreach ($exe in $exes) {
            $gameRoot = $exe.Directory.Parent.Parent.FullName
            $candidates += [pscustomobject]@{
                Exe = $exe.FullName
                Root = $gameRoot
                Name = $exe.Name
            }
        }
    }
    if (-not $candidates.Count) { return $null }
    $preferred = $candidates | Where-Object { $_.Name -eq "raceGPS.exe" } | Select-Object -First 1
    if ($preferred) { return $preferred }
    $legacy = $candidates | Where-Object { $_.Name -eq "raceGPSAkronBeta.exe" } | Select-Object -First 1
    if ($legacy) { return $legacy }
    return $candidates | Select-Object -First 1
}

Write-Host "raceGPS — stage Windows installer payload" -ForegroundColor Cyan

$match = Find-GameRoot -Roots $SearchRoots
if (-not $match) {
    Write-Host "ERROR: No packaged game executable found under:" -ForegroundColor Red
    foreach ($r in $SearchRoots) { Write-Host "  $r" -ForegroundColor Gray }
    Write-Host "Run apps\unreal-akron-beta\Build.bat after UE5.5 packaging completes." -ForegroundColor Yellow
    exit 1
}

Write-Host "Found game root: $($match.Root)" -ForegroundColor Green
Write-Host "Executable: $($match.Exe)" -ForegroundColor Gray

if (Test-Path $StageDir) {
    Remove-Item -Path $StageDir -Recurse -Force
}
New-Item -ItemType Directory -Path $StageDir -Force | Out-Null

Write-Host "Copying game files to $StageDir ..." -ForegroundColor Green
robocopy $match.Root $StageDir /E /NFL /NDL /NJH /NJS /nc /ns /np | Out-Null
if ($LASTEXITCODE -ge 8) {
    Write-Host "ERROR: robocopy failed with exit code $LASTEXITCODE" -ForegroundColor Red
    exit 1
}

$stageExe = Join-Path $StageDir "Binaries\Win64\raceGPS.exe"
$legacyExe = Join-Path $StageDir "Binaries\Win64\raceGPSAkronBeta.exe"
if (-not (Test-Path $stageExe) -and (Test-Path $legacyExe)) {
    Rename-Item -Path $legacyExe -NewName "raceGPS.exe"
    Write-Host "Renamed raceGPSAkronBeta.exe -> raceGPS.exe" -ForegroundColor Yellow
}

if (-not (Test-Path $stageExe)) {
    Write-Host "ERROR: Expected $stageExe after staging." -ForegroundColor Red
    exit 1
}

$stageCitypacks = Join-Path $StageDir "citypacks"
if (-not (Test-Path $stageCitypacks)) {
    New-Item -ItemType Directory -Path $stageCitypacks -Force | Out-Null
}
if (Test-Path $CitypackSource) {
    Write-Host "Syncing citypacks..." -ForegroundColor Green
    robocopy $CitypackSource $stageCitypacks /E /NFL /NDL /NJH /NJS /nc /ns /np | Out-Null
}

$akron = Join-Path $stageCitypacks "akron-oh-beta-001\akron_routes.json"
if (-not (Test-Path $akron)) {
    Write-Host "ERROR: Akron citypack missing at $akron" -ForegroundColor Red
    exit 1
}

$manifest = @{
    schema = "racegps.windows_installer_payload.v1"
    staged_at = (Get-Date).ToUniversalTime().ToString("o")
    game_root = $match.Root
    game_exe = $stageExe
    game_exe_relative = "Binaries\Win64\raceGPS.exe"
    citypacks = $stageCitypacks
} | ConvertTo-Json -Depth 4
Set-Content -Path (Join-Path $StageDir "installer-payload.json") -Value $manifest -Encoding UTF8

$worldManifest = @{
    schema = "racegps.world_content.v1"
    worlds = @(
        @{
            id = "akron"
            package = "/Game/Maps/AkronWorld"
            citypack = "akron-oh-beta-001"
            min_cooked_bytes = 50000
            required_files = @("Content/Maps/AkronWorld.umap")
        }
    )
} | ConvertTo-Json -Depth 6
Set-Content -Path (Join-Path $StageDir "world-content-manifest.json") -Value $worldManifest -Encoding UTF8

Write-Host "Installer payload ready." -ForegroundColor Cyan
Write-Host "  Game exe: $stageExe"
Write-Host "  Citypacks: $stageCitypacks"
exit 0