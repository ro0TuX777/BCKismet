#!/usr/bin/env python3
"""
Test Elasticsearch Connection and Upload Capability
Use this script to verify your application can connect and send data to Elasticsearch
"""

import sys
import json
import time
import argparse
from datetime import datetime

try:
    import requests
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
except ImportError:
    print("❌ Error: requests library not found")
    print("Run: pip install requests")
    sys.exit(1)

import base64

class ElasticsearchTester:
    """Test Elasticsearch connectivity and data upload"""
    
    def __init__(self, es_hosts, username="", password="", device_name="test-device", app_name="test-app"):
        self.es_hosts = es_hosts.rstrip('/')
        self.username = username
        self.password = password
        self.device_name = device_name
        self.app_name = app_name
        
        # Setup authentication header
        self.headers = {'Content-Type': 'application/json'}
        if username and password:
            auth_string = base64.b64encode(f"{username}:{password}".encode()).decode()
            self.headers['Authorization'] = f'Basic {auth_string}'
    
    def test_connection(self):
        """Test basic connectivity to Elasticsearch"""
        print("🔧 Testing Elasticsearch Connection...")
        print(f"Host: {self.es_hosts}")
        print(f"Username: {self.username}")
        print("-" * 50)
        
        try:
            url = f"{self.es_hosts}/"
            response = requests.get(
                url,
                headers=self.headers,
                verify=False,
                timeout=10
            )
            
            if response.status_code == 403:
                print("✅ Connection successful (403 expected for write-only user)")
                return True
            elif response.status_code == 200:
                print("✅ Connection successful")
                try:
                    info = response.json()
                    print(f"   Elasticsearch version: {info.get('version', {}).get('number', 'unknown')}")
                except:
                    pass
                return True
            elif response.status_code == 401:
                print("❌ Authentication failed - check username/password")
                return False
            else:
                print(f"❌ Connection failed: HTTP {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                return False
                
        except Exception as e:
            print(f"❌ Connection error: {e}")
            return False
    
    def test_single_document_upload(self, index_name):
        """Test uploading a single document"""
        print(f"🧪 Testing single document upload to: {index_name}")
        
        test_doc = {
            '@timestamp': datetime.now().isoformat(),
            'device_name': self.device_name,
            'app_name': self.app_name,
            'test_type': 'connection_test',
            'message': f'Test document from {self.app_name}',
            'test_data': {
                'number': 42,
                'text': 'Hello Elasticsearch',
                'boolean': True
            }
        }
        
        try:
            url = f"{self.es_hosts}/{index_name}/_doc"
            response = requests.post(
                url,
                headers=self.headers,
                json=test_doc,
                verify=False,
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                result = response.json()
                print(f"✅ Document uploaded successfully!")
                print(f"   Index: {result.get('_index')}")
                print(f"   Document ID: {result.get('_id')}")
                print(f"   Result: {result.get('result')}")
                return True
            else:
                print(f"❌ Upload failed: HTTP {response.status_code}")
                print(f"   Response: {response.text[:300]}")
                return False
                
        except Exception as e:
            print(f"❌ Upload error: {e}")
            return False
    
    def test_bulk_upload(self, index_name, num_docs=5):
        """Test bulk document upload"""
        print(f"🧪 Testing bulk upload of {num_docs} documents to: {index_name}")
        
        # Prepare bulk request body
        bulk_body = ""
        for i in range(num_docs):
            # Index action
            action = {"index": {"_index": index_name}}
            bulk_body += json.dumps(action) + "\n"
            
            # Document
            doc = {
                '@timestamp': datetime.now().isoformat(),
                'device_name': self.device_name,
                'app_name': self.app_name,
                'test_type': 'bulk_test',
                'sequence': i + 1,
                'message': f'Bulk test document {i + 1}',
                'data': f'test_data_{i + 1}'
            }
            bulk_body += json.dumps(doc) + "\n"
        
        try:
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
                
                for item in result.get('items', []):
                    if 'index' in item and item['index'].get('status') in [200, 201]:
                        success_count += 1
                    else:
                        error_count += 1
                
                print(f"✅ Bulk upload completed!")
                print(f"   Successful: {success_count}/{num_docs}")
                print(f"   Errors: {error_count}")
                
                if error_count > 0:
                    print("   Sample errors:")
                    for item in result.get('items', [])[:3]:
                        if 'index' in item and item['index'].get('status') not in [200, 201]:
                            error = item['index'].get('error', {})
                            print(f"     - {error.get('type', 'unknown')}: {error.get('reason', 'unknown')}")
                
                return success_count > 0
            else:
                print(f"❌ Bulk upload failed: HTTP {response.status_code}")
                print(f"   Response: {response.text[:300]}")
                return False
                
        except Exception as e:
            print(f"❌ Bulk upload error: {e}")
            return False
    
    def run_comprehensive_test(self):
        """Run all tests"""
        print("🚀 Starting Comprehensive Elasticsearch Test")
        print("=" * 60)
        
        # Test 1: Basic connection
        if not self.test_connection():
            print("\n❌ Connection test failed - stopping here")
            return False
        
        print("\n" + "=" * 60)
        
        # Test 2: Try different index patterns
        test_indices = [
            f"test-{self.app_name}-{datetime.now().strftime('%Y.%m.%d')}",
            f"filebeat-{datetime.now().strftime('%Y.%m.%d')}",
            f"logstash-{datetime.now().strftime('%Y.%m.%d')}",
            f"{self.app_name}-logs-{datetime.now().strftime('%Y.%m.%d')}"
        ]
        
        successful_index = None
        for index_name in test_indices:
            print(f"\n📋 Testing index: {index_name}")
            if self.test_single_document_upload(index_name):
                successful_index = index_name
                break
            print(f"   ❌ Failed to upload to {index_name}")
        
        if not successful_index:
            print("\n❌ All index tests failed")
            return False
        
        print(f"\n✅ Found working index: {successful_index}")
        
        # Test 3: Bulk upload
        print("\n" + "=" * 60)
        bulk_success = self.test_bulk_upload(successful_index)
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 Test Summary:")
        print(f"✅ Connection: Success")
        print(f"✅ Single upload: Success ({successful_index})")
        print(f"{'✅' if bulk_success else '❌'} Bulk upload: {'Success' if bulk_success else 'Failed'}")
        
        if bulk_success:
            print("\n🎉 All tests passed! Your application can send data to Elasticsearch.")
            print(f"💡 Use index pattern: {successful_index.replace(datetime.now().strftime('%Y.%m.%d'), 'YYYY.MM.DD')}")
        else:
            print("\n⚠️  Basic upload works, but bulk upload failed. Check permissions.")
        
        return True

def main():
    parser = argparse.ArgumentParser(description="Test Elasticsearch Connection and Upload")
    parser.add_argument("--es-hosts", default="https://172.18.18.20:9200", help="Elasticsearch hosts")
    parser.add_argument("--username", default="filebeat-dragonos", help="Elasticsearch username")
    parser.add_argument("--password", default="KUX4hkxjwp9qhu2wjx", help="Elasticsearch password")
    parser.add_argument("--device-name", default="test-device", help="Device name for testing")
    parser.add_argument("--app-name", default="test-app", help="Application name for testing")
    
    args = parser.parse_args()
    
    tester = ElasticsearchTester(
        es_hosts=args.es_hosts,
        username=args.username,
        password=args.password,
        device_name=args.device_name,
        app_name=args.app_name
    )
    
    success = tester.run_comprehensive_test()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
