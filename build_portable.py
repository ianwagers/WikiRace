#!/usr/bin/env python3
"""
WikiRace Portable Build Script

Creates portable versions of WikiRace for cross-platform distribution.
Supports both client-only and full (client + server) builds.
"""

import os
import sys
import shutil
import subprocess
import platform
from pathlib import Path
import argparse


class PortableBuilder:
    """Builds portable versions of WikiRace"""
    
    def __init__(self, build_dir="build_portable"):
        self.build_dir = Path(build_dir)
        self.project_root = Path(__file__).parent
        self.system = platform.system().lower()
        
    def clean_build_dir(self):
        """Clean the build directory"""
        if self.build_dir.exists():
            print(f"🧹 Cleaning build directory: {self.build_dir}")
            shutil.rmtree(self.build_dir)
        self.build_dir.mkdir(exist_ok=True)
    
    def create_client_build(self):
        """Create a portable client build using PyInstaller"""
        print("🔨 Building portable client...")
        
        # Create PyInstaller spec file
        spec_content = f"""
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['bin/main.py'],
    pathex=['{self.project_root}'],
    binaries=[],
    datas=[
        ('src/resources', 'src/resources'),
        ('README.md', '.'),
        ('docs', 'docs'),
    ],
    hiddenimports=[
        'PyQt6.QtCore',
        'PyQt6.QtWidgets', 
        'PyQt6.QtWebEngineWidgets',
        'PyQt6.QtWebEngineCore',
        'requests',
        'beautifulsoup4',
        'lxml',
        'socketio',
        'websocket',
        'dotenv',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='WikiRace',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='src/resources/icons/wikirace.ico' if Path('src/resources/icons/wikirace.ico').exists() else None,
)
"""
        
        spec_file = self.build_dir / "wikirace.spec"
        with open(spec_file, 'w') as f:
            f.write(spec_content)
        
        # Build with PyInstaller
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--clean",
            "--noconfirm", 
            str(spec_file)
        ]
        
        try:
            subprocess.run(cmd, check=True, cwd=self.build_dir)
            print("✅ Client build completed successfully!")
        except subprocess.CalledProcessError as e:
            print(f"❌ Client build failed: {e}")
            return False
        
        return True
    
    def create_server_build(self):
        """Create a portable server build"""
        print("🔨 Building portable server...")
        
        server_build_dir = self.build_dir / "server"
        server_build_dir.mkdir(exist_ok=True)
        
        # Copy server files
        server_files = [
            "main.py",
            "start_server.py", 
            "config.py",
            "models.py",
            "room_manager.py",
            "socket_handlers.py",
            "api_routes.py",
            "game_logic.py",
            "requirements.txt",
            "Dockerfile",
            "docker-compose.yml",
            "deploy.sh",
            "nginx.conf",
            "DEPLOYMENT.md"
        ]
        
        for file in server_files:
            src = self.project_root / "server" / file
            if src.exists():
                shutil.copy2(src, server_build_dir / file)
                print(f"📁 Copied {file}")
        
        # Create server requirements
        server_requirements = [
            "fastapi>=0.104.0",
            "uvicorn[standard]>=0.24.0",
            "python-socketio>=5.8.0",
            "pydantic>=2.0.0",
            "pydantic-settings>=2.0.0",
            "python-multipart>=0.0.6",
            "redis>=5.0.0",
            "requests>=2.32.0",
        ]
        
        with open(server_build_dir / "requirements.txt", 'w') as f:
            f.write("\\n".join(server_requirements))
        
        # Create server startup script
        if self.system == "windows":
            startup_script = """@echo off
echo Starting WikiRace Multiplayer Server...
echo.
echo Server will be accessible at:
echo   Local: http://localhost:8001
echo   Network: http://YOUR_IP:8001
echo.
echo Press Ctrl+C to stop the server
echo.
python start_server.py
pause
"""
            with open(server_build_dir / "start_server.bat", 'w') as f:
                f.write(startup_script)
        else:
            startup_script = """#!/bin/bash
echo "Starting WikiRace Multiplayer Server..."
echo ""
echo "Server will be accessible at:"
echo "  Local: http://localhost:8001"
echo "  Network: http://YOUR_IP:8001"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""
python3 start_server.py
"""
            with open(server_build_dir / "start_server.sh", 'w') as f:
                f.write(startup_script)
            os.chmod(server_build_dir / "start_server.sh", 0o755)
        
        print("✅ Server build completed successfully!")
        return True
    
    def create_installer_script(self):
        """Create installation script for the portable version"""
        print("📝 Creating installer script...")
        
        if self.system == "windows":
            installer_content = """@echo off
echo ========================================
echo   WikiRace Portable Installation
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.13+ from https://python.org
    echo.
    pause
    exit /b 1
)

echo Python found. Installing dependencies...
echo.

REM Install client dependencies
echo Installing client dependencies...
pip install PyQt6 PyQt6-WebEngine requests beautifulsoup4 lxml python-socketio[client] websocket-client python-dotenv

REM Install server dependencies (optional)
echo.
set /p install_server="Install server dependencies? (y/n): "
if /i "%install_server%"=="y" (
    echo Installing server dependencies...
    cd server
    pip install -r requirements.txt
    cd ..
)

echo.
echo ========================================
echo   Installation Complete!
echo ========================================
echo.
echo To run WikiRace:
echo   1. Double-click: bin\\main.py
echo   2. Or run: python bin\\main.py
echo.
echo To run the server (optional):
echo   1. Double-click: server\\start_server.bat
echo   2. Or run: python server\\start_server.py
echo.
echo For multiplayer, make sure the server is running
echo on one device and configure the client to connect
echo to the server's IP address.
echo.
pause
"""
            installer_file = self.build_dir / "install.bat"
        else:
            installer_content = """#!/bin/bash
echo "========================================"
echo "  WikiRace Portable Installation"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.13+ from your package manager or https://python.org"
    echo ""
    exit 1
fi

echo "Python found. Installing dependencies..."
echo ""

# Install client dependencies
echo "Installing client dependencies..."
pip3 install PyQt6 PyQt6-WebEngine requests beautifulsoup4 lxml python-socketio[client] websocket-client python-dotenv

# Install server dependencies (optional)
echo ""
read -p "Install server dependencies? (y/n): " install_server
if [[ $install_server == "y" || $install_server == "Y" ]]; then
    echo "Installing server dependencies..."
    cd server
    pip3 install -r requirements.txt
    cd ..
fi

echo ""
echo "========================================"
echo "  Installation Complete!"
echo "========================================"
echo ""
echo "To run WikiRace:"
echo "  1. Run: python3 bin/main.py"
echo "  2. Or make executable: chmod +x bin/main.py && ./bin/main.py"
echo ""
echo "To run the server (optional):"
echo "  1. Run: python3 server/start_server.py"
echo "  2. Or make executable: chmod +x server/start_server.sh && ./server/start_server.sh"
echo ""
echo "For multiplayer, make sure the server is running"
echo "on one device and configure the client to connect"
echo "to the server's IP address."
echo ""
"""
            installer_file = self.build_dir / "install.sh"
            os.chmod(installer_file, 0o755)
        
        with open(installer_file, 'w') as f:
            f.write(installer_content)
        
        print(f"✅ Installer script created: {installer_file}")
    
    def create_readme(self):
        """Create README for portable version"""
        readme_content = """# WikiRace Portable Version

This is a portable version of WikiRace that can run on any device with Python 3.13+ installed.

## Quick Start

1. **Install Dependencies**: Run the installer script
   - Windows: Double-click `install.bat`
   - Linux/macOS: Run `./install.sh`

2. **Start the Game**: Run `python bin/main.py` (or double-click on Windows)

## Multiplayer Setup

### Option 1: Local Multiplayer (Same Network)
1. On one device, start the server: `python server/start_server.py`
2. On other devices, configure the client to connect to the server's IP address
3. Create/join rooms and play together!

### Option 2: Internet Multiplayer
1. Set up the server on a cloud provider or VPS
2. Configure firewall to allow port 8001
3. All players connect to the server's public IP

## Server Configuration

The server will run on `0.0.0.0:8001` by default, making it accessible from other devices on the same network.

### Finding Your Server IP
- **Windows**: Run `ipconfig` and look for IPv4 Address
- **Linux/macOS**: Run `ifconfig` or `ip addr show`

### Client Configuration
1. Open WikiRace
2. Go to Multiplayer → Settings
3. Enter the server's IP address (not localhost)
4. Set port to 8001
5. Test connection and save

## Troubleshooting

### Connection Issues
- Make sure the server is running and accessible
- Check firewall settings (port 8001 should be open)
- Verify IP address and port in client settings

### Performance Issues
- Close other applications to free up memory
- Use a wired network connection for better stability
- Ensure all devices are on the same network for local multiplayer

## Files Included

- `bin/main.py` - Main game executable
- `server/` - Multiplayer server files
- `docs/` - Documentation
- `src/` - Game source code
- `install.bat/install.sh` - Dependency installer

## Support

For issues or questions, please check the documentation in the `docs/` folder or visit the project repository.
"""
        
        readme_file = self.build_dir / "README_PORTABLE.md"
        with open(readme_file, 'w') as f:
            f.write(readme_content)
        
        print(f"✅ README created: {readme_file}")
    
    def build(self, include_server=True):
        """Build the complete portable version"""
        print("🚀 Starting WikiRace Portable Build...")
        print(f"System: {self.system}")
        print(f"Build directory: {self.build_dir}")
        
        self.clean_build_dir()
        
        # Copy main project files
        print("📁 Copying project files...")
        files_to_copy = [
            "bin/",
            "src/", 
            "docs/",
            "README.md",
            "pyproject.toml",
            "install_client.bat",
            "install_client.sh"
        ]
        
        for item in files_to_copy:
            src = self.project_root / item
            if src.exists():
                if src.is_dir():
                    shutil.copytree(src, self.build_dir / item)
                else:
                    shutil.copy2(src, self.build_dir / item)
                print(f"📁 Copied {item}")
        
        # Create installer script
        self.create_installer_script()
        
        # Create README
        self.create_readme()
        
        # Build server if requested
        if include_server:
            self.create_server_build()
        
        print(f"\\n🎉 Portable build completed!")
        print(f"📦 Build directory: {self.build_dir.absolute()}")
        print(f"📁 Size: {self._get_dir_size(self.build_dir):.1f} MB")
        
        print("\\n📋 Next Steps:")
        print("1. Test the build by running the installer")
        print("2. Verify the game starts correctly")
        print("3. Test multiplayer functionality")
        print("4. Package for distribution (zip, etc.)")
    
    def _get_dir_size(self, path):
        """Get directory size in MB"""
        total = 0
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                if os.path.exists(filepath):
                    total += os.path.getsize(filepath)
        return total / (1024 * 1024)  # Convert to MB


def main():
    parser = argparse.ArgumentParser(description="Build portable WikiRace version")
    parser.add_argument("--no-server", action="store_true", 
                       help="Build client only (exclude server)")
    parser.add_argument("--build-dir", default="build_portable",
                       help="Build directory (default: build_portable)")
    
    args = parser.parse_args()
    
    builder = PortableBuilder(args.build_dir)
    builder.build(include_server=not args.no_server)


if __name__ == "__main__":
    main()
