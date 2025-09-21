
"""
Network manager for WikiRace multiplayer functionality
"""

import socketio
import requests
import json
from PyQt6.QtCore import QObject, pyqtSignal, QThread
from typing import Dict, Any, Optional

class NetworkManager(QObject):
    """Manages network connections and real-time communication with the multiplayer server"""
    
    # Signals for UI updates
    connected = pyqtSignal()
    disconnected = pyqtSignal()
    room_created = pyqtSignal(str, str)  # room_code, player_name
    room_joined = pyqtSignal(str, str)   # room_code, player_name
    player_joined = pyqtSignal(str)      # player_name
    player_left = pyqtSignal(str)        # player_name
    error_occurred = pyqtSignal(str)     # error_message
    
    def __init__(self, server_url: str = "http://127.0.0.1:8000"):
        super().__init__()
        self.server_url = server_url
        self.sio = socketio.Client()
        self.connected_to_server = False
        self.current_room = None
        self.player_name = None
        
        # Set up Socket.IO event handlers
        self._setup_socket_handlers()
    
    def _setup_socket_handlers(self):
        """Set up Socket.IO event handlers"""
        
        @self.sio.event
        def connect():
            print("✅ Connected to multiplayer server")
            self.connected_to_server = True
            self.connected.emit()
        
        @self.sio.event
        def disconnect():
            print("❌ Disconnected from multiplayer server")
            self.connected_to_server = False
            self.disconnected.emit()
        
        @self.sio.event
        def connected(data):
            print(f"Server connection confirmed: {data}")
        
        @self.sio.event
        def room_created(data):
            print(f"Room created: {data}")
            self.current_room = data['room_code']
            self.room_created.emit(data['room_code'], data.get('players', [{}])[0].get('display_name', ''))
        
        @self.sio.event
        def player_joined(data):
            print(f"Player joined: {data}")
            self.player_joined.emit(data['display_name'])
        
        @self.sio.event
        def player_left(data):
            print(f"Player left: {data}")
            self.player_left.emit(data['player_name'])
        
        @self.sio.event
        def error(data):
            print(f"Server error: {data}")
            self.error_occurred.emit(data.get('message', 'Unknown error'))
    
    def connect_to_server(self) -> bool:
        """Connect to the multiplayer server"""
        try:
            if not self.connected_to_server:
                self.sio.connect(self.server_url)
                return True
            return True
        except Exception as e:
            print(f"❌ Failed to connect to server: {e}")
            self.error_occurred.emit(f"Failed to connect to server: {e}")
            return False
    
    def disconnect_from_server(self):
        """Disconnect from the multiplayer server"""
        try:
            if self.connected_to_server:
                self.sio.disconnect()
        except Exception as e:
            print(f"Error disconnecting: {e}")
    
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
            self.sio.emit('join_room', {
                'room_code': room_code.upper(),
                'display_name': player_name
            })
            return True
            
        except Exception as e:
            print(f"❌ Failed to join room: {e}")
            self.error_occurred.emit(f"Failed to join room: {e}")
            return False
    
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
            response = requests.get(f"{self.server_url}/health", timeout=5)
            if response.status_code == 200:
                return response.json()
            return {"error": f"Server returned status {response.status_code}"}
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
