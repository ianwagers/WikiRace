
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
    
    def __init__(self, server_url: str = "http://127.0.0.1:8000"):  # Fixed to match server port
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
        self.heartbeat_interval = 5000  # 5 seconds
        
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
    
    def _on_player_color_changed(self, color_hex: str, color_name: str):
        """Handle player color change from Player instance"""
        if self.current_player:
            print(f"🎨 Player {self.current_player.display_name} color changed: {color_name} ({color_hex})")
            # Send color update to server
            self.send_player_color_update(color_hex, color_name)
    
    def _on_player_progress_updated(self, current_page: str, links_used: int):
        """Handle player progress update from Player instance"""
        if self.current_player:
            print(f"🔄 Player {self.current_player.display_name} progress: {current_page} ({links_used} links)")
            # Send progress update to server
            self.send_player_progress_update(current_page, links_used)
    
    def _on_player_game_completed(self, completion_time: float, links_used: int):
        """Handle player game completion from Player instance"""
        if self.current_player:
            print(f"🏁 Player {self.current_player.display_name} completed game: {completion_time}s, {links_used} links")
            # Send completion update to server
            self.send_player_completion_update(completion_time, links_used)
    
    def _setup_socket_handlers(self):
        """Set up Socket.IO event handlers"""
        
        @self.sio.event
        def connect():
            print("✅ Connected to multiplayer server")
            self.connected_to_server = True
            self.connected.emit()
            
            # Start heartbeat
            self.start_heartbeat()
        
        @self.sio.event
        def disconnect():
            print("❌ DEBUG: Socket disconnected from multiplayer server")
            print(f"❌ DEBUG: Disconnect - was in room: {self.current_room}")
            print(f"❌ DEBUG: Disconnect - reconnection enabled: {self.reconnection_enabled}")
            self.connected_to_server = False
            self.disconnected.emit()
            
            # Start reconnection process if enabled and we were in a room
            if self.reconnection_enabled and self.current_room:
                print("🔄 DEBUG: Starting reconnection process...")
                self._start_reconnection()
            else:
                print("⏸️ DEBUG: Not starting reconnection (disabled or no room)")
        
        @self.sio.event
        def connected(data):
            print(f"Server connection confirmed: {data}")
        
        @self.sio.event
        def room_created(data):
            print(f"Room created: {data}")
            self.current_room = data['room_code']
            
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
            print(f"Room joined: {data}")
            self.current_room = data['room_code']
            
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
            print(f"Player joined: {data}")
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
            print(f"Player left: {data}")
            # Remove Player instance
            self.remove_room_player(data['player_name'])
            self.player_left.emit(data['player_name'], data.get('players', []))
        
        @self.sio.event
        def error(data):
            print(f"Server error: {data}")
            self.error_occurred.emit(data.get('message', 'Unknown error'))
        
        @self.sio.event
        def host_transferred(data):
            print(f"Host transferred: {data}")
            new_host_id = data.get('new_host_id', '')
            new_host_name = data.get('new_host_name', '')
            self.host_transferred.emit(new_host_id, new_host_name)
        
        @self.sio.event
        def game_starting(data):
            print(f"🎬 DEBUG: Received game_starting socket event: {data}")
            self.game_starting.emit(data)
            print(f"🎬 DEBUG: Emitted game_starting signal to UI")
        
        @self.sio.event
        def game_started(data):
            print(f"🎮 DEBUG: Received game_started socket event: {data}")
            self.game_started.emit(data)
            print(f"🎮 DEBUG: Emitted game_started signal to UI")
        
        @self.sio.event
        def game_ended(data):
            print(f"Game ended: {data}")
            self.game_ended.emit(data)
        
        @self.sio.event
        def player_progress(data):
            print(f"📊 DEBUG: Network received player_progress: {data}")
            player_name = data.get('player_name', '')
            current_page = data.get('current_page', '')
            links_used = data.get('links_used', 0)
            print(f"📊 DEBUG: Parsed - player: {player_name}, page: {current_page}, links: {links_used}")
            print(f"📊 DEBUG: Emitting player_progress signal...")
            self.player_progress.emit(player_name, current_page, links_used)
            print(f"📊 DEBUG: Signal emitted successfully")
        
        @self.sio.event
        def player_completed(data):
            print(f"Player completed: {data}")
            player_name = data.get('player_name', '')
            completion_time = data.get('completion_time', 0.0)
            links_used = data.get('links_used', 0)
            self.player_completed.emit(player_name, completion_time, links_used)
        
        @self.sio.event
        def game_config_updated(data):
            print(f"Game config updated: {data}")
            self.game_config_updated.emit(data)
        
        @self.sio.event
        def player_color_updated(data):
            print(f"🎨 RECEIVED: Player color updated: {data}")
            player_name = data.get('player_name', '')
            color_hex = data.get('color_hex', '')
            color_name = data.get('color_name', '')
            
            # Always emit the signal, regardless of player instance
            self.player_color_updated.emit(player_name, color_hex, color_name)
        
        @self.sio.event
        def room_progress_sync(data):
            print(f"Room progress sync: {data}")
            # This could be used for additional synchronization if needed
            pass
        
        @self.sio.event
        def pong(data):
            """Handle pong response from server"""
            print(f"Pong received: {data}")
            # Heartbeat successful, no action needed
    
    def connect_to_server(self) -> bool:
        """Connect to the multiplayer server"""
        try:
            if not self.connected_to_server or not self.sio.connected:
                print(f"🔌 Connecting to server at {self.server_url}")
                # Disconnect any existing connection first
                try:
                    if hasattr(self.sio, 'connected') and self.sio.connected:
                        self.sio.disconnect()
                        import time
                        time.sleep(0.1)  # Brief pause after disconnect
                except:
                    pass
                
                # Connect with longer timeout for stability
                self.sio.connect(self.server_url, wait_timeout=15)
                # Wait a moment for connection to establish
                import time
                time.sleep(0.5)
                return self.sio.connected
            return True
        except Exception as e:
            print(f"❌ Failed to connect to server: {e}")
            self.error_occurred.emit(f"Failed to connect to server: {e}")
            return False
    
    def disconnect_from_server(self):
        """Disconnect from the multiplayer server"""
        try:
            # Disable reconnection when manually disconnecting
            self.reconnection_enabled = False
            
            # Stop heartbeat
            self.stop_heartbeat()
            
            if self.connected_to_server:
                self.sio.disconnect()
        except Exception as e:
            print(f"Error disconnecting: {e}")
    
    def start_heartbeat(self):
        """Start the heartbeat timer"""
        if self.heartbeat_timer:
            self.heartbeat_timer.stop()
        
        self.heartbeat_timer = QTimer()
        self.heartbeat_timer.timeout.connect(self.send_heartbeat)
        self.heartbeat_timer.start(self.heartbeat_interval)
        print("💓 Heartbeat started")
    
    def stop_heartbeat(self):
        """Stop the heartbeat timer"""
        if self.heartbeat_timer:
            self.heartbeat_timer.stop()
            self.heartbeat_timer = None
        print("💓 Heartbeat stopped")
    
    def send_heartbeat(self):
        """Send heartbeat ping to server"""
        if self.connected_to_server and self.sio.connected:
            try:
                import time
                self.sio.emit('ping', {'timestamp': time.time()})
                print("💓 Heartbeat sent")
            except Exception as e:
                print(f"💓 Heartbeat failed: {e}")
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
            print(f"❌ Max reconnection attempts ({self.max_reconnection_attempts}) reached")
            self.reconnection_failed.emit()
            return
        
        self.current_reconnection_attempts += 1
        print(f"🔄 Scheduling reconnection attempt {self.current_reconnection_attempts}/{self.max_reconnection_attempts} in {self.reconnection_delay}s")
        
        # Emit reconnecting signal
        self.reconnecting.emit(self.current_reconnection_attempts)
        
        # Schedule next attempt using QTimer.singleShot to avoid threading issues
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(int(self.reconnection_delay * 1000), self._attempt_reconnection)
        
        # Exponential backoff with jitter (less aggressive)
        self.reconnection_delay = min(self.reconnection_delay * 1.5, self.max_reconnection_delay)
    
    def _attempt_reconnection(self):
        """Attempt to reconnect to the server"""
        try:
            print(f"🔄 Attempting reconnection #{self.current_reconnection_attempts}...")
            
            # Cleanup any existing connection
            try:
                if self.sio.connected:
                    self.sio.disconnect()
            except:
                pass
            
            # Try to reconnect with timeout
            self.sio.connect(self.server_url, wait_timeout=10)
            
            # Wait a moment for connection to establish
            import time
            time.sleep(0.5)
            
            if self.sio.connected and self.connected_to_server:
                print("✅ Reconnection successful!")
                self.current_reconnection_attempts = 0
                self.reconnection_delay = 0.5  # Reset to much faster initial delay
                self.reconnected.emit()
                
                # Try to rejoin the room if we were in one
                if self.current_room and self.player_name:
                    print(f"🚪 Attempting to rejoin room {self.current_room}")
                    self.join_room(self.current_room, self.player_name)
            else:
                # Connection failed, schedule next attempt
                self._schedule_reconnection()
                
        except Exception as e:
            print(f"❌ Reconnection attempt {self.current_reconnection_attempts} failed: {e}")
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
            print(f"🎮 Creating room for player: {player_name}")
            self.sio.emit('create_room', {'display_name': player_name})
            return "Creating room..."  # Will be updated via socket event
            
        except Exception as e:
            print(f"❌ Failed to create room: {e}")
            self.error_occurred.emit(f"Failed to create room: {e}")
            return None
    
    def join_room(self, room_code: str, player_name: str) -> bool:
        """Join an existing multiplayer room"""
        try:
            if not self.connected_to_server:
                if not self.connect_to_server():
                    return False
            
            self.player_name = player_name
            print(f"🚪 Joining room {room_code} as {player_name}")
            self.sio.emit('join_room', {
                'room_code': room_code.upper(),
                'display_name': player_name
            })
            return True
            
        except Exception as e:
            print(f"❌ Failed to join room: {e}")
            self.error_occurred.emit(f"Failed to join room: {e}")
            return False
    
    def check_room_exists(self, room_code: str) -> bool:
        """Check if a room with the given code exists"""
        try:
            if not self.connected_to_server:
                if not self.connect_to_server():
                    # If we can't connect to server, assume room exists and let join_room handle validation
                    print(f"⚠️ Cannot connect to server for room validation, assuming room exists")
                    return True
            
            # Use REST API to check if room exists
            response = requests.get(f"{self.server_url}/api/rooms/{room_code.upper()}")
            return response.status_code == 200
            
        except Exception as e:
            print(f"❌ Failed to check room existence: {e}")
            # If check fails, assume room exists and let join_room handle the error
            return True
    
    def leave_room(self):
        """Leave the current room"""
        try:
            if self.connected_to_server and self.current_room:
                self.sio.emit('leave_room')
                self.current_room = None
        except Exception as e:
            print(f"❌ Failed to leave room: {e}")
    
    def get_server_status(self) -> Dict[str, Any]:
        """Get server status via REST API"""
        try:
            # First check basic health
            health_response = requests.get(f"{self.server_url}/health", timeout=5)
            if health_response.status_code != 200:
                return {"error": f"Server returned status {health_response.status_code}"}
            
            # Get detailed stats including room count
            stats_response = requests.get(f"{self.server_url}/api/stats", timeout=5)
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
                timeout=5
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"❌ API room creation failed: {e}")
            return None
    
    def send_player_progress(self, page_url: str, page_title: str):
        """Send detailed player progress update to server"""
        try:
            # Enhanced connection check
            if not self._is_connection_healthy():
                print(f"⚠️ Cannot send progress - connection unhealthy")
                print(f"   - connected_to_server: {self.connected_to_server}")
                print(f"   - current_room: {self.current_room}")
                print(f"   - sio.connected: {getattr(self.sio, 'connected', 'N/A')}")
                return
            
            self.sio.emit('player_progress', {
                'room_code': self.current_room,
                'player_name': self.player_name,
                'page_url': page_url,
                'page_title': page_title
            })
            print(f"📊 Sent navigation: {page_title} ({page_url})")
        except Exception as e:
            print(f"❌ Failed to send progress: {e}")
            import traceback
            print(f"❌ Progress send traceback: {traceback.format_exc()}")
    
    def send_game_completion(self, completion_time: float, links_used: int):
        """Send game completion to server"""
        try:
            if self.connected_to_server and self.current_room and self.sio.connected:
                self.sio.emit('game_complete', {
                    'room_code': self.current_room,
                    'player_name': self.player_name,
                    'completion_time': completion_time,
                    'links_used': links_used
                })
                print(f"🏆 Sent completion: {completion_time:.2f}s, {links_used} links")
            else:
                print(f"⚠️ Cannot send completion - not connected (connected: {self.connected_to_server}, room: {self.current_room})")
        except Exception as e:
            print(f"❌ Failed to send completion: {e}")
    
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
                print(f"⚙️ Sent game config: {start_category} -> {end_category}")
            else:
                print(f"⚠️ Cannot send config - connection unhealthy")
        except Exception as e:
            print(f"❌ Failed to send game config: {e}")
    
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
                print(f"🎨 Sent color update: {color_name} ({color_hex})")
            else:
                print(f"⚠️ Cannot send color update - connection unhealthy")
        except Exception as e:
            print(f"❌ Failed to send color update: {e}")
            import traceback
            print(f"❌ Color update send traceback: {traceback.format_exc()}")
    
    def _is_connection_healthy(self) -> bool:
        """Check if the connection is healthy for sending messages"""
        try:
            return (self.connected_to_server and 
                   self.current_room and 
                   hasattr(self.sio, 'connected') and 
                   self.sio.connected and
                   hasattr(self.sio, 'eio') and
                   self.sio.eio.state == 'connected')
        except:
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
            print(f"🎨 Sent color update: {color_name} ({color_hex})")
        except Exception as e:
            print(f"❌ Error sending color update: {e}")
    
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
            print(f"🔄 Sent progress update: {current_page} ({links_used} links)")
        except Exception as e:
            print(f"❌ Error sending progress update: {e}")
    
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
            print(f"🏁 Sent completion update: {completion_time}s, {links_used} links")
        except Exception as e:
            print(f"❌ Error sending completion update: {e}")


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
