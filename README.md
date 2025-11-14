# BCKismet

**Enhanced Kismet Wireless Network Detection Tool by Blue Cloak**

BCKismet is a customized version of Kismet with enhanced GPS capabilities, custom branding, and improved data source management for wireless network detection and analysis.

## 🚀 Features

- **GPS Integration**: Full GPSD integration with real-time location tracking
- **Enhanced Web Interface**: Custom "Blue Cloak" branding with improved UX
- **Data Source Management**: Fixed "Add Data Sources" functionality for easy WiFi/Bluetooth device addition
- **Multi-Interface Support**: Support for USB WiFi adapters, internal WiFi, and Bluetooth devices
- **Desktop Integration**: Desktop launcher with automatic terminal management
- **Configuration Profiles**: Multiple configuration profiles (minimal and full working configs)

## 📋 Quick Start

### Prerequisites
- Linux system with Kismet installed
- GPSD for GPS functionality
- WiFi adapters and/or Bluetooth devices for capture

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/ro0TuX777/BCKismet.git
   cd BCKismet
   ```

2. Make scripts executable:
   ```bash
   chmod +x run-kismet.sh
   chmod +x create-desktop-icon.sh
   ```

3. Run BCKismet:
   ```bash
   # For basic functionality (GPS + Web UI)
   ./run-kismet.sh

   # For full WiFi capture (requires root)
   sudo ./run-kismet.sh
   ```

4. Access the web interface:
   - Open browser to http://localhost:2502
   - Set up admin credentials on first run
   - Navigate to Data Sources to add WiFi/Bluetooth interfaces

## 🔧 Configuration Files

- `forgedfate/kismet_minimal.conf` - Minimal configuration for testing
- `forgedfate/kismet_working.conf` - Full configuration with all features
- `run-kismet.sh` - Command-line launcher script
- `forgedkismet-wrapper.sh` - Desktop launcher wrapper

## 📊 Supported Interfaces

### WiFi Interfaces
- USB WiFi adapters (TP-Link, Realtek, MediaTek chipsets)
- Internal WiFi cards
- Monitor mode capable devices

### Bluetooth Interfaces
- Internal Bluetooth adapters
- USB Bluetooth dongles
- HCI-compatible devices

### GPS
- GPSD integration (recommended)
- Serial GPS devices
- USB GPS modules

## 🎯 Key Improvements

### Fixed Issues
- ✅ GPS driver configuration (now uses proper GPSD integration)
- ✅ Helper binary path corrections
- ✅ Data source driver type specifications
- ✅ Web interface branding and functionality
- ✅ Plugin directory error resolution

### Enhanced Features
- 🔧 Improved "Add Data Sources" functionality
- 🎨 Custom Blue Cloak branding
- 📱 Desktop integration with launcher
- 📍 Real-time GPS tracking
- 🔍 Enhanced interface detection

## 📖 Documentation

- `QUICK_START_GUIDE.md` - Comprehensive setup and usage guide
- `DESKTOP_ICON_CREATION_GUIDE.md` - Desktop integration instructions
- `GITHUB_WORKFLOW_GUIDE.md` - Complete GitHub workflow for developers
- `GITHUB_QUICK_REFERENCE.md` - Quick commands and safety checks
- Configuration examples and troubleshooting tips included

## 🤝 Contributing

This project is based on the Kismet wireless network detector. Contributions and improvements are welcome.

**For Developers**: Please review `GITHUB_WORKFLOW_GUIDE.md` before making contributions to ensure proper workflow and prevent large file issues.

## 📄 License

Based on Kismet - see original Kismet licensing terms.

## 🔗 Links

- Original Kismet: https://www.kismetwireless.net/
- Documentation: See included guides and configuration files

---

**Powered by Blue Cloak** 🛡️
