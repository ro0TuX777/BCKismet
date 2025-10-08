#!/bin/bash
# ForgedFate GPS Integration Installer
# Configures BU-353 S4 GPS support for Kismet

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
    error "This script should not be run as root. Run as regular user with sudo access."
    exit 1
fi

log "Starting ForgedFate GPS Integration Setup..."

# 1. Install required packages
log "Installing GPS packages..."
sudo apt update
sudo apt install -y gpsd gpsd-clients python3-gps

# 2. Stop services before configuration
log "Stopping GPS services..."
sudo systemctl stop gpsd || true
sudo systemctl stop gpsd.socket || true

# 3. Create udev rule
log "Creating udev rule for BU-353 S4..."
sudo tee /etc/udev/rules.d/99-gps-bu353s4.rules > /dev/null << 'EOF'
# BU-353 S4 GPS USB Dongle (Prolific PL2303)
# Creates stable /dev/gps0 symlink for the GPS device
SUBSYSTEM=="tty", ATTRS{idVendor}=="067b", ATTRS{idProduct}=="2303", ATTRS{product}=="USB-Serial Controller", SYMLINK+="gps0", GROUP="dialout", MODE="0664"

# Alternative rule if product string varies
SUBSYSTEM=="tty", ATTRS{idVendor}=="067b", ATTRS{idProduct}=="2303", SYMLINK+="gps0", GROUP="dialout", MODE="0664"
EOF

# 4. Reload udev rules
log "Reloading udev rules..."
sudo udevadm control --reload-rules
sudo udevadm trigger

# 5. Configure gpsd
log "Configuring gpsd..."
sudo tee /etc/default/gpsd > /dev/null << 'EOF'
# Default settings for the gpsd init script and the hotplug wrapper.

# Start the gpsd daemon automatically at boot time
START_DAEMON="true"

# Use USB hotplugging to add new USB devices automatically to the daemon
USBAUTO="true"

# Devices gpsd should collect to at boot time.
# They need to be read/writeable, either by user gpsd or the group dialout.
DEVICES="/dev/gps0"

# Other options you want to pass to gpsd
GPSD_OPTIONS="-n -b"

# Automatically hot add/remove USB GPS devices via gpsdctl
GPSD_SOCKET="/var/run/gpsd.sock"
EOF

# 6. Create systemd override
log "Creating systemd service override..."
sudo mkdir -p /etc/systemd/system/gpsd.service.d
sudo tee /etc/systemd/system/gpsd.service.d/override.conf > /dev/null << 'EOF'
[Unit]
# Ensure GPS device is available before starting
After=dev-gps0.device
Wants=dev-gps0.device

[Service]
# Restart on failure
Restart=on-failure
RestartSec=5

# Environment variables
Environment="GPSD_OPTIONS=-n -b"
Environment="GPSD_SOCKET=/var/run/gpsd.sock"

# Start gpsd with proper options
ExecStart=
ExecStart=/usr/sbin/gpsd -N -n -b /dev/gps0
EOF

# 7. Add user to dialout group
log "Adding user to dialout group..."
sudo usermod -a -G dialout $USER

# 8. Reload systemd and enable services
log "Reloading systemd configuration..."
sudo systemctl daemon-reload
sudo systemctl enable gpsd
sudo systemctl enable gpsd.socket

# 9. Wait for device and start services
log "Waiting for GPS device..."
sleep 3

if [ -e /dev/gps0 ]; then
    success "GPS device found at /dev/gps0"
    
    log "Starting GPS services..."
    sudo systemctl start gpsd.socket
    sudo systemctl start gpsd
    
    sleep 5
    
    # Test gpsd connection
    if systemctl is-active --quiet gpsd; then
        success "gpsd service is running"
    else
        warning "gpsd service failed to start"
    fi
else
    warning "GPS device not found at /dev/gps0. Please check USB connection."
fi

success "GPS integration setup complete!"
log "Please log out and back in for group changes to take effect."
log "Run './gps_health_check.sh' to verify GPS functionality."
