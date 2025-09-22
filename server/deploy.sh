#!/bin/bash

# WikiRace Multiplayer Server Deployment Script
# Automates the deployment process for the WikiRace multiplayer server

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DEFAULT_PORT=8000
DEFAULT_ENV=production
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Functions
print_header() {
    echo -e "${BLUE}"
    echo "=========================================="
    echo "   WikiRace Multiplayer Server Deploy"
    echo "   Version 1.6.0"
    echo "=========================================="
    echo -e "${NC}"
}

print_step() {
    echo -e "${GREEN}[STEP]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_dependencies() {
    print_step "Checking dependencies..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_info "All dependencies are available."
}

setup_environment() {
    print_step "Setting up environment..."
    
    # Create .env file if it doesn't exist
    if [ ! -f "$SCRIPT_DIR/.env" ]; then
        print_info "Creating .env file from template..."
        cp "$SCRIPT_DIR/env.template" "$SCRIPT_DIR/.env"
        print_warning "Please edit .env file to configure your deployment."
    else
        print_info ".env file already exists."
    fi
    
    # Create logs directory
    mkdir -p "$SCRIPT_DIR/logs"
    
    # Create SSL directory (for nginx)
    mkdir -p "$SCRIPT_DIR/ssl"
}

build_and_deploy() {
    print_step "Building and deploying server..."
    
    cd "$SCRIPT_DIR"
    
    # Build the Docker image
    print_info "Building Docker image..."
    docker build -t wikirace-multiplayer:latest .
    
    # Start services
    print_info "Starting services with Docker Compose..."
    if command -v docker-compose &> /dev/null; then
        docker-compose up -d
    else
        docker compose up -d
    fi
    
    # Wait for services to be ready
    print_info "Waiting for services to start..."
    sleep 10
    
    # Check if server is running
    if curl -f http://localhost:${WIKIRACE_PORT:-8000}/health &> /dev/null; then
        print_info "✅ Server is running and healthy!"
    else
        print_warning "Server may not be ready yet. Check logs with: docker-compose logs"
    fi
}

show_status() {
    print_step "Service Status:"
    
    cd "$SCRIPT_DIR"
    if command -v docker-compose &> /dev/null; then
        docker-compose ps
    else
        docker compose ps
    fi
}

show_logs() {
    print_step "Recent logs:"
    
    cd "$SCRIPT_DIR"
    if command -v docker-compose &> /dev/null; then
        docker-compose logs --tail=50
    else
        docker compose logs --tail=50
    fi
}

stop_services() {
    print_step "Stopping services..."
    
    cd "$SCRIPT_DIR"
    if command -v docker-compose &> /dev/null; then
        docker-compose down
    else
        docker compose down
    fi
    
    print_info "Services stopped."
}

cleanup() {
    print_step "Cleaning up..."
    
    cd "$SCRIPT_DIR"
    
    # Stop and remove containers
    if command -v docker-compose &> /dev/null; then
        docker-compose down -v --remove-orphans
    else
        docker compose down -v --remove-orphans
    fi
    
    # Remove images
    docker rmi wikirace-multiplayer:latest 2>/dev/null || true
    
    print_info "Cleanup completed."
}

show_help() {
    echo "WikiRace Multiplayer Server Deployment Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  deploy    Build and deploy the server (default)"
    echo "  status    Show service status"
    echo "  logs      Show recent logs"
    echo "  stop      Stop all services"
    echo "  restart   Restart all services"
    echo "  cleanup   Stop services and remove containers/images"
    echo "  help      Show this help message"
    echo ""
    echo "Environment Variables:"
    echo "  WIKIRACE_PORT    Server port (default: 8000)"
    echo "  WIKIRACE_ENV     Environment (default: production)"
    echo ""
    echo "Examples:"
    echo "  $0 deploy"
    echo "  $0 status"
    echo "  WIKIRACE_PORT=9000 $0 deploy"
}

# Main execution
main() {
    print_header
    
    case "${1:-deploy}" in
        "deploy")
            check_dependencies
            setup_environment
            build_and_deploy
            show_status
            ;;
        "status")
            show_status
            ;;
        "logs")
            show_logs
            ;;
        "stop")
            stop_services
            ;;
        "restart")
            stop_services
            sleep 2
            build_and_deploy
            show_status
            ;;
        "cleanup")
            cleanup
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            print_error "Unknown command: $1"
            show_help
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
