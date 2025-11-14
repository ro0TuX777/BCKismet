#!/bin/bash

# ForgedKismet Command Line Launcher
# Enhanced Kismet with GPS and Elasticsearch export capabilities

# Set the working directory to the script location
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "Starting ForgedKismet..."
echo "Working directory: $SCRIPT_DIR"

# Function to clean up existing Kismet processes
cleanup_kismet() {
    echo "Cleaning up existing Kismet processes..."
    if [[ $EUID -eq 0 ]]; then
        pkill -f kismet 2>/dev/null || true
        killall kismet 2>/dev/null || true
    else
        pkill -f kismet 2>/dev/null || true
        echo "Note: Some root Kismet processes may still be running. Use 'sudo pkill -f kismet' to clean them up."
    fi
    sleep 2
}

# Clean up any existing processes first
cleanup_kismet

# Check if running as root (required for WiFi capture)
if [[ $EUID -eq 0 ]]; then
    echo "Running as root - Full WiFi capture enabled"
    echo "Available interfaces for capture:"
    echo "  WiFi: wlx8c902da2e062, wlx9cefd5f62bbe, wlp0s20f3"
    echo "  Bluetooth: hci0"
    echo "  GPS: Connected via GPSD"
    KISMET_CMD="/usr/bin/kismet --config-file=./forgedfate/kismet_working.conf --no-ncurses"
else
    echo "Running as user - Limited functionality"
    echo "Available features:"
    echo "  ✓ Web interface (http://localhost:2502)"
    echo "  ✓ GPS tracking (via GPSD)"
    echo "  ✓ Manual source addition via web UI"
    echo "  ✗ WiFi capture (requires root privileges)"
    echo ""
    echo "For full WiFi capture capabilities, run:"
    echo "  sudo $0"
    echo ""
    KISMET_CMD="/usr/bin/kismet --config-file=./forgedfate/kismet_minimal.conf --no-ncurses"
fi

# Start Kismet
echo "Executing: $KISMET_CMD"
echo "Web interface will be available at: http://localhost:2502"
echo ""
exec $KISMET_CMD
