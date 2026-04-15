
"""
Network manager for WikiRace multiplayer functionality
"""

import socketio
import requests
import json
from PyQt6.QtCore import QObject, pyqtSignal, QThread, QTimer
from typing import Dict, Any, Optional
from src.logic.Player import Player

class NetworkManager(QObject):
    """Manages network connections and real-time communication with the multiplayer server"""
    
    # Signals for UI updates
    connected = pyqtSignal()
    disconnected = pyqtSignal()
    room_created = pyqtSignal(str, str)  # room_code, player_name
    room_joined = pyqtSignal(str, str, list)   # room_code, player_name, players_list
    player_joined = pyqtSignal(str, list)  # player_name, players_list
    player_left = pyqtSignal(str, list)  # player_name, players_list
    host_transferred = pyqtSignal(str, str)  # new_host_id, new_host_name
    room_deleted = pyqtSignal()          # room was deleted
    game_starting = pyqtSignal(dict)     # countdown_data
    game_started = pyqtSignal(dict)      # game_data
    game_ended = pyqtSignal(dict)        # game_results
    player_progress = pyqtSignal(str, str, int)  # player_name, current_page, links_used
    player_completed = pyqtSignal(str, float, int)  # player_name, completion_time, links_used
    error_occurred = pyqtSignal(str)     # error_message
    reconnecting = pyqtSignal(int)       # attempt_number
    reconnection_failed = pyqtSignal()   # max attempts reached
    reconnected = pyqtSignal()           # successfully reconnected
    game_config_updated = pyqtSignal(dict)  # config_data
    player_color_updated = pyqtSignal(str, str, str)  # player_name, color_hex, color_name
    kicked_for_inactivity = pyqtSignal(str)  # reason
    room_closed = pyqtSignal(str)  # reason
    player_disconnected = pyqtSignal(str, str)  # player_name, message
    player_reconnected = pyqtSignal(str, str)  # player_name, message
    
    def __init__(self, server_url: str = "http://127.0.0.1:8001"):  # Fixed to match server port
        super().__init__()
        self.server_url = server_url
        self.sio = socketio.Client()
        self.connected_to_server = False
        self.current_room = None
        self.player_name = None
        
        # Player management
        self.current_player: Optional[Player] = None
        self.room_players: Dict[str, Player] = {}  # player_name -> Player instance
        
        # Reconnection logic
        self.reconnection_enabled = True
        self.max_reconnection_attempts = 2  # Much faster - only 2 attempts
        self.reconnection_delay = 0.5  # Start with 0.5 seconds (much faster)
        self.max_reconnection_delay = 3.0  # Max 3 seconds (much faster)
        self.current_reconnection_attempts = 0
        
        # Heartbeat settings
        self.heartbeat_timer = None
        self.heartbeat_interval = 10000  # 10 seconds
        
        # Set up Socket.IO event handlers
        self._setup_socket_handlers()
    
    def create_player(self, socket_id: str, display_name: str, is_host: bool = False, connect_signals: bool = True) -> Player:
        """Create a new Player instance"""
        player = Player(socket_id, display_name, is_host)
        
        # Only connect signals for the current player, not for other players in the room
        if connect_signals:
            player.color_changed.connect(self._on_player_color_changed)
            player.progress_updated.connect(self._on_player_progress_updated)
            player.game_finished.connect(self._on_player_game_completed)
        
        return player
    
    def add_room_player(self, player: Player):
        """Add a player to the room players dictionary"""
        self.room_players[player.display_name] = player
    
    def remove_room_player(self, player_name: str) -> Optional[Player]:
        """Remove a player from the room players dictionary"""
        return self.room_players.pop(player_name, None)
    
    def get_room_player(self, player_name: str) -> Optional[Player]:
        """Get a player from the room players dictionary"""
        return self.room_players.get(player_name)
    
    def request_room_state(self, room_code: str):
        """Request current room state from server to refresh player list"""
        try:
            if self.connected_to_server and self.sio:
                # Emit a ping to the room to trigger a state refresh
                self.sio.emit('ping', {'room_code': room_code})
        except Exception as e:
            pass
    
    def _on_player_color_changed(self, color_hex: str, color_name: str):
        """Handle player color change from Player instance"""
        if self.current_player:
            # Send color update to server
            self.send_player_color_update(color_hex, color_name)
    
    def _on_player_progress_updated(self, current_page: str, links_used: int):
        """Handle player progress update from Player instance"""
        if self.current_player:
            # Send progress update to server
            self.send_player_progress_update(current_page, links_used)
    
    def _on_player_game_completed(self, completion_time: float, links_used: int):
        """Handle player game completion from Player instance"""
        if self.current_player:
            # Send completion update to server
            self.send_player_completion_update(completion_time, links_used)
    
    def _setup_socket_handlers(self):
        """Set up Socket.IO event handlers"""
        
        @self.sio.event
        def connect():
            self.connected_to_server = True
            self.connected.emit()
            
            # Start heartbeat
            self.start_heartbeat()
        
        @self.sio.event
        def disconnect():
            self.connected_to_server = False
            self.disconnected.emit()
            
            # Start reconnection process if enabled and we were in a room
            if self.reconnection_enabled and self.current_room:
                self._start_reconnection()
            else:
                pass
        
        @self.sio.event
        def connected(data):
            pass
        
        @self.sio.event
        def room_created(data):
            self.current_room = data['room_code']
            self._last_known_room = data['room_code']
            
            # Create current player instance
            players_data = data.get('players', [])
            if players_data:
                player_data = players_data[0]
                self.current_player = self.create_player(
                    player_data.get('socket_id', ''),
                    player_data.get('display_name', ''),
                    player_data.get('is_host', False)
                )
                self.player_name = self.current_player.display_name
                self.add_room_player(self.current_player)
            
            self.room_created.emit(data['room_code'], self.player_name or '')
        
        @self.sio.event
        def room_joined(data):
            self.current_room = data['room_code']
            self._last_known_room = data['room_code']
            
            # Create current player instance
            self.current_player = self.create_player(
                data.get('socket_id', ''),
                data.get('display_name', ''),
                data.get('is_host', False)
            )
            self.player_name = self.current_player.display_name
            self.add_room_player(self.current_player)
            
            # Create Player instances for all OTHER players in room
            # NOTE: Do not set current player's color from room_joined event
            # The current player manages their own color through UI interactions
            players_data = data.get('players', [])
            for player_data in players_data:
                player_name = player_data.get('display_name', '')
                if player_name != self.player_name:
                    # Create Player instance for other players only (without signal connections)
                    room_player = self.create_player(
                        player_data.get('socket_id', ''),
                        player_name,
                        player_data.get('is_host', False),
                        connect_signals=False
                    )
                    # Set player color if available
                    if player_data.get('player_color'):
                        room_player.update_color(
                            player_data.get('player_color'),
                            player_data.get('color_name')
                        )
                    self.add_room_player(room_player)
            
            self.room_joined.emit(data['room_code'], data['display_name'], data['players'])
        
        @self.sio.event
        def player_joined(data):
            # Create Player instance for new player (without signal connections)
            new_player = self.create_player(
                data.get('socket_id', ''),
                data.get('display_name', ''),
                data.get('is_host', False),
                connect_signals=False
            )
            self.add_room_player(new_player)
            self.player_joined.emit(data['display_name'], data.get('players', []))
        
        @self.sio.event
        def player_left(data):
            # Remove Player instance
            self.remove_room_player(data['player_name'])
            self.player_left.emit(data['player_name'], data.get('players', []))
        
        @self.sio.event
        def error(data):
            self.error_occurred.emit(data.get('message', 'Unknown error'))
        
        @self.sio.event
        def host_transferred(data):
            new_host_id = data.get('new_host_id', '')
            new_host_name = data.get('new_host_name', '')
            self.host_transferred.emit(new_host_id, new_host_name)
        
        @self.sio.event
        def game_starting(data):
            self.game_starting.emit(data)
        
        @self.sio.event
        def game_started(data):
            self.game_started.emit(data)
        
        @self.sio.event
        def game_ended(data):
            self.game_ended.emit(data)
        
        @self.sio.event
        def player_progress(data):
            player_name = data.get('player_name', '')
            current_page = data.get('current_page', '')
            links_used = data.get('links_used', 0)
            self.player_progress.emit(player_name, current_page, links_used)
        
        @self.sio.event
        def player_completed(data):
            player_name = data.get('player_name', '')
            completion_time = data.get('completion_time', 0.0)
            links_used = data.get('links_used', 0)
            self.player_completed.emit(player_name, completion_time, links_used)
        
        @self.sio.event
        def game_config_updated(data):
            self.game_config_updated.emit(data)
        
        @self.sio.event
        def player_color_updated(data):
            player_name = data.get('player_name', '')
            color_hex = data.get('color_hex', '')
            color_name = data.get('color_name', '')
            
            # Always emit the signal, regardless of player instance
            self.player_color_updated.emit(player_name, color_hex, color_name)
        
        @self.sio.event
        def kicked_for_inactivity(data):
            reason = data.get('reason', 'timeout')
            self.kicked_for_inactivity.emit(reason)
        
        @self.sio.event
        def room_closed(data):
            reason = data.get('reason', 'timeout')
            self.room_closed.emit(reason)
        
        @self.sio.event
        def player_disconnected(data):
            player_name = data.get('player_name', '')
            message = data.get('message', '')
            self.player_disconnected.emit(player_name, message)
        
        @self.sio.event
        def player_reconnected(data):
            player_name = data.get('player_name', '')
            message = data.get('message', '')
            self.player_reconnected.emit(player_name, message)
        
        @self.sio.event
        def players_removed(data):
            removed_players = data.get('removed_players', [])
            message = data.get('message', '')
            players = data.get('players', [])
            
            # Update our local player list
            if players:
                self.players_in_room = [p['display_name'] for p in players]
            
            # Emit signal for UI update
            self.player_left.emit(f"{', '.join(removed_players)} (removed)", players)
            
            # Show notification
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(None, "Players Removed", f"{message}")
        
        @self.sio.event
        def room_progress_sync(data):
            # This could be used for additional synchronization if needed
            pass
        
        @self.sio.event
        def pong(data):
            """Handle pong response from server"""
            # Heartbeat successful, no action needed
    
    def connect_to_server(self) -> bool:
        """Connect to the multiplayer server"""
        try:
            if not self.connected_to_server or not self.sio.connected:
                # Disconnect any existing connection first
                try:
                    if hasattr(self.sio, 'connected') and self.sio.connected:
                        self.sio.disconnect()
                        import time
                        time.sleep(0.1)  # Brief pause after disconnect
                except Exception:
                    pass
                
                # Connect with longer timeout for stability
                self.sio.connect(self.server_url, wait_timeout=30)
                
                import time
                max_wait = 3.0  # Maximum wait time in seconds
                wait_interval = 0.1  # Check every 100ms
                waited = 0.0
                
                while waited < max_wait:
                    if self.connected_to_server and self.sio.connected:
                        return True
                    time.sleep(wait_interval)
                    waited += wait_interval
                
                return False
            return True
        except Exception as e:
            self.error_occurred.emit(f"Failed to connect to server: {e}")
            return False
    
    def disconnect_from_server(self):
        """Disconnect from the multiplayer server with proper cleanup"""
        try:
            
            # Disable reconnection when manually disconnecting
            self.reconnection_enabled = False
            
            # Stop heartbeat first
            self.stop_heartbeat()
            
            # Clear reconnection state
            self.current_reconnection_attempts = 0
            
            if self.connected_to_server:
                try:
                    if hasattr(self.sio, 'connected') and self.sio.connected:
                        
                        # Use a timer to force disconnect if it takes too long
                        from PyQt6.QtCore import QTimer
                        disconnect_timer = QTimer()
                        disconnect_timer.timeout.connect(lambda: self._force_disconnect_cleanup())
                        disconnect_timer.setSingleShot(True)
                        disconnect_timer.start(2000)  # 2 second timeout
                        
                        # Attempt normal disconnect
                        self.sio.disconnect()
                        
                        # Clean up timer after successful disconnect
                        disconnect_timer.stop()
                        
                except Exception as disconnect_error:
                    # Force cleanup if normal disconnect fails
                    self._force_disconnect_cleanup()
            
            # Reset connection state immediately
            self.connected_to_server = False
            
            # Clear room state
            self.current_room = None
            self.player_name = None
            
            # Clear player data
            self.current_player = None
            self.room_players.clear()
            
            
        except Exception as e:
            import traceback
            # Force cleanup on error
            self._force_disconnect_cleanup()
    
    def _force_disconnect_cleanup(self):
        """Force cleanup of connection state if normal disconnect fails"""
        try:
            
            # Force reset all connection states
            self.connected_to_server = False
            self.current_room = None
            self.player_name = None
            self.current_player = None
            self.room_players.clear()
            self.reconnection_enabled = False
            self.current_reconnection_attempts = 0
            
            # Stop any remaining timers
            self.stop_heartbeat()
            
            
        except Exception as e:
            pass
    
    def cleanup_network_resources(self):
        """Clean up all network resources and prevent memory leaks"""
        try:
            
            # Stop all timers
            self.stop_heartbeat()
            
            # Disable reconnection
            self.reconnection_enabled = False
            
            # Disconnect from server
            self.disconnect_from_server()
            
            # Clear all references
            self.sio = None
            self.current_player = None
            self.room_players.clear()
            
            
        except Exception as e:
            import traceback
    
    def start_heartbeat(self):
        """Start the heartbeat timer"""
        if self.heartbeat_timer:
            self.heartbeat_timer.stop()
        
        self.heartbeat_timer = QTimer()
        self.heartbeat_timer.timeout.connect(self.send_heartbeat)
        self.heartbeat_timer.start(self.heartbeat_interval)
    
    def stop_heartbeat(self):
        """Stop the heartbeat timer"""
        if self.heartbeat_timer:
            self.heartbeat_timer.stop()
            self.heartbeat_timer = None
    
    def send_heartbeat(self):
        """Send heartbeat ping to server"""
        if self.connected_to_server and self.sio.connected:
            try:
                import time
                self.sio.emit('ping', {'timestamp': time.time()})
            except Exception as e:
                # If heartbeat fails, try to reconnect
                if self.reconnection_enabled:
                    self._start_reconnection()
    
    def _start_reconnection(self):
        """Start the reconnection process"""
        if not self.reconnection_enabled:
            return
        
        self.current_reconnection_attempts = 0
        self.reconnection_delay = 0.5  # Reset delay (much faster)
        self._schedule_reconnection()
    
    def _schedule_reconnection(self):
        """Schedule the next reconnection attempt"""
        if self.current_reconnection_attempts >= self.max_reconnection_attempts:
            self.reconnection_failed.emit()
            return
        
        self.current_reconnection_attempts += 1
        
        # Emit reconnecting signal
        self.reconnecting.emit(self.current_reconnection_attempts)
        
        # Schedule next attempt using QTimer.singleShot to avoid threading issues
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(int(self.reconnection_delay * 1000), self._attempt_reconnection)
        
        # Exponential backoff with jitter (less aggressive)
        self.reconnection_delay = min(self.reconnection_delay * 1.5, self.max_reconnection_delay)
    
    def _attempt_reconnection(self):
        """Attempt to reconnect to the server with improved timeout handling"""
        try:
            
            # Cleanup any existing connection
            try:
                if hasattr(self.sio, 'connected') and self.sio.connected:
                    self.sio.disconnect()
                    # Give time for cleanup
                    import time
                    time.sleep(0.1)
            except Exception as cleanup_error:
                pass
            
            # Try to reconnect with timeout
            try:
                self.sio.connect(self.server_url, wait_timeout=10)  # Shorter timeout for faster failure detection
                
                # Wait for connection to establish with timeout
                max_wait = 2.0  # Maximum wait time in seconds
                wait_interval = 0.1  # Check every 100ms
                waited = 0.0
                
                while waited < max_wait:
                    if (hasattr(self.sio, 'connected') and self.sio.connected and 
                        self.connected_to_server and self._is_connection_healthy()):
                        self.current_reconnection_attempts = 0
                        self.reconnection_delay = 0.5  # Reset to much faster initial delay
                        self.reconnected.emit()
                        
                        # Restart heartbeat
                        self.start_heartbeat()
                        
                        # Try to rejoin the room if we were in one
                        if self.current_room and self.player_name:
                            # Use a small delay to ensure connection is fully established
                            from PyQt6.QtCore import QTimer
                            QTimer.singleShot(500, lambda: self.join_room(self.current_room, self.player_name))
                        return
                    
                    time.sleep(wait_interval)
                    waited += wait_interval
                
                # Connection failed, schedule next attempt
                self._schedule_reconnection()
                
            except Exception as connect_error:
                self._schedule_reconnection()
                
        except Exception as e:
            import traceback
            # Schedule next attempt
            self._schedule_reconnection()
    
    def enable_reconnection(self):
        """Enable automatic reconnection"""
        self.reconnection_enabled = True
    
    def disable_reconnection(self):
        """Disable automatic reconnection"""
        self.reconnection_enabled = False
    
    def create_room(self, player_name: str) -> Optional[str]:
        """Create a new multiplayer room"""
        try:
            if not self.connected_to_server:
                if not self.connect_to_server():
                    return None
            
            self.player_name = player_name
            self.sio.emit('create_room', {'display_name': player_name})
            return "Creating room..."  # Will be updated via socket event
            
        except Exception as e:
            self.error_occurred.emit(f"Failed to create room: {e}")
            return None
    
    def join_room(self, room_code: str, player_name: str) -> bool:
        """Join an existing multiplayer room"""
        try:
            if not self.connected_to_server:
                if not self.connect_to_server():
                    return False
            
            self.player_name = player_name
            self.sio.emit('join_room', {
                'room_code': room_code.upper(),
                'display_name': player_name
            })
            return True
            
        except Exception as e:
            self.error_occurred.emit(f"Failed to join room: {e}")
            return False
    
    def check_room_exists(self, room_code: str) -> bool:
        """Check if a room with the given code exists"""
        try:
            if not self.connected_to_server:
                if not self.connect_to_server():
                    # If we can't connect to server, assume room exists and let join_room handle validation
                    return True
            
            # Use REST API to check if room exists
            response = requests.get(f"{self.server_url}/api/rooms/{room_code.upper()}")
            return response.status_code == 200
            
        except Exception as e:
            # If check fails, assume room exists and let join_room handle the error
            return True
    
    def leave_room(self):
        """Leave the current room but stay connected to server"""
        try:
            
            if self.connected_to_server and self.current_room:
                room_code = self.current_room
                
                # STRATEGY 1: Try Socket.IO event first
                socketio_success = False
                try:
                    
                    # Test connection with a ping first
                    try:
                        self.sio.emit('ping')
                    except Exception as ping_error:
                        pass
                    
                    # SIMPLE FIX: Just try Socket.IO once
                    self.sio.emit('leave_room')
                    socketio_success = True
                except Exception as emit_error:
                    socketio_success = False
                
                # SIMPLE FIX: Use REST API as primary method (more reliable)
                try:
                    response = requests.post(
                        f"{self.server_url}/api/rooms/{room_code}/leave",
                        json={"player_name": self.player_name},
                        timeout=10
                    )
                    if response.status_code == 200:
                        pass
                    else:
                        pass
                except Exception as rest_error:
                    pass
                
                # SIMPLE FIX: Just wait a bit and clear local state
                from PyQt6.QtCore import QTimer
                QTimer.singleShot(2000, lambda: self._complete_leave_room(room_code))
                
                # DO NOT call disconnect_from_server() here
                
            else:
                pass
        except Exception as e:
            import traceback
    
    def _start_leave_room_retry(self, room_code: str, attempt: int = 1):
        """Start retry mechanism for leave_room with exponential backoff"""
        try:
            max_attempts = 3
            base_delay = 500  # 500ms base delay
            
            if attempt > max_attempts:
                self._complete_leave_room(room_code)
                return
            
            delay = base_delay * (2 ** (attempt - 1))  # Exponential backoff: 500ms, 1000ms, 2000ms
            
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(delay, lambda: self._retry_leave_room(room_code, attempt))
            
        except Exception as e:
            self._complete_leave_room(room_code)
    
    def _retry_leave_room(self, room_code: str, attempt: int):
        """Retry leave_room with different strategies"""
        try:
            
            # Strategy 1: Try REST API again
            try:
                response = requests.post(
                    f"{self.server_url}/api/rooms/{room_code}/leave",
                    json={"player_name": self.player_name},
                    timeout=10
                )
                if response.status_code == 200:
                    self._complete_leave_room(room_code)
                    return
                else:
                    pass
            except Exception as e:
                pass
            
            # Strategy 2: Try Socket.IO again
            try:
                self.sio.emit('leave_room')
            except Exception as e:
                pass
            
            # Strategy 3: Nuclear option - force disconnect/reconnect on final attempt
            if attempt == 3:
                try:
                    # Force disconnect
                    if hasattr(self.sio, 'disconnect'):
                        self.sio.disconnect()
                    # Force reconnect
                    self.connect_to_server()
                    # Try REST API one more time
                    response = requests.post(
                        f"{self.server_url}/api/rooms/{room_code}/leave",
                        json={"player_name": self.player_name},
                        timeout=10
                    )
                    if response.status_code == 200:
                        self._complete_leave_room(room_code)
                        return
                except Exception as nuclear_error:
                    pass
            
            # Schedule next retry
            self._start_leave_room_retry(room_code, attempt + 1)
            
        except Exception as e:
            self._complete_leave_room(room_code)
    
    def _complete_leave_room(self, room_code: str):
        """Complete the leave room process after server has had time to process the event"""
        try:
            self.current_room = None
        except Exception as e:
            pass
    
    def get_server_status(self) -> Dict[str, Any]:
        """Get server status via REST API"""
        try:
            # First check basic health
            health_response = requests.get(f"{self.server_url}/health", timeout=10)
            if health_response.status_code != 200:
                return {"error": f"Server returned status {health_response.status_code}"}
            
            # Get detailed stats including room count
            stats_response = requests.get(f"{self.server_url}/api/stats", timeout=10)
            if stats_response.status_code == 200:
                stats_data = stats_response.json()
                room_stats = stats_data.get('room_stats', {})
                return {
                    "status": "healthy",
                    "rooms_active": room_stats.get('total_rooms', 0),
                    "total_players": room_stats.get('total_players', 0)
                }
            else:
                # Fallback to basic health check
                return health_response.json()
        except Exception as e:
            return {"error": f"Failed to connect to server: {e}"}
    
    def create_room_via_api(self, player_name: str) -> Optional[Dict[str, Any]]:
        """Create a room via REST API (for testing)"""
        try:
            response = requests.post(
                f"{self.server_url}/api/rooms",
                json={"display_name": player_name},
                timeout=10
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            return None
    
    def send_player_progress(self, page_url: str, page_title: str):
        """Send detailed player progress update to server"""
        try:
            # Enhanced connection check
            if not self._is_connection_healthy():
                return
            
            self.sio.emit('player_progress', {
                'room_code': self.current_room,
                'player_name': self.player_name,
                'page_url': page_url,
                'page_title': page_title
            })
        except Exception as e:
            import traceback
    
    def send_game_completion(self, completion_time: float, links_used: int):
        """Send game completion to server"""
        try:
            room_code = self.current_room
            if not room_code and hasattr(self, '_last_known_room'):
                room_code = self._last_known_room
            
            if self.connected_to_server and room_code and self.sio.connected:
                self.sio.emit('game_complete', {
                    'room_code': room_code,
                    'player_name': self.player_name,
                    'completion_time': completion_time,
                    'links_used': links_used
                })
            else:
                pass
        except Exception as e:
            pass
    
    def send_game_config(self, start_category: str, end_category: str, 
                        custom_start: str = None, custom_end: str = None):
        """Send game configuration update to server"""
        try:
            if self._is_connection_healthy():
                self.sio.emit('select_categories', {
                    'start_category': start_category,
                    'end_category': end_category,
                    'custom_start': custom_start,
                    'custom_end': custom_end
                })
            else:
                pass
        except Exception as e:
            pass
    
    def send_player_color(self, color_hex: str, color_name: str):
        """Send player color update to server"""
        try:
            if self._is_connection_healthy():
                self.sio.emit('player_color_update', {
                    'room_code': self.current_room,
                    'player_name': self.player_name,
                    'color_hex': color_hex,
                    'color_name': color_name
                })
            else:
                pass
        except Exception as e:
            import traceback
    
    def _is_connection_healthy(self) -> bool:
        """Check if the connection is healthy for sending messages"""
        try:
            # Basic connection checks
            if not self.connected_to_server:
                return False
            
            if not self.current_room:
                return False
            
            # Socket.IO connection checks
            if not hasattr(self.sio, 'connected') or not self.sio.connected:
                return False
            
            # Engine.IO state checks
            if hasattr(self.sio, 'eio'):
                if self.sio.eio.state != 'connected':
                    return False
                
                # Additional transport checks
                if hasattr(self.sio.eio, 'transport') and self.sio.eio.transport:
                    if hasattr(self.sio.eio.transport, 'state') and self.sio.eio.transport.state != 'connected':
                        return False
            
            # Check if we're in the middle of reconnection
            if self.current_reconnection_attempts > 0:
                return False
            
            return True
            
        except Exception as e:
            return False
    
    def send_player_color_update(self, color_hex: str, color_name: str):
        """Send player color update to server (new method using Player instances)"""
        if not self.connected_to_server or not self.current_room:
            return
        
        try:
            self.sio.emit('player_color_update', {
                'room_code': self.current_room,
                'player_name': self.player_name,
                'color_hex': color_hex,
                'color_name': color_name
            })
        except Exception as e:
            pass
    
    def send_player_progress_update(self, current_page: str, links_used: int):
        """Send player progress update to server"""
        if not self.connected_to_server or not self.current_room:
            return
        
        try:
            self.sio.emit('player_progress', {
                'room_code': self.current_room,
                'player_name': self.player_name,
                'page_url': current_page,  # Use page_url for server compatibility
                'page_title': current_page  # Use page_title for server compatibility
            })
        except Exception as e:
            pass
    
    def send_player_completion_update(self, completion_time: float, links_used: int):
        """Send player completion update to server"""
        if not self.connected_to_server or not self.current_room:
            return
        
        try:
            self.sio.emit('player_finished', {
                'room_code': self.current_room,
                'player_name': self.player_name,
                'completion_time': completion_time,
                'links_used': links_used
            })
        except Exception as e:
            pass
    
    async def get_room_info(self, room_code: str) -> Optional[Dict[str, Any]]:
        """Get current room information including player list"""
        if not self.server_url or not room_code:
            return None
        
        try:
            url = f"{self.server_url}/api/rooms/{room_code}"
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        return None
        except Exception as e:
            return None
    
    def auto_discover_servers(self, possible_servers=None) -> list:
        """Try to automatically discover available WikiRace servers"""
        import requests
        import socket
        import time
        
        if possible_servers is None:
            possible_servers = [
                "wikirace.duckdns.org:8001",  # Your dynamic DNS domain (try first)
                "127.0.0.1:8001",  # Localhost
                "localhost:8001",  # Localhost alternative
                "71.237.25.28:8001",  # Your external IP
            ]
        
        working_servers = []
        
        
        for server in possible_servers:
            try:
                host, port = server.split(':')
                port = int(port)
                
                # Test connection with short timeout
                response = requests.get(f"http://{host}:{port}/health", timeout=3)
                if response.status_code == 200:
                    working_servers.append({
                        'address': server,
                        'url': f"http://{host}:{port}",
                        'host': host,
                        'port': port,
                        'status': 'healthy'
                    })
                    
                    # If this is the DuckDNS server, stop trying others for faster connection
                    if server == "wikirace.duckdns.org:8001":
                        break
                else:
                    pass
            except requests.exceptions.Timeout:
                pass
            except requests.exceptions.ConnectionError:
                pass
            except Exception as e:
                pass
        
        if working_servers:
            pass
        else:
            pass
        
        return working_servers
    
    def auto_connect_to_best_server(self, possible_servers=None) -> bool:
        """Automatically connect to the best available server"""
        working_servers = self.auto_discover_servers(possible_servers)
        
        if not working_servers:
            return False
        
        # Try to connect to the first working server
        best_server = working_servers[0]
        
        # Update server URL and try to connect
        self.server_url = best_server['url']
        return self.connect_to_server()
    
    def test_server_connection(self, server_address: str) -> bool:
        """Test if a specific server is reachable"""
        try:
            import requests
            if ':' not in server_address:
                server_address += ':8001'  # Default port
            
            host, port = server_address.split(':')
            response = requests.get(f"http://{host}:{port}/health", timeout=3)
            return response.status_code == 200
        except Exception:
            return False


# Legacy Network class for backward compatibility
class Network:
    def __init__(self):
        self.network_manager = NetworkManager()
    
    def hostGame(self):
        # Legacy method - now uses NetworkManager
        return self.network_manager.create_room("Player")
    
    def joinGame(self, host):
        # Legacy method - now uses NetworkManager  
        return self.network_manager.join_room(host, "Player")
