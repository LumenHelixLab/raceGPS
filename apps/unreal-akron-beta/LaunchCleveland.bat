@echo off
REM raceGPS Cleveland Historic Circuit - solo drive (G4)
REM Does NOT change GlobalDefaultGameMode (Akron stays CruiseSprint).
REM Usage: LaunchCleveland.bat [Sunset|Twilight|Midnight] [capture]
setlocal
set UE=C:\Program Files\Epic Games\UE_5.7\Engine\Binaries\Win64\UnrealEditor.exe
set PROJ=%~dp0raceGPSAkronBeta.uproject
set MAP=/Game/Maps/Cleveland5_0KmWorld
set GAME=/Script/raceGPSAkronBeta.ClevelandSoloGameMode
set PRESET=Sunset
if not "%~1"=="" set PRESET=%~1
set EXTRA=-ClevelandPreset=%PRESET% -log -windowed -ResX=1600 -ResY=900
if /I "%~2"=="capture" (
  set EXTRA=%EXTRA% -ClevelandCapture=%PRESET%_hero
)
if /I "%~1"=="nullrhi" (
  set PRESET=Sunset
  if not "%~2"=="" set PRESET=%~2
  set EXTRA=-ClevelandPreset=%PRESET% -nullrhi -log -unattended -nosound
)
if not exist "%UE%" (
  echo UnrealEditor not found at %UE%
  exit /b 1
)
echo Launching raceGPS Cleveland Historic Circuit (PROVISIONAL Burke pack)...
echo   map    %MAP%
echo   game   %GAME%
echo   preset %PRESET%
echo   GlobalDefaultGameMode unchanged (CruiseSprint)
start "raceGPS Cleveland" "%UE%" "%PROJ%" "%MAP%?game=%GAME%" -game %EXTRA%
