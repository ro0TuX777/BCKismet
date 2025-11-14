ss# 🚀 ForgedKismet Quick Start Guide

## Overview

ForgedKismet is an enhanced wireless network detection and monitoring application based on Kismet. This guide will get you up and running quickly with the essential features: launching the application, configuring source devices, and exporting data to Elasticsearch.

## 📋 Prerequisites

- Linux system with desktop environment
- WiFi adapters capable of monitor mode
- Bluetooth adapter (optional)
- GPS device (optional)
- Elasticsearch cluster (for data export)

## 🖥️ Step 1: Launch the Application

### Option A: Desktop Icon (Recommended)
1. **Locate the desktop icon** - Look for "ForgedKismet" on your desktop
2. **Double-click the icon** to launch the application
3. **Wait for startup** - The application will automatically:
   - Start the Kismet server with GPS and multi-device configuration
   - Open your web browser to `http://localhost:2501`
   - Initialize configured data sources (WiFi, Bluetooth, GPS)

### Option B: Command Line Launch
```bash
# Navigate to the application directory
cd /home/dragos/Downloads/kismet

# Launch with minimal configuration (GPS + WiFi + Bluetooth)
./launch-forgedkismet.sh
# Select option 1 for minimal configuration

# Or launch with full configuration (all devices including SDR)
./launch-forgedkismet.sh
# Select option 2 for full configuration
```

### Option C: Direct Kismet Launch
```bash
# Launch with specific configuration file
sudo kismet --config-file=/home/dragos/Downloads/kismet/forgedfate/kismet_working.conf
```

## 🔧 Step 2: Configure Source Devices

### Web Interface Configuration
1. **Access the web interface** at `http://localhost:2501`
2. **Click the hamburger menu** (☰) in the top-left corner
3. **Select "Data Sources"** from the menu
4. **Add or modify sources** as needed

### Available Source Types

#### WiFi Sources
- **Internal WiFi**: `wlp0s20f3:name=WiFi-Internal:hop=true`
- **USB WiFi Adapters**: `wlx9cefd5f62bbe:name=WiFi-USB-1:hop=true`
- **TP-Link RTL8821AU**: `wlx8c902da2e062:name=WiFi-USB-2:hop=true`

#### Bluetooth Sources
- **Internal Bluetooth**: `hci0:name=Bluetooth:type=linuxbluetooth`

#### GPS Sources
- **GPSD**: `gpsd:host=localhost,port=2947:name=GPS-GPSD`
- **Serial GPS**: `gpsnmea:/dev/ttyUSB0:baud=4800:name=GPS-Serial`
- **USB GPS**: `gpsnmea:/dev/ttyACM1:baud=9600:name=GPS-UBlox`

### Configuration Files
Source devices are pre-configured in these files:
- **Minimal Config**: `forgedfate/kismet_minimal.conf` - Basic working sources
- **Full Config**: `forgedfate/kismet_working.conf` - All available sources
- **Site Config**: `forgedfate/kismet_site.conf` - Custom overrides

## 📊 Step 3: View Real-Time Data

### Web Interface Features
1. **Device List** - View discovered WiFi networks and Bluetooth devices
2. **Live Map** - See device locations (requires GPS)
3. **Signal Strength** - Monitor signal levels and proximity
4. **Device Details** - Click on any device for detailed information
5. **Alerts** - Security alerts and anomaly detection

### Key Interface Elements
- **Top Bar**: Shows "Kismet ForgedFate" branding
- **Hamburger Menu** (☰): Access all features and settings
- **Device Tabs**: Switch between WiFi, Bluetooth, and other device types
- **Status Icons**: GPS, alerts, battery, and connection status

## 📤 Step 4: Export Data to Elasticsearch

### Method 1: Real-Time WebSocket Export (Recommended)
1. **Access Export GUI**:
   - Click hamburger menu (☰) → "Export"
   - Select "Real-Time WebSocket Export"

