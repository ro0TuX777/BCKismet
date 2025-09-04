#!/bin/bash
# ForgedFate Kismet Filebeat Setup Script for Elasticsearch 9.1.3
# Automatically installs and configures Filebeat for comprehensive Kismet integration

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration for Elasticsearch 9.1.3
FILEBEAT_VERSION="9.1.3"
FILEBEAT_DEB="filebeat-${FILEBEAT_VERSION}-amd64.deb"
FILEBEAT_URL="https://artifacts.elastic.co/downloads/beats/filebeat/${FILEBEAT_DEB}"
ELASTICSEARCH_HOST="https://172.18.18.20:9200"
ELASTICSEARCH_USER="filebeat-dragonos"
ELASTICSEARCH_PASS="KUX4hkxjwp9qhu2wjx"
ELASTICSEARCH_INDEX="kismet-sdr"

print_header() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║           ForgedFate Kismet Filebeat Setup 9.1.3           ║"
    echo "║        Comprehensive Kismet → Elasticsearch Integration     ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_root() {
    if [[ $EUID -ne 0 ]]; then
        print_error "This script must be run as root (use sudo)"
        exit 1
    fi
}

check_system() {
    print_step "Checking system requirements..."
    
    # Check if running on supported system
    if ! command -v apt-get &> /dev/null; then
        print_error "This script requires a Debian/Ubuntu system with apt-get"
        exit 1
    fi
    
    # Check if curl is available
    if ! command -v curl &> /dev/null; then
        print_step "Installing curl..."
        apt-get update -qq
        apt-get install -y curl
    fi
    
    # Check if python3 is available
    if ! command -v python3 &> /dev/null; then
        print_step "Installing Python 3..."
        apt-get install -y python3 python3-pip
    fi
    
    # Check if PyYAML is available
    if ! python3 -c "import yaml" &> /dev/null; then
        print_step "Installing PyYAML..."
        apt-get install -y python3-yaml
    fi
    
    print_success "System requirements satisfied"
}

install_filebeat() {
    print_step "Installing Filebeat ${FILEBEAT_VERSION}..."
    
    # Check if Filebeat is already installed
    if command -v filebeat &> /dev/null; then
        local installed_version=$(filebeat version | grep -oP 'version \K[0-9.]+' || echo "unknown")
        if [[ "$installed_version" == "$FILEBEAT_VERSION" ]]; then
            print_success "Filebeat ${FILEBEAT_VERSION} is already installed"
            return 0
        else
            print_warning "Different Filebeat version detected: $installed_version"
            print_step "Upgrading to version ${FILEBEAT_VERSION}..."
        fi
    fi
    
    # Download Filebeat
    print_step "Downloading Filebeat..."
    cd /tmp
    if [[ -f "$FILEBEAT_DEB" ]]; then
        print_step "Using existing download: $FILEBEAT_DEB"
    else
        curl -L -O "$FILEBEAT_URL"
    fi
    
    # Install Filebeat
    print_step "Installing Filebeat package..."
    dpkg -i "$FILEBEAT_DEB" || {
        print_step "Fixing dependencies..."
        apt-get install -f -y
    }
    
    # Enable but don't start yet
    systemctl enable filebeat
    
    print_success "Filebeat ${FILEBEAT_VERSION} installed successfully"
}

setup_permissions() {
    print_step "Setting up permissions for Kismet logs..."
    
    # Create kismet group if it doesn't exist
    if ! getent group kismet > /dev/null 2>&1; then
        groupadd kismet
        print_step "Created kismet group"
    fi
    
    # Add filebeat user to kismet group
    usermod -a -G kismet filebeat
    
    # Set up log directory permissions
    if [[ -d "/opt/kismet/logs" ]]; then
        chgrp -R kismet /opt/kismet/logs
        chmod -R g+r /opt/kismet/logs
        print_success "Permissions configured for /opt/kismet/logs"
    else
        print_warning "Kismet log directory not found at /opt/kismet/logs"
        print_warning "You may need to adjust permissions manually after running Kismet"
    fi
}

configure_filebeat() {
    print_step "Configuring Filebeat for comprehensive Kismet integration..."
    
    # Backup existing configuration
    if [[ -f "/etc/filebeat/filebeat.yml" ]]; then
        cp "/etc/filebeat/filebeat.yml" "/etc/filebeat/filebeat.yml.backup.$(date +%Y%m%d_%H%M%S)"
        print_step "Backed up existing Filebeat configuration"
    fi
    
    # Copy our comprehensive configuration
    if [[ -f "filebeat-kismet-complete.yml" ]]; then
        cp "filebeat-kismet-complete.yml" "/etc/filebeat/filebeat.yml"
        print_success "Installed comprehensive Kismet Filebeat configuration"
    else
        print_error "Configuration file filebeat-kismet-complete.yml not found"
        return 1
    fi
    
    # Set proper permissions
    chown root:root /etc/filebeat/filebeat.yml
    chmod 600 /etc/filebeat/filebeat.yml
    
    print_success "Filebeat configuration completed"
}

