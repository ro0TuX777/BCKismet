"""
ForgedFate: Kismet-Elasticsearch Integration Platform

A comprehensive wireless intelligence platform that integrates Kismet wireless 
detection capabilities with Elasticsearch for real-time data analysis and visualization.

Author: ForgedFate Development Team
License: MIT
Version: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "ForgedFate Development Team"
__license__ = "MIT"
__email__ = "dev@forgedfate.com"

# Core imports
from .core.config import Config
from .core.logger import get_logger
from .integrations.elasticsearch import ElasticsearchClient
from .integrations.kismet import KismetDataExtractor

# Version info
VERSION_INFO = {
    "major": 1,
    "minor": 0,
    "patch": 0,
    "release": "stable"
}

def get_version():
    """Get the current version string."""
    return __version__

def get_version_info():
    """Get detailed version information."""
    return VERSION_INFO.copy()

# Package-level logger
logger = get_logger(__name__)

# Initialize package
logger.info(f"ForgedFate v{__version__} initialized")

__all__ = [
    "__version__",
    "__author__",
    "__license__",
    "__email__",
    "Config",
    "get_logger",
    "ElasticsearchClient", 
    "KismetDataExtractor",
    "get_version",
    "get_version_info",
]
