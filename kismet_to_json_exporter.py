#!/usr/bin/env python3
"""
Export Kismet database to JSON files for Filebeat ingestion
Exports WiFi and Bluetooth devices separately
"""

import sqlite3
import json
import os
from datetime import datetime
from pathlib import Path

class KismetJSONExporter:
    def __init__(self, kismet_db_path, output_dir="/home/dragos/rf-kit/logs/kismet"):
        self.db_path = kismet_db_path
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Extract session name from database filename
        db_name = Path(kismet_db_path).stem
        self.session_dir = self.output_dir / db_name
        self.session_dir.mkdir(parents=True, exist_ok=True)
        
    def connect_db(self):
        """Connect to Kismet database"""
        return sqlite3.connect(self.db_path)
    
    def export_devices(self):
        """Export all devices from Kismet database"""
        conn = self.connect_db()
        cursor = conn.cursor()
        
        # Get all devices
        cursor.execute("""
            SELECT devkey, phyname, devmac, strongest_signal,
                   min_lat, min_lon, max_lat, max_lon,
                   first_time, last_time, bytes_data, device
            FROM devices
        """)
        
        wifi_devices = []
        bluetooth_devices = []
        
        for row in cursor.fetchall():
            devkey, phyname, devmac, signal, min_lat, min_lon, max_lat, max_lon, \
            first_time, last_time, bytes_data, device_json = row

            # Calculate packets from device data
            packets = 0
            
            # Parse device JSON
            try:
                device_data = json.loads(device_json) if device_json else {}
            except:
                device_data = {}
            
            # Build common device record
            device_record = {
                "@timestamp": datetime.now().isoformat(),
                "timestamp": datetime.fromtimestamp(last_time).isoformat() if last_time else None,
                "first_seen": datetime.fromtimestamp(first_time).isoformat() if first_time else None,
                "last_seen": datetime.fromtimestamp(last_time).isoformat() if last_time else None,
                "device_key": devkey,
                "phy_name": phyname,
                "mac_address": devmac,
                "signal_dbm": signal,
                "packets": packets,
                "event": {
                    "kind": "signal",
                    "category": ["network"]
                },
                "raw_device": {
                    "kismet": {
                        "device": device_data
                    }
                }
            }
            
            # Add location if available
            if min_lat and min_lon:
                device_record["geo"] = {
                    "location": {
                        "lat": (min_lat + max_lat) / 2 if max_lat else min_lat,
                        "lon": (min_lon + max_lon) / 2 if max_lon else min_lon
                    }
                }
            
            # Extract device-specific fields
            if phyname == "IEEE802.11":
                # WiFi device
                device_record["device_type"] = "WiFi"
                
                # Extract SSID
                if "dot11.device" in device_data:
                    dot11 = device_data["dot11.device"]
                    if "dot11.device.last_beaconed_ssid" in dot11:
                        device_record["ssid"] = dot11["dot11.device.last_beaconed_ssid"]
                    if "dot11.device.num_associated_clients" in dot11:
                        device_record["associated_clients"] = dot11["dot11.device.num_associated_clients"]
                    if "dot11.device.client_map" in dot11:
                        device_record["client_count"] = len(dot11["dot11.device.client_map"])
                
                # Extract manufacturer
                if "kismet.device.base.manuf" in device_data:
                    device_record["manufacturer"] = device_data["kismet.device.base.manuf"]
                else:
                    device_record["manufacturer"] = "Unknown"
                
                # Extract device name
                if "kismet.device.base.name" in device_data:
                    device_record["device_name"] = device_data["kismet.device.base.name"]
                else:
                    device_record["device_name"] = ""
                
                wifi_devices.append(device_record)
                
            elif phyname == "Bluetooth":
                # Bluetooth device
                bt_type = "BTLE"  # Default
                
                if "bluetooth.device" in device_data:
                    bt_data = device_data["bluetooth.device"]
                    if "bluetooth.device.type" in bt_data:
                        bt_type = bt_data["bluetooth.device.type"]
                
                device_record["device_type"] = bt_type
                
                # Extract manufacturer
                if "kismet.device.base.manuf" in device_data:
                    device_record["manufacturer"] = device_data["kismet.device.base.manuf"]
                else:
                    device_record["manufacturer"] = "Unknown"
                
                # Extract device name
                if "kismet.device.base.name" in device_data:
                    device_record["device_name"] = device_data["kismet.device.base.name"]
                else:
                    device_record["device_name"] = ""
                
                bluetooth_devices.append(device_record)
        
        conn.close()
        
        # Write to JSON files
        wifi_file = self.session_dir / "wifi.devices.json"
        bluetooth_file = self.session_dir / "bluetooth.devices.json"
        
        with open(wifi_file, 'w') as f:
            for device in wifi_devices:
                f.write(json.dumps(device) + '\n')
        
        with open(bluetooth_file, 'w') as f:
            for device in bluetooth_devices:
                f.write(json.dumps(device) + '\n')
        
        print(f"✅ Exported {len(wifi_devices)} WiFi devices to {wifi_file}")
        print(f"✅ Exported {len(bluetooth_devices)} Bluetooth devices to {bluetooth_file}")
        
        return len(wifi_devices), len(bluetooth_devices)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python3 kismet_to_json_exporter.py <kismet_db_path>")
        sys.exit(1)
    
    db_path = sys.argv[1]
    
    if not os.path.exists(db_path):
        print(f"Error: Database file not found: {db_path}")
        sys.exit(1)
    
    exporter = KismetJSONExporter(db_path)
    wifi_count, bt_count = exporter.export_devices()
    
    print(f"\n📊 Total: {wifi_count} WiFi + {bt_count} Bluetooth = {wifi_count + bt_count} devices")

