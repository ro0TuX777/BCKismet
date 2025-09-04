#!/usr/bin/env python3
"""
Convert Kismet database to JSON format for Filebeat processing
"""

import json
import sqlite3
import sys
import os
import base64
from datetime import datetime
from pathlib import Path

def convert_kismet_to_json(db_path, output_path, device_name="dragonos-laptop"):
    """Convert Kismet database to JSON lines format"""
    
    print(f"Converting {db_path} to {output_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        print(f"Found {len(tables)} tables: {', '.join(tables)}")
        
        with open(output_path, 'w') as f:
            total_records = 0
            
            for table in tables:
                try:
                    cursor.execute(f"SELECT * FROM {table}")
                    rows = cursor.fetchall()
                    
                    for row in rows:
                        doc = {
                            '@timestamp': datetime.now().isoformat(),
                            'source_file': os.path.basename(db_path),
                            'source_table': table,
                            'device_name': device_name,
                            'data_type': 'kismetdb',
                            'log_type': 'kismet'
                        }
                        
                        # Add all columns as fields
                        for key in row.keys():
                            value = row[key]
                            if value is not None:
                                # Handle binary data
                                if isinstance(value, bytes):
                                    try:
                                        doc[key] = value.decode('utf-8')
                                    except:
                                        doc[key] = base64.b64encode(value).decode('ascii')
                                        doc[f"{key}_type"] = "base64_encoded"
                                # Handle JSON fields
                                elif isinstance(value, str) and value.startswith('{'):
                                    try:
                                        doc[key] = json.loads(value)
                                    except:
                                        doc[key] = value
                                else:
                                    doc[key] = value
                        
                        # Write as JSON line
                        f.write(json.dumps(doc) + '\n')
                        total_records += 1
                    
                    if rows:
                        print(f"Processed {len(rows)} records from table {table}")
                
                except Exception as e:
                    print(f"Error processing table {table}: {e}")
            
            print(f"Total records written: {total_records}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error converting database: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 kismet_to_json.py <kismet_db_file> [output_file] [device_name]")
        sys.exit(1)
    
    db_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else f"{db_path}.json"
    device_name = sys.argv[3] if len(sys.argv) > 3 else "dragonos-laptop"
    
    if not os.path.exists(db_path):
        print(f"Error: Database file {db_path} not found")
        sys.exit(1)
    
    success = convert_kismet_to_json(db_path, output_path, device_name)
    
    if success:
        print(f"✅ Conversion successful!")
        print(f"📄 Output file: {output_path}")
        print(f"📊 File size: {os.path.getsize(output_path)} bytes")
        print(f"🚀 Ready for Filebeat processing")
    else:
        print("❌ Conversion failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
