"""
ForgedFate Exception Classes

Custom exception hierarchy for the ForgedFate platform.
"""

class ForgedFateError(Exception):
    """Base exception class for ForgedFate platform."""
    
    def __init__(self, message: str, error_code: str = None, details: dict = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "UNKNOWN_ERROR"
        self.details = details or {}
    
    def __str__(self):
        if self.details:
            return f"{self.message} (Code: {self.error_code}, Details: {self.details})"
        return f"{self.message} (Code: {self.error_code})"


class ConfigError(ForgedFateError):
    """Configuration-related errors."""
    
    def __init__(self, message: str, config_key: str = None, **kwargs):
        super().__init__(message, error_code="CONFIG_ERROR", **kwargs)
        self.config_key = config_key


class ValidationError(ForgedFateError):
    """Data validation errors."""
    
    def __init__(self, message: str, field: str = None, value=None, **kwargs):
        super().__init__(message, error_code="VALIDATION_ERROR", **kwargs)
        self.field = field
        self.value = value


class ConnectionError(ForgedFateError):
    """Network and connection-related errors."""
    
    def __init__(self, message: str, host: str = None, port: int = None, **kwargs):
        super().__init__(message, error_code="CONNECTION_ERROR", **kwargs)
        self.host = host
        self.port = port


class ElasticsearchError(ForgedFateError):
    """Elasticsearch-specific errors."""
    
    def __init__(self, message: str, index: str = None, operation: str = None, **kwargs):
        super().__init__(message, error_code="ELASTICSEARCH_ERROR", **kwargs)
        self.index = index
        self.operation = operation


class KismetError(ForgedFateError):
    """Kismet-specific errors."""
    
    def __init__(self, message: str, source: str = None, data_type: str = None, **kwargs):
        super().__init__(message, error_code="KISMET_ERROR", **kwargs)
        self.source = source
        self.data_type = data_type


class DataProcessingError(ForgedFateError):
    """Data processing and transformation errors."""
    
    def __init__(self, message: str, processor: str = None, record_id: str = None, **kwargs):
        super().__init__(message, error_code="DATA_PROCESSING_ERROR", **kwargs)
        self.processor = processor
        self.record_id = record_id


class AuthenticationError(ForgedFateError):
    """Authentication and authorization errors."""
    
    def __init__(self, message: str, service: str = None, username: str = None, **kwargs):
        super().__init__(message, error_code="AUTH_ERROR", **kwargs)
        self.service = service
        self.username = username


class FileSystemError(ForgedFateError):
    """File system and I/O related errors."""
    
    def __init__(self, message: str, file_path: str = None, operation: str = None, **kwargs):
        super().__init__(message, error_code="FILESYSTEM_ERROR", **kwargs)
        self.file_path = file_path
        self.operation = operation
