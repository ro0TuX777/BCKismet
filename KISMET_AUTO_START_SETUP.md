# Kismet Auto-Start Configuration

## Overview

This configuration enables Kismet to automatically start on boot with all available data sources (WiFi and Bluetooth) enabled.

## Available Interfaces

### WiFi Interfaces
- **wlp0s20f3** - Internal WiFi adapter
- **wlx9cefd5f62bbe** - USB WiFi adapter #1
- **wlx8c902da2e062** - USB WiFi adapter #2

### Bluetooth Interfaces
- **hci0** - Bluetooth adapter

## Configuration Files

### 1. kismet_site.conf
Location: `/home/dragos/Downloads/kismet/forgedfate/kismet_site.conf`

This file contains the data source configuration that auto-enables all interfaces on startup.

```conf
# WiFi interfaces
source=wlp0s20f3:name=WiFi-Internal:hop=true
source=wlx9cefd5f62bbe:name=WiFi-USB-1:hop=true
source=wlx8c902da2e062:name=WiFi-USB-2:hop=true

# Bluetooth
source=hci0:name=Bluetooth:type=linuxbluetooth

# GPS
source=gpsd:host=localhost,port=2947:name=GPS-GPSD:priority=100
```

### 2. kismet-autostart.service
Location: `/home/dragos/rf-kit/kismet/kismet-autostart.service`

Systemd service file for auto-starting Kismet on boot.

## Installation Steps

### 1. Install the systemd service

```bash
sudo cp /home/dragos/rf-kit/kismet/kismet-autostart.service /etc/systemd/system/
sudo systemctl daemon-reload
```

### 2. Enable auto-start on boot

```bash
sudo systemctl enable kismet-autostart
```

### 3. Start the service now

```bash
sudo systemctl start kismet-autostart
```

### 4. Verify the service is running

```bash
sudo systemctl status kismet-autostart
```

## Accessing Kismet

- **Web UI**: http://localhost:2501
- **Remote Access**: http://<server-ip>:2501

## Data Export to Elasticsearch

Kismet data is automatically exported to Elasticsearch via Filebeat.

### Export Process

1. **Kismet captures data** → `.kismet` database files
2. **Export script converts** → JSON files (wifi.devices.json, bluetooth.devices.json)
3. **Filebeat reads JSON** → Sends to Elasticsearch
4. **Kibana dashboards** → Visualize the data

### Manual Export

To export current Kismet session to JSON:

```bash
cd /home/dragos/rf-kit
python3 kismet/kismet_to_json_exporter.py /home/dragos/Downloads/kismet/forgedfate/Kismet-<session>.kismet
```

This creates:
- `/home/dragos/rf-kit/logs/kismet/Kismet-<session>/wifi.devices.json`
- `/home/dragos/rf-kit/logs/kismet/Kismet-<session>/bluetooth.devices.json`

### Automated Export (TODO)

Create a cron job or systemd timer to periodically export Kismet data:

```bash
# Example cron job (every 5 minutes)
*/5 * * * * /home/dragos/rf-kit/kismet/export_latest_kismet.sh
```

## Troubleshooting

### Check if Kismet is running

```bash
ps aux | grep kismet
```

### View Kismet logs

```bash
sudo journalctl -u kismet-autostart -f
```

### Check data sources status

```bash
# Via web UI
http://localhost:2501

# Via command line
curl -s http://localhost:2501/datasource/all_sources.json | jq '.'
```

### Restart Kismet

```bash
sudo systemctl restart kismet-autostart
```

### Stop Kismet

```bash
sudo systemctl stop kismet-autostart
```

### Disable auto-start

```bash
sudo systemctl disable kismet-autostart
```

## Data Sources Not Starting?

If data sources are not auto-starting:

1. **Check interface names** - They may have changed:
   ```bash
   iw dev  # WiFi interfaces
   hciconfig  # Bluetooth interfaces
   ```

2. **Update kismet_site.conf** with correct interface names

3. **Restart Kismet**:
   ```bash
   sudo systemctl restart kismet-autostart
   ```

## Logs and Data Locations

- **Kismet databases**: `/home/dragos/Downloads/kismet/forgedfate/Kismet-*.kismet`
- **Exported JSON**: `/home/dragos/rf-kit/logs/kismet/Kismet-*/`
- **Filebeat config**: `/etc/filebeat/filebeat.yml`
- **Elasticsearch index**: `kismet-sdr-default`
- **Kibana dashboards**: https://172.18.18.20:5601/app/dashboards

## Current Status

✅ **Kismet is configured** with auto-enabled data sources
✅ **WiFi interfaces**: 3 adapters configured
✅ **Bluetooth**: 1 adapter configured  
✅ **GPS**: Configured (gpsd)
✅ **Systemd service**: Created
⏳ **Auto-start on boot**: Needs to be enabled (see Installation Steps)

## Next Steps

1. Enable the systemd service (see Installation Steps above)
2. Set up automated JSON export (cron job or systemd timer)
3. Fix Elasticsearch field mappings for WiFi data export
4. Create comprehensive Kismet dashboard with WiFi + Bluetooth data

