#!/bin/bash

# ForgedKismet Desktop Wrapper Script
# This script finds an available terminal and launches ForgedKismet

# Configuration file to use (passed as argument)
CONFIG_FILE="$1"

if [[ -z "$CONFIG_FILE" ]]; then
    echo "Error: No configuration file specified"
    exit 1
fi

if [[ ! -f "$CONFIG_FILE" ]]; then
    echo "Error: Configuration file not found: $CONFIG_FILE"
    exit 1
fi

# Function to find available terminal
find_terminal() {
    local terminals=(
        "qterminal -e"
        "gnome-terminal --"
        "konsole -e"
        "xfce4-terminal -e"
        "lxterminal -e"
        "mate-terminal -e"
        "terminator -e"
        "x-terminal-emulator -e"
    )
    
    for term in "${terminals[@]}"; do
        local term_cmd=$(echo $term | cut -d' ' -f1)
        if command -v "$term_cmd" &> /dev/null; then
            echo "$term"
            return 0
        fi
    done
    
    return 1
}

# Find available terminal
TERMINAL=$(find_terminal)

if [[ -z "$TERMINAL" ]]; then
    echo "Error: No suitable terminal emulator found"
    echo "Please install one of: qterminal, gnome-terminal, konsole, xfce4-terminal"
    exit 1
fi

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

# Launch ForgedKismet in terminal
echo "Launching ForgedKismet with configuration: $CONFIG_FILE"
echo "Using terminal: $TERMINAL"

# Start Kismet in background
$TERMINAL /usr/bin/kismet --config-file="$CONFIG_FILE" &
KISMET_PID=$!

# Wait a moment for Kismet to start up
echo "Waiting for Kismet to start up..."
sleep 3

# Open the web UI
echo "Opening Kismet Web UI..."
open_browser "http://localhost:2501"

# Keep the script running so the desktop icon doesn't disappear immediately
wait $KISMET_PID
