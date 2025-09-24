"""
Data models for WikiRace Multiplayer Server

Defines the core data structures for game rooms, players, and game state.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, validator


class GameState(str, Enum):
    """Game state enumeration"""
    LOBBY = "lobby"
    STARTING = "starting"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class NavigationEntry(BaseModel):
    """Single navigation entry in a player's history"""
    
    page_url: str = Field(..., description="Full Wikipedia page URL")
    page_title: str = Field(..., description="Wikipedia page title")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When page was visited")
    link_number: int = Field(..., ge=0, description="Sequential link number (0 = start page)")
    time_elapsed: float = Field(default=0.0, ge=0, description="Time elapsed since game start (seconds)")
    
    class Config:
        # Allow datetime serialization
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class Player(BaseModel):
    """Player model for multiplayer games"""
    
    socket_id: str = Field(..., description="Unique socket connection ID")
    display_name: str = Field(..., min_length=1, max_length=50, description="Player's chosen name")
    is_host: bool = Field(default=False, description="Whether player is room host")
    
    # Game state
    current_page: Optional[str] = Field(default=None, description="Current Wikipedia page URL")
    current_page_title: Optional[str] = Field(default=None, description="Current Wikipedia page title")
    links_clicked: int = Field(default=0, ge=0, description="Number of links used")
    navigation_history: List[NavigationEntry] = Field(default_factory=list, description="Detailed navigation path")
    game_completed: bool = Field(default=False, description="Whether reached destination")
    completion_time: Optional[float] = Field(default=None, ge=0, description="Time to complete (seconds)")
    game_start_time: Optional[datetime] = Field(default=None, description="When game started for this player")
    
    # Timestamps
    joined_at: datetime = Field(default_factory=datetime.utcnow, description="When player joined room")
    last_activity: datetime = Field(default_factory=datetime.utcnow, description="Last activity timestamp")
    
    @validator('display_name')
    def validate_display_name(cls, v):
        """Validate display name format"""
        # Remove extra whitespace and ensure non-empty
        v = v.strip()
        if not v:
            raise ValueError('Display name cannot be empty')
        return v
    
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
        
        # FIXED: Links clicked should match client-side logic
        # The client starts at 0 and increments only on actual link clicks
        # The server should count only actual link clicks, not the starting page
        # If this is the first entry (starting page), links_clicked = 0
        # Otherwise, links_clicked = number of entries after the starting page
        if len(self.navigation_history) == 1:
            # This is the starting page, no links clicked yet
            self.links_clicked = 0
        else:
            # This is a link click, count all entries after the starting page
            self.links_clicked = len(self.navigation_history) - 1
        self.last_activity = datetime.utcnow()
        
        return entry
    
    def get_navigation_summary(self) -> List[Dict[str, Any]]:
        """Get a summary of navigation history for results display"""
        return [
            {
                'page_title': entry.page_title,
                'page_url': entry.page_url,
                'link_number': entry.link_number,
                'time_elapsed': entry.time_elapsed,
                'timestamp': entry.timestamp.isoformat()
            }
            for entry in self.navigation_history
        ]


class GameRoom(BaseModel):
    """Game room model for multiplayer sessions"""
    
    room_code: str = Field(..., min_length=4, max_length=4, description="4-letter room code")
    host_id: str = Field(..., description="Socket ID of room host")
    players: Dict[str, Player] = Field(default_factory=dict, description="Socket ID → Player mapping")
    
    # Game state
    game_state: GameState = Field(default=GameState.LOBBY, description="Current game phase")
    start_url: Optional[str] = Field(default=None, description="Starting Wikipedia page")
    end_url: Optional[str] = Field(default=None, description="Target Wikipedia page")
    start_title: Optional[str] = Field(default=None, description="Display title for start page")
    end_title: Optional[str] = Field(default=None, description="Display title for end page")
    categories: List[str] = Field(default_factory=list, description="Selected categories for page selection")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Room creation timestamp")
    game_started_at: Optional[datetime] = Field(default=None, description="Game start time")
    
    @validator('room_code')
    def validate_room_code(cls, v):
        """Validate room code format"""
        if not v.isupper() or not v.isalpha():
            raise ValueError('Room code must be 4 uppercase letters')
        return v
    
    @property
    def player_count(self) -> int:
        """Get current number of players in room"""
        return len(self.players)
    
    @property
    def is_full(self) -> bool:
        """Check if room is at capacity"""
        return self.player_count >= 10  # Max players per room
    
    def add_player(self, player: Player) -> bool:
        """Add a player to the room"""
        if self.is_full:
            return False
        self.players[player.socket_id] = player
        return True
    
    def remove_player(self, socket_id: str) -> Optional[Player]:
        """Remove a player from the room"""
        return self.players.pop(socket_id, None)
    
    def get_player(self, socket_id: str) -> Optional[Player]:
        """Get a player by socket ID"""
        return self.players.get(socket_id)
    
    def get_player_by_name(self, display_name: str) -> Optional[Player]:
        """Get a player by display name"""
        for player in self.players.values():
            if player.display_name == display_name:
                return player
        return None
    
    def is_host(self, socket_id: str) -> bool:
        """Check if socket ID belongs to room host"""
        return self.host_id == socket_id
    
    def transfer_host(self) -> Optional[str]:
        """Transfer host to another player, return new host socket_id"""
        if len(self.players) <= 1:
            return None
        
        # Store old host ID
        old_host_id = self.host_id
        
        # Find next available player (not current host)
        for socket_id, player in self.players.items():
            if socket_id != self.host_id:
                # Set new host
                self.host_id = socket_id
                player.is_host = True
                
                # Update old host (if still in room)
                if old_host_id in self.players:
                    self.players[old_host_id].is_host = False
                
                return socket_id
        
        return None


class RoomCreateRequest(BaseModel):
    """Request model for creating a new room"""
    display_name: str = Field(..., min_length=1, max_length=50)


class RoomJoinRequest(BaseModel):
    """Request model for joining an existing room"""
    display_name: str = Field(..., min_length=1, max_length=50)


class GameConfigRequest(BaseModel):
    """Request model for game configuration"""
    start_category: Optional[str] = None
    end_category: Optional[str] = None
    custom_start_url: Optional[str] = None
    custom_end_url: Optional[str] = None


class GameStartRequest(BaseModel):
    """Request model for starting a game"""
    pass  # No additional parameters needed


class PlayerProgressUpdate(BaseModel):
    """Model for player progress updates during game"""
    current_page: str
    links_clicked: int
    navigation_history: List[str]
    game_completed: bool = False
    completion_time: Optional[int] = None


class GameResults(BaseModel):
    """Final game results for all players"""
    room_code: str
    game_duration: int  # Total game duration in seconds
    players: List[Dict[str, any]]  # Player results with rankings
    
    class Config:
        # Allow arbitrary types for complex nested data
        arbitrary_types_allowed = True
