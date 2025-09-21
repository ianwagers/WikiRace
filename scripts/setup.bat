@echo off
echo 🎮 WikiRace Python 3.13 Setup
echo ================================

REM Set the path to your local Python 3.13 installation
set PYTHON313_PATH=%~dp0..\Python313\python.exe

REM Check if local Python 3.13 is available, otherwise use system Python
echo 🔍 Checking for local Python 3.13...
if not exist "%PYTHON313_PATH%" (
    echo ⚠️  Local Python 3.13 not found at: %PYTHON313_PATH%
    echo 💡 Using system Python instead
    set PYTHON313_PATH=python
) else (
    echo ✅ Found local Python 3.13 at: %PYTHON313_PATH%
)

REM Check Python version
echo 🔍 Checking Python version...
"%PYTHON313_PATH%" --version
if %errorlevel% neq 0 (
    echo ❌ Python 3.13 not working. Please check your Python313 installation
    pause
    exit /b 1
)

REM Create virtual environment using local Python 3.13
echo 🔄 Creating virtual environment with local Python 3.13...
"%PYTHON313_PATH%" -m venv venv
if %errorlevel% neq 0 (
    echo ❌ Failed to create virtual environment
    pause
    exit /b 1
)

REM Activate virtual environment
echo 🔄 Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo 🔄 Upgrading pip...
python -m pip install --upgrade pip

REM Install project dependencies
echo 🔄 Installing project dependencies...
pip install -e .

REM Install development dependencies
echo 🔄 Installing development dependencies...
pip install -e .[dev]

echo.
echo ✅ Setup completed successfully!
echo.
echo 📋 Next steps:
echo 1. Activate the virtual environment: venv\Scripts\activate
echo 2. Run the application: python src/app.py
echo 3. Or use the command: wikirace
echo.
echo 💡 Tips:
echo - Make sure you have PyQt6 installed properly
echo - If you encounter issues, try: pip install --upgrade PyQt6 PyQt6-WebEngine
echo.
pause
