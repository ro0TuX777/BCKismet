# Kismet + BU-353 S4 (PL2303) Integration Plan

## Goals

- **gpsd-first**: If gpsd is running and exposing a socket, Kismet uses it.
- **Serial fallback**: If gpsd is unavailable, Kismet opens /dev/ttyUSBx directly at baud=4800.
- **Deterministic device path**: udev rule creates /dev/gps0 for the BU-353 S4.
- **Repeatable**: One-shot installer + idempotent config (safe to re-run).
- **Observability**: Health checks + logs to quickly diagnose “NO FIX” vs config issues.

## 0) System Requirements

- Ubuntu 24.04+ (noble) or similar.
- Packages: gpsd, gpsd-clients, kismet (our specialized build).
- Kismet service user belongs to dialout.

## 1) udev rule (stable device name)

Create `/etc/udev/rules.d/99-gps-bu353s4.rules`:

```bash
# BU-353 S4 GPS USB Dongle (Prolific PL2303)
# Creates stable /dev/gps0 symlink for the GPS device
SUBSYSTEM=="tty", ATTRS{idVendor}=="067b", ATTRS{idProduct}=="2303", ATTRS{product}=="USB-Serial Controller", SYMLINK+="gps0", GROUP="dialout", MODE="0664"

# Alternative rule if product string varies
SUBSYSTEM=="tty", ATTRS{idVendor}=="067b", ATTRS{idProduct}=="2303", SYMLINK+="gps0", GROUP="dialout", MODE="0664"
```

## 2) gpsd Configuration

Create `/etc/default/gpsd`:

```bash
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
```

## 3) gpsd systemd service configuration

Create `/etc/systemd/system/gpsd.service.d/override.conf`:

```ini
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
```

## 4) Kismet GPS Configuration

### 4.1) Primary GPS source (gpsd-first)

In your Kismet configuration file, add:

```bash
# GPS Configuration - BU-353 S4 with gpsd-first approach
# Try gpsd first, fallback to serial if unavailable
source=gpsd:host=localhost,port=2947:name=GPS-GPSD:priority=100
source=gpsnmea:/dev/gps0:baud=4800:name=GPS-Serial:priority=50

# GPS settings
gps=true
gps_reconnect=true
gps_log=true
gps_reconnect_attempt=30
```

### 4.2) Alternative configuration (serial-only)

If you prefer direct serial access:

```bash
# GPS Configuration - Direct serial access to BU-353 S4
source=gpsnmea:/dev/gps0:baud=4800:name=GPS-BU353S4:priority=100

# GPS settings
gps=true
gps_reconnect=true
gps_log=true
gps_reconnect_attempt=30
```

## 5) Installation Script

Create `install_gps_support.sh`:

```bash
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
log "Run 'gps_health_check.sh' to verify GPS functionality."
```

## 6) Health Check Script

Create `gps_health_check.sh`:

