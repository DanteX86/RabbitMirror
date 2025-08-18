"""
Database package for RabbitMirror - Simplified for single-user YouTube analysis.

This package provides database connectivity, models, and utilities for
persistent data storage and management in single-user mode.
"""

from .cache import CacheManager
from .config import DatabaseConfig
from .models import Base, CacheEntry, DataRetentionPolicy, YouTubeAnalysis
from .session import get_db_session, init_database

__all__ = [
    "DatabaseConfig",
    "Base",
    "YouTubeAnalysis",
    "CacheEntry",
    "DataRetentionPolicy",
    "get_db_session",
    "init_database",
    "CacheManager",
]
