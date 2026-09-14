@echo off
setlocal
cd /d "%~dp0"
where uv >nul 2>&1
if errorlevel 1 (
    echo Install uv first, then run build.bat again. Node.js 22 is also required.
    exit /b 1
)
uv run --locked --group build --group test python build.py %*
exit /b %errorlevel%
