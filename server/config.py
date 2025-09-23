"""
Configuration settings for WikiRace Multiplayer Server
"""

import os
from typing import List
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Server settings
    HOST: str = "0.0.0.0"  # Bind to all interfaces for cross-device access
    PORT: int = 8001  # Changed from 8000 to avoid port conflicts
    DEBUG: bool = False
    
    # CORS settings
    ALLOWED_ORIGINS: List[str] = ["*"]  # In production, specify actual origins
    
    # Redis settings
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_DB: int = 0
    
    # Game settings
    MAX_PLAYERS_PER_ROOM: int = 10
    ROOM_CODE_LENGTH: int = 4
    ROOM_EXPIRY_HOURS: int = 2
    
    # Rate limiting
    MAX_ROOMS_PER_IP: int = 5
    RATE_LIMIT_WINDOW: int = 3600  # 1 hour in seconds
    
    class Config:
        # Find .env file relative to this config file's location
        env_file = Path(__file__).parent / ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