```bash
#!/bin/bash
# ForgedFate GPS Health Check
# Comprehensive GPS functionality verification

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

check_mark() {
    echo -e "${GREEN}✓${NC}"
}

cross_mark() {
    echo -e "${RED}✗${NC}"
}

# Header
echo "=================================================="
echo "    ForgedFate GPS Health Check"
echo "    BU-353 S4 (PL2303) Integration Verification"
echo "=================================================="
echo

# 1. Check USB device
log "Checking USB GPS device..."
if lsusb | grep -q "067b:2303"; then
    success "BU-353 S4 GPS device detected via USB"
    echo -n "   USB Device: "
    check_mark
    lsusb | grep "067b:2303"
else
    error "BU-353 S4 GPS device not found via USB"
    echo -n "   USB Device: "
    cross_mark
    echo "   Please check USB connection"
fi
echo

# 2. Check device files
log "Checking device files..."
if [ -e /dev/gps0 ]; then
    success "Stable GPS device found: /dev/gps0"
    echo -n "   /dev/gps0: "
    check_mark
    ls -la /dev/gps0
else
    warning "Stable GPS device /dev/gps0 not found"
    echo -n "   /dev/gps0: "
    cross_mark
fi

if [ -e /dev/ttyUSB0 ]; then
    success "Raw GPS device found: /dev/ttyUSB0"
    echo -n "   /dev/ttyUSB0: "
    check_mark
    ls -la /dev/ttyUSB0
else
    warning "Raw GPS device /dev/ttyUSB0 not found"
    echo -n "   /dev/ttyUSB0: "
    cross_mark
fi
echo

# 3. Check permissions
log "Checking device permissions..."
if [ -e /dev/gps0 ]; then
    if [ -r /dev/gps0 ] && [ -w /dev/gps0 ]; then
        success "GPS device permissions OK"
        echo -n "   Permissions: "
        check_mark
    else
        error "GPS device permissions insufficient"
        echo -n "   Permissions: "
        cross_mark
        echo "   Run: sudo chmod 666 /dev/gps0"
    fi
fi
echo

# 4. Check group membership
log "Checking group membership..."
if groups | grep -q dialout; then
    success "User is member of dialout group"
    echo -n "   dialout group: "
    check_mark
else
    warning "User is not member of dialout group"
    echo -n "   dialout group: "
    cross_mark
    echo "   Run: sudo usermod -a -G dialout $USER"
fi
echo

# 5. Check gpsd service
log "Checking gpsd service..."
if systemctl is-active --quiet gpsd; then
    success "gpsd service is running"
    echo -n "   gpsd service: "
    check_mark
    systemctl status gpsd --no-pager -l
else
    warning "gpsd service is not running"
    echo -n "   gpsd service: "
    cross_mark
    echo "   Run: sudo systemctl start gpsd"
fi
echo

# 6. Check gpsd socket
log "Checking gpsd socket..."
if systemctl is-active --quiet gpsd.socket; then
    success "gpsd socket is active"
    echo -n "   gpsd socket: "
    check_mark
else
    warning "gpsd socket is not active"
    echo -n "   gpsd socket: "
    cross_mark
    echo "   Run: sudo systemctl start gpsd.socket"
fi
echo

# 7. Test raw GPS data
log "Testing raw GPS data (10 seconds)..."
if [ -e /dev/gps0 ]; then
    echo "   Reading raw NMEA data from /dev/gps0..."
    timeout 10s cat /dev/gps0 | head -5 || {
        warning "No data received from GPS device"
        echo "   This may be normal if GPS has no fix yet"
    }
else
    error "Cannot test raw GPS data - device not available"
fi
echo

# 8. Test gpsd client
log "Testing gpsd client connection..."
if command -v cgps >/dev/null 2>&1; then
    echo "   Testing gpsd connection (5 seconds)..."
    timeout 5s cgps -s || {
        warning "cgps failed to connect or get data"
        echo "   This may be normal if GPS has no fix yet"
    }
else
    warning "cgps not available - install gpsd-clients"
fi
echo

# 9. Test with gpsmon
log "Testing with gpsmon..."
if command -v gpsmon >/dev/null 2>&1; then
    echo "   Testing GPS monitor (5 seconds)..."
    timeout 5s gpsmon /dev/gps0 || {
        warning "gpsmon failed"
        echo "   This may be normal if GPS has no fix yet"
    }
else
    warning "gpsmon not available - install gpsd-clients"
fi
echo

# 10. Kismet GPS configuration check
log "Checking Kismet GPS configuration..."
KISMET_CONF="/home/dragos/Downloads/kismet/forgedfate/kismet_site.conf"
if [ -f "$KISMET_CONF" ]; then
    if grep -q "gps.*true" "$KISMET_CONF"; then
        success "GPS enabled in Kismet configuration"
        echo -n "   GPS enabled: "
        check_mark
    else
        warning "GPS not enabled in Kismet configuration"
        echo -n "   GPS enabled: "
        cross_mark
    fi

    if grep -q "source=.*gps" "$KISMET_CONF"; then
        success "GPS source configured in Kismet"
        echo -n "   GPS source: "
        check_mark
        grep "source=.*gps" "$KISMET_CONF" | head -2
    else
        warning "No GPS source found in Kismet configuration"
        echo -n "   GPS source: "
        cross_mark
    fi
else
    error "Kismet configuration file not found: $KISMET_CONF"
fi
echo

# Summary
echo "=================================================="
echo "                   SUMMARY"
echo "=================================================="

# Count checks
total_checks=0
passed_checks=0

# Device checks
if lsusb | grep -q "067b:2303"; then ((passed_checks++)); fi
((total_checks++))

if [ -e /dev/gps0 ]; then ((passed_checks++)); fi
((total_checks++))

if [ -e /dev/gps0 ] && [ -r /dev/gps0 ] && [ -w /dev/gps0 ]; then ((passed_checks++)); fi
((total_checks++))

if groups | grep -q dialout; then ((passed_checks++)); fi
((total_checks++))

if systemctl is-active --quiet gpsd; then ((passed_checks++)); fi
((total_checks++))

if systemctl is-active --quiet gpsd.socket; then ((passed_checks++)); fi
((total_checks++))

echo "Checks passed: $passed_checks/$total_checks"

if [ $passed_checks -eq $total_checks ]; then
    success "All GPS health checks passed!"
    echo
    log "GPS integration is working correctly."
    log "You can now use GPS with Kismet."
else
    warning "Some GPS health checks failed."
    echo
    log "Please review the failed checks above and follow the suggested fixes."
fi

echo "=================================================="
```

## 7) Troubleshooting Guide

### 7.1) Common Issues

**Issue: GPS device not found**
```bash
# Check USB connection
lsusb | grep 067b:2303

# Check for any ttyUSB devices
ls -la /dev/ttyUSB*

# Reload udev rules
sudo udevadm control --reload-rules
sudo udevadm trigger
```

