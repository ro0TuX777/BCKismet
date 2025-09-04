# Elasticsearch Integration Guide

## Overview
This guide documents the complete process for sending application data to an Elasticsearch server, based on the successful Kismet integration. This approach can be adapted for any application that generates log files or database data.

## Prerequisites

### Server Information
- **Elasticsearch Server**: `172.18.18.20:9200` (HTTPS)
- **Kibana Interface**: `172.18.18.20:5601` (HTTP)
- **Write Credentials**: `filebeat-dragonos:KUX4hkxjwp9qhu2wjx`
- **Read Credentials**: `vinson:ERC8mkm1ngf@anf0uwc` (Kibana access)

### Required Software
```bash
# Install required packages
sudo apt update
sudo apt install filebeat python3-pip python3-venv

# Python dependencies
pip install requests sqlite3 json
```

## Method 1: Direct Upload (For Testing)

### Step 1: Create Python Virtual Environment
```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install requests elasticsearch
```

### Step 2: Test Connection
```bash
# Test basic connectivity
python3 -c "
import requests, base64
auth = base64.b64encode(b'filebeat-dragonos:KUX4hkxjwp9qhu2wjx').decode()
headers = {'Authorization': f'Basic {auth}', 'Content-Type': 'application/json'}
doc = {'test': 'connection', '@timestamp': '$(date -u +%Y-%m-%dT%H:%M:%S.%3NZ)', 'device_name': 'test-device'}
response = requests.post('https://172.18.18.20:9200/test-index/_doc', headers=headers, json=doc, verify=False)
print(f'Status: {response.status_code}')
"
```

### Step 3: Convert Application Data to JSON
Use the provided `data_to_json_converter.py` script to convert your application's data to JSON format suitable for Elasticsearch.

## Method 2: Filebeat Integration (Recommended for Production)

### Step 1: Install and Configure Filebeat

```bash
# Install Filebeat (if not already installed)
sudo apt install filebeat

# Backup existing configuration
sudo cp /etc/filebeat/filebeat.yml /etc/filebeat/filebeat.yml.backup
```

### Step 2: Configure Filebeat for Your Application

```yaml
# Add to /etc/filebeat/filebeat.yml
filebeat.inputs:
- close_inactive: 5m
  enabled: true
  fields:
    integration_tool: filebeat_app_integrator
    app_version: your_app_version
    log_type: your_app_logtype
    source_device: your-device-name
  fields_under_root: true
  id: your-app-logs
  index: your-app-logs
  parsers:
  - ndjson:
      target: ''
  paths:
  - /path/to/your/app/logs/*.log
  - /path/to/your/app/data/*.json
  scan_frequency: 10s
  type: filestream

# Elasticsearch output configuration
output.elasticsearch:
  hosts:
  - https://172.18.18.20:9200
  username: filebeat-dragonos
  password: KUX4hkxjwp9qhu2wjx
  ssl.certificate_authorities: []
  ssl.verification_mode: none

# Logging configuration
logging.level: info
logging.to_files: true
logging.files:
  path: /var/log/filebeat
  name: filebeat
  keepfiles: 7
  permissions: '0644'

# Template settings
setup.template.settings:
  index.number_of_shards: 1
  index.number_of_replicas: 0
```

### Step 3: Test and Start Filebeat

```bash
# Test configuration
sudo filebeat test config

# Test Elasticsearch connection
sudo filebeat test output

# Start Filebeat
sudo systemctl enable filebeat
sudo systemctl start filebeat

# Monitor logs
sudo journalctl -u filebeat -f
```

## Data Conversion Process

### For Database Applications (like Kismet)

1. **Extract data from database**:
   ```python
   # Use the provided database_to_json.py script
   python3 database_to_json.py your_database.db output.json your-device-name
   ```

2. **Place JSON file in monitored directory**:
   ```bash
   # Copy to Filebeat monitored path
   cp output.json /path/to/monitored/directory/
   ```

### For Log File Applications

1. **Ensure logs are in JSON format** (one JSON object per line)
2. **Place logs in monitored directory**
3. **Filebeat will automatically process** new files

## Verification

### Check Data in Kibana

1. **Access Kibana**: http://172.18.18.20:5601
2. **Login**: `vinson:ERC8mkm1ngf@anf0uwc`
3. **Go to Discover**
4. **Search for your data**:
   ```
   source_device:"your-device-name"
   log_type:"your_app_logtype"
   ```

### Monitor Filebeat Status

```bash
# Check Filebeat status
sudo systemctl status filebeat

# View recent logs
sudo journalctl -u filebeat --since "10 minutes ago"

# Check for errors
sudo journalctl -u filebeat --since "10 minutes ago" | grep -i error
```

## Troubleshooting

### Common Issues

1. **403 Forbidden Errors**:
   - User cannot create new indices
   - Solution: Use existing index patterns or get admin credentials

2. **Connection Refused**:
   - Check network connectivity
   - Verify Elasticsearch server is running
   - Check firewall settings

3. **Authentication Failures**:
   - Verify credentials are correct
   - Check user permissions in Elasticsearch

4. **Data Not Appearing**:
   - Check Filebeat logs for processing errors
   - Verify file permissions
   - Ensure JSON format is valid

### Debug Commands

```bash
# Test Elasticsearch connectivity
curl -k -u filebeat-dragonos:KUX4hkxjwp9qhu2wjx https://172.18.18.20:9200/

# Check Filebeat registry
sudo cat /var/lib/filebeat/registry/filebeat/log.json

# Force Filebeat to reprocess files
sudo systemctl stop filebeat
sudo rm -f /var/lib/filebeat/registry/filebeat/log.json
sudo systemctl start filebeat
```

## Security Considerations

1. **Use HTTPS** for Elasticsearch connections
2. **Store credentials securely** (consider using environment variables)
3. **Limit user permissions** to write-only for data sources
4. **Monitor access logs** for unauthorized access attempts
5. **Regularly rotate passwords**

## Performance Optimization

1. **Batch processing**: Use bulk uploads for large datasets
2. **Index management**: Use date-based indices for time-series data
3. **Resource monitoring**: Monitor Elasticsearch cluster health
4. **Data retention**: Implement index lifecycle management

## Adaptation for New Applications

1. **Copy the `elasticsearch_integration_files/` directory** to your new application
2. **Modify the configuration files** with your application-specific settings:
   - Update paths in Filebeat configuration
   - Change device names and log types
   - Adjust data conversion scripts for your data format
3. **Test the integration** using the provided test scripts
4. **Deploy and monitor** using the verification steps

## Files Included

- `data_to_json_converter.py`: Generic data conversion script
- `filebeat_config_template.yml`: Template Filebeat configuration
- `test_elasticsearch_connection.py`: Connection testing script
- `elasticsearch_integration_guide.md`: This guide

## Success Metrics

- ✅ Filebeat successfully connects to Elasticsearch
- ✅ Data appears in Kibana with correct device identification
- ✅ No authentication or permission errors in logs
- ✅ Data is searchable and properly formatted
- ✅ Continuous data flow without interruption
