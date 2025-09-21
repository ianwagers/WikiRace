#!/usr/bin/env python3
"""
Setup script for WikiRace with Python 3.13
This script helps set up the development environment with the correct Python version.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def check_python_version():
    """Check if Python 3.13 is available."""
    print("🔍 Checking Python version...")
    
    # First, try to use local Python 3.13
    local_python_path = Path(__file__).parent / "Python313" / "python.exe"
    python_executable = None
    
    if local_python_path.exists():
        python_executable = str(local_python_path)
        print(f"🔍 Found local Python 3.13 at: {python_executable}")
    else:
        python_executable = sys.executable
        print(f"🔍 Using system Python: {python_executable}")
    
    try:
        result = subprocess.run([python_executable, "--version"], capture_output=True, text=True)
        version = result.stdout.strip()
        print(f"Current Python version: {version}")
        
        # Check if it's Python 3.13 or higher
        if "3.13" in version or "3.14" in version:
            print("✅ Python 3.13+ detected")
            return True, python_executable
        else:
            print("⚠️  Python 3.13+ not detected. Please install Python 3.13")
            return False, python_executable
    except Exception as e:
        print(f"❌ Error checking Python version: {e}")
        return False, python_executable

def setup_environment():
    """Set up the development environment."""
    print("🚀 Setting up WikiRace development environment...")
    
    # Check Python version and get the executable
    python_ok, python_executable = check_python_version()
    if not python_ok:
        print("\n📝 Please install Python 3.13 from https://www.python.org/downloads/")
        print("   Make sure to add Python to your PATH during installation.")
        return False
    
    # Create virtual environment using the detected Python
    print(f"\n🔄 Creating virtual environment with {python_executable}...")
    if not run_command(f'"{python_executable}" -m venv venv', "Creating virtual environment"):
        return False
    
    # Activate virtual environment and install dependencies
    print("\n📦 Installing project dependencies...")
    if not run_command(f'venv\\Scripts\\activate && python -m pip install -e .', "Installing project in development mode"):
        return False
    
    # Install development dependencies
    print("\n🛠️  Installing development dependencies...")
    if not run_command(f'venv\\Scripts\\activate && python -m pip install -e .[dev]', "Installing development dependencies"):
        print("⚠️  Development dependencies installation failed, but core dependencies should be installed")
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Activate virtual environment: venv\\Scripts\\activate")
    print("2. Run the application: python src/app.py")
    print("3. Or use the command: wikirace")
    print("\n💡 Tips:")
    print("- Make sure you have PyQt6 installed properly")
    print("- If you encounter issues, try: pip install --upgrade PyQt6 PyQt6-WebEngine")
    
    return True

if __name__ == "__main__":
    print("🎮 WikiRace Python 3.13 Setup")
    print("=" * 40)
    
    if setup_environment():
        print("\n✅ All done! Your WikiRace project is ready to run with Python 3.13")
    else:
        print("\n❌ Setup failed. Please check the error messages above.")
        sys.exit(1)
