@echo off
setlocal
REM Canonical build/cook/archive path. Requires Python 3.11+ and Unreal 5.7.
REM Pass --engine or set RACEGPS_UE_ROOT. Legacy UE5_BUILD is also supported.
where py >nul 2>nul
if errorlevel 1 goto python_fallback
py -3 "%~dp0..\..\scripts\build.py" %*
exit /b %errorlevel%
:python_fallback
python "%~dp0..\..\scripts\build.py" %*
exit /b %errorlevel%
