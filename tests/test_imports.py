#!/usr/bin/env python3
"""
Test script to verify all PyQt6 imports are working correctly
"""

import sys
from pathlib import Path

def test_import(module_name, display_name):
    """Test if a module can be imported."""
    try:
        __import__(module_name)
        print(f"✅ {display_name}")
        return True
    except ImportError as e:
        print(f"❌ {display_name}: {e}")
        return False

def test_pyqt6_imports():
    """Test all PyQt6 imports used in the project."""
    print("🔍 Testing PyQt6 imports...")
    
    imports_to_test = [
        ("PyQt6.QtWidgets", "PyQt6 Widgets"),
        ("PyQt6.QtCore", "PyQt6 Core"),
        ("PyQt6.QtGui", "PyQt6 GUI"),
        ("PyQt6.QtWebEngineWidgets", "PyQt6 WebEngine Widgets"),
        ("PyQt6.QtWebEngineCore", "PyQt6 WebEngine Core"),
    ]
    
    all_imports_successful = True
    
    for module_name, display_name in imports_to_test:
        if not test_import(module_name, display_name):
            all_imports_successful = False
    
    return all_imports_successful

def test_project_imports():
    """Test if project modules can be imported."""
    print("\n🎮 Testing project imports...")
    
    project_modules = [
        ("src.logic.GameLogic", "Game Logic"),
        ("src.gui.HomePage", "Home Page"),
        ("src.gui.SoloGamePage", "Solo Game Page"),
        ("src.gui.MultiplayerPage", "Multiplayer Page"),
        ("src.gui.SettingsPage", "Settings Page"),
    ]
    
    all_imports_successful = True
    
    for module_name, display_name in project_modules:
        if not test_import(module_name, display_name):
            all_imports_successful = False
    
    return all_imports_successful

def main():
    """Run all import tests."""
    print("🧪 PyQt6 Import Test")
    print("=" * 40)
    
    # Test PyQt6 imports
    pyqt6_ok = test_pyqt6_imports()
    
    # Test project imports
    project_ok = test_project_imports()
    
    print("\n" + "=" * 40)
    print("📊 Test Results:")
    print(f"PyQt6 Imports: {'✅' if pyqt6_ok else '❌'}")
    print(f"Project Imports: {'✅' if project_ok else '❌'}")
    
    if pyqt6_ok and project_ok:
        print("\n🎉 All imports working correctly!")
        print("\n🚀 You can now run your project from VSCode (F5)")
        return True
    else:
        print("\n❌ Some imports failed. Please check the error messages above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
