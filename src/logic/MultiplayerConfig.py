"""
MultiplayerConfig - Centralized configuration management for multiplayer functionality

Handles loading, saving, and managing configuration settings for the WikiRace
multiplayer system including server connection, reconnection, and game settings.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from PyQt6.QtCore import QObject, pyqtSignal


@dataclass
class ServerConfig:
    """Server connection configuration"""
    host: str = "127.0.0.1"
    port: int = 8001
    use_https: bool = False
    connection_timeout: float = 10.0
    
    @property
    def url(self) -> str:
        """Get the full server URL"""
        protocol = "https" if self.use_https else "http"
        return f"{protocol}://{self.host}:{self.port}"


@dataclass
class ReconnectionConfig:
    """Automatic reconnection configuration"""
    enabled: bool = True
    max_attempts: int = 5
    initial_delay: float = 2.0
    max_delay: float = 30.0
    backoff_multiplier: float = 1.5
    
    def get_delay(self, attempt: int) -> float:
        """Calculate delay for a given attempt number"""
        delay = self.initial_delay * (self.backoff_multiplier ** (attempt - 1))
        return min(delay, self.max_delay)


@dataclass
class GameConfig:
    """Game-specific configuration"""
    default_start_category: str = "Random"
    default_end_category: str = "Random"
    max_players_per_room: int = 10
    room_code_length: int = 4
    game_timeout_minutes: int = 30
    countdown_seconds: int = 5


@dataclass
class UIConfig:
    """User interface configuration"""
    auto_join_last_room: bool = False
    remember_player_name: bool = True
    last_player_name: str = ""
    show_progress_notifications: bool = True
    enable_sound_effects: bool = True


class MultiplayerConfig(QObject):
    """Centralized configuration manager for multiplayer functionality"""
    
    # Signals
    config_changed = pyqtSignal(str)  # section_name
    config_loaded = pyqtSignal()
    config_saved = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        
        # Configuration sections
        self.server = ServerConfig()
        self.reconnection = ReconnectionConfig()
        self.game = GameConfig()
        self.ui = UIConfig()
        
        # Internal state
        self._config_file_path = self._get_config_file_path()
        self._auto_save = True
        
        # Load configuration on initialization
        self.load_config()
    
    def _get_config_file_path(self) -> Path:
        """Get the path to the configuration file"""
        config_dir = Path.home() / ".wikirace"
        config_dir.mkdir(exist_ok=True)
        return config_dir / "multiplayer_config.json"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            'server': asdict(self.server),
            'reconnection': asdict(self.reconnection),
            'game': asdict(self.game),
            'ui': asdict(self.ui),
            'version': '1.0'
        }
    
    def from_dict(self, data: Dict[str, Any]) -> None:
        """Load configuration from dictionary"""
        # Server configuration
        if 'server' in data:
            server_data = data['server']
            self.server = ServerConfig(**server_data)
        
        # Reconnection configuration
        if 'reconnection' in data:
            reconnection_data = data['reconnection']
            self.reconnection = ReconnectionConfig(**reconnection_data)
        
        # Game configuration
        if 'game' in data:
            game_data = data['game']
            self.game = GameConfig(**game_data)
        
        # UI configuration
        if 'ui' in data:
            ui_data = data['ui']
            self.ui = UIConfig(**ui_data)
    
    def load_config(self) -> bool:
        """Load configuration from file"""
        try:
            if self._config_file_path.exists():
                with open(self._config_file_path, 'r') as f:
                    data = json.load(f)
                
                self.from_dict(data)
                self.config_loaded.emit()
                return True
            else:
                # Create default configuration file
                self.save_config()
                return True
                
        except Exception as e:
            print(f"Failed to load multiplayer config: {e}")
            # Keep default values and try to save them
            try:
                self.save_config()
            except Exception as save_error:
                print(f"Failed to save default config: {save_error}")
            return False
    
    def save_config(self) -> bool:
        """Save configuration to file"""
        try:
            data = self.to_dict()
            
            # Ensure directory exists
            self._config_file_path.parent.mkdir(exist_ok=True)
            
            # Write configuration
            with open(self._config_file_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            self.config_saved.emit()
            return True
            
        except Exception as e:
            print(f"Failed to save multiplayer config: {e}")
            return False
    
    def reset_to_defaults(self) -> None:
        """Reset all configuration to default values"""
        self.server = ServerConfig()
        self.reconnection = ReconnectionConfig()
        self.game = GameConfig()
        self.ui = UIConfig()
        
        if self._auto_save:
            self.save_config()
        
        self.config_changed.emit("all")
    
    def update_server_config(self, host: str = None, port: int = None, 
                           use_https: bool = None, timeout: float = None) -> None:
        """Update server configuration"""
        if host is not None:
            self.server.host = host
        if port is not None:
            self.server.port = port
        if use_https is not None:
            self.server.use_https = use_https
        if timeout is not None:
            self.server.connection_timeout = timeout
        
        if self._auto_save:
            self.save_config()
        
        self.config_changed.emit("server")
    
    def update_reconnection_config(self, enabled: bool = None, max_attempts: int = None,
                                 initial_delay: float = None, max_delay: float = None) -> None:
        """Update reconnection configuration"""
        if enabled is not None:
            self.reconnection.enabled = enabled
        if max_attempts is not None:
            self.reconnection.max_attempts = max_attempts
        if initial_delay is not None:
            self.reconnection.initial_delay = initial_delay
        if max_delay is not None:
            self.reconnection.max_delay = max_delay
        
        if self._auto_save:
            self.save_config()
        
        self.config_changed.emit("reconnection")
    
    def update_game_config(self, start_category: str = None, end_category: str = None,
                          max_players: int = None, countdown_seconds: int = None) -> None:
        """Update game configuration"""
        if start_category is not None:
            self.game.default_start_category = start_category
        if end_category is not None:
            self.game.default_end_category = end_category
        if max_players is not None:
            self.game.max_players_per_room = max_players
        if countdown_seconds is not None:
            self.game.countdown_seconds = countdown_seconds
        
        if self._auto_save:
            self.save_config()
        
        self.config_changed.emit("game")
    
    def update_ui_config(self, player_name: str = None, remember_name: bool = None,
                        show_notifications: bool = None, sound_effects: bool = None) -> None:
        """Update UI configuration"""
        if player_name is not None:
            self.ui.last_player_name = player_name
        if remember_name is not None:
            self.ui.remember_player_name = remember_name
        if show_notifications is not None:
            self.ui.show_progress_notifications = show_notifications
        if sound_effects is not None:
            self.ui.enable_sound_effects = sound_effects
        
        if self._auto_save:
            self.save_config()
        
        self.config_changed.emit("ui")
    
    def get_server_url(self) -> str:
        """Get the complete server URL"""
        return self.server.url
    
    def is_reconnection_enabled(self) -> bool:
        """Check if automatic reconnection is enabled"""
        return self.reconnection.enabled
    
    def get_reconnection_delay(self, attempt: int) -> float:
        """Get the delay for a specific reconnection attempt"""
        return self.reconnection.get_delay(attempt)
    
    def get_player_name(self) -> str:
        """Get the last used player name"""
        return self.ui.last_player_name if self.ui.remember_player_name else ""
    
    def set_auto_save(self, enabled: bool) -> None:
        """Enable or disable automatic saving"""
        self._auto_save = enabled
    
    def export_config(self, file_path: str) -> bool:
        """Export configuration to a specific file"""
        try:
            data = self.to_dict()
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Failed to export config: {e}")
            return False
    
    def import_config(self, file_path: str) -> bool:
        """Import configuration from a specific file"""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            self.from_dict(data)
            
            if self._auto_save:
                self.save_config()
            
            self.config_changed.emit("all")
            return True
            
        except Exception as e:
            print(f"Failed to import config: {e}")
            return False
    
    def validate_config(self) -> Dict[str, list]:
        """Validate configuration and return any issues"""
        issues = {}
        
        # Validate server config
        server_issues = []
        if not self.server.host:
            server_issues.append("Host cannot be empty")
        if not (1 <= self.server.port <= 65535):
            server_issues.append("Port must be between 1 and 65535")
        if self.server.connection_timeout <= 0:
            server_issues.append("Connection timeout must be positive")
        if server_issues:
            issues['server'] = server_issues
        
        # Validate reconnection config
        reconnection_issues = []
        if self.reconnection.max_attempts < 1:
            reconnection_issues.append("Max attempts must be at least 1")
        if self.reconnection.initial_delay <= 0:
            reconnection_issues.append("Initial delay must be positive")
        if self.reconnection.max_delay < self.reconnection.initial_delay:
            reconnection_issues.append("Max delay must be >= initial delay")
        if reconnection_issues:
            issues['reconnection'] = reconnection_issues
        
        # Validate game config
        game_issues = []
        if not (2 <= self.game.max_players_per_room <= 20):
            game_issues.append("Max players must be between 2 and 20")
        if self.game.countdown_seconds < 0:
            game_issues.append("Countdown seconds cannot be negative")
        if game_issues:
            issues['game'] = game_issues
        
        return issues
    
    def __str__(self) -> str:
        """String representation of configuration"""
        return f"MultiplayerConfig(server={self.server.url}, reconnection={self.reconnection.enabled})"


# Global configuration instance
multiplayer_config = MultiplayerConfig()
