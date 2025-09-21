# WikiRace Multiplayer Architecture Specification

## Overview

This document defines the architecture and implementation strategy for multiplayer functionality in WikiRace, allowing up to 10 players to compete in real-time Wikipedia navigation races.

## Current Architecture Analysis

### Existing Game State Management
The current solo game tracks:
- **Game Timer**: `startTime` (seconds elapsed)
- **Link Counter**: `linksUsed` (number of links clicked)
- **Navigation History**: `previousLinksList` (QListWidget with page titles)
- **Current Page**: Tracked via `onUrlChanged()` events
- **Start/End URLs**: `start_url`, `end_url`, `start_title`, `end_title`
- **Game Completion**: Detected via `checkEndGame()` method

### Current UI Components
- `SoloGamePage`: Main game interface with WebView, sidebar, and controls
- `GameLogic`: Handles page selection and Wikipedia API interactions
- `HomePage`: Entry point with game setup dialogs

## Multiplayer Architecture Design

### 1. Network Architecture

#### Server Component (New)
**Technology Stack**: Flask/FastAPI + Socket.IO for real-time communication
**Deployment**: Self-hosted web server (as mentioned by user)

**Core Responsibilities**:
- Game room management (4-letter codes)
- Player session handling
- Real-time game state synchronization
- Game lifecycle management (lobby → game → results)

#### Client-Server Communication
**Protocol**: WebSocket (Socket.IO) for real-time events
**Fallback**: HTTP REST API for critical operations

**Key Events**:
```python
# Client → Server
'create_room'       # Host creates new game room
'join_room'         # Player joins existing room
'set_profile'       # Player sets display name
'select_categories' # Host selects game parameters
'start_game'        # Host initiates game start
'page_navigation'   # Player navigates to new page
'game_complete'     # Player reaches destination

# Server → Client
'room_created'      # Room successfully created
'player_joined'     # New player joined room
'player_left'       # Player left room
'game_starting'     # Game countdown initiated
'game_started'      # Game officially begins
'player_progress'   # Other players' progress updates
'game_ended'        # First player completed race
'final_results'     # Complete results table
```

### 2. Data Models

#### Game Room
```python
class GameRoom:
    room_code: str          # 4-letter code (e.g., "ABCD")
    host_id: str            # Socket ID of room host
    players: Dict[str, Player]  # Socket ID → Player mapping
    game_state: GameState   # Current game phase
    start_url: str          # Starting Wikipedia page
    end_url: str            # Target Wikipedia page
    start_title: str        # Display title for start page
    end_title: str          # Display title for end page
    categories: List[str]   # Selected categories for page selection
    created_at: datetime    # Room creation timestamp
    game_started_at: Optional[datetime]  # Game start time
```

#### Player
```python
class Player:
    socket_id: str          # Unique socket connection ID
    display_name: str       # Player's chosen name
    is_host: bool          # Whether player is room host
    current_page: str       # Current Wikipedia page URL
    links_clicked: int      # Number of links used
    navigation_history: List[str]  # Pages visited (titles)
    game_completed: bool    # Whether reached destination
    completion_time: Optional[int]  # Time to complete (seconds)
    joined_at: datetime     # When player joined room
```

#### Game State
```python
class GameState(Enum):
    LOBBY = "lobby"         # Players joining, host configuring
    STARTING = "starting"   # Countdown before game begins
    IN_PROGRESS = "in_progress"  # Game actively running
    COMPLETED = "completed" # Game finished, showing results
    ABANDONED = "abandoned" # Room closed/expired
```

### 3. Client-Side Architecture

#### New Components

**MultiplayerGamePage** (extends/wraps SoloGamePage):
- Inherits core game UI and Wikipedia navigation
- Adds multiplayer-specific UI elements:
  - Other players' progress sidebar
  - Real-time status updates
  - Multiplayer results table
- Handles network communication for game events

**MultiplayerLobby** (replaces current placeholder):
- Room creation/joining interface
- Player profile setup
- Game configuration (categories, custom pages)
- Real-time lobby updates

