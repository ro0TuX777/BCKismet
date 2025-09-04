"""
ForgedFate Logging Configuration

Centralized logging setup with structured logging support.
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional, Dict, Any
import structlog
from datetime import datetime


class ForgedFateFormatter(logging.Formatter):
    """Custom formatter for ForgedFate logs."""
    
    def __init__(self):
        super().__init__()
        self.fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    def format(self, record):
        # Add custom fields
        record.component = getattr(record, 'component', 'core')
        record.session_id = getattr(record, 'session_id', 'unknown')
        
        # Format timestamp
        record.asctime = datetime.fromtimestamp(record.created).isoformat()
        
        return super().format(record)


def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
    structured: bool = True
) -> None:
    """
    Setup logging configuration for ForgedFate.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (optional)
        max_bytes: Maximum log file size before rotation
        backup_count: Number of backup files to keep
        structured: Whether to use structured logging
    """
    
    # Configure structlog if enabled
    if structured:
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer()
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
    
    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper()))
    console_handler.setFormatter(ForgedFateFormatter())
    root_logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count
        )
        file_handler.setLevel(getattr(logging, level.upper()))
        file_handler.setFormatter(ForgedFateFormatter())
        root_logger.addHandler(file_handler)
    
    # Set specific logger levels
    logging.getLogger("elasticsearch").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)


def get_logger(name: str, **kwargs) -> logging.Logger:
    """
    Get a logger instance with ForgedFate configuration.
    
    Args:
        name: Logger name (usually __name__)
        **kwargs: Additional context for structured logging
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Add context if using structured logging
    if kwargs:
        logger = structlog.get_logger(name).bind(**kwargs)
    
    return logger


class LogContext:
    """Context manager for adding structured logging context."""
    
    def __init__(self, logger: logging.Logger, **context):
        self.logger = logger
        self.context = context
        self.original_logger = None
    
    def __enter__(self):
        if hasattr(self.logger, 'bind'):
            self.original_logger = self.logger
            self.logger = self.logger.bind(**self.context)
        return self.logger
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.original_logger:
            self.logger = self.original_logger


# Default logger for the package
logger = get_logger(__name__)
