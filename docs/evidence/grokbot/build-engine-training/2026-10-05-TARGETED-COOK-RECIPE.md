# B&E: Targeted skyline cook recipe (2026-10-05)

**Lane:** Build & Engine
**Status:** **DOCS ONLY. NOT RUN. NOT PASS.** This file is a recipe. Nothing in it was executed on omni when it was written.
**Worktree:** `C:\projects\raceGPS-grokbot-cleveland`, branch `grokbot/cleveland-integration`, tip `9604d0b` when this was written. UE **5.7.4** (`++UE5+Release-5.7-CL-51494982`).
**Supersedes:** the "Next" section of `2026-09-27-SKYLINE-ASSET-COOK-ABORT.md`. It does **not** supersede that abort note's verdict. The 09-27 cook is still **ABORT / KILLED_BY_BE**.
**Still valid:** `2026-09-27-SKYLINE-ASSET-LOAD-CHECK.md` **LOAD PASS**. That was UnrealEditor-Cmd plus Python under NullRHI, so it is asset load only and **not Gate 1**.

## 0. Locks (unchanged, restated)

| Lock | State |
|------|-------|
| `GlobalDefaultGameMode=/Script/raceGPSAkronBeta.CruiseSprintGameMode` | **Stays.** This recipe edits no `.ini`. Every config change below is a per-process `-ini:` command-line override. |
| NullRHI / `-nullrhi` | A cook with `-NullRHI` is **cook evidence only. It is never Gate 1 evidence.** |
| `LaunchClevelandRace.bat` / `-game` / Gate 1 | **No unattended launch.** This recipe never calls them. |
| Full Windows cook / `BuildCookRun` / `package_cleveland_solo.ps1` | **No full-cook retry.** That is the G4 family: AutomationTool exit 25, `HARD_CAP_KILLED`. This recipe is a single-package cook into a separate sandbox. |
| One UnrealEditor owner on omni | When this was written, World Environment held the editor lock for still captures. A cook run counts as an editor owner, so it waits for WE to release the lock. |
| Running this recipe | **Requires an Unreal PM gate AND Chris's explicit unlock** (see section 6). |

---

## 1. What ran on 2026-09-27 (cited)

Source: `2026-09-27-skyline-asset-cook.log`. Line numbers below refer to that file. Its timestamps are **UTC**, so `2026.09.28-00.44` UTC = **2026-09-27 20:44 ET**.

L322 (`LogInit: Command Line:`):

```text
raceGPSAkronBeta.uproject -run=Cook -TargetPlatform=Windows
  -CookPackages=/Game/Materials/M_SkylineBackdrop+/Game/Textures/T_Cleveland_SkylineNight
  -Unversioned -legacyiterative -unattended -nosplash -NullRHI -nosound -stdout -FullStdOutLogOutput
```

The meta file (`2026-09-27-skyline-asset-cook.meta.txt`) records: `COOK_START=2026-09-27T20:43:43-04:00`, `COOK_PID=26284`, `COOK_EXIT=KILLED_BY_BE`, `COOK_KILL_AT=2026-09-27T20:48:23-04:00`.

## 2. Root cause of the escalation

The cook went "full" for three separate reasons. Fixing only one of them would still have stalled.

### 2a. `-CookPackages=` does not exist in UE 5.7.4, so the package list was empty, so the cooker fell back to cook-all

- Engine source, `Engine\Source\Editor\UnrealEd\Private\Commandlets\CookCommandlet.cpp` (5.7.4, local install on omni):
  - L364-366: the only package-list switches are `-MAP=` and `-PACKAGE=`, both `+`-separated:
    `CmdLineMapEntries += GetSwitchValueElements(TEXT("MAP")); CmdLineMapEntries += GetSwitchValueElements(TEXT("PACKAGE"));`
  - The file contains no `COOKPACKAGES` switch. The cooker silently ignored `-CookPackages=...`.