**NetworkManager** (replaces placeholder Network.py):
- Socket.IO client management
- Event handling and message routing
- Connection state management
- Automatic reconnection logic

#### Modified Components

**MultiplayerPage** (enhanced):
- Entry point for multiplayer functionality
- Room code input/generation
- Profile name setup
- Navigation to lobby or game

### 4. Game Flow Design

#### Phase 1: Room Creation/Joining
1. Player clicks "Multiplayer" from HomePage
2. **Host Path**:
   - Enters display name
   - Clicks "Host Game"
   - Server generates 4-letter room code
   - Host enters lobby as room leader
3. **Join Path**:
   - Enters display name and room code
   - Clicks "Join Game"
   - Server validates room exists and has space
   - Player enters lobby

#### Phase 2: Lobby Configuration
- **All Players**: See real-time list of joined players
- **Host Only**: 
  - Select starting/ending page categories (or custom)
  - Configure game settings
  - "Start Game" button (grayed until ready)
- **Real-time Updates**: Players see configuration changes instantly

#### Phase 3: Game Execution
1. Host clicks "Start Game"
2. Server selects start/end pages using existing GameLogic
3. All players receive same start/end URLs
4. 3-second countdown displayed to all players
5. Game begins simultaneously for all players
6. **During Game**:
   - Each player's navigation tracked locally
   - Page changes broadcast to other players
   - Progress sidebar shows other players' current pages
   - Link counts updated in real-time

#### Phase 4: Game Completion
1. First player to reach destination triggers game end
2. Server immediately notifies all players: "Game Over"
3. All players' games freeze/become read-only
4. Results table displayed showing:
   - Final ranking (completion order)
   - Each player's total time
   - Each player's link count
   - Complete navigation path for each player

### 5. UI/UX Enhancements

#### Multiplayer Lobby UI
```
┌─────────────────────────────────────────────┐
│ Room: ABCD        👥 Players: 3/10          │
├─────────────────────────────────────────────┤
│ Players:                                    │
│ • 🏆 Alice (Host)                           │
│ • 🔹 Bob                                    │
│ • 🔹 Charlie                               │
├─────────────────────────────────────────────┤
│ Game Setup: (Host Only)                    │
│ Start: [Animals ▼] End: [Countries ▼]     │
│                                            │
│ [Start Game] (Host) / [Ready] (Others)     │
└─────────────────────────────────────────────┘
```

#### Multiplayer Game UI
```
┌──────────────────┬─────────────────────────┐
│ Players Progress │ Main Game Area          │
│ 🏆 Alice (Host)  │ ┌─────────────────────┐ │
│ 📄 Tiger (3)     │ │ Destination:        │ │
│                  │ │ United States       │ │
│ 🔹 Bob           │ ├─────────────────────┤ │
│ 📄 Lion (2)      │ │                     │ │
│                  │ │ [Wikipedia Content] │ │
│ 🔹 Charlie       │ │                     │ │
│ 📄 Elephant (4)  │ │                     │ │
│                  │ └─────────────────────┘ │
│ ⏱️ 02:34         │ Your Progress:          │
│ 🔗 Links: 5      │ 🏁 Lion → Tiger → ...   │
└──────────────────┴─────────────────────────┘
```

#### Results Table UI
```
┌─────────────────────────────────────────────┐
│ 🏆 Race Results                             │
├──────┬─────────┬──────┬──────┬─────────────┤
│ Rank │ Player  │ Time │ Links│ Path        │
├──────┼─────────┼──────┼──────┼─────────────┤
│ 1st  │ Alice   │ 2:34 │ 5    │ [View Path] │
│ 2nd  │ Bob     │ 3:12 │ 7    │ [View Path] │
│ 3rd  │ Charlie │ DNF  │ 4    │ [View Path] │
└──────┴─────────┴──────┴──────┴─────────────┘
```

### 6. Technical Implementation Strategy