2. **Configure Connection**:
   ```
   Elasticsearch Host: your-elasticsearch-host:9200
   Username: your-username
   Password: your-password
   Index Prefix: kismet
   ```

3. **Start Export** - Data flows automatically to Elasticsearch

### Method 2: Bulk Database Upload
```bash
# Navigate to the application directory
cd /home/dragos/Downloads/kismet/forgedfate

# Upload existing database files
python kismet_bulk_upload.py \
  --es-hosts "your-elasticsearch-host:9200" \
  --es-username "your-username" \
  --es-password "your-password" \
  --index-prefix "kismet" \
  --log-directory "./logs"
```

### Method 3: Manual Database Export
```bash
# Export specific database to JSON
python kismet_elasticsearch_export.py \
  --input-file "logs/Kismet-20241029-12-00-00-1.kismet" \
  --elasticsearch-hosts "your-elasticsearch-host:9200" \
  --username "your-username" \
  --password "your-password"
```

## 🗄️ Step 5: View Kismet Database

### Database Location
Kismet databases are stored in:
```
/home/dragos/Downloads/kismet/forgedfate/logs/
```

### Database Files
- **`.kismet` files**: SQLite databases containing device and packet data
- **`.kismet-journal` files**: SQLite journal files (temporary)
- **`.pcapng` files**: Packet capture files (if enabled)

### Database Structure
The Kismet database contains these main tables:
- **`devices`**: Discovered devices (WiFi, Bluetooth, etc.)
- **`packets`**: Raw packet data
- **`data`**: Additional metadata and GPS information
- **`alerts`**: Security alerts and anomalies

### Viewing Database Content
```bash
# Use SQLite command line
sqlite3 logs/Kismet-20241029-12-00-00-1.kismet

# List tables
.tables

# View devices
SELECT * FROM devices LIMIT 5;

# View recent packets
SELECT ts_sec, sourcemac, destmac, signal FROM packets 
ORDER BY ts_sec DESC LIMIT 10;
```

### Export Database to JSON
```bash
# Convert entire database to JSON
kismet/log_tools/kismetdb_dump_devices \
  -i logs/Kismet-20241029-12-00-00-1.kismet \
  -o devices.json \
  --json-path
```

## 🔍 Troubleshooting

### Application Won't Start
- Check if Kismet is already running: `ps aux | grep kismet`
- Verify WiFi adapters support monitor mode
- Check configuration file paths in desktop shortcuts

### No Data Sources Detected
- Ensure WiFi adapters are not in use by NetworkManager
- Check USB device permissions
- Verify Bluetooth service is running: `systemctl status bluetooth`

### Web Interface Not Accessible
- Confirm Kismet is running on port 2501: `netstat -tlnp | grep 2501`
- Check firewall settings
- Try accessing via `http://127.0.0.1:2501`

### Elasticsearch Export Issues
- Verify Elasticsearch cluster is accessible
- Check authentication credentials
- Confirm network connectivity to Elasticsearch host
- Review export logs for error messages

## 📚 Additional Resources

- **Configuration Guide**: `DESKTOP_ICON_CREATION_GUIDE.md`
- **Export GUI Guide**: `EXPORT_GUI_GUIDE.md`
- **GPS Setup**: `forgedfate/GPS_SETUP_GUIDE.md`
- **Official Kismet Docs**: https://www.kismetwireless.net/docs/

## 🎯 Quick Reference

| Action | Method |
|--------|--------|
| Launch App | Double-click desktop icon |
| Web Interface | `http://localhost:2501` |
| Add Sources | Hamburger menu → Data Sources |
| Export Data | Hamburger menu → Export |
| View Logs | `forgedfate/logs/` directory |
| Stop App | Close web browser, Ctrl+C in terminal |

---

**Need Help?** Check the troubleshooting section above or refer to the detailed documentation files in this directory.
