# WikiRace Portable Deployment Guide

This guide explains how to create and deploy portable versions of WikiRace for cross-device multiplayer testing.

## Quick Start

### Option 1: Automated Build (Recommended)
1. **Windows**: Double-click `build_portable.bat`
2. **Linux/macOS**: Run `./build_portable.sh`

### Option 2: Manual Build
```bash
python build_portable.py
```

## What Gets Created

The build script creates a `build_portable/` directory containing:

```
build_portable/
├── bin/main.py                    # Main game executable
├── src/                          # Game source code
├── docs/                         # Documentation
├── server/                       # Multiplayer server
│   ├── start_server.py
│   ├── start_server.bat/sh       # Server startup scripts
│   ├── requirements.txt
│   └── ... (all server files)
├── install.bat/sh                # Dependency installer
├── README_PORTABLE.md            # Portable version instructions
└── ... (other project files)
```

## Deployment Steps

### Step 1: Build the Portable Version
Run the build script on your development machine:
```bash
python build_portable.py
```

### Step 2: Test Locally
1. Navigate to the `build_portable/` directory
2. Run the installer: `install.bat` (Windows) or `./install.sh` (Linux/macOS)
3. Test the game: `python bin/main.py`
4. Test the server: `python server/start_server.py`

### Step 3: Package for Distribution
Create a zip file of the `build_portable/` directory:
```bash
# Windows (PowerShell)
Compress-Archive -Path build_portable -DestinationPath WikiRace_Portable.zip

# Linux/macOS
zip -r WikiRace_Portable.zip build_portable/
```

### Step 4: Deploy to Target Devices

#### For Each Device:
1. **Extract** the zip file
2. **Install Python 3.13+** if not already installed
3. **Run the installer** (`install.bat` or `./install.sh`)
4. **Start the game** (`python bin/main.py`)

## Multiplayer Setup Instructions

### For the Host Device (Server):
1. Find your device's IP address:
   - **Windows**: Run `ipconfig` and look for "IPv4 Address"
   - **Linux/macOS**: Run `ifconfig` or `ip addr show`
2. Start the server: `python server/start_server.py`
3. Share your IP address with other players

### For Client Devices:
1. Start WikiRace: `python bin/main.py`
2. Go to **Multiplayer** → **Settings**
3. Enter the host's IP address (not localhost)
4. Set port to **8001**
5. Test connection and save
6. Create or join a room

## Network Configuration

### Firewall Settings
Make sure port **8001** is open on the host device:

#### Windows:
1. Open Windows Defender Firewall
2. Click "Allow an app through firewall"
3. Add Python.exe and allow both private and public networks
4. Or manually open port 8001 for inbound connections

#### Linux (ufw):
```bash
sudo ufw allow 8001
```

#### macOS:
1. System Preferences → Security & Privacy → Firewall
2. Click "Firewall Options"
3. Add Python and allow incoming connections

### Router Configuration (Optional)
For internet multiplayer, configure port forwarding:
1. Access your router's admin panel
2. Set up port forwarding for port 8001 to the host device
3. Use your public IP address for connections

## Troubleshooting

### Common Issues

#### "Connection Refused" Error
- ✅ Server is not running → Start the server first
- ✅ Wrong IP address → Check the host's IP address
- ✅ Firewall blocking → Open port 8001
- ✅ Wrong port → Use port 8001, not 8000

#### "Module Not Found" Error
- ✅ Dependencies not installed → Run the installer script
- ✅ Wrong Python version → Use Python 3.13+
- ✅ Virtual environment issues → Install globally

#### Game Won't Start
- ✅ PyQt6 not installed → Run `pip install PyQt6 PyQt6-WebEngine`
- ✅ Missing dependencies → Run the installer script
- ✅ Permission issues → Run as administrator (Windows)

### Network Testing

#### Test Server Connectivity
```bash
# From any device on the network
curl http://HOST_IP:8001/health

# Should return: {"status":"healthy"}
```

#### Test Socket.IO Connection
```bash
# Install socket.io client for testing
pip install python-socketio[client]

# Test connection
python -c "
import socketio
sio = socketio.Client()
try:
    sio.connect('http://HOST_IP:8001')
    print('✅ Connection successful!')
    sio.disconnect()
except Exception as e:
    print(f'❌ Connection failed: {e}')
"
```

## Advanced Configuration

### Custom Server Settings
Edit `server/config.py` to modify:
- Host binding (`0.0.0.0` for network access)
- Port number (default: 8001)
- CORS settings
- Rate limiting

### Client Configuration
Users can modify server settings in the game:
1. Go to Multiplayer → Settings
2. Configure server host, port, and reconnection settings
3. Settings are saved automatically

## Production Deployment

### For Public Servers
1. **Use HTTPS**: Set up SSL certificates
2. **Domain Name**: Use a proper domain instead of IP
3. **Load Balancing**: For multiple server instances
4. **Monitoring**: Set up server monitoring and logging
5. **Security**: Implement authentication and rate limiting

### Docker Deployment
The portable version includes Docker files:
```bash
cd server/
docker-compose up -d
```

## Support and Updates

### Getting Help
- Check the `docs/` folder for detailed documentation
- Review server logs in `wikirace_server.log`
- Test network connectivity using the troubleshooting steps

### Updating the Portable Version
1. Update the source code
2. Re-run the build script
3. Distribute the new `build_portable/` directory
4. Users can extract over their existing installation

## Security Considerations

### For Development/Testing
- Default configuration is suitable for local network testing
- CORS is set to allow all origins (`*`)
- No authentication is required

### For Production Use
- Implement proper authentication
- Restrict CORS to specific domains
- Use HTTPS with valid certificates
- Implement rate limiting and abuse prevention
- Regular security updates

---

**Note**: This portable version is designed for testing and development. For production deployment, consider additional security measures and proper server infrastructure.
