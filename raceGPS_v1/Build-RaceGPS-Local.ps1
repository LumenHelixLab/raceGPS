# Run from Windows PowerShell 5.1+; no administrator rights or Grok required.
[CmdletBinding()]
param(
    [string]$Repo = 'D:\projects\raceGPS',
    [string]$Engine = '',
    [string]$Bundle = (Join-Path $PSScriptRoot 'raceGPS-current.bundle'),
    [switch]$CheckOnly
)
$ErrorActionPreference = 'Stop'
$raceRecord = [ordered]@{ schema_version=1; status='failed'; user_reported_engine='5.7.4'; unreal_compiled=$false; packaged=$false; play_tested=$false; steps=@() }
$raceStamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$raceEvidence = Join-Path $PSScriptRoot ('raceGPS-evidence-' + $raceStamp)
New-Item -ItemType Directory -Path $raceEvidence -ErrorAction Stop | Out-Null

function Invoke-RaceCommand {
    param([string]$Name, [string]$Program, [string[]]$Arguments, [switch]$AllowFailure)
    if (-not (Test-Path -LiteralPath $Program -PathType Leaf)) { throw "Executable missing: $Program" }
    $raceLog = Join-Path $raceEvidence ($Name + '.log')
    # Redirect native stderr into the retained log without converting it into a
    # PowerShell terminating error; the native exit code is authoritative.
    $racePreviousPreference = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    $global:LASTEXITCODE = 1
    & $Program @Arguments 2>&1 | Tee-Object -FilePath $raceLog
    $raceExit = $LASTEXITCODE
    $ErrorActionPreference = $racePreviousPreference
    $raceRecord.steps += @{name=$Name; program=$Program; arguments=$Arguments; exit_code=$raceExit; log=$raceLog}
    if ($raceExit -ne 0 -and -not $AllowFailure) { throw "$Name failed with exit code $raceExit; see $raceLog" }
}

