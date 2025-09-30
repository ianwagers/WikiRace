"""
MultiplayerResultsDialog - Results display for multiplayer games

Shows final rankings, completion times, link counts, and navigation paths
for all players in a completed multiplayer game.
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QTableWidget, QTableWidgetItem, QPushButton,
                            QTabWidget, QTextEdit, QScrollArea, QWidget,
                            QHeaderView, QFrame, QSpacerItem, QSizePolicy)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QIcon
from src.logic.ThemeManager import theme_manager
import json


class PathViewerWidget(QWidget):
    """Widget for displaying a player's navigation path"""
    
    def __init__(self, player_data, parent=None):
        super().__init__(parent)
        self.player_data = player_data
        self.initUI()
        self.apply_theme()
    
    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # Player info header
        player_name = self.player_data.get('player_name', 'Unknown')
        rank = self.player_data.get('rank', 0)
        is_completed = self.player_data.get('is_completed', False)
        
        # Header with player info
        header_layout = QHBoxLayout()
        
        # Rank indicator
        rank_label = QLabel(f"#{rank}")
        rank_label.setFont(QFont("Inter", 24, QFont.Weight.Bold))
        if rank == 1:
            rank_label.setStyleSheet("color: #FFD700;")  # Gold
        elif rank == 2:
            rank_label.setStyleSheet("color: #C0C0C0;")  # Silver
        elif rank == 3:
            rank_label.setStyleSheet("color: #CD7F32;")  # Bronze
        header_layout.addWidget(rank_label)
        
        # Player name and status
        name_layout = QVBoxLayout()
        name_label = QLabel(player_name)
        name_label.setFont(QFont("Inter", 16, QFont.Weight.Bold))
        name_layout.addWidget(name_label)
        
        if is_completed:
            status_label = QLabel("🏆 COMPLETED")
            status_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
            completion_time = self.player_data.get('completion_time', 0)
            links_used = self.player_data.get('links_used', 0)
            stats_label = QLabel(f"Time: {completion_time:.2f}s | Links: {links_used}")
            stats_label.setStyleSheet("color: #666; font-size: 12px;")
            name_layout.addWidget(status_label)
            name_layout.addWidget(stats_label)
        else:
            status_label = QLabel("❌ DID NOT FINISH")
            status_label.setStyleSheet("color: #F44336; font-weight: bold;")
            links_used = self.player_data.get('links_used', 0)
            stats_label = QLabel(f"Links used: {links_used}")
            stats_label.setStyleSheet("color: #666; font-size: 12px;")
            name_layout.addWidget(status_label)
            name_layout.addWidget(stats_label)
        
        header_layout.addLayout(name_layout)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Navigation path
        path_label = QLabel("🗺️ Navigation Path:")
        path_label.setFont(QFont("Inter", 12, QFont.Weight.Bold))
        layout.addWidget(path_label)
        
        # Path display
        self.path_text = QTextEdit()
        self.path_text.setReadOnly(True)
        self.path_text.setMaximumHeight(200)
        self.path_text.setFont(QFont("Inter", 10))
        
        # Build path text
        path_text = self.build_path_text()
        self.path_text.setPlainText(path_text)
        
        layout.addWidget(self.path_text)
    
    def build_path_text(self):
        """Build the navigation path text from detailed navigation history"""
        navigation_history = self.player_data.get('navigation_history', [])
        current_page = self.player_data.get('current_page', 'Unknown Page')
        links_used = self.player_data.get('links_used', 0)
        is_completed = self.player_data.get('is_completed', False)
        
        if not navigation_history:
            # Fallback to simple display if no detailed history
            if is_completed:
                path_lines = [
                    f"🏁 Started at: [Starting Page]",
                    f"📄 Navigated through {links_used} links",
                    f"🎯 Reached: {current_page}",
                    f"✅ Successfully completed the race!"
                ]
            else:
                path_lines = [
                    f"🏁 Started at: [Starting Page]", 
                    f"📄 Navigated through {links_used} links",
                    f"📍 Last page: {current_page}",
                    f"❌ Did not reach the destination"
                ]
            return "\n".join(path_lines)
        
        # Build detailed navigation path
        path_lines = []
        
        for i, entry in enumerate(navigation_history):
            page_title = entry.get('page_title', 'Unknown Page')
            time_elapsed = entry.get('time_elapsed', 0)
            link_number = entry.get('link_number', i)
            
            # Format time
            if time_elapsed < 60:
                time_str = f"{time_elapsed:.1f}s"
            else:
                minutes = int(time_elapsed // 60)
                seconds = time_elapsed % 60
                time_str = f"{minutes}m {seconds:.1f}s"
            
            # Different icons for different steps
            if link_number == 0:
                icon = "🏁"  # Start
                prefix = "Started at:"
            elif i == len(navigation_history) - 1 and is_completed:
                icon = "🎯"  # Target reached
                prefix = f"Link {link_number}:"
            else:
                icon = "📄"  # Regular page
                prefix = f"Link {link_number}:"
            
            path_lines.append(f"{icon} {prefix} {page_title} ({time_str})")
        
        # Add completion status
        if is_completed:
            path_lines.append(f"✅ Successfully completed in {time_elapsed:.1f}s with {links_used} links!")
        else:
            path_lines.append(f"❌ Did not reach destination ({links_used} links used)")
        
        return "\n".join(path_lines)
    
    def apply_theme(self):
        """Apply theme-based styling"""
        styles = theme_manager.get_theme_styles()
        
        if styles['is_dark']:
            self.setStyleSheet(f"""
                QWidget {{
                    background-color: {styles['background_color']};
                    color: {styles['text_color']};
                }}
                QTextEdit {{
                    background-color: #2a2a2a;
                    border: 1px solid #444;
                    border-radius: 6px;
                    padding: 8px;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QWidget {{
                    background-color: {styles['background_color']};
                    color: {styles['text_color']};
                }}
                QTextEdit {{
                    background-color: #f9f9f9;
                    border: 1px solid #ddd;
                    border-radius: 6px;
                    padding: 8px;
                }}
            """)


class MultiplayerResultsDialog(QDialog):
    """Dialog showing multiplayer game results"""
    
    # Signals for different user actions
    play_again_requested = pyqtSignal()  # Return to room for another game
    exit_to_home_requested = pyqtSignal()  # Leave room and go to home
    
    def __init__(self, results_data, parent=None):
        super().__init__(parent)
        self.results_data = results_data
        self.setModal(True)
        self.setWindowTitle("🏆 Race Results")
        self.setMinimumSize(800, 600)
        
        self.initUI()
        self.apply_theme()
        
        # Connect to theme changes
        theme_manager.theme_changed.connect(self.apply_theme)
    
    def initUI(self):
        """Initialize the results dialog UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # Title
        title_label = QLabel("🏆 WikiRace Results")
        title_label.setFont(QFont("Inter", 20, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Winner announcement
        winner = self.results_data.get('winner')
        if winner:
            winner_text = f"🎉 Congratulations {winner['player_name']}! 🎉"
            winner_label = QLabel(winner_text)
            winner_label.setFont(QFont("Inter", 16, QFont.Weight.Bold))
            winner_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            winner_label.setStyleSheet("color: #4CAF50; padding: 10px;")
            layout.addWidget(winner_label)
        
        # Results summary
        summary_layout = QHBoxLayout()
        
        # Removed completion stats as requested - focus on winner only
        
        layout.addLayout(summary_layout)
        
        # Tab widget for different views
        tab_widget = QTabWidget()
        
        # Rankings tab
        rankings_tab = self.create_rankings_tab()
        tab_widget.addTab(rankings_tab, "🏆 Rankings")
        
        # Detailed paths tab
        paths_tab = self.create_paths_tab()
        tab_widget.addTab(paths_tab, "🗺️ Navigation Paths")
        
        layout.addWidget(tab_widget)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        
        # Exit to Home button (leaves room)
        exit_button = QPushButton("Exit to Home")
        exit_button.setFont(QFont("Inter", 12))
        exit_button.clicked.connect(self.on_exit_to_home)
        button_layout.addWidget(exit_button)
        
        button_layout.addStretch()  # Center the buttons
        
        # Play again button (stays in room)
        play_again_button = QPushButton("Play Again")
        play_again_button.setFont(QFont("Inter", 12, QFont.Weight.Bold))
        play_again_button.setDefault(True)  # Make it the default action
        play_again_button.clicked.connect(self.on_play_again)
        button_layout.addWidget(play_again_button)
        
        layout.addLayout(button_layout)
    
    def create_rankings_tab(self):
        """Create the rankings tab with summary info only"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Title
        title_label = QLabel("🏆 Game Results Summary")
        title_label.setFont(QFont("Inter", 18, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Results summary
        results = self.results_data.get('results', [])
        
        # Winner announcement
        if results:
            winner = results[0]  # First result is the winner
            winner_label = QLabel(f"🥇 Winner: {winner.get('player_name', 'Unknown')}")
            winner_label.setFont(QFont("Inter", 16, QFont.Weight.Bold))
            winner_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            winner_label.setStyleSheet("color: #FFD700; padding: 10px;")
            layout.addWidget(winner_label)
            
            # Winner stats
            completion_time = winner.get('completion_time')
            links_used = winner.get('links_used', 0)
            if completion_time:
                stats_label = QLabel(f"Time: {completion_time:.2f}s | Links Used: {links_used}")
                stats_label.setFont(QFont("Inter", 14))
                stats_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                layout.addWidget(stats_label)
        
        # Game info (only show if we have valid titles)
        start_title = self.results_data.get('start_title', '')
        end_title = self.results_data.get('end_title', '')
        
        if start_title and end_title and start_title != 'Unknown' and end_title != 'Unknown':
            game_info = QLabel(f"Game: {start_title} → {end_title}")
            game_info.setFont(QFont("Inter", 12))
            game_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
            game_info.setStyleSheet("color: #888; font-style: italic;")
            layout.addWidget(game_info)
        
        # Only show completion stats for winner (no DNF or player count info)
        
        layout.addStretch()
        
        # Note about detailed paths
        note_label = QLabel("📊 View detailed navigation paths in the 'Navigation Paths' tab")
        note_label.setFont(QFont("Inter", 11))
        note_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        note_label.setStyleSheet("color: #666; font-style: italic; padding: 20px;")
        layout.addWidget(note_label)
        
        return widget
    
    def create_paths_tab(self):
        """Create the navigation paths tab with players as columns"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # Title with rankings info
        title_label = QLabel("🗺️ Navigation Paths & Rankings")
        title_label.setFont(QFont("Inter", 16, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Create paths table with players as columns
        results = self.results_data.get('results', [])
        if not results:
            no_data_label = QLabel("No navigation data available")
            no_data_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(no_data_label)
            return widget
        
        # Sort results by rank (winner first)
        sorted_results = sorted(results, key=lambda x: x.get('rank', 999))
        
        # Find the maximum path length to determine number of rows
        max_path_length = 0
        for result in sorted_results:
            navigation_history = result.get('navigation_history', [])
            max_path_length = max(max_path_length, len(navigation_history))
        
        # Create table: rows = path steps, columns = players
        self.paths_table = QTableWidget(max_path_length, len(sorted_results))
        
        # Set column headers with player names and rankings
        headers = []
        for i, result in enumerate(sorted_results):
            player_name = result.get('player_name', f'Player {i+1}')
            rank = result.get('rank', i+1)
            completion_time = result.get('completion_time')
            
            # Create header with rank and stats
            if completion_time:
                header = f"#{rank} {player_name}\n{completion_time:.2f}s"
            else:
                header = f"#{rank} {player_name}\nDNF"
            headers.append(header)
        
        self.paths_table.setHorizontalHeaderLabels(headers)
        
        # Populate table with navigation paths
        for col, result in enumerate(sorted_results):
            navigation_history = result.get('navigation_history', [])
            
            for row, nav_entry in enumerate(navigation_history):
                page_title = nav_entry.get('page_title', 'Unknown Page')
                timestamp = nav_entry.get('timestamp', '')
                
                # Create item with page title and timestamp
                if timestamp:
                    # Parse timestamp to show time since start
                    try:
                        from datetime import datetime
                        ts = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        # For now, just show the page title
                        item_text = page_title
                    except:
                        item_text = page_title
                else:
                    item_text = page_title
                
                item = QTableWidgetItem(item_text)
                item.setToolTip(f"Page: {page_title}\nTime: {timestamp}")
                self.paths_table.setItem(row, col, item)
        
        # Configure table
        self.paths_table.setAlternatingRowColors(True)
        self.paths_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.paths_table.verticalHeader().setVisible(True)
        self.paths_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectItems)
        
        # Set row labels (Step 1, Step 2, etc.)
        row_labels = [f"Step {i+1}" for i in range(max_path_length)]
        self.paths_table.setVerticalHeaderLabels(row_labels)
        
        layout.addWidget(self.paths_table)
        
        return widget
    
    def apply_theme(self):
        """Apply theme-based styling"""
        styles = theme_manager.get_theme_styles()
        
        if styles['is_dark']:
            self.setStyleSheet(f"""
                QDialog {{
                    background-color: {styles['background_color']};
                    color: {styles['text_color']};
                }}
                QLabel {{
                    color: {styles['text_color']};
                }}
                QTableWidget {{
                    background-color: #2a2a2a;
                    color: {styles['text_color']};
                    gridline-color: #444;
                    border: 1px solid #444;
                    border-radius: 6px;
                }}
                QTableWidget::item {{
                    padding: 8px;
                    border-bottom: 1px solid #444;
                }}
                QTableWidget::item:selected {{
                    background-color: #404040;
                }}
                QHeaderView::section {{
                    background-color: #404040;
                    color: {styles['text_color']};
                    padding: 8px;
                    border: none;
                    border-bottom: 2px solid #555;
                }}
                QTabWidget::pane {{
                    border: 1px solid #444;
                    background-color: {styles['background_color']};
                }}
                QTabBar::tab {{
                    background-color: #404040;
                    color: {styles['text_color']};
                    padding: 8px 16px;
                    margin-right: 2px;
                    border-top-left-radius: 6px;
                    border-top-right-radius: 6px;
                }}
                QTabBar::tab:selected {{
                    background-color: {styles['background_color']};
                    border-bottom: 2px solid #4CAF50;
                }}
                QPushButton {{
                    background-color: #404040;
                    color: {styles['text_color']};
                    border: 1px solid #555;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: #4CAF50;
                    color: white;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QDialog {{
                    background-color: {styles['background_color']};
                    color: {styles['text_color']};
                }}
                QLabel {{
                    color: {styles['text_color']};
                }}
                QTableWidget {{
                    background-color: white;
                    color: {styles['text_color']};
                    gridline-color: #ddd;
                    border: 1px solid #ddd;
                    border-radius: 6px;
                }}
                QTableWidget::item {{
                    padding: 8px;
                    border-bottom: 1px solid #eee;
                }}
                QTableWidget::item:selected {{
                    background-color: #e3f2fd;
                }}
                QHeaderView::section {{
                    background-color: #f5f5f5;
                    color: {styles['text_color']};
                    padding: 8px;
                    border: none;
                    border-bottom: 2px solid #ddd;
                }}
                QTabWidget::pane {{
                    border: 1px solid #ddd;
                    background-color: {styles['background_color']};
                }}
                QTabBar::tab {{
                    background-color: #f5f5f5;
                    color: {styles['text_color']};
                    padding: 8px 16px;
                    margin-right: 2px;
                    border-top-left-radius: 6px;
                    border-top-right-radius: 6px;
                }}
                QTabBar::tab:selected {{
                    background-color: {styles['background_color']};
                    border-bottom: 2px solid #4CAF50;
                }}
                QPushButton {{
                    background-color: #f5f5f5;
                    color: {styles['text_color']};
                    border: 1px solid #ddd;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: #4CAF50;
                    color: white;
                }}
            """)
    
    def on_play_again(self):
        """Handle play again button click - return to room for another game"""
        self.play_again_requested.emit()
        self.accept()  # Close the dialog
    
    def on_exit_to_home(self):
        """Handle exit to home button click - leave room and go to home page"""
        # CRITICAL FIX: Close dialog immediately, then handle cleanup
        print(f"🏠 PlayerResultsDialog: Exit to home requested")
        
        # CRITICAL FIX: Stop any WebView loading in the parent game page to prevent stutter
        try:
            if hasattr(self.parent(), 'solo_game') and self.parent().solo_game:
                if hasattr(self.parent().solo_game, 'webView') and self.parent().solo_game.webView:
                    print("🛑 CRITICAL: Stopping WebView loading before exit to prevent stutter")
                    self.parent().solo_game.webView.stop()
                    self.parent().solo_game.webView.setHtml("")
                    self.parent().solo_game.webView.setEnabled(False)
                    print("✅ WebView stopped before exit")
        except Exception as e:
            print(f"⚠️ Error stopping WebView before exit: {e}")
        
        self.accept()  # Close the dialog immediately
        self.exit_to_home_requested.emit()  # Emit signal after closing
