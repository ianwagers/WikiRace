@echo off
echo 🔧 Installing PyQt6 and dependencies...
echo ========================================

REM Set the path to your local Python 3.13 installation
set PYTHON313_PATH=%~dp0Python313\python.exe

REM Check if local Python 3.13 is available
echo 🔍 Checking for local Python 3.13...
if not exist "%PYTHON313_PATH%" (
    echo ❌ Local Python 3.13 not found at: %PYTHON313_PATH%
    echo 💡 Make sure Python313 directory exists in your project folder
    pause
    exit /b 1
)

echo ✅ Found Python 3.13 at: %PYTHON313_PATH%

REM Install PyQt6 and dependencies
echo 🔄 Installing PyQt6...
"%PYTHON313_PATH%" -m pip install PyQt6>=6.7.0
if %errorlevel% neq 0 (
    echo ❌ Failed to install PyQt6
    pause
    exit /b 1
)

echo 🔄 Installing PyQt6-WebEngine...
"%PYTHON313_PATH%" -m pip install PyQt6-WebEngine>=6.7.0
if %errorlevel% neq 0 (
    echo ❌ Failed to install PyQt6-WebEngine
    pause
    exit /b 1
)

echo 🔄 Installing requests...
"%PYTHON313_PATH%" -m pip install requests>=2.32.0

echo 🔄 Installing beautifulsoup4...
"%PYTHON313_PATH%" -m pip install beautifulsoup4>=4.12.0

echo 🔄 Installing lxml...
"%PYTHON313_PATH%" -m pip install lxml>=5.0.0

echo 🔄 Installing project in development mode...
"%PYTHON313_PATH%" -m pip install -e .

echo.
echo ✅ PyQt6 installation completed!
echo.
echo 📋 Next steps:
echo 1. Try running your project again
echo 2. If you still get errors, try running: setup.bat
echo.
pause
