@echo off
REM raceGPS Cleveland Historic Circuit - 3-car physical race (G5)
REM Does NOT change GlobalDefaultGameMode (Akron stays CruiseSprint).
REM Usage:
REM   LaunchClevelandRace.bat [Sunset|Twilight|Midnight]
REM   LaunchClevelandRace.bat nullrhi [Sunset|Twilight|Midnight]
REM   LaunchClevelandRace.bat playtest   (auto-drive lap + EndRace proof)
setlocal
set UE=C:\Program Files\Epic Games\UE_5.7\Engine\Binaries\Win64\UnrealEditor.exe
set PROJ=%~dp0raceGPSAkronBeta.uproject
set MAP=/Game/Maps/Cleveland5_0KmWorld
set GAME=/Script/raceGPSAkronBeta.ClevelandShowcaseGameMode
set PRESET=Sunset
set MODE=%~1
if /I "%MODE%"=="nullrhi" (
  set PRESET=Sunset
  if not "%~2"=="" set PRESET=%~2
  set EXTRA=-ClevelandPreset=%PRESET% -ClevelandAutoLap -ClevelandSkipIntro -nullrhi -log -unattended -nosound
  goto :launch
)
if /I "%MODE%"=="playtest" (
  set PRESET=Sunset
  if not "%~2"=="" set PRESET=%~2
  set EXTRA=-ClevelandPreset=%PRESET% -ClevelandAutoLap -ClevelandSkipIntro -log -windowed -ResX=1600 -ResY=900
  goto :launch
)
if not "%~1"=="" set PRESET=%~1
set EXTRA=-ClevelandPreset=%PRESET% -log -windowed -ResX=1600 -ResY=900
:launch
if not exist "%UE%" (
  echo UnrealEditor not found at %UE%
  exit /b 1
)
echo Launching raceGPS Cleveland Historic Circuit RACE (PROVISIONAL Burke pack)...
echo   map    %MAP%
echo   game   %GAME%
echo   preset %PRESET%
echo   GlobalDefaultGameMode unchanged (CruiseSprint)
start "raceGPS Cleveland Race" "%UE%" "%PROJ%" "%MAP%?game=%GAME%" -game %EXTRA%