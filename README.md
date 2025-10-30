# Kismet - WiFi/Bluetooth Detection for RF-Kit

Kismet wireless network detector integrated with RF-Kit for comprehensive WiFi and Bluetooth scanning.

## Overview

This directory contains Kismet configuration and data export tools for the RF-Kit system. Kismet scans for WiFi networks and Bluetooth devices, storing data in SQLite databases that are then exported to JSON for Elasticsearch ingestion.

## Features

- **WiFi Detection** - Comprehensive 802.11 network scanning
- **Bluetooth Detection** - Bluetooth device discovery and tracking
- **Database Export** - Convert Kismet SQLite databases to JSON
- **Elasticsearch Integration** - Automatic data export via Filebeat
- **Control Panel Integration** - Managed by RF-Kit control panel

## Quick Start

### Using Control Panel (Recommended)

```bash
cd /home/dragos/rf-kit/control-panel
python3 control-panel.py
# Select Option 2 for Quick Scan (includes Kismet)
# Select Option 9 to Export Kismet Data
```

### Manual Operation

1. **Start Kismet:**
   ```bash
   sudo kismet --override=/home/dragos/Downloads/kismet/forgedfate/kismet_site.conf
   ```

2. **Export Kismet Database:**
   ```bash
   cd /home/dragos/rf-kit/kismet
   python3 kismet_to_json_exporter.py /path/to/database.kismet
   ```

## Configuration

### Kismet Configuration File

Location: `/home/dragos/Downloads/kismet/forgedfate/kismet_site.conf`

**Key Settings:**
```
log_types=kismet
log_title=Kismet
log_prefix=/home/dragos/Downloads/kismet/forgedfate/logs/
```

### Data Export Configuration

Kismet databases are exported to JSON and ingested by Filebeat:

**Export Location:** `/home/dragos/rf-kit/logs/kismet/`

**Filebeat Paths:**
- WiFi devices: `/home/dragos/rf-kit/logs/kismet/Kismet-*/wifi.devices.json`
- Bluetooth devices: `/home/dragos/rf-kit/logs/kismet/Kismet-*/bluetooth.devices.json`

**Elasticsearch Index:** `kismet-sdr-default`

## Data Flow

```
Kismet Scan
    ↓
SQLite Database (.kismet file)
    ↓
kismet_to_json_exporter.py
    ↓
JSON Files (wifi.devices.json, bluetooth.devices.json)
    ↓
Filebeat
    ↓
Elasticsearch (kismet-sdr-default index)
    ↓
Kibana Dashboard
```

## Files

### kismet_to_json_exporter.py

Exports Kismet SQLite databases to JSON format for Elasticsearch ingestion.

**Usage:**
```bash
python3 kismet_to_json_exporter.py /path/to/database.kismet
```

**Output:**
- Creates directory: `/home/dragos/rf-kit/logs/kismet/Kismet-YYYYMMDD-HH-MM-SS-N/`
- Exports `wifi.devices.json` - WiFi access points and clients
- Exports `bluetooth.devices.json` - Bluetooth devices

**Features:**
- Extracts device information (MAC, SSID, manufacturer, signal strength)
- Converts timestamps to Unix format for Elasticsearch
- Handles both WiFi and Bluetooth devices
- Automatic Filebeat ingestion

### Configuration Files

- `forgedfate/kismet_site.conf` - Main Kismet configuration
- `kismet/` - Kismet source code (ForgedFate fork)

## Directory Structure

```
kismet/
├── kismet_to_json_exporter.py   # Database export tool
├── forgedfate/                  # Kismet configuration
│   ├── kismet_site.conf         # Main config file
│   └── logs/                    # Kismet database output
├── kismet/                      # Kismet source (ForgedFate)
│   ├── capture_linux_bluetooth/
│   ├── examples/
│   ├── kaitai/
│   └── README.md
└── README.md                    # This file
└── README.md                    # This file
```

## Troubleshooting

### Kismet Not Creating Database Files

**Problem:** Kismet runs but no `.kismet` files are created

**Solution:** Check `log_types` and `log_title` in `kismet_site.conf`:
```
log_types=kismet
log_title=Kismet
```

### Data Not Appearing in Elasticsearch

**Problem:** JSON files exported but not in Elasticsearch

**Solution:**
1. Check timestamp format (must be Unix timestamps, not ISO strings)
2. Restart Filebeat: `sudo systemctl restart filebeat`
3. Verify Filebeat is watching correct paths
4. Check Filebeat logs: `journalctl -u filebeat -n 50`

### Permission Denied

**Problem:** Cannot start Kismet

**Solution:** Run with sudo: `sudo kismet`

## Web Interface

When Kismet is running, access the web interface at:
- **URL:** http://localhost:2501
- **Features:** Live device tracking, network visualization, packet capture

## Integration with RF-Kit

Kismet is fully integrated with the RF-Kit control panel:
- Automatically started/stopped during scans
- Data exported to Elasticsearch
- Monitored in unified dashboard
- Logs accessible from control panel

For more information, see the [Control Panel README](../control-panel/README.md).

## References

- **Official Kismet Documentation:** https://www.kismetwireless.net/docs/
- **ForgedFate Project:** Based on enhanced Kismet fork with export capabilities
