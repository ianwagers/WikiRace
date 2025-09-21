
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QLineEdit, QMessageBox, QFrame, QTextEdit,
                            QGridLayout, QSpacerItem, QSizePolicy)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from src.logic.ThemeManager import theme_manager
from src.logic.Network import NetworkManager
import json

class MultiplayerPage(QWidget):
    def __init__(self, tabWidget, parent=None):
        super().__init__(parent)
        self.tabWidget = tabWidget
        
        # Initialize network manager
        self.network_manager = NetworkManager()
        self.connect_network_signals()
        
        # UI state
        self.current_room_code = None
        self.player_name = None
        
        self.initUI()
        self.apply_theme()
        
        # Connect to theme changes
        theme_manager.theme_changed.connect(self.apply_theme)
        
        # Test server connection on startup
        self.test_server_connection()

    def apply_theme(self):
        """Apply theme-based styles to the multiplayer page"""
        styles = theme_manager.get_theme_styles()
        
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {styles['background_color']};
                color: {styles['text_color']};
                font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif;
            }}
            QLabel {{
                color: {styles['text_color']};
                font-size: 24px;
                font-weight: bold;
                padding: 20px;
                background-color: transparent;
            }}
            QPushButton {{
                background-color: {styles['secondary_background']};
                color: {styles['text_color']};
                border: 1px solid {styles['border_color']};
                border-radius: 8px;
                font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif;
                font-size: 16px;
                font-weight: 600;
                padding: 16px 24px;
                margin: 8px;
            }}
            QPushButton:hover {{
                background-color: {styles['button_hover']};
                border-color: {styles['border_hover']};
            }}
            QPushButton:pressed {{
                background-color: {styles['button_pressed']};
                border-color: {styles['border_pressed']};
            }}
        """)

    def connect_network_signals(self):
        """Connect network manager signals to UI updates"""
        self.network_manager.connected.connect(self.on_connected)
        self.network_manager.disconnected.connect(self.on_disconnected)
        self.network_manager.room_created.connect(self.on_room_created)
        self.network_manager.player_joined.connect(self.on_player_joined)
        self.network_manager.player_left.connect(self.on_player_left)
        self.network_manager.error_occurred.connect(self.on_error_occurred)
    
    def test_server_connection(self):
        """Test connection to the multiplayer server"""
        status = self.network_manager.get_server_status()
        if "error" in status:
            self.show_server_status("❌ Server Offline", f"Cannot connect to server: {status['error']}", "error")
        else:
            self.show_server_status("✅ Server Online", f"Connected to server. Active rooms: {status.get('rooms_active', 0)}", "success")
    
    def show_server_status(self, title, message, status_type):
        """Show server connection status"""
        if hasattr(self, 'statusLabel'):
            self.statusLabel.setText(f"{title}: {message}")
            if status_type == "error":
                self.statusLabel.setStyleSheet("color: #ff6b6b; font-weight: bold;")
            else:
                self.statusLabel.setStyleSheet("color: #51cf66; font-weight: bold;")

    def initUI(self):
        """Initialize the multiplayer UI"""
        # Main layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(30, 30, 30, 30)
        self.layout.setSpacing(20)

        # Title
        self.titleLabel = QLabel("🎮 Multiplayer WikiRace")
        self.titleLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.titleLabel.setStyleSheet("font-size: 28px; font-weight: bold; margin-bottom: 20px;")
        self.layout.addWidget(self.titleLabel)

        # Server status
        self.statusLabel = QLabel("Checking server connection...")
        self.statusLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.statusLabel.setStyleSheet("font-size: 14px; margin-bottom: 20px;")
        self.layout.addWidget(self.statusLabel)

        # Player name input
        name_frame = QFrame()
        name_layout = QHBoxLayout(name_frame)
        name_layout.setContentsMargins(0, 0, 0, 0)
        
        name_label = QLabel("Your Name:")
        name_label.setMinimumWidth(100)
        name_layout.addWidget(name_label)
        
        self.playerNameInput = QLineEdit()
        self.playerNameInput.setPlaceholderText("Enter your display name...")
        self.playerNameInput.setText("Player")
        name_layout.addWidget(self.playerNameInput)
        
        self.layout.addWidget(name_frame)

        # Host Game section
        host_frame = QFrame()
        host_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        host_layout = QVBoxLayout(host_frame)
        host_layout.setContentsMargins(20, 20, 20, 20)
        
        host_title = QLabel("🏠 Host a Game")
        host_title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        host_layout.addWidget(host_title)
        
        host_desc = QLabel("Create a new game room and invite friends to join")
        host_desc.setStyleSheet("color: #868e96; margin-bottom: 15px;")
        host_layout.addWidget(host_desc)
        
        self.hostGameButton = QPushButton("Create Room")
        self.hostGameButton.setMinimumHeight(50)
        host_layout.addWidget(self.hostGameButton)
        
        self.layout.addWidget(host_frame)

        # Join Game section
        join_frame = QFrame()
        join_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        join_layout = QVBoxLayout(join_frame)
        join_layout.setContentsMargins(20, 20, 20, 20)
        
        join_title = QLabel("🚪 Join a Game")
        join_title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        join_layout.addWidget(join_title)
        
        join_desc = QLabel("Enter a room code to join an existing game")
        join_desc.setStyleSheet("color: #868e96; margin-bottom: 15px;")
        join_layout.addWidget(join_desc)
        
        room_input_layout = QHBoxLayout()
        room_label = QLabel("Room Code:")
        room_label.setMinimumWidth(100)
        room_input_layout.addWidget(room_label)
        
        self.roomCodeInput = QLineEdit()
        self.roomCodeInput.setPlaceholderText("Enter 4-letter room code...")
        self.roomCodeInput.setMaxLength(4)
        self.roomCodeInput.setStyleSheet("font-family: monospace; font-size: 16px; letter-spacing: 2px;")
        room_input_layout.addWidget(self.roomCodeInput)
        
        join_layout.addLayout(room_input_layout)
        
        self.joinGameButton = QPushButton("Join Room")
        self.joinGameButton.setMinimumHeight(50)
        join_layout.addWidget(self.joinGameButton)
        
        self.layout.addWidget(join_frame)

        # Room info (hidden initially)
        self.roomInfoFrame = QFrame()
        self.roomInfoFrame.setFrameStyle(QFrame.Shape.StyledPanel)
        self.roomInfoFrame.hide()
        room_info_layout = QVBoxLayout(self.roomInfoFrame)
        room_info_layout.setContentsMargins(20, 20, 20, 20)
        
        self.roomInfoLabel = QLabel()
        self.roomInfoLabel.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        room_info_layout.addWidget(self.roomInfoLabel)
        
        self.playersList = QTextEdit()
        self.playersList.setMaximumHeight(100)
        self.playersList.setReadOnly(True)
        room_info_layout.addWidget(self.playersList)
        
        self.leaveRoomButton = QPushButton("Leave Room")
        room_info_layout.addWidget(self.leaveRoomButton)
        
        self.layout.addWidget(self.roomInfoFrame)

        # Add stretch to push everything to top
        self.layout.addStretch()

        # Connect signals
        self.hostGameButton.clicked.connect(self.on_host_game_clicked)
        self.joinGameButton.clicked.connect(self.on_join_game_clicked)
        self.leaveRoomButton.clicked.connect(self.on_leave_room_clicked)
        
        # Connect input events
        self.roomCodeInput.textChanged.connect(self.on_room_code_changed)
        self.roomCodeInput.returnPressed.connect(self.on_join_game_clicked)
        self.playerNameInput.returnPressed.connect(self.on_host_game_clicked)

    def on_room_code_changed(self, text):
        """Handle room code input changes"""
        # Convert to uppercase and limit to 4 characters
        text = text.upper()[:4]
        if self.roomCodeInput.text() != text:
            self.roomCodeInput.setText(text)
    
    def on_host_game_clicked(self):
        """Handle host game button click"""
        player_name = self.playerNameInput.text().strip()
        if not player_name:
            QMessageBox.warning(self, "Invalid Name", "Please enter your display name.")
            return
        
        self.player_name = player_name
        self.hostGameButton.setEnabled(False)
        self.hostGameButton.setText("Creating Room...")
        
        # Try to create room via API first (simpler for testing)
        room_data = self.network_manager.create_room_via_api(player_name)
        if room_data:
            self.current_room_code = room_data['room_code']
            self.show_room_info(f"Room Created: {self.current_room_code}", [player_name])
            QMessageBox.information(self, "Room Created", 
                                  f"Room {self.current_room_code} created successfully!\n\n"
                                  f"Share this code with friends to join your game.")
        else:
            QMessageBox.critical(self, "Error", "Failed to create room. Please check server connection.")
        
        self.hostGameButton.setEnabled(True)
        self.hostGameButton.setText("Create Room")
    
    def on_join_game_clicked(self):
        """Handle join game button click"""
        player_name = self.playerNameInput.text().strip()
        room_code = self.roomCodeInput.text().strip()
        
        if not player_name:
            QMessageBox.warning(self, "Invalid Name", "Please enter your display name.")
            return
        
        if len(room_code) != 4:
            QMessageBox.warning(self, "Invalid Room Code", "Please enter a 4-letter room code.")
            return
        
        self.player_name = player_name
        self.joinGameButton.setEnabled(False)
        self.joinGameButton.setText("Joining...")
        
        # Test room existence via API
        try:
            import requests
            response = requests.get(f"http://127.0.0.1:8000/api/rooms/{room_code}", timeout=5)
            if response.status_code == 200:
                room_data = response.json()
                self.current_room_code = room_code
                
                # Add player to room via API
                join_response = requests.post(
                    f"http://127.0.0.1:8000/api/rooms/{room_code}/join",
                    json={"display_name": player_name},
                    timeout=5
                )
                
                if join_response.status_code == 200:
                    join_data = join_response.json()
                    players = [p['display_name'] for p in room_data['players']]
                    if player_name not in players:
                        players.append(player_name)
                    
                    self.show_room_info(f"Joined Room: {room_code}", players)
                    QMessageBox.information(self, "Room Joined", 
                                          f"Successfully joined room {room_code}!")
                else:
                    QMessageBox.critical(self, "Error", "Failed to join room. Room may be full.")
            else:
                QMessageBox.critical(self, "Room Not Found", f"Room {room_code} does not exist.")
        except Exception as e:
            QMessageBox.critical(self, "Connection Error", f"Failed to connect to server: {e}")
        
        self.joinGameButton.setEnabled(True)
        self.joinGameButton.setText("Join Room")
    
    def on_leave_room_clicked(self):
        """Handle leave room button click"""
        self.roomInfoFrame.hide()
        self.current_room_code = None
        self.player_name = None
        QMessageBox.information(self, "Left Room", "You have left the room.")
    
    def show_room_info(self, title, players):
        """Show room information"""
        self.roomInfoLabel.setText(title)
        self.playersList.setText("Players:\n" + "\n".join(f"• {player}" for player in players))
        self.roomInfoFrame.show()
    
    # Network signal handlers
    def on_connected(self):
        """Handle successful server connection"""
        self.show_server_status("✅ Connected", "Connected to multiplayer server", "success")
    
    def on_disconnected(self):
        """Handle server disconnection"""
        self.show_server_status("❌ Disconnected", "Lost connection to server", "error")
    
    def on_room_created(self, room_code, player_name):
        """Handle room creation event"""
        self.current_room_code = room_code
        self.show_room_info(f"Room Created: {room_code}", [player_name])
    
    def on_player_joined(self, player_name):
        """Handle player join event"""
        if hasattr(self, 'playersList'):
            current_text = self.playersList.toPlainText()
            if player_name not in current_text:
                self.playersList.append(f"• {player_name}")
    
    def on_player_left(self, player_name):
        """Handle player leave event"""
        if hasattr(self, 'playersList'):
            current_text = self.playersList.toPlainText()
            new_text = current_text.replace(f"• {player_name}\n", "").replace(f"• {player_name}", "")
            self.playersList.setText(new_text)
    
    def on_error_occurred(self, error_message):
        """Handle network errors"""
        QMessageBox.critical(self, "Network Error", f"Error: {error_message}")
        self.show_server_status("❌ Error", error_message, "error")
