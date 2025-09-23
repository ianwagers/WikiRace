
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QLineEdit, QMessageBox, QFrame, QTextEdit,
                            QGridLayout, QSpacerItem, QSizePolicy, QComboBox,
                            QScrollArea)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from src.logic.ThemeManager import theme_manager
from src.logic.Network import NetworkManager
import json

class MultiplayerPage(QWidget):
    def __init__(self, tabWidget, parent=None):
        super().__init__(parent)
        self.tabWidget = tabWidget
        
        # Load server configuration
        self.load_server_config()
        
        # Initialize network manager with configured server URL
        server_url = f"http://{self.server_config['server_host']}:{self.server_config['server_port']}"
        self.network_manager = NetworkManager(server_url)
        self.apply_config_to_network_manager()
        self.connect_network_signals()
        
        # UI state
        self.current_room_code = None
        self.player_name = None
        self.is_leader = False
        self.players_in_room = []
        
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
                font-size: 14px;
                font-weight: bold;
                padding: 8px;
                background-color: transparent;
            }}
            QPushButton {{
                background-color: {styles['secondary_background']};
                color: {styles['text_color']};
                border: 1px solid {styles['border_color']};
                border-radius: 6px;
                font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif;
                font-size: 12px;
                font-weight: 600;
                padding: 10px 18px;
                margin: 6px;
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
        self.network_manager.room_joined.connect(self.on_room_joined)
        self.network_manager.player_joined.connect(self.on_player_joined)
        self.network_manager.player_left.connect(self.on_player_left)
        self.network_manager.host_transferred.connect(self.on_host_transferred)
        self.network_manager.room_deleted.connect(self.on_room_deleted)
        self.network_manager.game_starting.connect(self.on_game_starting)
        self.network_manager.game_started.connect(self.on_game_started)
        self.network_manager.error_occurred.connect(self.on_error_occurred)
        self.network_manager.reconnecting.connect(self.on_reconnecting)
        self.network_manager.reconnected.connect(self.on_reconnected)
        self.network_manager.reconnection_failed.connect(self.on_reconnection_failed)
        self.network_manager.game_config_updated.connect(self.on_game_config_updated)
    
    def test_server_connection(self):
        """Test connection to the multiplayer server"""
        self.update_server_status()
    
    def show_server_status(self, title, message, status_type):
        """Show server connection status"""
        if hasattr(self, 'statusLabel'):
            # Truncate very long messages to prevent UI from becoming too wide
            if len(message) > 100:
                message = message[:97] + "..."
            
            self.statusLabel.setText(f"{title}: {message}")
            if status_type == "error":
                self.statusLabel.setStyleSheet("color: #ff6b6b; font-weight: bold;")
            elif status_type == "warning":
                self.statusLabel.setStyleSheet("color: #ffa726; font-weight: bold;")
            else:
                self.statusLabel.setStyleSheet("color: #51cf66; font-weight: bold;")

    def initUI(self):
        """Initialize the multiplayer UI"""
        # Main layout with scroll area
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)
        
        # Create scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setMinimumHeight(400)  # Ensure scroll area has minimum height
        
        # Create scroll content widget
        self.scroll_content = QWidget()
        self.layout = QVBoxLayout(self.scroll_content)
        self.layout.setContentsMargins(15, 15, 15, 15)
        self.layout.setSpacing(15)
        
        # Set minimum size to ensure scroll bar appears when needed
        self.scroll_content.setMinimumHeight(500)
        
        # Set scroll area widget
        self.scroll_area.setWidget(self.scroll_content)
        main_layout.addWidget(self.scroll_area)

        # Title
        self.titleLabel = QLabel("🎮 Multiplayer WikiRace")
        self.titleLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.titleLabel.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 10px;")
        self.layout.addWidget(self.titleLabel)

        # Server status and settings
        status_layout = QHBoxLayout()
        
        self.statusLabel = QLabel("Checking server connection...")
        self.statusLabel.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.statusLabel.setStyleSheet("font-size: 12px; margin-bottom: 10px;")
        self.statusLabel.setWordWrap(True)
        self.statusLabel.setMaximumWidth(300)  # Limit width to prevent app from becoming too wide
        status_layout.addWidget(self.statusLabel)
        
        status_layout.addStretch()
        
        # Server settings button
        self.settingsButton = QPushButton("⚙️ Server Settings")
        self.settingsButton.setMinimumWidth(140)
        self.settingsButton.setMinimumHeight(35)
        self.settingsButton.setMaximumHeight(40)
        self.settingsButton.clicked.connect(self.show_server_settings)
        status_layout.addWidget(self.settingsButton)
        
        self.layout.addLayout(status_layout)

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
        self.host_frame = QFrame()
        self.host_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        self.host_frame.setMaximumWidth(400)  # Limit width
        host_layout = QVBoxLayout(self.host_frame)
        host_layout.setContentsMargins(12, 12, 12, 12)
        
        host_title = QLabel("🏠 Host a Game")
        host_title.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 5px;")
        host_layout.addWidget(host_title)
        
        host_desc = QLabel("Create a new game room and invite friends to join")
        host_desc.setStyleSheet("color: #868e96; margin-bottom: 8px; font-size: 11px;")
        host_layout.addWidget(host_desc)
        
        self.hostGameButton = QPushButton("Create Room")
        self.hostGameButton.setMinimumHeight(40)
        self.hostGameButton.setMaximumHeight(45)
        host_layout.addWidget(self.hostGameButton)
        
        self.layout.addWidget(self.host_frame)

        # Join Game section
        self.join_frame = QFrame()
        self.join_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        self.join_frame.setMaximumWidth(400)  # Limit width
        join_layout = QVBoxLayout(self.join_frame)
        join_layout.setContentsMargins(12, 12, 12, 12)
        
        join_title = QLabel("🚪 Join a Game")
        join_title.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 5px;")
        join_layout.addWidget(join_title)
        
        join_desc = QLabel("Enter a room code to join an existing game")
        join_desc.setStyleSheet("color: #868e96; margin-bottom: 8px; font-size: 11px;")
        join_layout.addWidget(join_desc)
        
        room_input_layout = QHBoxLayout()
        room_label = QLabel("Room Code:")
        room_label.setMinimumWidth(80)
        room_label.setStyleSheet("font-size: 12px;")
        room_input_layout.addWidget(room_label)
        
        self.roomCodeInput = QLineEdit()
        self.roomCodeInput.setPlaceholderText("Enter 4-letter room code...")
        self.roomCodeInput.setMaxLength(4)
        self.roomCodeInput.setStyleSheet("font-family: monospace; font-size: 14px; letter-spacing: 1px;")
        room_input_layout.addWidget(self.roomCodeInput)
        
        join_layout.addLayout(room_input_layout)
        
        self.joinGameButton = QPushButton("Join Room")
        self.joinGameButton.setMinimumHeight(40)
        self.joinGameButton.setMaximumHeight(45)
        join_layout.addWidget(self.joinGameButton)
        
        self.layout.addWidget(self.join_frame)

        # Room info (hidden initially)
        self.roomInfoFrame = QFrame()
        self.roomInfoFrame.setFrameStyle(QFrame.Shape.StyledPanel)
        self.roomInfoFrame.setMaximumWidth(400)  # Limit width
        self.roomInfoFrame.hide()
        room_info_layout = QVBoxLayout(self.roomInfoFrame)
        room_info_layout.setContentsMargins(12, 12, 12, 12)
        
        self.roomInfoLabel = QLabel()
        self.roomInfoLabel.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 8px; padding: 5px;")
        self.roomInfoLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.roomInfoLabel.setWordWrap(True)
        self.roomInfoLabel.setMaximumWidth(400)  # Limit width to prevent app from becoming too wide
        room_info_layout.addWidget(self.roomInfoLabel)
        
        self.playersList = QTextEdit()
        self.playersList.setMaximumHeight(80)
        self.playersList.setMaximumWidth(400)  # Limit width to prevent app from becoming too wide
        self.playersList.setReadOnly(True)
        self.playersList.setStyleSheet("font-size: 11px;")
        room_info_layout.addWidget(self.playersList)
        
        # Game Configuration Section (only visible for leader)
        self.gameConfigFrame = QFrame()
        self.gameConfigFrame.setFrameStyle(QFrame.Shape.StyledPanel)
        self.gameConfigFrame.hide()  # Hidden by default
        game_config_layout = QVBoxLayout(self.gameConfigFrame)
        game_config_layout.setContentsMargins(8, 8, 8, 8)
        
        # Game config title
        config_title = QLabel("🎮 Game Configuration")
        config_title.setStyleSheet("font-size: 12px; font-weight: bold; margin-bottom: 6px;")
        game_config_layout.addWidget(config_title)
        
        # Starting page selection
        start_layout = QHBoxLayout()
        start_label = QLabel("Start Page:")
        start_label.setMinimumWidth(70)
        start_label.setStyleSheet("font-size: 11px;")
        start_layout.addWidget(start_label)
        
        self.startPageCombo = QComboBox()
        self.startPageCombo.setStyleSheet("font-size: 11px;")
        self.startPageCombo.addItems(['Animals', 'Buildings', 'Celebrities', 'Countries', 'Gaming', 
                                     'Literature', 'Music', 'STEM', 'Most Linked', 'US Presidents', 
                                     'Historical Events', 'Random', 'Custom'])
        start_layout.addWidget(self.startPageCombo)
        game_config_layout.addLayout(start_layout)
        
        # Custom start page input
        self.customStartPageEdit = QLineEdit()
        self.customStartPageEdit.setPlaceholderText("Enter custom starting page...")
        self.customStartPageEdit.setEnabled(False)
        self.customStartPageEdit.setStyleSheet("font-size: 11px;")
        game_config_layout.addWidget(self.customStartPageEdit)
        
        # Ending page selection
        end_layout = QHBoxLayout()
        end_label = QLabel("End Page:")
        end_label.setMinimumWidth(70)
        end_label.setStyleSheet("font-size: 11px;")
        end_layout.addWidget(end_label)
        
        self.endPageCombo = QComboBox()
        self.endPageCombo.setStyleSheet("font-size: 11px;")
        self.endPageCombo.addItems(['Animals', 'Buildings', 'Celebrities', 'Countries', 'Gaming', 
                                   'Literature', 'Music', 'STEM', 'Most Linked', 'US Presidents', 
                                   'Historical Events', 'Random', 'Custom'])
        end_layout.addWidget(self.endPageCombo)
        game_config_layout.addLayout(end_layout)
        
        # Custom end page input
        self.customEndPageEdit = QLineEdit()
        self.customEndPageEdit.setPlaceholderText("Enter custom ending page...")
        self.customEndPageEdit.setEnabled(False)
        self.customEndPageEdit.setStyleSheet("font-size: 11px;")
        game_config_layout.addWidget(self.customEndPageEdit)
        
        # Game selection display (for non-leaders)
        self.gameSelectionDisplay = QLabel("Waiting for leader to configure game...")
        self.gameSelectionDisplay.setStyleSheet("font-style: italic; color: #666; margin: 5px; font-size: 10px;")
        self.gameSelectionDisplay.setWordWrap(True)
        self.gameSelectionDisplay.setMaximumWidth(400)  # Limit width to prevent app from becoming too wide
        self.gameSelectionDisplay.hide()
        game_config_layout.addWidget(self.gameSelectionDisplay)
        
        room_info_layout.addWidget(self.gameConfigFrame)
        
        # Start Game button (only visible for leader)
        self.startGameButton = QPushButton("Start Game")
        self.startGameButton.setMinimumHeight(40)
        self.startGameButton.setMaximumHeight(45)
        self.startGameButton.setEnabled(False)
        self.startGameButton.hide()  # Hidden by default
        self.startGameButton.setStyleSheet("""
            QPushButton:disabled {
                background-color: #495057;
                color: #adb5bd;
                border: 1px solid #6c757d;
            }
        """)
        room_info_layout.addWidget(self.startGameButton)
        
        self.leaveRoomButton = QPushButton("Leave Room")
        self.leaveRoomButton.setMinimumHeight(40)
        self.leaveRoomButton.setMaximumHeight(45)
        room_info_layout.addWidget(self.leaveRoomButton)
        
        self.layout.addWidget(self.roomInfoFrame)

        # Add stretch to push everything to top
        self.layout.addStretch()

        # Connect signals
        self.hostGameButton.clicked.connect(self.on_host_game_clicked)
        self.joinGameButton.clicked.connect(self.on_join_game_clicked)
        self.leaveRoomButton.clicked.connect(self.on_leave_room_clicked)
        self.startGameButton.clicked.connect(self.on_start_game_clicked)
        
        # Connect game configuration signals
        self.startPageCombo.currentTextChanged.connect(self.on_game_config_changed)
        self.endPageCombo.currentTextChanged.connect(self.on_game_config_changed)
        self.customStartPageEdit.textChanged.connect(self.on_game_config_changed)
        self.customEndPageEdit.textChanged.connect(self.on_game_config_changed)
        
        # Connect input events
        self.roomCodeInput.textChanged.connect(self.on_room_code_changed)
        self.roomCodeInput.returnPressed.connect(self.on_join_game_clicked)
        self.playerNameInput.returnPressed.connect(self.on_host_game_clicked)
    
    def hide_host_join_sections(self):
        """Hide the host and join game sections when user joins a room"""
        self.host_frame.hide()
        self.join_frame.hide()
    
    def show_host_join_sections(self):
        """Show the host and join game sections when user leaves a room"""
        self.host_frame.show()
        self.join_frame.show()
    
    def update_server_status(self):
        """Update the server status display"""
        status = self.network_manager.get_server_status()
        if "error" in status:
            self.show_server_status("❌ Server Offline", f"Cannot connect to server: {status['error']}", "error")
        else:
            self.show_server_status("✅ Server Online", f"Connected to server. Active rooms: {status.get('rooms_active', 0)}", "success")
    
    def on_game_config_changed(self):
        """Handle game configuration changes"""
        if not self.is_leader:
            return
        
        # Enable/disable custom input fields based on selection
        start_is_custom = self.startPageCombo.currentText() == 'Custom'
        end_is_custom = self.endPageCombo.currentText() == 'Custom'
        
        self.customStartPageEdit.setEnabled(start_is_custom)
        self.customEndPageEdit.setEnabled(end_is_custom)
        
        # Update the Start Game button state based on configuration validity
        self.update_start_game_button_state()
        
        # Throttle config updates to prevent spam
        if not hasattr(self, '_config_update_timer'):
            from PyQt6.QtCore import QTimer
            self._config_update_timer = QTimer()
            self._config_update_timer.setSingleShot(True)
            self._config_update_timer.timeout.connect(self._send_config_update)
        
        # Restart the timer - this prevents rapid-fire updates
        self._config_update_timer.stop()
        self._config_update_timer.start(1000)  # 1 second delay to prevent spam
        
        # Update local display immediately
        self.update_game_selection_display()
    
    def _send_config_update(self):
        """Send the actual config update (throttled)"""
        if not self.is_leader or not self.network_manager.connected_to_server or not self.current_room_code:
            return
            
        start_is_custom = self.startPageCombo.currentText() == 'Custom'
        end_is_custom = self.endPageCombo.currentText() == 'Custom'
        
        start_category = self.startPageCombo.currentText()
        end_category = self.endPageCombo.currentText()
        custom_start = self.customStartPageEdit.text().strip() if start_is_custom else None
        custom_end = self.customEndPageEdit.text().strip() if end_is_custom else None
        
        self.network_manager.send_game_config(start_category, end_category, custom_start, custom_end)
    
    def update_game_selection_display(self):
        """Update the game selection display for non-leaders"""
        start_selection = self.startPageCombo.currentText()
        end_selection = self.endPageCombo.currentText()
        
        if start_selection == 'Custom':
            start_text = self.customStartPageEdit.text() or "Custom (not set)"
        else:
            start_text = start_selection
        
        if end_selection == 'Custom':
            end_text = self.customEndPageEdit.text() or "Custom (not set)"
        else:
            end_text = end_selection
        
        self.gameSelectionDisplay.setText(f"Game Setup:\nStart: {start_text}\nEnd: {end_text}")
    
    def update_start_game_button_state(self):
        """Update the Start Game button state based on current conditions"""
        if not self.is_leader:
            return
        
        # Check if we have enough players
        has_enough_players = len(self.players_in_room) > 1
        
        # Check if game configuration is valid
        start_selection = self.startPageCombo.currentText()
        end_selection = self.endPageCombo.currentText()
        
        config_valid = True
        if start_selection == 'Custom':
            config_valid = config_valid and bool(self.customStartPageEdit.text().strip())
        if end_selection == 'Custom':
            config_valid = config_valid and bool(self.customEndPageEdit.text().strip())
        
        # Enable button only if we have enough players AND valid configuration
        button_enabled = has_enough_players and config_valid
        self.startGameButton.setEnabled(button_enabled)
        
        # Update button text to indicate why it might be disabled
        if not has_enough_players:
            self.startGameButton.setText("Start Game (Need More Players)")
        elif not config_valid:
            self.startGameButton.setText("Start Game (Complete Configuration)")
        else:
            self.startGameButton.setText("Start Game")
    
    def on_start_game_clicked(self):
        """Handle start game button click"""
        if not self.is_leader:
            QMessageBox.warning(self, "Not Leader", "Only the room leader can start the game.")
            return
        
        if len(self.players_in_room) < 2:
            QMessageBox.warning(self, "Need More Players", "At least 2 players are required to start the game.")
            return
        
        # Validate game configuration
        start_selection = self.startPageCombo.currentText()
        end_selection = self.endPageCombo.currentText()
        
        # Validate custom pages if selected
        if start_selection == 'Custom':
            if not self.customStartPageEdit.text().strip():
                QMessageBox.warning(self, "Invalid Configuration", "Please enter a custom starting page.")
                return
        
        if end_selection == 'Custom':
            if not self.customEndPageEdit.text().strip():
                QMessageBox.warning(self, "Invalid Configuration", "Please enter a custom ending page.")
                return
        
        # Prepare game config
        game_config = {
            'start_page': start_selection,
            'end_page': end_selection,
            'custom_start': self.customStartPageEdit.text().strip() if start_selection == 'Custom' else None,
            'custom_end': self.customEndPageEdit.text().strip() if end_selection == 'Custom' else None
        }
        
        # Validate Wikipedia pages before starting (for custom pages)
        if start_selection == 'Custom' or end_selection == 'Custom':
            # Show validation message
            self.startGameButton.setText("Validating Pages...")
            self.startGameButton.setEnabled(False)
            
            # Use QTimer to validate without blocking UI
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(100, lambda: self._validate_and_start_game(game_config))
            return  # Exit here, validation will continue the process
        else:
            # No custom pages to validate, start immediately
            self._proceed_with_game_start(game_config)
    
    def _send_start_game_request(self, game_config):
        """Send the actual start game request (with delay for stability)"""
        try:
            print(f"🚀 DEBUG: About to send start_game request")
            print(f"🚀 DEBUG: Connection state - connected_to_server: {self.network_manager.connected_to_server}")
            print(f"🚀 DEBUG: Connection state - sio.connected: {getattr(self.network_manager.sio, 'connected', 'N/A')}")
            print(f"🚀 DEBUG: Connection state - current_room: {self.network_manager.current_room}")
            print(f"🚀 DEBUG: Connection state - is_healthy: {self.network_manager._is_connection_healthy()}")
            print(f"🚀 DEBUG: Game config being sent: {game_config}")
            
            # FIRST: Test if Socket.IO is working at all
            print("🧪 TESTING: Sending test_event first...")
            try:
                self.network_manager.sio.emit('test_event', {'test': 'data', 'from': 'client'})
                print("🧪 Test event sent successfully")
            except Exception as test_e:
                print(f"🧪 CRITICAL: Test event failed: {test_e}")
            
            # THEN: Send the actual start_game event
            self.network_manager.sio.emit('start_game', game_config)
            print(f"✅ Game start request sent successfully: {game_config}")
            
        except Exception as e:
            print(f"❌ CRITICAL: Failed to send start game request: {e}")
            print(f"❌ DEBUG: Exception type: {type(e).__name__}")
            import traceback
            print(f"❌ DEBUG: Full traceback: {traceback.format_exc()}")
            
            QMessageBox.critical(self, "Error", f"Failed to start game: {e}")
            # Re-enable button on error
            self.startGameButton.setEnabled(True)
            self.update_start_game_button_state()

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
        
        # Use Socket.IO to create room
        result = self.network_manager.create_room(player_name)
        if result:
            # Room creation request sent, wait for room_created event
            print(f"Room creation request sent for {player_name}")
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
        
        # Use Socket.IO to join room
        result = self.network_manager.join_room(room_code, player_name)
        if result:
            # Join request sent, wait for player_joined event
            print(f"Join room request sent for {player_name} to room {room_code}")
        else:
            QMessageBox.critical(self, "Error", "Failed to join room. Please check server connection.")
            self.joinGameButton.setEnabled(True)
            self.joinGameButton.setText("Join Room")
    
    def on_leave_room_clicked(self):
        """Handle leave room button click"""
        # Hide all room-related UI elements
        self.roomInfoFrame.hide()
        self.gameConfigFrame.hide()
        self.gameSelectionDisplay.hide()
        self.startGameButton.hide()
        
        # Show the host/join sections again
        self.show_host_join_sections()
        
        # Reset all state
        self.current_room_code = None
        self.player_name = None
        self.is_leader = False
        self.players_in_room = []
        
        # Update server status
        self.update_server_status()
        
        QMessageBox.information(self, "Left Room", "You have left the room.")
    
    def show_room_info(self, title, players):
        """Show room information"""
        self.roomInfoLabel.setText(title)
        self.playersList.setText("Players:\n" + "\n".join(f"• {player}" for player in players))
        
        # Show game configuration for all players, but with different permissions
        self.gameConfigFrame.show()
        
        if self.is_leader:
            # Leader can modify settings
            self.gameSelectionDisplay.hide()
            self.startGameButton.show()
            self.startPageCombo.setEnabled(True)
            self.endPageCombo.setEnabled(True)
            # Update start game button state based on players and configuration
            self.update_start_game_button_state()
        else:
            # Non-leader can see but not modify settings
            self.gameSelectionDisplay.show()
            self.startGameButton.hide()
            self.startPageCombo.setEnabled(False)  # Disabled but visible
            self.endPageCombo.setEnabled(False)    # Disabled but visible
            self.customStartPageEdit.setEnabled(False)
            self.customEndPageEdit.setEnabled(False)
        
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
        print(f"🎉 Room created: {room_code} by {player_name}")
        self.current_room_code = room_code
        self.is_leader = True
        self.players_in_room = [player_name]
        self.hide_host_join_sections()
        self.show_room_info(f"Room Code: {room_code}", [f"{player_name} (Leader)"])
        self.update_server_status()  # Refresh server status to show updated room count
        
        # Reset button state
        self.hostGameButton.setEnabled(True)
        self.hostGameButton.setText("Create Room")
        
        QMessageBox.information(self, "Room Created", 
                              f"Room {room_code} created successfully!\n\n"
                              f"Share this code with friends to join your game.")
    
    def on_room_joined(self, room_code, player_name, players_list):
        """Handle successful room join event"""
        print(f"🎉 Successfully joined room: {room_code}")
        self.current_room_code = room_code
        self.is_leader = False
        self.players_in_room = [p['display_name'] for p in players_list]
        self.hide_host_join_sections()
        
        # Format players list with leader tag
        formatted_players = []
        for i, p in enumerate(players_list):
            if p.get('is_host', False):
                formatted_players.append(f"{p['display_name']} (Leader)")
            else:
                formatted_players.append(p['display_name'])
        
        self.show_room_info(f"Room Code: {room_code}", formatted_players)
        self.update_server_status()  # Refresh server status
        
        # Reset button state
        self.joinGameButton.setEnabled(True)
        self.joinGameButton.setText("Join Room")
        
        QMessageBox.information(self, "Room Joined", 
                              f"Successfully joined room {room_code}!")
    
    def on_player_joined(self, player_name):
        """Handle player join event"""
        if hasattr(self, 'playersList'):
            current_text = self.playersList.toPlainText()
            if player_name not in current_text:
                self.playersList.append(f"• {player_name}")
                # Add to our local player list
                if player_name not in self.players_in_room:
                    self.players_in_room.append(player_name)
                # Update start game button state
                self.update_start_game_button_state()
    
    def on_player_left(self, player_name):
        """Handle player leave event"""
        if hasattr(self, 'playersList'):
            current_text = self.playersList.toPlainText()
            new_text = current_text.replace(f"• {player_name}\n", "").replace(f"• {player_name}", "")
            self.playersList.setText(new_text)
            # Remove from our local player list
            if player_name in self.players_in_room:
                self.players_in_room.remove(player_name)
            # Update start game button state
            self.update_start_game_button_state()
    
    def on_host_transferred(self, new_host_id, new_host_name):
        """Handle host transfer event"""
        # Update our leadership status
        if hasattr(self, 'network_manager') and hasattr(self.network_manager, 'sio'):
            # Check if we are the new host (this is a simple check, in real implementation
            # you'd want to track socket IDs properly)
            if new_host_name == self.player_name:
                self.is_leader = True
                QMessageBox.information(self, "Leadership Transferred", 
                                      "You are now the room leader!")
            else:
                self.is_leader = False
                QMessageBox.information(self, "Leadership Transferred", 
                                      f"{new_host_name} is now the room leader.")
        
        # Update the players list to reflect the new leader
        if hasattr(self, 'players_in_room') and self.players_in_room:
            # Update the leader tag in our local player list
            updated_players = []
            for player in self.players_in_room:
                player_name = player.replace(" (Leader)", "")
                if player_name == new_host_name:
                    updated_players.append(f"{player_name} (Leader)")
                else:
                    updated_players.append(player_name)
            
            self.players_in_room = updated_players
            self.show_room_info(f"Room Code: {self.current_room_code}", self.players_in_room)
    
    def on_room_deleted(self):
        """Handle room deletion event"""
        QMessageBox.information(self, "Room Closed", 
                              "The room has been closed because all players have left.")
        # Reset to initial state
        self.on_leave_room_clicked()
    
    def on_game_starting(self, countdown_data):
        """Handle game starting countdown event"""
        print(f"🎬 DEBUG: Received game_starting event with data: {countdown_data}")
        try:
            from src.gui.CountdownDialog import CountdownDialog
            
            print(f"🎬 DEBUG: Creating countdown dialog...")
            # Store reference to prevent garbage collection
            self.countdown_dialog = CountdownDialog(
                countdown_data.get('countdown_seconds', 5),
                countdown_data.get('message', 'Get ready!'),
                parent=self
            )
            
            print(f"🎬 DEBUG: Showing countdown dialog...")
            # Show the countdown dialog
            self.countdown_dialog.exec()  # Use exec() to make it modal and blocking
            
            print(f"✅ Countdown completed: {countdown_data.get('message', 'Game starting...')}")
            
        except ImportError as e:
            print(f"❌ DEBUG: CountdownDialog import failed: {e}")
            # Fallback to simple message box if CountdownDialog doesn't exist yet
            from PyQt6.QtWidgets import QMessageBox
            msg = QMessageBox(self)
            msg.setWindowTitle("Game Starting!")
            msg.setText(countdown_data.get('message', 'Get ready! Game starting soon...'))
            msg.setStandardButtons(QMessageBox.StandardButton.NoButton)
            msg.show()
            
            # Auto-close after countdown
            QTimer.singleShot(countdown_data.get('countdown_seconds', 5) * 1000, msg.close)
        except Exception as e:
            print(f"❌ DEBUG: Error in countdown dialog: {e}")
            import traceback
            print(f"❌ DEBUG: Countdown traceback: {traceback.format_exc()}")
    
    def on_game_started(self, game_data):
        """Handle game start event"""
        print(f"🎮 DEBUG: Received game_started event with data: {game_data}")
        
        room_code = game_data.get('room_code', self.current_room_code)
        start_url = game_data.get('start_url')
        end_url = game_data.get('end_url')
        start_title = game_data.get('start_title')
        end_title = game_data.get('end_title')
        
        print(f"🎮 DEBUG: Extracted game data - room: {room_code}, start: {start_title}, end: {end_title}")
        
        # Add players data to game_data
        game_data['players'] = []
        for player_name in self.players_in_room:
            # Remove "(Leader)" suffix for processing
            clean_name = player_name.replace(" (Leader)", "")
            is_host = "(Leader)" in player_name
            game_data['players'].append({
                'name': clean_name,
                'is_host': is_host
            })
        
        print(f"🎮 DEBUG: Players in game: {game_data['players']}")
        
        # Create and open multiplayer game tab
        try:
            print(f"🎮 DEBUG: Importing MultiplayerGamePage...")
            from src.gui.MultiplayerGamePage import MultiplayerGamePage
            
            print(f"🎮 DEBUG: Creating multiplayer game page...")
            # Create the multiplayer game page
            multiplayer_game = MultiplayerGamePage(
                self.tabWidget,
                self.network_manager,
                game_data,
                parent=self
            )
            
            print(f"🎮 DEBUG: Adding game tab to tab widget...")
            # Add to tab widget
            tab_index = self.tabWidget.addTab(multiplayer_game, f"🏁 Race: {room_code}")
            self.tabWidget.setCurrentIndex(tab_index)
            
            print(f"🎮 DEBUG: Starting the actual game...")
            # Start the game immediately
            multiplayer_game.start_game()
            
            print(f"✅ Multiplayer game started successfully: {start_url} -> {end_url}")
            
        except Exception as e:
            print(f"❌ CRITICAL: Failed to create multiplayer game: {e}")
            print(f"❌ DEBUG: Exception type: {type(e).__name__}")
            import traceback
            print(f"❌ DEBUG: Full traceback: {traceback.format_exc()}")
            
            # Only show error dialog for actual failures, not for normal operation
            QMessageBox.critical(self, "Game Start Error", 
                              f"Failed to start multiplayer game: {e}")
    
    def on_error_occurred(self, error_message):
        """Handle network errors"""
        QMessageBox.critical(self, "Network Error", f"Error: {error_message}")
        self.show_server_status("❌ Error", error_message, "error")
    
    def on_reconnecting(self, attempt_number):
        """Handle reconnection attempts"""
        self.show_server_status("🔄 Reconnecting", f"Attempting to reconnect... (attempt {attempt_number})", "warning")
    
    def on_reconnected(self):
        """Handle successful reconnection"""
        self.show_server_status("✅ Reconnected", "Successfully reconnected to server", "success")
        QMessageBox.information(self, "Reconnected", 
                              "Successfully reconnected to the multiplayer server!")
    
    def on_reconnection_failed(self):
        """Handle failed reconnection"""
        self.show_server_status("❌ Connection Lost", "Could not reconnect to server", "error")
        QMessageBox.warning(self, "Connection Lost", 
                          "Could not reconnect to the multiplayer server.\n"
                          "You may need to rejoin your room manually.")
    
    def load_server_config(self):
        """Load server configuration from file or use defaults"""
        try:
            from src.gui.ServerConfigDialog import ServerConfigDialog
            self.server_config = ServerConfigDialog.get_saved_config()
        except Exception as e:
            print(f"Failed to load server config: {e}")
            # Use default configuration
            self.server_config = {
                'server_host': '127.0.0.1',
                'server_port': 8001,  # Changed to match server default
                'auto_reconnect': True,
                'max_reconnection_attempts': 5,
                'reconnection_delay': 2.0,
                'max_reconnection_delay': 30.0,
                'connection_timeout': 10.0
            }
    
    def apply_config_to_network_manager(self):
        """Apply configuration settings to the network manager"""
        if hasattr(self.network_manager, 'max_reconnection_attempts'):
            self.network_manager.max_reconnection_attempts = self.server_config.get('max_reconnection_attempts', 5)
            self.network_manager.reconnection_delay = self.server_config.get('reconnection_delay', 2.0)
            self.network_manager.max_reconnection_delay = self.server_config.get('max_reconnection_delay', 30.0)
            self.network_manager.reconnection_enabled = self.server_config.get('auto_reconnect', True)
    
    def show_server_settings(self):
        """Show the server configuration dialog"""
        try:
            from src.gui.ServerConfigDialog import ServerConfigDialog
            
            dialog = ServerConfigDialog(self.server_config, self)
            dialog.config_saved.connect(self.on_server_config_saved)
            dialog.exec()
            
        except Exception as e:
            QMessageBox.critical(self, "Settings Error", f"Failed to open settings dialog:\n{e}")
    
    def on_server_config_saved(self, new_config):
        """Handle when server configuration is saved"""
        old_url = f"http://{self.server_config['server_host']}:{self.server_config['server_port']}"
        new_url = f"http://{new_config['server_host']}:{new_config['server_port']}"
        
        self.server_config = new_config
        
        # Check if server URL changed
        if old_url != new_url:
            reply = QMessageBox.question(self, "Server Changed", 
                                       f"Server URL changed to {new_url}.\n"
                                       f"Do you want to reconnect now?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                       QMessageBox.StandardButton.Yes)
            
            if reply == QMessageBox.StandardButton.Yes:
                # Disconnect from old server
                self.network_manager.disconnect_from_server()
                
                # Update network manager with new URL
                self.network_manager.server_url = new_url
                self.apply_config_to_network_manager()
                
                # Test new connection
                self.test_server_connection()
        else:
            # Just apply the new configuration
            self.apply_config_to_network_manager()
        
        QMessageBox.information(self, "Settings Saved", 
                              "Server configuration has been saved successfully!")
    
    def on_game_config_updated(self, config_data):
        """Handle game configuration updates from host"""
        if self.is_leader:
            # Don't update if we're the host (we sent this update)
            return
        
        start_category = config_data.get('start_category', 'Random')
        end_category = config_data.get('end_category', 'Random')
        custom_start = config_data.get('custom_start')
        custom_end = config_data.get('custom_end')
        host_name = config_data.get('host_name', 'Host')
        
        # Update the display for non-leaders
        start_text = custom_start if start_category == 'Custom' and custom_start else start_category
        end_text = custom_end if end_category == 'Custom' and custom_end else end_category
        
        # Handle empty custom fields
        if start_category == 'Custom' and not custom_start:
            start_text = "Custom (not set)"
        if end_category == 'Custom' and not custom_end:
            end_text = "Custom (not set)"
        
        self.gameSelectionDisplay.setText(f"Game Setup by {host_name}:\nStart: {start_text}\nEnd: {end_text}")
        
        # Update the combo boxes for non-leaders to show the selection
        if not self.is_leader:
            # Temporarily disconnect signals to prevent recursion
            self.startPageCombo.blockSignals(True)
            self.endPageCombo.blockSignals(True)
            self.customStartPageEdit.blockSignals(True)
            self.customEndPageEdit.blockSignals(True)
            
            # Update the UI elements
            start_index = self.startPageCombo.findText(start_category)
            if start_index >= 0:
                self.startPageCombo.setCurrentIndex(start_index)
            
            end_index = self.endPageCombo.findText(end_category)
            if end_index >= 0:
                self.endPageCombo.setCurrentIndex(end_index)
                
            # Update custom fields (clear first, then set)
            self.customStartPageEdit.clear()
            self.customEndPageEdit.clear()
            
            if custom_start:
                self.customStartPageEdit.setText(custom_start)
            if custom_end:
                self.customEndPageEdit.setText(custom_end)
                
            # For non-leaders, these should remain disabled but visible
            # They were already disabled in show_room_info
            
            # Re-enable signals
            self.startPageCombo.blockSignals(False)
            self.endPageCombo.blockSignals(False)
            self.customStartPageEdit.blockSignals(False)
            self.customEndPageEdit.blockSignals(False)
            
            print(f"🔄 Non-leader UI updated: {start_category} -> {end_category} (start: '{custom_start}', end: '{custom_end}')")
        
        print(f"📝 Game configuration updated by {host_name}: {start_text} -> {end_text}")
    
    def _validate_wikipedia_page(self, page_title):
        """Validate that a Wikipedia page exists using search API"""
        try:
            import requests
            # Use Wikipedia search API (same as findWikiPage method)
            api_url = "https://en.wikipedia.org/w/api.php"
            headers = {
                'User-Agent': 'WikiRace Game/1.0 (https://github.com/ianwagers/wikirace)'
            }
            params = {
                "action": "query",
                "list": "search",
                "srsearch": page_title,
                "format": "json",
                "srlimit": 1
            }
            response = requests.get(api_url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            # Check if search results are present
            return bool(data.get("query", {}).get("search", []))
        except Exception as e:
            print(f"❌ Error validating Wikipedia page '{page_title}': {e}")
            return False  # If we can't validate, assume it's invalid
    
    def _validate_and_start_game(self, game_config):
        """Validate custom pages and start game if valid"""
        try:
            start_selection = game_config['start_page']
            end_selection = game_config['end_page']
            
            # Validate custom start page
            if start_selection == 'Custom':
                custom_start = game_config['custom_start']
                if not self._validate_wikipedia_page(custom_start):
                    QMessageBox.critical(self, "Invalid Starting Page", 
                                       f"The page '{custom_start}' was not found on Wikipedia.\n"
                                       f"Please enter a valid Wikipedia page title.")
                    self.startGameButton.setEnabled(True)
                    self.update_start_game_button_state()
                    return
            
            # Validate custom end page
            if end_selection == 'Custom':
                custom_end = game_config['custom_end']
                if not self._validate_wikipedia_page(custom_end):
                    QMessageBox.critical(self, "Invalid Ending Page", 
                                       f"The page '{custom_end}' was not found on Wikipedia.\n"
                                       f"Please enter a valid Wikipedia page title.")
                    self.startGameButton.setEnabled(True)
                    self.update_start_game_button_state()
                    return
            
            # All validations passed, proceed with game start
            self._proceed_with_game_start(game_config)
                
        except Exception as e:
            QMessageBox.critical(self, "Validation Error", f"Failed to validate pages: {e}")
            self.startGameButton.setEnabled(True)
            self.update_start_game_button_state()
    
    def _proceed_with_game_start(self, game_config):
        """Proceed with game start after validation"""
        try:
            # Use the healthier connection check
            if hasattr(self.network_manager, '_is_connection_healthy') and self.network_manager._is_connection_healthy():
                # Disable the start button to prevent double-clicks
                self.startGameButton.setEnabled(False)
                self.startGameButton.setText("Starting Game...")
                
                # Add a small delay to ensure connection stability
                from PyQt6.QtCore import QTimer
                QTimer.singleShot(100, lambda: self._send_start_game_request(game_config))
                
            else:
                QMessageBox.warning(self, "Connection Error", "Connection is not stable. Please wait and try again.")
                self.startGameButton.setEnabled(True)
                self.update_start_game_button_state()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to start game: {e}")
            # Re-enable button on error
            self.startGameButton.setEnabled(True)
            self.update_start_game_button_state()
