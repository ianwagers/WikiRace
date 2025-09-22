#!/usr/bin/env python3
"""
Automatic Context Updater for WikiRace Project

This script automatically updates the .cursorrules file and other documentation
based on the current state of the project. It can be run manually or as part
of a git hook to keep documentation synchronized with code changes.

Usage:
    python scripts/update_context.py
    python scripts/update_context.py --check  # Check if updates are needed
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set

class ProjectAnalyzer:
    """Analyzes the project structure and generates context information"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.src_dir = project_root / "src"
        self.server_dir = project_root / "server"
        self.docs_dir = project_root / "docs"
        
    def get_project_stats(self) -> Dict:
        """Get basic project statistics"""
        stats = {
            "total_python_files": 0,
            "total_lines_of_code": 0,
            "gui_components": 0,
            "logic_components": 0,
            "server_components": 0,
            "test_files": 0,
            "doc_files": 0,
            "last_updated": datetime.now().isoformat()
        }
        
        # Count Python files and lines
        for py_file in self.project_root.rglob("*.py"):
            if "venv" in str(py_file) or "__pycache__" in str(py_file):
                continue
                
            stats["total_python_files"] += 1
            
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    lines = len([line for line in f if line.strip() and not line.strip().startswith('#')])
                    stats["total_lines_of_code"] += lines
            except:
                continue
                
            # Categorize files
            if "src/gui" in str(py_file):
                stats["gui_components"] += 1
            elif "src/logic" in str(py_file):
                stats["logic_components"] += 1
            elif "server/" in str(py_file):
                stats["server_components"] += 1
            elif "test" in str(py_file).lower():
                stats["test_files"] += 1
        
        # Count documentation files
        if self.docs_dir.exists():
            stats["doc_files"] = len(list(self.docs_dir.glob("*.md")))
        
        return stats
    
    def get_recent_changes(self) -> List[str]:
        """Get recent git changes (if in a git repository)"""
        try:
            # Get recent commits
            result = subprocess.run(
                ["git", "log", "--oneline", "-10"],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            if result.returncode == 0:
                return result.stdout.strip().split('\n')
        except:
            pass
        return []
    
    def get_key_files(self) -> Dict[str, List[str]]:
        """Get lists of key files by category"""
        key_files = {
            "entry_points": [],
            "gui_components": [],
            "logic_components": [],
            "server_components": [],
            "config_files": [],
            "documentation": []
        }
        
        # Entry points
        if (self.project_root / "bin" / "main.py").exists():
            key_files["entry_points"].append("bin/main.py")
        if (self.project_root / "src" / "app.py").exists():
            key_files["entry_points"].append("src/app.py")
        
        # GUI components
        if self.src_dir.exists():
            gui_dir = self.src_dir / "gui"
            if gui_dir.exists():
                key_files["gui_components"] = [
                    f"src/gui/{f.name}" for f in gui_dir.glob("*.py") 
                    if not f.name.startswith("__")
                ]
        
        # Logic components
        if self.src_dir.exists():
            logic_dir = self.src_dir / "logic"
            if logic_dir.exists():
                key_files["logic_components"] = [
                    f"src/logic/{f.name}" for f in logic_dir.glob("*.py")
                    if not f.name.startswith("__")
                ]
        
        # Server components
        if self.server_dir.exists():
            key_files["server_components"] = [
                f"server/{f.name}" for f in self.server_dir.glob("*.py")
                if not f.name.startswith("__")
            ]
        
        # Config files
        config_patterns = ["*.toml", "*.yaml", "*.yml", "*.json", "*.env*"]
        for pattern in config_patterns:
            for f in self.project_root.glob(pattern):
                if f.is_file() and "venv" not in str(f):
                    key_files["config_files"].append(str(f.relative_to(self.project_root)))
        
        # Documentation
        if self.docs_dir.exists():
            key_files["documentation"] = [
                f"docs/{f.name}" for f in self.docs_dir.glob("*.md")
            ]
        
        return key_files

class ContextUpdater:
    """Updates the .cursorrules file and other documentation"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.analyzer = ProjectAnalyzer(project_root)
        self.cursorrules_path = project_root / ".cursorrules"
        
    def needs_update(self) -> bool:
        """Check if the context file needs updating"""
        if not self.cursorrules_path.exists():
            return True
            
        # Check if key files have been modified more recently than .cursorrules
        cursorrules_mtime = self.cursorrules_path.stat().st_mtime
        
        key_paths = [
            "pyproject.toml",
            "src/",
            "server/",
            "docs/",
            "README.md"
        ]
        
        for path_str in key_paths:
            path = self.project_root / path_str
            if path.exists():
                if path.is_file():
                    if path.stat().st_mtime > cursorrules_mtime:
                        return True
                else:
                    # Check directory for recent changes
                    for file_path in path.rglob("*"):
                        if file_path.is_file() and file_path.stat().st_mtime > cursorrules_mtime:
                            return True
        
        return False
    
    def generate_context_content(self) -> str:
        """Generate updated content for .cursorrules file"""
        stats = self.analyzer.get_project_stats()
        recent_changes = self.analyzer.get_recent_changes()
        key_files = self.analyzer.get_key_files()
        
        # Read version from pyproject.toml
        version = "1.7.0"
        try:
            import tomllib
            with open(self.project_root / "pyproject.toml", "rb") as f:
                data = tomllib.load(f)
                version = data.get("project", {}).get("version", version)
        except:
            pass
        
        content = f"""# WikiRace - Global Project Context for Cursor AI

## Project Overview
WikiRace is a desktop Wikipedia navigation game built with PyQt6 and Python 3.13. Originally a solo game, it has been significantly expanded with real-time multiplayer functionality using a FastAPI + Socket.IO server architecture.

## Current Status: v{version} (Beta with Multiplayer)
- ✅ Solo gameplay fully functional
- ✅ Multiplayer server infrastructure complete
- ✅ Real-time room management and player communication
- 🔄 Multiplayer game flow implementation in progress
- 🔄 UI polish and testing ongoing

## Project Statistics (Auto-generated)
- **Total Python Files**: {stats['total_python_files']}
- **Lines of Code**: {stats['total_lines_of_code']}
- **GUI Components**: {stats['gui_components']}
- **Logic Components**: {stats['logic_components']}
- **Server Components**: {stats['server_components']}
- **Documentation Files**: {stats['doc_files']}
- **Last Updated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Architecture Overview

### Client Application (PyQt6)
- **Entry Points**: {', '.join(key_files['entry_points']) if key_files['entry_points'] else 'None'}
- **Main Window**: `src/gui/MainApplication.py` (tab-based interface)
- **Core Pages**: HomePage, SoloGamePage, MultiplayerPage
- **Game Logic**: `src/logic/GameLogic.py` (Wikipedia API, page selection)
- **Network**: `src/logic/Network.py` (Socket.IO client, REST API calls)
- **Theming**: `src/logic/ThemeManager.py` (dark/light mode support)

### Multiplayer Server (FastAPI + Socket.IO)
- **Location**: `server/` directory
- **Entry**: `server/start_server.py` → `server/main.py`
- **Models**: `server/models.py` (GameRoom, Player, GameState)
- **Room Management**: `server/room_manager.py`
- **Socket Events**: `server/socket_handlers.py`
- **API Routes**: `server/api_routes.py`
- **Config**: `server/config.py`

## Key Technologies
- **Frontend**: PyQt6, PyQt6-WebEngine (Wikipedia display)
- **Backend**: FastAPI, Socket.IO, Pydantic
- **Data**: Redis (planned for persistence), in-memory storage (current)
- **APIs**: Wikipedia API, MediaWiki API
- **Build**: setuptools, pyproject.toml

## Project Structure
```
WikiRace/
├── bin/main.py                 # Application entry point
├── src/                        # Main application code
│   ├── app.py                  # Application initialization
│   ├── gui/                    # PyQt6 UI components ({stats['gui_components']} files)
│   │   ├── MainApplication.py  # Main window with tabs
│   │   ├── HomePage.py         # Landing page and game setup
│   │   ├── SoloGamePage.py     # Solo Wikipedia racing game
│   │   ├── MultiplayerPage.py  # Multiplayer room management
│   │   └── ...                 # Other UI components
│   ├── logic/                  # Business logic ({stats['logic_components']} files)
│   │   ├── GameLogic.py        # Core game mechanics
│   │   ├── Network.py          # Multiplayer networking
│   │   ├── ThemeManager.py     # UI theming system
│   │   └── ...
│   └── resources/              # Assets (icons, images)
├── server/                     # Multiplayer server ({stats['server_components']} files)
│   ├── main.py                 # FastAPI application
│   ├── start_server.py         # Server startup script
│   ├── models.py               # Data models (Pydantic)
│   ├── room_manager.py         # Game room lifecycle
│   ├── socket_handlers.py      # Socket.IO events
│   ├── api_routes.py           # REST API endpoints
│   └── config.py               # Server configuration
├── docs/                       # Documentation ({stats['doc_files']} files)
│   ├── MULTIPLAYER_SPEC.md     # Detailed multiplayer architecture
│   ├── SETUP_INSTRUCTIONS.md   # Installation guide
│   └── ...
├── tests/                      # Test files ({stats['test_files']} files)
├── pyproject.toml              # Project configuration
└── README.md                   # Project overview
```

## Core Game Flow

### Solo Game
1. User selects "Solo Game" from HomePage
2. GameLogic selects random start/end Wikipedia pages
3. SoloGamePage displays embedded Wikipedia content
4. Player navigates by clicking links, timer tracks progress
5. Game ends when target page is reached

### Multiplayer Game (Current Implementation)
1. **Room Setup**: Player creates/joins room via MultiplayerPage
2. **Lobby**: Real-time player list, host configures game
3. **Game Start**: Server selects pages, synchronizes all clients
4. **Racing**: Players navigate independently, progress shared
5. **Results**: First to finish triggers end, rankings displayed

## Key Classes and Components

### Client-Side Core Classes
- **MainApplication**: Main window, tab management, theme handling
- **HomePage**: Game mode selection, settings, about info
- **SoloGamePage**: Complete solo game implementation with WebView
- **MultiplayerPage**: Room creation/joining, lobby management
- **GameLogic**: Wikipedia API integration, page selection algorithms
- **NetworkManager**: Socket.IO client, server communication
- **ThemeManager**: Dark/light theme system with Qt stylesheets

### Server-Side Core Classes
- **GameRoom**: Room state, player management, game configuration
- **Player**: Individual player state, progress tracking
- **RoomManager**: Room lifecycle, cleanup, host transfers
- **SocketHandler**: Real-time event handling for multiplayer
- **APIRoutes**: REST endpoints for room operations

## Current Development Focus
The project is transitioning from a working solo game to a full multiplayer experience. Key areas of active development:

1. **Game State Synchronization**: Ensuring all players start simultaneously with identical conditions
2. **Real-time Progress Tracking**: Broadcasting player navigation events
3. **Results System**: Collecting and displaying final race results
4. **UI Polish**: Improving multiplayer interface consistency
5. **Error Handling**: Graceful network disconnection recovery

## Code Patterns and Conventions

### PyQt6 Patterns
- Use Qt signals/slots for event handling
- Apply consistent theming via ThemeManager
- Implement proper widget lifecycle (show/hide/cleanup)
- Use QTimer for periodic updates

### Networking Patterns
- Socket.IO events for real-time communication
- REST API for stateful operations (room creation/joining)
- Pydantic models for data validation
- Qt signals to bridge network events to UI updates

### Error Handling
- Try/catch around all network operations
- User-friendly error messages via QMessageBox
- Graceful degradation when server unavailable
- Logging for debugging (print statements currently)

## Dependencies and Requirements
- **Python**: 3.13+ (strict requirement)
- **PyQt6**: 6.7.0+ (GUI framework)
- **PyQt6-WebEngine**: 6.7.0+ (Wikipedia page display)
- **Requests**: 2.32.0+ (HTTP API calls)
- **BeautifulSoup4**: 4.12.0+ (HTML parsing)
- **Socket.IO Client**: 5.8.0+ (real-time communication)
- **FastAPI**: Latest (server framework)
- **Pydantic**: Latest (data validation)

## Testing Strategy
- Unit tests for core game logic
- Integration tests for multiplayer flow
- Manual testing with multiple clients
- Server stress testing with max players (10)

## Deployment Considerations
- Client: Standalone executable for Windows
- Server: Self-hosted deployment (user's server)
- Configuration: Environment variables for server settings
- Docker: Container deployment for server (planned)

## Known Issues and TODOs
- [ ] Complete multiplayer game flow implementation
- [ ] Add Redis persistence for room state
- [ ] Implement reconnection logic for network drops
- [ ] Add comprehensive error handling
- [ ] Create deployment packages
- [ ] Performance optimization for 10+ concurrent players

## Development Guidelines
- Maintain backward compatibility with solo game
- Follow existing UI/UX patterns
- Use type hints for all new code
- Add docstrings for public methods
- Test multiplayer features with multiple clients
- Keep server and client loosely coupled"""

        # Add recent changes if available
        if recent_changes:
            content += f"""

## Recent Changes (Auto-detected)
{chr(10).join(f'- {change}' for change in recent_changes[:5])}"""

        content += f"""

## File Modification Patterns
When working on this project, common modification patterns include:
- **GUI Updates**: Modify files in `src/gui/` and update theme applications
- **Game Logic**: Changes in `src/logic/` often require testing both solo and multiplayer modes
- **Server Changes**: Modifications in `server/` require server restart and client testing
- **Dependencies**: Updates to `pyproject.toml` need virtual environment refresh

## Auto-Update Information
This context file was automatically updated on {datetime.now().strftime('%Y-%m-%d at %H:%M:%S')}.
To manually update: `python scripts/update_context.py`
To check if updates are needed: `python scripts/update_context.py --check`

This context should be automatically updated when significant architectural changes are made to the project."""

        return content
    
    def update_context(self) -> bool:
        """Update the .cursorrules file with current project information"""
        try:
            content = self.generate_context_content()
            
            # Backup existing file if it exists
            if self.cursorrules_path.exists():
                backup_path = self.cursorrules_path.with_suffix(".cursorrules.backup")
                self.cursorrules_path.rename(backup_path)
            
            # Write new content
            with open(self.cursorrules_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ Updated {self.cursorrules_path}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to update context: {e}")
            return False

def main():
    """Main entry point"""
    project_root = Path(__file__).parent.parent
    updater = ContextUpdater(project_root)
    
    if len(sys.argv) > 1 and sys.argv[1] == "--check":
        # Check if update is needed
        if updater.needs_update():
            print("📋 Context file needs updating")
            sys.exit(1)
        else:
            print("✅ Context file is up to date")
            sys.exit(0)
    
    # Perform update
    print("🔄 Checking if context update is needed...")
    if updater.needs_update():
        print("📋 Context file needs updating...")
        if updater.update_context():
            print("✅ Context successfully updated!")
        else:
            print("❌ Failed to update context")
            sys.exit(1)
    else:
        print("✅ Context file is already up to date")

if __name__ == "__main__":
    main()
