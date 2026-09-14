@echo off
setlocal
cd /d "%~dp0"
set "UV=uv"
if exist "%~dp0bin\windows-x64\uv.exe" set "UV=%~dp0bin\windows-x64\uv.exe"
if exist "%~dp0bin\uv.exe" set "UV=%~dp0bin\uv.exe"
"%UV%" run --locked python main.py %*
exit /b %errorlevel%