**Issue: Permission denied**
```bash
# Add user to dialout group
sudo usermod -a -G dialout $USER

# Set device permissions
sudo chmod 666 /dev/gps0
sudo chmod 666 /dev/ttyUSB0
```

**Issue: gpsd not starting**
```bash
# Check gpsd status
sudo systemctl status gpsd

# Check gpsd logs
sudo journalctl -u gpsd -f

# Restart gpsd
sudo systemctl restart gpsd
```

**Issue: No GPS fix**
```bash
# Check GPS signal strength
cgps -s

# Monitor raw NMEA data
cat /dev/gps0

# Check GPS antenna connection
# Move to outdoor location with clear sky view
```

### 7.2) Manual Testing Commands

```bash
# Test raw GPS data
cat /dev/gps0

# Test with specific baud rate
stty -F /dev/gps0 4800
cat /dev/gps0

# Test gpsd connection
cgps -s
gpsmon /dev/gps0

# Test Kismet GPS
kismet --list-datasources | grep -i gps
```

### 7.3) Configuration Validation

```bash
# Validate udev rule
udevadm test $(udevadm info -q path -n /dev/ttyUSB0)

# Check gpsd configuration
cat /etc/default/gpsd

# Verify systemd override
cat /etc/systemd/system/gpsd.service.d/override.conf
```

## 8) Kismet Integration Examples

### 8.1) Updated Kismet Configuration

For your `forgedfate/kismet_site.conf`:

```bash
# GPS Configuration - BU-353 S4 with dual approach
# Primary: gpsd (recommended)
source=gpsd:host=localhost,port=2947:name=GPS-GPSD:priority=100

# Fallback: direct serial (if gpsd fails)
source=gpsnmea:/dev/gps0:baud=4800:name=GPS-Serial:priority=50

# GPS settings
gps=true
gps_reconnect=true
gps_log=true
gps_reconnect_attempt=30

# GPS logging options
gps_log_driver=true
gps_log_movement=true
```

### 8.2) Testing GPS with Kismet

```bash
# Start Kismet with GPS logging
kismet -c wlan0,gpsd:localhost:2947

# Check GPS status in Kismet logs
tail -f ~/.kismet/logs/kismet*.log | grep -i gps

# Verify GPS data in web interface
# Navigate to http://localhost:2501 -> GPS tab
```

## 9) Automation and Monitoring

### 9.1) GPS Watchdog Script

Create `gps_watchdog.sh`:

```bash
#!/bin/bash
# GPS Watchdog - Monitors and restarts GPS services if needed

GPS_DEVICE="/dev/gps0"
GPSD_SERVICE="gpsd"
LOG_FILE="/var/log/gps_watchdog.log"

log_message() {
    echo "$(date): $1" >> "$LOG_FILE"
}

# Check if GPS device exists
if [ ! -e "$GPS_DEVICE" ]; then
    log_message "GPS device $GPS_DEVICE not found, reloading udev rules"
    sudo udevadm control --reload-rules
    sudo udevadm trigger
    sleep 5
fi

# Check if gpsd is running
if ! systemctl is-active --quiet "$GPSD_SERVICE"; then
    log_message "gpsd service not running, restarting"
    sudo systemctl restart "$GPSD_SERVICE"
    sleep 10
fi

# Test GPS data availability
if ! timeout 10s cat "$GPS_DEVICE" | head -1 > /dev/null 2>&1; then
    log_message "No GPS data available, restarting gpsd"
    sudo systemctl restart "$GPSD_SERVICE"
fi

log_message "GPS watchdog check completed"
```

### 9.2) Systemd Timer for Watchdog

Create `/etc/systemd/system/gps-watchdog.timer`:

```ini
[Unit]
Description=GPS Watchdog Timer
Requires=gps-watchdog.service

[Timer]
OnBootSec=5min
OnUnitActiveSec=5min

[Install]
WantedBy=timers.target
```

Create `/etc/systemd/system/gps-watchdog.service`:

```ini
[Unit]
Description=GPS Watchdog Service
After=gpsd.service

[Service]
Type=oneshot
ExecStart=/home/dragos/Downloads/kismet/forgedfate/gps_watchdog.sh
User=root
```

## 10) Performance Optimization

### 10.1) GPS Update Rate Tuning

```bash
# For high-precision applications
source=gpsd:host=localhost,port=2947,rate=1:name=GPS-GPSD-1Hz

# For standard monitoring
source=gpsd:host=localhost,port=2947,rate=5:name=GPS-GPSD-5Hz

# For low-power applications
source=gpsd:host=localhost,port=2947,rate=10:name=GPS-GPSD-10Hz
```

### 10.2) Memory and CPU Optimization

```bash
# Limit GPS history in Kismet
gps_track_history=1000
gps_track_max_age=3600

# Optimize gpsd for performance
GPSD_OPTIONS="-n -b -N"
```

This completes the comprehensive GPS integration plan for your ForgedFate Kismet build!