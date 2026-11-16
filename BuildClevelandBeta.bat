@echo off
setlocal
cd /d "%~dp0"
REM Builds the approved two-car Cleveland beta and keeps logs beside its report.
REM Pass --check for engine preflight, or --engine "D:\Epic Games\UE_5.7".
REM The packaged Windows\Play-raceGPS.bat runs without an editor or source tree.
if exist "%~dp0.venv-grokbot\Scripts\python.exe" (
  "%~dp0.venv-grokbot\Scripts\python.exe" scripts\build.py --profile cleveland-beta --max-parallel-actions 2 %*
  goto :done
)
where py >nul 2>nul
if not errorlevel 1 (
  py -3 scripts\build.py --profile cleveland-beta --max-parallel-actions 2 %*
  goto :done
)
python scripts\build.py --profile cleveland-beta --max-parallel-actions 2 %*
:done
set "build_exit=%errorlevel%"
if not "%build_exit%"=="0" (
  echo Cleveland beta build failed. Read the Evidence path printed above.
) else (
  echo Build command completed. Packaging does not certify a visible race or rematch.
)
exit /b %build_exit%
