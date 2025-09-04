#!/bin/bash
# Quick Setup Script for Kismet Filebeat Integration
# One-command setup for DragonOS with Elasticsearch 9.1.3

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║              ForgedFate Kismet Quick Setup                  ║"
echo "║                 Elasticsearch 9.1.3                        ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check if running as root
if [[ $EUID -ne 0 ]]; then
    echo -e "${RED}This script must be run as root (use sudo)${NC}"
    exit 1
fi

echo -e "${BLUE}Starting automated Filebeat setup...${NC}"

# Check if the comprehensive setup script exists
if [[ -f "setup_kismet_filebeat_9.1.3.sh" ]]; then
    echo -e "${GREEN}Found comprehensive setup script, running...${NC}"
    ./setup_kismet_filebeat_9.1.3.sh
else
    echo -e "${YELLOW}Comprehensive setup script not found, running basic setup...${NC}"
    
    # Basic setup steps
    echo -e "${BLUE}Installing Filebeat 9.1.3...${NC}"
    curl -L -O https://artifacts.elastic.co/downloads/beats/filebeat/filebeat-9.1.3-amd64.deb
    dpkg -i filebeat-9.1.3-amd64.deb || apt-get install -f -y
    
    echo -e "${BLUE}Configuring permissions...${NC}"
    groupadd kismet 2>/dev/null || true
    usermod -a -G kismet filebeat
    
    if [[ -d "/opt/kismet/logs" ]]; then
        chgrp -R kismet /opt/kismet/logs
        chmod -R g+r /opt/kismet/logs
    fi
    
    echo -e "${BLUE}Installing configuration...${NC}"
    if [[ -f "filebeat-kismet-complete.yml" ]]; then
        cp /etc/filebeat/filebeat.yml /etc/filebeat/filebeat.yml.backup.$(date +%Y%m%d_%H%M%S) 2>/dev/null || true
        cp filebeat-kismet-complete.yml /etc/filebeat/filebeat.yml
        chown root:root /etc/filebeat/filebeat.yml
        chmod 600 /etc/filebeat/filebeat.yml
    else
        echo -e "${RED}Configuration file not found!${NC}"
        exit 1
    fi
    
    echo -e "${BLUE}Starting Filebeat...${NC}"
    systemctl enable filebeat
    systemctl restart filebeat
fi

echo -e "${GREEN}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                     Setup Complete!                         ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

echo -e "${BLUE}Next steps:${NC}"
echo "1. Start Kismet to generate logs:"
echo "   ${YELLOW}sudo kismet${NC}"
echo ""
echo "2. Check Filebeat status:"
echo "   ${YELLOW}sudo systemctl status filebeat${NC}"
echo ""
echo "3. Monitor logs:"
echo "   ${YELLOW}sudo journalctl -u filebeat -f${NC}"
echo ""
echo "4. Verify data in Elasticsearch:"
echo "   ${YELLOW}curl -X GET \"https://172.18.18.20:9200/kismet-sdr/_search?size=1&pretty\" \\${NC}"
echo "   ${YELLOW}  -u \"filebeat-dragonos:KUX4hkxjwp9qhu2wjx\" -k${NC}"

echo -e "${GREEN}All Kismet log types (Bluetooth, WiFi, ADS-B, etc.) are now configured!${NC}"
