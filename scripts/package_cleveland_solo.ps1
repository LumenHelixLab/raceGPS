#Requires -Version 5.1
<#
.SYNOPSIS
  Cook/package Cleveland solo Windows build (G4).
.DESCRIPTION
  Uses UE 5.7 UAT BuildCookRun. Does not change GlobalDefaultGameMode.
  Map override at runtime via LaunchCleveland / -game ClevelandSoloGameMode.
  Memory-aware: Development by default; Shipping via -Shipping.
#>
param(
  [ValidateSet('Development','Shipping')]
  [string]$Config = 'Development',
  [switch]$CookOnly,
  [switch]$SkipBuild
)
$ErrorActionPreference = 'Stop'
$UERoot = 'C:\Program Files\Epic Games\UE_5.7'
$RunUAT = Join-Path $UERoot 'Engine\Build\BatchFiles\RunUAT.bat'
$Project = Join-Path $PSScriptRoot '..\apps\unreal-akron-beta\raceGPSAkronBeta.uproject' | Resolve-Path
$ArchiveDir = Join-Path $PSScriptRoot '..\docs\evidence\grokbot\G4-packaged-solo-visual\package' | Resolve-Path -ErrorAction SilentlyContinue
if (-not $ArchiveDir) {
  $ArchiveDir = Join-Path $PSScriptRoot '..\docs\evidence\grokbot\G4-packaged-solo-visual\package'
  New-Item -ItemType Directory -Force -Path $ArchiveDir | Out-Null
  $ArchiveDir = Resolve-Path $ArchiveDir
}
if (-not (Test-Path $RunUAT)) { throw "RunUAT not found: $RunUAT" }

# One Unreal build lease at a time
$busy = Get-Process -Name UnrealEditor,UnrealBuildTool,ShaderCompileWorker -ErrorAction SilentlyContinue
if ($busy) {
  Write-Host "BLOCKED: Unreal process already running:" -ForegroundColor Red
  $busy | Format-Table Name,Id
  exit 2
}

$clientCfg = if ($Config -eq 'Shipping') { 'Shipping' } else { 'Development' }
$args = @(
  "BuildCookRun",
  "-project=`"$Project`"",
  "-noP4",
  "-platform=Win64",
  "-clientconfig=$clientCfg",
  "-build",
  "-cook",
  "-stage",
  "-pak",
  "-archive",
  "-archivedirectory=`"$ArchiveDir`"",
  "-utf8output"
)
if ($CookOnly) { $args = $args | Where-Object { $_ -ne '-build' } }
if ($SkipBuild) { $args = @($args | Where-Object { $_ -ne '-build' }) }

Write-Host "raceGPS Cleveland G4 package ($clientCfg)" -ForegroundColor Cyan
Write-Host "Project: $Project"
Write-Host "Archive: $ArchiveDir"
Write-Host "NOTE: GlobalDefaultGameMode stays CruiseSprint; Cleveland is LaunchCleveland / map override only."
& $RunUAT @args
$exit = $LASTEXITCODE
Write-Host "UAT exit=$exit"
exit $exit
