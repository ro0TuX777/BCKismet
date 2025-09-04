"""
ForgedFate Configuration Management

Centralized configuration handling with validation and environment support.
"""

import os
import yaml
import json
from pathlib import Path
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass, field
from .exceptions import ConfigError
from .logger import get_logger

logger = get_logger(__name__)


@dataclass
class ElasticsearchConfig:
    """Elasticsearch connection configuration."""
    hosts: list = field(default_factory=lambda: ["https://localhost:9200"])
    username: str = ""
    password: str = ""
    verify_certs: bool = False
    timeout: int = 30
    max_retries: int = 3
    index_prefix: str = "kismet"


@dataclass
class KismetConfig:
    """Kismet integration configuration."""
    host: str = "localhost"
    port: int = 2501
    username: str = ""
    password: str = ""
    log_directory: str = "./kismet"
    data_sources: list = field(default_factory=list)
    device_name: str = "forgedfate-device"


@dataclass
class FilebeatConfig:
    """Filebeat integration configuration."""
    enabled: bool = True
    config_path: str = "/etc/filebeat/filebeat.yml"
    log_paths: list = field(default_factory=lambda: ["./kismet/*.kismet"])
    fields: dict = field(default_factory=dict)


@dataclass
class LoggingConfig:
    """Logging configuration."""
    level: str = "INFO"
    file: Optional[str] = None
    max_bytes: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
    structured: bool = True


