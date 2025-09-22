# WikiRace Multiplayer Server Deployment Guide

This guide provides comprehensive instructions for deploying the WikiRace Multiplayer Server in various environments.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Prerequisites](#prerequisites)
3. [Docker Deployment](#docker-deployment)
4. [Manual Installation](#manual-installation)
5. [Production Deployment](#production-deployment)
6. [Configuration](#configuration)
7. [Monitoring and Maintenance](#monitoring-and-maintenance)
8. [Troubleshooting](#troubleshooting)

## Quick Start

The fastest way to get the server running:

```bash
# 1. Clone/navigate to the server directory
cd server/

# 2. Make deployment script executable
chmod +x deploy.sh

# 3. Deploy with Docker
./deploy.sh deploy

# 4. Check status
./deploy.sh status
```

The server will be available at `http://localhost:8000`

## Prerequisites

### System Requirements
- **OS**: Linux (Ubuntu 20.04+ recommended), macOS, or Windows with WSL2
- **RAM**: Minimum 1GB, 2GB+ recommended for production
- **CPU**: 1 core minimum, 2+ cores recommended
- **Storage**: 500MB minimum, 2GB+ for logs and data
- **Network**: Port 8000 (configurable) must be accessible

### Software Dependencies
- **Docker**: 20.10+ 
- **Docker Compose**: 2.0+ (or legacy 1.29+)
- **Python**: 3.11+ (for manual installation)
- **Git**: For cloning the repository

### Installing Docker

#### Ubuntu/Debian
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
# Log out and back in
```

#### macOS
```bash
brew install --cask docker
# Or download from https://docker.com/products/docker-desktop
```

#### Windows
Download Docker Desktop from https://docker.com/products/docker-desktop

## Docker Deployment

### Basic Deployment

1. **Prepare the environment:**
```bash
cd server/
cp env.template .env
# Edit .env file as needed
```

2. **Deploy using the script:**
```bash
chmod +x deploy.sh
./deploy.sh deploy
```

3. **Verify deployment:**
```bash
curl http://localhost:8000/health
```

### Docker Compose (Manual)

If you prefer manual control:

```bash
# Build and start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Configuration Options

The deployment uses environment variables from `.env`:

```bash
# Server settings
WIKIRACE_PORT=8000
WIKIRACE_HOST=0.0.0.0
WIKIRACE_DEBUG=false

# Redis (optional)
REDIS_URL=redis://redis:6379

# Security
MAX_ROOMS=100
MAX_PLAYERS_PER_ROOM=10
```

## Manual Installation

For development or custom deployments:

### 1. Install Python Dependencies
```bash
cd server/
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp env.template .env
# Edit .env file
```

### 3. Start the Server
```bash
python start_server.py
```

### 4. Optional: Install Redis
```bash
# Ubuntu/Debian
sudo apt-get install redis-server

# macOS
brew install redis

# Start Redis
redis-server
```

## Production Deployment

### Security Considerations

1. **Use HTTPS**: Configure SSL certificates
2. **Firewall**: Only expose necessary ports
3. **Updates**: Keep Docker images and system updated
4. **Monitoring**: Set up health checks and alerts

### SSL/TLS Setup

1. **Obtain SSL certificates:**
```bash
# Using Let's Encrypt (certbot)
sudo apt-get install certbot
sudo certbot certonly --standalone -d your-domain.com
```

2. **Copy certificates:**
```bash
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem server/ssl/wikirace.crt
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem server/ssl/wikirace.key
```

3. **Enable Nginx proxy:**
```bash
docker-compose --profile nginx up -d
```

### Reverse Proxy (Nginx)

The included `nginx.conf` provides:
- SSL termination
- Rate limiting
- Gzip compression
- Security headers
- WebSocket support

### Cloud Deployment

#### AWS EC2
```bash
# Launch Ubuntu 20.04 instance
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Clone and deploy
git clone <your-repo>
cd WikiRace/server
./deploy.sh deploy
```

#### DigitalOcean Droplet
```bash
# Create Ubuntu droplet
# Follow AWS EC2 instructions above
```

#### Google Cloud Platform
```bash
# Create Compute Engine instance
# Install Docker and deploy as above
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `WIKIRACE_ENV` | `production` | Environment mode |
| `WIKIRACE_HOST` | `0.0.0.0` | Server bind address |
| `WIKIRACE_PORT` | `8000` | Server port |
| `WIKIRACE_DEBUG` | `false` | Enable debug mode |
| `REDIS_URL` | `redis://redis:6379` | Redis connection URL |
| `MAX_ROOMS` | `100` | Maximum concurrent rooms |
| `MAX_PLAYERS_PER_ROOM` | `10` | Players per room limit |
| `LOG_LEVEL` | `INFO` | Logging level |
| `CORS_ORIGINS` | `["*"]` | Allowed CORS origins |

### Performance Tuning

#### For High Load
```bash
# In .env file
MAX_ROOMS=500
MAX_PLAYERS_PER_ROOM=20

# Docker resource limits
docker-compose up -d --scale wikirace-server=3
```

#### Memory Optimization
```bash
# Limit container memory
docker run -m 512m wikirace-multiplayer
```

## Monitoring and Maintenance

### Health Checks

The server provides a health endpoint:
```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "timestamp": "2025-01-01T12:00:00Z",
  "uptime": "2h 30m 15s"
}
```

### Logging

#### View Logs
```bash
# All services
./deploy.sh logs

# Specific service
docker-compose logs wikirace-server

# Follow logs
docker-compose logs -f
```

#### Log Files
- **Container logs**: `docker-compose logs`
- **Application logs**: `./logs/wikirace_server.log`
- **Nginx logs**: Inside nginx container

### Backup and Recovery

#### Backup Redis Data
```bash
docker exec wikirace-redis redis-cli BGSAVE
docker cp wikirace-redis:/data/dump.rdb ./backup/
```

#### Restore Redis Data
```bash
docker cp ./backup/dump.rdb wikirace-redis:/data/
docker-compose restart redis
```

### Updates

#### Update Server Code
```bash
git pull
./deploy.sh restart
```

#### Update Docker Images
```bash
docker-compose pull
docker-compose up -d
```

## Troubleshooting

### Common Issues

#### Server Won't Start
```bash
# Check logs
./deploy.sh logs

# Common causes:
# - Port already in use
# - Invalid configuration
# - Docker not running
```

#### Connection Refused
```bash
# Check if server is running
./deploy.sh status

# Check firewall
sudo ufw status

# Test connectivity
curl -v http://localhost:8000/health
```

#### High Memory Usage
```bash
# Monitor container resources
docker stats

# Restart services
./deploy.sh restart
```

#### WebSocket Connection Issues
```bash
# Check nginx configuration
docker-compose logs nginx

# Verify proxy settings
curl -H "Upgrade: websocket" http://localhost:8000/socket.io/
```

### Performance Issues

#### High CPU Usage
- Increase container CPU limits
- Scale horizontally with multiple containers
- Check for infinite loops in logs

#### Memory Leaks
- Monitor memory usage over time
- Restart containers periodically
- Review application logs for errors

#### Network Latency
- Use a CDN for static assets
- Deploy closer to users
- Optimize database queries

### Debug Mode

Enable debug mode for development:
```bash
# In .env
WIKIRACE_DEBUG=true
LOG_LEVEL=DEBUG

# Restart
./deploy.sh restart
```

### Getting Help

1. **Check logs**: Always start with application logs
2. **Health endpoint**: Verify server status
3. **Network connectivity**: Test from client machine
4. **Resource usage**: Monitor CPU, memory, disk
5. **Documentation**: Review configuration options

## Deployment Checklist

### Pre-deployment
- [ ] System requirements met
- [ ] Docker installed and running
- [ ] Firewall configured
- [ ] SSL certificates ready (production)
- [ ] Environment variables configured

### Deployment
- [ ] Code pulled/updated
- [ ] `.env` file configured
- [ ] Services built and started
- [ ] Health check passes
- [ ] Client connectivity tested

### Post-deployment
- [ ] Monitoring configured
- [ ] Backup strategy implemented
- [ ] Log rotation configured
- [ ] Security hardening applied
- [ ] Documentation updated

---

For additional support or questions, please refer to the main project documentation or create an issue in the project repository.