test_configuration() {
    print_step "Testing Filebeat configuration..."
    
    # Test configuration syntax
    if filebeat test config; then
        print_success "Configuration syntax is valid"
    else
        print_error "Configuration syntax test failed"
        return 1
    fi
    
    # Test Elasticsearch connectivity
    print_step "Testing Elasticsearch connectivity..."
    if filebeat test output; then
        print_success "Elasticsearch connectivity test passed"
    else
        print_warning "Elasticsearch connectivity test failed - check network and credentials"
        print_warning "This may be normal if Elasticsearch is not currently accessible"
    fi
}

start_filebeat() {
    print_step "Starting Filebeat service..."
    
    # Start and enable Filebeat
    systemctl restart filebeat
    systemctl enable filebeat
    
    # Wait a moment for startup
    sleep 3
    
    # Check status
    if systemctl is-active --quiet filebeat; then
        print_success "Filebeat is running successfully"
    else
        print_error "Filebeat failed to start"
        print_step "Checking logs..."
        journalctl -u filebeat --no-pager -n 10
        return 1
    fi
}

show_verification_steps() {
    echo -e "${GREEN}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                    Setup Complete!                          ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    echo -e "${BLUE}Verification Steps:${NC}"
    echo "1. Check Filebeat status:"
    echo "   ${YELLOW}sudo systemctl status filebeat${NC}"
    echo ""
    echo "2. Monitor Filebeat logs:"
    echo "   ${YELLOW}sudo journalctl -u filebeat -f${NC}"
    echo ""
    echo "3. Start Kismet to generate logs:"
    echo "   ${YELLOW}sudo kismet${NC}"
    echo ""
    echo "4. Verify data in Elasticsearch:"
    echo "   ${YELLOW}curl -X GET \"${ELASTICSEARCH_HOST}/_cat/indices/kismet-*?v\" \\${NC}"
    echo "   ${YELLOW}  -u \"${ELASTICSEARCH_USER}:${ELASTICSEARCH_PASS}\" \\${NC}"
    echo "   ${YELLOW}  -k${NC}"
    echo ""
    echo "5. Sample data query:"
    echo "   ${YELLOW}curl -X GET \"${ELASTICSEARCH_HOST}/${ELASTICSEARCH_INDEX}/_search?size=1&pretty\" \\${NC}"
    echo "   ${YELLOW}  -u \"${ELASTICSEARCH_USER}:${ELASTICSEARCH_PASS}\" \\${NC}"
    echo "   ${YELLOW}  -k${NC}"
    echo ""
    echo -e "${GREEN}Log Types Configured:${NC}"
    echo "  • General Devices (devices.json)"
    echo "  • Bluetooth Devices (bluetooth.devices.json)"
    echo "  • WiFi Devices (wifi.devices.json)"
    echo "  • Packet Data (packets.json)"
    echo "  • Alerts (alerts.json)"
    echo "  • ADS-B Devices (adsb.devices.json)"
    echo "  • RTL433 Devices (rtl433.devices.json)"
    echo "  • Zigbee Devices (zigbee.devices.json)"
    echo "  • Radiation Devices (radiation.devices.json)"
    echo "  • UAV/Drone Devices (uav.devices.json)"
    echo ""
    echo -e "${GREEN}All data will be indexed to: ${ELASTICSEARCH_INDEX}${NC}"
}

main() {
    print_header
    
    check_root
    check_system
    install_filebeat
    setup_permissions
    configure_filebeat
    test_configuration
    start_filebeat
    
    print_success "ForgedFate Kismet Filebeat setup completed successfully!"
    echo ""
    show_verification_steps
}

# Handle script arguments
case "${1:-}" in
    --help|-h)
        echo "ForgedFate Kismet Filebeat Setup Script for Elasticsearch 9.1.3"
        echo ""
        echo "Usage: $0 [options]"
        echo ""
        echo "Options:"
        echo "  --help, -h     Show this help message"
        echo "  --version      Show Filebeat version to install"
        echo ""
        echo "This script will:"
        echo "  1. Install Filebeat $FILEBEAT_VERSION"
        echo "  2. Set up permissions for Kismet log access"
        echo "  3. Configure comprehensive Kismet log ingestion"
        echo "  4. Test connectivity to Elasticsearch"
        echo "  5. Start and enable Filebeat service"
        echo ""
        echo "Elasticsearch Configuration:"
        echo "  Host: $ELASTICSEARCH_HOST"
        echo "  Index: $ELASTICSEARCH_INDEX"
        echo "  User: $ELASTICSEARCH_USER"
        echo ""
        exit 0
        ;;
    --version)
        echo "Filebeat version: $FILEBEAT_VERSION"
        echo "Elasticsearch host: $ELASTICSEARCH_HOST"
        echo "Target index: $ELASTICSEARCH_INDEX"
        exit 0
        ;;
    *)
        main "$@"
        ;;
esac
