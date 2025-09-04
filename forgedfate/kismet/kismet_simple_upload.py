#!/usr/bin/env python3
"""
Simple Kismet Elasticsearch Upload Tool
Bypasses connection test issues by using direct HTTP requests
"""

import argparse
import json
import logging
import os
import sqlite3
import sys
import time
import requests
import base64
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# Disable SSL warnings
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class SimpleKismetUploader:
    """Simple uploader using direct HTTP requests"""
    
    def __init__(self, es_hosts: str, username: str = "", password: str = "", 
                 index_prefix: str = "kismet", device_name: str = "unknown"):
        self.es_hosts = es_hosts.rstrip('/')
        self.username = username
        self.password = password
        self.index_prefix = index_prefix
        self.device_name = device_name
        
        # Statistics
        self.stats = {
            'files_processed': 0,
            'documents_uploaded': 0,
            'errors': 0,
            'start_time': None
        }
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Setup authentication header
        self.headers = {'Content-Type': 'application/json'}
        if username and password:
            auth_string = base64.b64encode(f"{username}:{password}".encode()).decode()
            self.headers['Authorization'] = f'Basic {auth_string}'
    
    def upload_document(self, index_name: str, document: Dict) -> bool:
        """Upload a single document using HTTP POST"""
        try:
            url = f"{self.es_hosts}/{index_name}/_doc"
            response = requests.post(
                url,
                headers=self.headers,
                json=document,
                verify=False,
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                self.logger.debug(f"Document uploaded to {index_name}")
                return True
            else:
                self.logger.warning(f"Upload failed: {response.status_code} - {response.text[:100]}")
                return False
                
        except Exception as e:
            self.logger.error(f"Upload error: {e}")
            return False
    
    def bulk_upload_documents(self, index_name: str, documents: List[Dict]) -> int:
        """Upload multiple documents using bulk API"""
        if not documents:
            return 0
        
        try:
            # Prepare bulk request body
            bulk_body = ""
            for doc in documents:
                # Index action
                action = {"index": {"_index": index_name}}
                bulk_body += json.dumps(action) + "\n"
                bulk_body += json.dumps(doc) + "\n"
            
            url = f"{self.es_hosts}/_bulk"
            response = requests.post(
                url,
                headers={'Content-Type': 'application/x-ndjson', **{k:v for k,v in self.headers.items() if k != 'Content-Type'}},
                data=bulk_body,
                verify=False,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                success_count = 0
                error_count = 0
                errors = []

                for item in result.get('items', []):
                    if 'index' in item:
                        if item['index'].get('status') in [200, 201]:
                            success_count += 1
                        else:
                            error_count += 1
                            error_info = item['index'].get('error', {})
                            if error_info:
                                errors.append(f"{error_info.get('type', 'unknown')}: {error_info.get('reason', 'unknown')}")

                if success_count > 0:
                    self.logger.info(f"✅ Bulk uploaded {success_count}/{len(documents)} documents to {index_name}")
                    return success_count
                else:
                    self.logger.warning(f"⚠️ Upload to {index_name}: {success_count} success, {error_count} errors")
                    if errors:
                        unique_errors = list(set(errors[:3]))  # Show first 3 unique errors
                        for error in unique_errors:
                            self.logger.warning(f"   Error: {error}")
                    return 0
            else:
                self.logger.error(f"Bulk upload failed: {response.status_code} - {response.text[:200]}")
                return 0
                
        except Exception as e:
            self.logger.error(f"Bulk upload error: {e}")
            return 0
    
    def discover_log_files(self, log_directory: str = ".") -> Dict[str, List[str]]:
        """Discover all Kismet log files"""
        log_files = {'kismetdb': [], 'json': []}
        
        search_paths = [log_directory, "/opt/kismet/logs", "~/.kismet", "./logs"]
        
        for search_path in search_paths:
            path = Path(search_path).expanduser()
            if path.exists():
                self.logger.info(f"Searching for logs in: {path}")
                
                # Find .kismet files
                for kismet_file in path.glob("*.kismet"):
                    log_files['kismetdb'].append(str(kismet_file))
                
                # Find JSON files
                for json_file in path.glob("*.json"):
                    if any(x in json_file.name.lower() for x in ['kismet', 'device', 'bluetooth', 'wifi']):
                        log_files['json'].append(str(json_file))
        
        # Log discovery results
        for log_type, files in log_files.items():
            if files:
                self.logger.info(f"Found {len(files)} {log_type} files")
                for file in files[:3]:  # Show first 3
                    self.logger.info(f"  - {file}")
                if len(files) > 3:
                    self.logger.info(f"  ... and {len(files) - 3} more")
        
        return log_files
    
    def process_kismetdb_file(self, db_path: str) -> List[Dict]:
        """Extract data from .kismet database file"""
        documents = []
        
        try:
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            self.logger.info(f"Processing {len(tables)} tables from {db_path}")
            
            for table in tables:
                try:
                    cursor.execute(f"SELECT * FROM {table} LIMIT 100")  # Limit for testing
                    rows = cursor.fetchall()
                    
                    for row in rows:
                        doc = {
                            '@timestamp': datetime.now().isoformat(),
                            'source_file': os.path.basename(db_path),
                            'source_table': table,
                            'device_name': self.device_name,
                            'data_type': 'kismetdb'
                        }
                        
                        # Add all columns as fields
                        for key in row.keys():
                            value = row[key]
                            if value is not None:
                                # Handle binary data
                                if isinstance(value, bytes):
                                    try:
                                        # Try to decode as UTF-8 string
                                        doc[key] = value.decode('utf-8')
                                    except:
                                        # If that fails, convert to base64
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
                        
                        documents.append(doc)
                    
                    if rows:
                        self.logger.info(f"Extracted {len(rows)} records from table {table}")
                    
                except Exception as e:
                    self.logger.warning(f"Error processing table {table}: {e}")
            
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error processing kismetdb file {db_path}: {e}")
            self.stats['errors'] += 1
        
        return documents
    
    def test_connection(self) -> bool:
        """Test connection without triggering cluster info"""
        try:
            # Simple test - try to get server info
            url = f"{self.es_hosts}/"
            response = requests.get(
                url,
                headers=self.headers,
                verify=False,
                timeout=10
            )
            
            if response.status_code == 403:
                self.logger.info("✅ Connection successful (403 expected for write-only user)")
                return True
            elif response.status_code == 200:
                self.logger.info("✅ Connection successful")
                return True
            else:
                self.logger.error(f"Connection failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False
    
    def run_upload(self, log_directory: str = ".") -> Dict:
        """Run the complete upload process"""
        self.stats['start_time'] = time.time()
        
        self.logger.info("🚀 Starting Simple Kismet Upload...")
        
        # Test connection
        if not self.test_connection():
            self.logger.error("❌ Connection test failed")
            return self.stats
        
        # Discover log files
        log_files = self.discover_log_files(log_directory)
        
        if not any(log_files.values()):
            self.logger.warning("No Kismet log files found")
            return self.stats
        
        # Try different index patterns
        date_str = datetime.now().strftime("%Y.%m.%d")
        index_patterns = [
            f"filebeat-7.17.0-{date_str}-000001",
            f"filebeat-{date_str}",
            f"{self.index_prefix}-{date_str}",
            f"logstash-{date_str}"
        ]
        
        # Process kismetdb files
        for kismet_file in log_files['kismetdb']:
            self.logger.info(f"Processing kismetdb file: {kismet_file}")
            documents = self.process_kismetdb_file(kismet_file)
            
            if documents:
                # Try uploading to different indices
                uploaded = False
                for index_name in index_patterns:
                    self.logger.info(f"Attempting upload to: {index_name}")

                    # First try a single document to test
                    if documents:
                        test_doc = documents[0]
                        single_success = self.upload_document(index_name, test_doc)
                        if single_success:
                            self.logger.info(f"✅ Single document test successful for {index_name}")
                            # Now try bulk upload
                            success_count = self.bulk_upload_documents(index_name, documents)
                            if success_count > 0:
                                self.stats['documents_uploaded'] += success_count
                                uploaded = True
                                break
                        else:
                            self.logger.warning(f"❌ Single document test failed for {index_name}")
                            continue
                
                if not uploaded:
                    self.logger.error("Failed to upload to any index")
                    self.stats['errors'] += 1
            
            self.stats['files_processed'] += 1
        
        # Print final statistics
        runtime = time.time() - self.stats['start_time']
        self.logger.info("🎉 Upload complete!")
        self.logger.info(f"Files processed: {self.stats['files_processed']}")
        self.logger.info(f"Documents uploaded: {self.stats['documents_uploaded']}")
        self.logger.info(f"Errors: {self.stats['errors']}")
        self.logger.info(f"Runtime: {runtime:.1f} seconds")
        
        return self.stats

def main():
    parser = argparse.ArgumentParser(description="Simple Kismet Elasticsearch Upload Tool")
    parser.add_argument("--es-hosts", required=True, help="Elasticsearch hosts")
    parser.add_argument("--es-username", help="Elasticsearch username")
    parser.add_argument("--es-password", help="Elasticsearch password")
    parser.add_argument("--index-prefix", default="kismet", help="Index prefix")
    parser.add_argument("--device-name", default="unknown", help="Device name")
    parser.add_argument("--log-directory", default=".", help="Directory to search for logs")
    
    args = parser.parse_args()
    
    uploader = SimpleKismetUploader(
        es_hosts=args.es_hosts,
        username=args.es_username,
        password=args.es_password,
        index_prefix=args.index_prefix,
        device_name=args.device_name
    )
    
    stats = uploader.run_upload(args.log_directory)
    
    if stats['errors'] > 0:
        sys.exit(1)

if __name__ == "__main__":
    main()
