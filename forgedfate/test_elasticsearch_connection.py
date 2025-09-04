#!/usr/bin/env python3
"""
Direct Elasticsearch Connection Test
Bypasses the non-functional Kismet UI "Test Connection" buttons
"""

import sys
import json
import time
from datetime import datetime

try:
    from elasticsearch import Elasticsearch
    from elasticsearch.helpers import bulk
except ImportError:
    print("❌ Error: elasticsearch library not found")
    print("Run: pip install elasticsearch")
    sys.exit(1)

def test_elasticsearch_connection(hosts, username, password, index_prefix="kismet"):
    """Test Elasticsearch connection and write permissions"""
    
    print("🔧 Testing Elasticsearch Connection...")
    print(f"Host: {hosts}")
    print(f"Username: {username}")
    print(f"Index Prefix: {index_prefix}")
    print("-" * 50)
    
    try:
        # Create Elasticsearch client
        auth = (username, password) if username and password else None
        
        es_client = Elasticsearch(
            [hosts],
            basic_auth=auth,
            verify_certs=False,
            ssl_show_warn=False
        )
        
        print("✅ Elasticsearch client created successfully")
        
        # Test 1: Basic connectivity (this might fail with 403 for write-only users)
        try:
            info = es_client.info()
            print(f"✅ Cluster info: {info['version']['number']}")
        except Exception as e:
            print(f"⚠️  Cluster info failed (expected for write-only users): {e}")
            print("   This is normal for write-only accounts")
        
        # Test 2: Write permission test
        test_index = f"{index_prefix}-connection-test"
        test_doc = {
            '@timestamp': datetime.utcnow().isoformat(),
            'test_type': 'connection_test',
            'device_name': 'dragonos-laptop',
            'message': 'Kismet connection test from Python',
            'source': 'test_elasticsearch_connection.py'
        }
        
        print(f"🧪 Testing write permissions to index: {test_index}")
        
        result = es_client.index(index=test_index, document=test_doc)
        print(f"✅ Document uploaded successfully!")
        print(f"   Index: {result['_index']}")
        print(f"   Document ID: {result['_id']}")
        print(f"   Result: {result['result']}")
        
        # Test 3: Search test (might fail with read restrictions)
        try:
            search_result = es_client.search(
                index=test_index,
                body={"query": {"match_all": {}}, "size": 1}
            )
            print(f"✅ Search test successful: {search_result['hits']['total']['value']} documents found")
        except Exception as e:
            print(f"⚠️  Search test failed (expected for write-only users): {e}")
        
        # Test 4: Bulk upload test
        print("🧪 Testing bulk upload...")
        
        bulk_docs = []
        for i in range(3):
            doc = {
                '_index': test_index,
                '_source': {
                    '@timestamp': datetime.utcnow().isoformat(),
                    'test_type': 'bulk_test',
                    'device_name': 'dragonos-laptop',
                    'message': f'Bulk test document {i+1}',
                    'sequence': i+1
                }
            }
            bulk_docs.append(doc)
        
        success_count, failed_items = bulk(es_client, bulk_docs)
        print(f"✅ Bulk upload successful: {success_count} documents uploaded")
        
        if failed_items:
            print(f"⚠️  Failed items: {len(failed_items)}")
        
        print("\n🎉 Connection test completed successfully!")
        print("✅ Elasticsearch is ready for Kismet data upload")
        
        return True
        
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        print("\n🔧 Troubleshooting suggestions:")
        print("1. Check if Elasticsearch is running")
        print("2. Verify the host and port are correct")
        print("3. Check username and password")
        print("4. Verify network connectivity")
        return False

def test_tcp_connection(host, port):
    """Test TCP connectivity (what the TCP Test button should do)"""
    import socket
    
    print(f"🔧 Testing TCP Connection to {host}:{port}...")
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            print(f"✅ TCP connection to {host}:{port} successful")
            return True
        else:
            print(f"❌ TCP connection to {host}:{port} failed")
            return False
            
    except Exception as e:
        print(f"❌ TCP connection error: {e}")
        return False

def main():
    print("🚀 Kismet Connection Test Tool")
    print("=" * 50)
    
    # Test configurations
    configs = [
        {
            'name': 'Elasticsearch (filebeat-dragonos)',
            'type': 'elasticsearch',
            'hosts': 'https://172.18.18.20:9200',
            'username': 'filebeat-dragonos',
            'password': 'KUX4hkxjwp9qhu2wjx'
        },
        {
            'name': 'Elasticsearch (vinson)',
            'type': 'elasticsearch', 
            'hosts': 'https://172.18.18.20:9200',
            'username': 'vinson',
            'password': 'ERC8mkm1ngf@anf0uwc'
        },
        {
            'name': 'TCP Connection Test',
            'type': 'tcp',
            'host': '172.18.18.20',
            'port': 8685
        }
    ]
    
    for config in configs:
        print(f"\n📋 Testing: {config['name']}")
        print("-" * 30)
        
        if config['type'] == 'elasticsearch':
            success = test_elasticsearch_connection(
                config['hosts'],
                config['username'], 
                config['password']
            )
        elif config['type'] == 'tcp':
            success = test_tcp_connection(config['host'], config['port'])
        
        if success:
            print(f"✅ {config['name']}: PASSED")
        else:
            print(f"❌ {config['name']}: FAILED")
        
        print()

if __name__ == "__main__":
    main()
