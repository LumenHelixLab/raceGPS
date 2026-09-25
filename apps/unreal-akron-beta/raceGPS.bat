@echo off
REM raceGPS launcher with GPU lock (Workshop vs Race)
REM Does NOT change GlobalDefaultGameMode (Akron stays CruiseSprint).
REM Usage: raceGPS.bat workshop|race [extra args...]
setlocal EnableExtensions EnableDelayedExpansion

REM Capture bat directory BEFORE any shift (shift replaces %0 on Windows cmd)
set "ROOT=%~dp0"
for %%I in ("%ROOT%..\..") do set "REPO=%%~fI"

set "MODE=%~1"
if /I not "%MODE%"=="workshop" if /I not "%MODE%"=="race" (
  echo Usage: raceGPS.bat workshop^|race [extra args...]
  exit /b 2
)

REM Collect extra args after mode (shift does not update %%*)
set "EXTRA="
shift
:collect_args
if "%~1"=="" goto args_done
if defined EXTRA (
  set "EXTRA=!EXTRA! %1"
) else (
  set "EXTRA=%1"
)
shift
goto collect_args
:args_done

set "LOCK_DIR=%ROOT%Saved\raceGPS"
set "LOCK=%LOCK_DIR%\gpu.lock"
set "UE=C:\Program Files\Epic Games\UE_5.7\Engine\Binaries\Win64\UnrealEditor.exe"
set "PROJ=%ROOT%raceGPSAkronBeta.uproject"
set "PY=%REPO%\.venv-grokbot\Scripts\python.exe"
set "LOCK_PY=%REPO%\tools\rgpack\launcher_lock.py"

if not exist "%PY%" (
  echo Python not found at %PY%
  exit /b 1
)
if not exist "%LOCK_PY%" (
  echo Lock helper not found at %LOCK_PY%
  exit /b 1
)

if not exist "%LOCK_DIR%" mkdir "%LOCK_DIR%"

REM Resolve current holder via temp file (avoids for /f quoting issues)
set "HOLDER="
"%PY%" "%LOCK_PY%" is_held "%LOCK%" > "%LOCK_DIR%\holder.txt" 2>nul
set /p HOLDER=<"%LOCK_DIR%\holder.txt"
del "%LOCK_DIR%\holder.txt" >nul 2>&1

if /I "%MODE%"=="workshop" (
  if /I "!HOLDER!"=="race" (
    echo [raceGPS] REFUSED: GPU lock held by Race. Close Race before launching Workshop.
    exit /b 1
  )
  "%PY%" "%LOCK_PY%" acquire "%LOCK%" workshop
  if errorlevel 1 (
    echo [raceGPS] REFUSED: could not acquire GPU lock as workshop.
    exit /b 1
  )
  set "OWNER=workshop"
  set "BIN=%ROOT%Binaries\Win64\raceGPSWorkshop.exe"
  goto launch
)

if /I "%MODE%"=="race" (
  if /I "!HOLDER!"=="workshop" (
    echo [raceGPS] REFUSED: GPU lock held by Workshop. Close Workshop before launching Race.
    exit /b 1
  )
  "%PY%" "%LOCK_PY%" acquire "%LOCK%" race
  if errorlevel 1 (
    echo [raceGPS] REFUSED: could not acquire GPU lock as race.
    exit /b 1
  )
  set "OWNER=race"
  set "BIN=%ROOT%Binaries\Win64\raceGPSRace.exe"
  goto launch
)

:launch
set "EXITCODE=0"
if exist "!BIN!" (
  echo [raceGPS] Launching %MODE% via Development binary:
  echo   !BIN!
  if defined EXTRA (
    "!BIN!" !EXTRA!
  ) else (
    "!BIN!"
  )
  set "EXITCODE=!ERRORLEVEL!"
) else (
  if not exist "%UE%" (
    echo UnrealEditor not found at %UE%
    "%PY%" "%LOCK_PY%" release "%LOCK%" !OWNER!
    exit /b 1
  )
  echo [raceGPS] NOTE: full %MODE% binary not cooked yet - falling back to editor -game.
  echo   UE    %UE%
  echo   PROJ  %PROJ%
  echo   GlobalDefaultGameMode unchanged ^(CruiseSprint^)
  if defined EXTRA (
    "%UE%" "%PROJ%" -game -log !EXTRA!
  ) else (
    "%UE%" "%PROJ%" -game -log
  )
  set "EXITCODE=!ERRORLEVEL!"
)

"%PY%" "%LOCK_PY%" release "%LOCK%" !OWNER!
exit /b !EXITCODE!
