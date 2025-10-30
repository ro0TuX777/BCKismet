#!/bin/bash

# ForgedKismet Desktop Wrapper Script
# This script finds an available terminal and launches ForgedKismet

# Set up environment for desktop execution
export PATH="/usr/local/bin:/usr/bin:/bin:/usr/local/sbin:/usr/sbin:/sbin"

# Configuration file to use (passed as argument)
CONFIG_FILE="$1"

# Log file for debugging desktop execution
LOG_FILE="/tmp/forgedkismet-wrapper.log"

# Function to log messages
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S'): $1" >> "$LOG_FILE"
}

# Function to check if Kismet web server is ready
wait_for_kismet() {
    local max_attempts=45  # Increased from 30 to allow more time for sudo
    local attempt=1

    echo "Waiting for Kismet to start up..."

    while [ $attempt -le $max_attempts ]; do
        log_message "Checking Kismet web server (attempt $attempt/$max_attempts)..."

        if curl -s --connect-timeout 2 http://localhost:2501 >/dev/null 2>&1; then
            log_message "Kismet web server is ready!"
            echo ""
            echo "Kismet web server is ready!"
            return 0
        fi

        echo -n "."
        sleep 2
        attempt=$((attempt + 1))
    done

    log_message "Warning: Kismet web server not responding after $max_attempts attempts"
    echo ""
    echo "Warning: Kismet web server not responding. You may need to wait longer or check the terminal."
    return 1
}

log_message "Starting ForgedKismet wrapper with config: $CONFIG_FILE"

if [[ -z "$CONFIG_FILE" ]]; then
    log_message "Error: No configuration file specified"
    echo "Error: No configuration file specified"
    exit 1
fi

if [[ ! -f "$CONFIG_FILE" ]]; then
    log_message "Error: Configuration file not found: $CONFIG_FILE"
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

    log_message "Searching for available terminals..."

    for term in "${terminals[@]}"; do
        local term_cmd=$(echo $term | cut -d' ' -f1)
        log_message "Checking for terminal: $term_cmd"
        if command -v "$term_cmd" &> /dev/null; then
            log_message "Found terminal: $term"
            echo "$term"
            return 0
        fi
    done

    log_message "No suitable terminal found"
    return 1
}

# Find available terminal
TERMINAL=$(find_terminal)

if [[ -z "$TERMINAL" ]]; then
    log_message "Error: No suitable terminal emulator found"
    echo "Error: No suitable terminal emulator found"
    echo "Please install one of: qterminal, gnome-terminal, konsole, xfce4-terminal"

    # Try to show error in a GUI dialog if available
    if command -v zenity &> /dev/null; then
        zenity --error --text="No suitable terminal emulator found.\nPlease install one of: qterminal, gnome-terminal, konsole, xfce4-terminal"
    elif command -v kdialog &> /dev/null; then
        kdialog --error "No suitable terminal emulator found.\nPlease install one of: qterminal, gnome-terminal, konsole, xfce4-terminal"
    fi

    exit 1
fi

log_message "Selected terminal: $TERMINAL"

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

    log_message "Attempting to open browser for URL: $url"

    for browser in "${browsers[@]}"; do
        if command -v "$browser" &> /dev/null; then
            log_message "Opening web UI in browser: $browser"
            echo "Opening web UI in browser: $browser"
            "$browser" "$url" &> /dev/null &
            return 0
        fi
    done

    log_message "Warning: No suitable web browser found to open $url"
    echo "Warning: No suitable web browser found to open $url"
    echo "Please manually open your browser and navigate to: $url"
    return 1
}

# Launch ForgedKismet in terminal
log_message "Launching ForgedKismet with configuration: $CONFIG_FILE"
log_message "Using terminal: $TERMINAL"
echo "Launching ForgedKismet with configuration: $CONFIG_FILE"
echo "Using terminal: $TERMINAL"

# Create a launch script for the terminal to execute
LAUNCH_SCRIPT="/tmp/kismet-launch-$$.sh"
cat > "$LAUNCH_SCRIPT" << EOF
#!/bin/bash
echo "========================================"
echo "ForgedKismet - Enhanced Kismet Launcher"
echo "========================================"
echo "Configuration: $CONFIG_FILE"
echo "Web Interface: http://localhost:2501"
echo ""
echo "Starting Kismet server..."
echo "Press Ctrl+C to stop Kismet"
echo ""

# Change to the correct directory
cd "/home/dragos/Downloads/kismet"

# Check if port 2501 is already in use
if netstat -tln 2>/dev/null | grep -q ":2501 "; then
    echo "WARNING: Port 2501 is already in use!"
    echo "Another Kismet instance may be running."
    echo "Please stop other Kismet instances first."
    echo ""
    read -p "Press Enter to continue anyway or Ctrl+C to exit..."
fi

# Launch Kismet
echo "Launching Kismet..."
echo "You may be prompted for your password to run Kismet with proper permissions."
echo ""
sudo /usr/bin/kismet --config-file="$CONFIG_FILE"

echo ""
echo "Kismet has stopped."
read -p "Press Enter to close this window..."
EOF

chmod +x "$LAUNCH_SCRIPT"
log_message "Created launch script: $LAUNCH_SCRIPT"

# Start Kismet in terminal
log_message "Executing: $TERMINAL $LAUNCH_SCRIPT"
$TERMINAL "$LAUNCH_SCRIPT" &
TERMINAL_PID=$!

# Wait for Kismet to start up and be ready
wait_for_kismet

# Wait for Kismet to be ready
wait_for_kismet

# Open the web UI
echo "Opening Kismet Web UI..."
log_message "Opening Kismet Web UI..."
open_browser "http://localhost:2501"

# Clean up the temporary launch script after a delay
(sleep 60; rm -f "$LAUNCH_SCRIPT") &

log_message "ForgedKismet wrapper completed successfully"
