#!/usr/bin/env python3
"""
Test script to verify the multiplayer server is working
"""

import requests
import time
import sys

def test_server():
    """Test if the server is running and responding"""
    try:
        print("Testing server connection...")
        
        # Test basic health endpoint
        response = requests.get("http://127.0.0.1:8000/", timeout=5)
        print(f"✅ Server is running! Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # Test API endpoints
        print("\nTesting API endpoints...")
        
        # Test room creation
        create_data = {"display_name": "TestPlayer"}
        response = requests.post("http://127.0.0.1:8000/api/rooms", json=create_data, timeout=5)
        if response.status_code == 200:
            room_data = response.json()
            print(f"✅ Room created: {room_data['room_code']}")
            
            # Test room info
            room_code = room_data['room_code']
            response = requests.get(f"http://127.0.0.1:8000/api/rooms/{room_code}", timeout=5)
            if response.status_code == 200:
                print(f"✅ Room info retrieved for {room_code}")
            else:
                print(f"❌ Failed to get room info: {response.status_code}")
        else:
            print(f"❌ Failed to create room: {response.status_code}")
        
        # Test server stats
        response = requests.get("http://127.0.0.1:8000/api/stats", timeout=5)
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ Server stats: {stats['room_stats']['total_rooms']} rooms, {stats['room_stats']['total_players']} players")
        else:
            print(f"❌ Failed to get server stats: {response.status_code}")
        
        print("\n🎉 All tests passed! Server is working correctly.")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure it's running on http://127.0.0.1:8000")
        return False
    except Exception as e:
        print(f"❌ Error testing server: {e}")
        return False

if __name__ == "__main__":
    success = test_server()
    sys.exit(0 if success else 1)
