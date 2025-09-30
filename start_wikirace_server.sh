#!/bin/bash

echo "========================================"
echo "    WikiRace Multiplayer Server"
echo "========================================"
echo ""
echo "Your server will be available at:"
echo "  Local: http://127.0.0.1:8001"
echo "  Network: http://wikirace.duckdns.org:8001"
echo "  Direct IP: http://71.237.25.28:8001"
echo ""
echo "External players can connect using:"
echo "  - wikirace.duckdns.org:8001 (recommended)"
echo "  - 71.237.25.28:8001 (direct IP)"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

cd server
python start_server.py
