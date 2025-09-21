#!/usr/bin/env python3
"""
Test script for WikiRace Multiplayer Server

Tests basic server functionality without requiring Redis.
"""

import asyncio
import sys
import logging
from pathlib import Path

# Add server directory to Python path
server_dir = Path(__file__).parent
sys.path.insert(0, str(server_dir))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_room_manager():
    """Test basic room manager functionality"""
    try:
        from room_manager import RoomManager
        
        logger.info("Testing Room Manager...")
        
        # Create room manager
        rm = RoomManager()
        
        # Test room creation
        room = await rm.create_room("test_socket_1", "TestPlayer1")
        logger.info(f"✓ Created room: {room.room_code}")
        
        # Test room retrieval
        retrieved_room = rm.get_room(room.room_code)
        assert retrieved_room is not None
        logger.info(f"✓ Retrieved room: {retrieved_room.room_code}")
        
        # Test player joining
        join_room = rm.join_room(room.room_code, "test_socket_2", "TestPlayer2")
        assert join_room is not None
        logger.info(f"✓ Player joined room: {join_room.player_count} players")
        
        # Test room stats
        stats = rm.get_room_stats()
        logger.info(f"✓ Room stats: {stats}")
        
        logger.info("✓ All room manager tests passed!")
        return True
        
    except Exception as e:
        logger.error(f"✗ Room manager test failed: {e}")
        return False

async def test_models():
    """Test data model validation"""
    try:
        from models import Player, GameRoom, GameState
        
        logger.info("Testing Data Models...")
        
        # Test Player model
        player = Player(
            socket_id="test_socket",
            display_name="TestPlayer",
            is_host=True
        )
        logger.info(f"✓ Created player: {player.display_name}")
        
        # Test GameRoom model
        room = GameRoom(
            room_code="TEST",
            host_id="test_socket",
            players={"test_socket": player}
        )
        logger.info(f"✓ Created room: {room.room_code}")
        
        # Test validation
        try:
            invalid_room = GameRoom(
                room_code="invalid",  # Should fail validation
                host_id="test_socket"
            )
            logger.error("✗ Validation should have failed for invalid room code")
            return False
        except Exception:
            logger.info("✓ Validation correctly rejected invalid room code")
        
        logger.info("✓ All model tests passed!")
        return True
        
    except Exception as e:
        logger.error(f"✗ Model test failed: {e}")
        return False

async def test_config():
    """Test configuration loading"""
    try:
        from config import settings
        
        logger.info("Testing Configuration...")
        
        logger.info(f"✓ Host: {settings.HOST}")
        logger.info(f"✓ Port: {settings.PORT}")
        logger.info(f"✓ Max players per room: {settings.MAX_PLAYERS_PER_ROOM}")
        logger.info(f"✓ Room code length: {settings.ROOM_CODE_LENGTH}")
        
        logger.info("✓ All config tests passed!")
        return True
        
    except Exception as e:
        logger.error(f"✗ Config test failed: {e}")
        return False

async def main():
    """Run all tests"""
    logger.info("Starting WikiRace Server Tests...")
    
    tests = [
        test_config,
        test_models,
        test_room_manager,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if await test():
            passed += 1
        logger.info("")  # Empty line between tests
    
    logger.info(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("✓ All tests passed! Server foundation is ready.")
        return True
    else:
        logger.error("✗ Some tests failed. Check the logs above.")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
