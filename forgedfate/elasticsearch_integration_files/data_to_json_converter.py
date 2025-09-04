#!/usr/bin/env python3
"""
Generic Data to JSON Converter for Elasticsearch Integration
Converts various data sources (databases, logs, etc.) to JSON format suitable for Filebeat/Elasticsearch
"""

import json
import sqlite3
import sys
import os
import base64
import argparse
from datetime import datetime
from pathlib import Path

class DataToJsonConverter:
    """Generic converter for various data sources"""
    
    def __init__(self, device_name="unknown-device", app_name="generic-app"):
        self.device_name = device_name
        self.app_name = app_name
    
    def convert_sqlite_database(self, db_path, output_path):
        """Convert SQLite database to JSON lines format"""
        
        print(f"Converting SQLite database: {db_path}")
        
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
                                'device_name': self.device_name,
                                'app_name': self.app_name,
                                'data_type': 'database',
                                'log_type': f'{self.app_name}_db'
                            }
                            
                            # Add all columns as fields
                            for key in row.keys():
                                value = row[key]
                                if value is not None:
                                    doc[key] = self._convert_value(value, key)
                            
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
    
    def convert_log_file(self, log_path, output_path, log_format="auto"):
        """Convert log file to JSON lines format"""
        
        print(f"Converting log file: {log_path}")
        
        try:
            with open(log_path, 'r') as infile, open(output_path, 'w') as outfile:
                total_records = 0
                
                for line_num, line in enumerate(infile, 1):
                    line = line.strip()
                    if not line:
                        continue
                    
                    doc = {
                        '@timestamp': datetime.now().isoformat(),
                        'source_file': os.path.basename(log_path),
                        'line_number': line_num,
                        'device_name': self.device_name,
                        'app_name': self.app_name,
                        'data_type': 'log',
                        'log_type': f'{self.app_name}_log'
                    }
                    
                    # Try to parse as JSON first
                    if log_format == "json" or (log_format == "auto" and line.startswith('{')):
                        try:
                            parsed = json.loads(line)
                            doc.update(parsed)
                        except json.JSONDecodeError:
                            doc['raw_message'] = line
                    else:
                        doc['raw_message'] = line
                    
                    outfile.write(json.dumps(doc) + '\n')
                    total_records += 1
                
                print(f"Total records written: {total_records}")
            
            return True
            
        except Exception as e:
            print(f"Error converting log file: {e}")
            return False
    
    def convert_csv_file(self, csv_path, output_path):
        """Convert CSV file to JSON lines format"""
        
        print(f"Converting CSV file: {csv_path}")
        
        try:
            import csv
            
            with open(csv_path, 'r') as csvfile, open(output_path, 'w') as outfile:
                reader = csv.DictReader(csvfile)
                total_records = 0
                
                for row_num, row in enumerate(reader, 1):
                    doc = {
                        '@timestamp': datetime.now().isoformat(),
                        'source_file': os.path.basename(csv_path),
                        'row_number': row_num,
                        'device_name': self.device_name,
                        'app_name': self.app_name,
                        'data_type': 'csv',
                        'log_type': f'{self.app_name}_csv'
                    }
                    
                    # Add CSV columns
                    for key, value in row.items():
                        if value:
                            doc[key] = self._convert_value(value, key)
                    
                    outfile.write(json.dumps(doc) + '\n')
                    total_records += 1
                
                print(f"Total records written: {total_records}")
            
            return True
            
        except Exception as e:
            print(f"Error converting CSV file: {e}")
            return False
    
    def _convert_value(self, value, key):
        """Convert value to appropriate type for JSON serialization"""
        
        # Handle binary data
        if isinstance(value, bytes):
            try:
                return value.decode('utf-8')
            except:
                return base64.b64encode(value).decode('ascii')
        
        # Handle JSON strings
        if isinstance(value, str) and value.startswith('{'):
            try:
                return json.loads(value)
            except:
                return value
        
        # Handle numeric strings
        if isinstance(value, str):
            # Try to convert to number if it looks like one
            if value.isdigit():
                return int(value)
            try:
                return float(value)
            except:
                pass
        
        return value

def main():
    parser = argparse.ArgumentParser(description="Convert various data sources to JSON for Elasticsearch")
    parser.add_argument("input_file", help="Input file path")
    parser.add_argument("output_file", help="Output JSON file path")
    parser.add_argument("--device-name", default="unknown-device", help="Device name identifier")
    parser.add_argument("--app-name", default="generic-app", help="Application name")
    parser.add_argument("--format", choices=["auto", "sqlite", "log", "json", "csv"], default="auto", 
                       help="Input format (auto-detect by default)")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input_file):
        print(f"Error: Input file {args.input_file} not found")
        sys.exit(1)
    
    converter = DataToJsonConverter(args.device_name, args.app_name)
    
    # Auto-detect format if not specified
    format_type = args.format
    if format_type == "auto":
        if args.input_file.endswith(('.db', '.sqlite', '.sqlite3')):
            format_type = "sqlite"
        elif args.input_file.endswith('.csv'):
            format_type = "csv"
        elif args.input_file.endswith(('.json', '.jsonl')):
            format_type = "json"
        else:
            format_type = "log"
    
    # Convert based on format
    success = False
    if format_type == "sqlite":
        success = converter.convert_sqlite_database(args.input_file, args.output_file)
    elif format_type in ["log", "json"]:
        success = converter.convert_log_file(args.input_file, args.output_file, format_type)
    elif format_type == "csv":
        success = converter.convert_csv_file(args.input_file, args.output_file)
    
    if success:
        print(f"✅ Conversion successful!")
        print(f"📄 Output file: {args.output_file}")
        print(f"📊 File size: {os.path.getsize(args.output_file)} bytes")
        print(f"🚀 Ready for Filebeat processing")
    else:
        print("❌ Conversion failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
