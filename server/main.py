"""
WikiRace Multiplayer Server - Main Entry Point

FastAPI + Socket.IO server for real-time multiplayer Wikipedia racing.
"""

import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import socketio

try:
    # Try relative imports first (when used as a package)
    from .config import settings
    from .models import GameRoom, Player, GameState
    from .room_manager import RoomManager
    from .socket_handlers import register_socket_handlers
    from .api_routes import router, set_room_manager
except ImportError:
    # Fall back to absolute imports (when run directly)
    from config import settings
    from models import GameRoom, Player, GameState
    from room_manager import RoomManager
    from socket_handlers import register_socket_handlers
    from api_routes import router, set_room_manager

# Initialize FastAPI app
app = FastAPI(
    title="WikiRace Multiplayer Server",
    description="Real-time multiplayer server for Wikipedia racing game",
    version="1.0.0"
)

# Configure CORS for client connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Socket.IO server
sio = socketio.AsyncServer(
    cors_allowed_origins=settings.ALLOWED_ORIGINS,
    async_mode="asgi"
)

# Create Socket.IO ASGI app
socket_app = socketio.ASGIApp(sio, app)

# Initialize room manager
room_manager = RoomManager()

# Set room manager for API routes
set_room_manager(room_manager)

# Include API routes
app.include_router(router)

# Register Socket.IO event handlers
register_socket_handlers(sio, room_manager)

# Initialize Redis connection on startup
@app.on_event("startup")
async def startup_event():
    """Initialize Redis connection on server startup"""
    await room_manager.initialize_redis()

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up Redis connection on server shutdown"""
    try:
        from .redis_manager import redis_manager
    except ImportError:
        from redis_manager import redis_manager
    await redis_manager.disconnect()

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "WikiRace Multiplayer Server",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "rooms_active": len(room_manager.rooms),
        "total_players": sum(len(room.players) for room in room_manager.rooms.values())
    }

if __name__ == "__main__":
    # Run the server
    uvicorn.run(
        "server.main:socket_app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info" if not settings.DEBUG else "debug"
    )
