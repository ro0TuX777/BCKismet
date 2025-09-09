#!/usr/bin/env python3
"""
Kismet Bluetooth Device Logger
Creates bluetooth.devices.json files in the format expected by Filebeat
"""

import requests
import json
import time
import os
from datetime import datetime
from pathlib import Path
import argparse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class KismetBluetoothLogger:
    def __init__(self, kismet_host="localhost", kismet_port=2501, log_dir="/opt/kismet/logs", update_interval=30):
        self.kismet_host = kismet_host
        self.kismet_port = kismet_port
        self.log_dir = Path(log_dir)
        self.update_interval = update_interval
        self.session_dir = None
        self.bluetooth_file = None
        
    def create_session_directory(self):
        """Create a new session directory for this run"""
        timestamp = datetime.now().strftime("%Y.%m.%d-%H%M%S")
        session_name = f"Kismet-{timestamp}-1"
        self.session_dir = self.log_dir / session_name
        self.session_dir.mkdir(parents=True, exist_ok=True)
        self.bluetooth_file = self.session_dir / "bluetooth.devices.json"
        logger.info(f"Created session directory: {self.session_dir}")
        
    def normalize_numeric_arrays(self, obj):
        """Recursively normalize numeric arrays to ensure consistent types"""
        if isinstance(obj, dict):
            normalized = {}
            for key, value in obj.items():
                if key.endswith('_vec') and isinstance(value, list):
                    # Convert all numeric values to float for consistency
                    normalized[key] = [float(x) if isinstance(x, (int, float)) else x for x in value]
                elif isinstance(value, list):
                    # Also check if it's a list that might contain mixed types
                    if all(isinstance(x, (int, float)) for x in value):
                        normalized[key] = [float(x) for x in value]
                    else:
                        normalized[key] = [self.normalize_numeric_arrays(item) for item in value]
                else:
                    normalized[key] = self.normalize_numeric_arrays(value)
            return normalized
        elif isinstance(obj, list):
            return [self.normalize_numeric_arrays(item) for item in obj]
        else:
            return obj

    def get_bluetooth_devices(self):
        """Fetch bluetooth devices from Kismet API"""
        try:
            # Get all devices with authentication
            url = f"http://{self.kismet_host}:{self.kismet_port}/devices/views/all/devices.json"
            auth = ('kismet', 'P@ssw0rd!')
            response = requests.get(url, auth=auth, timeout=10)
            response.raise_for_status()

            all_devices = response.json()
            bluetooth_devices = []

            # Filter for bluetooth devices (PHY ID 3 is Bluetooth)
            for device in all_devices:
                if device.get('kismet.device.base.phyname') == 'Bluetooth':
                    # Normalize the device data to fix type conflicts
                    normalized_device = self.normalize_numeric_arrays(device)

                    # Create a simplified device record
                    bt_device = {
                        'timestamp': datetime.now().isoformat(),
                        'mac_address': device.get('kismet.device.base.macaddr', ''),
                        'device_name': device.get('kismet.device.base.name', ''),
                        'manufacturer': device.get('kismet.device.base.manuf', ''),
                        'first_seen': device.get('kismet.device.base.first_time', 0),
                        'last_seen': device.get('kismet.device.base.last_time', 0),
                        'signal_dbm': device.get('kismet.device.base.signal', {}).get('kismet.common.signal.last_signal', 0),
                        'packets': device.get('kismet.device.base.packets.total', 0),
                        'data_size': device.get('kismet.device.base.datasize', 0),
                        'device_type': device.get('kismet.device.base.type', ''),
                        'phy_name': device.get('kismet.device.base.phyname', ''),
                        'raw_device': normalized_device  # Include normalized device data for analysis
                    }
                    bluetooth_devices.append(bt_device)

            return bluetooth_devices
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch devices from Kismet: {e}")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            return []
            
    def write_devices_to_file(self, devices):
        """Write devices to NDJSON file"""
        if not devices:
            logger.debug("No bluetooth devices to write")
            return
            
        try:
            with open(self.bluetooth_file, 'a') as f:
                for device in devices:
                    json.dump(device, f)
                    f.write('\n')
            logger.info(f"Wrote {len(devices)} bluetooth devices to {self.bluetooth_file}")
        except Exception as e:
            logger.error(f"Failed to write devices to file: {e}")
            
    def run(self):
        """Main monitoring loop"""
        logger.info(f"Starting Kismet Bluetooth Logger")
        logger.info(f"Kismet: {self.kismet_host}:{self.kismet_port}")
        logger.info(f"Log directory: {self.log_dir}")
        logger.info(f"Update interval: {self.update_interval}s")
        
        # Create session directory
        self.create_session_directory()
        
        try:
            while True:
                devices = self.get_bluetooth_devices()
                if devices:
                    self.write_devices_to_file(devices)
                else:
                    logger.debug("No bluetooth devices found")
                    
                time.sleep(self.update_interval)
                
        except KeyboardInterrupt:
            logger.info("Shutting down...")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")

def main():
    parser = argparse.ArgumentParser(description="Kismet Bluetooth Device Logger")
    parser.add_argument("--kismet-host", default="localhost", help="Kismet host")
    parser.add_argument("--kismet-port", type=int, default=2501, help="Kismet port")
    parser.add_argument("--log-dir", default="/opt/kismet/logs", help="Log directory")
    parser.add_argument("--interval", type=int, default=30, help="Update interval in seconds")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        
    logger = KismetBluetoothLogger(
        kismet_host=args.kismet_host,
        kismet_port=args.kismet_port,
        log_dir=args.log_dir,
        update_interval=args.interval
    )
    
    logger.run()

if __name__ == "__main__":
    main()
