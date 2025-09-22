#!/bin/bash

echo "========================================"
echo "  WikiRace Portable Build Script"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.13+ from your package manager or https://python.org"
    echo ""
    exit 1
fi

echo "Python found. Building portable version..."
echo ""

# Make the build script executable
chmod +x build_portable.py

# Run the build script
python3 build_portable.py

echo ""
echo "Build completed! Check the build_portable directory."
echo ""
