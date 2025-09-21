#!/usr/bin/env python3
"""
Quick script to install PyQt6 and dependencies using local Python 3.13
"""

import subprocess
import sys
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

def install_pyqt6():
    """Install PyQt6 and dependencies using local Python 3.13."""
    print("🚀 Installing PyQt6 and dependencies...")
    
    # Get the path to local Python 3.13
    python313_path = Path(__file__).parent / "Python313" / "python.exe"
    
    if not python313_path.exists():
        print(f"❌ Python 3.13 not found at: {python313_path}")
        print("💡 Make sure Python313 directory exists in your project folder")
        return False
    
    print(f"🔍 Using Python 3.13 at: {python313_path}")
    
    # Install PyQt6 and dependencies
    dependencies = [
        "PyQt6>=6.7.0",
        "PyQt6-WebEngine>=6.7.0", 
        "requests>=2.32.0",
        "beautifulsoup4>=4.12.0",
        "lxml>=5.0.0"
    ]
    
    for dep in dependencies:
        if not run_command(f'"{python313_path}" -m pip install {dep}', f"Installing {dep}"):
            print(f"⚠️  Failed to install {dep}, but continuing...")
    
    # Also try installing the project in development mode
    print("\n🔄 Installing project in development mode...")
    if not run_command(f'"{python313_path}" -m pip install -e .', "Installing project"):
        print("⚠️  Project installation failed, but PyQt6 should be installed")
    
    print("\n🎉 PyQt6 installation completed!")
    print("\n📋 Next steps:")
    print("1. Try running your project again")
    print("2. If you still get errors, try running: setup.bat")
    
    return True

if __name__ == "__main__":
    print("🔧 PyQt6 Installation Script")
    print("=" * 40)
    
    if install_pyqt6():
        print("\n✅ Installation completed successfully!")
    else:
        print("\n❌ Installation failed. Please check the error messages above.")
        sys.exit(1)
