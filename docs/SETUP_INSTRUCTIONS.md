# WikiRace Python 3.13 Setup Instructions

This guide will help you set up WikiRace with Python 3.13 and the latest dependencies.

## Prerequisites

- Python 3.13 or higher installed on your system
- Git (optional, for version control)

## Quick Setup (Windows)

1. **Run the setup script:**
   ```cmd
   setup.bat
   ```

2. **Activate the virtual environment:**
   ```cmd
   venv\Scripts\activate
   ```

3. **Run the application:**
   ```cmd
   python src/app.py
   ```

## Manual Setup

### 1. Create Virtual Environment

```bash
# Using Python 3.13
python3.13 -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 2. Install Dependencies

```bash
# Install the project and its dependencies
pip install -e .

# Install development dependencies (optional)
pip install -e .[dev]
```

### 3. Run the Application

```bash
# Method 1: Direct execution
python bin/main.py

# Method 2: Using the installed command
wikirace
```

### 4. Multiplayer Server Setup (Optional)

For multiplayer functionality, you'll need to run the server:

```bash
# Start the multiplayer server
python server/start_server.py

# Or run the server directly
python server/main.py
```

The server will start on `http://localhost:8000` by default.

## What's New in This Setup

### Updated Dependencies

#### Client Application
- **PyQt6** (instead of PyQt5) - Modern Qt framework with better Python 3.13 support
- **PyQt6-WebEngine** - For web content display
- **requests** 2.32.0+ - For HTTP requests to Wikipedia API
- **beautifulsoup4** 4.12.0+ - For HTML parsing
- **lxml** 5.0.0+ - Fast XML/HTML parser

#### Multiplayer Support (New!)
- **python-socketio[client]** 5.8.0+ - Real-time communication with server
- **websocket-client** 1.6.0+ - WebSocket support
- **python-dotenv** 1.0.0+ - Environment configuration

#### Server Dependencies
- **FastAPI** - Modern web framework for the multiplayer server
- **python-socketio** - Server-side Socket.IO implementation
- **pydantic** - Data validation and serialization
- **uvicorn** - ASGI server for FastAPI

### Python 3.13 Features

- Better performance
- Improved error messages
- Enhanced type checking
- New language features

## Troubleshooting

### Common Issues

1. **PyQt6 Installation Issues:**
   ```bash
   pip install --upgrade PyQt6 PyQt6-WebEngine
   ```

2. **Python 3.13 Not Found:**
   - Download from https://www.python.org/downloads/
   - Make sure to add Python to your PATH during installation

3. **Virtual Environment Issues:**
   ```bash
   # Remove old virtual environment
   rmdir /s venv  # Windows
   rm -rf venv    # macOS/Linux
   
   # Create new one
   python3.13 -m venv venv
   ```

### Development Tools

If you installed development dependencies, you have access to:

- **pytest** - For running tests
- **black** - For code formatting
- **flake8** - For code linting
- **mypy** - For type checking

```bash
# Format code
black src/

# Lint code
flake8 src/

# Type check
mypy src/
```

## Project Structure

```
WikiRace/
├── pyproject.toml          # Project configuration
├── setup_environment.py    # Setup script
├── setup.bat              # Windows setup script
├── bin/                   # Entry points
│   └── main.py           # Application launcher
├── src/                   # Client application source code
│   ├── app.py            # Main application
│   ├── gui/              # GUI components
│   ├── logic/            # Game logic
│   └── resources/        # Images and icons
├── server/                # Multiplayer server (NEW!)
│   ├── main.py           # FastAPI server
│   ├── start_server.py   # Server startup script
│   ├── models.py         # Data models
│   ├── room_manager.py   # Room management
│   ├── socket_handlers.py # Socket.IO events
│   └── config.py         # Server configuration
├── docs/                  # Documentation
│   ├── SETUP_INSTRUCTIONS.md
│   ├── MULTIPLAYER_SPEC.md
│   └── ...
└── venv/                 # Virtual environment (created during setup)
```

## Next Steps

1. **Run the application** to test the setup
2. **Explore the code** to understand the structure
3. **Make modifications** as needed
4. **Test thoroughly** before deploying

## Support

If you encounter any issues:

1. Check the troubleshooting section above
2. Ensure Python 3.13 is properly installed
3. Verify all dependencies are installed correctly
4. Check the console output for error messages

Happy coding! 🎮
