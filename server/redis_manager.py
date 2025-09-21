"""
Redis manager for WikiRace Multiplayer Server

Handles Redis connection and session storage operations.
"""

import json
import logging
from typing import Optional, Dict, Any
import redis.asyncio as redis
from datetime import datetime, timedelta

try:
    from .config import settings
except ImportError:
    from config import settings

logger = logging.getLogger(__name__)


class RedisManager:
    """Manages Redis connections and operations"""
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.connected = False
    
    async def connect(self) -> bool:
        """Establish connection to Redis server"""
        try:
            self.redis_client = redis.from_url(
                settings.REDIS_URL,
                db=settings.REDIS_DB,
                decode_responses=True
            )
            
            # Test connection
            await self.redis_client.ping()
            self.connected = True
            logger.info(f"Connected to Redis at {settings.REDIS_URL}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.connected = False
            return False
    
    async def disconnect(self):
        """Close Redis connection"""
        if self.redis_client:
            await self.redis_client.close()
            self.connected = False
            logger.info("Disconnected from Redis")
    
    async def is_connected(self) -> bool:
        """Check if Redis connection is active"""
        if not self.redis_client:
            return False
        
        try:
            await self.redis_client.ping()
            return True
        except:
            self.connected = False
            return False
    
    # Room storage operations
    
    async def store_room(self, room_code: str, room_data: Dict[str, Any], ttl_hours: int = 2) -> bool:
        """Store room data in Redis"""
        if not await self.is_connected():
            return False
        
        try:
            key = f"room:{room_code}"
            # Serialize room data to JSON
            serialized_data = json.dumps(room_data, default=str)
            
            # Store with TTL
            await self.redis_client.setex(
                key, 
                timedelta(hours=ttl_hours), 
                serialized_data
            )
            
            logger.debug(f"Stored room {room_code} in Redis")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store room {room_code}: {e}")
            return False
    
    async def get_room(self, room_code: str) -> Optional[Dict[str, Any]]:
        """Retrieve room data from Redis"""
        if not await self.is_connected():
            return None
        
        try:
            key = f"room:{room_code}"
            serialized_data = await self.redis_client.get(key)
            
            if serialized_data:
                room_data = json.loads(serialized_data)
                logger.debug(f"Retrieved room {room_code} from Redis")
                return room_data
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get room {room_code}: {e}")
            return None
    
    async def delete_room(self, room_code: str) -> bool:
        """Delete room data from Redis"""
        if not await self.is_connected():
            return False
        
        try:
            key = f"room:{room_code}"
            result = await self.redis_client.delete(key)
            logger.debug(f"Deleted room {room_code} from Redis")
            return result > 0
            
        except Exception as e:
            logger.error(f"Failed to delete room {room_code}: {e}")
            return False
    
    async def room_exists(self, room_code: str) -> bool:
        """Check if room exists in Redis"""
        if not await self.is_connected():
            return False
        
        try:
            key = f"room:{room_code}"
            return await self.redis_client.exists(key) > 0
        except Exception as e:
            logger.error(f"Failed to check room existence {room_code}: {e}")
            return False
    
    # Player session operations
    
    async def store_player_session(self, socket_id: str, session_data: Dict[str, Any], ttl_hours: int = 2) -> bool:
        """Store player session data"""
        if not await self.is_connected():
            return False
        
        try:
            key = f"player:{socket_id}"
            serialized_data = json.dumps(session_data, default=str)
            
            await self.redis_client.setex(
                key,
                timedelta(hours=ttl_hours),
                serialized_data
            )
            
            logger.debug(f"Stored player session {socket_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store player session {socket_id}: {e}")
            return False
    
    async def get_player_session(self, socket_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve player session data"""
        if not await self.is_connected():
            return None
        
        try:
            key = f"player:{socket_id}"
            serialized_data = await self.redis_client.get(key)
            
            if serialized_data:
                session_data = json.loads(serialized_data)
                logger.debug(f"Retrieved player session {socket_id}")
                return session_data
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get player session {socket_id}: {e}")
            return None
    
    async def delete_player_session(self, socket_id: str) -> bool:
        """Delete player session data"""
        if not await self.is_connected():
            return False
        
        try:
            key = f"player:{socket_id}"
            result = await self.redis_client.delete(key)
            logger.debug(f"Deleted player session {socket_id}")
            return result > 0
            
        except Exception as e:
            logger.error(f"Failed to delete player session {socket_id}: {e}")
            return False
    
    # Room listing operations
    
    async def get_all_rooms(self) -> Dict[str, Dict[str, Any]]:
        """Get all active rooms from Redis"""
        if not await self.is_connected():
            return {}
        
        try:
            pattern = "room:*"
            keys = await self.redis_client.keys(pattern)
            
            rooms = {}
            for key in keys:
                room_code = key.split(":", 1)[1]
                room_data = await self.get_room(room_code)
                if room_data:
                    rooms[room_code] = room_data
            
            logger.debug(f"Retrieved {len(rooms)} rooms from Redis")
            return rooms
            
        except Exception as e:
            logger.error(f"Failed to get all rooms: {e}")
            return {}
    
    async def cleanup_expired_rooms(self) -> int:
        """Clean up expired rooms (Redis TTL handles this automatically)"""
        # Redis TTL automatically removes expired keys
        # This method is kept for compatibility with future manual cleanup logic
        return 0
    
    # Statistics and monitoring
    
    async def get_redis_stats(self) -> Dict[str, Any]:
        """Get Redis server statistics"""
        if not await self.is_connected():
            return {"error": "Not connected to Redis"}
        
        try:
            info = await self.redis_client.info()
            return {
                "connected_clients": info.get("connected_clients", 0),
                "used_memory_human": info.get("used_memory_human", "0B"),
                "total_commands_processed": info.get("total_commands_processed", 0),
                "keyspace": info.get("keyspace", {}),
                "redis_version": info.get("redis_version", "unknown")
            }
        except Exception as e:
            logger.error(f"Failed to get Redis stats: {e}")
            return {"error": str(e)}


# Global Redis manager instance
redis_manager = RedisManager()