#### Server Setup
1. **Framework**: FastAPI + Socket.IO for real-time communication
2. **Database**: Redis for session storage, room management
3. **Deployment**: Docker container on user's server
4. **Configuration**: Environment variables for host/port settings

#### Client Integration
1. **Minimal Code Changes**: Leverage existing SoloGamePage as base
2. **Wrapper Approach**: MultiplayerGamePage wraps SoloGamePage
3. **Event-Driven**: Use Qt signals/slots for network event handling
4. **Graceful Degradation**: Handle network disconnections gracefully

#### Dependencies
```toml
# Additional dependencies for multiplayer
"python-socketio[client]>=5.8.0"
"websocket-client>=1.6.0"
"python-dotenv>=1.0.0"  # For server configuration
```

### 7. Error Handling & Edge Cases

#### Network Issues
- **Connection Loss**: Automatic reconnection with game state recovery
- **Server Down**: Graceful fallback to solo mode
- **Lag/Latency**: Optimistic UI updates with server reconciliation

#### Game Management
- **Host Leaves**: Automatic host transfer to next player
- **Player Drops**: Remove from game, continue with remaining players
- **Room Expiration**: Auto-cleanup after 2 hours of inactivity
- **Invalid Room Codes**: Clear error messages and suggestions

#### Race Conditions
- **Simultaneous Completion**: Server timestamp determines winner
- **Page Load Timing**: Server validates page navigation events
- **Duplicate Room Codes**: Server ensures uniqueness

### 8. Security Considerations

#### Input Validation
- Room codes: 4 uppercase letters only
- Display names: Sanitized, length limited
- Page URLs: Validate Wikipedia domain only

#### Rate Limiting
- Room creation: Max 5 rooms per IP per hour
- Page navigation: Reasonable limits to prevent spam
- Connection attempts: Prevent connection flooding

#### Privacy
- No persistent user data storage
- Room data purged after completion
- Minimal logging (errors only)

### 9. Detailed Development Roadmap

#### Phase 1: Server Foundation (Week 1)

1. **Set up FastAPI server project structure**
   - Create `server/` directory in project root
   - Initialize FastAPI application with basic routing
   - Set up project dependencies (FastAPI, Socket.IO, Redis)
   - Create basic server entry point (`server/main.py`)

2. **Implement core data models**
   - Create `server/models.py` with GameRoom, Player, GameState classes
   - Implement data validation using Pydantic models
   - Add utility methods for room code generation (4-letter codes)

3. **Set up Redis for session storage**
   - Configure Redis connection and basic operations
   - Implement room storage/retrieval functions
   - Create player session management functions

4. **Implement basic room management endpoints**
   - POST `/api/rooms` - Create new game room
   - GET `/api/rooms/{room_code}` - Get room information
   - POST `/api/rooms/{room_code}/join` - Join existing room
   - DELETE `/api/rooms/{room_code}/leave` - Leave room

5. **Set up Socket.IO server integration**
   - Initialize Socket.IO server with FastAPI
   - Implement basic connection/disconnection handlers
   - Create room-based event broadcasting system

#### Phase 2: Client Network Foundation (Week 1-2)

6. **Update project dependencies**
   - Add `python-socketio[client]>=5.8.0` to pyproject.toml
   - Add `websocket-client>=1.6.0` for WebSocket support
   - Update requirements and test installation

7. **Create NetworkManager class**
   - Replace placeholder `src/logic/Network.py` with full implementation
   - Implement Socket.IO client connection management
   - Add methods for room creation, joining, and leaving
   - Create event handler registration system

8. **Implement network event handling**
   - Create event dispatcher using Qt signals/slots
   - Implement connection state management (connected/disconnected)
   - Add basic error handling for network operations

9. **Create multiplayer configuration classes**
   - Create `src/logic/MultiplayerConfig.py` for game settings
   - Implement player profile management (display name storage)
   - Add room code validation and formatting utilities