try {
    $raceGit = (Get-Command git -ErrorAction Stop).Source
    if (-not (Test-Path -LiteralPath $Repo)) { throw "Repository not found: $Repo. Pass -Repo with the real path." }
    $Repo = (Resolve-Path -LiteralPath $Repo).Path
    Invoke-RaceCommand 'repository-status' $raceGit @('-C', $Repo, 'status', '--short')
    $raceRecord.repo = $Repo
    $raceRecord.running_editors = @(Get-Process -Name 'UnrealEditor','UnrealEditor-Cmd' -ErrorAction SilentlyContinue | Select-Object Id,ProcessName)

    if (-not $Engine) {
        $raceCandidates = @()
        $raceLauncher = Join-Path $env:ProgramData 'Epic\UnrealEngineLauncher\LauncherInstalled.dat'
        if (Test-Path -LiteralPath $raceLauncher) {
            $raceInstallations = (Get-Content -Raw -LiteralPath $raceLauncher | ConvertFrom-Json).InstallationList
            $raceCandidates += @($raceInstallations | Where-Object { $_.AppName -like 'UE_*' } | ForEach-Object { $_.InstallLocation })
        }
        $raceDefaultRoot = Join-Path $env:ProgramFiles 'Epic Games'
        if (Test-Path -LiteralPath $raceDefaultRoot) {
            $raceCandidates += @(Get-ChildItem -LiteralPath $raceDefaultRoot -Directory -Filter 'UE_*' | ForEach-Object { $_.FullName })
        }
        foreach ($raceCandidate in ($raceCandidates | Select-Object -Unique)) {
            $raceVersionPath = Join-Path $raceCandidate 'Engine\Build\Build.version'
            if (Test-Path -LiteralPath $raceVersionPath) {
                $raceVersion = Get-Content -Raw -LiteralPath $raceVersionPath | ConvertFrom-Json
                if ($raceVersion.MajorVersion -eq 5 -and $raceVersion.MinorVersion -eq 7) {
                    $Engine = $raceCandidate
                    if ($raceVersion.PatchVersion -eq 4) { break }
                }
            }
        }
    }
    if (-not $Engine) { throw 'Unreal 5.7 was not found automatically. Pass -Engine with its actual installation directory.' }
    $raceVersion = Get-Content -Raw -LiteralPath (Join-Path $Engine 'Engine\Build\Build.version') | ConvertFrom-Json
    if ($raceVersion.MajorVersion -ne 5 -or $raceVersion.MinorVersion -ne 7) { throw 'This checkpoint requires Unreal 5.7; no project downgrade was performed.' }
    $raceRecord.engine = $Engine
    $raceRecord.engine_version = $raceVersion
    Write-Host "Detected Unreal $($raceVersion.MajorVersion).$($raceVersion.MinorVersion).$($raceVersion.PatchVersion) at $Engine"
    if ($CheckOnly) {
        $raceRecord.status = 'host_discovered_build_not_run'
    }
    else {
        if ($raceRecord.running_editors.Count -gt 0) { throw 'Save your work and close Unreal Editor before the C++/header build, then rerun. No editor process was stopped.' }
        $raceHashPath = $Bundle + '.sha256'
        if (-not (Test-Path -LiteralPath $raceHashPath)) { throw 'Bundle checksum file is missing; extract the whole local-build archive.' }
        $raceExpectedHash = (Get-Content -Raw -LiteralPath $raceHashPath).Trim()
        if ((Get-FileHash -LiteralPath $Bundle -Algorithm SHA256).Hash.ToLowerInvariant() -ne $raceExpectedHash.ToLowerInvariant()) { throw 'Transfer bundle checksum mismatch' }
        Invoke-RaceCommand 'bundle-verify' $raceGit @('-C',$Repo,'bundle','verify',$Bundle)
        Invoke-RaceCommand 'bundle-fetch' $raceGit @('-C',$Repo,'fetch',$Bundle,'refs/heads/codex/d1-cleveland-build-baseline')
        $raceRevision = (& $raceGit -C $Repo rev-parse FETCH_HEAD).Trim()
        if ($LASTEXITCODE -ne 0) { throw 'Cannot resolve imported revision' }
        $raceRecord.source_commit = $raceRevision
        $raceWorktree = Join-Path (Split-Path -Parent $Repo) ('raceGPS-build-' + $raceStamp)
        Invoke-RaceCommand 'worktree' $raceGit @('-C',$Repo,'worktree','add','-b',('codex/local-build-' + $raceStamp),$raceWorktree,$raceRevision)
        $raceRecord.worktree = $raceWorktree
        Push-Location -LiteralPath $raceWorktree
        try {
            $racePythonLauncher = (Get-Command py -ErrorAction Stop).Source
            $raceVenv = Join-Path $raceEvidence 'python-env'
            Invoke-RaceCommand 'python-environment' $racePythonLauncher @('-3.12','-m','venv',$raceVenv)
            $racePython = Join-Path $raceVenv 'Scripts\python.exe'
            Invoke-RaceCommand 'python-dependencies' $racePython @('-m','pip','install','-r','requirements-dev.txt')
            Invoke-RaceCommand 'portable-tests' $racePython @('-m','pytest','tests','-q')
            Invoke-RaceCommand 'city-audit' $racePython @('scripts/citypack_audit.py','citypacks/akron-oh-beta-001','--report',(Join-Path $raceEvidence 'city-audit.json')) -AllowFailure
            Invoke-RaceCommand 'unreal-preflight' $racePython @('scripts/build.py','--check','--engine',$Engine,'--report',(Join-Path $raceEvidence 'preflight.json'))
            $raceProject = Join-Path $raceWorktree 'apps\unreal-akron-beta\raceGPSAkronBeta.uproject'
            Invoke-RaceCommand 'editor-compile' (Join-Path $Engine 'Engine\Build\BatchFiles\Build.bat') @('raceGPSAkronBetaEditor','Win64','Development',('-project=' + $raceProject),'-waitmutex')
            $raceRecord.unreal_compiled = $true
            $raceRecord.status = 'editor_compiled_packaging_and_playtest_pending'
        }
        finally { Pop-Location }
    }
}
catch {
    $raceRecord.error = $_.Exception.Message
    Write-Host $raceRecord.error -ForegroundColor Red
}
finally {
    $raceRecord.finished_at = (Get-Date).ToUniversalTime().ToString('o')
    $raceRecord | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $raceEvidence 'result.json') -Encoding UTF8
    $raceLogs = @(Get-ChildItem -LiteralPath $raceEvidence -File)
    if ($raceLogs.Count -gt 0) { Compress-Archive -LiteralPath $raceLogs.FullName -DestinationPath ($raceEvidence + '.zip') }
    Write-Host "Evidence to attach in ChatGPT: $raceEvidence.zip"
}
if ($raceRecord.status -eq 'failed') { exit 1 }
