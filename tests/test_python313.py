#!/usr/bin/env python3
"""
Test script to verify Python 3.13 setup
"""

import sys
import subprocess
from pathlib import Path

def test_local_python313():
    """Test if local Python 3.13 is available and working."""
    print("🔍 Testing local Python 3.13 setup...")
    
    # Check if Python313 directory exists
    python313_dir = Path(__file__).parent / "Python313"
    python_exe = python313_dir / "python.exe"
    
    if not python313_dir.exists():
        print(f"❌ Python313 directory not found at: {python313_dir}")
        return False
    
    if not python_exe.exists():
        print(f"❌ Python executable not found at: {python_exe}")
        return False
    
    print(f"✅ Found Python313 directory: {python313_dir}")
    print(f"✅ Found Python executable: {python_exe}")
    
    # Test Python version
    try:
        result = subprocess.run([str(python_exe), "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"✅ Python version: {version}")
            
            if "3.13" in version:
                print("🎉 Python 3.13 is working correctly!")
                return True
            else:
                print(f"⚠️  Expected Python 3.13, but got: {version}")
                return False
        else:
            print(f"❌ Python executable failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error running Python: {e}")
        return False

def test_virtual_environment():
    """Test if virtual environment can be created with local Python."""
    print("\n🔍 Testing virtual environment creation...")
    
    python313_dir = Path(__file__).parent / "Python313"
    python_exe = python313_dir / "python.exe"
    venv_dir = Path(__file__).parent / "venv"
    
    # Remove existing venv if it exists
    if venv_dir.exists():
        import shutil
        shutil.rmtree(venv_dir)
        print("🗑️  Removed existing virtual environment")
    
    try:
        # Create virtual environment
        result = subprocess.run([
            str(python_exe), "-m", "venv", "venv"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Virtual environment created successfully")
            
            # Test activation
            activate_script = venv_dir / "Scripts" / "activate.bat"
            if activate_script.exists():
                print("✅ Virtual environment activation script found")
                return True
            else:
                print("❌ Virtual environment activation script not found")
                return False
        else:
            print(f"❌ Failed to create virtual environment: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error creating virtual environment: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Python 3.13 Setup Test")
    print("=" * 40)
    
    # Test local Python 3.13
    python_ok = test_local_python313()
    
    # Test virtual environment creation
    venv_ok = test_virtual_environment()
    
    print("\n" + "=" * 40)
    print("📊 Test Results:")
    print(f"Local Python 3.13: {'✅' if python_ok else '❌'}")
    print(f"Virtual Environment: {'✅' if venv_ok else '❌'}")
    
    if python_ok and venv_ok:
        print("\n🎉 All tests passed! Your Python 3.13 setup is ready.")
        print("\n🚀 You can now run:")
        print("   setup.bat")
        print("   or")
        print("   python setup_environment.py")
        return True
    else:
        print("\n❌ Some tests failed. Please check your Python313 installation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
