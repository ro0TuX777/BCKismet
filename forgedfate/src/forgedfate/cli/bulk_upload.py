#!/usr/bin/env python3
"""
ForgedFate Bulk Upload CLI

Command-line tool for bulk uploading Kismet data to Elasticsearch.
"""

import asyncio
import click
import sys
from pathlib import Path
from typing import Optional

from ..core.config import Config, ElasticsearchConfig
from ..core.logger import setup_logging, get_logger
from ..core.exceptions import ForgedFateError
from ..integrations.elasticsearch import ElasticsearchClient, ElasticsearchExporter
from ..integrations.kismet import KismetDataExtractor


@click.command()
@click.option('--config', '-c', type=click.Path(exists=True), 
              help='Configuration file path')
@click.option('--es-hosts', multiple=True, 
              help='Elasticsearch hosts (can be specified multiple times)')
@click.option('--es-username', help='Elasticsearch username')
@click.option('--es-password', help='Elasticsearch password')
@click.option('--index-prefix', default='kismet', 
              help='Elasticsearch index prefix')
@click.option('--device-name', default='forgedfate-device',
              help='Device name for data identification')
@click.option('--log-directory', type=click.Path(exists=True), default='.',
              help='Directory containing Kismet log files')
@click.option('--batch-size', default=1000, type=int,
              help='Number of documents per batch')
@click.option('--dry-run', is_flag=True,
              help='Show what would be uploaded without actually uploading')
@click.option('--verbose', '-v', is_flag=True,
              help='Enable verbose logging')
@click.option('--log-file', type=click.Path(),
              help='Log file path')
def main(config: Optional[str], es_hosts: tuple, es_username: Optional[str],
         es_password: Optional[str], index_prefix: str, device_name: str,
         log_directory: str, batch_size: int, dry_run: bool, verbose: bool,
         log_file: Optional[str]):
    """
    Bulk upload Kismet data to Elasticsearch.
    
    This tool processes all Kismet database files in the specified directory
    and uploads the extracted data to Elasticsearch in batches.
    """
    
    # Setup logging
    log_level = "DEBUG" if verbose else "INFO"
    setup_logging(level=log_level, log_file=log_file)
    logger = get_logger(__name__)
    
    try:
        # Load configuration
        if config:
            app_config = Config.from_file(config)
        else:
            app_config = Config.from_env()
        
        # Override with command line arguments
        if es_hosts:
            app_config.elasticsearch.hosts = list(es_hosts)
        if es_username:
            app_config.elasticsearch.username = es_username
        if es_password:
            app_config.elasticsearch.password = es_password
        if index_prefix:
            app_config.elasticsearch.index_prefix = index_prefix
        if device_name:
            app_config.kismet.device_name = device_name
        if log_directory:
            app_config.kismet.log_directory = log_directory
        if batch_size:
            app_config.batch_size = batch_size
        if dry_run:
            app_config.dry_run = dry_run
        
        # Validate configuration
        app_config.validate()
        
        # Run bulk upload
        asyncio.run(run_bulk_upload(app_config))
        
    except ForgedFateError as e:
        logger.error(f"ForgedFate error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


async def run_bulk_upload(config: Config):
    """
    Execute the bulk upload process.
    
    Args:
        config: Application configuration
    """
    logger = get_logger(__name__)
    
    logger.info("🚀 Starting ForgedFate Kismet Bulk Upload...")
    
    # Initialize Elasticsearch client
    logger.info("Configuring Elasticsearch client...")
    es_client = ElasticsearchClient(config.elasticsearch)
    
    # Test connection
    try:
        connection_result = es_client.test_connection()
        logger.info(f"✅ Elasticsearch connection successful: {connection_result.get('status')}")
    except Exception as e:
        logger.error(f"❌ Elasticsearch connection failed: {e}")
        return
    
    # Initialize data extractor
    extractor = KismetDataExtractor(device_name=config.kismet.device_name)
    
    # Initialize exporter
    exporter = ElasticsearchExporter(es_client, batch_size=config.batch_size)
    
    # Find Kismet files
    log_dir = Path(config.kismet.log_directory)
    kismet_files = list(log_dir.glob("*.kismet"))
    
    if not kismet_files:
        logger.warning(f"No Kismet files found in {log_dir}")
        return
    
    logger.info(f"Found {len(kismet_files)} Kismet files to process")
    
    total_documents = 0
    total_files = 0
    
    # Process each file
    for kismet_file in kismet_files:
        logger.info(f"Processing {kismet_file.name}...")
        
        try:
            # Extract data from Kismet file
            devices = extractor.extract_devices(str(kismet_file))
            
            if not devices:
                logger.warning(f"No devices found in {kismet_file.name}")
                continue
            
            logger.info(f"Extracted {len(devices)} devices from {kismet_file.name}")
            
            if config.dry_run:
                logger.info(f"[DRY RUN] Would upload {len(devices)} documents")
                total_documents += len(devices)
                total_files += 1
                continue
            
            # Generate index name
            index_name = f"{config.elasticsearch.index_prefix}-{config.kismet.device_name}-devices"
            
            # Upload to Elasticsearch
            stats = exporter.export_documents(devices, index_name)
            
            total_documents += len(devices)
            total_files += 1
            
            logger.info(f"✅ Uploaded {len(devices)} devices from {kismet_file.name}")
            
        except Exception as e:
            logger.error(f"❌ Failed to process {kismet_file.name}: {e}")
            continue
    
    # Final statistics
    final_stats = exporter.get_stats()
    
    logger.info("🎉 Bulk upload complete!")
    logger.info(f"Files processed: {total_files}")
    logger.info(f"Documents uploaded: {final_stats.get('documents_sent', total_documents)}")
    logger.info(f"Batches sent: {final_stats.get('batches_sent', 0)}")
    logger.info(f"Errors: {final_stats.get('errors', 0)}")
    
    if config.dry_run:
        logger.info("[DRY RUN] No data was actually uploaded")
    
    # Close connections
    es_client.close()


if __name__ == "__main__":
    main()