@dataclass
class Config:
    """Main configuration class for ForgedFate."""
    
    elasticsearch: ElasticsearchConfig = field(default_factory=ElasticsearchConfig)
    kismet: KismetConfig = field(default_factory=KismetConfig)
    filebeat: FilebeatConfig = field(default_factory=FilebeatConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    
    # Runtime settings
    debug: bool = False
    dry_run: bool = False
    batch_size: int = 1000
    max_workers: int = 4
    
    @classmethod
    def from_file(cls, config_path: Union[str, Path]) -> 'Config':
        """
        Load configuration from a file.
        
        Args:
            config_path: Path to configuration file (YAML or JSON)
            
        Returns:
            Config instance
            
        Raises:
            ConfigError: If file cannot be loaded or parsed
        """
        config_path = Path(config_path)
        
        if not config_path.exists():
            raise ConfigError(f"Configuration file not found: {config_path}")
        
        try:
            with open(config_path, 'r') as f:
                if config_path.suffix.lower() in ['.yml', '.yaml']:
                    data = yaml.safe_load(f)
                elif config_path.suffix.lower() == '.json':
                    data = json.load(f)
                else:
                    raise ConfigError(f"Unsupported config file format: {config_path.suffix}")
            
            return cls.from_dict(data)
            
        except Exception as e:
            raise ConfigError(f"Failed to load config from {config_path}: {e}")
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Config':
        """
        Create configuration from dictionary.
        
        Args:
            data: Configuration dictionary
            
        Returns:
            Config instance
        """
        config = cls()
        
        # Update elasticsearch config
        if 'elasticsearch' in data:
            es_data = data['elasticsearch']
            config.elasticsearch = ElasticsearchConfig(**es_data)
        
        # Update kismet config
        if 'kismet' in data:
            kismet_data = data['kismet']
            config.kismet = KismetConfig(**kismet_data)
        
        # Update filebeat config
        if 'filebeat' in data:
            filebeat_data = data['filebeat']
            config.filebeat = FilebeatConfig(**filebeat_data)
        
        # Update logging config
        if 'logging' in data:
            logging_data = data['logging']
            config.logging = LoggingConfig(**logging_data)
        
        # Update runtime settings
        for key in ['debug', 'dry_run', 'batch_size', 'max_workers']:
            if key in data:
                setattr(config, key, data[key])
        
        return config
    
    @classmethod
    def from_env(cls) -> 'Config':
        """
        Create configuration from environment variables.
        
        Returns:
            Config instance with values from environment
        """
        config = cls()
        
        # Elasticsearch settings
        if os.getenv('ES_HOSTS'):
            config.elasticsearch.hosts = os.getenv('ES_HOSTS').split(',')
        if os.getenv('ES_USERNAME'):
            config.elasticsearch.username = os.getenv('ES_USERNAME')
        if os.getenv('ES_PASSWORD'):
            config.elasticsearch.password = os.getenv('ES_PASSWORD')
        if os.getenv('ES_INDEX_PREFIX'):
            config.elasticsearch.index_prefix = os.getenv('ES_INDEX_PREFIX')
        
        # Kismet settings
        if os.getenv('KISMET_HOST'):
            config.kismet.host = os.getenv('KISMET_HOST')
        if os.getenv('KISMET_PORT'):
            config.kismet.port = int(os.getenv('KISMET_PORT'))
        if os.getenv('KISMET_DEVICE_NAME'):
            config.kismet.device_name = os.getenv('KISMET_DEVICE_NAME')
        if os.getenv('KISMET_LOG_DIR'):
            config.kismet.log_directory = os.getenv('KISMET_LOG_DIR')
        
        # Logging settings
        if os.getenv('LOG_LEVEL'):
            config.logging.level = os.getenv('LOG_LEVEL')
        if os.getenv('LOG_FILE'):
            config.logging.file = os.getenv('LOG_FILE')
        
        # Runtime settings
        if os.getenv('DEBUG'):
            config.debug = os.getenv('DEBUG').lower() in ['true', '1', 'yes']
        if os.getenv('DRY_RUN'):
            config.dry_run = os.getenv('DRY_RUN').lower() in ['true', '1', 'yes']
        
        return config
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to dictionary.
        
        Returns:
            Configuration as dictionary
        """
        return {
            'elasticsearch': {
                'hosts': self.elasticsearch.hosts,
                'username': self.elasticsearch.username,
                'password': self.elasticsearch.password,
                'verify_certs': self.elasticsearch.verify_certs,
                'timeout': self.elasticsearch.timeout,
                'max_retries': self.elasticsearch.max_retries,
                'index_prefix': self.elasticsearch.index_prefix,
            },
            'kismet': {
                'host': self.kismet.host,
                'port': self.kismet.port,
                'username': self.kismet.username,
                'password': self.kismet.password,
                'log_directory': self.kismet.log_directory,
                'data_sources': self.kismet.data_sources,
                'device_name': self.kismet.device_name,
            },
            'filebeat': {
                'enabled': self.filebeat.enabled,
                'config_path': self.filebeat.config_path,
                'log_paths': self.filebeat.log_paths,
                'fields': self.filebeat.fields,
            },
            'logging': {
                'level': self.logging.level,
                'file': self.logging.file,
                'max_bytes': self.logging.max_bytes,
                'backup_count': self.logging.backup_count,
                'structured': self.logging.structured,
            },
            'debug': self.debug,
            'dry_run': self.dry_run,
            'batch_size': self.batch_size,
            'max_workers': self.max_workers,
        }
    
    def save(self, config_path: Union[str, Path]) -> None:
        """
        Save configuration to file.
        
        Args:
            config_path: Path to save configuration file
        """
        config_path = Path(config_path)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        data = self.to_dict()
        
        try:
            with open(config_path, 'w') as f:
                if config_path.suffix.lower() in ['.yml', '.yaml']:
                    yaml.dump(data, f, default_flow_style=False, indent=2)
                elif config_path.suffix.lower() == '.json':
                    json.dump(data, f, indent=2)
                else:
                    raise ConfigError(f"Unsupported config file format: {config_path.suffix}")
            
            logger.info(f"Configuration saved to {config_path}")
            
        except Exception as e:
            raise ConfigError(f"Failed to save config to {config_path}: {e}")
    
    def validate(self) -> None:
        """
        Validate configuration settings.
        
        Raises:
            ConfigError: If configuration is invalid
        """
        # Validate Elasticsearch settings
        if not self.elasticsearch.hosts:
            raise ConfigError("Elasticsearch hosts cannot be empty")
        
        # Validate Kismet settings
        if not self.kismet.device_name:
            raise ConfigError("Kismet device name cannot be empty")
        
        if self.kismet.port < 1 or self.kismet.port > 65535:
            raise ConfigError(f"Invalid Kismet port: {self.kismet.port}")
        
        # Validate batch size
        if self.batch_size < 1:
            raise ConfigError(f"Batch size must be positive: {self.batch_size}")
        
        # Validate worker count
        if self.max_workers < 1:
            raise ConfigError(f"Max workers must be positive: {self.max_workers}")
        
        logger.info("Configuration validation passed")
