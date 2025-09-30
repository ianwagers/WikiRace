# WikiRace Multiplayer Server

FastAPI + Socket.IO server for real-time multiplayer Wikipedia racing. Production-ready with Docker deployment support.

## Quick Start

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Start the server:
   ```bash
   python start_server.py
   ```

The server will start on `http://localhost:8000` by default.

## Configuration

Create a `.env` file in the server directory to customize settings:

```env
HOST=0.0.0.0
PORT=8000
DEBUG=false
REDIS_URL=redis://localhost:6379
MAX_PLAYERS_PER_ROOM=10
```

## API Endpoints

- `GET /` - Health check
- `GET /health` - Detailed server status
- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /redoc` - Alternative API documentation

## Socket.IO Events

### Client → Server
- `create_room` - Create a new game room
- `join_room` - Join an existing room
- `leave_room` - Leave current room
- `set_profile` - Update player display name
- `start_game` - Host starts the game
- `player_progress` - Update player navigation progress
- `player_finished` - Player completed the race
- `ping` - Test connection

### Server → Client
- `connected` - Connection confirmation
- `room_created` - Room creation success
- `player_joined` - Player joined room
- `player_left` - Player left room
- `countdown_start` - Game countdown begins
- `countdown_tick` - Countdown timer updates
- `game_start` - Game begins
- `game_end` - Game completed
- `navigation_update` - Real-time player progress
- `room_config_update` - Host configuration changes
- `error` - Error message

## Development

The server is built with:
- **FastAPI** - Web framework and REST API
- **Socket.IO** - Real-time bidirectional communication
- **Pydantic** - Data validation and serialization
- **Redis** - Session storage (planned)

## Architecture

- `main.py` - Server entry point and FastAPI app
- `models.py` - Data models (GameRoom, Player, GameState)
- `room_manager.py` - Room lifecycle management
- `socket_handlers.py` - Socket.IO event handlers
- `config.py` - Configuration settings
