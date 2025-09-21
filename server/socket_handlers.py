"""
Socket.IO event handlers for WikiRace Multiplayer Server

Handles real-time communication between clients and server.
"""

import logging
from typing import Dict, Any

try:
    from .models import GameRoom, Player, GameState
    from .room_manager import RoomManager
except ImportError:
    from models import GameRoom, Player, GameState
    from room_manager import RoomManager

logger = logging.getLogger(__name__)


def register_socket_handlers(sio, room_manager: RoomManager):
    """Register all Socket.IO event handlers"""
    
    @sio.event
    async def connect(sid, environ, auth):
        """Handle client connection"""
        logger.info(f"Client connected: {sid}")
        
        # Send connection confirmation
        await sio.emit('connected', {
            'message': 'Connected to WikiRace Multiplayer Server',
            'socket_id': sid
        }, room=sid)
    
    @sio.event
    async def disconnect(sid):
        """Handle client disconnection"""
        logger.info(f"Client disconnected: {sid}")
        
        # Handle player leaving their room
        room = room_manager.get_room_by_player(sid)
        if room:
            player = room.get_player(sid)
            if player:
                logger.info(f"Player {player.display_name} disconnected from room {room.room_code}")
                
                # Remove player from room
                room_manager.leave_room(sid)
                
                # Notify other players in room
                await sio.emit('player_left', {
                    'socket_id': sid,
                    'player_name': player.display_name
                }, room=room.room_code, skip_sid=sid)
    
    @sio.event
    async def create_room(sid, data):
        """Handle room creation request"""
        try:
            display_name = data.get('display_name', '').strip()
            if not display_name:
                await sio.emit('error', {'message': 'Display name is required'}, room=sid)
                return
            
            # Create room
            room = room_manager.create_room(sid, display_name)
            
            # Join the room namespace
            await sio.enter_room(sid, room.room_code)
            
            # Send confirmation to creator
            await sio.emit('room_created', {
                'room_code': room.room_code,
                'is_host': True,
                'players': [{
                    'socket_id': p.socket_id,
                    'display_name': p.display_name,
                    'is_host': p.is_host
                } for p in room.players.values()]
            }, room=sid)
            
            logger.info(f"Room {room.room_code} created by {display_name}")
            
        except Exception as e:
            logger.error(f"Error creating room: {e}")
            await sio.emit('error', {'message': 'Failed to create room'}, room=sid)
    
    @sio.event
    async def join_room(sid, data):
        """Handle room join request"""
        try:
            room_code = data.get('room_code', '').strip().upper()
            display_name = data.get('display_name', '').strip()
            
            if not room_code or not display_name:
                await sio.emit('error', {'message': 'Room code and display name are required'}, room=sid)
                return
            
            # Validate room code format
            if len(room_code) != 4 or not room_code.isalpha():
                await sio.emit('error', {'message': 'Invalid room code format'}, room=sid)
                return
            
            # Try to join room
            room = room_manager.join_room(room_code, sid, display_name)
            if not room:
                await sio.emit('error', {'message': 'Room not found or unavailable'}, room=sid)
                return
            
            # Join the room namespace
            await sio.enter_room(sid, room.room_code)
            
            # Notify all players in room
            await sio.emit('player_joined', {
                'socket_id': sid,
                'display_name': display_name,
                'is_host': False,
                'players': [{
                    'socket_id': p.socket_id,
                    'display_name': p.display_name,
                    'is_host': p.is_host
                } for p in room.players.values()]
            }, room=room.room_code)
            
            logger.info(f"Player {display_name} joined room {room_code}")
            
        except Exception as e:
            logger.error(f"Error joining room: {e}")
            await sio.emit('error', {'message': 'Failed to join room'}, room=sid)
    
    @sio.event
    async def leave_room(sid):
        """Handle room leave request"""
        try:
            room = room_manager.get_room_by_player(sid)
            if not room:
                await sio.emit('error', {'message': 'Not in a room'}, room=sid)
                return
            
            player = room.get_player(sid)
            if not player:
                await sio.emit('error', {'message': 'Player not found'}, room=sid)
                return
            
            # Leave room namespace
            await sio.leave_room(sid, room.room_code)
            
            # Remove from room
            room_manager.leave_room(sid)
            
            # Notify other players
            await sio.emit('player_left', {
                'socket_id': sid,
                'player_name': player.display_name,
                'players': [{
                    'socket_id': p.socket_id,
                    'display_name': p.display_name,
                    'is_host': p.is_host
                } for p in room.players.values()]
            }, room=room.room_code, skip_sid=sid)
            
            logger.info(f"Player {player.display_name} left room {room.room_code}")
            
        except Exception as e:
            logger.error(f"Error leaving room: {e}")
            await sio.emit('error', {'message': 'Failed to leave room'}, room=sid)
    
    @sio.event
    async def set_profile(sid, data):
        """Handle player profile update"""
        try:
            display_name = data.get('display_name', '').strip()
            if not display_name:
                await sio.emit('error', {'message': 'Display name is required'}, room=sid)
                return
            
            player = room_manager.get_player(sid)
            if not player:
                await sio.emit('error', {'message': 'Player not found'}, room=sid)
                return
            
            # Update display name
            old_name = player.display_name
            player.display_name = display_name
            
            # Notify room of name change
            room = room_manager.get_room_by_player(sid)
            if room:
                await sio.emit('player_profile_updated', {
                    'socket_id': sid,
                    'old_name': old_name,
                    'new_name': display_name
                }, room=room.room_code)
            
            logger.info(f"Player {old_name} renamed to {display_name}")
            
        except Exception as e:
            logger.error(f"Error updating profile: {e}")
            await sio.emit('error', {'message': 'Failed to update profile'}, room=sid)
    
    @sio.event
    async def ping(sid):
        """Handle ping for connection testing"""
        await sio.emit('pong', {'timestamp': 'now'}, room=sid)
    
    # Placeholder for future game-related events
    # These will be implemented in later phases
    
    @sio.event
    async def select_categories(sid, data):
        """Handle game category selection (host only)"""
        # TODO: Implement in Phase 3
        await sio.emit('error', {'message': 'Category selection not yet implemented'}, room=sid)
    
    @sio.event
    async def start_game(sid, data):
        """Handle game start request (host only)"""
        # TODO: Implement in Phase 4
        await sio.emit('error', {'message': 'Game start not yet implemented'}, room=sid)
    
    @sio.event
    async def page_navigation(sid, data):
        """Handle player page navigation"""
        # TODO: Implement in Phase 4
        await sio.emit('error', {'message': 'Page navigation not yet implemented'}, room=sid)
    
    @sio.event
    async def game_complete(sid, data):
        """Handle game completion"""
        # TODO: Implement in Phase 5
        await sio.emit('error', {'message': 'Game completion not yet implemented'}, room=sid)
