@echo off
echo ========================================
echo   WikiRace Portable Build Script
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.13+ from https://python.org
    echo.
    pause
    exit /b 1
)

echo Python found. Building portable version...
echo.

REM Run the build script
python build_portable.py

echo.
echo Build completed! Check the build_portable directory.
echo.
pause
