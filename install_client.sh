#!/bin/bash

# WikiRace Multiplayer Client Installation Script
# Automates the setup process for the WikiRace client on Linux/macOS

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo -e "${BLUE}"
    echo "=========================================="
    echo "   WikiRace Multiplayer Client Setup"
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

check_python() {
    print_step "Checking Python installation..."
    
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed."
        echo "Please install Python 3.11+ from your package manager:"
        echo "  Ubuntu/Debian: sudo apt-get install python3 python3-venv python3-pip"
        echo "  macOS: brew install python3"
        echo "  Or download from: https://python.org"
        exit 1
    fi
    
    # Check Python version
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    print_info "Found Python version: $PYTHON_VERSION"
    
    # Check if version is 3.11+
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)
    
    if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 11 ]); then
        print_warning "Python 3.11+ is recommended for best compatibility."
        print_warning "Current version: $PYTHON_VERSION"
    fi
}

check_directory() {
    print_step "Checking project directory..."
    
    if [ ! -f "src/app.py" ]; then
        print_error "Not in WikiRace project directory."
        print_error "Please run this script from the WikiRace root directory."
        exit 1
    fi
    
    print_info "Project directory verified."
}

setup_virtual_environment() {
    print_step "Setting up virtual environment..."
    
    if [ -d "venv" ]; then
        print_warning "Virtual environment already exists."
    else
        print_info "Creating virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    print_info "Activating virtual environment..."
    source venv/bin/activate
    
    # Upgrade pip
    print_info "Upgrading pip..."
    pip install --upgrade pip
}

install_system_dependencies() {
    print_step "Checking system dependencies..."
    
    # Detect OS
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        if command -v apt-get &> /dev/null; then
            # Ubuntu/Debian
            print_info "Detected Ubuntu/Debian system"
            print_info "Installing system dependencies..."
            
            # Check if we need to install Qt dependencies
            if ! dpkg -l | grep -q libqt6; then
                print_info "Installing Qt6 system libraries..."
                sudo apt-get update
                sudo apt-get install -y \
                    python3-venv \
                    python3-pip \
                    python3-dev \
                    libgl1-mesa-glx \
                    libegl1-mesa \
                    libxrandr2 \
                    libxss1 \
                    libxcursor1 \
                    libxcomposite1 \
                    libasound2 \
                    libxi6 \
                    libxtst6
            fi
        elif command -v yum &> /dev/null; then
            # RHEL/CentOS/Fedora
            print_info "Detected RHEL/CentOS/Fedora system"
            print_info "Installing system dependencies..."
            sudo yum install -y python3-venv python3-pip python3-devel
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        print_info "Detected macOS system"
        if ! command -v brew &> /dev/null; then
            print_warning "Homebrew not found. Installing Homebrew..."
            /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        fi
        
        # Install Python if needed
        if ! brew list python@3.11 &> /dev/null; then
            print_info "Installing Python 3.11 via Homebrew..."
            brew install python@3.11
        fi
    fi
}

install_python_dependencies() {
    print_step "Installing Python dependencies..."
    
    # Make sure we're in the virtual environment
    source venv/bin/activate
    
    if [ -f "requirements.txt" ]; then
        print_info "Installing from requirements.txt..."
        pip install -r requirements.txt
    else
        print_info "Installing core dependencies manually..."
        pip install \
            PyQt6>=6.7.0 \
            PyQt6-WebEngine>=6.7.0 \
            requests>=2.32.0 \
            beautifulsoup4>=4.12.0 \
            "python-socketio[client]>=5.8.0" \
            websocket-client>=1.6.0
    fi
}

test_installation() {
    print_step "Testing installation..."
    
    source venv/bin/activate
    
    # Test Python imports
    python3 -c "
import sys
print(f'Python version: {sys.version}')

try:
    import PyQt6
    print('✓ PyQt6 imported successfully')
except ImportError as e:
    print(f'✗ PyQt6 import failed: {e}')
    sys.exit(1)

try:
    import requests
    print('✓ requests imported successfully')
except ImportError as e:
    print(f'✗ requests import failed: {e}')
    sys.exit(1)

try:
    import socketio
    print('✓ socketio imported successfully')
except ImportError as e:
    print(f'✗ socketio import failed: {e}')
    sys.exit(1)

print('All core dependencies imported successfully!')
"
    
    if [ $? -eq 0 ]; then
        print_info "✅ Installation test passed!"
    else
        print_error "❌ Installation test failed!"
        exit 1
    fi
}

create_shortcuts() {
    print_step "Creating shortcuts..."
    
    # Create a launch script
    cat > run_wikirace.sh << 'EOF'
#!/bin/bash
# WikiRace Launcher Script

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Activate virtual environment
source venv/bin/activate

# Run the application
python3 bin/main.py
EOF
    
    chmod +x run_wikirace.sh
    print_info "Created run_wikirace.sh launcher script"
    
    # Create desktop entry for Linux
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        DESKTOP_FILE="$HOME/.local/share/applications/wikirace-multiplayer.desktop"
        mkdir -p "$(dirname "$DESKTOP_FILE")"
        
        cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=WikiRace Multiplayer
Comment=Wikipedia navigation racing game
Exec=$(pwd)/run_wikirace.sh
Icon=applications-games
Terminal=false
Categories=Game;
EOF
        
        print_info "Created desktop entry: $DESKTOP_FILE"
    fi
}

show_completion_message() {
    echo
    echo -e "${GREEN}=========================================${NC}"
    echo -e "${GREEN}   Installation completed successfully!${NC}"
    echo -e "${GREEN}=========================================${NC}"
    echo
    echo "To start WikiRace Multiplayer:"
    echo "  1. Run: ./run_wikirace.sh, or"
    echo "  2. Run: source venv/bin/activate && python3 bin/main.py"
    echo
    echo "For multiplayer functionality:"
    echo "  1. Start the server (see server/DEPLOYMENT.md)"
    echo "  2. Configure server settings in the client"
    echo "  3. Create or join a multiplayer room"
    echo
}

# Main installation process
main() {
    print_header
    
    check_python
    check_directory
    install_system_dependencies
    setup_virtual_environment
    install_python_dependencies
    test_installation
    create_shortcuts
    show_completion_message
    
    # Ask if user wants to start the application
    echo -n "Start WikiRace now? (y/n): "
    read -r START_NOW
    
    if [[ "$START_NOW" =~ ^[Yy]$ ]]; then
        print_info "Starting WikiRace..."
        source venv/bin/activate
        python3 bin/main.py
    fi
    
    echo
    echo "Installation complete. Enjoy playing WikiRace!"
}

# Run main function
main "$@"
