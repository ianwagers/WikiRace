"""
MultiplayerGamePage - Wrapper for SoloGamePage with multiplayer functionality

This class extends the solo game experience to support real-time multiplayer
by wrapping SoloGamePage and adding multiplayer-specific UI elements.
"""

import time
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QSplitter, 
                            QLabel, QListWidget, QListWidgetItem, QFrame,
                            QScrollArea, QProgressBar, QApplication)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QSize
from PyQt6.QtGui import QFont
from src.gui.SoloGamePage import SoloGamePage
from src.logic.ThemeManager import theme_manager
from src.logic.Network import NetworkManager
from src.logic.Player import Player


class PlayerProgressWidget(QWidget):
    """Widget showing individual player progress in the sidebar"""
    
    def __init__(self, player: Player, parent=None):
        super().__init__(parent)
        self.player = player
        self.player_name = player.display_name
        self.is_host = player.is_host
        self.player_color = player.player_color or "#CCCCCC"  # Default gray color
        self.current_page = "Starting..."
        self.links_used = 0
        self.is_completed = False
        self.completion_time = None
        
        # Connect to player signals
        self.player.color_changed.connect(self._on_player_color_changed)
        self.player.progress_updated.connect(self._on_player_progress_updated)
        self.player.game_finished.connect(self._on_player_game_completed)
        
        # Detect screen size for responsive design
        self.is_small_screen = self._is_small_screen()
        
        # Dynamic sizing properties - more aggressive heights
        self.min_height = 25  # Minimum height for very small spaces
        self.standard_height = 60  # Standard height for normal spaces
        self.compact_height = 35  # Compact height for small spaces
        
        self.initUI()
        self.apply_theme()
        
        # CRITICAL FIX: Ensure color is properly applied after theme is set
        if self.player_color and self.player_color != "#CCCCCC":
            print(f"🎨 DEBUG: Applying initial color {self.player_color} to {self.player_name}")
            self._apply_progress_bar_theme()
        
        # Connect to resize events for dynamic sizing
        self.installEventFilter(self)
    
    def _on_player_color_changed(self, color_hex: str, color_name: str):
        """Handle player color change from Player instance"""
        print(f"🎨 DEBUG: PlayerProgressWidget {self.player_name} received color change: {color_hex}")
        self.player_color = color_hex
        self.update_display()
        print(f"🎨 DEBUG: PlayerProgressWidget {self.player_name} color updated to {self.player_color}")
    
    def _on_player_progress_updated(self, current_page: str, links_used: int):
        """Handle player progress update from Player instance"""
        self.current_page = current_page
        self.links_used = links_used
        self.update_display()
    
    def _on_player_game_completed(self, completion_time: float, links_used: int):
        """Handle player game completion from Player instance"""
        self.is_completed = True
        self.completion_time = completion_time
        self.links_used = links_used
        self.update_display()
    
    def update_display(self):
        """Update the display based on current state"""
        # Update progress bar
        self.progress_bar.setValue(self.links_used)
        
        # Update current page display
        if hasattr(self, 'current_page_label'):
            self.current_page_label.setText(self.current_page)
        
        # Update color if changed
        if hasattr(self, 'color_indicator'):
            self.color_indicator.setStyleSheet(f"background-color: {self.player_color};")
        
        # Update completion state
        if self.is_completed:
            self.progress_bar.setStyleSheet("""
                QProgressBar {
                    background-color: #2d5a2d;
                    border: 1px solid #4a8b4a;
                    border-radius: 4px;
                    text-align: center;
                }
                QProgressBar::chunk {
                    background-color: #4a8b4a;
                    border-radius: 3px;
                }
            """)
        else:
            # Apply theme with current player color
            self._apply_progress_bar_theme()
    
    def _apply_progress_bar_theme(self):
        """Apply progress bar theme with current player color"""
        print(f"🎨 DEBUG: _apply_progress_bar_theme called for {self.player_name} with color {self.player_color}")
        styles = theme_manager.get_theme_styles()
        
        if styles['is_dark']:
            # Dark theme progress bar with player color
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
                    background-color: {self.player_color};
                    border-radius: 8px;
                    margin: 1px;
                }}
            """
        else:
            # Light theme progress bar with player color
            progress_style = f"""
                QProgressBar {{
                    border: 2px solid {styles['border_color']};
                    border-radius: 10px;
                    text-align: center;
                    font-weight: bold;
                    font-size: 11px;
                    color: black;
                    background-color: #f0f0f0;
                    margin: 4px 0px;
                }}
                QProgressBar::chunk {{
                    background-color: {self.player_color};
                    border-radius: 8px;
                    margin: 1px;
                }}
            """
        
        self.progress_bar.setStyleSheet(progress_style)
    
    def resizeEvent(self, event):
        """Handle resize events directly"""
        super().resizeEvent(event)
        print(f"🔧 PLAYER WIDGET RESIZE: {self.player_name} -> {self.width()}x{self.height()}")
        self._update_dynamic_layout()
    
    def _is_small_screen(self):
        """Detect if we're on a smaller screen (like 1920x1080p)"""
        try:
            app = QApplication.instance()
            if app:
                screen = app.primaryScreen()
                if screen:
                    geometry = screen.availableGeometry()
                    # Consider screens with height <= 1080 as small
                    return geometry.height() <= 1080
        except Exception:
            pass
        return False
    
    def eventFilter(self, obj, event):
        """Handle resize events for dynamic sizing"""
        if obj == self and event.type() == event.Type.Resize:
            self._update_dynamic_layout()
        return super().eventFilter(obj, event)
    
    def _update_dynamic_layout(self):
        """Update layout based on current widget size"""
        # Get available height from parent container
        available_height = self.parent().height() if self.parent() else self.height()
        
        # Calculate how many players we need to fit
        num_players = len(self.parent().findChildren(PlayerProgressWidget)) if self.parent() else 1
        
        # Calculate available height per player
        if num_players > 0:
            height_per_player = available_height / num_players
        else:
            height_per_player = available_height
        
        # Very aggressive height calculation - maximize game area
        if height_per_player < 80:  # Cramped space - use minimum
            target_height = self.min_height
            self._apply_compact_layout(target_height)
        elif height_per_player < 120:  # Small space - use compact
            target_height = self.compact_height
            self._apply_compact_layout(target_height)
        else:  # Normal space - use standard
            target_height = self.standard_height
            self._apply_standard_layout(target_height)
        
        # Update height constraints - use maximum height instead of fixed height
        self.setMaximumHeight(target_height)
        self.setMinimumHeight(target_height)
        # Also set the preferred size
        self.setSizePolicy(self.sizePolicy().horizontalPolicy(), self.sizePolicy().verticalPolicy())
        
        # Force geometry update
        self.updateGeometry()
        self.update()
        
        print(f"🔧 DYNAMIC RESIZE: {self.player_name} -> {height_per_player:.1f}px/player -> {target_height}px height")
    
    def _apply_compact_layout(self, height):
        """Apply compact layout for small spaces"""
        # Hide optional elements
        if hasattr(self, 'page_label'):
            self.page_label.hide()
        if hasattr(self, 'progress_label'):
            self.progress_label.hide()
        
        # Increased font sizes for better readability even in compact mode
        if hasattr(self, 'name_label'):
            self.name_label.setFont(QFont("Inter", 10, QFont.Weight.Bold))  # Increased from 8 to 12
        if hasattr(self, 'links_label'):
            self.links_label.setFont(QFont("Inter", 8))  # Increased from 6 to 10
        if hasattr(self, 'host_icon'):
            self.host_icon.setFont(QFont("Inter", 10))  # Increased from 8 to 12
        
        # Very compact progress bar
        if hasattr(self, 'progress_bar'):
            self.progress_bar.setMinimumHeight(8)
            self.progress_bar.setMinimumWidth(80)
        
        # Reduce layout spacing
        if hasattr(self, 'layout'):
            self.layout().setContentsMargins(2, 1, 2, 1)
            self.layout().setSpacing(2)
    
    def _apply_standard_layout(self, height):
        """Apply standard layout for normal spaces"""
        # Show all elements
        if hasattr(self, 'page_label'):
            self.page_label.show()
        if hasattr(self, 'progress_label'):
            self.progress_label.show()
        
        # Increased standard font sizes for better readability
        if hasattr(self, 'name_label'):
            self.name_label.setFont(QFont("Inter", 14, QFont.Weight.Bold))  # Increased from 11 to 16
        if hasattr(self, 'links_label'):
            self.links_label.setFont(QFont("Inter", 12))  # Increased from 8 to 14
        if hasattr(self, 'host_icon'):
            self.host_icon.setFont(QFont("Inter", 14))  # Increased from 11 to 16
        
        # Standard progress bar size
        if hasattr(self, 'progress_bar'):
            self.progress_bar.setMinimumHeight(14)
            self.progress_bar.setMinimumWidth(120)
        
        # Restore normal layout spacing
        if hasattr(self, 'layout'):
            self.layout().setContentsMargins(8, 4, 8, 4)
            self.layout().setSpacing(6)
    
    def initUI(self):
        # Horizontal layout: Player info on left, progress bar on right
        layout = QHBoxLayout(self)
        
        # Very aggressive margins and spacing for maximum space efficiency
        if self.is_small_screen:
            layout.setContentsMargins(4, 2, 4, 2)
            layout.setSpacing(4)
        else:
            layout.setContentsMargins(8, 4, 8, 4)
            layout.setSpacing(6)
        
        # Left side: Player info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2 if self.is_small_screen else 4)
        
        # Player name with host indicator - increased font sizes
        name_layout = QHBoxLayout()
        name_layout.setContentsMargins(0, 0, 0, 0)
        name_layout.setSpacing(4 if self.is_small_screen else 6)
        
        host_icon = QLabel("👑" if self.is_host else "🔹")
        # Increased font sizes for better readability
        icon_size = 12 if self.is_small_screen else 14
        host_icon.setFont(QFont("Inter", icon_size))
        name_layout.addWidget(host_icon)
        
        # Create color dot + name label
        name_label = QLabel(f"● {self.player_name}")
        # Increased font sizes for better readability
        name_size = 12 if self.is_small_screen else 14
        name_label.setFont(QFont("Inter", name_size, QFont.Weight.Bold))
        
        # Style the label with player color for the dot
        name_label.setStyleSheet(f"""
            QLabel {{
                color: {self.player_color};
                font-size: {name_size}px;
            }}
        """)
        
        name_layout.addWidget(name_label)
        name_layout.addStretch()
        
        info_layout.addLayout(name_layout)
        
        # Current page (smaller text) - hide on small screens to save space
        self.page_label = QLabel(self.current_page)
        if not self.is_small_screen:
            self.page_label.setFont(QFont("Inter", 12))  # Increased from 9 to 12
            self.page_label.setWordWrap(True)
            info_layout.addWidget(self.page_label)
        else:
            # Hide on small screens
            self.page_label.hide()
        
        # Links count - increased font size
        self.links_label = QLabel(f"Links: {self.links_used}")
        # Increased font sizes for better readability
        links_size = 12 if self.is_small_screen else 14
        self.links_label.setFont(QFont("Inter", links_size))
        info_layout.addWidget(self.links_label)
        
        layout.addLayout(info_layout)
        
        # Right side: Progress bar
        progress_container = QVBoxLayout()
        progress_container.setSpacing(2 if self.is_small_screen else 4)
        
        # Progress label - hide on small screens to save space
        self.progress_label = QLabel("Progress")
        if not self.is_small_screen:
            self.progress_label.setFont(QFont("Inter", 9, QFont.Weight.Medium))
            self.progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            progress_container.addWidget(self.progress_label)
        else:
            # Hide on small screens
            self.progress_label.hide()
        
        # Progress bar (horizontal, on the right)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)  # Changed back to 100 for percentage
        self.progress_bar.setValue(0)
        
        # Smaller progress bar for small screens
        if self.is_small_screen:
            self.progress_bar.setMinimumHeight(12)
            self.progress_bar.setMinimumWidth(120)
        else:
            self.progress_bar.setMinimumHeight(16)
            self.progress_bar.setMinimumWidth(150)
        
        progress_container.addWidget(self.progress_bar)
        
        layout.addLayout(progress_container)
        
        # Set initial height constraints - will be updated dynamically
        if self.is_small_screen:
            self.setMaximumHeight(self.compact_height)
            self.setMinimumHeight(self.compact_height)
            self.setMinimumWidth(280)
        else:
            self.setMaximumHeight(self.standard_height)
            self.setMinimumHeight(self.standard_height)
            self.setMinimumWidth(350)
        
        # Store references for dynamic layout updates
        self.name_label = name_label
        self.host_icon = host_icon
    
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
            
            # Dark theme progress bar with player color
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
                    background-color: {self.player_color};
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
                    /* box-shadow not supported in Qt stylesheets */
                }}
                PlayerProgressWidget:hover {{
                    border-color: {styles['border_hover']};
                    background-color: {styles['secondary_background']};
                    /* box-shadow not supported in Qt stylesheets */
                }}
                QLabel {{
                    color: {styles['text_color']};
                    background-color: transparent;
                    border: none;
                }}
            """)
            
            # Light theme progress bar with player color
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
                    background-color: {self.player_color};
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
        # Only update page label if it's visible (not hidden on small screens)
        if self.page_label.isVisible():
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
    
    def update_color(self, new_color):
        """Update the player's color and refresh styling"""
        self.player_color = new_color
        
        # Update name label color (for the color dot)
        if hasattr(self, 'name_label'):
            self.name_label.setStyleSheet(f"""
                QLabel {{
                    color: {self.player_color};
                }}
            """)
        
        self.apply_theme()  # Reapply theme with new color
    
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
        self.player_instances = {}  # player_name -> Player instance
        self.game_started = False
        self.game_finished = False  # Changed variable name to avoid conflict with signal
        self.results_dialog_shown = False  # Prevent duplicate dialogs
        self.start_time = None
        self.first_link_clicked = False  # Track if first link has been clicked
        
        # Connect to network signals
        self.connect_network_signals()
        
        # Initialize UI
        self.initUI()
        self.apply_theme()
        
        # Connect to theme changes
        theme_manager.theme_changed.connect(self.apply_theme)
    
    def _is_small_screen(self):
        """Detect if we're on a smaller screen (like 1920x1080p)"""
        try:
            app = QApplication.instance()
            if app:
                screen = app.primaryScreen()
                if screen:
                    geometry = screen.availableGeometry()
                    # Consider screens with height <= 1080 as small
                    return geometry.height() <= 1080
        except Exception:
            pass
        return False
    
    def eventFilter(self, obj, event):
        """Handle resize events for dynamic sizing"""
        if obj == self and event.type() == event.Type.Resize:
            # Update all player widgets when the main widget is resized
            print(f"🔧 MAIN WINDOW RESIZE: {self.width()}x{self.height()}")
            self._update_all_player_widgets()
        return super().eventFilter(obj, event)
    
    def _on_splitter_moved(self, pos, index):
        """Handle splitter movement to update player widget sizing"""
        # Update all player widgets when splitter is moved
        self._update_all_player_widgets()
    
    def _update_all_player_widgets(self):
        """Update all player widgets for dynamic sizing"""
        print(f"🔧 UPDATING ALL PLAYER WIDGETS: {len(self.players)} players")
        
        # Calculate optimal height for the entire progress container
        self._update_progress_container_height()
        
        for player_widget in self.players.values():
            if hasattr(player_widget, '_update_dynamic_layout'):
                player_widget._update_dynamic_layout()
        
        # Force layout update
        self.players_widget.update()
        self.players_widget.repaint()
        
        # Force parent layout to recalculate
        if hasattr(self, 'players_layout'):
            self.players_layout.update()
            self.players_layout.invalidate()
    
    def _update_progress_container_height(self):
        """Dynamically resize the progress container based on available space"""
        if not hasattr(self, 'progress_frame'):
            return
        
        # Get total available height
        total_height = self.height()
        num_players = len(self.players)
        
        if num_players == 0:
            return
        
        # Calculate optimal height for progress container
        # Use a maximum of 30% of total height for progress area
        max_progress_height = int(total_height * 0.30)
        
        # Calculate height per player
        height_per_player = max_progress_height / num_players
        
        # Determine container height based on space per player
        if height_per_player < 40:  # Very cramped
            container_height = 25 * num_players  # 25px per player
        elif height_per_player < 60:  # Cramped
            container_height = 35 * num_players  # 35px per player
        else:  # Normal
            container_height = 50 * num_players  # 50px per player
        
        # Ensure we don't exceed the maximum
        container_height = min(container_height, max_progress_height)
        
        # Set the container height
        self.progress_frame.setMaximumHeight(container_height)
        self.progress_frame.setMinimumHeight(container_height)
        
        print(f"🔧 PROGRESS CONTAINER: {total_height}px total -> {container_height}px for {num_players} players")
        print(f"🔧 PROGRESS CONTAINER: {height_per_player:.1f}px per player")
    
    def _monitor_container_size(self):
        """Continuously monitor and update container size"""
        if not hasattr(self, 'progress_frame'):
            return
        
        # Check if we need to update the container size
        current_height = self.progress_frame.height()
        total_height = self.height()
        num_players = len(self.players)
        
        if num_players == 0:
            return
        
        # Calculate what the height should be
        max_progress_height = int(total_height * 0.30)
        height_per_player = max_progress_height / num_players
        
        if height_per_player < 40:
            target_height = 25 * num_players
        elif height_per_player < 60:
            target_height = 35 * num_players
        else:
            target_height = 50 * num_players
        
        target_height = min(target_height, max_progress_height)
        
        # Update if height has changed significantly
        if abs(current_height - target_height) > 5:
            print(f"🔧 MONITOR: Updating container from {current_height}px to {target_height}px")
            self.progress_frame.setMaximumHeight(target_height)
            self.progress_frame.setMinimumHeight(target_height)
            self.progress_frame.updateGeometry()
            self.progress_frame.update()
    
    def _monitor_splitter_proportions(self):
        """Monitor and adjust splitter proportions to maximize game area"""
        if not hasattr(self, 'splitter'):
            return
        
        # Get current splitter sizes
        current_sizes = self.splitter.sizes()
        total_height = self.height()
        
        if total_height == 0:
            return
        
        # Calculate optimal progress area height (max 30% of total)
        max_progress_height = int(total_height * 0.30)
        num_players = len(self.players)
        
        if num_players == 0:
            return
        
        # Calculate required progress height
        if num_players == 1:
            required_height = 50
        elif num_players == 2:
            required_height = 80
        else:
            required_height = 100
        
        # Use the smaller of required height or max allowed
        optimal_progress_height = min(required_height, max_progress_height)
        optimal_game_height = total_height - optimal_progress_height
        
        # Update splitter if proportions are off
        current_progress = current_sizes[0]
        if abs(current_progress - optimal_progress_height) > 20:
            print(f"🔧 SPLITTER: Updating from {current_progress}px to {optimal_progress_height}px progress area")
            self.splitter.setSizes([optimal_progress_height, optimal_game_height])
    
    def _force_dynamic_update(self):
        """Force a dynamic layout update"""
        print("🔧 FORCING DYNAMIC UPDATE")
        self._update_all_player_widgets()
    
    def trigger_dynamic_resize(self):
        """Manually trigger dynamic resizing - can be called externally"""
        print("🔧 MANUAL DYNAMIC RESIZE TRIGGERED")
        self._update_all_player_widgets()
    
    def debug_player_sizes(self):
        """Debug method to check current player widget sizes"""
        print("🔍 PLAYER WIDGET SIZES DEBUG:")
        for name, widget in self.players.items():
            print(f"  {name}: {widget.width()}x{widget.height()}px")
            if hasattr(widget, 'min_height'):
                print(f"    Min: {widget.min_height}px, Compact: {widget.compact_height}px, Standard: {widget.standard_height}px")
    
    def connect_network_signals(self):
        """Connect to network manager signals"""
        self.network_manager.game_starting.connect(self.on_game_starting)
        self.network_manager.game_started.connect(self.on_game_started)
        self.network_manager.player_progress.connect(self.on_player_progress)
        self.network_manager.game_ended.connect(self.on_game_ended)
        self.network_manager.player_completed.connect(self.on_player_completed)
        self.network_manager.player_left.connect(self.on_player_left)
        self.network_manager.player_color_updated.connect(self.on_player_color_updated)
    
    def disconnect_network_signals(self):
        """Disconnect from network manager signals to prevent multiple dialogs"""
        try:
            self.network_manager.game_starting.disconnect(self.on_game_starting)
            self.network_manager.game_started.disconnect(self.on_game_started)
            self.network_manager.player_progress.disconnect(self.on_player_progress)
            self.network_manager.game_ended.disconnect(self.on_game_ended)
            self.network_manager.player_completed.disconnect(self.on_player_completed)
            self.network_manager.player_left.disconnect(self.on_player_left)
            self.network_manager.player_color_updated.disconnect(self.on_player_color_updated)
            print(f"🔌 DEBUG: Disconnected network signals for instance {id(self)}")
        except Exception as e:
            print(f"⚠️ DEBUG: Error disconnecting network signals: {e}")
    
    def closeEvent(self, event):
        """Handle widget close event - disconnect signals to prevent memory leaks"""
        print(f"🔌 DEBUG: MultiplayerGamePage closing, disconnecting signals for instance {id(self)}")
        
        # CRITICAL FIX: Proper cleanup order to prevent signal ordering issues
        try:
            # 1. Stop all timers first to prevent further updates
            self.stop_all_timers_and_progress()
            
            # 2. Disconnect network signals to prevent further network events
            self.disconnect_network_signals()
            
            # 3. Clear all player data and references
            self.players.clear()
            self.player_instances.clear()
            
            # 4. Reset game state flags
            self.game_started = False
            self.game_finished = False
            self.results_dialog_shown = False
            
            # 5. Clean up solo game if it exists
            if hasattr(self, 'solo_game') and self.solo_game:
                try:
                    self.solo_game.setEnabled(False)
                    # Disconnect solo game signals
                    if hasattr(self.solo_game, 'urlChanged'):
                        self.solo_game.urlChanged.disconnect()
                    if hasattr(self.solo_game, 'linkClicked'):
                        self.solo_game.linkClicked.disconnect()
                    if hasattr(self.solo_game, 'gameCompleted'):
                        self.solo_game.gameCompleted.disconnect()
                except Exception as e:
                    print(f"⚠️ Error cleaning up solo game: {e}")
            
            # 6. Reset multiplayer page state when exiting game
            if hasattr(self, 'tabWidget'):
                # Find the multiplayer page tab and reset its state
                for i in range(self.tabWidget.count()):
                    widget = self.tabWidget.widget(i)
                    if hasattr(widget, 'reset_for_exit'):
                        print("🔄 Resetting multiplayer page state on game exit")
                        try:
                            widget.reset_for_exit()
                        except Exception as e:
                            print(f"⚠️ Error resetting multiplayer page: {e}")
                        break
            
            print(f"✅ MultiplayerGamePage cleanup completed for instance {id(self)}")
            
        except Exception as e:
            print(f"❌ Error during MultiplayerGamePage cleanup: {e}")
            import traceback
            print(f"❌ Cleanup traceback: {traceback.format_exc()}")
        
        super().closeEvent(event)
    
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
        
        # Set splitter proportions - much more aggressive about game area
        if self._is_small_screen():
            # Very small progress area for small screens (10% progress, 90% game)
            self.splitter.setSizes([100, 900])
        else:
            # Small progress area for normal screens (15% progress, 85% game)
            self.splitter.setSizes([150, 850])
        
        self.splitter.setStretchFactor(0, 0)  # Progress bar is fixed height
        self.splitter.setStretchFactor(1, 1)  # Game area is stretchable
        
        # Connect to splitter resize events for dynamic player widget sizing
        self.splitter.splitterMoved.connect(self._on_splitter_moved)
        
        # Install event filter for window resize events
        self.installEventFilter(self)
    
    def resizeEvent(self, event):
        """Handle resize events directly"""
        super().resizeEvent(event)
        print(f"🔧 RESIZE EVENT: {self.width()}x{self.height()}")
        # Update all player widgets when the main widget is resized
        self._update_all_player_widgets()
    
    def create_progress_bar(self):
        """Create the multiplayer progress bar at the top"""
        # Progress bar container
        self.progress_frame = QFrame()
        self.progress_frame.setFrameStyle(QFrame.Shape.Box)
        self.progress_frame.setLineWidth(1)
        # Simple vertical layout for players
        progress_layout = QVBoxLayout(self.progress_frame)
        
        # Very aggressive margins for maximum space efficiency
        if self._is_small_screen():
            progress_layout.setContentsMargins(6, 3, 6, 3)
            progress_layout.setSpacing(2)
        else:
            progress_layout.setContentsMargins(10, 5, 10, 5)
            progress_layout.setSpacing(4)
        
        # Players container - vertical layout as requested
        self.players_widget = QWidget()
        self.players_layout = QVBoxLayout(self.players_widget)
        self.players_layout.setContentsMargins(0, 0, 0, 0)
        
        # Adjust spacing based on screen size
        if self._is_small_screen():
            self.players_layout.setSpacing(4)
        else:
            self.players_layout.setSpacing(8)
        
        progress_layout.addWidget(self.players_widget)
        
        # Add progress bar to splitter
        self.splitter.addWidget(self.progress_frame)
        
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
            player_color = player_data.get('player_color', '#CCCCCC')  # Default gray
            
            print(f"🎮 DEBUG: Creating player widget for {player_name} (host: {is_host}, color: {player_color})")
            
            # Get or create Player instance
            player_instance = self.network_manager.get_room_player(player_name)
            if not player_instance:
                # Create Player instance if not found
                player_instance = self.network_manager.create_player(
                    player_data.get('socket_id', ''),
                    player_name,
                    is_host
                )
                self.network_manager.add_room_player(player_instance)
            
            # CRITICAL FIX: Ensure color is set on Player instance BEFORE creating widget
            if player_color != '#CCCCCC':
                player_instance.update_color(player_color)
                print(f"🎨 DEBUG: Set {player_name}'s color to {player_color} on Player instance")
            else:
                print(f"🎨 DEBUG: {player_name} using default color {player_color}")
            
            # Create player progress widget with Player instance
            player_widget = PlayerProgressWidget(player_instance)
            
            # CRITICAL FIX: Ensure color is properly applied to the widget after creation
            if player_color != '#CCCCCC':
                player_widget.update_color(player_color)
                print(f"🎨 DEBUG: Applied color {player_color} to {player_name}'s widget after creation")
            
            # Ensure progress starts at 0
            player_widget.update_progress("Starting...", 0, False, None)
            
            self.players[player_name] = player_widget
            self.player_instances[player_name] = player_instance
            
            # Add to layout
            self.players_layout.addWidget(player_widget)
        
        print(f"🎮 DEBUG: Initialized {len(self.players)} players: {list(self.players.keys())}")
        
        # CRITICAL FIX: Ensure all player colors are properly applied after initialization
        self._refresh_all_player_colors()
        
        # Update all player widgets for dynamic sizing
        self._update_all_player_widgets()
        
        # Force initial dynamic layout after a short delay to ensure proper sizing
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(100, self._force_dynamic_update)
        
        # Set up continuous monitoring timer
        self.monitor_timer = QTimer()
        self.monitor_timer.timeout.connect(self._monitor_container_size)
        self.monitor_timer.start(500)  # Check every 500ms
        
        # Set up splitter monitoring
        self.splitter_timer = QTimer()
        self.splitter_timer.timeout.connect(self._monitor_splitter_proportions)
        self.splitter_timer.start(1000)  # Check every 1 second
    
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
            
            # CRITICAL FIX: Stop all timers immediately when local player completes
            self.stop_all_timers_and_progress()
            
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
            # Use the actual links used from the solo game
            actual_links_used = self.solo_game.linksUsed
            print(f"🏆 COMPLETION: Sending completion with {actual_links_used} links (solo_game.linksUsed)")
            print(f"🏆 COMPLETION: Solo game linksUsedLabel: {self.solo_game.linksUsedLabel.text()}")
            print(f"🏆 COMPLETION: Solo game previousLinksList count: {self.solo_game.previousLinksList.count()}")
            self.network_manager.send_game_completion(completion_time, actual_links_used)
    
    def on_game_starting(self, countdown_data):
        """Handle game starting countdown event from server"""
        print(f"🎬 DEBUG: MultiplayerGamePage received game_starting event: {countdown_data}")
        # Note: Countdown dialog is handled by MultiplayerPage, not here
        # This prevents duplicate countdown dialogs
    
    def on_game_started(self, game_data):
        """Handle game start event from server"""
        print(f"🎮 DEBUG: MultiplayerGamePage received game_started event: {game_data}")
        print(f"🎮 DEBUG: Current game_started state: {self.game_started}")
        print(f"🎮 DEBUG: Current game_finished state: {self.game_finished}")
        
        # Reset complete game state for new game
        self.reset_game_state()
        
        # Start the multiplayer game
        self.start_game()
        
        # CRITICAL FIX: Ensure all player colors are properly applied after game start
        self._refresh_all_player_colors()
        
        print(f"🎮 DEBUG: Game started successfully, game_started is now: {self.game_started}")
    
    def _refresh_all_player_colors(self):
        """Refresh all player colors to ensure they are properly applied"""
        print(f"🎨 DEBUG: Refreshing all player colors")
        for player_name, player_widget in self.players.items():
            if hasattr(player_widget, 'player_color'):
                print(f"🎨 DEBUG: Refreshing color for {player_name}: {player_widget.player_color}")
                player_widget._apply_progress_bar_theme()
    
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
        
        # Update Player instance if it exists
        if player_name in self.player_instances:
            player_instance = self.player_instances[player_name]
            # Add navigation entry to Player instance
            player_instance.add_navigation_entry(current_page, current_page)
            print(f"📊 PROGRESS UPDATE: Updated {player_name}'s Player instance with {links_used} links")
        
        # Update progress widget for other players only
        print(f"📊 PROGRESS UPDATE: Updating {player_name} widget with {links_used} links")
        self.players[player_name].update_progress(current_page, links_used)
        
        # Emit signal for parent components
        self.player_progress_updated.emit(player_name, current_page, links_used)
    
    
    def on_player_completed(self, player_name, completion_time, links_used):
        """Handle player completion events"""
        # Update Player instance if it exists
        if player_name in self.player_instances:
            player_instance = self.player_instances[player_name]
            player_instance.complete_game(completion_time)
            print(f"🏁 Updated {player_name}'s Player instance completion: {completion_time:.2f}s with {links_used} links")
        
        if player_name in self.players:
            self.players[player_name].update_progress(
                "🏆 COMPLETED!", 
                links_used, 
                True, 
                completion_time
            )
            
            # CRITICAL FIX: Stop all timers and progress bars when any player wins
            self.stop_all_timers_and_progress()
            self.stop_all_progress_bars()
    
    def reset_all_player_progress(self):
        """Reset all player progress for new game"""
        print(f"🔄 DEBUG: Resetting all player progress for new game")
        print(f"🔄 DEBUG: Current players dict: {list(self.players.keys())}")
        print(f"🔄 DEBUG: Current players count: {len(self.players)}")
        
        # Reset Player instances
        for player_name, player_instance in self.player_instances.items():
            print(f"🔄 DEBUG: Resetting Player instance for {player_name}")
            player_instance.reset_game_state()
        
        # Reset player widgets
        for player_name, player_widget in self.players.items():
            print(f"🔄 DEBUG: Resetting {player_name} widget...")
            player_widget.update_progress(
                "Starting...", 
                0, 
                False, 
                None
            )
            print(f"🔄 DEBUG: Reset {player_name} to starting state")
        
        print(f"🔄 DEBUG: All player progress reset complete")
    
    def reset_game_state(self):
        """Reset all game state for a new game"""
        print(f"🔄 DEBUG: Resetting complete game state for new game")
        
        # Reset all flags
        self.game_started = False
        self.game_finished = False
        self.results_dialog_shown = False
        self.first_link_clicked = False
        self.start_time = None
        
        # Reset all player progress
        self.reset_all_player_progress()
        
        # Re-enable solo game
        self.solo_game.setEnabled(True)
        
        print(f"🔄 DEBUG: Game state reset complete")
    
    def update_game_data(self, new_game_data):
        """Update the game data for a new game in the same tab"""
        print(f"🔄 DEBUG: Updating game data for new game")
        
        # Update the stored game data
        self.game_data = new_game_data
        
        # Update the solo game with new URLs
        start_url = new_game_data.get('start_url', '')
        end_url = new_game_data.get('end_url', '')
        start_title = new_game_data.get('start_title', '')
        end_title = new_game_data.get('end_title', '')
        
        # Update the solo game page with new URLs
        if hasattr(self.solo_game, 'start_url'):
            self.solo_game.start_url = start_url
        if hasattr(self.solo_game, 'end_url'):
            self.solo_game.end_url = end_url
        if hasattr(self.solo_game, 'start_title'):
            self.solo_game.start_title = start_title
        if hasattr(self.solo_game, 'end_title'):
            self.solo_game.end_title = end_title
        
        # Reset the game state
        self.reset_game_state()
        
        print(f"🔄 DEBUG: Game data updated successfully")
    
    def on_player_left(self, player_name, players_list):
        """Handle player disconnection during active game"""
        print(f"🔄 Player {player_name} disconnected during game. Remaining players: {[p['display_name'] for p in players_list]}")
        
        # Update the disconnected player's progress to show disconnection status
        if player_name in self.players:
            player_widget = self.players[player_name]
            
            # Update the player widget to show disconnection
            player_widget.update_progress(
                "❌ DISCONNECTED", 
                player_widget.links_used,  # Keep current progress
                False,  # Not completed
                None
            )
            
            # Disable the progress bar and change its appearance
            player_widget.progress_bar.setEnabled(False)
            player_widget.progress_bar.setStyleSheet("""
                QProgressBar {
                    border: 2px solid #666666;
                    border-radius: 10px;
                    text-align: center;
                    font-weight: bold;
                    font-size: 11px;
                    color: #666666;
                    background-color: #2a2a2a;
                    margin: 4px 0px;
                }
                QProgressBar::chunk {
                    background-color: #666666;
                    border-radius: 8px;
                    margin: 1px;
                }
            """)
            
            # Update the player name label to show disconnection
            if hasattr(player_widget, 'name_label'):
                player_widget.name_label.setText(f"{player_name} (Disconnected)")
                player_widget.name_label.setStyleSheet("color: #666666; text-decoration: line-through;")
            
            print(f"🔄 Updated {player_name} widget to show disconnection status")
        
        # Update our local player list with the server's authoritative list
        remaining_players = [p['display_name'] for p in players_list]
        print(f"🔄 Remaining active players: {remaining_players}")
        
        # Emit signal for parent components
        self.player_progress_updated.emit(player_name, "DISCONNECTED", 0)
    
    def on_player_color_updated(self, player_name, color_hex, color_name):
        """Handle player color update during game"""
        print(f"🎨 Player {player_name} updated color to {color_name} ({color_hex})")
        
        # Update Player instance if it exists
        if player_name in self.player_instances:
            player_instance = self.player_instances[player_name]
            player_instance.update_color(color_hex, color_name)
            print(f"🎨 Updated {player_name}'s Player instance color to {color_hex}")
        
        # CRITICAL FIX: Also update the PlayerProgressWidget directly
        if player_name in self.players:
            player_widget = self.players[player_name]
            player_widget.update_color(color_hex)
            print(f"🎨 Updated {player_name}'s progress widget color to {color_hex}")
        else:
            print(f"⚠️ Player {player_name} not found in players widgets")
    
    def stop_all_timers_and_progress(self):
        """CRITICAL FIX: Stop all timers when game ends to prevent non-winners from continuing to tick"""
        print(f"⏰ WikiRace: [{time.time():.3f}] Stopping all timers and progress tracking")
        
        try:
            # Stop the solo game timer if it exists
            if hasattr(self, 'solo_game') and self.solo_game:
                if hasattr(self.solo_game, 'timer') and self.solo_game.timer.isActive():
                    self.solo_game.timer.stop()
                    print(f"⏰ WikiRace: [{time.time():.3f}] Stopped solo game timer")
                
                # Also stop any other timers in solo game
                for attr_name in dir(self.solo_game):
                    attr = getattr(self.solo_game, attr_name)
                    if isinstance(attr, QTimer) and attr.isActive():
                        attr.stop()
                        print(f"⏰ WikiRace: [{time.time():.3f}] Stopped solo game timer: {attr_name}")
            
            # Stop any monitoring timers
            if hasattr(self, 'monitor_timer') and self.monitor_timer and self.monitor_timer.isActive():
                self.monitor_timer.stop()
                print(f"⏰ WikiRace: [{time.time():.3f}] Stopped monitor timer")
            
            if hasattr(self, 'splitter_timer') and self.splitter_timer and self.splitter_timer.isActive():
                self.splitter_timer.stop()
                print(f"⏰ WikiRace: [{time.time():.3f}] Stopped splitter timer")
            
            # Stop all other timers that might exist
            for attr_name in dir(self):
                attr = getattr(self, attr_name)
                if isinstance(attr, QTimer) and attr.isActive():
                    attr.stop()
                    print(f"⏰ WikiRace: [{time.time():.3f}] Stopped timer: {attr_name}")
            
            # Stop progress tracking for all players
            self.stop_all_progress_bars()
            
            print(f"✅ WikiRace: [{time.time():.3f}] All timers stopped - no more ticking for non-winners")
            
        except Exception as e:
            print(f"❌ Error stopping timers: {e}")
            import traceback
            print(f"❌ Timer stop traceback: {traceback.format_exc()}")
    
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
        print(f"🏆 DEBUG: Received game_ended event: {results}")
        print(f"🏆 DEBUG: Current results_dialog_shown state: {self.results_dialog_shown}")
        print(f"🏆 DEBUG: Current game_finished state: {self.game_finished}")
        print(f"🏆 DEBUG: Current instance ID: {id(self)}")
        
        # Check if this instance is still the current active tab
        current_tab_index = self.tabWidget.currentIndex()
        current_widget = self.tabWidget.widget(current_tab_index)
        is_current_tab = (current_widget == self)
        
        print(f"🏆 DEBUG: Is current active tab: {is_current_tab}")
        print(f"🏆 DEBUG: Current tab index: {current_tab_index}, This widget index: {self.tabWidget.indexOf(self)}")
        
        # Only show dialog if this is the current active tab
        if not is_current_tab:
            print(f"🏆 DEBUG: Not current active tab, skipping dialog for instance {id(self)}")
            return
        
        # Prevent duplicate dialogs
        if self.results_dialog_shown:
            print(f"🏆 DEBUG: Results dialog already shown, skipping duplicate")
            return
            
        self.results_dialog_shown = True
        self.game_finished = True  # Use the boolean variable
        
        print(f"🏆 DEBUG: Setting results_dialog_shown to True for instance {id(self)}")
        
        # Disable navigation in solo game
        self.solo_game.setEnabled(False)
        
        # Show results dialog
        print(f"🏆 DEBUG: About to show results dialog for instance {id(self)}")
        self.show_results_dialog(results)
        
        # Emit completion signal with results
        self.game_completed.emit(results)  # Use the signal
    
    def show_results_dialog(self, results):
        """Show the multiplayer results dialog"""
        try:
            from src.gui.MultiplayerResultsDialog import MultiplayerResultsDialog
            
            # Set flag to prevent duplicates
            self.results_dialog_shown = True
            
            # Create and show results dialog
            dialog = MultiplayerResultsDialog(results, parent=self)
            
            # Connect dialog signals
            dialog.play_again_requested.connect(self.on_play_again_requested)
            dialog.exit_to_home_requested.connect(self.on_exit_to_home_requested)
            
            # Actually show the dialog
            print(f"🏆 DEBUG: Showing results dialog with {len(results.get('results', []))} players")
            print(f"🏆 DEBUG: Dialog instance ID: {id(self)}")
            print(f"🏆 DEBUG: Results data: {results}")
            dialog.exec()
            print(f"🏆 DEBUG: Dialog execution completed for instance {id(self)}")
            
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
        
        # Clean up any old game tabs to prevent multiple dialogs
        self.cleanup_old_game_tabs()
        
        # Close the current game tab and return to multiplayer page
        self.close_game_tab()
    
    def cleanup_old_game_tabs(self):
        """Clean up old game tabs to prevent multiple dialogs"""
        print("🧹 DEBUG: Cleaning up old game tabs...")
        
        # Find and remove old game tabs (keep only the current one)
        game_tabs_to_remove = []
        current_tab_index = self.tabWidget.indexOf(self)
        
        for i in range(self.tabWidget.count()):
            widget = self.tabWidget.widget(i)
            if hasattr(widget, '__class__') and 'MultiplayerGamePage' in str(widget.__class__):
                if i != current_tab_index:  # Keep only the current tab
                    # Disconnect signals from old instances before removing
                    if hasattr(widget, 'disconnect_network_signals'):
                        widget.disconnect_network_signals()
                    game_tabs_to_remove.append(i)
        
        # Remove extra game tabs (in reverse order to maintain indices)
        for i in reversed(game_tabs_to_remove):
            print(f"🧹 DEBUG: Removing old game tab at index {i}")
            self.tabWidget.removeTab(i)
        
        print(f"🧹 DEBUG: Cleaned up {len(game_tabs_to_remove)} old game tabs")
    
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
            # CRITICAL FIX: Close tabs first, then disconnect from server
            # Find the multiplayer page and close its tab
            multiplayer_tab_index = None
            for i in range(self.tabWidget.count()):
                widget = self.tabWidget.widget(i)
                # Check if this is the MultiplayerPage by looking for specific attributes
                if (hasattr(widget, 'reset_for_exit') and 
                    hasattr(widget, 'network_manager') and 
                    hasattr(widget, 'current_room_code')):
                    print(f"🔄 CRITICAL: Found multiplayer tab for exit")
                    multiplayer_tab_index = i
                    break
            
            # Find the current game tab index
            current_index = self.tabWidget.indexOf(self)
            if current_index >= 0:
                # Close the game tab first
                self.tabWidget.removeTab(current_index)
                print(f"🔄 CRITICAL: Game tab closed")
            
            # Close the multiplayer tab if found
            if multiplayer_tab_index is not None:
                # Adjust index if game tab was removed before multiplayer tab
                if multiplayer_tab_index > current_index:
                    multiplayer_tab_index -= 1
                
                # Get the multiplayer widget before removing the tab
                multiplayer_widget = self.tabWidget.widget(multiplayer_tab_index)
                
                # Close the multiplayer tab first
                self.tabWidget.removeTab(multiplayer_tab_index)
                print(f"🔄 CRITICAL: Multiplayer tab closed")
                
                # Disconnect from server after closing tab
                if hasattr(multiplayer_widget, 'network_manager') and multiplayer_widget.network_manager:
                    print(f"🔄 CRITICAL: Disconnecting from server after closing multiplayer tab")
                    multiplayer_widget.network_manager.disconnect_from_server()
            
            # Switch to home tab (index 0)
            self.tabWidget.setCurrentIndex(0)
            print(f"🔄 CRITICAL: Returned to home page - ready for new games")
                
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
