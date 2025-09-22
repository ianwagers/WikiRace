#!/usr/bin/env python3
"""
Test script to verify the multiplayer tab opens and functions correctly
"""

import sys
import time
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtWebEngineWidgets import QWebEngineView

# Set Qt attributes before creating QApplication
QApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts, True)

def test_multiplayer_tab():
    """Test that the multiplayer tab opens and functions correctly"""
    
    print("🧪 Testing Multiplayer Tab Integration")
    print("=" * 50)
    
    # Create application
    app = QApplication(sys.argv)
    
    # Import and create main application
    from src.app import MainApplication
    main_app = MainApplication()
    
    print("1. Testing multiplayer tab creation...")
    
    # Test adding multiplayer tab
    try:
        main_app.addMultiplayerTab()
        tab_count = main_app.tabWidget.count()
        print(f"   ✅ Multiplayer tab added successfully")
        print(f"   📊 Total tabs: {tab_count}")
        
        # Check if multiplayer page exists
        if hasattr(main_app, 'multiplayerPage'):
            print("   ✅ MultiplayerPage instance created")
            
            # Check if network manager exists
            if hasattr(main_app.multiplayerPage, 'network_manager'):
                print("   ✅ NetworkManager initialized")
            else:
                print("   ❌ NetworkManager not found")
                return False
        else:
            print("   ❌ MultiplayerPage instance not created")
            return False
            
    except Exception as e:
        print(f"   ❌ Error creating multiplayer tab: {e}")
        return False
    
    print("\n2. Testing server connection...")
    
    # Test server connection
    try:
        status = main_app.multiplayerPage.network_manager.get_server_status()
        if "error" in status:
            print(f"   ⚠️ Server connection test: {status['error']}")
            print("   💡 Make sure the server is running with:")
            print("      python -m uvicorn server.main:socket_app --host 127.0.0.1 --port 8000")
        else:
            print("   ✅ Server connection successful")
            print(f"   📊 Server status: {status.get('status', 'unknown')}")
    except Exception as e:
        print(f"   ❌ Server connection test failed: {e}")
    
    print("\n3. Testing UI components...")
    
    # Test UI components
    try:
        ui_components = [
            ('titleLabel', 'Title Label'),
            ('statusLabel', 'Status Label'),
            ('playerNameInput', 'Player Name Input'),
            ('hostGameButton', 'Host Game Button'),
            ('joinGameButton', 'Join Game Button'),
            ('roomCodeInput', 'Room Code Input'),
        ]
        
        for attr, name in ui_components:
            if hasattr(main_app.multiplayerPage, attr):
                print(f"   ✅ {name} found")
            else:
                print(f"   ❌ {name} not found")
                return False
                
    except Exception as e:
        print(f"   ❌ UI component test failed: {e}")
        return False
    
    print("\n🎉 Multiplayer Tab Test Results:")
    print("   ✅ Multiplayer tab creates successfully")
    print("   ✅ NetworkManager initializes correctly")
    print("   ✅ All UI components are present")
    print("\n📋 Next Steps:")
    print("   1. Start the server: python -m uvicorn server.main:socket_app --host 127.0.0.1 --port 8000")
    print("   2. Start the GUI: python -m src.app")
    print("   3. Click the 'Multiplayer' button on the Home page")
    print("   4. Test creating and joining rooms!")
    
    # Don't actually show the window in automated test
    # main_app.show()
    
    return True

if __name__ == "__main__":
    success = test_multiplayer_tab()
    sys.exit(0 if success else 1)
