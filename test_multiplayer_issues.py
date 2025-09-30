#!/usr/bin/env python3
"""
Test suite to validate the issues documented in MULTIPLAYER_ISSUES.md

This script tests the identified client/server logic issues.
"""

import sys
import os
from pathlib import Path

# Add paths to import the modules
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))
sys.path.insert(0, str(project_root / "server"))

def test_port_mismatch():
    """Test Issue #1: Port mismatch between client and server"""
    print("\n" + "="*60)
    print("TEST: Port Mismatch (Issue #1)")
    print("="*60)
    
    try:
        # Read server config without importing
        server_config_file = Path(__file__).parent / "server" / "config.py"
        with open(server_config_file, 'r') as f:
            server_source = f.read()
        
        # Extract server port
        import re
        server_match = re.search(r'PORT:\s*int\s*=\s*(\d+)', server_source)
        server_port = int(server_match.group(1)) if server_match else None
        
        # Read client network file
        network_file = Path(__file__).parent / "src" / "logic" / "Network.py"
        with open(network_file, 'r') as f:
            network_source = f.read()
        
        # Extract client default port
        client_match = re.search(r'server_url:\s*str\s*=\s*"http://[^:]+:(\d+)"', network_source)
        client_port = int(client_match.group(1)) if client_match else None
        
        print(f"Server configured port: {server_port}")
        print(f"Client default port: {client_port}")
        
        if server_port and client_port and server_port != client_port:
            print("❌ FAILED: Port mismatch detected!")
            print(f"   Server expects connections on port {server_port}")
            print(f"   Client defaults to connecting to port {client_port}")
            return False
        else:
            print("✅ PASSED: Ports match")
            return True
            
    except Exception as e:
        print(f"❌ TEST ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_duplicate_methods():
    """Test Issue #3: Duplicate progress update methods"""
    print("\n" + "="*60)
    print("TEST: Duplicate Methods (Issue #3)")
    print("="*60)
    
    try:
        # Read Network.py without importing
        network_file = Path(__file__).parent / "src" / "logic" / "Network.py"
        with open(network_file, 'r') as f:
            source = f.read()
        
        # Check for duplicate progress methods
        has_send_player_progress = 'def send_player_progress(' in source
        has_send_player_progress_update = 'def send_player_progress_update(' in source
        
        print(f"Has send_player_progress: {has_send_player_progress}")
        print(f"Has send_player_progress_update: {has_send_player_progress_update}")
        
        # Check for duplicate completion methods
        has_send_game_completion = 'def send_game_completion(' in source
        has_send_player_completion_update = 'def send_player_completion_update(' in source
        
        print(f"Has send_game_completion: {has_send_game_completion}")
        print(f"Has send_player_completion_update: {has_send_player_completion_update}")
        
        if has_send_player_progress and has_send_player_progress_update:
            print("❌ FAILED: Duplicate progress methods detected!")
            return False
        
        if has_send_game_completion and has_send_player_completion_update:
            print("❌ FAILED: Duplicate completion methods detected!")
            return False
            
        print("✅ PASSED: No duplicate methods found")
        return True
        
    except Exception as e:
        print(f"❌ TEST ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_blocking_sleep_calls():
    """Test Issue #5 and #19: Blocking time.sleep() calls in client code"""
    print("\n" + "="*60)
    print("TEST: Blocking Sleep Calls (Issues #5, #19)")
    print("="*60)
    
    try:
        # Get the source code of Network.py
        network_file = Path(__file__).parent / "src" / "logic" / "Network.py"
        with open(network_file, 'r') as f:
            source = f.read()
        
        # Count time.sleep calls
        sleep_count = source.count('time.sleep(')
        
        print(f"Found {sleep_count} time.sleep() calls in Network.py")
        
        if sleep_count > 0:
            print("❌ FAILED: Blocking time.sleep() calls found!")
            print("   These will freeze the UI thread.")
            # Find line numbers
            for i, line in enumerate(source.split('\n'), 1):
                if 'time.sleep(' in line:
                    print(f"   Line {i}: {line.strip()}")
            return False
        else:
            print("✅ PASSED: No blocking sleep calls found")
            return True
            
    except Exception as e:
        print(f"❌ TEST ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_rejoin_logic():
    """Test Issue #7: Rejoin during active game is impossible"""
    print("\n" + "="*60)
    print("TEST: Rejoin Logic (Issue #7)")
    print("="*60)
    
    try:
        # Read room_manager without importing
        room_manager_file = Path(__file__).parent / "server" / "room_manager.py"
        with open(room_manager_file, 'r') as f:
            source = f.read()
        
        # Check if IN_PROGRESS is in the allowed states for join_room
        has_in_progress_check = 'GameState.IN_PROGRESS' in source
        
        print(f"room_manager.py mentions IN_PROGRESS: {has_in_progress_check}")
        
        # Check the actual condition in join_room
        if 'not in [GameState.LOBBY, GameState.COMPLETED]' in source:
            print("❌ FAILED: join_room only allows LOBBY and COMPLETED states!")
            print("   Players cannot rejoin during IN_PROGRESS games.")
            print("   But leave_room marks them for rejoin during IN_PROGRESS.")
            return False
        elif '[GameState.LOBBY, GameState.COMPLETED, GameState.IN_PROGRESS]' in source:
            print("✅ PASSED: Rejoin logic appears to handle IN_PROGRESS")
            return True
        else:
            print("⚠️  INCONCLUSIVE: Unable to determine rejoin logic from source")
            return None
            
    except Exception as e:
        print(f"❌ TEST ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_connection_health_check():
    """Test Issue #4: Connection health check during reconnection"""
    print("\n" + "="*60)
    print("TEST: Connection Health Check (Issue #4)")
    print("="*60)
    
    try:
        # Read Network.py without importing
        network_file = Path(__file__).parent / "src" / "logic" / "Network.py"
        with open(network_file, 'r') as f:
            source = f.read()
        
        # Check if it blocks during reconnection
        if 'current_reconnection_attempts > 0' in source and 'return False' in source:
            print("❌ FAILED: Health check returns False during any reconnection!")
            print("   This prevents operations when connection might be restored.")
            return False
        else:
            print("✅ PASSED: Health check doesn't block on reconnection attempts")
            return True
            
    except Exception as e:
        print(f"❌ TEST ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_cleanup_sets_sio_to_none():
    """Test Issue #20: cleanup_network_resources sets sio to None"""
    print("\n" + "="*60)
    print("TEST: Cleanup Sets sio to None (Issue #20)")
    print("="*60)
    
    try:
        # Read Network.py without importing
        network_file = Path(__file__).parent / "src" / "logic" / "Network.py"
        with open(network_file, 'r') as f:
            source = f.read()
        
        # Check if cleanup sets sio to None
        sets_sio_none = 'self.sio = None' in source
        
        # Check if heartbeat checks for None before accessing
        # Look for the send_heartbeat method specifically
        import re
        heartbeat_match = re.search(r'def send_heartbeat\(self\):.*?(?=\n    def |\nclass |\Z)', source, re.DOTALL)
        if heartbeat_match:
            heartbeat_source = heartbeat_match.group(0)
            checks_sio_none = 'self.sio is not None' in heartbeat_source or 'if self.sio and' in heartbeat_source
        else:
            checks_sio_none = False
        
        print(f"cleanup_network_resources sets sio to None: {sets_sio_none}")
        print(f"send_heartbeat checks for None: {checks_sio_none}")
        
        if sets_sio_none and not checks_sio_none:
            print("❌ FAILED: cleanup sets sio=None but other methods don't check!")
            print("   This will cause AttributeError: 'NoneType' object has no attribute 'connected'")
            return False
        else:
            print("✅ PASSED: Either sio is not set to None or checks are in place")
            return True
            
    except Exception as e:
        print(f"❌ TEST ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("MULTIPLAYER CLIENT/SERVER LOGIC ISSUE VALIDATION")
    print("="*70)
    
    tests = [
        ("Port Mismatch", test_port_mismatch),
        ("Duplicate Methods", test_duplicate_methods),
        ("Blocking Sleep Calls", test_blocking_sleep_calls),
        ("Rejoin Logic", test_rejoin_logic),
        ("Connection Health Check", test_connection_health_check),
        ("Cleanup Sets sio to None", test_cleanup_sets_sio_to_none),
    ]
    
    results = {}
    for name, test_func in tests:
        try:
            result = test_func()
            results[name] = result
        except Exception as e:
            print(f"\n❌ FATAL ERROR in {name}: {e}")
            import traceback
            traceback.print_exc()
            results[name] = False
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for r in results.values() if r is True)
    failed = sum(1 for r in results.values() if r is False)
    inconclusive = sum(1 for r in results.values() if r is None)
    
    for name, result in results.items():
        if result is True:
            status = "✅ PASSED"
        elif result is False:
            status = "❌ FAILED"
        else:
            status = "⚠️  INCONCLUSIVE"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {len(results)} tests")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Inconclusive: {inconclusive}")
    
    if failed > 0:
        print("\n⚠️  VALIDATION FAILED: Issues confirmed in code!")
        print("See MULTIPLAYER_ISSUES.md for detailed documentation.")
        return 1
    else:
        print("\n✅ All tests passed or inconclusive")
        return 0

if __name__ == "__main__":
    sys.exit(main())
