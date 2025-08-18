"""
Database configuration for RabbitMirror.

Handles database connection settings, environment variables,
and configuration validation.
"""

import os
from dataclasses import dataclass
from typing import Dict
from urllib.parse import urlparse

from ..exceptions import ConfigurationError


@dataclass
class DatabaseConfig:
    """Database configuration settings."""

    # Database connection
    database_url: str
    echo: bool = False
    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30
    pool_recycle: int = 3600

    # Redis cache
    redis_url: str = "redis://localhost:6379/0"
    cache_ttl: int = 3600  # 1 hour default

    # Session configuration
    session_lifetime: int = 86400  # 24 hours
    cleanup_interval: int = 3600  # 1 hour

    @classmethod
    def from_environment(cls) -> "DatabaseConfig":
        """Create configuration from environment variables."""

        # Database URL - required
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            # Default to SQLite for development
            database_url = f"sqlite:///{os.path.join(os.getcwd(), 'rabbitmirror.db')}"

        # Validate database URL
        try:
            parsed = urlparse(database_url)
            if not parsed.scheme:
                raise ValueError("Invalid database URL format")
        except Exception as e:
            raise ConfigurationError(
                f"Invalid database URL: {database_url}",
                error_code="INVALID_DATABASE_URL",
            ) from e

        # Redis URL
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

        return cls(
            database_url=database_url,
            echo=os.getenv("DATABASE_ECHO", "false").lower() == "true",
            pool_size=int(os.getenv("DATABASE_POOL_SIZE", "10")),
            max_overflow=int(os.getenv("DATABASE_MAX_OVERFLOW", "20")),
            pool_timeout=int(os.getenv("DATABASE_POOL_TIMEOUT", "30")),
            pool_recycle=int(os.getenv("DATABASE_POOL_RECYCLE", "3600")),
            redis_url=redis_url,
            cache_ttl=int(os.getenv("CACHE_TTL", "3600")),
            session_lifetime=int(os.getenv("SESSION_LIFETIME", "86400")),
            cleanup_interval=int(os.getenv("CLEANUP_INTERVAL", "3600")),
        )

    def is_sqlite(self) -> bool:
        """Check if using SQLite database."""
        return self.database_url.startswith("sqlite://")

    def is_postgresql(self) -> bool:
        """Check if using PostgreSQL database."""
        return self.database_url.startswith("postgresql://")

    def validate(self) -> None:
        """Validate configuration settings."""
        if self.pool_size <= 0:
            raise ConfigurationError(
                "Database pool size must be positive", error_code="INVALID_POOL_SIZE"
            )

        if self.session_lifetime <= 0:
            raise ConfigurationError(
                "Session lifetime must be positive",
                error_code="INVALID_SESSION_LIFETIME",
            )

        if self.cache_ttl <= 0:
            raise ConfigurationError(
                "Cache TTL must be positive", error_code="INVALID_CACHE_TTL"
            )
