@echo off
setlocal enableextensions enabledelayedexpansion

echo ==================================================
echo FORZA HORIZON CRUISE CONTROL - LAUNCHER
echo ==================================================

:: Sprawdzanie czy folder jest repozytorium Git
if exist ".git" (
    echo [1/3] Git repository detected. Pulling latest updates...
    git pull
    echo.
) else (
    echo [1/3] Not a Git repository. Skipping git pull...
    echo.
)

:: Synchronizacja zależności za pomocą uv
echo [2/3] Synchronizing environment with uv...
uv sync
if %errorlevel% neq 0 (
    echo.
    echo ❌ ERROR: "uv sync" failed. Make sure uv is installed.
    pause
    exit /b %errorlevel%
)
echo.

:: Uruchomienie skryptu
echo [3/3] Starting Cruise Control...
echo ==================================================
echo.

uv run cruise-control.py

if %errorlevel% neq 0 (
    echo.
    echo ❌ Script exited with an error.
    pause
)