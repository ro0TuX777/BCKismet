# ForgedFate: Enhanced Kismet Wireless Intelligence Platform

[![License: GPL v2](https://img.shields.io/badge/License-GPL%20v2-blue.svg)](https://www.gnu.org/licenses/gpl-2.0)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Elasticsearch 8.x](https://img.shields.io/badge/elasticsearch-8.x-orange.svg)](https://www.elastic.co/)
[![Docker Ready](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)

ForgedFate is an enhanced version of the Kismet wireless network detector with powerful real-time data export capabilities, Elasticsearch integration, and improved security features for comprehensive wireless intelligence gathering.

## 🚀 Features

### Core Kismet Capabilities
- **Wireless Network Detection**: Comprehensive 802.11 (WiFi), Bluetooth, and other wireless protocol detection
- **Real-time Monitoring**: Live device tracking and analysis with GPS integration
- **Multi-Protocol Support**: WiFi, Bluetooth, Zigbee, LoRa, SDR platforms, and more
- **Hardware Support**: RTL8821AU, MediaTek MT7921, Ralink RT3070, U-Blox GPS, ADALM-PLUTO
- **Web Interface**: Modern web-based management and visualization

### Enhanced Export Capabilities
- **🔄 Real-time Data Export**: Stream device data to external systems via API
- **📊 Elasticsearch Integration**: Advanced search, analytics, and visualization
- **📡 Multiple Database Support**: PostgreSQL, InfluxDB, Elasticsearch
- **📨 MQTT Integration**: Publish data to MQTT brokers
- **💾 Offline Support**: Local SQLite buffering with store-and-forward
- **🔄 Filebeat Integration**: Automated log shipping and processing
- **🐳 Docker Ready**: Containerized deployment with security updates

### Enterprise Features
- **Scalable Architecture**: Multi-sensor deployment support
- **Role-based Access Control**: Secure data access management
- **TLS Encryption**: Secure data transmission
- **Batch Processing**: Historical data analysis capabilities
- **Real-time Dashboards**: Kibana integration for visualization

## 📋 Requirements

### System Requirements
- **OS**: Linux (Ubuntu 20.04+ recommended)
- **CPU**: Multi-core processor (4+ cores recommended)
- **Memory**: 8GB+ RAM for real-time processing
- **Storage**: SSD recommended for high I/O operations
- **Network**: Gigabit Ethernet for data transmission

### Software Dependencies
- **Python**: 3.8 or higher
- **Kismet**: Latest version with database support
- **Elasticsearch**: 8.x series
- **Filebeat**: 8.x series (optional)
- **Docker**: For containerized deployment (optional)

## 🛠️ Installation

### Quick Start

```bash
# Clone the repository
git clone https://github.com/forgedfate/forgedfate.git
cd forgedfate

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install ForgedFate
pip install -e .
```

### Development Installation

```bash
# Install with development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Run tests
pytest tests/
```

### Docker Installation

```bash
# Build Docker image
docker build -t forgedfate .

# Run with Docker Compose
docker-compose up -d
```

## ⚙️ Configuration

### Environment Variables

```bash
# Elasticsearch Configuration
export ES_HOSTS="https://your-elasticsearch:9200"
export ES_USERNAME="filebeat-dragonos"
export ES_PASSWORD="your-password"
export ES_INDEX_PREFIX="kismet"

# Kismet Configuration
export KISMET_HOST="localhost"
export KISMET_PORT="2501"
export KISMET_DEVICE_NAME="dragon-os-box"
export KISMET_LOG_DIR="/path/to/kismet/logs"

# Logging Configuration
export LOG_LEVEL="INFO"
export LOG_FILE="/var/log/forgedfate.log"
```

### Configuration File

Create `config.yml`:

```yaml
elasticsearch:
  hosts:
    - "https://your-elasticsearch:9200"
  username: "filebeat-dragonos"
  password: "your-password"
  index_prefix: "kismet"
  verify_certs: false

kismet:
  host: "localhost"
  port: 2501
  device_name: "dragon-os-box"
  log_directory: "/path/to/kismet/logs"
  data_sources:
    - "wlan0"
    - "hci0"
    - "gpsnmea:/dev/ttyACM0"

filebeat:
  enabled: true
  config_path: "/etc/filebeat/filebeat.yml"
  log_paths:
    - "/path/to/kismet/*.kismet"

logging:
  level: "INFO"
  file: "/var/log/forgedfate.log"
  structured: true

batch_size: 1000
max_workers: 4
```

## 🚀 Usage

### Bulk Upload

Upload existing Kismet data to Elasticsearch:

```bash
# Using command line arguments
forgedfate-bulk-upload \
  --es-hosts "https://your-elasticsearch:9200" \
  --es-username "filebeat-dragonos" \
  --es-password "your-password" \
  --device-name "dragon-os-box" \
  --log-directory "/path/to/kismet/logs"

# Using configuration file
forgedfate-bulk-upload --config config.yml

# Dry run (show what would be uploaded)
forgedfate-bulk-upload --config config.yml --dry-run --verbose
```

### Test Connection

Verify Elasticsearch connectivity:

```bash
forgedfate-test-connection \
  --es-hosts "https://your-elasticsearch:9200" \
  --es-username "filebeat-dragonos" \
  --es-password "your-password"
```

### Real-time Integration

#### 1. Start Kismet with Multi-Source Support

```bash
# Start Kismet with comprehensive logging
sudo kismet --log-types=kismetdb,json \
  --log-prefix=./ \
  --log-title=ForgedFate-$(date +%Y%m%d-%H%M%S) \
  -c wlan0,wlan1,hci0,gpsnmea:/dev/ttyACM0
```

#### 2. Configure Web UI Export

1. **Open Kismet Web Interface**: http://localhost:2501
2. **Navigate to**: Settings → API Configuration → Elasticsearch Export
3. **Configure Settings**:
   - **Elasticsearch Hosts**: `https://your-elasticsearch:9200`
   - **Username**: `filebeat-dragonos`
   - **Password**: `your-password`
   - **Index Prefix**: `kismet-realtime`
   - **Device Name**: `dragon-os-box`
4. **Test Connection**: Should show "Connection successful (write-only access confirmed)"
5. **Enable Export**: Toggle real-time export ON
6. **Monitor Status**: Watch export status indicator for live data flow

#### 3. Configure Filebeat (Optional)

```bash
# Configure Filebeat for automated log shipping
sudo systemctl start filebeat
sudo journalctl -u filebeat -f
```

## 📊 Data Visualization

### Kibana Dashboards

Access your data in Kibana:

1. **Open Kibana**: http://your-elasticsearch:5601
2. **Login**: Use your Elasticsearch credentials
3. **Create Index Pattern**: 
   - Pattern: `kismet-*`
   - Time field: `@timestamp`
4. **Explore Data**: Go to Discover and search

### Sample Queries

```bash
# Find all devices from a specific sensor
device_name:"dragon-os-box"

# WiFi access points with strong signals
source_type:"wifi" AND signal_strength:>-50

# Bluetooth devices detected in last hour
source_type:"bluetooth" AND @timestamp:[now-1h TO now]

# Devices with GPS coordinates
latitude:* AND longitude:*

# Real-time data from web UI export
_index:*kismet-realtime* AND device_name:"dragon-os-box"
```

## 🏗️ Architecture

```
[Wireless Devices] → [Kismet] → [Local Storage] → [Filebeat] → [Elasticsearch] → [Kibana]
                              ↘ [Real-time API] ↗
```

### Data Flow Modes

1. **Real-time Streaming**: Kismet Web UI → Direct API → Elasticsearch
2. **Batch Processing**: Kismet Files → Filebeat → Elasticsearch  
3. **Hybrid Mode**: Both real-time and batch with deduplication

### Components

- **Kismet**: Multi-protocol wireless packet capture and analysis
- **Elasticsearch**: Distributed search and analytics engine
- **Filebeat**: Log file monitoring and forwarding agent
- **Kibana**: Real-time dashboard and analysis interface
- **ForgedFate**: Integration layer and enhanced functionality

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/forgedfate

# Run specific test categories
pytest tests/unit/
pytest tests/integration/

# Test Elasticsearch connection
forgedfate-test-connection --config config.yml
```

## 📚 Documentation

- **[Technical Paper](ForgedFate_Kismet_Elasticsearch_Integration_Technical_Paper.md)**: Comprehensive system documentation
- **[Hardware Compatibility](docs/hardware-compatibility.md)**: Supported devices and drivers
- **[Deployment Guide](docs/deployment.md)**: Production deployment instructions
- **[API Reference](docs/api-reference.md)**: REST API documentation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Add tests for new functionality
- Update documentation as needed
- Use meaningful commit messages
- Ensure all tests pass before submitting

## 📄 License

This project is licensed under the GNU General Public License v2.0 - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Kismet Team**: For the excellent wireless detection framework
- **Elastic Team**: For the powerful search and analytics platform
- **Community Contributors**: For testing, feedback, and improvements
- **Security Researchers**: For responsible disclosure and improvements

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/forgedfate/forgedfate/issues)
- **Discussions**: [GitHub Discussions](https://github.com/forgedfate/forgedfate/discussions)
- **Documentation**: [Wiki](https://github.com/forgedfate/forgedfate/wiki)
- **Email**: dev@forgedfate.com

## 🗺️ Roadmap

- [ ] Machine Learning integration for anomaly detection
- [ ] Extended protocol support (LoRaWAN, Zigbee, Z-Wave)
- [ ] Cloud deployment templates (AWS, Azure, GCP)
- [ ] Mobile app for remote monitoring
- [ ] Advanced visualization dashboards
- [ ] Threat intelligence integration
- [ ] Automated reporting and alerting
