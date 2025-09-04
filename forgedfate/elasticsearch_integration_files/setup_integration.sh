#!/bin/bash
# Elasticsearch Integration Setup Script
# Run this script to set up Elasticsearch integration for your application

set -e

# Configuration variables - CUSTOMIZE THESE FOR YOUR APPLICATION
APP_NAME="your-app-name"                    # Replace with your application name
DEVICE_NAME="your-device-name"              # Replace with your device identifier
LOG_DIRECTORY="/path/to/your/app/logs"      # Replace with your log directory
DATA_DIRECTORY="/path/to/your/app/data"     # Replace with your data directory

# Elasticsearch configuration
ES_HOST="https://172.18.18.20:9200"
ES_USERNAME="filebeat-dragonos"
ES_PASSWORD="KUX4hkxjwp9qhu2wjx"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Elasticsearch Integration Setup${NC}"
echo "=================================="
echo "App Name: $APP_NAME"
echo "Device Name: $DEVICE_NAME"
echo "Elasticsearch: $ES_HOST"
echo ""

# Function to print status
print_status() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ $1${NC}"
    else
        echo -e "${RED}❌ $1${NC}"
        exit 1
    fi
}

# Check if running as root for system configuration
check_root() {
    if [ "$EUID" -ne 0 ]; then
        echo -e "${YELLOW}⚠️  Some operations require sudo privileges${NC}"
    fi
}

# Install required packages
install_dependencies() {
    echo -e "${BLUE}📦 Installing dependencies...${NC}"
    
    # Update package list
    sudo apt update
    print_status "Package list updated"
    
    # Install Filebeat if not present
    if ! command -v filebeat &> /dev/null; then
        echo "Installing Filebeat..."
        wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add -
        echo "deb https://artifacts.elastic.co/packages/7.x/apt stable main" | sudo tee /etc/apt/sources.list.d/elastic-7.x.list
        sudo apt update
        sudo apt install -y filebeat
        print_status "Filebeat installed"
    else
        echo -e "${GREEN}✅ Filebeat already installed${NC}"
    fi
    
    # Install Python dependencies
    if ! python3 -c "import requests" &> /dev/null; then
        echo "Installing Python requests..."
        pip3 install requests
        print_status "Python requests installed"
    else
        echo -e "${GREEN}✅ Python requests already installed${NC}"
    fi
}

# Test Elasticsearch connection
test_connection() {
    echo -e "${BLUE}🔧 Testing Elasticsearch connection...${NC}"
    
    python3 test_elasticsearch_connection.py \
        --es-hosts "$ES_HOST" \
        --username "$ES_USERNAME" \
        --password "$ES_PASSWORD" \
        --device-name "$DEVICE_NAME" \
        --app-name "$APP_NAME"
    
    print_status "Elasticsearch connection test"
}

# Configure Filebeat
configure_filebeat() {
    echo -e "${BLUE}⚙️  Configuring Filebeat...${NC}"
    
    # Backup existing configuration
    if [ -f /etc/filebeat/filebeat.yml ]; then
        sudo cp /etc/filebeat/filebeat.yml /etc/filebeat/filebeat.yml.backup.$(date +%Y%m%d-%H%M%S)
        print_status "Existing configuration backed up"
    fi
    
    # Create new configuration from template
    sed -e "s/YOUR_APP_VERSION/1.0/g" \
        -e "s/YOUR_APP_LOGTYPE/${APP_NAME}_logs/g" \
        -e "s/YOUR_DEVICE_NAME/$DEVICE_NAME/g" \
        -e "s|/path/to/your/app/logs/\*\.log|$LOG_DIRECTORY/*.log|g" \
        -e "s|/path/to/your/app/data/\*\.json|$DATA_DIRECTORY/*.json|g" \
        -e "s/your-app-logs/$APP_NAME-logs/g" \
        filebeat_config_template.yml | sudo tee /etc/filebeat/filebeat.yml > /dev/null
    
    print_status "Filebeat configuration created"
    
    # Test configuration
    sudo filebeat test config
    print_status "Filebeat configuration validated"
    
    # Test Elasticsearch output
    sudo filebeat test output
    print_status "Elasticsearch output test"
}

# Start services
start_services() {
    echo -e "${BLUE}🚀 Starting services...${NC}"
    
    # Enable and start Filebeat
    sudo systemctl enable filebeat
    sudo systemctl start filebeat
    print_status "Filebeat service started"
    
    # Check service status
    sleep 5
    if sudo systemctl is-active --quiet filebeat; then
        echo -e "${GREEN}✅ Filebeat is running${NC}"
    else
        echo -e "${RED}❌ Filebeat failed to start${NC}"
        echo "Check logs with: sudo journalctl -u filebeat -f"
        exit 1
    fi
}

# Create monitoring script
create_monitoring_script() {
    echo -e "${BLUE}📊 Creating monitoring script...${NC}"
    
    cat > monitor_elasticsearch_integration.sh << EOF
#!/bin/bash
# Monitor Elasticsearch Integration for $APP_NAME

echo "🔍 Elasticsearch Integration Status for $APP_NAME"
echo "================================================"

# Check Filebeat status
echo "📡 Filebeat Service:"
sudo systemctl status filebeat --no-pager -l

echo ""
echo "📋 Recent Filebeat Logs:"
sudo journalctl -u filebeat --since "10 minutes ago" --no-pager | tail -20

echo ""
echo "📊 Filebeat Registry (tracked files):"
sudo cat /var/lib/filebeat/registry/filebeat/log.json | grep -o '"source":"[^"]*"' | head -10

echo ""
echo "🔧 Test Elasticsearch Connection:"
python3 test_elasticsearch_connection.py \\
    --es-hosts "$ES_HOST" \\
    --username "$ES_USERNAME" \\
    --password "$ES_PASSWORD" \\
    --device-name "$DEVICE_NAME" \\
    --app-name "$APP_NAME"
EOF

    chmod +x monitor_elasticsearch_integration.sh
    print_status "Monitoring script created"
}

# Main execution
main() {
    check_root
    install_dependencies
    test_connection
    configure_filebeat
    start_services
    create_monitoring_script
    
    echo ""
    echo -e "${GREEN}🎉 Elasticsearch Integration Setup Complete!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Place your application data files in: $LOG_DIRECTORY or $DATA_DIRECTORY"
    echo "2. Monitor integration with: ./monitor_elasticsearch_integration.sh"
    echo "3. View data in Kibana: http://172.18.18.20:5601 (login: vinson:ERC8mkm1ngf@anf0uwc)"
    echo "4. Search for your data with: device_name:\"$DEVICE_NAME\" OR app_name:\"$APP_NAME\""
    echo ""
    echo "Files created:"
    echo "- /etc/filebeat/filebeat.yml (Filebeat configuration)"
    echo "- monitor_elasticsearch_integration.sh (monitoring script)"
    echo ""
    echo "Useful commands:"
    echo "- Check Filebeat status: sudo systemctl status filebeat"
    echo "- View Filebeat logs: sudo journalctl -u filebeat -f"
    echo "- Restart Filebeat: sudo systemctl restart filebeat"
}

# Run main function
main "$@"
