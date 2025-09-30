
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QLineEdit, QMessageBox, QFrame, QTextEdit,
                            QGridLayout, QSpacerItem, QSizePolicy, QComboBox,
                            QScrollArea)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from src.logic.ThemeManager import theme_manager
from src.logic.Network import NetworkManager
from src.gui.components.PlayerColorPicker import PlayerColorPicker
import json
import time

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
        self.countdown_dialogs = []  # Store list of countdown dialogs for debugging
        self.player_colors = {}  # Store player color mappings
        self.my_color = None  # Store current player's selected color
        
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
            QFrame {{
                border: none;
                background-color: transparent;
            }}
            QComboBox {{
                background-color: {styles['input_background']};
                color: {styles['text_color']};
                border: 1px solid {styles['input_border']};
                border-radius: 4px;
                font-size: 12px;
                padding: 6px;
                min-height: 20px;
            }}
            QComboBox:hover {{
                border-color: {styles['border_hover']};
            }}
            QComboBox:focus {{
                border-color: {styles['input_focus']};
            }}
            QComboBox::drop-down {{
                border: none;
                background-color: {styles['input_background']};
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid {styles['text_color']};
                margin-right: 5px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {styles['input_background']};
                color: {styles['text_color']};
                border: 1px solid {styles['input_border']};
                selection-background-color: {styles['accent_color']};
                selection-color: white;
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
        self.network_manager.game_ended.connect(self.on_game_ended)
        self.network_manager.error_occurred.connect(self.on_error_occurred)
        self.network_manager.reconnecting.connect(self.on_reconnecting)
        self.network_manager.reconnected.connect(self.on_reconnected)
        self.network_manager.reconnection_failed.connect(self.on_reconnection_failed)
        self.network_manager.game_config_updated.connect(self.on_game_config_updated)
        self.network_manager.player_color_updated.connect(self.on_player_color_updated)
        self.network_manager.kicked_for_inactivity.connect(self.on_kicked_for_inactivity)
        self.network_manager.room_closed.connect(self.on_room_closed)
        self.network_manager.player_disconnected.connect(self.on_player_disconnected)
        self.network_manager.player_reconnected.connect(self.on_player_reconnected)
        
        # Also try connecting with a different approach
        try:
            self.network_manager.player_color_updated.disconnect()
            self.network_manager.player_color_updated.connect(self.on_player_color_updated)
        except:
            pass
    
    def test_server_connection(self):
        """Test connection to the multiplayer server"""
        self.update_server_status()
    
    def show_server_status(self, title, message, status_type):
        """Show server connection status with improved formatting"""
        if hasattr(self, 'statusLabel'):
            # Format the status with better line breaks and styling
            if "Rooms:" in message or "rooms:" in message:
                # Split server status and room count into separate lines
                parts = message.split("Active rooms:")
                if len(parts) == 2:
                    server_status = parts[0].strip()
                    room_count = parts[1].strip()
                    formatted_text = f"{title}\n{server_status}\nRooms: {room_count}"
                else:
                    formatted_text = f"{title}\n{message}"
            else:
                formatted_text = f"{title}\n{message}"
            
            self.statusLabel.setText(formatted_text)
            
            # Apply status-specific styling
            if status_type == "error":
                self.statusLabel.setStyleSheet("""
                    color: #ff6b6b; 
                    font-weight: bold; 
                    font-size: 13px;
                    margin-bottom: 5px;
                """)
            elif status_type == "warning":
                self.statusLabel.setStyleSheet("""
                    color: #ffa726; 
                    font-weight: bold; 
                    font-size: 13px;
                    margin-bottom: 5px;
                """)
            else:
                self.statusLabel.setStyleSheet("""
                    color: #51cf66; 
                    font-weight: bold; 
                    font-size: 13px;
                    margin-bottom: 5px;
                """)

    def initUI(self):
        """Initialize the multiplayer UI"""
        # Calculate dynamic width based on screen size - cap at 600px for better UX
        screen_width = self.screen().availableGeometry().width()
        self.dynamic_width = min(int(screen_width * 0.45), 600)  # 45% of screen width, max 600px
        
        # Main layout with scroll area
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)
        
        # Create scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setMinimumHeight(600)  # Ensure scroll area has minimum height
        
        # Create scroll content widget with vertical layout
        self.scroll_content = QWidget()
        self.main_layout = QVBoxLayout(self.scroll_content)
        self.main_layout.setContentsMargins(15, 15, 15, 15)
        self.main_layout.setSpacing(15)
        
        # Player Color Picker (only visible when in a room)
        self.color_picker = PlayerColorPicker()
        self.color_picker.setSizePolicy(QSizePolicy.Policy.Preferred,
                                QSizePolicy.Policy.Expanding)
        self.color_picker.hide()  # Hidden initially
        self.color_picker.color_selected.connect(self.on_color_selected)
        
        # Wrap color picker in scroll area for scroll safety
        self.color_scroll = QScrollArea()
        self.color_scroll.setWidgetResizable(True)
        self.color_scroll.setSizePolicy(QSizePolicy.Policy.Preferred,
                                QSizePolicy.Policy.Expanding)
        self.color_scroll.setWidget(self.color_picker)
        self.color_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.color_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Track used colors for conflict detection
        self.used_colors = set()
        
        # Keep the old layout reference for compatibility
        self.layout = self.main_layout
        
        # Set minimum size to ensure scroll bar appears when needed
        self.scroll_content.setMinimumHeight(500)
        
        # Set scroll area widget
        self.scroll_area.setWidget(self.scroll_content)
        main_layout.addWidget(self.scroll_area)

        # Title
        self.titleLabel = QLabel("🎮 Multiplayer WikiRace")
        self.titleLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.titleLabel.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 10px;")
        self.main_layout.addWidget(self.titleLabel)

        # Server status and settings
        status_layout = QVBoxLayout()  # Changed to vertical layout for better spacing
        
        # Server status section
        status_info_layout = QHBoxLayout()
        
        self.statusLabel = QLabel("Checking server connection...")
        self.statusLabel.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.statusLabel.setStyleSheet("font-size: 13px; margin-bottom: 5px; font-weight: 500;")
        self.statusLabel.setWordWrap(True)
        self.statusLabel.setMaximumWidth(400)  # Increased width for better readability
        status_info_layout.addWidget(self.statusLabel)
        
        status_info_layout.addStretch()
        
        # Server settings button with better sizing
        self.settingsButton = QPushButton("⚙️ Server Settings")
        self.settingsButton.setMinimumWidth(160)  # Increased width
        self.settingsButton.setMinimumHeight(40)  # Increased height
        self.settingsButton.setMaximumHeight(45)  # Increased max height
        self.settingsButton.setStyleSheet("""
            QPushButton {
                font-size: 13px;
                font-weight: 600;
                padding: 8px 16px;
            }
        """)
        self.settingsButton.clicked.connect(self.show_server_settings)
        status_info_layout.addWidget(self.settingsButton)
        
        status_layout.addLayout(status_info_layout)
        
        self.main_layout.addLayout(status_layout)

        # Player name input removed - now handled by dialog

        # Host Game section
        self.host_frame = QFrame()
        self.host_frame.setFrameStyle(QFrame.Shape.NoFrame)
        # Cap width at 600px for better UX as requested
        self.host_frame.setMinimumWidth(300)  # Minimum width for readability
        self.host_frame.setMaximumWidth(600)  # Cap at 600px as requested
        host_layout = QVBoxLayout(self.host_frame)
        host_layout.setContentsMargins(20, 20, 20, 20)  # Further increased padding for better spacing
        
        host_title = QLabel("🏠 Host a Game")
        host_title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 8px; color: #2c3e50;")  # Larger and better color
        host_layout.addWidget(host_title)
        
        host_desc = QLabel("Create a new game room and invite friends to join")
        host_desc.setStyleSheet("color: #868e96; margin-bottom: 12px; font-size: 13px; line-height: 1.4;")  # Better line height
        host_desc.setWordWrap(True)  # Enable text wrapping
        host_desc.setMaximumWidth(400)  # Allow wrapping at reasonable width
        host_layout.addWidget(host_desc)
        
        self.hostGameButton = QPushButton("Create Room")
        self.hostGameButton.setMinimumHeight(55)  # Even larger for better usability
        self.hostGameButton.setMaximumHeight(60)  # Even larger for better usability
        self.hostGameButton.setMinimumWidth(200)  # Fixed minimum width for horizontal layout
        self.hostGameButton.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                font-weight: 600;
                padding: 12px 20px;
                border-radius: 8px;
            }
        """)
        host_layout.addWidget(self.hostGameButton)
        
        # Create horizontal layout for host and join frames
        self.host_join_layout = QHBoxLayout()
        self.host_join_layout.setSpacing(20)
        self.host_join_layout.setContentsMargins(0, 0, 0, 0)
        
        # Add host frame to horizontal layout
        self.host_join_layout.addWidget(self.host_frame)

        # Join Game section
        self.join_frame = QFrame()
        self.join_frame.setFrameStyle(QFrame.Shape.NoFrame)
        # Cap width at 600px for better UX as requested
        self.join_frame.setMinimumWidth(500)  # Minimum width for readability
        self.join_frame.setMaximumWidth(600)  # Cap at 600px as requested
        join_layout = QVBoxLayout(self.join_frame)
        join_layout.setContentsMargins(20, 20, 20, 20)  # Further increased padding for better spacing
        
        join_title = QLabel("🚪 Join a Game")
        join_title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 8px; color: #2c3e50;")  # Larger and better color
        join_layout.addWidget(join_title)
        
        join_desc = QLabel("Enter a room code to join an existing game")
        join_desc.setStyleSheet("color: #868e96; margin-bottom: 12px; font-size: 13px; line-height: 1.4;")  # Better line height
        join_layout.addWidget(join_desc)
        
        room_input_layout = QHBoxLayout()
        room_label = QLabel("Room Code:")
        room_label.setMinimumWidth(120)  # Even larger for better spacing
        room_label.setStyleSheet("font-size: 13px; font-weight: 500;")
        room_input_layout.addWidget(room_label)
        
        self.roomCodeInput = QLineEdit()
        self.roomCodeInput.setPlaceholderText("Enter 4-letter room code...")
        self.roomCodeInput.setMaxLength(4)
        self.roomCodeInput.setStyleSheet("""
            font-family: monospace; 
            font-size: 18px; 
            letter-spacing: 2px; 
            padding: 10px 12px;
            border-radius: 6px;
            text-align: center;
        """)  # Better styling for room code input
        self.roomCodeInput.setMinimumHeight(40)  # Larger input height
        room_input_layout.addWidget(self.roomCodeInput)
        
        join_layout.addLayout(room_input_layout)
        
        self.joinGameButton = QPushButton("Join Room")
        self.joinGameButton.setMinimumHeight(55)  # Even larger for better usability
        self.joinGameButton.setMaximumHeight(60)  # Even larger for better usability
        self.joinGameButton.setMinimumWidth(200)  # Fixed minimum width for horizontal layout
        self.joinGameButton.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                font-weight: 600;
                padding: 12px 20px;
                border-radius: 8px;
            }
        """)
        join_layout.addWidget(self.joinGameButton)
        
        # Add join frame to horizontal layout
        self.host_join_layout.addWidget(self.join_frame)
        
        # Add spacer to force dialogs to the left on large displays
        self.host_join_layout.addStretch()
        
        # Add the horizontal layout to main layout
        self.main_layout.addLayout(self.host_join_layout)

        # Room info (hidden initially)
        self.roomInfoFrame = QFrame()
        self.roomInfoFrame.setFrameStyle(QFrame.Shape.NoFrame)
        self.roomInfoFrame.setMaximumWidth(self.dynamic_width)  # Use same dynamic width
        self.roomInfoFrame.setMinimumWidth(int(self.dynamic_width * 0.8))  # Minimum 80% of calculated width
        self.roomInfoFrame.hide()
        room_info_layout = QVBoxLayout(self.roomInfoFrame)
        room_info_layout.setContentsMargins(16, 16, 16, 16)  # Increased padding by 25%
        
        self.roomInfoLabel = QLabel()
        self.roomInfoLabel.setStyleSheet("font-size: 32px; font-weight: bold; margin-bottom: 8px; padding: 5px;")  # Doubled from 16px to 32px
        self.roomInfoLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.roomInfoLabel.setWordWrap(True)
        self.roomInfoLabel.setMaximumWidth(self.dynamic_width)  # Use dynamic width
        room_info_layout.addWidget(self.roomInfoLabel)
        
        # Create players grid layout (3 rows, up to 10 players)
        self.playersGrid = QWidget()
        self.playersGrid.setMaximumHeight(200)  # Increased height for grid
        self.playersGrid.setMaximumWidth(self.dynamic_width)  # Use dynamic width
        self.playersGridLayout = QGridLayout(self.playersGrid)
        self.playersGridLayout.setSpacing(8)
        self.playersGridLayout.setContentsMargins(8, 8, 8, 8)
        
        # Initialize player labels (up to 10 players)
        self.playerLabels = []
        for i in range(10):
            label = QLabel("")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet("""
                QLabel {
                    background-color: rgba(255, 255, 255, 0.1);
                    border: 1px solid rgba(255, 255, 255, 0.2);
                    border-radius: 8px;
                    padding: 8px;
                    font-size: 12px;
                    font-weight: bold;
                    min-height: 40px;
                }
                QLabel:empty {
                    background-color: transparent;
                    border: 1px dashed rgba(255, 255, 255, 0.3);
                }
            """)
            label.hide()  # Hide empty slots
            self.playerLabels.append(label)
            self.playersGridLayout.addWidget(label, i // 4, i % 4)  # 3 rows, 4 columns (3*4=12, but we use 10)
        
        room_info_layout.addWidget(self.playersGrid)
        
        # Game Configuration Section (only visible for leader)
        self.gameConfigFrame = QFrame()
        self.gameConfigFrame.setFrameStyle(QFrame.Shape.NoFrame)
        self.gameConfigFrame.hide()  # Hidden by default
        self.gameConfigFrame.setMaximumWidth(self.dynamic_width)  # Use dynamic width
        game_config_layout = QVBoxLayout(self.gameConfigFrame)
        game_config_layout.setContentsMargins(12, 12, 12, 12)  # Increased padding by 25%
        
        # Game config title
        config_title = QLabel("🎮 Game Configuration")
        config_title.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 8px;")  # Increased font size
        game_config_layout.addWidget(config_title)
        
        # Starting page selection
        start_layout = QHBoxLayout()
        start_label = QLabel("Start Page:")
        start_label.setMinimumWidth(90)  # Increased by 25% (70 * 1.25 = 87.5, rounded to 90)
        start_label.setStyleSheet("font-size: 12px;")  # Increased font size
        start_layout.addWidget(start_label)
        
        self.startPageCombo = QComboBox()
        self.startPageCombo.setMinimumHeight(35)  # Increased combo box height
        self.startPageCombo.addItems(['Animals', 'Buildings', 'Celebrities', 'Countries', 'Gaming', 
                                     'Literature', 'Music', 'STEM', 'Most Linked', 'US Presidents', 
                                     'Historical Events', 'Wacky', 'Random', 'Custom'])
        start_layout.addWidget(self.startPageCombo)
        game_config_layout.addLayout(start_layout)
        
        # Custom start page input
        self.customStartPageEdit = QLineEdit()
        self.customStartPageEdit.setPlaceholderText("Enter custom starting page...")
        self.customStartPageEdit.setEnabled(False)
        self.customStartPageEdit.setStyleSheet("font-size: 12px; padding: 6px;")  # Increased font size and padding
        self.customStartPageEdit.setMinimumHeight(35)  # Increased input height
        game_config_layout.addWidget(self.customStartPageEdit)
        
        # Ending page selection
        end_layout = QHBoxLayout()
        end_label = QLabel("End Page:")
        end_label.setMinimumWidth(90)  # Increased by 25% (70 * 1.25 = 87.5, rounded to 90)
        end_label.setStyleSheet("font-size: 12px;")  # Increased font size
        end_layout.addWidget(end_label)
        
        self.endPageCombo = QComboBox()
        self.endPageCombo.setMinimumHeight(35)  # Increased combo box height
        self.endPageCombo.addItems(['Animals', 'Buildings', 'Celebrities', 'Countries', 'Gaming', 
                                   'Literature', 'Music', 'STEM', 'Most Linked', 'US Presidents', 
                                   'Historical Events', 'Wacky', 'Random', 'Custom'])
        end_layout.addWidget(self.endPageCombo)
        game_config_layout.addLayout(end_layout)
        
        # Custom end page input
        self.customEndPageEdit = QLineEdit()
        self.customEndPageEdit.setPlaceholderText("Enter custom ending page...")
        self.customEndPageEdit.setEnabled(False)
        self.customEndPageEdit.setStyleSheet("font-size: 12px; padding: 6px;")  # Increased font size and padding
        self.customEndPageEdit.setMinimumHeight(35)  # Increased input height
        game_config_layout.addWidget(self.customEndPageEdit)
        
        # Game selection display (for non-leaders)
        self.gameSelectionDisplay = QLabel("Waiting for leader to configure game...")
        self.gameSelectionDisplay.setStyleSheet("font-style: italic; color: #666; margin: 8px; font-size: 12px;")  # Increased font size and margin
        self.gameSelectionDisplay.setWordWrap(True)
        self.gameSelectionDisplay.setMaximumWidth(self.dynamic_width)  # Use dynamic width
        self.gameSelectionDisplay.hide()
        game_config_layout.addWidget(self.gameSelectionDisplay)
        
        room_info_layout.addWidget(self.gameConfigFrame)
        
        # Start Game button (only visible for leader)
        self.startGameButton = QPushButton("Start Game")
        self.startGameButton.setMinimumHeight(50)  # Increased by 25% (40 * 1.25 = 50)
        self.startGameButton.setMaximumHeight(56)  # Increased by 25% (45 * 1.25 = 56)
        self.startGameButton.setMinimumWidth(int(self.dynamic_width * 0.8))  # Dynamic button width
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
        self.leaveRoomButton.setMinimumHeight(50)  # Increased by 25% (40 * 1.25 = 50)
        self.leaveRoomButton.setMaximumHeight(56)  # Increased by 25% (45 * 1.25 = 56)
        self.leaveRoomButton.setMinimumWidth(int(self.dynamic_width * 0.8))  # Dynamic button width
        room_info_layout.addWidget(self.leaveRoomButton)
        
        # Create horizontal frame to contain room info and color picker
        self.roomAndColorFrame = QFrame()
        self.roomAndColorFrame.setFrameStyle(QFrame.Shape.NoFrame)
        self.roomAndColorFrame.setMaximumWidth(1600)  # Increased to accommodate game settings, room code, and color picker
        self.roomAndColorFrame.setMinimumWidth(int(self.dynamic_width * 0.8))
        self.roomAndColorFrame.hide()
        room_and_color_layout = QHBoxLayout(self.roomAndColorFrame)
        room_and_color_layout.setContentsMargins(16, 16, 16, 16)
        room_and_color_layout.setSpacing(20)
        
        # Add room info frame to the left (takes more space)
        room_and_color_layout.addWidget(self.roomInfoFrame, stretch=3)
        
        # Add color picker scroll area to the right (takes less space to prevent overlap)
        room_and_color_layout.addWidget(self.color_scroll, stretch=1)
        
        # Anchor the color picker scroll area to the right and top
        # room_and_color_layout.setAlignment(self.color_scroll, Qt.AlignmentFlag.AlignTop)
        
        self.main_layout.addWidget(self.roomAndColorFrame)

        # Add stretch to push everything to top
        self.main_layout.addStretch()

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
        
        # Dynamic width is already set at the beginning of initUI
    
    def resizeEvent(self, event):
        """Handle window resize events for dynamic sizing"""
        super().resizeEvent(event)
        
        # Update dynamic width based on current window size
        current_width = self.width()
        # Use screen width for better cross-platform support
        screen_width = self.screen().availableGeometry().width()
        
        # Calculate new dynamic width with better cross-platform support
        # Use 45% of screen width, capped at 600px for better UX
        new_dynamic_width = min(int(screen_width * 0.45), 600)
        
        # Only update if there's a significant change to avoid constant updates
        if abs(new_dynamic_width - self.dynamic_width) > 20:
            self.dynamic_width = new_dynamic_width
            self.update_dynamic_sizing()
    
    def update_dynamic_sizing(self):
        """Update all dynamic sizing elements"""
        # Update frame widths - cap at 600px for better UX as requested
        # Calculate available width for each frame (half of available space minus spacing)
        available_width = max(300, min(self.dynamic_width, 600))  # Minimum 300px, max 600px per frame
        self.host_frame.setMinimumWidth(available_width)
        self.host_frame.setMaximumWidth(600)  # Ensure cap is maintained
        self.join_frame.setMinimumWidth(available_width)
        self.join_frame.setMaximumWidth(600)  # Ensure cap is maintained
        
        # Room info and game config still use dynamic width
        self.roomInfoFrame.setMaximumWidth(self.dynamic_width)
        self.roomInfoFrame.setMinimumWidth(int(self.dynamic_width * 0.8))
        self.gameConfigFrame.setMaximumWidth(self.dynamic_width)
        
        # Keep room and color frame at the wider 1600px maximum
        self.roomAndColorFrame.setMaximumWidth(1600)
        
        # Update button widths for horizontal layout
        button_width = max(200, int(self.dynamic_width * 0.4))  # Each button gets half the width
        self.hostGameButton.setMinimumWidth(button_width)
        self.joinGameButton.setMinimumWidth(button_width)
        self.startGameButton.setMinimumWidth(button_width)
        self.leaveRoomButton.setMinimumWidth(button_width)
        
        # Update other elements
        self.roomInfoLabel.setMaximumWidth(self.dynamic_width)
        self.playersGrid.setMaximumWidth(self.dynamic_width)
        self.gameSelectionDisplay.setMaximumWidth(self.dynamic_width)
        
        # Set proper size constraints for color picker to prevent overlap
        if hasattr(self, 'color_scroll'):
            # Set maximum width based on dynamic width to prevent overlap
            max_width = int(self.dynamic_width * 0.4)  # 40% of dynamic width
            self.color_scroll.setMaximumWidth(max_width)
            self.color_scroll.setMinimumHeight(200)  # optional, small baseline
    
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
        
        # Enable/disable custom input fields based on selection AND leadership status
        start_is_custom = self.startPageCombo.currentText() == 'Custom'
        end_is_custom = self.endPageCombo.currentText() == 'Custom'
        
        # Only enable custom edit boxes if we're the leader AND the combo is set to Custom
        self.customStartPageEdit.setEnabled(start_is_custom and self.is_leader)
        self.customEndPageEdit.setEnabled(end_is_custom and self.is_leader)
        
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
        # Convert to uppercase, limit to 4 characters, and only allow letters
        text = ''.join(c for c in text.upper() if c.isalpha())[:4]
        if self.roomCodeInput.text() != text:
            self.roomCodeInput.setText(text)
    
    def on_host_game_clicked(self):
        """Handle host game button click"""
        # Show player name dialog
        from src.gui.PlayerNameDialog import PlayerNameDialog
        player_name = PlayerNameDialog.get_player_name("Enter Your Name", self)
        if not player_name:
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
        room_code = self.roomCodeInput.text().strip()
        
        # Validate room code first before showing dialog
        if len(room_code) != 4:
            QMessageBox.warning(self, "Invalid Room Code", "Please enter a 4-letter room code.")
            return
        
        # Check if room exists before showing name dialog
        if not self._validate_room_exists(room_code):
            QMessageBox.warning(self, "Room Not Found", f"Room '{room_code}' does not exist. Please check the room code.")
            return
        
        # Show player name dialog only after room validation
        from src.gui.PlayerNameDialog import PlayerNameDialog
        player_name = PlayerNameDialog.get_player_name("Enter Your Name", self)
        if not player_name:
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
        # CRITICAL FIX: Properly clean up state when leaving room to prevent rejoin bugs
        print(f"🔄 WikiRace: [{time.time():.3f}] Leaving room - cleaning up state")
        
        # CRITICAL FIX: Clean up countdown dialogs before leaving room
        self.cleanup_countdown_dialogs()
        
        # Leave the room via network manager first
        if hasattr(self.network_manager, 'leave_room') and self.current_room_code:
            try:
                self.network_manager.leave_room()
                print(f"🔄 WikiRace: [{time.time():.3f}] Sent leave room request to server")
            except Exception as e:
                print(f"⚠️ WikiRace: [{time.time():.3f}] Error leaving room via network: {e}")
        
        # CRITICAL FIX: Reset UI state but keep network connection for rejoining
        self.reset_for_leave_room()
        
        print(f"✅ WikiRace: [{time.time():.3f}] Room state completely reset - ready for rejoin")
        QMessageBox.information(self, "Left Room", "You have left the room.")
    
    def reset_for_new_game(self):
        """Reset the multiplayer page state to allow starting new games after play again"""
        print("🔄 Resetting multiplayer page for new game...")
        print(f"🔍 DEBUG: current_room_code = {self.current_room_code}")
        print(f"🔍 DEBUG: network_manager exists = {hasattr(self, 'network_manager')}")
        if hasattr(self, 'network_manager'):
            print(f"🔍 DEBUG: network_manager.current_room = {getattr(self.network_manager, 'current_room', 'None')}")
        
        # SIMPLIFIED FIX: Just ensure signal connections are active for real-time updates
        # The existing player_left event handling should work automatically
        if hasattr(self, 'network_manager') and self.network_manager.connected_to_server:
            print("🔄 Ensuring real-time event listeners are active after play again")
            # Force a refresh of the player list to catch any missed events
            self._refresh_player_list_if_needed()
        else:
            print("⚠️ Cannot ensure event listeners - network manager not available")
        
        # Reset game configuration to defaults
        if hasattr(self, 'startPageCombo'):
            self.startPageCombo.setCurrentIndex(0)  # Reset to first option
        if hasattr(self, 'endPageCombo'):
            self.endPageCombo.setCurrentIndex(0)  # Reset to first option
        if hasattr(self, 'customStartPageEdit'):
            self.customStartPageEdit.clear()
        if hasattr(self, 'customEndPageEdit'):
            self.customEndPageEdit.clear()
        
        # Clear the waiting flag immediately when resetting
        if hasattr(self, '_waiting_for_players_ready'):
            self._waiting_for_players_ready = False
        
        # Reset start game button state - enable it if we have enough players and valid config
        if hasattr(self, 'startGameButton'):
            self.startGameButton.show()  # Make sure it's visible for leaders
            # Update the button state based on current conditions
            self.update_start_game_button_state()
        
        # Update game selection display for non-leaders
        if hasattr(self, 'update_game_selection_display'):
            self.update_game_selection_display()
        
        # Force a configuration update to broadcast the reset settings to other players
        if self.is_leader and hasattr(self, '_send_config_update'):
            # Send the reset configuration to other players
            self._send_config_update()
        
        print("✅ Multiplayer page reset for new game")
    
    def _refresh_player_list_if_needed(self):
        """Simple refresh to catch any missed player_left events"""
        try:
            print("🔄 Checking if player list refresh is needed...")
            
            # Request fresh room state from server to ensure we have the latest player list
            if self.current_room_code and hasattr(self, 'network_manager'):
                print(f"🔄 Requesting fresh room state for room {self.current_room_code}")
                self._refresh_room_state_from_server()
            
            # The existing player_left event handling should work automatically
            # This is just a safety check to ensure we're in sync
            if hasattr(self, 'update_start_game_button_state'):
                self.update_start_game_button_state()
            print("✅ Player list refresh check completed")
        except Exception as e:
            print(f"⚠️ Error refreshing player list: {e}")
    
    def _refresh_room_state_from_server(self):
        """Refresh room state from server to get updated player list"""
        if not self.current_room_code or not hasattr(self, 'network_manager'):
            return
        
        try:
            print(f"🔄 Fetching fresh room state from server for {self.current_room_code}")
            # Use the network manager to get fresh room info via REST API
            import requests
            server_url = getattr(self.network_manager, 'server_url', 'http://127.0.0.1:8000')
            url = f"{server_url}/api/rooms/{self.current_room_code}"
            
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    room_info = response.json()
                    print(f"📡 Received fresh room state: {room_info}")
                    # Update our local state with fresh data
                    self._update_room_state_from_server_data(room_info)
                else:
                    print(f"⚠️ Room info request failed with status {response.status_code}")
            except Exception as e:
                print(f"⚠️ Error fetching room info via REST API: {e}")
                
        except Exception as e:
            print(f"⚠️ Error refreshing room state from server: {e}")
    
    def _update_room_state_from_server_data(self, room_data):
        """Update UI state based on fresh server room data"""
        try:
            if 'players' in room_data:
                # Update player list with fresh data
                players = room_data['players']
                print(f"👥 Updating player list with {len(players)} players from server")
                
                # Update the player list display
                if hasattr(self, 'update_player_list'):
                    self.update_player_list(players)
                
                # Update player count
                if hasattr(self, 'playerCountLabel'):
                    self.playerCountLabel.setText(f"Players: {len(players)}")
                
                # Update start game button state based on fresh player count
                if hasattr(self, 'update_start_game_button_state'):
                    self.update_start_game_button_state()
                    
        except Exception as e:
            print(f"⚠️ Error updating room state from server data: {e}")
    
    def reset_for_leave_room(self):
        """Reset UI state when leaving room but keep network connection for rejoining"""
        print("🔄 Resetting multiplayer page state for leave room...")
        
        # Reset all state variables to initial values
        self.current_room_code = None
        self.player_name = None
        self.is_leader = False
        self.players_in_room = []
        self.player_colors = {}
        self.my_color = None
        self.used_colors = set()
        
        # Clear any waiting flags
        if hasattr(self, '_waiting_for_players_ready'):
            self._waiting_for_players_ready = False
        
        # Reset UI elements to initial state
        if hasattr(self, 'startPageCombo'):
            self.startPageCombo.setCurrentIndex(0)
        if hasattr(self, 'endPageCombo'):
            self.endPageCombo.setCurrentIndex(0)
        if hasattr(self, 'customStartPageEdit'):
            self.customStartPageEdit.clear()
        if hasattr(self, 'customEndPageEdit'):
            self.customEndPageEdit.clear()
        
        # Hide room-related UI elements
        if hasattr(self, 'roomAndColorFrame'):
            self.roomAndColorFrame.hide()
        if hasattr(self, 'gameConfigFrame'):
            self.gameConfigFrame.hide()
        if hasattr(self, 'gameSelectionDisplay'):
            self.gameSelectionDisplay.hide()
        if hasattr(self, 'startGameButton'):
            self.startGameButton.hide()
        if hasattr(self, 'roomInfoFrame'):
            self.roomInfoFrame.hide()
        
        # Show the host/join sections again
        self.show_host_join_sections()
        
        # Reset button states
        if hasattr(self, 'hostGameButton'):
            self.hostGameButton.setEnabled(True)
            self.hostGameButton.setText("Create Room")
        if hasattr(self, 'joinGameButton'):
            self.joinGameButton.setEnabled(True)
            self.joinGameButton.setText("Join Room")
        
        # Clear room code input
        if hasattr(self, 'roomCodeInput'):
            self.roomCodeInput.clear()
        
        # Reset color picker if it exists
        if hasattr(self, 'color_picker'):
            self.color_picker.reset_selection()
        if hasattr(self, 'color_scroll'):
            self.color_scroll.hide()
        
        # Update server status
        self.update_server_status()
        
        print("✅ Multiplayer page state reset for leave room - network connection preserved")
    
    def reset_for_exit(self):
        """CRITICAL FIX: Complete state reset when exiting multiplayer games"""
        print("🔄 CRITICAL: Resetting multiplayer page state for exit...")
        
        # Disconnect from network and clean up connections
        if hasattr(self, 'network_manager') and self.network_manager:
            try:
                self.network_manager.disconnect_from_server()
                print("🔌 Disconnected from network manager")
            except Exception as e:
                print(f"⚠️ Error disconnecting network manager: {e}")
        
        # Reset all state variables to initial values
        self.current_room_code = None
        self.player_name = None
        self.is_leader = False
        self.players_in_room = []
        self.player_colors = {}
        self.my_color = None
        self.used_colors = set()
        
        # Clear any waiting flags
        if hasattr(self, '_waiting_for_players_ready'):
            self._waiting_for_players_ready = False
        
        # Reset UI elements to initial state
        if hasattr(self, 'startPageCombo'):
            self.startPageCombo.setCurrentIndex(0)
        if hasattr(self, 'endPageCombo'):
            self.endPageCombo.setCurrentIndex(0)
        if hasattr(self, 'customStartPageEdit'):
            self.customStartPageEdit.clear()
        if hasattr(self, 'customEndPageEdit'):
            self.customEndPageEdit.clear()
        
        # Hide all room-related UI elements
        if hasattr(self, 'roomAndColorFrame'):
            self.roomAndColorFrame.hide()
        if hasattr(self, 'gameConfigFrame'):
            self.gameConfigFrame.hide()
        if hasattr(self, 'gameSelectionDisplay'):
            self.gameSelectionDisplay.hide()
        if hasattr(self, 'startGameButton'):
            self.startGameButton.hide()
        
        # Show the host/join sections again
        self.show_host_join_sections()
        
        # Reset button states
        if hasattr(self, 'hostGameButton'):
            self.hostGameButton.setEnabled(True)
            self.hostGameButton.setText("Create Room")
        if hasattr(self, 'joinGameButton'):
            self.joinGameButton.setEnabled(True)
            self.joinGameButton.setText("Join Room")
        
        # Clear room code input
        if hasattr(self, 'roomCodeInput'):
            self.roomCodeInput.clear()
        
        # Clear any countdown dialogs
        if hasattr(self, 'countdown_dialogs'):
            for dialog in self.countdown_dialogs:
                try:
                    dialog.close()
                except:
                    pass
            self.countdown_dialogs.clear()
        
        # Reset color picker if it exists
        if hasattr(self, 'color_picker'):
            self.color_picker.reset_selection()
        if hasattr(self, 'color_scroll'):
            self.color_scroll.hide()
        
        print("✅ CRITICAL: Multiplayer page state completely reset for exit")
    
    def on_kicked_for_inactivity(self, reason):
        """Handle being kicked for inactivity"""
        print(f"⏰ Kicked for inactivity: {reason}")
        QMessageBox.warning(self, "Disconnected", f"You were disconnected due to inactivity.\nReason: {reason}")
        self.reset_for_exit()
    
    def on_room_closed(self, reason):
        """Handle room being closed"""
        print(f"🚪 Room closed: {reason}")
        QMessageBox.information(self, "Room Closed", f"The room was closed.\nReason: {reason}")
        self.reset_for_exit()
    
    def on_player_disconnected(self, player_name, message):
        """Handle another player disconnecting"""
        print(f"🔌 Player disconnected: {player_name} - {message}")
        # Show a brief notification
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(self, "Player Disconnected", f"{player_name} has disconnected from the game.\n{message}")
    
    def on_player_reconnected(self, player_name, message):
        """Handle another player reconnecting"""
        print(f"🔄 Player reconnected: {player_name} - {message}")
        # Show a brief notification
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(self, "Player Reconnected", f"{player_name} has reconnected to the game.\n{message}")
    
    def _validate_room_exists(self, room_code):
        """Validate that a room with the given code exists"""
        try:
            # Check if we have a network manager and it's connected
            if not hasattr(self, 'network_manager') or not self.network_manager.connected_to_server:
                # If not connected, try to connect first
                if hasattr(self.network_manager, 'connect_to_server'):
                    self.network_manager.connect_to_server()
                    # Give it a moment to connect
                    import time
                    time.sleep(0.5)
            
            # Use the network manager to check if room exists
            if hasattr(self.network_manager, 'check_room_exists'):
                return self.network_manager.check_room_exists(room_code)
            else:
                # Fallback: assume room exists and let server handle validation
                return True
                
        except Exception as e:
            print(f"❌ Error validating room existence: {e}")
            # If validation fails, assume room exists and let server handle it
            return True
    
    def clear_waiting_for_players(self):
        """Clear the waiting for players flag to allow starting new games"""
        if hasattr(self, '_waiting_for_players_ready'):
            self._waiting_for_players_ready = False
            print("🔄 Cleared waiting for players flag - can now start new games")
            # Update button state
            self.update_start_game_button_state()
    
    def on_player_play_again(self):
        """Handle when a player hits 'Play Again' - clear waiting flag for leader"""
        if self.is_leader and hasattr(self, '_waiting_for_players_ready') and self._waiting_for_players_ready:
            self._waiting_for_players_ready = False
            print("🔄 Player hit 'Play Again' - clearing waiting flag for leader")
            self.update_start_game_button_state()
    
    def update_players_grid(self, players):
        """Update the players grid display"""
        print(f"🎨 DEBUG: update_players_grid called with players: {players}")
        print(f"🎨 DEBUG: Current player_colors: {self.player_colors}")
        print(f"🎨 DEBUG: Number of player labels: {len(self.playerLabels)}")
        
        # Clear all labels first
        for label in self.playerLabels:
            label.setText("")
            label.hide()
        
        # Only show boxes for actual players (1-10)
        for i, player in enumerate(players[:10]):  # Limit to 10 players
            if i < len(self.playerLabels):
                label = self.playerLabels[i]
                
                # Clean player name (remove leader tag for color lookup)
                clean_name = player.replace(" (Leader)", "")
                
                # Get player color if available, use default gray if not set
                player_color = self.player_colors.get(clean_name, "#CCCCCC")  # Default gray
                print(f"🎨 DEBUG: Player {clean_name} -> color {player_color}")
                
                # Update label text and styling
                label.setText(player)
                label.setStyleSheet(f"""
                    QLabel {{
                        background-color: {player_color};
                        border: 2px solid {player_color};
                        border-radius: 8px;
                        padding: 8px;
                        font-size: 12px;
                        font-weight: bold;
                        color: #000000;
                        min-height: 40px;
                    }}
                    QLabel:hover {{
                        border: 2px solid #ffffff;
                        /* box-shadow not supported in Qt stylesheets */
                    }}
                """)
                label.show()
                print(f"🎨 DEBUG: Updated label {i} with player: {player}")
        
        print(f"🎨 DEBUG: Grid update completed. Showing {len(players)} players")
        # Don't show any empty slots - only show boxes when players actually join
    
    def show_room_info(self, title, players):
        """Show room information"""
        self.roomInfoLabel.setText(title)
        self.update_players_grid(players)
        
        # Show room and color picker section
        self.roomAndColorFrame.show()
        self.color_scroll.show()  # Explicitly show the color picker scroll area
        
        # CRITICAL FIX: Ensure color picker is visible and properly initialized
        if hasattr(self, 'color_picker'):
            self.color_picker.show()
            # Reset color picker state to ensure it's ready for selection
            self.color_picker.reset_selection()
            # Update used colors to reflect current room state
            self._update_used_colors()
        
        # Show game configuration for all players, but with different permissions
        self.gameConfigFrame.show()
        
        if self.is_leader:
            # Leader can modify settings
            print(f"🏆 LEADERSHIP: Enabling leader controls - is_leader={self.is_leader}")
            self.gameSelectionDisplay.hide()
            self.startGameButton.show()
            self.startPageCombo.setEnabled(True)
            self.endPageCombo.setEnabled(True)
            # CRITICAL FIX: Also enable custom edit boxes for leader
            self.customStartPageEdit.setEnabled(True)
            self.customEndPageEdit.setEnabled(True)
            print(f"🏆 LEADERSHIP: Custom edit boxes enabled: start={self.customStartPageEdit.isEnabled()}, end={self.customEndPageEdit.isEnabled()}")
            # Update start game button state based on players and configuration
            self.update_start_game_button_state()
        else:
            # Non-leader can see but not modify settings
            print(f"🏆 LEADERSHIP: Disabling non-leader controls - is_leader={self.is_leader}")
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
        
        # Extract player colors from the players list
        for player_data in players_list:
            if isinstance(player_data, dict):
                player_name_data = player_data.get('display_name', '')
                player_color = player_data.get('player_color')
                if player_color:
                    self.player_colors[player_name_data] = player_color
                    print(f"🎨 Loaded existing color for {player_name_data}: {player_color}")
        
        # Update used colors tracking
        self._update_used_colors()
        
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
    
    def on_player_joined(self, player_name, players_list):
        """Handle player join event"""
        print(f"🎨 UI RECEIVED: Player {player_name} joined with players list: {players_list}")
        
        # Update our local player list with the server's authoritative list
        self.players_in_room = [p['display_name'] for p in players_list]
        
        # Update player colors from server data
        for player_data in players_list:
            player_name_from_data = player_data['display_name']
            player_color = player_data.get('player_color')
            if player_color:  # Only update if player has a color
                self.player_colors[player_name_from_data] = player_color
                print(f"🎨 UI RECEIVED: Updated color for {player_name_from_data}: {player_color}")
            else:
                # Remove color for players who don't have one (like newly joined players)
                if player_name_from_data in self.player_colors:
                    del self.player_colors[player_name_from_data]
                    print(f"🎨 UI RECEIVED: Removed color for {player_name_from_data} (no color assigned)")
        
        print(f"🎨 UI RECEIVED: Current players_in_room: {self.players_in_room}")
        print(f"🎨 UI RECEIVED: Current player_colors: {self.player_colors}")
        
        # Update the grid display
        if hasattr(self, 'update_players_grid'):
            # Format players list with leader tag
            formatted_players = []
            for p in players_list:
                if p.get('is_host', False):
                    formatted_players.append(f"{p['display_name']} (Leader)")
                else:
                    formatted_players.append(p['display_name'])
            
            self.update_players_grid(formatted_players)
        
        # Clear waiting for players flag if we were waiting
        self.clear_waiting_for_players()
        
        # Update start game button state
        self.update_start_game_button_state()
    
    def on_player_left(self, player_name, players_list):
        """Handle player leave event"""
        print(f"🔄 CRITICAL: on_player_left called - Player {player_name} left the room")
        print(f"🔄 CRITICAL: Remaining players: {[p['display_name'] for p in players_list]}")
        print(f"🔄 CRITICAL: Current players_in_room before update: {self.players_in_room}")
        
        # Update our local player list with the server's authoritative list
        self.players_in_room = [p['display_name'] for p in players_list]
        print(f"🔄 CRITICAL: Updated players_in_room to: {self.players_in_room}")
        
        # Update the players grid display
        if hasattr(self, 'update_players_grid'):
            print(f"🔄 CRITICAL: Calling update_players_grid with {len(players_list)} players")
            # Format players list with leader tag
            formatted_players = []
            for p in players_list:
                if p.get('is_host', False):
                    formatted_players.append(f"{p['display_name']} (Leader)")
                else:
                    formatted_players.append(p['display_name'])
            
            print(f"🔄 CRITICAL: Formatted players for grid: {formatted_players}")
            self.update_players_grid(formatted_players)
        else:
            print(f"🔄 CRITICAL: update_players_grid method not found!")
        
        # Update start game button state
        self.update_start_game_button_state()
        
        # Show notification
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(self, "Player Left", f"{player_name} has left the room.")
    
    def on_host_transferred(self, new_host_id, new_host_name):
        """Handle host transfer event"""
        print(f"🏆 LEADERSHIP: MultiplayerPage received host_transferred - new_host_id: {new_host_id}, new_host_name: {new_host_name}")
        print(f"🏆 LEADERSHIP: Current player_name: {self.player_name}")
        
        # Update our leadership status
        if hasattr(self, 'network_manager') and hasattr(self.network_manager, 'sio'):
            # Check if we are the new host (this is a simple check, in real implementation
            # you'd want to track socket IDs properly)
            if new_host_name == self.player_name:
                self.is_leader = True
                print(f"🏆 LEADERSHIP: Player {self.player_name} is now the leader")
                QMessageBox.information(self, "Leadership Transferred", 
                                      "You are now the room leader!")
            else:
                self.is_leader = False
                print(f"🏆 LEADERSHIP: Player {new_host_name} is now the leader, {self.player_name} is not leader")
                QMessageBox.information(self, "Leadership Transferred", 
                                      f"{new_host_name} is now the room leader.")
        else:
            print(f"🏆 LEADERSHIP: No network manager available for leadership transfer")
        
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
            print(f"🎯 DEBUG: Refreshing room info after host transfer - is_leader={self.is_leader}")
            self.show_room_info(f"Room Code: {self.current_room_code}", self.players_in_room)
            
            # CRITICAL FIX: Update custom edit boxes based on current combo selections and leadership
            if self.is_leader:
                self.on_game_config_changed()
    
    def on_room_deleted(self):
        """Handle room deletion event"""
        print(f"🗑️ WikiRace: [{time.time():.3f}] Room deleted - performing complete cleanup")
        QMessageBox.information(self, "Room Closed", 
                              "The room has been closed because all players have left.")
        # CRITICAL FIX: Reset to initial state with complete cleanup to prevent rejoin bugs
        self.on_leave_room_clicked()
    
    def cleanup_countdown_dialogs(self):
        """Clean up any existing countdown dialogs"""
        print(f"🎬 DEBUG: Cleaning up {len(self.countdown_dialogs)} countdown dialogs")
        
        # Close and remove all countdown dialogs from the list
        for dialog in self.countdown_dialogs:
            try:
                if hasattr(dialog, 'close'):
                    dialog.close()
                if hasattr(dialog, 'deleteLater'):
                    dialog.deleteLater()
            except:
                pass
        self.countdown_dialogs.clear()
        
        # Also clear the single dialog reference if it exists
        if hasattr(self, 'countdown_dialog'):
            try:
                if self.countdown_dialog and hasattr(self.countdown_dialog, 'close'):
                    print(f"🎬 DEBUG: Closing single countdown dialog reference")
                    self.countdown_dialog.close()
                    self.countdown_dialog.deleteLater()
            except:
                pass
            self.countdown_dialog = None
        
        print(f"🎬 DEBUG: Cleaned up all countdown dialogs")
    
    def hideEvent(self, event):
        """Handle page hide event - clean up countdown dialogs"""
        super().hideEvent(event)
        # CRITICAL FIX: Clean up any active countdown dialogs when page is hidden
        self.cleanup_countdown_dialogs()
    
    def showEvent(self, event):
        """Handle page show event - clean up any lingering countdown dialogs"""
        super().showEvent(event)
        # CRITICAL FIX: Clean up any lingering countdown dialogs when page is shown
        self.cleanup_countdown_dialogs()
    
    def show_debug_countdown_info(self):
        """Debug method to show information about active countdown dialogs"""
        print(f"🎬 DEBUG: Active countdown dialogs: {len(self.countdown_dialogs)}")
        for i, dialog in enumerate(self.countdown_dialogs):
            if hasattr(dialog, 'dialog_id'):
                print(f"  Dialog {i}: {dialog.dialog_id} (count: {dialog.current_count})")
            else:
                print(f"  Dialog {i}: No ID available")
    
    def on_game_starting(self, countdown_data):
        """Handle game starting countdown event"""
        print(f"🎬 DEBUG: Received game_starting event with data: {countdown_data}")
        
        # Lock colors during game
        self.lock_colors()
        
        # CRITICAL FIX: Clean up any existing countdown dialogs first
        self.cleanup_countdown_dialogs()
        
        # CRITICAL FIX: Check if we already have a countdown dialog active
        if hasattr(self, 'countdown_dialog') and self.countdown_dialog and not self.countdown_dialog.isHidden():
            print(f"🎬 DEBUG: Countdown dialog already active, skipping duplicate")
            return
        
        try:
            from src.gui.CountdownDialog import CountdownDialog
            
            print(f"🎬 DEBUG: Creating countdown dialog... (Total dialogs: {len(self.countdown_dialogs)})")
            # Create new countdown dialog
            countdown_dialog = CountdownDialog(
                countdown_data.get('countdown_seconds', 5),
                countdown_data.get('message', 'Get ready!'),
                parent=self
            )
            
            # Add to list for debugging
            self.countdown_dialogs.append(countdown_dialog)
            print(f"🎬 DEBUG: Added dialog to list. Total dialogs: {len(self.countdown_dialogs)}")
            
            # Show debug info about all dialogs
            self.show_debug_countdown_info()
            
            # Store reference to prevent garbage collection
            self.countdown_dialog = countdown_dialog
            
            print(f"🎬 DEBUG: Showing countdown dialog...")
            # Show the countdown dialog
            countdown_dialog.exec()  # Use exec() to make it modal and blocking
            
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
        
        # Use server's player data if available (includes colors), otherwise build from local data
        if 'players' not in game_data or not game_data['players']:
            # Fallback: build from local data if server didn't provide player data
            game_data['players'] = []
            for player_name in self.players_in_room:
                # Remove "(Leader)" suffix for processing
                clean_name = player_name.replace(" (Leader)", "")
                is_host = "(Leader)" in player_name
                player_color = self.player_colors.get(clean_name, '#CCCCCC')
                game_data['players'].append({
                    'name': clean_name,
                    'is_host': is_host,
                    'player_color': player_color
                })
        # Server provided player data - use it as is (includes colors)
        
        print(f"🎮 DEBUG: Players in game: {game_data['players']}")
        
        # CRITICAL: Clean up ALL existing game tabs first to prevent multiple instances
        print(f"🧹 DEBUG: Cleaning up ALL existing game tabs before creating new one...")
        game_tabs_to_remove = []
        
        for i in range(self.tabWidget.count()):
            widget = self.tabWidget.widget(i)
            if hasattr(widget, '__class__') and 'MultiplayerGamePage' in str(widget.__class__):
                game_tabs_to_remove.append(i)
                print(f"🧹 DEBUG: Found existing game tab at index {i} - marking for removal")
        
        # Remove all existing game tabs (in reverse order to maintain indices)
        for i in reversed(game_tabs_to_remove):
            widget = self.tabWidget.widget(i)
            # Disconnect signals from old instances before removing
            if hasattr(widget, 'disconnect_network_signals'):
                widget.disconnect_network_signals()
            print(f"🧹 DEBUG: Removing existing game tab at index {i}")
            self.tabWidget.removeTab(i)
        
        print(f"🧹 DEBUG: Cleaned up {len(game_tabs_to_remove)} existing game tabs")
        
        # Create new multiplayer game tab if no existing one or reuse failed
        try:
            print(f"🎮 DEBUG: Importing MultiplayerGamePage...")
            from src.gui.MultiplayerGamePage import MultiplayerGamePage
            
            print(f"🎮 DEBUG: Creating new multiplayer game page...")
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
        
        # Reset join button if it's in "Joining..." state
        if self.joinGameButton.text() == "Joining...":
            self.joinGameButton.setEnabled(True)
            self.joinGameButton.setText("Join Room")
    
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
        
        # CRITICAL FIX: If we were in a room, perform complete cleanup to prevent rejoin bugs
        if self.current_room_code:
            print(f"🔌 WikiRace: [{time.time():.3f}] Reconnection failed - cleaning up room state")
            self.on_leave_room_clicked()
        
        QMessageBox.warning(self, "Connection Lost", 
                          "Could not reconnect to the multiplayer server.\n"
                          "You have been removed from your room.\n"
                          "Please rejoin manually if the room still exists.")
    
    def load_server_config(self):
        """Load server configuration from MultiplayerConfig"""
        try:
            from src.logic.MultiplayerConfig import multiplayer_config
            self.multiplayer_config = multiplayer_config
            
            # Convert to the expected format for backward compatibility
            self.server_config = {
                'server_host': self.multiplayer_config.server.host,
                'server_port': self.multiplayer_config.server.port,
                'auto_reconnect': self.multiplayer_config.reconnection.enabled,
                'max_reconnection_attempts': self.multiplayer_config.reconnection.max_attempts,
                'reconnection_delay': self.multiplayer_config.reconnection.initial_delay,
                'max_reconnection_delay': self.multiplayer_config.reconnection.max_delay,
                'connection_timeout': self.multiplayer_config.server.connection_timeout
            }
        except Exception as e:
            print(f"Failed to load server config: {e}")
            # Use default configuration
            self.server_config = {
                'server_host': '127.0.0.1',
                'server_port': 8001,
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
    
    def on_player_color_updated(self, player_name, color_hex, color_name):
        """Handle player color update from server"""
        print(f"🎨 UI RECEIVED: Player {player_name} updated color to {color_name} ({color_hex})")
        print(f"🎨 UI RECEIVED: Current players_in_room: {self.players_in_room}")
        print(f"🎨 UI RECEIVED: Current player_colors: {self.player_colors}")
        
        # Update local color mapping
        self.player_colors[player_name] = color_hex
        print(f"🎨 Updated player_colors: {self.player_colors}")
        
        # Update used colors tracking
        self._update_used_colors()
        
        # Format players list with leader tag for display
        formatted_players = []
        for player in self.players_in_room:
            clean_name = player.replace(" (Leader)", "")
            if clean_name == player_name:
                # Check if this player is the leader by looking at the original player name
                if "(Leader)" in player:
                    formatted_players.append(f"{player_name} (Leader)")
                else:
                    formatted_players.append(player_name)
            else:
                formatted_players.append(player)
        
        # Update the players grid to show the new color
        self.update_players_grid(formatted_players)
        
        # Force UI update
        self.update()
        self.repaint()
        
        # Use a timer to refresh the display after a short delay
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(100, lambda: self.update_players_grid(formatted_players))
    
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
            print(f"❌ Error starting game: {e}")
            QMessageBox.critical(self, "Error", f"Failed to start game: {e}")
            # Re-enable button on error
            self.startGameButton.setEnabled(True)
            self.update_start_game_button_state()
            
        # Reset button text
        self.startGameButton.setText("Start Game")
    
    def on_color_selected(self, color_hex, color_name):
        """Handle player color selection"""
        if not self.player_name or not self.current_room_code:
            return
        
        print(f"🎨 Player {self.player_name} selected color: {color_name} ({color_hex})")
        
        # Check for color conflicts
        if color_hex in self.used_colors:
            print(f"⚠️ Color {color_name} is already used by another player")
            # Find an available color
            available_colors = self._get_available_colors()
            if available_colors:
                color_hex, color_name = available_colors[0]
                print(f"🔄 Auto-selecting available color: {color_name} ({color_hex})")
            else:
                print(f"❌ No available colors, keeping current selection")
                return
        
        # Store the color locally
        self.my_color = color_hex
        self.player_colors[self.player_name] = color_hex
        
        # Update used colors tracking
        self._update_used_colors()
        
        # Send color update to server
        if hasattr(self.network_manager, 'send_player_color'):
            self.network_manager.send_player_color(color_hex, color_name)
        
        # Format players list with leader tag for display
        formatted_players = []
        for player in self.players_in_room:
            clean_name = player.replace(" (Leader)", "")
            if clean_name == self.player_name:
                # This is the current player - check if they are the leader
                if self.is_leader:
                    formatted_players.append(f"{self.player_name} (Leader)")
                else:
                    formatted_players.append(self.player_name)
            else:
                formatted_players.append(player)
        
        # Update the players grid to show the new color
        self.update_players_grid(formatted_players)
    
    def _update_used_colors(self):
        """Update the used colors set and notify color picker"""
        self.used_colors = set(self.player_colors.values())
        self.color_picker.update_used_colors(list(self.used_colors))
        print(f"🎨 Updated used colors: {self.used_colors}")
    
    def _get_available_colors(self):
        """Get list of available colors that aren't used"""
        # Get all possible colors from the color picker
        all_colors = []
        if hasattr(self.color_picker, 'light_colors'):
            all_colors.extend(self.color_picker.light_colors)
        if hasattr(self.color_picker, 'dark_colors'):
            all_colors.extend(self.color_picker.dark_colors)
        
        # Filter out used colors
        available = []
        for color_hex, color_name in all_colors:
            if color_hex not in self.used_colors:
                available.append((color_hex, color_name))
        
        return available
    
    def lock_colors(self):
        """Lock color selection during game"""
        self.color_picker.setEnabled(False)
        print("🔒 Colors locked during game")
    
    def unlock_colors(self):
        """Unlock color selection between games"""
        self.color_picker.setEnabled(True)
        print("🔓 Colors unlocked between games")
    
    def on_game_ended(self, results):
        """Handle game end event - unlock colors for next game"""
        print("🏁 Game ended - unlocking colors for next game")
        self.unlock_colors()
