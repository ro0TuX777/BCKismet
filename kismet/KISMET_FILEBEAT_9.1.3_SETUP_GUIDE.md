# Kismet Filebeat 9.1.3 Setup Guide for DragonOS

This guide provides step-by-step instructions for setting up Filebeat 9.1.3 to ingest comprehensive Kismet data (Bluetooth, WiFi, and all other supported protocols) into Elasticsearch.

## 🚀 Quick Setup

### Option 1: Automated Setup (Recommended)

```bash
# Navigate to the Kismet directory
cd /path/to/ForgedFate/kismet

# Run the automated setup script
sudo ./setup_kismet_filebeat_9.1.3.sh
```

### Option 2: Manual Installation

Follow the manual steps below if you prefer to understand each step or need to customize the installation.

## 📋 Manual Installation Steps

### 1. Install Filebeat 9.1.3

```bash
# Download Filebeat 9.1.3
curl -L -O https://artifacts.elastic.co/downloads/beats/filebeat/filebeat-9.1.3-amd64.deb

# Install the package
sudo dpkg -i filebeat-9.1.3-amd64.deb

# Fix any dependency issues
sudo apt-get install -f -y
```

### 2. Configure Permissions

```bash
# Create kismet group if it doesn't exist
sudo groupadd kismet

# Add filebeat user to kismet group
sudo usermod -a -G kismet filebeat

# Set up log directory permissions (if Kismet logs exist)
sudo chgrp -R kismet /opt/kismet/logs
sudo chmod -R g+r /opt/kismet/logs
```

### 3. Install Filebeat Configuration

```bash
# Backup existing configuration
sudo cp /etc/filebeat/filebeat.yml /etc/filebeat/filebeat.yml.backup.$(date +%Y%m%d_%H%M%S)

# Copy the comprehensive Kismet configuration
sudo cp filebeat-kismet-complete.yml /etc/filebeat/filebeat.yml

# Set proper permissions
sudo chown root:root /etc/filebeat/filebeat.yml
sudo chmod 600 /etc/filebeat/filebeat.yml
```

### 4. Test Configuration

```bash
# Test configuration syntax
sudo filebeat test config

# Test Elasticsearch connectivity
sudo filebeat test output
```

### 5. Start Filebeat

```bash
# Enable and start Filebeat
sudo systemctl enable filebeat
sudo systemctl restart filebeat

# Check status
sudo systemctl status filebeat
```

## 📊 Supported Kismet Log Types

The configuration automatically detects and ingests the following Kismet log types:

| Log Type | File Pattern | Description |
|----------|--------------|-------------|
| **General Devices** | `devices.json` | All detected devices |
| **Bluetooth** | `bluetooth.devices.json` | Bluetooth devices and services |
| **WiFi** | `wifi.devices.json` | WiFi networks and clients |
| **Packets** | `packets.json` | Raw packet data |
| **Alerts** | `alerts.json` | Security alerts and notifications |
| **ADS-B** | `adsb.devices.json` | Aircraft transponder data |
| **RTL433** | `rtl433.devices.json` | ISM band devices (sensors, etc.) |
| **Zigbee** | `zigbee.devices.json` | Zigbee network devices |
| **Radiation** | `radiation.devices.json` | Radiation detection data |
| **UAV/Drones** | `uav.devices.json` | Drone and UAV detection |

## ⚙️ Configuration Details

### Elasticsearch Settings
- **Host**: `https://172.18.18.20:9200`
- **Username**: `filebeat-dragonos`
- **Password**: `KUX4hkxjwp9qhu2wjx`
- **Index**: `kismet-sdr`
- **SSL Verification**: Disabled (`none`)

### Log Paths
All logs are expected in the standard Kismet location:
```
/opt/kismet/logs/Kismet-*/[log-type].json
```

### Field Enrichment
Each log entry is enriched with:
- `log_type`: Type of Kismet log (e.g., `kismet_bluetooth`)
- `source_device`: Device identifier (`dragonos-laptop`)
- `sdr_type`: SDR type identifier (`kismet_forgedfate`)
- `kismet_version`: Version identifier (`forgedfate`)

## 🔍 Verification

### Check Filebeat Status
```bash
# Service status
sudo systemctl status filebeat

# Live logs
sudo journalctl -u filebeat -f

# Configuration test
sudo filebeat test config
sudo filebeat test output
```

