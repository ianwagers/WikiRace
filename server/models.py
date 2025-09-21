"""
Data models for WikiRace Multiplayer Server

Defines the core data structures for game rooms, players, and game state.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, validator


class GameState(str, Enum):
    """Game state enumeration"""
    LOBBY = "lobby"
    STARTING = "starting"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class Player(BaseModel):
    """Player model for multiplayer games"""
    
    socket_id: str = Field(..., description="Unique socket connection ID")
    display_name: str = Field(..., min_length=1, max_length=50, description="Player's chosen name")
    is_host: bool = Field(default=False, description="Whether player is room host")
    
    # Game state
    current_page: Optional[str] = Field(default=None, description="Current Wikipedia page URL")
    links_clicked: int = Field(default=0, ge=0, description="Number of links used")
    navigation_history: List[str] = Field(default_factory=list, description="Pages visited (titles)")
    game_completed: bool = Field(default=False, description="Whether reached destination")
    completion_time: Optional[int] = Field(default=None, ge=0, description="Time to complete (seconds)")
    
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
    
    def is_host(self, socket_id: str) -> bool:
        """Check if socket ID belongs to room host"""
        return self.host_id == socket_id
    
    def transfer_host(self) -> Optional[str]:
        """Transfer host to another player, return new host socket_id"""
        if len(self.players) <= 1:
            return None
        
        # Find next available player (not current host)
        for socket_id, player in self.players.items():
            if socket_id != self.host_id:
                self.host_id = socket_id
                player.is_host = True
                # Update old host
                if self.host_id in self.players:
                    self.players[self.host_id].is_host = False
                return socket_id
        
        return None


class RoomCreateRequest(BaseModel):
    """Request model for creating a new room"""
    display_name: str = Field(..., min_length=1, max_length=50)


class RoomJoinRequest(BaseModel):
    """Request model for joining an existing room"""
    room_code: str = Field(..., min_length=4, max_length=4)
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
