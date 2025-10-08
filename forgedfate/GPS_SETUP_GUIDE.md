# 🛰️ ForgedFate GPS Integration Setup Guide

## 📋 **Overview**

This guide provides step-by-step instructions for integrating the BU-353 S4 GPS USB dongle with your ForgedFate Kismet build. The implementation uses a **gpsd-first approach** with serial fallback for maximum reliability.

## 🎯 **Features**

✅ **Dual GPS Sources** - gpsd primary, serial fallback  
✅ **Stable Device Naming** - `/dev/gps0` via udev rules  
✅ **Automatic Service Management** - systemd integration  
✅ **Health Monitoring** - Comprehensive diagnostics  
✅ **Watchdog Support** - Automatic recovery  
✅ **Kismet Integration** - Location-aware wireless monitoring  

## 🔧 **Prerequisites**

- **Hardware**: BU-353 S4 GPS USB dongle (PL2303 chipset)
- **OS**: Ubuntu 24.04+ or compatible Linux distribution
- **Permissions**: sudo access for system configuration
- **ForgedFate**: Kismet build with GPS support

## 📦 **Quick Setup**

### **Step 1: Run the GPS Integration Installer**

```bash
cd /home/dragos/Downloads/kismet/forgedfate
./install_gps_support.sh
```

This script will:
- Install required GPS packages (gpsd, gpsd-clients)
- Create udev rules for stable device naming
- Configure gpsd service
- Set up systemd integration
- Add user to dialout group

### **Step 2: Verify Installation**

```bash
./gps_health_check.sh
```

This will perform comprehensive checks:
- USB device detection
- Device file permissions
- Service status
- GPS data availability
- Kismet configuration

### **Step 3: Test GPS Functionality**

```bash
# Check raw GPS data
cat /dev/gps0

# Test gpsd connection
cgps -s

# Monitor GPS with detailed view
gpsmon /dev/gps0
```

### **Step 4: Start Kismet with GPS**

```bash
# Stop any running Kismet instance
pkill -f kismet

# Start with GPS-enabled configuration
./forgedkismet-wrapper.sh /home/dragos/Downloads/kismet/forgedfate/kismet_working.conf
```

## 🔍 **Detailed Configuration**

### **GPS Device Detection**

Your BU-353 S4 should appear as:
```bash
# USB device
lsusb | grep "067b:2303"
# Output: Bus 003 Device 020: ID 067b:2303 Prolific Technology, Inc. PL2303 Serial Port

# Device files
ls -la /dev/gps0 /dev/ttyUSB0
# Output: 
# lrwxrwxrwx 1 root root 7 Oct  8 12:30 /dev/gps0 -> ttyUSB0
# crw-rw---- 1 root dialout 188, 0 Oct  8 12:30 /dev/ttyUSB0
```

### **Service Status**

Check GPS services:
```bash
# gpsd service
sudo systemctl status gpsd

# gpsd socket
sudo systemctl status gpsd.socket

# View logs
sudo journalctl -u gpsd -f
```

### **Kismet GPS Configuration**

The updated configuration includes:

```bash
# GPS Configuration - BU-353 S4 with gpsd-first approach
# Primary: gpsd (recommended for reliability)
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

## 🚨 **Troubleshooting**

### **Common Issues**

**Issue: GPS device not found**
```bash
# Check USB connection
lsusb | grep 067b:2303

# Reload udev rules
sudo udevadm control --reload-rules
sudo udevadm trigger

# Check for any ttyUSB devices
ls -la /dev/ttyUSB*
```

**Issue: Permission denied**
```bash
# Add user to dialout group
sudo usermod -a -G dialout $USER

# Log out and back in, then check
groups | grep dialout

# Set device permissions manually if needed
sudo chmod 666 /dev/gps0
```

**Issue: gpsd not starting**
```bash
# Check gpsd status and logs
sudo systemctl status gpsd
sudo journalctl -u gpsd -n 50

# Restart gpsd services
sudo systemctl restart gpsd.socket
sudo systemctl restart gpsd
```

**Issue: No GPS fix**
```bash
# Check GPS signal (requires clear sky view)
cgps -s

# Monitor raw NMEA data
cat /dev/gps0

# Check antenna connection and move outdoors
```

### **Manual Testing**

```bash
# Test raw GPS data with specific baud rate
stty -F /dev/gps0 4800
cat /dev/gps0

# Test gpsd connection
echo "?WATCH={\"enable\":true,\"json\":true}" | nc localhost 2947

# Test Kismet GPS sources
kismet --list-datasources | grep -i gps
```

## 📊 **Monitoring and Maintenance**

### **GPS Watchdog**

Enable automatic GPS monitoring:
```bash
# Copy watchdog script to system location
sudo cp gps_watchdog.sh /usr/local/bin/

# Create systemd timer (optional)
sudo systemctl enable gps-watchdog.timer
sudo systemctl start gps-watchdog.timer
```

### **Performance Monitoring**

```bash
# Check GPS fix quality
cgps -s

# Monitor GPS data rate
cat /dev/gps0 | pv > /dev/null

# Check Kismet GPS logs
tail -f ~/.kismet/logs/kismet*.log | grep -i gps
```

## 🎯 **Integration with ForgedFate**

### **Web Interface GPS Status**

1. **Open Kismet web interface**: `http://localhost:2501`
2. **Navigate to GPS tab** to view:
   - Current GPS coordinates
   - Fix quality and satellite count
   - GPS track history
   - Location-based device mapping

### **Export GPS Data**

Use the Export functionality (bookmarklet) to include GPS data:

1. **Click the Export button** in Kismet web interface
2. **Configure Elasticsearch export** with GPS data
3. **Generated commands** will include location information

### **GPS Data in Elasticsearch**

GPS coordinates will be included in exported data:
```json
{
  "@timestamp": "2025-10-08T12:00:00.000Z",
  "device_name": "dragon-os-box",
  "gps": {
    "lat": 40.7128,
    "lon": -74.0060,
    "alt": 10.5,
    "fix": 3,
    "satellites": 8
  },
  "wifi_device": {
    "mac": "aa:bb:cc:dd:ee:ff",
    "ssid": "ExampleNetwork"
  }
}
```

## ✅ **Verification Checklist**

- [ ] BU-353 S4 GPS device connected via USB
- [ ] Device appears as `/dev/gps0` and `/dev/ttyUSB0`
- [ ] User is member of `dialout` group
- [ ] gpsd service is running and active
- [ ] Raw GPS data is available (`cat /dev/gps0`)
- [ ] gpsd client can connect (`cgps -s`)
- [ ] Kismet configuration includes GPS sources
- [ ] Kismet web interface shows GPS status
- [ ] GPS coordinates appear in exported data

## 🚀 **Next Steps**

1. **Test GPS accuracy** by comparing with known coordinates
2. **Configure GPS logging** for your specific use case
3. **Set up automated exports** with GPS data to Elasticsearch
4. **Create GPS-based alerts** in Kismet for location tracking
5. **Integrate with mapping tools** for visualization

## 📞 **Support**

If you encounter issues:

1. **Run health check**: `./gps_health_check.sh`
2. **Check logs**: `sudo journalctl -u gpsd -f`
3. **Verify hardware**: Ensure GPS has clear sky view
4. **Review configuration**: Compare with working examples

Your ForgedFate GPS integration is now ready for location-aware wireless intelligence! 🛰️
