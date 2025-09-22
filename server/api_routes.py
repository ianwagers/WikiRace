"""
REST API routes for WikiRace Multiplayer Server

Provides HTTP endpoints for room management and server information.
"""

from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any

try:
    from .models import (
        RoomCreateRequest, 
        RoomJoinRequest, 
        GameRoom, 
        Player
    )
    from .room_manager import RoomManager
except ImportError:
    from models import (
        RoomCreateRequest, 
        RoomJoinRequest, 
        GameRoom, 
        Player
    )
    from room_manager import RoomManager

# Create API router
router = APIRouter(prefix="/api", tags=["rooms"])

# Room manager instance (will be injected)
room_manager: RoomManager = None

def set_room_manager(manager: RoomManager):
    """Set the room manager instance for the API routes"""
    global room_manager
    room_manager = manager


@router.post("/rooms", response_model=Dict[str, Any])
async def create_room(request: RoomCreateRequest) -> Dict[str, Any]:
    """Create a new game room"""
    if not room_manager:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Room manager not available"
        )
    
    try:
        # For REST API, we need a temporary socket ID
        # In real usage, this would be called from Socket.IO handlers
        import time
        import random
        timestamp = int(time.time() * 1000)  # milliseconds
        random_suffix = random.randint(1000, 9999)
        temp_socket_id = f"rest_{request.display_name}_{timestamp}_{random_suffix}"
        
        room = await room_manager.create_room(temp_socket_id, request.display_name)
        
        return {
            "success": True,
            "room_code": room.room_code,
            "message": f"Room {room.room_code} created successfully",
            "host_name": request.display_name,
            "player_count": room.player_count
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create room: {str(e)}"
        )

@router.get("/rooms/{room_code}", response_model=Dict[str, Any])
async def get_room(room_code: str) -> Dict[str, Any]:
    """Get information about a specific room"""
    if not room_manager:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Room manager not available"
        )
    
    # Validate room code format
    if len(room_code) != 4 or not room_code.isalpha():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid room code format"
        )
    
    room_code = room_code.upper()
    room = room_manager.get_room(room_code)
    
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Room {room_code} not found"
        )
    
    return {
        "success": True,
        "room_code": room.room_code,
        "game_state": room.game_state.value,
        "player_count": room.player_count,
        "max_players": 10,
        "is_full": room.is_full,
        "host_name": room.players[room.host_id].display_name,
        "players": [
            {
                "display_name": player.display_name,
                "is_host": player.is_host,
                "joined_at": player.joined_at.isoformat()
            }
            for player in room.players.values()
        ],
        "created_at": room.created_at.isoformat(),
        "game_started_at": room.game_started_at.isoformat() if room.game_started_at else None
    }

@router.post("/rooms/{room_code}/join", response_model=Dict[str, Any])
async def join_room(room_code: str, request: RoomJoinRequest) -> Dict[str, Any]:
    """Join an existing room"""
    if not room_manager:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Room manager not available"
        )
    
    # Validate room code format
    if len(room_code) != 4 or not room_code.isalpha():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid room code format"
        )
    
    room_code = room_code.upper()
    
    try:
        # For REST API, we need a temporary socket ID
        import time
        import random
        timestamp = int(time.time() * 1000)  # milliseconds
        random_suffix = random.randint(1000, 9999)
        temp_socket_id = f"rest_{request.display_name}_{timestamp}_{random_suffix}"
        
        room = room_manager.join_room(room_code, temp_socket_id, request.display_name)
        
        if not room:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Room not found, full, or not accepting new players"
            )
        
        return {
            "success": True,
            "room_code": room.room_code,
            "message": f"Successfully joined room {room.room_code}",
            "player_name": request.display_name,
            "player_count": room.player_count,
            "is_host": False
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to join room: {str(e)}"
        )

@router.delete("/rooms/{room_code}/leave", response_model=Dict[str, Any])
async def leave_room(room_code: str, socket_id: str) -> Dict[str, Any]:
    """Leave a room (for testing purposes)"""
    if not room_manager:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Room manager not available"
        )
    
    # Validate room code format
    if len(room_code) != 4 or not room_code.isalpha():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid room code format"
        )
    
    room_code = room_code.upper()
    
    try:
        room = room_manager.leave_room(socket_id)
        
        if not room:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Player not found in any room"
            )
        
        return {
            "success": True,
            "message": f"Successfully left room {room_code}",
            "remaining_players": room.player_count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to leave room: {str(e)}"
        )

@router.get("/rooms", response_model=Dict[str, Any])
async def list_rooms() -> Dict[str, Any]:
    """Get list of all active rooms"""
    if not room_manager:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Room manager not available"
        )
    
    try:
        stats = room_manager.get_room_stats()
        
        # Get basic info about each room (without exposing sensitive data)
        rooms_info = []
        for room_code, room in room_manager.rooms.items():
            rooms_info.append({
                "room_code": room.room_code,
                "game_state": room.game_state.value,
                "player_count": room.player_count,
                "is_full": room.is_full,
                "created_at": room.created_at.isoformat()
            })
        
        return {
            "success": True,
            "total_rooms": stats["total_rooms"],
            "total_players": stats["total_players"],
            "rooms": rooms_info
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list rooms: {str(e)}"
        )

@router.get("/stats", response_model=Dict[str, Any])
async def get_server_stats() -> Dict[str, Any]:
    """Get server statistics"""
    if not room_manager:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Room manager not available"
        )
    
    try:
        room_stats = room_manager.get_room_stats()
        
        # Get Redis stats if available
        redis_stats = {}
        if room_manager.use_redis:
            try:
                from .redis_manager import redis_manager
            except ImportError:
                from redis_manager import redis_manager
            redis_stats = await redis_manager.get_redis_stats()
        
        return {
            "success": True,
            "room_stats": room_stats,
            "redis_stats": redis_stats,
            "redis_enabled": room_manager.use_redis
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get server stats: {str(e)}"
        )
