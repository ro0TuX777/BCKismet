#!/usr/bin/env python3
"""
ForgedFate Kismet Bulk Upload Tool
Uploads all collected Kismet logs to Elasticsearch in bulk
"""

import argparse
import asyncio
import json
import logging
import os
import sqlite3
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

try:
    from elasticsearch import Elasticsearch
    from elasticsearch.helpers import bulk
except ImportError:
    print("Error: elasticsearch library not found. Install with: pip install elasticsearch")
    sys.exit(1)

class KismetBulkUploader:
    """Bulk upload all Kismet logs to Elasticsearch"""
    
    def __init__(self, es_hosts: str, username: str = "", password: str = "", 
                 index_prefix: str = "kismet", device_name: str = "unknown"):
        self.es_hosts = es_hosts
        self.username = username
        self.password = password
        self.index_prefix = index_prefix
        self.device_name = device_name
        self.es_client = None
        
        # Statistics
        self.stats = {
            'files_processed': 0,
            'documents_uploaded': 0,
            'errors': 0,
            'start_time': None,
            'data_types': {}
        }
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    def connect_elasticsearch(self) -> bool:
        """Connect to Elasticsearch"""
        try:
            auth = None
            if self.username and self.password:
                auth = (self.username, self.password)
            
            self.es_client = Elasticsearch(
                [self.es_hosts],
                basic_auth=auth,
                verify_certs=False,
                ssl_show_warn=False
            )
            
            # Test connection
            info = self.es_client.info()
            self.logger.info(f"Connected to Elasticsearch: {info['version']['number']}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect to Elasticsearch: {e}")
            return False
    
    def discover_log_files(self, log_directory: str = ".") -> Dict[str, List[str]]:
        """Discover all Kismet log files"""
        log_files = {
            'kismetdb': [],
            'json': [],
            'pcap': [],
            'other': []
        }
        
        search_paths = [
            log_directory,
            "/opt/kismet/logs",
            "~/.kismet",
            "./logs"
        ]
        
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
                
                # Find PCAP files
                for pcap_file in path.glob("*.pcap*"):
                    log_files['pcap'].append(str(pcap_file))
        
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
                    cursor.execute(f"SELECT * FROM {table} LIMIT 1000")  # Limit for bulk upload
                    rows = cursor.fetchall()
                    
                    for row in rows:
                        doc = {
                            '@timestamp': datetime.utcnow().isoformat(),
                            'source_file': os.path.basename(db_path),
                            'source_table': table,
                            'device_name': self.device_name,
                            'data_type': 'kismetdb'
                        }
                        
                        # Add all columns as fields
                        for key in row.keys():
                            value = row[key]
                            if value is not None:
                                # Handle JSON fields
                                if isinstance(value, str) and value.startswith('{'):
                                    try:
                                        doc[key] = json.loads(value)
                                    except:
                                        doc[key] = value
                                else:
                                    doc[key] = value
                        
                        documents.append(doc)
                    
                    self.stats['data_types'][f'kismetdb_{table}'] = len(rows)
                    
                except Exception as e:
                    self.logger.warning(f"Error processing table {table}: {e}")
            
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error processing kismetdb file {db_path}: {e}")
            self.stats['errors'] += 1
        
        return documents
    
    def process_json_file(self, json_path: str) -> List[Dict]:
        """Process JSON log files"""
        documents = []
        
        try:
            with open(json_path, 'r') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        data = json.loads(line)
                        
                        doc = {
                            '@timestamp': datetime.utcnow().isoformat(),
                            'source_file': os.path.basename(json_path),
                            'line_number': line_num,
                            'device_name': self.device_name,
                            'data_type': 'json_log'
                        }
                        
                        # Merge the JSON data
                        doc.update(data)
                        documents.append(doc)
                        
                    except json.JSONDecodeError as e:
                        self.logger.warning(f"Invalid JSON at line {line_num} in {json_path}: {e}")
            
            self.stats['data_types']['json_logs'] = len(documents)
            
        except Exception as e:
            self.logger.error(f"Error processing JSON file {json_path}: {e}")
            self.stats['errors'] += 1
        
        return documents
    
    def upload_documents(self, documents: List[Dict], data_type: str) -> bool:
        """Upload documents to Elasticsearch"""
        if not documents:
            return True
        
        try:
            # Create index name with date
            date_str = datetime.now().strftime("%Y.%m.%d")
            index_name = f"{self.index_prefix}-{data_type}-{date_str}"
            
            # Prepare documents for bulk upload
            actions = []
            for doc in documents:
                action = {
                    "_index": index_name,
                    "_source": doc
                }
                actions.append(action)
            
            # Bulk upload
            success_count, failed_items = bulk(
                self.es_client,
                actions,
                chunk_size=500,
                request_timeout=60
            )
            
            self.logger.info(f"Uploaded {success_count} documents to {index_name}")
            self.stats['documents_uploaded'] += success_count
            
            if failed_items:
                self.logger.warning(f"Failed to upload {len(failed_items)} documents")
                self.stats['errors'] += len(failed_items)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error uploading documents: {e}")
            self.stats['errors'] += 1
            return False
    
    def run_bulk_upload(self, log_directory: str = ".") -> Dict:
        """Run the complete bulk upload process"""
        self.stats['start_time'] = time.time()
        
        self.logger.info("🚀 Starting ForgedFate Kismet Bulk Upload...")
        
        # Connect to Elasticsearch
        if not self.connect_elasticsearch():
            return self.stats
        
        # Discover log files
        log_files = self.discover_log_files(log_directory)
        
        # Process each file type
        for kismet_file in log_files['kismetdb']:
            self.logger.info(f"Processing kismetdb file: {kismet_file}")
            documents = self.process_kismetdb_file(kismet_file)
            if documents:
                self.upload_documents(documents, 'kismetdb')
            self.stats['files_processed'] += 1
        
        for json_file in log_files['json']:
            self.logger.info(f"Processing JSON file: {json_file}")
            documents = self.process_json_file(json_file)
            if documents:
                self.upload_documents(documents, 'json')
            self.stats['files_processed'] += 1
        
        # Print final statistics
        runtime = time.time() - self.stats['start_time']
        self.logger.info("🎉 Bulk upload complete!")
        self.logger.info(f"Files processed: {self.stats['files_processed']}")
        self.logger.info(f"Documents uploaded: {self.stats['documents_uploaded']}")
        self.logger.info(f"Errors: {self.stats['errors']}")
        self.logger.info(f"Runtime: {runtime:.1f} seconds")
        
        return self.stats

def main():
    parser = argparse.ArgumentParser(description="ForgedFate Kismet Bulk Upload Tool")
    parser.add_argument("--es-hosts", required=True, help="Elasticsearch hosts")
    parser.add_argument("--es-username", help="Elasticsearch username")
    parser.add_argument("--es-password", help="Elasticsearch password")
    parser.add_argument("--index-prefix", default="kismet", help="Index prefix")
    parser.add_argument("--device-name", default="unknown", help="Device name")
    parser.add_argument("--log-directory", default=".", help="Directory to search for logs")
    
    args = parser.parse_args()
    
    uploader = KismetBulkUploader(
        es_hosts=args.es_hosts,
        username=args.es_username,
        password=args.es_password,
        index_prefix=args.index_prefix,
        device_name=args.device_name
    )
    
    stats = uploader.run_bulk_upload(args.log_directory)
    
    if stats['errors'] > 0:
        sys.exit(1)

if __name__ == "__main__":
    main()