- `Engine\Source\Editor\UnrealEd\Private\CookOnTheFlyServer.cpp`:
  - L253-257: `Cook.CookAllByDefault = true`, described as "When FilesInPath is empty. Cook all packages by default."
  - L8776-8780: `if (bCookAll || (UE::Cook::bCookAllByDefault && NumFilesAddedByCommandLineOrGameCallback == 0))`. With zero command-line packages, the cooker adds every `*.uasset` and `*.umap` in the project (`EInstigator::FullDepotSearch`, L8811).
- Project config gave it nothing narrower either:
  - `Config\DefaultGame.ini` has **no** `[/Script/UnrealEd.ProjectPackagingSettings]` section, so there is no `MapsToCook`, no `DirectoriesToAlwaysCook`, and no `bCookAll`.
  - `Config\DefaultEngine.ini` `[/Script/EngineSettings.GameMapsSettings]` sets only `GlobalDefaultGameMode` and `GameInstanceClass`. There is **no `GameDefaultMap`**.
  - So DirectoriesToAlwaysCook and startup maps were **not** the culprit. The culprit was the empty command-line list plus the `CookAllByDefault` fallback.
- `.uproject` plugins (`ChaosVehiclesPlugin`, `ModelingToolsEditorMode` [Editor-only], `PythonScriptPlugin`, `EditorScriptingUtilities`) add no cook roots. This is not a plugin issue.

### 2b. `-legacyiterative` could not be incremental, so it wiped the existing `Saved\Cooked\Windows`

