#!/usr/bin/env python3
"""
Find where Kismet documents are actually being stored
"""

import requests
import json
import urllib3
from datetime import datetime, timedelta

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def find_kismet_documents():
    """Try to find where the 422 Kismet documents are stored"""
    
    # Configuration
    es_url = "https://172.18.18.20:9200"
    username = "filebeat-dragonos"
    password = "KUX4hkxjwp9qhu2wjx"
    
    print("=" * 60)
    print("SEARCHING FOR KISMET DOCUMENTS")
    print("=" * 60)
    
    # Possible index patterns where Kismet might be sending data
    index_patterns = [
        "kismet*",
        "kismet-*", 
        "*kismet*",
        "filebeat*",
        "*dragonos*",
        "*bluetooth*",
        "*wifi*",
        "*devices*",
        "_all"  # Search everything (if permissions allow)
    ]
    
    # Possible index names to test write access
    test_indices = [
        "kismet",
        "kismet-data", 
        "kismet-export",
        "kismet-devices",
        "kismet-bluetooth", 
        "kismet-wifi",
        "kismet-gps",
        "filebeat-kismet",
        "dragonos-laptop",
        "dragonos-kismet",
        f"kismet-{datetime.now().strftime('%Y.%m.%d')}",
        f"kismet-{datetime.now().strftime('%Y-%m-%d')}"
    ]
    
    print("1. Testing write access to possible indices...")
    successful_indices = []
    
    test_doc = {
        "@timestamp": datetime.now().isoformat(),
        "test": "document_search",
        "source_device": "dragonos-laptop",
        "kismet.device.type": "test_search"
    }
    
    for index in test_indices:
        try:
            response = requests.post(
                f"{es_url}/{index}/_doc",
                auth=(username, password),
                verify=False,
                timeout=5,
                json=test_doc
            )
            
            if response.status_code in [200, 201]:
                successful_indices.append(index)
                print(f"   ✅ Can write to: {index}")
            elif response.status_code == 403:
                print(f"   ❌ Access denied: {index}")
            elif response.status_code == 404:
                print(f"   ⚠️  Index doesn't exist: {index}")
            else:
                print(f"   ❓ Unknown response for {index}: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error testing {index}: {e}")
    
    print(f"\n2. Found {len(successful_indices)} writable indices:")
    for idx in successful_indices:
        print(f"   - {idx}")
    
    print("\n3. Testing HEAD requests to check index existence...")
    existing_indices = []
    
    for index in test_indices:
        try:
            response = requests.head(
                f"{es_url}/{index}",
                auth=(username, password),
                verify=False,
                timeout=5
            )
            
            if response.status_code == 200:
                existing_indices.append(index)
                print(f"   ✅ Index exists: {index}")
            elif response.status_code == 404:
                print(f"   ❌ Index not found: {index}")
            elif response.status_code == 403:
                print(f"   ❓ Access denied (might exist): {index}")
                
        except Exception as e:
            print(f"   ❌ Error checking {index}: {e}")
    
    print("\n4. Trying to search with different patterns...")
    
    # Try searching recent documents with different time ranges
    time_ranges = [
        "now-1h",  # Last hour
        "now-6h",  # Last 6 hours  
        "now-1d",  # Last day
        "now-7d"   # Last week
    ]
    
    for time_range in time_ranges:
        print(f"\n   Searching documents from {time_range}...")
        
        for pattern in ["kismet*", "*"]:
            try:
                search_query = {
                    "query": {
                        "bool": {
                            "must": [
                                {
                                    "range": {
                                        "@timestamp": {
                                            "gte": time_range
                                        }
                                    }
                                }
                            ],
                            "should": [
                                {"match": {"source_device": "dragonos-laptop"}},
                                {"match": {"device_name": "dragonos-laptop"}},
                                {"match": {"kismet.device.type": "*"}},
                                {"exists": {"field": "kismet"}}
                            ],
                            "minimum_should_match": 1
                        }
                    },
                    "size": 1,
                    "sort": [{"@timestamp": {"order": "desc"}}]
                }
                
                response = requests.post(
                    f"{es_url}/{pattern}/_search",
                    auth=(username, password),
                    verify=False,
                    timeout=10,
                    json=search_query
                )
                
                if response.status_code == 200:
                    result = response.json()
                    hits = result.get('hits', {}).get('hits', [])
                    total = result.get('hits', {}).get('total', {})
                    
                    if isinstance(total, dict):
                        count = total.get('value', 0)
                    else:
                        count = total
                        
                    if count > 0:
                        print(f"     ✅ Found {count} documents in {pattern}")
                        if hits:
                            doc = hits[0]
                            print(f"        Index: {doc['_index']}")
                            print(f"        Timestamp: {doc['_source'].get('@timestamp', 'unknown')}")
                            print(f"        Source: {doc['_source']}")
                            return doc['_index']  # Return the index where we found data
                    else:
                        print(f"     ❌ No documents found in {pattern}")
                        
                elif response.status_code == 403:
                    print(f"     ❌ Access denied to {pattern}")
                else:
                    print(f"     ❌ Error searching {pattern}: {response.status_code}")
                    
            except Exception as e:
                print(f"     ❌ Error searching {pattern}: {e}")
    
    print("\n" + "=" * 60)
    print("SEARCH COMPLETE")
    print("=" * 60)
    
    if successful_indices:
        print(f"\n✅ You can write to these indices: {', '.join(successful_indices)}")
        print("💡 Kismet should be configured to use one of these indices")
    else:
        print("\n❌ No writable indices found!")
        print("🔧 Check Kismet configuration and Elasticsearch permissions")
    
    return successful_indices

if __name__ == "__main__":
    print("🔍 Searching for the missing 422 Kismet documents...")
    print("   This will test multiple index patterns and names")
    print()
    
    indices = find_kismet_documents()
    
    if indices:
        print(f"\n🎯 RECOMMENDATION:")
        print(f"   Configure Kismet to use index: {indices[0]}")
        print(f"   This is where your documents should go!")
    else:
        print(f"\n💥 No accessible indices found")
        print(f"   Check Elasticsearch permissions and Kismet configuration")
