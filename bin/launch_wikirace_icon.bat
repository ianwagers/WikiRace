@echo off
REM WikiRace Launcher with Proper Taskbar Icon
REM This ensures the favicon.ico appears in the Windows taskbar

cd /d "%~dp0.."

REM Set the application title for better taskbar identification
set WIKIRACE_TITLE=WikiRace

REM Launch with proper icon handling
python bin/main.py

REM Keep window open if there's an error
if errorlevel 1 (
    echo.
    echo WikiRace encountered an error. Press any key to exit.
    pause >nul
)
