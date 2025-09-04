"""
ForgedFate Command Line Interface

CLI tools and utilities for ForgedFate operations.
"""

from .bulk_upload import main as bulk_upload_main
from .test_connection import main as test_connection_main
from .setup import main as setup_main

__all__ = [
    "bulk_upload_main",
    "test_connection_main", 
    "setup_main",
]
