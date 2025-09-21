#!/usr/bin/env python3
"""
WikiRace Multiplayer Server Startup Script

Run this from the project root to start the multiplayer server.
"""

import sys
import logging
from pathlib import Path

# Add server directory to Python path
server_dir = Path(__file__).parent / "server"
sys.path.insert(0, str(server_dir))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('wikirace_server.log')
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Start the WikiRace multiplayer server"""
    try:
        logger.info("Starting WikiRace Multiplayer Server...")
        
        # Import and run the server
        import uvicorn
        from config import settings
        
        logger.info(f"Server will start on {settings.HOST}:{settings.PORT}")
        logger.info("Press Ctrl+C to stop the server")
        
        # Run the server using the module path
        uvicorn.run(
            "server.main:socket_app",
            host=settings.HOST,
            port=settings.PORT,
            reload=settings.DEBUG,
            log_level="info" if not settings.DEBUG else "debug"
        )
        
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
