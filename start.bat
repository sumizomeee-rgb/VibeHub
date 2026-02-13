@echo off
setlocal EnableDelayedExpansion
title VibeHub
echo.
echo  ========================================
echo           VibeHub v1.0 Starting
echo  ========================================
echo.

set "VIBEHUB_ROOT=%~dp0"
set "PATH=%VIBEHUB_ROOT%bin;%PATH%"
set "UV_CACHE_DIR=%VIBEHUB_ROOT%runtime"
set "XDG_DATA_HOME=%VIBEHUB_ROOT%caddy_data"

:: Claude CLI requires git-bash on Windows — auto-detect from PATH
if not defined CLAUDE_CODE_GIT_BASH_PATH (
    where bash >nul 2>&1
    if !errorlevel! equ 0 (
        for /f "delims=" %%p in ('where bash') do set "CLAUDE_CODE_GIT_BASH_PATH=%%p"
    )
)

:: ============================================
:: Clean up old processes
:: ============================================
echo [0/4] Cleaning up old processes...
taskkill /IM caddy.exe /F >nul 2>&1
:: Kill any leftover VibeHub python on port 8080
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8080" ^| findstr "LISTENING"') do (
    taskkill /PID %%a /F >nul 2>&1
)
timeout /t 1 /nobreak >nul
echo   Done
echo.

:: ============================================
:: Environment Check
:: ============================================
echo [1/4] Checking environment...

set "ENV_OK=1"

where node >nul 2>&1
if errorlevel 1 (
    echo   [X] Node.js not found - required by Claude CLI
    set "ENV_OK=0"
) else (
    echo   [OK] Node.js found
)

where npm >nul 2>&1
if errorlevel 1 (
    echo   [X] npm not found
    set "ENV_OK=0"
) else (
    echo   [OK] npm found
)

where claude >nul 2>&1
if errorlevel 1 (
    echo   [X] Claude CLI not found - run: npm install -g @anthropic-ai/claude-code
    set "ENV_OK=0"
) else (
    echo   [OK] Claude CLI found
)

where bash >nul 2>&1
if errorlevel 1 (
    echo   [X] Git Bash not found - install Git from https://git-scm.com/downloads/win
    set "ENV_OK=0"
) else (
    echo   [OK] Git Bash found
)

if not exist "%VIBEHUB_ROOT%bin\uv.exe" (
    echo   [X] bin\uv.exe not found - download from https://github.com/astral-sh/uv/releases
    set "ENV_OK=0"
) else (
    echo   [OK] uv.exe found
)

if not exist "%VIBEHUB_ROOT%bin\caddy.exe" (
    echo   [X] bin\caddy.exe not found - download from https://github.com/caddyserver/caddy/releases
    set "ENV_OK=0"
) else (
    echo   [OK] caddy.exe found
)

if "!ENV_OK!"=="0" (
    echo.
    echo  ========================================
    echo   Environment check FAILED.
    echo   Please install missing dependencies.
    echo  ========================================
    echo.
    pause
    exit /b 1
)

echo   All checks passed!
echo.

:: ============================================
:: Init directories
:: ============================================
if not exist "%VIBEHUB_ROOT%data\logs\tools" mkdir "%VIBEHUB_ROOT%data\logs\tools"
if not exist "%VIBEHUB_ROOT%projects" mkdir "%VIBEHUB_ROOT%projects"
if not exist "%VIBEHUB_ROOT%runtime" mkdir "%VIBEHUB_ROOT%runtime"
if not exist "%VIBEHUB_ROOT%caddy_data" mkdir "%VIBEHUB_ROOT%caddy_data"

if not exist "%VIBEHUB_ROOT%data\registry.json" (
    echo {} > "%VIBEHUB_ROOT%data\registry.json"
)

:: ============================================
:: Firewall rule
:: ============================================
echo [2/4] Configuring firewall...
netsh advfirewall firewall add rule name="VibeHub" dir=in action=allow protocol=TCP localport=9529 >nul 2>&1
echo   Port 9529 allowed
echo.

:: ============================================
:: Start Caddy
:: ============================================
echo [3/4] Starting Caddy gateway...
start /B "" "%VIBEHUB_ROOT%bin\caddy.exe" run 2>"%VIBEHUB_ROOT%data\logs\caddy.log"
timeout /t 2 /nobreak >nul
echo   Caddy Admin API ready (localhost:2019)
echo.

:: ============================================
:: Start VibeHub
:: ============================================
echo [4/4] Starting VibeHub...
echo.
echo   LAN access:  http://localhost:9529/
echo   Internal UI: http://127.0.0.1:8080/
echo.
"%VIBEHUB_ROOT%bin\uv.exe" run "%VIBEHUB_ROOT%main.py"

pause
