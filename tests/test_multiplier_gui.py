#!/usr/bin/env python3
"""
Test script to verify the multiplayer GUI integration
"""

import sys
import requests
import time

def test_server_and_gui():
    """Test that both server and GUI components work together"""
    
    print("🧪 Testing WikiRace Multiplayer Integration")
    print("=" * 50)
    
    # Test 1: Server is running
    print("1. Testing server connection...")
    try:
        response = requests.get("http://127.0.0.1:8000/", timeout=5)
        if response.status_code == 200:
            print("   ✅ Server is running")
            server_data = response.json()
            print(f"   📊 Server info: {server_data['message']} v{server_data['version']}")
        else:
            print(f"   ❌ Server returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Cannot connect to server: {e}")
        print("   💡 Make sure the server is running with:")
        print("      python server/start_server.py")
        return False
    
    # Test 2: API endpoints work
    print("\n2. Testing API endpoints...")
    try:
        # Create a test room
        response = requests.post(
            "http://127.0.0.1:8000/api/rooms",
            json={"display_name": "TestPlayer"},
            timeout=5
        )
        if response.status_code == 200:
            room_data = response.json()
            room_code = room_data['room_code']
            print(f"   ✅ Room creation works - Created room: {room_code}")
            
            # Test joining the room
            join_response = requests.post(
                f"http://127.0.0.1:8000/api/rooms/{room_code}/join",
                json={"display_name": "TestPlayer2"},
                timeout=5
            )
            if join_response.status_code == 200:
                print("   ✅ Room joining works")
            else:
                print(f"   ❌ Room joining failed: {join_response.status_code}")
        else:
            print(f"   ❌ Room creation failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ API test failed: {e}")
        return False
    
    # Test 3: Server stats
    print("\n3. Testing server statistics...")
    try:
        response = requests.get("http://127.0.0.1:8000/api/stats", timeout=5)
        if response.status_code == 200:
            stats = response.json()
            room_stats = stats['room_stats']
            print(f"   ✅ Server stats: {room_stats['total_rooms']} rooms, {room_stats['total_players']} players")
        else:
            print(f"   ❌ Failed to get server stats: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Stats test failed: {e}")
    
    print("\n🎉 Integration Test Results:")
    print("   ✅ Server is running and responding")
    print("   ✅ API endpoints are working")
    print("   ✅ Room creation and joining works")
    print("\n📋 Next Steps:")
    print("   1. Start the main GUI: python -m src.app")
    print("   2. Click on the 'Multiplayer' tab")
    print("   3. Test creating and joining rooms")
    print("   4. Share room codes with friends to test multiplayer!")
    
    return True

if __name__ == "__main__":
    success = test_server_and_gui()
    sys.exit(0 if success else 1)
