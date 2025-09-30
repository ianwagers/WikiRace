"""
Socket.IO event handlers for WikiRace Multiplayer Server

Handles real-time communication between clients and server.
"""

import logging
import traceback
from datetime import datetime
from typing import Dict, Any

try:
    from .models import GameRoom, Player, GameState
    from .room_manager import RoomManager
except ImportError:
    from models import GameRoom, Player, GameState
    from room_manager import RoomManager

logger = logging.getLogger(__name__)

# CRITICAL FIX: Enhanced error handling decorator
def handle_socket_error(operation_name: str):
    """Decorator for consistent error handling in socket operations"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error in {operation_name}: {e}")
                logger.error(f"Error traceback: {traceback.format_exc()}")
                
                # Extract socket ID if available
                socket_id = None
                if len(args) > 0:
                    socket_id = args[0]
                
                # Try to emit error to client if socket is available
                if socket_id and len(args) > 1:
                    sio = args[1]  # Assuming sio is second argument
                    try:
                        await sio.emit('error', {
                            'message': f'Server error in {operation_name}',
                            'operation': operation_name,
                            'timestamp': datetime.utcnow().isoformat()
                        }, room=socket_id)
                    except Exception as emit_error:
                        logger.error(f"Failed to emit error to client: {emit_error}")
                
                # Re-raise the exception for upstream handling
                raise
        return wrapper
    return decorator


async def broadcast_room_progress(sio, room, skip_sid=None):
    """Broadcast current progress of all players in a room"""
    try:
        progress_data = {}
        for player in room.players.values():
            progress_data[player.display_name] = {
                'current_page': player.current_page_title or "Starting...",
                'links_used': player.links_clicked,
                'is_completed': player.game_completed
            }
        
        # Send progress update to all players in the room (optionally skip a specific player)
        await sio.emit('room_progress_sync', {
            'room_code': room.room_code,
            'players_progress': progress_data
        }, room=room.room_code, skip_sid=skip_sid)
        
    except Exception as e:
        logger.error(f"Error broadcasting room progress: {e}")


async def check_inactive_players(sio, room_manager: RoomManager):
    """Background task to check for inactive players and remove them"""
    import asyncio
    from datetime import datetime, timedelta
    
    while True:
        try:
            await asyncio.sleep(30)  # Check every 30 seconds (less frequent)
            
            current_time = datetime.utcnow()
            
            # Check all rooms for inactive players and empty rooms
            for room_code, room in list(room_manager.rooms.items()):
                # CRITICAL FIX: Close empty rooms after 5 minutes
                if room.player_count == 0:
                    time_since_creation = current_time - room.created_at
                    if time_since_creation > timedelta(minutes=5):
                        logger.info(f"Closing empty room {room_code} after {time_since_creation.total_seconds():.1f} seconds")
                        room_manager.close_room(room_code)
                        continue
                
                inactive_players = []
                
                for socket_id, player in list(room.players.items()):
                    time_since_activity = current_time - player.last_activity
                    
                    # Different inactivity thresholds based on game state
                    if room.game_state == GameState.IN_PROGRESS:
                        # During active games, be more lenient - only disconnect after 20+ minutes
                        inactive_threshold = timedelta(minutes=20)
                        logger.debug(f"Player {player.display_name} in active game - threshold: 20 minutes")
                    else:
                        # In lobby or other states, use 20 minute threshold
                        inactive_threshold = timedelta(minutes=20)
                        logger.debug(f"Player {player.display_name} in {room.game_state.value} - threshold: 20 minutes")
                    
                    if time_since_activity > inactive_threshold:
                        logger.warning(f"Player {player.display_name} inactive for {time_since_activity.total_seconds():.1f} seconds (threshold: {inactive_threshold.total_seconds():.1f}s)")
                        inactive_players.append((socket_id, player))
                    else:
                        logger.debug(f"Player {player.display_name} active (last activity: {time_since_activity.total_seconds():.1f}s ago)")
                
                # Remove inactive players
                for socket_id, player in inactive_players:
                    logger.warning(f"Removing inactive player {player.display_name} from room {room_code}")
                    logger.warning(f"DEBUG: Player {player.display_name} (sid: {socket_id}) was inactive for {time_since_activity.total_seconds():.1f} seconds")
                    
                    # Notify the inactive player they're being kicked due to timeout
                    await sio.emit('kicked_for_inactivity', {
                        'message': 'You were disconnected due to inactivity',
                        'reason': 'timeout'
                    }, room=socket_id)
                    
                    # Remove player from room (now async)
                    updated_room = await room_manager.leave_room(socket_id)
                    
                    if updated_room:
                        # Notify remaining players
                        await sio.emit('player_left', {
                            'socket_id': socket_id,
                            'player_name': player.display_name,
                            'players': [{
                                'socket_id': p.socket_id,
                                'display_name': p.display_name,
                                'is_host': p.is_host,
                                'player_color': p.player_color
                            } for p in updated_room.players.values()]
                        }, room=room_code, skip_sid=socket_id)
                        
                        # Broadcast updated room progress to all remaining players
                        await broadcast_room_progress(sio, updated_room, skip_sid=socket_id)
                        
                        # If host was inactive, notify about new host
                        if player.is_host and updated_room.host_id:
                            new_host = updated_room.get_player(updated_room.host_id)
                            if new_host:
                                await sio.emit('host_transferred', {
                                    'new_host_id': updated_room.host_id,
                                    'new_host_name': new_host.display_name,
                                    'message': f"{new_host.display_name} is now the room leader"
                                }, room=room_code)
                    else:
                        # Room was closed, notify all remaining players and ensure complete cleanup
                        logger.info(f"Room {room_code} was closed due to inactivity")
                        
                        # CRITICAL FIX: Ensure all players in the room are properly notified and kicked
                        # Get all remaining players before room is deleted
                        remaining_players = list(room.players.values()) if room else []
                        
                        # Notify all remaining players about room closure
                        for remaining_player in remaining_players:
                            await sio.emit('room_closed', {
                                'message': 'Room was closed due to inactivity',
                                'reason': 'timeout'
                            }, room=remaining_player.socket_id)
                            
                            # Also send kicked_for_inactivity to ensure consistent behavior
                            await sio.emit('kicked_for_inactivity', {
                                'message': 'You were disconnected due to room timeout',
                                'reason': 'room_timeout'
                            }, room=remaining_player.socket_id)
                        
                        logger.info(f"Notified {len(remaining_players)} remaining players about room {room_code} closure")
                    
        except Exception as e:
            logger.error(f"Error in inactive player check: {e}")
            await asyncio.sleep(30)  # Wait before retrying


def register_socket_handlers(sio, room_manager: RoomManager):
    """Register all Socket.IO event handlers"""
    
    print("CONSOLE: Registering Socket.IO handlers...")
    logger.error("FORCE LOG: Socket handlers being registered!")
    
    # Start the inactive player checker
    import asyncio
    asyncio.create_task(check_inactive_players(sio, room_manager))
    
    @sio.event
    async def connect(sid, environ, auth):
        """Handle client connection"""
        print(f"CONSOLE: Client connected: {sid}")
        logger.info(f"Client connected: {sid}")
        
        # Send connection confirmation
        await sio.emit('connected', {
            'message': 'Connected to WikiRace Multiplayer Server',
            'socket_id': sid
        }, room=sid)
    
    @sio.event
    @handle_socket_error("disconnect")
    async def disconnect(sid):
        """Handle client disconnection with enhanced error handling"""
        logger.info(f"DISCONNECT: Client disconnected: {sid}")
        
        # Handle player leaving their room
        room = room_manager.get_room_by_player(sid)
        if room:
            player = room.get_player(sid)
            if player:
                logger.info(f"DISCONNECT: Player {player.display_name} disconnected from room {room.room_code}")
                
                # Check if player was host before removing
                was_host = room.is_host(sid)
                room_code = room.room_code
                game_state = room.game_state
                
                # CRITICAL FIX: Handle disconnection during active games
                if game_state == GameState.IN_PROGRESS:
                    # Mark player as disconnected but keep them in room for potential rejoin
                    player.disconnected = True
                    logger.info(f"DISCONNECT: Player {player.display_name} disconnected during active game - marked for potential rejoin")
                    
                    # Notify remaining players about disconnection
                    await sio.emit('player_disconnected', {
                        'socket_id': sid,
                        'player_name': player.display_name,
                        'message': f"{player.display_name} disconnected during the game",
                        'can_rejoin': True
                    }, room=room_code, skip_sid=sid)
                    
                    # If host disconnected during game, transfer host immediately
                    if was_host and room.host_id:
                        new_host = room.get_player(room.host_id)
                        if new_host:
                            await sio.emit('host_transferred', {
                                'new_host_id': room.host_id,
                                'new_host_name': new_host.display_name,
                                'message': f"{new_host.display_name} is now the room leader"
                            }, room=room_code)
                    
                    # CRITICAL FIX: Check if all players are now disconnected during game
                    active_players = [p for p in room.players.values() if not p.disconnected]
                    if len(active_players) == 0:
                        logger.warning(f"DISCONNECT: All players disconnected during game in room {room_code} - ending game")
                        # End the game and close the room
                        room.game_state = GameState.FINISHED
                        await sio.emit('game_ended', {
                            'message': 'Game ended - all players disconnected',
                            'reason': 'all_disconnected',
                            'results': []
                        }, room=room_code)
                        
                        # Close the room after a short delay
                        import asyncio
                        await asyncio.sleep(5)  # Give time for clients to process
                        room_manager.close_room(room_code)
                        logger.info(f"DISCONNECT: Closed room {room_code} due to all players disconnecting during game")
                else:
                    # CRITICAL FIX: For non-active games, remove player completely to prevent ghost players
                    logger.info(f"DISCONNECT: Removing player {player.display_name} from room {room_code} (non-active game)")
                    
                    # Get remaining players before removing the player
                    remaining_players = [p for p in room.players.values() if p.socket_id != sid]
                    logger.info(f"DISCONNECT: Remaining players after {player.display_name} leaves: {[p.display_name for p in remaining_players]}")
                    
                    # Remove player from room (now async)
                    updated_room = await room_manager.leave_room(sid)
                    
                    # CRITICAL FIX: Always notify remaining players about the player leaving
                    if remaining_players:
                        logger.info(f"DISCONNECT: Notifying {len(remaining_players)} remaining players about {player.display_name} leaving")
                        await sio.emit('player_left', {
                            'socket_id': sid,
                            'player_name': player.display_name,
                            'players': [{
                                'socket_id': p.socket_id,
                                'display_name': p.display_name,
                                'is_host': p.is_host,
                                'player_color': p.player_color
                            } for p in remaining_players]
                        }, room=room_code, skip_sid=sid)
                        
                        # If host left and there are remaining players, notify about new host
                        if was_host and updated_room and updated_room.host_id:
                            new_host = updated_room.get_player(updated_room.host_id)
                            if new_host:
                                logger.info(f"DISCONNECT: Host transfer - {new_host.display_name} is now the room leader")
                                await sio.emit('host_transferred', {
                                    'new_host_id': updated_room.host_id,
                                    'new_host_name': new_host.display_name,
                                    'message': f"{new_host.display_name} is now the room leader"
                                }, room=room_code)
                        
                        # Broadcast updated room progress to all remaining players
                        if updated_room:
                            await broadcast_room_progress(sio, updated_room, skip_sid=sid)
                    else:
                        # Room is now empty but kept open for potential rejoin
                        logger.info(f"DISCONNECT: Room {room_code} is now empty but kept open for potential rejoin")
            else:
                logger.warning(f"DISCONNECT: Player not found for socket {sid} in room {room.room_code}")
        else:
            logger.info(f"DISCONNECT: Socket {sid} was not in any room")
    
    @sio.event
    async def create_room(sid, data):
        """Handle room creation request"""
        try:
            display_name = data.get('display_name', '').strip()
            if not display_name:
                await sio.emit('error', {'message': 'Display name is required'}, room=sid)
                return
            
            # Create room
            room = await room_manager.create_room(sid, display_name)
            
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
                # Check if it's a name conflict by trying to get the room first
                existing_room = room_manager.get_room(room_code)
                if existing_room and existing_room.get_player_by_name(display_name):
                    # CRITICAL FIX: Handle rejoin scenario - use improved room manager logic
                    existing_player = existing_room.get_player_by_name(display_name)
                    if existing_player and (existing_player.socket_id == sid or existing_player.disconnected):
                        # This is a rejoin - let room manager handle the logic
                        logger.info(f"Player {display_name} attempting rejoin to room {room_code}")
                        room = existing_room
                    else:
                        await sio.emit('error', {'message': f'Player name "{display_name}" is already taken in this room'}, room=sid)
                        return
                else:
                    await sio.emit('error', {'message': 'Room not found or unavailable'}, room=sid)
                    return
            
            # Join the room namespace
            await sio.enter_room(sid, room.room_code)
            
            # Update player activity timestamp to ensure they're not marked inactive
            player = room.get_player(sid)
            if player:
                from datetime import datetime
                player.last_activity = datetime.utcnow()
                # CRITICAL FIX: Reset disconnected flag if player rejoins
                if player.disconnected:
                    player.disconnected = False
                    logger.info(f"Player {player.display_name} rejoined room {room_code} - reset disconnected flag")
                logger.debug(f"Updated activity for player {player.display_name} after room join")
            
            # Send room_joined event to the joining player
            await sio.emit('room_joined', {
                'room_code': room.room_code,
                'socket_id': sid,
                'display_name': display_name,
                'is_host': False,
                'players': [{
                    'socket_id': p.socket_id,
                    'display_name': p.display_name,
                    'is_host': p.is_host,
                    'player_color': p.player_color
                } for p in room.players.values()]
            }, room=sid)
            
            # Notify all other players in room
            await sio.emit('player_joined', {
                'socket_id': sid,
                'display_name': display_name,
                'is_host': False,
                'players': [{
                    'socket_id': p.socket_id,
                    'display_name': p.display_name,
                    'is_host': p.is_host,
                    'player_color': p.player_color
                } for p in room.players.values()]
            }, room=room.room_code, skip_sid=sid)
            
            # CRITICAL FIX: If player was disconnected and rejoined, notify about reconnection
            if player and player.disconnected == False and room.game_state == GameState.IN_PROGRESS:
                await sio.emit('player_reconnected', {
                    'socket_id': sid,
                    'player_name': display_name,
                    'message': f"{display_name} has reconnected to the game"
                }, room=room.room_code, skip_sid=sid)
            
            logger.info(f"Player {display_name} joined room {room_code}")
            
        except Exception as e:
            logger.error(f"Error joining room: {e}")
            await sio.emit('error', {'message': 'Failed to join room'}, room=sid)
    
    @sio.event
    async def ping(sid, data=None):
        """Handle ping requests for connection testing"""
        try:
            logger.info(f"PING: Received ping from socket {sid}")
            await sio.emit('pong', {'timestamp': datetime.utcnow().isoformat()}, room=sid)
            logger.info(f"PONG: Sent pong to socket {sid}")
        except Exception as e:
            logger.error(f"PING ERROR: Error handling ping: {e}")

    @sio.event
    async def pong(sid, data):
        """Handle pong responses (for debugging)"""
        try:
            timestamp = data.get('timestamp', 'unknown')
            logger.info(f"PONG: Received pong from socket {sid} at {timestamp}")
        except Exception as e:
            logger.error(f"PONG ERROR: Error handling pong: {e}")

    @sio.event
    @handle_socket_error("leave_room")
    async def leave_room(sid):
        """Handle room leave request with enhanced error handling"""
        try:
            print(f"CRITICAL: Server received leave_room request from socket {sid}")
            logger.info(f"CRITICAL: Received leave_room request from socket {sid}")
            print(f"CRITICAL: Processing leave_room for socket {sid}...")
            
            room = room_manager.get_room_by_player(sid)
            if not room:
                logger.warning(f"CRITICAL: Socket {sid} not in any room")
                await sio.emit('error', {'message': 'Not in a room'}, room=sid)
                return
            
            player = room.get_player(sid)
            if not player:
                logger.warning(f"CRITICAL: Player not found for socket {sid} in room {room.room_code}")
                await sio.emit('error', {'message': 'Player not found'}, room=sid)
                return
            
            logger.info(f"CRITICAL: Processing leave_room for player {player.display_name} from room {room.room_code}")
            
            # Check if player was host before removing
            was_host = room.is_host(sid)
            room_code = room.room_code
            
            # Leave room namespace
            await sio.leave_room(sid, room_code)
            
            # Remove from room (now async)
            updated_room = await room_manager.leave_room(sid)
            
            if updated_room:
                # Room still exists, notify remaining players
                remaining_players = [{
                    'socket_id': p.socket_id,
                    'display_name': p.display_name,
                    'is_host': p.is_host,
                    'player_color': p.player_color
                } for p in updated_room.players.values()]
                
                print(f"CRITICAL: Broadcasting player_left to room {room_code}")
                print(f"CRITICAL: Remaining players: {[p['display_name'] for p in remaining_players]}")
                print(f"CRITICAL: Skipping socket {sid}")
                
                await sio.emit('player_left', {
                    'socket_id': sid,
                    'player_name': player.display_name,
                    'players': remaining_players
                }, room=room_code, skip_sid=sid)
                
                print(f"CRITICAL: player_left event sent to room {room_code}")
                
                # Broadcast updated room progress to all remaining players
                await broadcast_room_progress(sio, updated_room, skip_sid=sid)
                
                # If host left and room still exists, notify about new host
                if was_host and updated_room.host_id:
                    new_host = updated_room.get_player(updated_room.host_id)
                    if new_host:
                        logger.info(f"LEADERSHIP: Emitting host_transferred event - {new_host.display_name} is now the room leader")
                        print(f"LEADERSHIP: Emitting host_transferred event - {new_host.display_name} is now the room leader")
                        await sio.emit('host_transferred', {
                            'new_host_id': updated_room.host_id,
                            'new_host_name': new_host.display_name,
                            'message': f"{new_host.display_name} is now the room leader"
                        }, room=room_code)
                        logger.info(f"LEADERSHIP: host_transferred event emitted successfully")
                    else:
                        logger.error(f"LEADERSHIP: Failed to get new host player object for socket_id {updated_room.host_id}")
                elif was_host:
                    logger.info(f"LEADERSHIP: Host left but no new host assigned (room.host_id: {updated_room.host_id})")
                else:
                    logger.info(f"LEADERSHIP: Non-host player left, no leadership transfer needed")
            else:
                # Room was deleted (last player left)
                logger.info(f"CRITICAL: Room {room_code} was deleted - last player left")
            
            logger.info(f"CRITICAL: leave_room handler completed for player {player.display_name}")
            
        except Exception as e:
            logger.error(f"CRITICAL: Error in leave_room handler: {e}")
            logger.error(f"CRITICAL: Leave room traceback: {traceback.format_exc()}")
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
    
    
    # Placeholder for future game-related events
    # These will be implemented in later phases
    
    @sio.event
    async def select_categories(sid, data):
        """Handle game category selection (host only)"""
        try:
            room = room_manager.get_room_by_player(sid)
            if not room:
                await sio.emit('error', {'message': 'Not in a room'}, room=sid)
                return
            
            # Check if player is host
            if not room.is_host(sid):
                await sio.emit('error', {'message': 'Only the room host can configure game settings'}, room=sid)
                return
            
            # Extract configuration data
            start_category = data.get('start_category', 'Random')
            end_category = data.get('end_category', 'Random')
            custom_start = data.get('custom_start')
            custom_end = data.get('custom_end')
            
            # Update room configuration (store for game start)
            room.categories = [start_category, end_category]
            
            # Broadcast configuration to all players in room
            await sio.emit('game_config_updated', {
                'start_category': start_category,
                'end_category': end_category,
                'custom_start': custom_start,
                'custom_end': custom_end,
                'host_name': room.get_player(sid).display_name if room.get_player(sid) else 'Unknown'
            }, room=room.room_code)
            
            logger.info(f"Game configuration updated in room {room.room_code}: {start_category} -> {end_category}")
            
        except Exception as e:
            logger.error(f"Error updating game configuration: {e}")
            await sio.emit('error', {'message': 'Failed to update game configuration'}, room=sid)
    
    @sio.event
    async def start_game(sid, data):
        """Handle game start request (host only)"""
        print(f"CONSOLE: start_game handler called! sid={sid}, data={data}")
        logger.info(f"DEBUG: Received start_game request from {sid} with data: {data}")
        logger.error(f"FORCE ERROR LOG: start_game handler was definitely called!")
        
        # Force flush logs
        import logging
        for handler in logging.getLogger().handlers:
            handler.flush()
        try:
            # Debug: Log current room manager state
            logger.info(f"DEBUG: Room manager has {len(room_manager.rooms)} rooms")
            logger.info(f"DEBUG: Player-to-room mapping: {room_manager.player_to_room}")
            
            room = room_manager.get_room_by_player(sid)
            if not room:
                logger.warning(f"DEBUG: Player {sid} not in any room")
                logger.warning(f"DEBUG: Available rooms: {list(room_manager.rooms.keys())}")
                logger.warning(f"DEBUG: Player mappings: {room_manager.player_to_room}")
                await sio.emit('error', {'message': 'Not in a room'}, room=sid)
                return
            
            logger.info(f"DEBUG: Found room {room.room_code} for player {sid}")
            
            # Check if player is host
            logger.info(f"DEBUG: Checking if player {sid} is host in room {room.room_code}")
            if not room.is_host(sid):
                logger.warning(f"DEBUG: Player {sid} is not host, rejecting start_game")
                await sio.emit('error', {'message': 'Only the room host can start the game'}, room=sid)
                return
            
            logger.info(f"DEBUG: Player {sid} is host, checking player count")
            # Check if enough players
            if room.player_count < 2:
                logger.warning(f"DEBUG: Not enough players ({room.player_count}), need at least 2")
                await sio.emit('error', {'message': 'At least 2 players required to start'}, room=sid)
                return
            
            # CRITICAL FIX: Check for disconnected players and prevent game start
            active_players = []
            disconnected_players = []
            for player in room.players.values():
                if hasattr(player, 'disconnected') and player.disconnected:
                    disconnected_players.append(player.display_name)
                else:
                    active_players.append(player.display_name)
            
            logger.info(f"DEBUG: Active players: {active_players}, Disconnected players: {disconnected_players}")
            
            if len(active_players) < 2:
                logger.warning(f"DEBUG: Not enough active players ({len(active_players)}), need at least 2")
                if disconnected_players:
                    await sio.emit('error', {'message': f'Cannot start game - {", ".join(disconnected_players)} have disconnected'}, room=sid)
                else:
                    await sio.emit('error', {'message': 'Not enough active players to start the game'}, room=sid)
                return
            
            if disconnected_players:
                logger.warning(f"DEBUG: Found disconnected players: {disconnected_players} - removing them from room")
                # Remove disconnected players from the room
                for player in list(room.players.values()):
                    if hasattr(player, 'disconnected') and player.disconnected:
                        logger.info(f"DEBUG: Removing disconnected player {player.display_name} from room")
                        del room.players[player.socket_id]
                        if player.socket_id in room_manager.player_to_room:
                            del room_manager.player_to_room[player.socket_id]
                
                # Update room player count
                room.player_count = len(room.players)
                logger.info(f"DEBUG: Room {room.room_code} now has {room.player_count} active players")
                
                # Notify remaining players about disconnected players being removed
                if room.players:
                    await sio.emit('players_removed', {
                        'removed_players': disconnected_players,
                        'message': f"{', '.join(disconnected_players)} were removed due to disconnection",
                        'players': [{
                            'socket_id': p.socket_id,
                            'display_name': p.display_name,
                            'is_host': p.is_host,
                            'player_color': p.player_color
                        } for p in room.players.values()]
                    }, room=room.room_code)
            
            logger.info(f"DEBUG: All validations passed, proceeding with game start")
            
            # Extract game configuration
            logger.info(f"DEBUG: Extracting game configuration from data: {data}")
            start_page = data.get('start_page', 'Random')
            end_page = data.get('end_page', 'Random')
            custom_start = data.get('custom_start')
            custom_end = data.get('custom_end')
            logger.info(f"DEBUG: Config - start: {start_page}, end: {end_page}, custom_start: {custom_start}, custom_end: {custom_end}")
            
            # Use server-side GameLogic to select pages
            logger.info(f"DEBUG: Starting page selection process...")
            try:
                # Try relative import first, then absolute import as fallback
                try:
                    from .game_logic import server_game_logic
                except ImportError:
                    from game_logic import server_game_logic
                logger.info(f"DEBUG: Imported game_logic successfully")
                
                start_url, end_url, start_title, end_title = server_game_logic.select_game_pages(
                    start_page, end_page, custom_start, custom_end
                )
                logger.info(f"DEBUG: Page selection completed - start: {start_title}, end: {end_title}")
                
                if not start_url or not end_url:
                    logger.error(f"DEBUG: Invalid pages selected - start_url: {start_url}, end_url: {end_url}")
                    await sio.emit('error', {'message': 'Failed to select valid game pages'}, room=sid)
                    return
                
                room.start_url = start_url
                room.end_url = end_url
                room.start_title = start_title or "Unknown Page"
                room.end_title = end_title or "Unknown Page"
                logger.info(f"DEBUG: Room URLs set successfully")
                
            except Exception as e:
                logger.error(f"DEBUG: Exception in page selection: {e}")
                import traceback
                logger.error(f"DEBUG: Page selection traceback: {traceback.format_exc()}")
                # Fallback to placeholder pages
                room.start_url = "https://en.wikipedia.org/wiki/Main_Page"
                room.end_url = "https://en.wikipedia.org/wiki/Special:Random"
                room.start_title = "Main Page"
                room.end_title = "Random Page"
                logger.info(f"DEBUG: Using fallback pages")
            
            # Update room state to starting (countdown phase)
            logger.info(f"DEBUG: Setting room state to STARTING")
            room.game_state = GameState.STARTING
            
            # Send countdown start event
            logger.info(f"DEBUG: About to send game_starting event to room {room.room_code}")
            logger.info(f"DEBUG: Room has {room.player_count} players")
            logger.info(f"DEBUG: Event data: start_url={room.start_url}, end_url={room.end_url}")
            
            try:
                await sio.emit('game_starting', {
                    'room_code': room.room_code,
                    'start_url': room.start_url,
                    'end_url': room.end_url,
                    'start_title': room.start_title,
                    'end_title': room.end_title,
                    'countdown_seconds': 5,
                    'message': 'Get ready! Game starting in 5 seconds...'
                }, room=room.room_code)
                logger.info(f"DEBUG: game_starting emit completed successfully")
            except Exception as emit_error:
                logger.error(f"ERROR DEBUG: Error emitting game_starting: {emit_error}")
                raise
            
            # Schedule game start with a background task
            import asyncio
            
            async def start_game_after_countdown():
                try:
                    logger.info(f"DEBUG: Starting countdown for room {room.room_code}")
                    await asyncio.sleep(5)
                    logger.info(f"DEBUG: Countdown finished, starting game for room {room.room_code}")
                    
                    # Update room state to in progress
                    room.game_state = GameState.IN_PROGRESS
                    game_start_time = datetime.utcnow()
                    room.game_started_at = game_start_time
                    
                    # RESET ALL PLAYER DATA FOR NEW GAME
                    logger.info(f"RESET SERVER DEBUG: Starting player data reset for {len(room.players)} players")
                    for player in room.players.values():
                        logger.info(f"RESET SERVER DEBUG: Before reset - {player.display_name}: links_clicked={player.links_clicked}, history_count={len(player.navigation_history)}")
                        
                        # Reset game state
                        player.game_completed = False
                        player.completion_time = None
                        player.game_start_time = game_start_time
                        
                        # Clear navigation history
                        player.navigation_history.clear()
                        player.links_clicked = 0
                        player.current_page = None
                        player.current_page_title = None
                        
                        # Reset activity tracking
                        player.last_activity = datetime.utcnow()
                        
                        logger.info(f"RESET SERVER DEBUG: After reset - {player.display_name}: links_clicked={player.links_clicked}, history_count={len(player.navigation_history)}")
                        logger.info(f"DEBUG: Reset player {player.display_name} data for new game")
                    
                    # CRITICAL: Wait a moment to ensure all previous progress updates are processed
                    await asyncio.sleep(0.1)
                    
                    # Broadcast initial progress reset to all players to ensure synchronization
                    logger.info(f"PROGRESS SERVER DEBUG: Broadcasting initial progress reset to {len(room.players)} players")
                    await broadcast_room_progress(sio, room, skip_sid=None)
                    
                    # Additional broadcast to ensure all clients receive the reset
                    await asyncio.sleep(0.05)
                    logger.info(f"PROGRESS SERVER DEBUG: Broadcasting second progress reset to {len(room.players)} players")
                    await broadcast_room_progress(sio, room, skip_sid=None)
                    
                    logger.info(f"DEBUG: Sending game_started event to room {room.room_code}")
                    # Prepare players data with colors
                    players_data = []
                    for player in room.players.values():
                        players_data.append({
                            'name': player.display_name,
                            'is_host': player.is_host,
                            'player_color': player.player_color or '#CCCCCC'
                        })
                    
                    # Notify all players that game has started
                    await sio.emit('game_started', {
                        'room_code': room.room_code,
                        'start_url': room.start_url,
                        'end_url': room.end_url,
                        'start_title': room.start_title,
                        'end_title': room.end_title,
                        'game_state': room.game_state.value,
                        'players': players_data,
                        'message': 'GO! Race to the destination!'
                    }, room=room.room_code)
                    logger.info(f"DEBUG: game_started emit completed successfully")
                    
                except Exception as e:
                    logger.error(f"ERROR DEBUG: Error in countdown task: {e}")
                    import traceback
                    logger.error(f"ERROR DEBUG: Countdown traceback: {traceback.format_exc()}")
            
            # Start the countdown task in the background with error handling
            try:
                asyncio.create_task(start_game_after_countdown())
                logger.info(f"DEBUG: Countdown task created successfully for room {room.room_code}")
            except Exception as task_error:
                logger.error(f"ERROR DEBUG: Failed to create countdown task: {task_error}")
                await sio.emit('error', {'message': 'Failed to start countdown'}, room=sid)
                return
            
            logger.info(f"DEBUG: Game start handler completed successfully for room {room.room_code}")
            
        except Exception as e:
            logger.error(f"ERROR DEBUG: CRITICAL ERROR in start_game handler: {e}")
            import traceback
            logger.error(f"ERROR DEBUG: Start game traceback: {traceback.format_exc()}")
            await sio.emit('error', {'message': 'Failed to start game'}, room=sid)
        
        logger.info(f"DEBUG: start_game handler exiting for {sid}")
    
    @sio.event
    async def test_event(sid, data):
        """TEST EVENT to verify Socket.IO is working"""
        print(f"CONSOLE: TEST EVENT RECEIVED! sid={sid}, data={data}")
        logger.error(f"FORCE LOG: TEST EVENT RECEIVED!")
        await sio.emit('test_response', {'received': data}, room=sid)
    
    @sio.event
    async def player_progress(sid, data):
        """Handle player progress updates with detailed navigation tracking"""
        print(f"PROGRESS DEBUG: Received player_progress from {sid}: {data}")
        try:
            room_code = data.get('room_code')
            player_name = data.get('player_name')
            page_url = data.get('page_url')
            page_title = data.get('page_title')
            
            print(f"PROGRESS DEBUG: Progress data - room: {room_code}, player: {player_name}, page: {page_title}")
            
            if not room_code or not player_name or not page_url or not page_title:
                print(f"ERROR DEBUG: Invalid progress data - missing fields")
                await sio.emit('error', {'message': 'Invalid progress data - missing required fields'}, room=sid)
                return
            
            room = room_manager.get_room(room_code)
            if not room:
                await sio.emit('error', {'message': 'Room not found'}, room=sid)
                return
            
            # Update player progress in room
            player = room.get_player_by_name(player_name)
            if player:
                # DEBUG: Log before adding entry
                print(f"PROGRESS DEBUG: Before adding entry for {player_name}:")
                print(f"PROGRESS DEBUG:   - Current navigation_history length: {len(player.navigation_history)}")
                print(f"PROGRESS DEBUG:   - Current links_clicked: {player.links_clicked}")
                print(f"PROGRESS DEBUG:   - Adding: {page_title} ({page_url})")
                
                # Check if this is a duplicate of the last navigation entry
                should_add_entry = True
                if player.navigation_history:
                    last_entry = player.navigation_history[-1]
                    # Check if it's the same page (ignoring query parameters)
                    last_url_base = last_entry.page_url.split('?')[0]
                    current_url_base = page_url.split('?')[0]
                    if last_url_base == current_url_base and last_entry.page_title == page_title:
                        should_add_entry = False  # Skip duplicate entry
                        print(f"PROGRESS DEBUG: Skipping duplicate entry for {player_name}")
                
                # Add navigation entry only if it's not a duplicate
                if should_add_entry:
                    navigation_entry = player.add_navigation_entry(page_url, page_title)
                else:
                    # Use the existing last entry for broadcasting
                    navigation_entry = player.navigation_history[-1]
                
                # DEBUG: Log after adding entry
                print(f"PROGRESS DEBUG: After adding entry for {player_name}:")
                print(f"PROGRESS DEBUG:   - New navigation_history length: {len(player.navigation_history)}")
                print(f"PROGRESS DEBUG:   - New links_clicked: {player.links_clicked}")
                print(f"PROGRESS DEBUG:   - Navigation entries:")
                for i, entry in enumerate(player.navigation_history):
                    print(f"PROGRESS DEBUG:     {i}: {entry.page_title} (link #{entry.link_number})")
                
                # Broadcast progress to OTHER players only (exclude sender to prevent feedback loop)
                await sio.emit('player_progress', {
                    'player_name': player_name,
                    'current_page': page_title,  # Send title for display
                    'current_page_url': page_url,
                    'links_used': player.links_clicked,
                    'time_elapsed': navigation_entry.time_elapsed
                }, room=room_code, skip_sid=sid)
                
                print(f"PROGRESS DEBUG: Broadcasting progress for {player_name}: {page_title} (links: {player.links_clicked})")
                print(f"PROGRESS DEBUG: Room has {len(room.players)} players, broadcasting to room {room_code}")
                
                # Also send updated progress to all players for sync (exclude sender to prevent feedback)
                await broadcast_room_progress(sio, room, skip_sid=sid)
                
                logger.info(f"Player {player_name} navigation: {page_title} (Link #{player.links_clicked}, {navigation_entry.time_elapsed:.1f}s)")
            
        except Exception as e:
            logger.error(f"Error handling player progress: {e}")
            await sio.emit('error', {'message': 'Failed to update progress'}, room=sid)
    
    @sio.event
    async def game_complete(sid, data):
        """Handle game completion"""
        try:
            room_code = data.get('room_code')
            player_name = data.get('player_name')
            completion_time = data.get('completion_time', 0.0)
            links_used = data.get('links_used', 0)
            
            if not room_code or not player_name:
                await sio.emit('error', {'message': 'Invalid completion data'}, room=sid)
                return
            
            room = room_manager.get_room(room_code)
            if not room:
                await sio.emit('error', {'message': 'Room not found'}, room=sid)
                return
            
            # Update player completion status
            player = room.get_player_by_name(player_name)
            if player:
                player.game_completed = True
                player.completion_time = completion_time
                
                # Check if this is the first completion (winner)
                completed_players = [p for p in room.players.values() if p.game_completed]
                
                # Broadcast player completion to all players
                await sio.emit('player_completed', {
                    'player_name': player_name,
                    'completion_time': completion_time,
                    'links_used': links_used
                }, room=room_code)
                
                # If this is the first completion, end the game
                if len(completed_players) == 1:  # First player to complete
                    await end_game_for_room(sio, room)
                
                logger.info(f"Player {player_name} completed game in {completion_time:.2f}s with {links_used} links")
            
        except Exception as e:
            logger.error(f"Error handling game completion: {e}")
            await sio.emit('error', {'message': 'Failed to process completion'}, room=sid)
    
    @sio.event
    async def player_color_update(sid, data):
        """Handle player color update"""
        try:
            room_code = data.get('room_code')
            player_name = data.get('player_name')
            color_hex = data.get('color_hex')
            color_name = data.get('color_name')
            
            logger.info(f"Player {player_name} updated color to {color_name} ({color_hex}) in room {room_code}")
            
            if not room_code or not player_name or not color_hex:
                await sio.emit('error', {'message': 'Invalid color update data'}, room=sid)
                return
            
            room = room_manager.get_room(room_code)
            if not room:
                await sio.emit('error', {'message': 'Room not found'}, room=sid)
                return
            
            player = room.get_player(sid)
            if not player or player.display_name != player_name:
                await sio.emit('error', {'message': 'Player not found in room'}, room=sid)
                return
            
            # Update player color
            player.update_color(color_hex)
            
            # Broadcast color update to all players in the room
            await sio.emit('player_color_updated', {
                'player_name': player_name,
                'color_hex': color_hex,
                'color_name': color_name
            }, room=room.room_code, skip_sid=sid)
            
            logger.info(f"Color update broadcasted for {player_name} in room {room_code}")
            
        except Exception as e:
            logger.error(f"Error handling color update: {e}")
            await sio.emit('error', {'message': 'Failed to update color'}, room=sid)


async def end_game_for_room(sio, room):
    """End the game for a room and broadcast results"""
    try:
        # Update room state
        room.game_state = GameState.COMPLETED
        
        # Collect results from all players
        results = []
        for player in room.players.values():
            results.append({
                'player_name': player.display_name,
                'is_completed': player.game_completed,
                'completion_time': player.completion_time,
                'links_used': player.links_clicked,
                'current_page': player.current_page_title or 'Unknown',
                'current_page_url': player.current_page,
                'navigation_history': player.get_navigation_summary()
            })
        
        # Sort results by completion status and time
        results.sort(key=lambda x: (not x['is_completed'], x['completion_time'] or float('inf')))
        
        # Add rankings
        for i, result in enumerate(results):
            result['rank'] = i + 1
        
        # Broadcast game end to all players
        await sio.emit('game_ended', {
            'room_code': room.room_code,
            'results': results,
            'winner': results[0] if results else None
        }, room=room.room_code)
        
        logger.info(f"Game ended in room {room.room_code}, winner: {results[0]['player_name'] if results else 'None'}")
        
    except Exception as e:
        logger.error(f"Error ending game for room {room.room_code}: {e}")