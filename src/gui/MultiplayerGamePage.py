"""
MultiplayerGamePage - Wrapper for SoloGamePage with multiplayer functionality

This class extends the solo game experience to support real-time multiplayer
by wrapping SoloGamePage and adding multiplayer-specific UI elements.
"""

import time
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QSplitter, 
                            QLabel, QListWidget, QListWidgetItem, QFrame,
                            QScrollArea, QProgressBar)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QSize
from PyQt6.QtGui import QFont
from src.gui.SoloGamePage import SoloGamePage
from src.logic.ThemeManager import theme_manager
from src.logic.Network import NetworkManager


class PlayerProgressWidget(QWidget):
    """Widget showing individual player progress in the sidebar"""
    
    def __init__(self, player_name, is_host=False, parent=None):
        super().__init__(parent)
        self.player_name = player_name
        self.is_host = is_host
        self.current_page = "Starting..."
        self.links_used = 0
        self.is_completed = False
        self.completion_time = None
        
        self.initUI()
        self.apply_theme()
    
    def initUI(self):
        # Horizontal layout: Player info on left, progress bar on right
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(12)
        
        # Left side: Player info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)
        
        # Player name with host indicator
        name_layout = QHBoxLayout()
        name_layout.setContentsMargins(0, 0, 0, 0)
        name_layout.setSpacing(6)
        
        host_icon = QLabel("👑" if self.is_host else "🔹")
        host_icon.setFont(QFont("Inter", 12))
        name_layout.addWidget(host_icon)
        
        name_label = QLabel(self.player_name)
        name_label.setFont(QFont("Inter", 12, QFont.Weight.Bold))
        name_layout.addWidget(name_label)
        name_layout.addStretch()
        
        info_layout.addLayout(name_layout)
        
        # Current page (smaller text)
        self.page_label = QLabel(self.current_page)
        self.page_label.setFont(QFont("Inter", 9))
        self.page_label.setWordWrap(True)
        info_layout.addWidget(self.page_label)
        
        # Links count
        self.links_label = QLabel(f"Links: {self.links_used}")
        self.links_label.setFont(QFont("Inter", 9))
        info_layout.addWidget(self.links_label)
        
        layout.addLayout(info_layout)
        
        # Right side: Progress bar
        progress_container = QVBoxLayout()
        progress_container.setSpacing(4)
        
        # Progress label
        progress_label = QLabel("Progress")
        progress_label.setFont(QFont("Inter", 9, QFont.Weight.Medium))
        progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        progress_container.addWidget(progress_label)
        
        # Progress bar (horizontal, on the right)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)  # Changed back to 100 for percentage
        self.progress_bar.setValue(0)
        self.progress_bar.setMinimumHeight(16)
        self.progress_bar.setMinimumWidth(150)
        progress_container.addWidget(self.progress_bar)
        
        layout.addLayout(progress_container)
        
        # Set fixed height for consistent sizing
        self.setFixedHeight(70)
        self.setMinimumWidth(350)
    
    def apply_theme(self):
        """Apply theme-based styling with card-style containers"""
        styles = theme_manager.get_theme_styles()
        
        if styles['is_dark']:
            # Dark theme card styling with shadow effect
            self.setStyleSheet(f"""
                PlayerProgressWidget {{
                    background-color: {styles['secondary_background']};
                    border: 2px solid {styles['border_color']};
                    border-radius: 12px;
                    margin: 8px;
                    padding: 4px;
                }}
                PlayerProgressWidget:hover {{
                    border-color: {styles['border_hover']};
                    background-color: {styles['tertiary_background']};
                }}
                QLabel {{
                    color: {styles['text_color']};
                    background-color: transparent;
                    border: none;
                }}
            """)
            
            # Dark theme progress bar with Wikipedia link blue
            progress_style = f"""
                QProgressBar {{
                    border: 2px solid {styles['border_color']};
                    border-radius: 10px;
                    text-align: center;
                    font-weight: bold;
                    font-size: 11px;
                    color: white;
                    background-color: #1a1a1a;
                    margin: 4px 0px;
                }}
                QProgressBar::chunk {{
                    background-color: #0645ad;
                    border-radius: 8px;
                    margin: 1px;
                }}
            """
        else:
            # Light theme card styling with shadow effect
            self.setStyleSheet(f"""
                PlayerProgressWidget {{
                    background-color: {styles['background_color']};
                    border: 2px solid {styles['border_color']};
                    border-radius: 12px;
                    margin: 8px;
                    padding: 4px;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                }}
                PlayerProgressWidget:hover {{
                    border-color: {styles['border_hover']};
                    background-color: {styles['secondary_background']};
                    box-shadow: 0 6px 12px rgba(0,0,0,0.15);
                }}
                QLabel {{
                    color: {styles['text_color']};
                    background-color: transparent;
                    border: none;
                }}
            """)
            
            # Light theme progress bar with Wikipedia link blue
            progress_style = f"""
                QProgressBar {{
                    border: 2px solid {styles['border_color']};
                    border-radius: 10px;
                    text-align: center;
                    font-weight: bold;
                    font-size: 11px;
                    color: white;
                    background-color: #f0f0f0;
                    margin: 4px 0px;
                }}
                QProgressBar::chunk {{
                    background-color: #0645ad;
                    border-radius: 8px;
                    margin: 1px;
                }}
            """
        
        # Apply progress bar styling
        self.progress_bar.setStyleSheet(progress_style)
    
    def update_progress(self, current_page, links_used, is_completed=False, completion_time=None):
        """SINGLE UPDATE METHOD: Updates both sidebar and progress bar with same data"""
        # Store state
        self.current_page = current_page
        self.links_used = links_used
        self.is_completed = is_completed
        self.completion_time = completion_time
        
        # Update both UI elements with identical data
        self.page_label.setText(current_page)
        self.links_label.setText(f"Links: {links_used}")
        
        # Progress bar shows exact same count as sidebar
        if is_completed:
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(100)
            self.progress_bar.setFormat("COMPLETED")
        else:
            # Both sidebar and progress bar show the same number
            self.progress_bar.setRange(0, 50)
            self.progress_bar.setValue(links_used)
            self.progress_bar.setFormat(f"{links_used} links")
        
        print(f"📊 UI SYNC: {self.player_name} -> Sidebar: {links_used}, Progress: {links_used}")
    
    def get_debug_info(self):
        """Debug method to check current state"""
        return {
            'player_name': self.player_name,
            'current_page': self.current_page,
            'links_used': self.links_used,
            'is_completed': self.is_completed,
            'sidebar_text': self.links_label.text(),
            'progress_value': self.progress_bar.value(),
            'progress_format': self.progress_bar.format()
        }