- Log L1036: `INCREMENTAL COOK DEPENDENCIES: Disabled ... cooker is not using ZenStore ... Falling back to legacy iterative cook mode.`
- Log L1045: `Invalidating inisettings: Unable to read previous cook inisettings for platform Windows.` The previous sandbox had no readable `Metadata\CookedIniVersion.txt` (source: `CookOnTheFlyServer.cpp` L7495-7497, L7619-7621).
- Log L1046-1048: `Cook invalidated ... Clearing previously cooked packages.` / `FULL COOK: -legacyiterative was specified, but global settings have changed ... Deleting previously cooked packages for platform Windows ...` / `Sandbox cleanup took 0.079 seconds`. The source string is at `CookOnTheFlyServer.cpp` L10391-10393.
- **Current on-disk state (read-only check, 2026-10-05):** `apps\unreal-akron-beta\Saved\Cooked\Windows\` holds only `Engine\GlobalShaderCache-PCD3D_{SM5,SM6,ES3_1}.bin` and `raceGPSAkronBeta\Metadata\{CookedSettings.txt,scriptobjects.bin}`, plus a `Saved\Cooked\_Del\2` folder. `CookedSettings.txt` says `CookInProgress=true`. **No full Windows cook output survives.** The 09-27 run deleted it. Any future "don't invalidate the existing cook" requirement therefore applies to whatever the next attended full cook produces. This recipe never writes to `Saved\Cooked\Windows` anyway (see `-OutputDir` in section 3).

### 2c. Global shaders are compiled for **every** Windows targeted shader format, including SF_VULKAN_SM5, before any package is cooked

- `Config\DefaultEngine.ini` `[/Script/WindowsTargetPlatform.WindowsTargetSettings]`:
  ```ini
  +D3D12TargetedShaderFormats=PCD3D_SM5
  +D3D12TargetedShaderFormats=PCD3D_SM6
  +D3D12TargetedShaderFormats=PCD3D_ES31
  +D3D11TargetedShaderFormats=PCD3D_SM5
  +D3D11TargetedShaderFormats=PCD3D_ES31
  +VulkanTargetedShaderFormats=SF_VULKAN_SM5
  +VulkanTargetedShaderFormats=SF_VULKAN_SM6
  ```
  (5.7 uses the per-RHI arrays. Legacy `TargetedRHIs` is folded in as `TargetedRHIs_DEPRECATED`: `WindowsTargetPlatformClasses.cpp` L45-51.)
- `Engine\Source\Developer\Windows\WindowsTargetPlatformSettings\Public\GenericWindowsTargetPlatformSettings.h` L173-186: `GetAllTargetedShaderFormats` unions `TargetedRHIs`, `D3D12TargetedShaderFormats`, `D3D11TargetedShaderFormats`, and **`VulkanTargetedShaderFormats`**, read from `GEngineIni`. **That is why Vulkan SM5 was in scope for a "Windows" cook.**
- `Engine\Source\Editor\UnrealEd\Private\Cooker\ShaderLibraryCooking.cpp` L326-334: unless `ForceDisableSaveGlobalShaders` is set, cook-by-the-book calls `SaveGlobalShaderMapFiles(..., ODSCRecompileCommand::Changed)`. That logs `Compiling global changed shaders for platform 'Windows'` (L152) and compiles the global shader map for all of those formats.
- Log L1049-1064: `Compiling global changed shaders for platform 'Windows'`, then only `FTSRRejectShadingCS(... format SF_VULKAN_SM5) compile time exceeded threshold` lines (40-171 s each) until the kill. The PCD3D global caches had already been written at 20:44 ET (see the on-disk `.bin` mtimes). The cook stalled on Vulkan.
- **G4 twin:** `docs\evidence\grokbot\G4-packaged-solo-visual\logs\package-development-retry.log`
  - L4 `BuildCookRun ... -platform=Win64 -clientconfig=Development -build -cook -stage -pak -archive` leads to L47 `UnrealEditor-Cmd.exe ... -run=Cook -TargetPlatform=Windows -unversioned ...` (also unscoped, so cook-all).
  - L248 `FULL COOK: Incremental Cook Dependencies are disabled, and -legacyiterative was not specified.`
  - L250 `Compiling global changed shaders` leads to L251-256 `FTSRRejectShadingCS` / `FSSDTemporalAccumulationCS` on `SF_VULKAN_SM5`.
  - L258 `ShaderCompileWorker terminated unexpectedly, return code 1!`
  - L270 `Took 681.22s ... ExitCode=1` and L274 `AutomationTool exiting with ExitCode=25 (Error_UnknownCookFailure)`.
  - `logs\package-development-retry.meta.txt`: `result=HARD_CAP_KILLED`.
  - **Same failure mode:** Vulkan SM5 TSR global shaders on omni (Radeon 880M iGPU host, ~31 GB RAM).

**One-line root cause:** `-CookPackages` is not a 5.7 switch, so the package list was empty and `Cook.CookAllByDefault` ran a full depot cook. `-legacyiterative` couldn't read prior ini settings, so it wiped `Saved\Cooked\Windows`. Then the global-shader pre-step compiled every Windows format in `DefaultEngine.ini`, including `SF_VULKAN_SM5`, which stalled on `FTSRRejectShadingCS` exactly like G4.

---

## 3. Recipe: cook only the two skyline packages, separate sandbox, D3D only

### 3a. Flag table (each one checked against 5.7.4 source on omni unless marked UNVERIFIED)

| Flag | Purpose | Verified where |
|------|---------|----------------|
| `-run=Cook -TargetPlatform=Windows` | Cook-by-the-book for Windows (the game platform, not an editor platform) | Same shape as UAT's own call in G4 log L47. Epic docs "Cooking Content in Unreal Engine" (UE 5.7 docs page, fetched 2026-10-05). Note: that page still lists the legacy name `WindowsNoEditor`; 5.7 logs use `Windows`. |
| `-PACKAGE=/Game/Materials/M_SkylineBackdrop+/Game/Textures/T_Cleveland_SkylineNight` | Explicit package list, replacing the bogus `-CookPackages` | `CookCommandlet.cpp` L351-366 (`+` split, `PACKAGE` key). `CookOnTheFlyServer.cpp` L8343-8350 logs `Unable to find package for path` on a bad path. |
| `-cooksinglepackage` | Adds `NoAlwaysCookMaps`, `NoDefaultMaps`, `NoGameAlwaysCookPackages`, `NoInputPackages`, **`ForceDisableSaveGlobalShaders`**, and `SkipSoftReferences`. **Keeps hard references** (deps), so the texture and material's hard deps still cook. | `CookCommandlet.cpp` L197-199, L459-467. `ShaderLibraryCooking.cpp` L327 (skips the global-shader pre-step). `NoGameAlwaysCookPackages` also blocks the cook-all fallback (`CookOnTheFlyServer.cpp` L8777-8780). |
| *(alt)* `-cooksinglepackagenorefs` | Same, plus `SkipHardReferences`. Cooks the two packages only, with no deps. | `CookCommandlet.cpp` L197, L466 |
| `-OutputDir=C:\projects\raceGPS-grokbot-cleveland\apps\unreal-akron-beta\Saved\Cooked-targeted\Windows` | Sandbox root override. A single platform is allowed without a `[Platform]` token. The default `Saved\Cooked\[Platform]` is never touched. | `CookCommandlet.cpp` L333-334, L388. `CookOnTheFlyServer.cpp` L7099-7140 (checkf: one platform is OK without `[Platform]`). |
| **no** `-legacyiterative` / `-iterate` | In a fresh sandbox there is nothing to iterate against. Without it, the expected log line is `FULL COOK: Incremental Cook Dependencies are disabled, and -legacyiterative was not specified` (L10354). That wipe is confined to the `-OutputDir` sandbox, which is empty. Dropping it is the right call. 5.7 incremental (`-cookincremental`) needs ZenStore (log L1036), and this project cooks loose. | `CookCommandlet.cpp` L194. `CookOnTheFlyServer.cpp` L10333-10357, L10391-10393 |
| `-ini:Engine:[/Script/WindowsTargetPlatform.WindowsTargetSettings]:-VulkanTargetedShaderFormats=SF_VULKAN_SM5` | Per-process removal of Vulkan SM5. **No `.ini` edit.** | Syntax from `Runtime\Core\Private\Misc\ConfigCacheIni.cpp` L1631-1639, L2234-2322: `-ini:<Ini>:[Section]:Key=Value`, leading `-` on the key = **Remove**, leading `+` = ArrayAdd. Every `-ini:` token is applied (loop over all tokens). Comma = multiple pairs in one token (legacy, avoid). |
| `-ini:Engine:[...WindowsTargetSettings]:-VulkanTargetedShaderFormats=SF_VULKAN_SM6` | Removes Vulkan SM6 | same |
| `-ini:Engine:[...WindowsTargetSettings]:-D3D12TargetedShaderFormats=PCD3D_ES31` and `...:-D3D11TargetedShaderFormats=PCD3D_ES31` | Leaves **PCD3D_SM6 + PCD3D_SM5 only** | same |
| `-Unversioned` | Matches the 09-27 and G4 cooks | `CookCommandlet.cpp` L191 |
| `-unattended -nosplash -nosound -NullRHI` | Headless commandlet hygiene. NullRHI is fine because shader compiles are offline (SCW). **Not Gate 1.** | Used by the 09-27 load PASS and the cook. Standard engine switches. |
| `-stdout -FullStdOutLogOutput -abslog=<evidence path>` | Log lands straight in the evidence dir | `-abslog` / `-stdout` are used by UAT itself in G4 log L47 |
| `-NoLogTimes` | **Do not use.** Keep timestamps so the wall-clock cap can be audited. | n/a |

### 3b. The command (single line, PowerShell-quoted). For a FUTURE attended run only.

```powershell
# ===== DO NOT RUN without Unreal PM gate + Chris unlock (section 6) =====
$UE    = 'C:\Program Files\Epic Games\UE_5.7\Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$Proj  = 'C:\projects\raceGPS-grokbot-cleveland\apps\unreal-akron-beta\raceGPSAkronBeta.uproject'
$Out   = 'C:\projects\raceGPS-grokbot-cleveland\apps\unreal-akron-beta\Saved\Cooked-targeted\Windows'
$Ev    = 'C:\projects\raceGPS-grokbot-cleveland\docs\evidence\grokbot\build-engine-training'
$Stamp = (Get-Date -Format 'yyyy-MM-dd')
$Log   = "$Ev\$Stamp-skyline-targeted-cook.log"
$Meta  = "$Ev\$Stamp-skyline-targeted-cook.meta.txt"
$WS    = '[/Script/WindowsTargetPlatform.WindowsTargetSettings]'

