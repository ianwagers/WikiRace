"""
Room management for WikiRace Multiplayer Server

Handles creation, storage, and lifecycle of game rooms.
"""

import random
import string
import asyncio
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
        
        # CRITICAL FIX: Add locks for atomic operations
        self._room_locks: Dict[str, asyncio.Lock] = {}  # room_code -> lock
        self._player_locks: Dict[str, asyncio.Lock] = {}  # socket_id -> lock
        self._global_lock = asyncio.Lock()  # Global lock for cross-room operations
    
    async def _get_room_lock(self, room_code: str) -> asyncio.Lock:
        """Get or create a lock for a specific room"""
        if room_code not in self._room_locks:
            async with self._global_lock:
                if room_code not in self._room_locks:
                    self._room_locks[room_code] = asyncio.Lock()
        return self._room_locks[room_code]
    
    async def _get_player_lock(self, socket_id: str) -> asyncio.Lock:
        """Get or create a lock for a specific player"""
        if socket_id not in self._player_locks:
            async with self._global_lock:
                if socket_id not in self._player_locks:
                    self._player_locks[socket_id] = asyncio.Lock()
        return self._player_locks[socket_id]
    
    async def _validate_room_state(self, room: GameRoom, operation: str) -> bool:
        """Validate room state before performing operations"""
        try:
            if not room:
                logger.error(f"Room validation failed for {operation}: room is None")
                return False
            
            if not room.room_code:
                logger.error(f"Room validation failed for {operation}: room_code is empty")
                return False
            
            # Validate room state transitions
            valid_transitions = {
                'join': [GameState.LOBBY, GameState.COMPLETED],
                'leave': [GameState.LOBBY, GameState.IN_PROGRESS, GameState.STARTING, GameState.COMPLETED],
                'start_game': [GameState.LOBBY],
                'end_game': [GameState.IN_PROGRESS, GameState.STARTING]
            }
            
            if operation in valid_transitions:
                if room.game_state not in valid_transitions[operation]:
                    logger.warning(f"Invalid state transition for {operation}: room {room.room_code} is in {room.game_state.value}")
                    return False
            
            # Validate player count
            if room.player_count < 0:
                logger.error(f"Room validation failed for {operation}: negative player count {room.player_count}")
                return False
            
            if room.player_count > settings.MAX_PLAYERS_PER_ROOM:
                logger.error(f"Room validation failed for {operation}: player count {room.player_count} exceeds max {settings.MAX_PLAYERS_PER_ROOM}")
                return False
            
            # Validate host exists if there are players
            if room.player_count > 0 and not room.host_id:
                logger.error(f"Room validation failed for {operation}: room has players but no host")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Room validation error for {operation}: {e}")
            return False
    
    async def _cleanup_locks(self, room_code: str = None, socket_id: str = None):
        """Clean up locks when rooms/players are removed"""
        try:
            async with self._global_lock:
                if room_code and room_code in self._room_locks:
                    del self._room_locks[room_code]
                if socket_id and socket_id in self._player_locks:
                    del self._player_locks[socket_id]
        except Exception as e:
            logger.error(f"Error cleaning up locks: {e}")
    
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
        
        # CRITICAL FIX: Allow joining rooms in LOBBY or COMPLETED state for rejoins
        if room.game_state not in [GameState.LOBBY, GameState.COMPLETED]:
            logger.warning(f"Room {room_code} is in {room.game_state.value} state, cannot join")
            return None
        
        # Check if player name already exists in room
        existing_player = room.get_player_by_name(display_name)
        if existing_player:
            # CRITICAL FIX: Handle rejoin scenario - allow rejoin if same socket ID or if player was disconnected
            if existing_player.socket_id == player_socket_id:
                logger.info(f"Player {display_name} rejoining room {room_code} with same socket ID")
                # Update the player mapping in case it was lost
                self.player_to_room[player_socket_id] = room_code
                return room
            elif existing_player.disconnected:
                # Player was disconnected and is rejoining with a new socket ID
                logger.info(f"Player {display_name} rejoining room {room_code} with new socket ID (was disconnected)")
                # Remove old socket mapping
                self.player_to_room.pop(existing_player.socket_id, None)
                # Update player's socket ID
                existing_player.socket_id = player_socket_id
                existing_player.disconnected = False
                existing_player.last_activity = datetime.utcnow()
                # Add new socket mapping
                self.player_to_room[player_socket_id] = room_code
                return room
            else:
                logger.warning(f"Player name '{display_name}' already exists in room {room_code} and is not disconnected")
                return None
        
        # Create player
        # CRITICAL FIX: If room is empty, make the first player the host
        is_host = room.player_count == 0
        player = Player(
            socket_id=player_socket_id,
            display_name=display_name,
            is_host=is_host
        )
        
        # Add player to room
        if room.add_player(player):
            # If this is the first player in an empty room, set them as host
            if is_host:
                room.host_id = player_socket_id
                logger.info(f"Player {display_name} joined empty room {room_code} and became host")
            else:
                logger.info(f"Player {display_name} joined room {room_code}")
            
            self.player_to_room[player_socket_id] = room_code
            return room
        
        return None
    
    async def leave_room(self, socket_id: str) -> Optional[GameRoom]:
        """Remove a player from their room with atomic operations and state validation"""
        try:
            # Get room code and acquire locks
            room_code = self.player_to_room.get(socket_id)
            if not room_code:
                logger.warning(f"Player {socket_id} not in any room")
                return None
            
            room_lock = await self._get_room_lock(room_code)
            player_lock = await self._get_player_lock(socket_id)
            
            async with room_lock, player_lock:
                # Re-validate room exists (may have changed during lock acquisition)
                room = self.get_room(room_code)
                if not room:
                    logger.warning(f"Room {room_code} no longer exists during leave operation")
                    await self._cleanup_locks(room_code=room_code, socket_id=socket_id)
                    return None
                
                # Validate room state for leave operation
                if not await self._validate_room_state(room, 'leave'):
                    logger.error(f"Room state validation failed for leave operation in room {room_code}")
                    return None
                
                # Get player before removal
                player = room.get_player(socket_id)
                if not player:
                    logger.warning(f"Player {socket_id} not found in room {room_code}")
                    return None
                
                player_name = player.display_name
                was_host = room.is_host(socket_id)
                game_state = room.game_state
                
                logger.info(f"Player {player_name} leaving room {room_code} (host: {was_host}, state: {game_state.value})")
                
                # CRITICAL FIX: Handle host transfer BEFORE removing the player
                if was_host:
                    logger.info(f"LEADERSHIP: Host {player_name} is leaving room {room_code}")
                    logger.info(f"LEADERSHIP: Current players before transfer: {[p.display_name for p in room.players.values()]}")
                    
                    # CRITICAL FIX: Transfer host BEFORE removing the player
                    new_host_id = room.transfer_host()
                    if new_host_id:
                        new_host = room.get_player(new_host_id)
                        if new_host:
                            logger.info(f"LEADERSHIP: Successfully transferred host to {new_host.display_name} in room {room_code}")
                            logger.info(f"LEADERSHIP: New host socket_id: {new_host_id}, is_host: {new_host.is_host}")
                        else:
                            logger.error(f"LEADERSHIP: Failed to get new host player object for socket_id {new_host_id}")
                    else:
                        # No other players, clear host_id but keep room open
                        room.host_id = None
                        logger.info(f"LEADERSHIP: Room {room_code} has no host but kept open for potential rejoin")
                
                # CRITICAL FIX: Handle different scenarios based on game state
                if game_state == GameState.IN_PROGRESS:
                    # During active game, mark as disconnected but keep in room for potential rejoin
                    player.disconnected = True
                    player.last_activity = datetime.utcnow()
                    logger.info(f"Player {player_name} marked as disconnected during active game")
                    
                    # Don't remove from player_to_room mapping during active games
                    # This allows for potential reconnection
                    
                else:
                    # Remove player completely for non-active games
                    room.remove_player(socket_id)
                    del self.player_to_room[socket_id]
                    await self._cleanup_locks(socket_id=socket_id)
                    logger.info(f"Player {player_name} completely removed from room {room_code}")
                
                # Check if room is now empty (excluding disconnected players)
                active_players = [p for p in room.players.values() if not p.disconnected]
                if len(active_players) == 0:
                    # Room is effectively empty, clear host_id
                    room.host_id = None
                    logger.info(f"Room {room_code} is now empty but kept open for potential rejoin")
                
                # Sync to Redis if available
                await self._sync_room_to_redis(room)
                
                logger.info(f"Player {player_name} leave operation completed for room {room_code}")
                return room
                
        except Exception as e:
            logger.error(f"Error in leave_room for socket {socket_id}: {e}")
            import traceback
            logger.error(f"Leave room traceback: {traceback.format_exc()}")
            return None
    
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
        
        # CRITICAL FIX: Ensure complete cleanup of all persistent data
        # Remove all player mappings
        for socket_id in list(room.players.keys()):
            self.player_to_room.pop(socket_id, None)
        
        # Remove room from Redis if available
        if self.use_redis:
            try:
                import asyncio
                # Run Redis cleanup in event loop if available
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # Schedule Redis cleanup
                    asyncio.create_task(self._remove_room_from_redis(room_code))
                else:
                    # Run directly if no event loop
                    asyncio.run(self._remove_room_from_redis(room_code))
            except Exception as e:
                logger.error(f"Failed to remove room {room_code} from Redis: {e}")
        
        # Remove room from memory
        del self.rooms[room_code]
        
        logger.info(f"Closed room {room_code} and cleared all persistent data")
        return True
    
    async def _remove_room_from_redis(self, room_code: str) -> bool:
        """Remove room data from Redis"""
        if not self.use_redis:
            return True
        
        try:
            return await redis_manager.remove_room(room_code)
        except Exception as e:
            logger.error(f"Failed to remove room {room_code} from Redis: {e}")
            return False
    
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
