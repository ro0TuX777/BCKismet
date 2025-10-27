#!/bin/bash

# ForgedKismet Launcher Script
# This script provides an easy way to launch ForgedKismet with different configurations

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FORGEDFATE_DIR="$SCRIPT_DIR/forgedfate"

# Function to open web browser
open_browser() {
    local url="$1"
    local browsers=(
        "xdg-open"
        "firefox"
        "google-chrome"
        "chromium"
        "chromium-browser"
        "opera"
        "vivaldi"
        "brave-browser"
    )

    for browser in "${browsers[@]}"; do
        if command -v "$browser" &> /dev/null; then
            echo "Opening web UI in browser: $browser"
            "$browser" "$url" &> /dev/null &
            return 0
        fi
    done

    echo "Warning: No suitable web browser found to open $url"
    echo "Please manually open your browser and navigate to: $url"
    return 1
}

echo "=== ForgedKismet Launcher ==="
echo "Enhanced Kismet Wireless Network Detector"
echo ""

# Check if Kismet is installed
if ! command -v kismet &> /dev/null; then
    echo "Error: Kismet is not installed or not in PATH"
    echo "Please install Kismet first"
    exit 1
fi

# Check if configuration files exist
MINIMAL_CONF="$FORGEDFATE_DIR/kismet_minimal.conf"
FULL_CONF="$FORGEDFATE_DIR/kismet_site.conf"

if [[ ! -f "$MINIMAL_CONF" ]]; then
    echo "Error: Minimal configuration file not found at $MINIMAL_CONF"
    exit 1
fi

if [[ ! -f "$FULL_CONF" ]]; then
    echo "Error: Full configuration file not found at $FULL_CONF"
    exit 1
fi

# Menu selection
echo "Select configuration:"
echo "1) Minimal Configuration (GPS + WiFi + Bluetooth)"
echo "2) Full Configuration (All devices including SDR)"
echo "3) Default Kismet (no custom config)"
echo ""
read -p "Enter your choice (1-3): " choice

case $choice in
    1)
        echo "Launching ForgedKismet with minimal configuration..."
        kismet -c "$MINIMAL_CONF" &
        KISMET_PID=$!
        ;;
    2)
        echo "Launching ForgedKismet with full configuration..."
        kismet -c "$FULL_CONF" &
        KISMET_PID=$!
        ;;
    3)
        echo "Launching Kismet with default configuration..."
        kismet &
        KISMET_PID=$!
        ;;
    *)
        echo "Invalid choice. Exiting."
        exit 1
        ;;
esac

# Wait a moment for Kismet to start up
echo "Waiting for Kismet to start up..."
sleep 3

# Open the web UI
echo "Opening Kismet Web UI..."
open_browser "http://localhost:2501"

# Keep the script running
echo "Kismet is running. Press Ctrl+C to stop."
wait $KISMET_PID
