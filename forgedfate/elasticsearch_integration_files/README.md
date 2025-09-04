# Elasticsearch Integration Files

This directory contains all the necessary files to integrate any application with the Elasticsearch server, based on the successful Kismet integration.

## Files Included

### 📋 Documentation
- **`README.md`** - This file
- **`../elasticsearch_integration_guide.md`** - Complete integration guide

### 🔧 Configuration Templates
- **`filebeat_config_template.yml`** - Filebeat configuration template
- **`setup_integration.sh`** - Automated setup script

### 🐍 Python Scripts
- **`data_to_json_converter.py`** - Convert various data formats to JSON
- **`test_elasticsearch_connection.py`** - Test Elasticsearch connectivity

## Quick Start

### 1. Copy Files to Your Application
```bash
# Copy the entire directory to your application
cp -r elasticsearch_integration_files /path/to/your/application/

# Navigate to your application directory
cd /path/to/your/application/elasticsearch_integration_files/
```

### 2. Customize Configuration
Edit the variables in `setup_integration.sh`:
```bash
APP_NAME="your-app-name"                    # Your application name
DEVICE_NAME="your-device-name"              # Your device identifier  
LOG_DIRECTORY="/path/to/your/app/logs"      # Your log directory
DATA_DIRECTORY="/path/to/your/app/data"     # Your data directory
```

### 3. Run Setup
```bash
# Make sure scripts are executable
chmod +x *.sh *.py

# Run the automated setup
sudo ./setup_integration.sh
```

### 4. Test Integration
```bash
# Test connection manually
python3 test_elasticsearch_connection.py \
    --device-name "your-device-name" \
    --app-name "your-app-name"

# Monitor the integration
./monitor_elasticsearch_integration.sh
```

## Manual Integration Steps

If you prefer manual setup, follow these steps:

### 1. Install Dependencies
```bash
sudo apt update
sudo apt install filebeat python3-pip
pip3 install requests
```

### 2. Convert Your Data
```bash
# For database files
python3 data_to_json_converter.py your_database.db output.json --device-name "your-device" --app-name "your-app"

# For log files  
python3 data_to_json_converter.py your_logfile.log output.json --device-name "your-device" --app-name "your-app"

# For CSV files
python3 data_to_json_converter.py your_data.csv output.json --device-name "your-device" --app-name "your-app"
```

### 3. Configure Filebeat
```bash
# Backup existing config
sudo cp /etc/filebeat/filebeat.yml /etc/filebeat/filebeat.yml.backup

# Copy and customize template
sudo cp filebeat_config_template.yml /etc/filebeat/filebeat.yml

# Edit the configuration file to match your paths and application details
sudo nano /etc/filebeat/filebeat.yml
```

### 4. Start Services
```bash
# Test configuration
sudo filebeat test config
sudo filebeat test output

# Start Filebeat
sudo systemctl enable filebeat
sudo systemctl start filebeat
```

## Data Format Requirements

### JSON Format
Your data should be in JSON Lines format (one JSON object per line):
```json
{"@timestamp": "2025-08-27T15:00:00Z", "device_name": "your-device", "app_name": "your-app", "message": "log entry"}
{"@timestamp": "2025-08-27T15:01:00Z", "device_name": "your-device", "app_name": "your-app", "message": "another entry"}
```

### Required Fields
Each document should include:
- **`@timestamp`** - ISO 8601 timestamp
- **`device_name`** - Your device identifier
- **`app_name`** - Your application name
- **`log_type`** - Type of log/data

## Verification

### Check in Kibana
1. Open: http://172.18.18.20:5601
2. Login: `vinson:ERC8mkm1ngf@anf0uwc`
3. Go to Discover
4. Search for: `device_name:"your-device-name"`

### Monitor Filebeat
```bash
# Check service status
sudo systemctl status filebeat

# View logs
sudo journalctl -u filebeat -f

# Check processed files
sudo cat /var/lib/filebeat/registry/filebeat/log.json | grep -o '"source":"[^"]*"'
```

## Troubleshooting

### Common Issues

1. **Permission Errors**
   ```bash
   # Fix file permissions
   sudo chown -R filebeat:filebeat /path/to/your/data/
   ```

2. **Configuration Errors**
   ```bash
   # Test configuration
   sudo filebeat test config
   ```

3. **Connection Issues**
   ```bash
   # Test Elasticsearch connection
   python3 test_elasticsearch_connection.py
   ```

4. **Data Not Appearing**
   ```bash
   # Check Filebeat logs
   sudo journalctl -u filebeat --since "10 minutes ago"
   ```

### Debug Commands
```bash
# Force Filebeat to reprocess files
sudo systemctl stop filebeat
sudo rm -f /var/lib/filebeat/registry/filebeat/log.json
sudo systemctl start filebeat

# Check what files Filebeat is monitoring
sudo cat /var/lib/filebeat/registry/filebeat/log.json | jq '.[]'
```

## Server Information

- **Elasticsearch**: `https://172.18.18.20:9200`
- **Kibana**: `http://172.18.18.20:5601`
- **Write Credentials**: `filebeat-dragonos:KUX4hkxjwp9qhu2wjx`
- **Read Credentials**: `vinson:ERC8mkm1ngf@anf0uwc`

## Success Criteria

✅ **Integration is successful when:**
- Filebeat service is running without errors
- Data appears in Kibana with correct device identification
- No authentication errors in Filebeat logs
- Data is searchable and properly formatted
- Continuous data flow without interruption

## Support

For issues or questions:
1. Check the main guide: `../elasticsearch_integration_guide.md`
2. Review Filebeat logs: `sudo journalctl -u filebeat -f`
3. Test connection: `python3 test_elasticsearch_connection.py`
4. Monitor integration: `./monitor_elasticsearch_integration.sh`
