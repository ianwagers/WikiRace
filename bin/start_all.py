#!/usr/bin/env python3
"""
WikiRace Development Launcher

This script checks if the multiplayer server is running, starts it if needed,
and then launches the WikiRace client application for development.
"""

import sys
import os
import time
import subprocess
import requests
import logging
from pathlib import Path
from threading import Thread

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_server_running(host="localhost", port=8001, timeout=2):  # Changed to port 8001
    """
    Check if the multiplayer server is already running
    
    Args:
        host: Server host (default: localhost)
        port: Server port (default: 8000)
        timeout: Request timeout in seconds
        
    Returns:
        bool: True if server is running, False otherwise
    """
    try:
        response = requests.get(f"http://{host}:{port}/health", timeout=timeout)
        return response.status_code == 200
    except (requests.exceptions.RequestException, requests.exceptions.ConnectionError):
        return False

def start_server_background():
    """
    Start the multiplayer server in a background process
    
    Returns:
        subprocess.Popen: The server process object
    """
    logger.info("Starting multiplayer server in background...")
    
    # Path to the server startup script
    server_script = project_root / "server" / "start_server.py"
    
    # Check if we're in a virtual environment
    venv_python = project_root / "venv" / "Scripts" / "python.exe"
    if venv_python.exists():
        python_executable = str(venv_python)
        logger.info("Using virtual environment Python")
    else:
        python_executable = sys.executable
        logger.info("Using system Python")
    
    # Start server as a background process
    process = subprocess.Popen(
        [python_executable, str(server_script)],
        cwd=project_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
    )
    
    return process

def wait_for_server_ready(host="localhost", port=8001, max_wait=30):  # Changed to port 8001
    """
    Wait for the server to be ready to accept connections
    
    Args:
        host: Server host
        port: Server port
        max_wait: Maximum time to wait in seconds
        
    Returns:
        bool: True if server is ready, False if timeout
    """
    logger.info("Waiting for server to be ready...")
    
    start_time = time.time()
    while time.time() - start_time < max_wait:
        if check_server_running(host, port):
            logger.info("Server is ready!")
            return True
        time.sleep(1)
    
    logger.error(f"Server did not start within {max_wait} seconds")
    return False

def start_client():
    """
    Start the WikiRace client application (two instances for multiplayer testing)
    """
    logger.info("Starting WikiRace client applications for multiplayer testing...")
    
    try:
        from PyQt6.QtWidgets import QApplication
        from src.app import MainApplication
        
        app = QApplication(sys.argv)
        
        # Create first client window
        mainWindow1 = MainApplication()
        mainWindow1.setWindowTitle("WikiRace - Player 1")
        mainWindow1.show()
        
        # Create second client window
        mainWindow2 = MainApplication()
        mainWindow2.setWindowTitle("WikiRace - Player 2")
        mainWindow2.show()
        
        logger.info("WikiRace clients started successfully!")
        logger.info("Server should be running at http://localhost:8001")  # Changed to port 8001
        logger.info("Two client windows opened for multiplayer testing!")
        logger.info("Use one window to host a game and the other to join it.")
        
        sys.exit(app.exec())
        
    except ImportError as e:
        logger.error(f"Failed to import required modules: {e}")
        logger.error("Make sure PyQt6 is installed and the virtual environment is activated")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to start client: {e}")
        sys.exit(1)

def cleanup_server(server_process):
    """
    Clean up server process on exit
    
    Args:
        server_process: The server process to terminate
    """
    if server_process and server_process.poll() is None:
        logger.info("Terminating server process...")
        try:
            server_process.terminate()
            server_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            logger.warning("Server process did not terminate gracefully, killing...")
            server_process.kill()

def main():
    """
    Main function that orchestrates server checking/starting and client launch
    """
    logger.info("WikiRace Development Launcher Starting...")
    
    # Check if server is already running
    if check_server_running():
        logger.info("Multiplayer server is already running!")
        server_process = None
    else:
        logger.info("Multiplayer server is not running, starting it...")
        
        # Start server in background
        server_process = start_server_background()
        
        # Wait for server to be ready
        if not wait_for_server_ready():
            logger.error("Failed to start multiplayer server")
            cleanup_server(server_process)
            sys.exit(1)
    
    try:
        # Start the client application
        start_client()
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        # Clean up server if we started it
        cleanup_server(server_process)

if __name__ == "__main__":
    main()
