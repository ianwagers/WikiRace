"""
Player class for WikiRace multiplayer functionality

Provides a client-side Player model that integrates with Qt signals
and matches the server-side Player model structure.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from PyQt6.QtCore import QObject, pyqtSignal


class NavigationEntry:
    """Single navigation entry in a player's history"""
    
    def __init__(self, page_url: str, page_title: str, link_number: int = 0, time_elapsed: float = 0.0):
        self.page_url = page_url
        self.page_title = page_title
        self.link_number = link_number
        self.time_elapsed = time_elapsed
        self.timestamp = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'page_url': self.page_url,
            'page_title': self.page_title,
            'link_number': self.link_number,
            'time_elapsed': self.time_elapsed,
            'timestamp': self.timestamp.isoformat()
        }


class Player(QObject):
    """Player model for multiplayer games with Qt signal integration"""
    
    # Qt signals for UI updates
    color_changed = pyqtSignal(str, str)  # color_hex, color_name
    progress_updated = pyqtSignal(str, int)  # current_page, links_used
    game_finished = pyqtSignal(float, int)  # completion_time, links_used
    navigation_updated = pyqtSignal(list)  # navigation_history
    
    def __init__(self, socket_id: str, display_name: str, is_host: bool = False, parent=None):
        super().__init__(parent)
        self.socket_id = socket_id
        self.display_name = display_name
        self.is_host = is_host
        self.player_color = None
        self.color_name = None
        
        # Game state
        self.current_page = None
        self.current_page_title = None
        self.links_clicked = 0
        self.navigation_history: List[NavigationEntry] = []
        self.game_completed = False
        self.completion_time = None
        self.game_start_time = None
        
        # Timestamps
        self.joined_at = datetime.utcnow()
        self.last_activity = datetime.utcnow()
    
    def update_color(self, color_hex: str, color_name: str = None):
        """Update player's color and emit signal"""
        self.player_color = color_hex
        self.color_name = color_name
        self.last_activity = datetime.utcnow()
        self.color_changed.emit(color_hex, color_name or "Unknown")
    
    def add_navigation_entry(self, page_url: str, page_title: str) -> NavigationEntry:
        """Add a new navigation entry to the player's history"""
        # Calculate time elapsed since game start
        time_elapsed = 0.0
        if self.game_start_time:
            time_elapsed = (datetime.utcnow() - self.game_start_time).total_seconds()
        
        # Create navigation entry
        entry = NavigationEntry(
            page_url=page_url,
            page_title=page_title,
            link_number=len(self.navigation_history),
            time_elapsed=time_elapsed
        )
        
        # Add to history
        self.navigation_history.append(entry)
        
        # Update current page info
        self.current_page = page_url
        self.current_page_title = page_title
        
        # Update links clicked count
        if len(self.navigation_history) == 1:
            # This is the starting page, no links clicked yet
            self.links_clicked = 0
        else:
            # This is a link click, count all entries after the starting page
            self.links_clicked = len(self.navigation_history) - 1
        
        self.last_activity = datetime.utcnow()
        
        # Emit signals for UI updates
        self.progress_updated.emit(page_title, self.links_clicked)
        self.navigation_updated.emit([entry.to_dict() for entry in self.navigation_history])
        
        return entry
    
    def complete_game(self, completion_time: float = None):
        """Mark game as completed"""
        self.game_completed = True
        if completion_time is None and self.game_start_time:
            completion_time = (datetime.utcnow() - self.game_start_time).total_seconds()
        self.completion_time = completion_time
        self.last_activity = datetime.utcnow()
        
        # Emit completion signal
        self.game_finished.emit(completion_time or 0.0, self.links_clicked)
    
    def start_game(self, start_url: str, start_title: str):
        """Initialize game state when game starts"""
        self.game_start_time = datetime.utcnow()
        self.game_completed = False
        self.completion_time = None
        self.links_clicked = 0
        self.navigation_history.clear()
        
        # Add starting page as first entry
        self.add_navigation_entry(start_url, start_title)
    
    def reset_game_state(self):
        """Reset game state for new game"""
        self.current_page = None
        self.current_page_title = None
        self.links_clicked = 0
        self.navigation_history.clear()
        self.game_completed = False
        self.completion_time = None
        self.game_start_time = None
    
    def get_navigation_summary(self) -> List[Dict[str, Any]]:
        """Get a summary of navigation history for results display"""
        return [entry.to_dict() for entry in self.navigation_history]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert player to dictionary for serialization"""
        return {
            'socket_id': self.socket_id,
            'display_name': self.display_name,
            'is_host': self.is_host,
            'player_color': self.player_color,
            'color_name': self.color_name,
            'current_page': self.current_page,
            'current_page_title': self.current_page_title,
            'links_clicked': self.links_clicked,
            'navigation_history': self.get_navigation_summary(),
            'game_completed': self.game_completed,
            'completion_time': self.completion_time,
            'joined_at': self.joined_at.isoformat(),
            'last_activity': self.last_activity.isoformat()
        }
    
    def __str__(self):
        return f"Player({self.display_name}, host={self.is_host}, color={self.player_color})"
    
    def __repr__(self):
        return self.__str__()