class MultiplayerGamePage(QWidget):
    """Multiplayer game page that wraps SoloGamePage with multiplayer functionality"""
    
    # Signals for communication with parent
    game_completed = pyqtSignal(dict)  # Emitted when game is completed
    player_progress_updated = pyqtSignal(str, str, int)  # player_name, current_page, links_used
    
    def __init__(self, tabWidget, network_manager: NetworkManager, game_data: dict, parent=None):
        super().__init__(parent)
        self.tabWidget = tabWidget
        self.network_manager = network_manager
        self.game_data = game_data
        
        # Game state
        self.players = {}  # player_name -> PlayerProgressWidget
        self.game_started = False
        self.game_finished = False  # Changed variable name to avoid conflict with signal
        self.start_time = None
        self.first_link_clicked = False  # Track if first link has been clicked
        
        # Connect to network signals
        self.connect_network_signals()
        
        # Initialize UI
        self.initUI()
        self.apply_theme()
        
        # Connect to theme changes
        theme_manager.theme_changed.connect(self.apply_theme)
    
    def connect_network_signals(self):
        """Connect to network manager signals"""
        self.network_manager.game_starting.connect(self.on_game_starting)
        self.network_manager.game_started.connect(self.on_game_started)
        self.network_manager.player_progress.connect(self.on_player_progress)
        self.network_manager.game_ended.connect(self.on_game_ended)
        self.network_manager.player_completed.connect(self.on_player_completed)
    
    def initUI(self):
        """Initialize the multiplayer game UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Create main splitter (vertical - progress on top, game on bottom)
        self.splitter = QSplitter(Qt.Orientation.Vertical)
        layout.addWidget(self.splitter)
        
        # Create top progress bar for player progress
        self.create_progress_bar()
        
        # Create main game area
        self.create_game_area()
        
        # Set splitter proportions (20% progress, 80% game)
        self.splitter.setSizes([200, 800])
        self.splitter.setStretchFactor(0, 0)  # Progress bar is fixed height
        self.splitter.setStretchFactor(1, 1)  # Game area is stretchable
    
    def create_progress_bar(self):
        """Create the multiplayer progress bar at the top"""
        # Progress bar container
        progress_frame = QFrame()
        progress_frame.setFrameStyle(QFrame.Shape.Box)
        progress_frame.setLineWidth(1)
        # Simple vertical layout for players
        progress_layout = QVBoxLayout(progress_frame)
        progress_layout.setContentsMargins(20, 12, 20, 12)
        progress_layout.setSpacing(8)
        
        # Players container - vertical layout as requested
        self.players_widget = QWidget()
        self.players_layout = QVBoxLayout(self.players_widget)
        self.players_layout.setContentsMargins(0, 0, 0, 0)
        self.players_layout.setSpacing(8)
        
        progress_layout.addWidget(self.players_widget)
        
        # Add progress bar to splitter
        self.splitter.addWidget(progress_frame)
        
        # Initialize with game data
        self.update_game_info()
        self.initialize_players()
    
    def create_game_area(self):
        """Create the main game area using SoloGamePage"""
        # Extract game data
        start_url = self.game_data.get('start_url', '')
        end_url = self.game_data.get('end_url', '')
        start_title = self.game_data.get('start_title', '')
        end_title = self.game_data.get('end_title', '')
        
        # Create SoloGamePage instance
        self.solo_game = SoloGamePage(
            self.tabWidget,
            start_url,
            end_url,
            start_title,
            end_title,
            parent=self,
            is_multiplayer=True
        )
        
        # Connect to SoloGamePage signals for navigation tracking
        self.solo_game.urlChanged.connect(self.on_url_changed)
        self.solo_game.linkClicked.connect(self.on_link_clicked)
        self.solo_game.gameCompleted.connect(self.on_solo_game_completed)
        
        # Add to splitter
        self.splitter.addWidget(self.solo_game)
    
    def update_game_info(self):
        """Update game information display"""
        # No longer needed since we removed the From/To info section
        pass
    
    def initialize_players(self):
        """Initialize player progress widgets"""
        # Get players from game data
        players_list = self.game_data.get('players', [])
        print(f"🎮 DEBUG: Initializing players from game data: {players_list}")
        
        for player_data in players_list:
            player_name = player_data.get('name', 'Unknown')
            is_host = player_data.get('is_host', False)
            
            print(f"🎮 DEBUG: Creating player widget for {player_name} (host: {is_host})")
            
            # Create player progress widget
            player_widget = PlayerProgressWidget(player_name, is_host)
            
            # Ensure progress starts at 0
            player_widget.update_progress("Starting...", 0, False, None)
            
            self.players[player_name] = player_widget
            
            # Add to layout
            self.players_layout.addWidget(player_widget)
        
        print(f"🎮 DEBUG: Initialized {len(self.players)} players: {list(self.players.keys())}")
    
    def apply_theme(self):
        """Apply theme-based styling"""
        styles = theme_manager.get_theme_styles()
        
        # Apply theme to sidebar
        sidebar = self.splitter.widget(1)  # Sidebar is second widget
        if sidebar:
            if styles['is_dark']:
                sidebar.setStyleSheet(f"""
                    QFrame {{
                        background-color: {styles['background_color']};
                        border: 1px solid {styles['border_color']};
                    }}
                    QLabel {{
                        color: {styles['text_color']};
                    }}
                    QScrollArea {{
                        background-color: {styles['background_color']};
                        border: none;
                    }}
                """)
            else:
                sidebar.setStyleSheet(f"""
                    QFrame {{
                        background-color: {styles['background_color']};
                        border: 1px solid {styles['border_color']};
                    }}
                    QLabel {{
                        color: {styles['text_color']};
                    }}
                    QScrollArea {{
                        background-color: {styles['background_color']};
                        border: none;
                    }}
                """)
    
    def start_game(self):
        """Start the multiplayer game"""
        print(f"🎮 DEBUG: Starting multiplayer game...")
        print(f"🎮 DEBUG: Network manager connected: {self.network_manager.connected_to_server}")
        print(f"🎮 DEBUG: Current room: {self.network_manager.current_room}")
        
        self.game_started = True
        self.game_finished = False  # Reset game finished flag for new race
        self.start_time = time.time()
        self.initial_page_loaded = False  # Flag to prevent initial page from counting as navigation
        
        # Re-enable navigation in solo game
        self.solo_game.setEnabled(True)
        
        # Reset all player progress to 0
        self.reset_all_progress()
        
        # Start the solo game immediately
        self.solo_game.startGame()
        
        # Send the starting page as the first progress update to server
        # This ensures server and client are in sync from the beginning
        if self.network_manager.connected_to_server:
            start_url = self.game_data.get('start_url', '')
            start_title = self.game_data.get('start_title', 'Starting...')
            print(f"📊 INITIAL PROGRESS: Sending starting page to server: {start_title}")
            print(f"📊 INITIAL PROGRESS: URL: {start_url}")
            print(f"📊 INITIAL PROGRESS: Local linksUsed: {self.solo_game.linksUsed}")
            self.network_manager.send_player_progress(start_url, start_title)
        
        # Set flag after a short delay to allow initial page load
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(1000, lambda: setattr(self, 'initial_page_loaded', True))
        
        print(f"🎮 DEBUG: Multiplayer game started successfully!")
    
    def reset_all_progress(self):
        """Reset all player progress to 0 at game start"""
        print(f"🎮 DEBUG: Resetting all player progress to 0")
        for player_name, player_widget in self.players.items():
            print(f"🎮 DEBUG: Resetting {player_name} to 0 links")
            player_widget.update_progress("Starting...", 0, False, None)
            player_widget.progress_bar.setEnabled(True)  # Re-enable progress bars
    
    def on_url_changed(self, url):
        """Handle URL changes from SoloGamePage - DIRECT LOCAL PROGRESS UPDATE"""
        if not self.game_started:
            return
        
        # Get current page title
        current_title = self.solo_game.getTitleFromUrlPath(url)
        
        # LOCAL PROGRESS BAR UPDATE: Update local player progress bar immediately (server agnostic)
        local_player_name = self.network_manager.player_name
        if local_player_name in self.players:
            # Update local player progress bar directly from SoloGamePage
            self.players[local_player_name].update_progress(
                current_title, 
                self.solo_game.linksUsed, 
                False, 
                None
            )
            print(f"📊 LOCAL PROGRESS: Updated {local_player_name} to {self.solo_game.linksUsed} links")
        
        # SERVER COMMUNICATION: Send to server for other players (separate from local updates)
        if not self.network_manager.connected_to_server:
            return
        
        # Skip sending the starting page since we already sent it in start_game()
        start_url = self.game_data.get('start_url', '')
        # Check if this is the starting page (with or without query parameters)
        is_starting_page = (url == start_url or 
                          (start_url in url and 'wikipedia.org' in url and 
                           url.split('?')[0] == start_url.split('?')[0]))
        
        if is_starting_page:
            print(f"📊 SKIPPING: Starting page already sent to server")
            print(f"📊 SKIPPING: URL: {url}")
            print(f"📊 SKIPPING: Start URL: {start_url}")
            print(f"📊 SKIPPING: Local linksUsed: {self.solo_game.linksUsed}")
            return
        
        # Send to server for other players (this is independent of local progress bar)
        print(f"📊 NAVIGATION: Sending {current_title} to server")
        print(f"📊 NAVIGATION: URL: {url}")
        print(f"📊 NAVIGATION: Local linksUsed: {self.solo_game.linksUsed}")
        self.network_manager.send_player_progress(url, current_title)
    
    def on_link_clicked(self, url, links_used):
        """Handle link clicks from SoloGamePage"""
        if not self.game_started:
            return

        # Get current page title
        current_title = self.solo_game.getTitleFromUrlPath(url)

        # LOCAL PROGRESS VALIDATION: Make sure the local progress bar is always correct
        local_player_name = self.network_manager.player_name
        if local_player_name in self.players:
            # Update local player progress bar directly from SoloGamePage
            self.players[local_player_name].update_progress(
                current_title, 
                links_used, 
                False, 
                None
            )
            print(f"📊 LOCAL PROGRESS: Updated {local_player_name} to {self.solo_game.linksUsed} links")
        
        # Update local player progress bar
        
    
    def on_solo_game_completed(self):
        """Handle solo game completion"""
        if not self.game_finished:
            self.game_finished = True
            
            # Calculate completion time
            completion_time = time.time() - self.start_time if self.start_time else 0
            
            # Update local player progress bar to show completion
            local_player_name = self.network_manager.player_name
            if local_player_name in self.players:
                self.players[local_player_name].update_progress(
                    "🏆 COMPLETED!", 
                    self.solo_game.linksUsed, 
                    True, 
                    completion_time
                )
                print(f"🏆 LOCAL COMPLETION: Updated {local_player_name} progress bar to completed")
            
            # Notify server of completion
            self.network_manager.send_game_completion(completion_time, self.solo_game.linksUsed)
    
    def on_game_starting(self, countdown_data):
        """Handle game starting countdown event from server"""
        print(f"🎬 DEBUG: MultiplayerGamePage received game_starting event: {countdown_data}")
        
        # Show countdown dialog if available
        try:
            from src.gui.CountdownDialog import CountdownDialog
            countdown_dialog = CountdownDialog(
                countdown_data.get('countdown_seconds', 5),
                countdown_data.get('message', 'Get ready!'),
                parent=self
            )
            countdown_dialog.exec()
        except Exception as e:
            print(f"❌ Failed to show countdown dialog: {e}")
            # Continue without countdown dialog
    
    def on_game_started(self, game_data):
        """Handle game start event from server"""
        print(f"🎮 DEBUG: MultiplayerGamePage received game_started event: {game_data}")
        print(f"🎮 DEBUG: Current game_started state: {self.game_started}")
        print(f"🎮 DEBUG: Current game_finished state: {self.game_finished}")
        
        # Start the multiplayer game
        self.start_game()
        print(f"🎮 DEBUG: Game started successfully, game_started is now: {self.game_started}")
    
    def on_player_progress(self, player_name, current_page, links_used):
        """SERVER UPDATE PATH: Updates for other players, skips local player to avoid conflicts"""
        print(f"📊 PROGRESS UPDATE: {player_name} -> {current_page} ({links_used} links)")
        print(f"📊 PROGRESS UPDATE: Local player: {self.network_manager.player_name}")
        print(f"📊 PROGRESS UPDATE: Local linksUsed: {self.solo_game.linksUsed}")
        
        # Validate player exists
        if player_name not in self.players:
            print(f"❌ ERROR: Player {player_name} not found in {list(self.players.keys())}")
            return
        
        # Skip local player updates from server to avoid conflicts with direct updates
        local_player_name = self.network_manager.player_name
        if player_name == local_player_name:
            print(f"📊 SKIPPING: Local player progress from server (handled directly)")
            return
        
        # Update progress widget for other players only
        print(f"📊 PROGRESS UPDATE: Updating {player_name} widget with {links_used} links")
        self.players[player_name].update_progress(current_page, links_used)
        
        # Emit signal for parent components
        self.player_progress_updated.emit(player_name, current_page, links_used)
    
    
    def on_player_completed(self, player_name, completion_time, links_used):
        """Handle player completion events"""
        if player_name in self.players:
            self.players[player_name].update_progress(
                "🏆 COMPLETED!", 
                links_used, 
                True, 
                completion_time
            )
            
            # Stop all progress bars when any player wins
            self.stop_all_progress_bars()
    
    def stop_all_progress_bars(self):
        """Stop progress tracking for all players when game ends"""
        for player_widget in self.players.values():
            if not player_widget.is_completed:
                # Freeze progress at current value for non-winners
                current_progress = player_widget.progress_bar.value()
                player_widget.progress_bar.setValue(current_progress)
                # Update styling to show game ended
                player_widget.progress_bar.setEnabled(False)
    
    def on_game_ended(self, results):
        """Handle game end event from server"""
        self.game_finished = True  # Use the boolean variable
        
        # Disable navigation in solo game
        self.solo_game.setEnabled(False)
        
        # Show results dialog
        self.show_results_dialog(results)
        
        # Emit completion signal with results
        self.game_completed.emit(results)  # Use the signal
    
    def show_results_dialog(self, results):
        """Show the multiplayer results dialog"""
        try:
            from src.gui.MultiplayerResultsDialog import MultiplayerResultsDialog
            
            # Create and show results dialog
            dialog = MultiplayerResultsDialog(results, parent=self)
            
            # Connect dialog signals
            dialog.play_again_requested.connect(self.on_play_again_requested)
            dialog.exit_to_home_requested.connect(self.on_exit_to_home_requested)
            
            dialog.exec()
            
        except Exception as e:
            print(f"❌ Failed to show results dialog: {e}")
            # Fallback: show simple message
            from PyQt6.QtWidgets import QMessageBox
            winner = results.get('winner')
            if winner:
                QMessageBox.information(self, "Game Complete", 
                                      f"🏆 {winner['player_name']} won the race!")
            else:
                QMessageBox.information(self, "Game Complete", "The race has ended!")
    
    def on_play_again_requested(self):
        """Handle play again request - return to multiplayer room"""
        print("🔄 Player requested to play again - returning to room")
        # Close the current game tab and return to multiplayer page
        self.close_game_tab()
    
    def on_exit_to_home_requested(self):
        """Handle exit to home request - leave room and go to home page"""
        print("🏠 Player requested to exit to home - leaving room")
        # Leave the room via network manager
        if hasattr(self.network_manager, 'leave_room'):
            self.network_manager.leave_room()
        
        # Close the game tab and switch to home page
        self.close_game_tab_and_go_home()
    
    def close_game_tab(self):
        """Close the current game tab and return to multiplayer page"""
        try:
            # Find the current tab index
            current_index = self.tabWidget.indexOf(self)
            if current_index >= 0:
                # Close this tab
                self.tabWidget.removeTab(current_index)
                
                # Switch to multiplayer tab (should be index 2: Home, Solo, Multiplayer)
                if self.tabWidget.count() > 2:
                    self.tabWidget.setCurrentIndex(2)  # Multiplayer tab
                    
                    # Reset the multiplayer page state to allow starting new games
                    multiplayer_widget = self.tabWidget.widget(2)
                    if hasattr(multiplayer_widget, 'reset_for_new_game'):
                        multiplayer_widget.reset_for_new_game()
                
        except Exception as e:
            print(f"❌ Error closing game tab: {e}")
    
    def close_game_tab_and_go_home(self):
        """Close the game tab and go to home page"""
        try:
            # Find the current tab index
            current_index = self.tabWidget.indexOf(self)
            if current_index >= 0:
                # Close this tab
                self.tabWidget.removeTab(current_index)
                
                # Switch to home tab (index 0)
                self.tabWidget.setCurrentIndex(0)
                
        except Exception as e:
            print(f"❌ Error closing game tab and going home: {e}")
    
    def get_game_results(self):
        """Get current game results"""
        results = []
        
        for player_name, widget in self.players.items():
            results.append({
                'player_name': player_name,
                'links_used': widget.links_used,
                'is_completed': widget.is_completed,
                'completion_time': widget.completion_time,
                'current_page': widget.current_page
            })
        
        # Sort by completion status and time
        results.sort(key=lambda x: (not x['is_completed'], x['completion_time'] or float('inf')))
        
        return results
    
    def debug_progress_state(self):
        """COMPREHENSIVE DEBUG: Check all progress states for troubleshooting"""
        print("=" * 60)
        print("🔍 PROGRESS DEBUG STATE")
        print("=" * 60)
        
        # Check local solo game state
        local_player_name = self.network_manager.player_name
        print(f"📊 LOCAL PLAYER: {local_player_name}")
        print(f"📊 SOLO GAME LINKS: {self.solo_game.linksUsed}")
        print(f"📊 SOLO GAME LABEL: {self.solo_game.linksUsedLabel.text()}")
        
        # Check all player progress widgets
        print("\n📊 PLAYER PROGRESS WIDGETS:")
        for player_name, widget in self.players.items():
            debug_info = widget.get_debug_info()
            print(f"  {player_name}:")
            print(f"    Links Used: {debug_info['links_used']}")
            print(f"    Sidebar Text: {debug_info['sidebar_text']}")
            print(f"    Progress Value: {debug_info['progress_value']}")
            print(f"    Progress Format: {debug_info['progress_format']}")
            print(f"    Current Page: {debug_info['current_page']}")
        
        # Check if there are any mismatches
        print("\n🔍 SYNC CHECK:")
        for player_name, widget in self.players.items():
            debug_info = widget.get_debug_info()
            sidebar_count = debug_info['links_used']
            progress_count = debug_info['progress_value']
            
            if sidebar_count != progress_count:
                print(f"❌ MISMATCH: {player_name} - Sidebar: {sidebar_count}, Progress: {progress_count}")
            else:
                print(f"✅ SYNCED: {player_name} - Both show {sidebar_count}")
        
        print("=" * 60)
