@echo off
REM WikiRace Multiplayer Client Installation Script
REM Automates the setup process for the WikiRace client

setlocal EnableDelayedExpansion

REM Colors (limited in Windows batch)
set "GREEN=[92m"
set "RED=[91m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "NC=[0m"

echo %BLUE%
echo ==========================================
echo    WikiRace Multiplayer Client Setup
echo    Version 1.7.0
echo ==========================================
echo %NC%

REM Check if Python is installed
echo %GREEN%[STEP]%NC% Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo %RED%[ERROR]%NC% Python is not installed or not in PATH.
    echo Please install Python 3.11+ from https://python.org
    pause
    exit /b 1
)

REM Check Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo %BLUE%[INFO]%NC% Found Python version: %PYTHON_VERSION%

REM Check if we're in the right directory
if not exist "src\app.py" (
    echo %RED%[ERROR]%NC% Not in WikiRace project directory.
    echo Please run this script from the WikiRace root directory.
    pause
    exit /b 1
)

REM Create virtual environment
echo %GREEN%[STEP]%NC% Creating virtual environment...
if exist "venv" (
    echo %YELLOW%[WARN]%NC% Virtual environment already exists.
) else (
    python -m venv venv
    if errorlevel 1 (
        echo %RED%[ERROR]%NC% Failed to create virtual environment.
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo %GREEN%[STEP]%NC% Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo %RED%[ERROR]%NC% Failed to activate virtual environment.
    pause
    exit /b 1
)

REM Upgrade pip
echo %GREEN%[STEP]%NC% Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo %GREEN%[STEP]%NC% Installing dependencies...
if exist "requirements.txt" (
    pip install -r requirements.txt
) else (
    REM Install core dependencies manually
    pip install PyQt6>=6.7.0
    pip install PyQt6-WebEngine>=6.7.0
    pip install requests>=2.32.0
    pip install beautifulsoup4>=4.12.0
    pip install python-socketio[client]>=5.8.0
    pip install websocket-client>=1.6.0
)

if errorlevel 1 (
    echo %RED%[ERROR]%NC% Failed to install dependencies.
    echo Try running: pip install --upgrade pip setuptools wheel
    pause
    exit /b 1
)

REM Test the installation
echo %GREEN%[STEP]%NC% Testing installation...
python -c "import PyQt6; import requests; import socketio; print('All dependencies imported successfully')"
if errorlevel 1 (
    echo %RED%[ERROR]%NC% Installation test failed.
    echo Some dependencies may not be properly installed.
    pause
    exit /b 1
)

REM Create desktop shortcut (optional)
echo %GREEN%[STEP]%NC% Creating shortcuts...
set "CURRENT_DIR=%CD%"
set "SHORTCUT_PATH=%USERPROFILE%\Desktop\WikiRace Multiplayer.lnk"

REM Create a simple batch file to run the application
echo @echo off > run_wikirace.bat
echo cd /d "%CURRENT_DIR%" >> run_wikirace.bat
echo call venv\Scripts\activate.bat >> run_wikirace.bat
echo python bin\main.py >> run_wikirace.bat
echo pause >> run_wikirace.bat

echo %BLUE%[INFO]%NC% Created run_wikirace.bat to start the application

REM Success message
echo.
echo %GREEN%=========================================%NC%
echo %GREEN%   Installation completed successfully!%NC%
echo %GREEN%=========================================%NC%
echo.
echo To start WikiRace Multiplayer:
echo   1. Double-click run_wikirace.bat, or
echo   2. Run: python bin\main.py
echo.
echo For multiplayer functionality:
echo   1. Start the server (see server\DEPLOYMENT.md)
echo   2. Configure server settings in the client
echo   3. Create or join a multiplayer room
echo.

REM Ask if user wants to start the application now
set /p "START_NOW=Start WikiRace now? (y/n): "
if /i "%START_NOW%"=="y" (
    echo %BLUE%[INFO]%NC% Starting WikiRace...
    python bin\main.py
)

echo.
echo Installation complete. Enjoy playing WikiRace!
pause
