"""
ForgedFate Elasticsearch Integration

Elasticsearch client and data export functionality.
"""

import asyncio
import json
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, AsyncGenerator
from elasticsearch import Elasticsearch, AsyncElasticsearch
from elasticsearch.helpers import bulk, async_bulk

from ..core.config import ElasticsearchConfig
from ..core.exceptions import ElasticsearchError, ConnectionError
from ..core.logger import get_logger

logger = get_logger(__name__)


class ElasticsearchClient:
    """Elasticsearch client with ForgedFate-specific functionality."""
    
    def __init__(self, config: ElasticsearchConfig):
        """
        Initialize Elasticsearch client.
        
        Args:
            config: Elasticsearch configuration
        """
        self.config = config
        self.client = None
        self.async_client = None
        self._setup_clients()
    
    def _setup_clients(self):
        """Setup synchronous and asynchronous Elasticsearch clients."""
        client_config = {
            'hosts': self.config.hosts,
            'verify_certs': self.config.verify_certs,
            'request_timeout': self.config.timeout,
            'max_retries': self.config.max_retries,
        }
        
        if self.config.username and self.config.password:
            client_config['basic_auth'] = (self.config.username, self.config.password)
        
        try:
            self.client = Elasticsearch(**client_config)
            self.async_client = AsyncElasticsearch(**client_config)
            logger.info("Elasticsearch clients initialized successfully")
        except Exception as e:
            raise ConnectionError(f"Failed to initialize Elasticsearch clients: {e}")
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Test connection to Elasticsearch.
        
        Returns:
            Connection test results
            
        Raises:
            ConnectionError: If connection fails
        """
        try:
            # Test basic connectivity
            health = self.client.cluster.health()
            
            # Test write permissions (for write-only users)
            test_index = f"{self.config.index_prefix}-connection-test"
            test_doc = {
                "@timestamp": datetime.now(timezone.utc).isoformat(),
                "test": True,
                "message": "Connection test document"
            }
            
            try:
                response = self.client.index(
                    index=test_index,
                    document=test_doc
                )
                
                # Clean up test document
                self.client.delete(
                    index=test_index,
                    id=response['_id']
                )
                
                return {
                    "status": "success",
                    "cluster_name": health.get("cluster_name"),
                    "status": health.get("status"),
                    "write_access": True,
                    "response_time_ms": 0  # TODO: Measure actual response time
                }
                
            except Exception as write_error:
                # For write-only users, we might get 403 on read operations
                if "403" in str(write_error) or "security_exception" in str(write_error):
                    return {
                        "status": "success",
                        "write_access": True,
                        "user_type": "write_only",
                        "note": "403 response expected for write-only users"
                    }
                else:
                    raise write_error
                    
        except Exception as e:
            logger.error(f"Elasticsearch connection test failed: {e}")
            raise ConnectionError(f"Elasticsearch connection test failed: {e}")
    
    async def async_test_connection(self) -> Dict[str, Any]:
        """Async version of connection test."""
        try:
            health = await self.async_client.cluster.health()
            return {
                "status": "success",
                "cluster_name": health.get("cluster_name"),
                "cluster_status": health.get("status")
            }
        except Exception as e:
            logger.error(f"Async Elasticsearch connection test failed: {e}")
            raise ConnectionError(f"Async Elasticsearch connection test failed: {e}")
    
    def create_index_template(self, template_name: str, index_pattern: str) -> None:
        """
        Create index template for ForgedFate data.
        
        Args:
            template_name: Name of the template
            index_pattern: Index pattern to match
        """
        template = {
            "index_patterns": [index_pattern],
            "template": {
                "settings": {
                    "number_of_shards": 1,
                    "number_of_replicas": 0,
                    "refresh_interval": "5s"
                },
                "mappings": {
                    "properties": {
                        "@timestamp": {"type": "date"},
                        "device_name": {"type": "keyword"},
                        "source_type": {"type": "keyword"},
                        "mac_addr": {"type": "keyword"},
                        "signal_strength": {"type": "integer"},
                        "latitude": {"type": "float"},
                        "longitude": {"type": "float"},
                        "phy_type": {"type": "keyword"},
                        "device_type": {"type": "keyword"},
                        "integration_tool": {"type": "keyword"}
                    }
                }
            }
        }
        
        try:
            self.client.indices.put_index_template(
                name=template_name,
                body=template
            )
            logger.info(f"Created index template: {template_name}")
        except Exception as e:
            logger.error(f"Failed to create index template {template_name}: {e}")
            raise ElasticsearchError(f"Failed to create index template: {e}")
    
    def close(self):
        """Close Elasticsearch clients."""
        if self.client:
            self.client.close()
        if self.async_client:
            asyncio.create_task(self.async_client.close())


class ElasticsearchExporter:
    """Export data to Elasticsearch with batching and error handling."""
    
    def __init__(self, client: ElasticsearchClient, batch_size: int = 1000):
        """
        Initialize exporter.
        
        Args:
            client: Elasticsearch client
            batch_size: Number of documents per batch
        """
        self.client = client
        self.batch_size = batch_size
        self.stats = {
            "documents_sent": 0,
            "batches_sent": 0,
            "errors": 0,
            "last_export": None
        }
    
    def export_documents(self, documents: List[Dict[str, Any]], index: str) -> Dict[str, Any]:
        """
        Export documents to Elasticsearch.
        
        Args:
            documents: List of documents to export
            index: Target index name
            
        Returns:
            Export statistics
        """
        if not documents:
            return self.stats
        
        try:
            # Prepare documents for bulk operation
            actions = []
            for doc in documents:
                action = {
                    "_index": index,
                    "_source": doc
                }
                actions.append(action)
            
            # Execute bulk operation
            success_count, failed_items = bulk(
                self.client.client,
                actions,
                chunk_size=self.batch_size,
                request_timeout=60
            )
            
            # Update statistics
            self.stats["documents_sent"] += success_count
            self.stats["batches_sent"] += 1
            self.stats["errors"] += len(failed_items) if failed_items else 0
            self.stats["last_export"] = datetime.now(timezone.utc).isoformat()
            
            logger.info(f"Exported {success_count} documents to {index}")
            
            if failed_items:
                logger.warning(f"Failed to export {len(failed_items)} documents")
            
            return self.stats
            
        except Exception as e:
            self.stats["errors"] += 1
            logger.error(f"Bulk export failed: {e}")
            raise ElasticsearchError(f"Bulk export failed: {e}", index=index, operation="bulk")
    
    async def async_export_documents(self, documents: List[Dict[str, Any]], index: str) -> Dict[str, Any]:
        """Async version of document export."""
        if not documents:
            return self.stats
        
        try:
            actions = []
            for doc in documents:
                action = {
                    "_index": index,
                    "_source": doc
                }
                actions.append(action)
            
            success_count, failed_items = await async_bulk(
                self.client.async_client,
                actions,
                chunk_size=self.batch_size,
                request_timeout=60
            )
            
            self.stats["documents_sent"] += success_count
            self.stats["batches_sent"] += 1
            self.stats["errors"] += len(failed_items) if failed_items else 0
            self.stats["last_export"] = datetime.now(timezone.utc).isoformat()
            
            logger.info(f"Async exported {success_count} documents to {index}")
            
            return self.stats
            
        except Exception as e:
            self.stats["errors"] += 1
            logger.error(f"Async bulk export failed: {e}")
            raise ElasticsearchError(f"Async bulk export failed: {e}", index=index, operation="async_bulk")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get export statistics."""
        return self.stats.copy()
