# WikiRace Multiplayer Server Setup

## Phase 1 Implementation Complete ✅

This document outlines what has been implemented in Phase 1 of the multiplayer server development.

## What's Been Implemented

### 1. Server Foundation ✅
- **FastAPI Application**: Complete web server with CORS support
- **Socket.IO Integration**: Real-time bidirectional communication
- **Project Structure**: Organized server directory with modular components
- **Dependencies**: Updated pyproject.toml with multiplayer dependencies

### 2. Core Data Models ✅
- **GameRoom**: Complete room management with validation
- **Player**: Player state tracking with game progress
- **GameState**: Enum for game lifecycle states
- **Request/Response Models**: API data validation with Pydantic

### 3. Redis Integration ✅
- **RedisManager**: Complete Redis connection and operations
- **Session Storage**: Room and player data persistence
- **Automatic TTL**: Room expiration handling
- **Fallback Support**: Graceful degradation without Redis

### 4. Room Management API ✅
- **POST /api/rooms**: Create new game rooms
- **GET /api/rooms/{code}**: Get room information
- **POST /api/rooms/{code}/join**: Join existing rooms
- **GET /api/rooms**: List all active rooms
- **GET /api/stats**: Server statistics

### 5. Socket.IO Event Handlers ✅
- **Connection Management**: Connect/disconnect handling
- **Room Events**: create_room, join_room, leave_room
- **Player Events**: set_profile, ping/pong
- **Placeholder Events**: Ready for game logic implementation

## File Structure

```
server/
├── __init__.py              # Package initialization
├── main.py                  # FastAPI app and server entry point
├── config.py                # Configuration settings
├── models.py                # Pydantic data models
├── room_manager.py          # Room lifecycle management
├── redis_manager.py         # Redis operations
├── socket_handlers.py       # Socket.IO event handlers
├── api_routes.py            # REST API endpoints
├── start_server.py          # Server startup script
├── test_server.py           # Basic functionality tests
├── requirements.txt         # Server dependencies
├── README.md               # Server documentation
├── SETUP.md                # This file
└── env.example             # Configuration template
```

## Installation & Setup

### 1. Install Server Dependencies
```bash
cd server
pip install -r requirements.txt
```

### 2. Configure Server (Optional)
```bash
cp env.example .env
# Edit .env with your settings
```

### 3. Start Server
```bash
python start_server.py
```

### 4. Test Server
```bash
python test_server.py
```

## API Endpoints

### Health Check
- `GET /` - Basic health check
- `GET /health` - Detailed server status

### Room Management
- `POST /api/rooms` - Create room
- `GET /api/rooms/{code}` - Get room info
- `POST /api/rooms/{code}/join` - Join room
- `GET /api/rooms` - List rooms
- `GET /api/stats` - Server statistics

## Socket.IO Events

### Client → Server
- `create_room` - Create new room
- `join_room` - Join existing room
- `leave_room` - Leave current room
- `set_profile` - Update display name
- `ping` - Test connection

### Server → Client
- `connected` - Connection confirmation
- `room_created` - Room creation success
- `player_joined` - Player joined room
- `player_left` - Player left room
- `error` - Error messages

## Next Steps (Phase 2)

The server foundation is complete and ready for Phase 2 implementation:

1. **Client Network Foundation**: Update client dependencies and create NetworkManager
2. **Enhanced Multiplayer UI**: Update MultiplayerPage and create MultiplayerLobby
3. **Game Integration**: Create MultiplayerGamePage wrapper
4. **Game Logic**: Implement server-side game flow

## Testing

Run the test suite to verify everything works:
```bash
python test_server.py
```

The tests verify:
- Configuration loading
- Data model validation
- Room manager functionality
- Redis integration (if available)

## Notes

- Server runs on `http://localhost:8000` by default
- Redis is optional - server works without it
- All room codes are 4 uppercase letters
- Maximum 10 players per room
- Rooms auto-expire after 2 hours
- CORS is configured for development (*)

## Dependencies Added

The following dependencies were added to the main project:
- `python-socketio[client]>=5.8.0`
- `websocket-client>=1.6.0`
- `python-dotenv>=1.0.0`

Server-specific dependencies (in server/requirements.txt):
- `fastapi>=0.104.0`
- `uvicorn[standard]>=0.24.0`
- `python-socketio>=5.8.0`
- `redis>=5.0.0`
- `pydantic>=2.5.0`
- `httpx>=0.25.0`