### Verify Data in Elasticsearch
```bash
# Check if index exists
curl -X GET "https://172.18.18.20:9200/_cat/indices/kismet-*?v" \
  -u "filebeat-dragonos:KUX4hkxjwp9qhu2wjx" \
  -k

# Sample data query
curl -X GET "https://172.18.18.20:9200/kismet-sdr/_search?size=1&pretty" \
  -u "filebeat-dragonos:KUX4hkxjwp9qhu2wjx" \
  -k

# Count documents by log type
curl -X GET "https://172.18.18.20:9200/kismet-sdr/_search?size=0&pretty" \
  -u "filebeat-dragonos:KUX4hkxjwp9qhu2wjx" \
  -k \
  -H "Content-Type: application/json" \
  -d '{
    "aggs": {
      "log_types": {
        "terms": {
          "field": "log_type.keyword"
        }
      }
    }
  }'
```

### Generate Test Data
```bash
# Start Kismet to generate logs
sudo kismet

# Or run Kismet in the background
sudo kismet --daemonize
```

## 🛠️ Troubleshooting

### Common Issues

**Filebeat not starting:**
```bash
# Check configuration syntax
sudo filebeat test config

# Check permissions
sudo chown root:root /etc/filebeat/filebeat.yml
sudo chmod 600 /etc/filebeat/filebeat.yml

# Check logs
sudo journalctl -u filebeat -n 50
```

**No data in Elasticsearch:**
```bash
# Verify Kismet logs exist
ls -la /opt/kismet/logs/Kismet-*/

# Check Filebeat is reading files
sudo filebeat test input

# Check Elasticsearch connectivity
sudo filebeat test output

# Monitor Filebeat processing
sudo tail -f /var/log/filebeat/filebeat
```

**Permission errors:**
```bash
# Ensure Filebeat can read Kismet logs
sudo usermod -a -G kismet filebeat
sudo chmod g+r /opt/kismet/logs/Kismet-*/*

# Restart Filebeat after permission changes
sudo systemctl restart filebeat
```

### Log Analysis
```bash
# Filebeat logs
sudo tail -f /var/log/filebeat/filebeat

# Kismet logs
sudo tail -f /opt/kismet/logs/Kismet-*/kismet.log

# System logs
sudo journalctl -u filebeat -u kismet -f
```

## 🎯 Performance Tuning

### For High-Volume Environments
Edit `/etc/filebeat/filebeat.yml` and adjust:

```yaml
# Increase queue size
queue.mem:
  events: 8192
  flush.min_events: 1024
  flush.timeout: 1s

# Adjust scan frequency
scan_frequency: 5s

# Bulk size for Elasticsearch
output.elasticsearch:
  bulk_max_size: 1600
  worker: 2
```

### For Low-Resource Systems
```yaml
# Reduce queue size
queue.mem:
  events: 1024
  flush.min_events: 256

# Slower scan frequency
scan_frequency: 30s

# Single worker
output.elasticsearch:
  worker: 1
```

## 📈 Integration with Kibana

Once data is flowing to Elasticsearch, you can create Kibana dashboards:

1. **Create Index Pattern**: `kismet-sdr*`
2. **Key Fields for Visualization**:
   - `log_type.keyword` - Filter by data type
   - `source_device.keyword` - Filter by device
   - `@timestamp` - Time-based analysis
   - Device-specific fields from Kismet logs

3. **Suggested Visualizations**:
   - Device detection timeline
   - Bluetooth vs WiFi device counts
   - Alert frequency over time
   - Geographic distribution (if GPS data available)

## 🔄 Maintenance

### Regular Tasks
```bash
# Check disk space
df -h /var/log/filebeat
df -h /opt/kismet/logs

# Rotate logs
sudo logrotate /etc/logrotate.d/filebeat

# Update configuration if needed
sudo ./setup_kismet_filebeat_9.1.3.sh
```

### Updates
When updating ForgedFate or Kismet:
1. Stop Filebeat: `sudo systemctl stop filebeat`
2. Update ForgedFate/Kismet
3. Re-run setup script: `sudo ./setup_kismet_filebeat_9.1.3.sh`
4. Verify data flow continues

## 📞 Support

For issues with this integration:
1. Check this guide for common solutions
2. Review Filebeat and Elasticsearch logs
3. Test individual components (config, connectivity, log files)
4. Use the diagnostic commands provided in the troubleshooting section

The comprehensive Kismet Filebeat integration provides robust monitoring of all wireless protocols supported by Kismet, making it easy to analyze and visualize your wireless environment data in Elasticsearch and Kibana!