$ArgList = @(
  "`"$Proj`"",
  '-run=Cook',
  '-TargetPlatform=Windows',
  '-cooksinglepackage',
  '-PACKAGE=/Game/Materials/M_SkylineBackdrop+/Game/Textures/T_Cleveland_SkylineNight',
  "-OutputDir=`"$Out`"",
  ('-ini:Engine:' + $WS + ':-VulkanTargetedShaderFormats=SF_VULKAN_SM5'),
  ('-ini:Engine:' + $WS + ':-VulkanTargetedShaderFormats=SF_VULKAN_SM6'),
  ('-ini:Engine:' + $WS + ':-D3D12TargetedShaderFormats=PCD3D_ES31'),
  ('-ini:Engine:' + $WS + ':-D3D11TargetedShaderFormats=PCD3D_ES31'),
  '-Unversioned',
  '-unattended', '-nosplash', '-nosound', '-NullRHI',
  '-stdout', '-FullStdOutLogOutput',
  "-abslog=`"$Log`""
)
```

The equivalent flat command line (for the meta file / PM review):

```text
"C:\Program Files\Epic Games\UE_5.7\Engine\Binaries\Win64\UnrealEditor-Cmd.exe"
  "C:\projects\raceGPS-grokbot-cleveland\apps\unreal-akron-beta\raceGPSAkronBeta.uproject"
  -run=Cook -TargetPlatform=Windows -cooksinglepackage
  -PACKAGE=/Game/Materials/M_SkylineBackdrop+/Game/Textures/T_Cleveland_SkylineNight
  -OutputDir="C:\projects\raceGPS-grokbot-cleveland\apps\unreal-akron-beta\Saved\Cooked-targeted\Windows"
  -ini:Engine:[/Script/WindowsTargetPlatform.WindowsTargetSettings]:-VulkanTargetedShaderFormats=SF_VULKAN_SM5
  -ini:Engine:[/Script/WindowsTargetPlatform.WindowsTargetSettings]:-VulkanTargetedShaderFormats=SF_VULKAN_SM6
  -ini:Engine:[/Script/WindowsTargetPlatform.WindowsTargetSettings]:-D3D12TargetedShaderFormats=PCD3D_ES31
  -ini:Engine:[/Script/WindowsTargetPlatform.WindowsTargetSettings]:-D3D11TargetedShaderFormats=PCD3D_ES31
  -Unversioned -unattended -nosplash -nosound -NullRHI -stdout -FullStdOutLogOutput
  -abslog="C:\projects\raceGPS-grokbot-cleveland\docs\evidence\grokbot\build-engine-training\<date>-skyline-targeted-cook.log"
```

### 3c. Hard wall-clock cap + FAIL-CLOSED watcher (attended; kills only the PID it started)

```powershell
$CapMin = 15          # hard cap. Two packages should take minutes, not tens of minutes.
$Before = (Get-Item 'C:\projects\raceGPS-grokbot-cleveland\apps\unreal-akron-beta\Saved\Cooked\Windows' -ErrorAction SilentlyContinue).LastWriteTime
"COOK_START=$(Get-Date -Format o)`nFLAGS=$($ArgList -join ' ')`nNOTE=NullRHI cook only - not Gate 1; no LaunchClevelandRace" | Set-Content $Meta
$p = Start-Process -FilePath $UE -ArgumentList $ArgList -PassThru -NoNewWindow `
       -RedirectStandardOutput "$Log.stdout.txt" -RedirectStandardError "$Ev\$Stamp-skyline-targeted-cook.err.log"
"COOK_PID=$($p.Id)" | Add-Content $Meta
$deadline = (Get-Date).AddMinutes($CapMin); $kill = $null
$FailPatterns = 'SF_VULKAN','FTSRRejectShadingCS','Compiling global .*shaders','FullDepotSearch',
                'Unable to find package for path','ShaderCompileWorker terminated unexpectedly','LogCook: Error:','Fatal error'
while (-not $p.HasExited) {
  Start-Sleep 10
  if ((Get-Date) -gt $deadline) { $kill = "HARD_CAP_${CapMin}m"; break }
  if (Test-Path $Log) {
    $hit = Select-String -Path $Log -Pattern $FailPatterns | Select-Object -First 1
    if ($hit) { $kill = "FAIL_PATTERN L$($hit.LineNumber): $($hit.Line.Trim())"; break }
  }
  $now = (Get-Item 'C:\projects\raceGPS-grokbot-cleveland\apps\unreal-akron-beta\Saved\Cooked\Windows' -ErrorAction SilentlyContinue).LastWriteTime
  if ($now -ne $Before) { $kill = 'DEFAULT_SANDBOX_TOUCHED'; break }
}
if ($kill) {
  # Kill only this cook's tree (its SCW children), never another lane's editor
  & taskkill /PID $p.Id /T /F | Out-Null
  "COOK_EXIT=KILLED_BY_BE`nCOOK_KILL_REASON=$kill`nCOOK_KILL_AT=$(Get-Date -Format o)" | Add-Content $Meta
} else {
  "COOK_EXIT=$($p.ExitCode)`nCOOK_END=$(Get-Date -Format o)" | Add-Content $Meta
}
```

**FAIL-CLOSED kill criteria (any one means kill, then verdict FAIL, never PASS):**

1. Wall clock > **15 min** from `COOK_START`.
2. Any `SF_VULKAN` string in the log. That means the `-ini:` override didn't reach the target-platform config (see UNVERIFIED #1).
3. `Compiling global ... shaders`. That means `ForceDisableSaveGlobalShaders` didn't apply and the G4/09-27 path is reopening.
4. `FTSRRejectShadingCS`, or `ShaderCompileWorker terminated unexpectedly`.
5. `Unable to find package for path`. The package list didn't resolve, and the cook may fall back.
6. `Saved\Cooked\Windows` mtime changes (the default sandbox was touched).
7. `Packages Cooked:` > **50** at the end. That's a scope leak: the two packages plus hard deps should be a small number. Record the count either way.
8. Any second `UnrealEditor*.exe` started by this run other than `$p` (check via the parent PID).

### 3d. PASS / FAIL log greps (after exit)

```powershell
$L = $Log
Select-String $L -Pattern 'LogInit: Command Line:'                   # must show -cooksinglepackage, -PACKAGE=, -OutputDir=, 4x -ini:
Select-String $L -Pattern 'FULL COOK:'                               # expected: "...-legacyiterative was not specified..." (fresh sandbox only)
Select-String $L -Pattern 'Sandbox cleanup took'                     # cleanup is of Cooked-targeted only
Select-String $L -Pattern 'Compiling global'                         # MUST be 0 hits
Select-String $L -Pattern 'SF_VULKAN|FTSRRejectShadingCS'           # MUST be 0 hits
Select-String $L -Pattern 'Unable to find package for path'          # MUST be 0 hits
Select-String $L -Pattern 'Cook by the book total time'              # MUST be 1 hit (CookOnTheFlyServer.cpp L9690)
Select-String $L -Pattern 'Packages Cooked: '                        # MUST be 1 hit; record N (L9719)
Select-String $L -Pattern 'LogCook: Error:|LogShaders: Error:'       # MUST be 0 hits
Select-String $L -Pattern 'Success - \d+ error'                      # UNVERIFIED exact 5.7 summary string; informative only
# Artifacts:
Get-ChildItem "$Out\raceGPSAkronBeta\Content\Materials\M_SkylineBackdrop.*"
Get-ChildItem "$Out\raceGPSAkronBeta\Content\Textures\T_Cleveland_SkylineNight.*"
```

**PASS requires all of:** process exit code **0**; `Cook by the book total time` present; `Packages Cooked: N` with N <= 50; zero hits on `Compiling global`, `SF_VULKAN`, `FTSRRejectShadingCS`, `Unable to find package`, and `LogCook: Error:`; `.uasset` (+ `.uexp`) for both packages under `Saved\Cooked-targeted\Windows\raceGPSAkronBeta\Content\...`; and `Saved\Cooked\Windows` mtime unchanged.
**What PASS proves:** the two skyline packages cook for Windows D3D SM5/SM6. **What it does not prove:** a full cook, packaging, stills, runtime `BuildSkylineBackdrop` greps, or Gate 1.

---

## 4. Preflight checklist (all must be true before starting; record in meta)

| # | Check | Command / criterion |
|---|-------|---------------------|
| 1 | **No other Unreal owner.** WE / any lane has released the editor lock. | `Get-Process UnrealEditor,UnrealEditor-Cmd,ShaderCompileWorker,AutomationTool,UnrealBuildTool -EA SilentlyContinue` returns **nothing**. If anything is listed, **STOP** (don't kill another lane's session). |
| 2 | Exactly one owner for the run | B&E only, confirmed in the PM room before start |
| 3 | Live Coding / editor closed | Same as #1 (Build exit 6 lesson, `G1-host-baseline/VERDICT.md`) |
| 4 | Disk | C: free >= **50 GB** (2026-10-05 read: ~319.5 GB free / ~297.6 GiB) |
| 5 | DDC | `C:\Users\cgp22\AppData\Local\UnrealEngine\Common\DerivedDataCache` reachable. Zen service already exists (09-27 log L1019-1023, `zen.exe service status`). Do not wipe DDC. |
| 6 | Output dir is new | `Saved\Cooked-targeted\Windows` absent or empty. Never point `-OutputDir` at `Saved\Cooked\Windows`. |
| 7 | Default sandbox snapshot | Record `Saved\Cooked\Windows` LastWriteTime + file count in meta (used by kill criterion 6) |
| 8 | Assets on disk | `Content\Materials\M_SkylineBackdrop.uasset`, `Content\Textures\T_Cleveland_SkylineNight.uasset` present |
| 9 | No config drift | `git diff --stat -- apps/unreal-akron-beta/Config apps/unreal-akron-beta/*.uproject` is empty (overrides are command-line only) |
| 10 | Gate | PM gate posted + Chris unlock quoted in meta (section 6) |

### Evidence a future attended run must land (`docs\evidence\grokbot\build-engine-training\`)

| File | Contents |
|------|----------|
| `<date>-skyline-targeted-cook.log` | Full `-abslog` output |
| `<date>-skyline-targeted-cook.log.stdout.txt` / `.err.log` | Redirected streams |
| `<date>-skyline-targeted-cook.meta.txt` | `COOK_START`, `FLAGS`, `COOK_PID`, `COOK_EXIT` or `KILLED_BY_BE` + `COOK_KILL_REASON`, `COOK_END`, preflight #1/#4/#7 snapshots, PM gate + Chris unlock reference, `Packages Cooked` N |
| `<date>-SKYLINE-TARGETED-COOK-{PASS,FAIL}.md` | Verdict note with each section 3d grep and its hit line number |
| Mirror | Same files under `%USERPROFILE%\Documents\raceGPS-handoff\build-engine-training\` |

Never overwrite the 09-27 abort files.

---

## 5. UNVERIFIED for 5.7 (do not treat as fact until the first attended run shows it in the log)

1. **Whether the `-ini:Engine:` override reaches the Windows *target-platform* config branch** (`FConfigCacheIni::ForPlatform("Windows")`) that `GetAllTargetedShaderFormats` reads. The syntax and Remove semantics are source-verified, and `ConfigContext.cpp` L1016/L1231 applies command-line overrides per branch. Whether that branch picks up the overrides was not traced. Kill criterion 2 (`SF_VULKAN` in the log) is the fail-closed backstop. Fallback if it fails: **stop, and escalate to PM.** Do not edit `DefaultEngine.ini` without Chris.
2. **Exact `_Del` location for `-OutputDir`.** `GetSandboxDirectory("_Del")` (`CookOnTheFlyServer.cpp` L7817) is expected under the overridden sandbox's parent (`Saved\Cooked-targeted\_Del`). Not traced.
3. **Whether material shader compiles for `M_SkylineBackdrop` honour the reduced format list.** They should, because they use the same `GetAllTargetedShaderFormats`. Not run.
4. **`Success - N error(s)` summary string** in the 5.7 commandlet exit. Not found in the read source. Informative only, not a PASS criterion.
5. **`-NoUBA`**: a UBT flag (Pack 01). It is **not a cook-commandlet switch** and doesn't appear in `CookCommandlet.cpp`. Omitted. Shader-compile UBA/XGE gating for the cooker was not verified. If wanted, it needs a separate PM-approved `-ini:` override, which is UNVERIFIED.
6. **`-nop4`**: a UAT (`BuildCookRun -noP4`) flag, not a cook switch. Omitted. Revision control is already disabled in-editor (09-27 log L987-988).
7. **`-cooksinglepackage` dependency fan-out count.** Keeping hard refs means `M_SkylineBackdrop`'s hard deps (texture, any parent material/functions) cook too. The "<= 50 packages" threshold is a judgement call, not measured.
8. **Epic docs page currency**: the UE 5.7 "Cooking Content" docs page still shows `WindowsNoEditor` and `-iterate`. Both are legacy. Engine source wins wherever they disagree.

### Sources

| Source | Date / version |
|--------|----------------|
| `C:\Program Files\Epic Games\UE_5.7\Engine\Source\Editor\UnrealEd\Private\Commandlets\CookCommandlet.cpp` | UE 5.7.4 CL 51494982 (installed on omni; read 2026-10-05) |
| `...\UnrealEd\Private\CookOnTheFlyServer.cpp` | same |
| `...\UnrealEd\Private\Cooker\ShaderLibraryCooking.cpp` | same |
| `...\Developer\Windows\WindowsTargetPlatformSettings\Public\GenericWindowsTargetPlatformSettings.h`, `...\Private\WindowsTargetPlatformClasses.cpp` | same |
| `...\Runtime\Core\Private\Misc\ConfigCacheIni.cpp` | same |
| Epic: "Cooking Content in Unreal Engine" (UE 5.7 docs), https://dev.epicgames.com/documentation/unreal-engine/cooking-content-in-unreal-engine | fetched 2026-10-05 |
| Epic forums: "[5.7] Pak / IoStore / MultiCook ..." (example 5.7 UAT cook command line with `-abslog -stdout -unattended`), https://forums.unrealengine.com/t/5-7-pak-iostore-multicook-assets-do-not-get-assigned-to-pak-utoc-ucas-correctly/2735138 | posts dated 2026-05-27/28 |
| Project evidence: `2026-09-27-skyline-asset-cook.{log,meta.txt}`, `2026-09-27-SKYLINE-ASSET-COOK-ABORT.md`, `2026-09-27-SKYLINE-ASSET-LOAD-CHECK.md`, `README.md`, `2026-09-26-PACK-01-WIN64-DEV-REBUILD-AND-LOG-FORENSICS.md`, `G4-packaged-solo-visual\logs\package-development-retry.{log,meta.txt}`, `scripts\package_cleveland_solo.ps1`, `Config\DefaultEngine.ini`, `Config\DefaultGame.ini`, `raceGPSAkronBeta.uproject` | read 2026-10-05 |

---

## 6. Gate to run

**Running sections 3b-3c requires BOTH:**
1. An **Unreal PM gate** posted in the room, approving a single attended targeted cook with this exact flag set and the 15-minute cap, **and**
2. **Chris's explicit unlock** for B&E to own UnrealEditor-Cmd on omni (Mode C/D per `UNLOCK-CRITERIA`), with WE's lock released first.

Until then, the status is **DOCS ONLY / NOT RUN / NOT PASS**. The 09-27 cook stays **ABORT** and the 09-27 load check stays **LOAD PASS (not Gate 1)**.
