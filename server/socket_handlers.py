"""
Socket.IO event handlers for WikiRace Multiplayer Server

Handles real-time communication between clients and server.
"""

import logging
from datetime import datetime
from typing import Dict, Any

try:
    from .models import GameRoom, Player, GameState
    from .room_manager import RoomManager
except ImportError:
    from models import GameRoom, Player, GameState
    from room_manager import RoomManager

logger = logging.getLogger(__name__)


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


def register_socket_handlers(sio, room_manager: RoomManager):
    """Register all Socket.IO event handlers"""
    
    print("CONSOLE: Registering Socket.IO handlers...")
    logger.error("FORCE LOG: Socket handlers being registered!")
    
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
    async def disconnect(sid):
        """Handle client disconnection"""
        logger.info(f"Client disconnected: {sid}")
        
        # Handle player leaving their room
        room = room_manager.get_room_by_player(sid)
        if room:
            player = room.get_player(sid)
            if player:
                logger.info(f"Player {player.display_name} disconnected from room {room.room_code}")
                
                # Check if player was host before removing
                was_host = room.is_host(sid)
                room_code = room.room_code
                
                # Remove player from room
                updated_room = room_manager.leave_room(sid)
                
                if updated_room:
                    # Room still exists, notify remaining players
                    await sio.emit('player_left', {
                        'socket_id': sid,
                        'player_name': player.display_name,
                        'players': [{
                            'socket_id': p.socket_id,
                            'display_name': p.display_name,
                            'is_host': p.is_host
                        } for p in updated_room.players.values()]
                    }, room=room_code, skip_sid=sid)
                    
                    # If host left and room still exists, notify about new host
                    if was_host and updated_room.host_id:
                        new_host = updated_room.get_player(updated_room.host_id)
                        if new_host:
                            await sio.emit('host_transferred', {
                                'new_host_id': updated_room.host_id,
                                'new_host_name': new_host.display_name,
                                'message': f"{new_host.display_name} is now the room leader"
                            }, room=room_code)
                else:
                    # Room was deleted (last player left)
                    logger.info(f"Room {room_code} was deleted - last player disconnected")
    
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
                await sio.emit('error', {'message': 'Room not found or unavailable'}, room=sid)
                return
            
            # Join the room namespace
            await sio.enter_room(sid, room.room_code)
            
            # Send room_joined event to the joining player
            await sio.emit('room_joined', {
                'room_code': room.room_code,
                'socket_id': sid,
                'display_name': display_name,
                'is_host': False,
                'players': [{
                    'socket_id': p.socket_id,
                    'display_name': p.display_name,
                    'is_host': p.is_host
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
                    'is_host': p.is_host
                } for p in room.players.values()]
            }, room=room.room_code, skip_sid=sid)
            
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
            
            # Check if player was host before removing
            was_host = room.is_host(sid)
            room_code = room.room_code
            
            # Leave room namespace
            await sio.leave_room(sid, room_code)
            
            # Remove from room
            updated_room = room_manager.leave_room(sid)
            
            if updated_room:
                # Room still exists, notify remaining players
                await sio.emit('player_left', {
                    'socket_id': sid,
                    'player_name': player.display_name,
                    'players': [{
                        'socket_id': p.socket_id,
                        'display_name': p.display_name,
                        'is_host': p.is_host
                    } for p in updated_room.players.values()]
                }, room=room_code, skip_sid=sid)
                
                # If host left and room still exists, notify about new host
                if was_host and updated_room.host_id:
                    new_host = updated_room.get_player(updated_room.host_id)
                    if new_host:
                        await sio.emit('host_transferred', {
                            'new_host_id': updated_room.host_id,
                            'new_host_name': new_host.display_name,
                            'message': f"{new_host.display_name} is now the room leader"
                        }, room=room_code)
            else:
                # Room was deleted (last player left)
                logger.info(f"Room {room_code} was deleted - last player left")
            
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
            room = room_manager.get_room_by_player(sid)
            if not room:
                logger.warning(f"DEBUG: Player {sid} not in any room")
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
                    
                    # Initialize all players' game start times and add start page to navigation history
                    for player in room.players.values():
                        player.game_start_time = game_start_time
                        # Add the starting page as the first navigation entry
                        if room.start_url and room.start_title:
                            player.add_navigation_entry(room.start_url, room.start_title)
                    
                    logger.info(f"DEBUG: Sending game_started event to room {room.room_code}")
                    # Notify all players that game has started
                    await sio.emit('game_started', {
                        'room_code': room.room_code,
                        'start_url': room.start_url,
                        'end_url': room.end_url,
                        'start_title': room.start_title,
                        'end_title': room.end_title,
                        'game_state': room.game_state.value,
                        'message': 'GO! Race to the destination!'
                    }, room=room.room_code)
                    logger.info(f"DEBUG: game_started emit completed successfully")
                    
                except Exception as e:
                    logger.error(f"ERROR DEBUG: Error in countdown task: {e}")
                    import traceback
                    logger.error(f"ERROR DEBUG: Countdown traceback: {traceback.format_exc()}")
            
            # Start the countdown task in the background
            asyncio.create_task(start_game_after_countdown())
            
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
        try:
            room_code = data.get('room_code')
            player_name = data.get('player_name')
            page_url = data.get('page_url')
            page_title = data.get('page_title')
            
            if not room_code or not player_name or not page_url or not page_title:
                await sio.emit('error', {'message': 'Invalid progress data - missing required fields'}, room=sid)
                return
            
            room = room_manager.get_room(room_code)
            if not room:
                await sio.emit('error', {'message': 'Room not found'}, room=sid)
                return
            
            # Update player progress in room
            player = room.get_player_by_name(player_name)
            if player:
                # Check if this is a duplicate of the last navigation entry
                should_add_entry = True
                if player.navigation_history:
                    last_entry = player.navigation_history[-1]
                    if last_entry.page_url == page_url and last_entry.page_title == page_title:
                        should_add_entry = False  # Skip duplicate entry
                
                # Add navigation entry only if it's not a duplicate
                if should_add_entry:
                    navigation_entry = player.add_navigation_entry(page_url, page_title)
                else:
                    # Use the existing last entry for broadcasting
                    navigation_entry = player.navigation_history[-1]
                
                # Broadcast progress to other players in the room
                await sio.emit('player_progress', {
                    'player_name': player_name,
                    'current_page': page_title,  # Send title for display
                    'current_page_url': page_url,
                    'links_used': player.links_clicked,
                    'time_elapsed': navigation_entry.time_elapsed
                }, room=room_code, skip_sid=sid)
                
                # Also send updated progress to all players (excluding sender) for sync
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