#### Phase 3: Enhanced Multiplayer UI (Week 2)

10. **Update MultiplayerPage with room interface**
    - Replace placeholder UI with room creation/joining interface
    - Add text input for display name (required field)
    - Add "Host Game" button that creates room and shows code
    - Add room code input field and "Join Game" button
    - Implement basic form validation and user feedback

11. **Create MultiplayerLobby widget**
    - Create `src/gui/MultiplayerLobby.py` as new QWidget
    - Implement real-time player list display
    - Add host-only game configuration controls (category selection)
    - Create "Start Game" button (enabled only for host)
    - Add "Leave Room" functionality

12. **Implement lobby real-time updates**
    - Connect NetworkManager events to lobby UI updates
    - Handle player join/leave events with visual updates
    - Update game configuration when host changes settings
    - Show connection status and room information

13. **Create game configuration dialog**
    - Extend existing category selection UI for multiplayer
    - Add multiplayer-specific options (if any)
    - Integrate with existing GameLogic for page selection
    - Ensure host selections are broadcast to all players

#### Phase 4: Core Game Integration (Week 3)

14. **Create MultiplayerGamePage wrapper**
    - Create `src/gui/MultiplayerGamePage.py` extending QWidget
    - Embed existing SoloGamePage as main content area
    - Add multiplayer-specific sidebar for other players' progress
    - Implement layout with resizable splitter

15. **Implement game state synchronization**
    - Modify SoloGamePage to emit navigation events
    - Connect URL change events to NetworkManager
    - Broadcast player page changes to server
    - Receive and display other players' progress updates

16. **Add multiplayer progress sidebar**
    - Create player progress widget showing other players
    - Display each player's current page and link count
    - Add visual indicators for player status (active, completed)
    - Update progress in real-time as events are received

17. **Implement game start synchronization**
    - Handle "game_starting" event with countdown display
    - Receive start/end URLs from server simultaneously
    - Initialize all players with identical game parameters
    - Start game timer synchronously across all clients

#### Phase 5: Game Flow Implementation (Week 3-4)

18. **Implement server-side game logic integration**
    - Integrate existing GameLogic.py methods on server
    - Implement page selection based on host's category choices
    - Broadcast selected start/end pages to all room players
    - Handle custom page validation on server side

19. **Add game lifecycle management**
    - Implement game state transitions (lobby → starting → in_progress → completed)
    - Handle host-initiated game start with server validation
    - Manage game timer and synchronization across clients
    - Implement game completion detection and broadcasting

20. **Create multiplayer game completion handling**
    - Detect when any player reaches the destination page
    - Immediately broadcast game_ended event to all players
    - Freeze all players' games (disable navigation)
    - Collect final game statistics from all players

21. **Implement navigation tracking for multiplayer**
    - Extend existing link counting to track detailed navigation history
    - Send page navigation events to server with timestamps
    - Store complete path history for results display
    - Handle navigation validation and synchronization

#### Phase 6: Results and UI Polish (Week 4)

22. **Create multiplayer results dialog**
    - Create `src/gui/MultiplayerResultsDialog.py` extending QDialog
    - Design results table with player rankings
    - Show completion times, link counts, and final status
    - Add "View Path" functionality for each player's route

23. **Implement results data collection**
    - Collect final statistics from all players
    - Calculate rankings based on completion time and status
    - Generate comprehensive results data structure
    - Handle players who didn't finish (DNF status)

24. **Add path visualization feature**
    - Create expandable path display for each player
    - Show complete navigation history with page titles
    - Add timestamps for each navigation step
    - Implement path comparison between players

25. **Polish multiplayer UI components**
    - Apply consistent theming to all multiplayer components
    - Add loading states and progress indicators
    - Implement smooth transitions between game phases
    - Add proper error messages and user feedback

#### Phase 7: Server Game Logic (Week 4-5)

26. **Implement server-side room lifecycle**
    - Handle room creation with unique code generation
    - Manage player joining with capacity limits (10 players max)
    - Implement host privileges and host transfer logic
    - Add room cleanup and expiration handling

