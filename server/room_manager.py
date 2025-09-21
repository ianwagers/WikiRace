"""
Room management for WikiRace Multiplayer Server

Handles creation, storage, and lifecycle of game rooms.
"""

import random
import string
from datetime import datetime, timedelta
from typing import Dict, Optional, List
import logging

try:
    from .models import GameRoom, Player, GameState
    from .config import settings
    from .redis_manager import redis_manager
except ImportError:
    from models import GameRoom, Player, GameState
    from config import settings
    from redis_manager import redis_manager

logger = logging.getLogger(__name__)


class RoomManager:
    """Manages game rooms and their lifecycle"""
    
    def __init__(self):
        self.rooms: Dict[str, GameRoom] = {}
        self.player_to_room: Dict[str, str] = {}  # socket_id -> room_code mapping
        self.use_redis = False  # Will be set to True when Redis is available
    
    async def initialize_redis(self) -> bool:
        """Initialize Redis connection and enable Redis storage"""
        try:
            success = await redis_manager.connect()
            if success:
                self.use_redis = True
                logger.info("Redis integration enabled")
            else:
                logger.warning("Redis connection failed, using in-memory storage only")
            return success
        except Exception as e:
            logger.error(f"Redis initialization error: {e}")
            return False
    
    def generate_room_code(self) -> str:
        """Generate a unique 4-letter room code"""
        max_attempts = 100
        for _ in range(max_attempts):
            code = ''.join(random.choices(string.ascii_uppercase, k=settings.ROOM_CODE_LENGTH))
            if code not in self.rooms:
                return code
        
        raise RuntimeError("Unable to generate unique room code after maximum attempts")
    
    async def _sync_room_to_redis(self, room: GameRoom) -> bool:
        """Sync room data to Redis if available"""
        if not self.use_redis:
            return True
        
        try:
            # Convert room to dict for Redis storage
            room_data = room.model_dump()
            return await redis_manager.store_room(room.room_code, room_data)
        except Exception as e:
            logger.error(f"Failed to sync room {room.room_code} to Redis: {e}")
            return False
    
    async def _load_room_from_redis(self, room_code: str) -> Optional[GameRoom]:
        """Load room data from Redis if available"""
        if not self.use_redis:
            return None
        
        try:
            room_data = await redis_manager.get_room(room_code)
            if room_data:
                # Convert dict back to GameRoom model
                room = GameRoom(**room_data)
                return room
        except Exception as e:
            logger.error(f"Failed to load room {room_code} from Redis: {e}")
        
        return None
    
    async def create_room(self, host_socket_id: str, host_display_name: str) -> GameRoom:
        """Create a new game room"""
        room_code = self.generate_room_code()
        
        # Create host player
        host_player = Player(
            socket_id=host_socket_id,
            display_name=host_display_name,
            is_host=True
        )
        
        # Create room
        room = GameRoom(
            room_code=room_code,
            host_id=host_socket_id,
            players={host_socket_id: host_player}
        )
        
        # Store room and player mapping
        self.rooms[room_code] = room
        self.player_to_room[host_socket_id] = room_code
        
        # Sync to Redis if available
        await self._sync_room_to_redis(room)
        
        logger.info(f"Created room {room_code} with host {host_display_name}")
        return room
    
    def join_room(self, room_code: str, player_socket_id: str, display_name: str) -> Optional[GameRoom]:
        """Join an existing room"""
        room = self.get_room(room_code)
        if not room:
            return None
        
        if room.is_full:
            logger.warning(f"Room {room_code} is full, cannot join")
            return None
        
        if room.game_state != GameState.LOBBY:
            logger.warning(f"Room {room_code} is not in lobby state, cannot join")
            return None
        
        # Create player
        player = Player(
            socket_id=player_socket_id,
            display_name=display_name,
            is_host=False
        )
        
        # Add player to room
        if room.add_player(player):
            self.player_to_room[player_socket_id] = room_code
            logger.info(f"Player {display_name} joined room {room_code}")
            return room
        
        return None
    
    def leave_room(self, socket_id: str) -> Optional[GameRoom]:
        """Remove a player from their room"""
        room_code = self.player_to_room.get(socket_id)
        if not room_code:
            return None
        
        room = self.get_room(room_code)
        if not room:
            return None
        
        # Get player before removal
        player = room.get_player(socket_id)
        if not player:
            return None
        
        # Remove player
        room.remove_player(socket_id)
        del self.player_to_room[socket_id]
        
        logger.info(f"Player {player.display_name} left room {room_code}")
        
        # Handle host leaving
        if room.is_host(socket_id):
            new_host_id = room.transfer_host()
            if new_host_id:
                logger.info(f"Transferred host to {room.players[new_host_id].display_name} in room {room_code}")
            else:
                # No other players, close room
                self.close_room(room_code)
                logger.info(f"Closed empty room {room_code}")
                return None
        
        # Close room if empty
        if room.player_count == 0:
            self.close_room(room_code)
            logger.info(f"Closed empty room {room_code}")
            return None
        
        return room
    
    def get_room(self, room_code: str) -> Optional[GameRoom]:
        """Get a room by code"""
        return self.rooms.get(room_code)
    
    def get_room_by_player(self, socket_id: str) -> Optional[GameRoom]:
        """Get room that contains a specific player"""
        room_code = self.player_to_room.get(socket_id)
        if room_code:
            return self.get_room(room_code)
        return None
    
    def get_player(self, socket_id: str) -> Optional[Player]:
        """Get a player by socket ID"""
        room = self.get_room_by_player(socket_id)
        if room:
            return room.get_player(socket_id)
        return None
    
    def close_room(self, room_code: str) -> bool:
        """Close and remove a room"""
        if room_code not in self.rooms:
            return False
        
        room = self.rooms[room_code]
        
        # Remove all player mappings
        for socket_id in list(room.players.keys()):
            self.player_to_room.pop(socket_id, None)
        
        # Remove room
        del self.rooms[room_code]
        
        logger.info(f"Closed room {room_code}")
        return True
    
    def cleanup_expired_rooms(self) -> int:
        """Remove expired rooms and return count of cleaned rooms"""
        expired_time = datetime.utcnow() - timedelta(hours=settings.ROOM_EXPIRY_HOURS)
        expired_rooms = []
        
        for room_code, room in self.rooms.items():
            if room.created_at < expired_time:
                expired_rooms.append(room_code)
        
        for room_code in expired_rooms:
            self.close_room(room_code)
        
        if expired_rooms:
            logger.info(f"Cleaned up {len(expired_rooms)} expired rooms")
        
        return len(expired_rooms)
    
    def get_room_stats(self) -> Dict[str, any]:
        """Get statistics about current rooms"""
        total_players = sum(len(room.players) for room in self.rooms.values())
        
        state_counts = {}
        for state in GameState:
            state_counts[state.value] = sum(
                1 for room in self.rooms.values() 
                if room.game_state == state
            )
        
        return {
            "total_rooms": len(self.rooms),
            "total_players": total_players,
            "state_distribution": state_counts,
            "average_players_per_room": total_players / len(self.rooms) if self.rooms else 0
        }
    
    def update_player_activity(self, socket_id: str) -> bool:
        """Update player's last activity timestamp"""
        player = self.get_player(socket_id)
        if player:
            player.last_activity = datetime.utcnow()
            return True
        return False
    
    def get_active_players(self, hours: int = 1) -> List[str]:
        """Get list of socket IDs for players active within specified hours"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        active_players = []
        
        for room in self.rooms.values():
            for socket_id, player in room.players.items():
                if player.last_activity > cutoff_time:
                    active_players.append(socket_id)
        
        return active_players
