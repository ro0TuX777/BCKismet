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