27. **Add server-side game state management**
    - Track game phases for each room (lobby/starting/in_progress/completed)
    - Implement game start validation and countdown
    - Handle real-time player progress tracking
    - Manage game completion and results aggregation

28. **Implement server event broadcasting**
    - Create room-specific event broadcasting system
    - Handle player progress updates and redistribution
    - Implement game state change notifications
    - Add player join/leave event handling

29. **Add server-side game logic**
    - Port relevant parts of GameLogic.py to server
    - Implement page selection based on categories
    - Handle custom page validation using Wikipedia API
    - Ensure consistent game parameters across all players

#### Phase 8: Integration and Testing (Week 5)

30. **Integrate server and client components**
    - Test complete room creation and joining flow
    - Verify real-time communication between all components
    - Test game start synchronization with multiple clients
    - Validate game completion and results display

31. **Implement comprehensive error handling**
    - Add connection error handling and user feedback
    - Handle server disconnection gracefully
    - Implement basic reconnection logic
    - Add validation for all user inputs

32. **Add application integration**
    - Update MainApplication to handle multiplayer tabs
    - Integrate multiplayer flow with existing tab management
    - Ensure proper cleanup when closing multiplayer tabs
    - Test integration with existing theme management

33. **Create multiplayer game flow testing**
    - Test complete multiplayer game from start to finish
    - Verify all UI updates happen correctly
    - Test with multiple players simultaneously
    - Validate results accuracy and display

#### Phase 9: Final Polish and Documentation (Week 6)

34. **Add server configuration management**
    - Create server configuration file (config.yaml)
    - Add environment variable support for server settings
    - Implement basic server logging
    - Create server startup scripts

35. **Update client configuration**
    - Add server connection settings to client
    - Create configuration UI for server host/port
    - Add connection status indicators
    - Implement server discovery/connection testing

36. **Create user documentation**
    - Write setup instructions for server deployment
    - Create user guide for multiplayer functionality
    - Add troubleshooting guide for common issues
    - Document server requirements and setup

37. **Final testing and bug fixes**
    - Comprehensive testing of all multiplayer features
    - Performance testing with maximum players (10)
    - UI/UX testing and polish
    - Bug fixes and stability improvements

38. **Package and deployment preparation**
    - Create server deployment package/Docker container
    - Update client build process to include new dependencies
    - Create installation scripts for easy setup
    - Prepare release documentation

#### Development Milestones

**End of Week 2**: Basic server running, client can create/join rooms, lobby UI functional
**End of Week 3**: Complete multiplayer game flow working, basic results display
**End of Week 4**: Full feature set implemented, comprehensive testing completed
**End of Week 5**: Polish completed, documentation written, ready for deployment
**End of Week 6**: Final testing, packaging, and deployment preparation complete

### 10. Future Enhancements

#### Advanced Features
- **Spectator Mode**: Allow observers in completed games
- **Tournament Mode**: Bracket-style competitions
- **Custom Challenges**: User-created page combinations
- **Statistics**: Player performance tracking
- **Replay System**: Review completed games

#### Social Features
- **Friends Lists**: Add/invite friends to games
- **Achievements**: Unlock badges for various accomplishments
- **Leaderboards**: Global and friends-only rankings

## Conclusion

This multiplayer architecture leverages the existing robust solo game implementation while adding minimal complexity to the client. The server-centric approach ensures consistent game state across all players while the wrapper pattern allows reuse of the well-tested SoloGamePage functionality.

The design prioritizes:
1. **Minimal Client Changes**: Reuse existing game logic
2. **Real-time Experience**: Smooth multiplayer interactions
3. **Scalability**: Support for multiple concurrent games
4. **Reliability**: Graceful handling of network issues
5. **User Experience**: Intuitive UI matching existing design patterns

Implementation can proceed incrementally, with each phase building upon the previous while maintaining backward compatibility with solo gameplay.
