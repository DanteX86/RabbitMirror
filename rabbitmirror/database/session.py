"""
Database session management for RabbitMirror.

Handles SQLAlchemy session creation, lifecycle management,
and database initialization.
"""

import atexit
import logging
from contextlib import contextmanager
from typing import Generator, Optional

from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session as SQLAlchemySession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from ..exceptions import DatabaseError
from .config import DatabaseConfig
from .models import Base

logger = logging.getLogger(__name__)

# Global session factory
_session_factory: Optional[sessionmaker] = None
_engine: Optional[Engine] = None


def create_database_engine(config: DatabaseConfig) -> Engine:
    """Create and configure database engine."""

    engine_kwargs = {
        "echo": config.echo,
    }

    # SQLite-specific configuration
    if config.is_sqlite():
        engine_kwargs.update(
            {
                "poolclass": StaticPool,
                "connect_args": {
                    "check_same_thread": False,
                    "timeout": config.pool_timeout,
                },
            }
        )

        # Enable foreign key constraints for SQLite
        @event.listens_for(Engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            if "sqlite" in str(dbapi_connection):
                cursor = dbapi_connection.cursor()
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.execute("PRAGMA journal_mode=WAL")
                cursor.execute("PRAGMA synchronous=NORMAL")
                cursor.close()

    else:
        # PostgreSQL and other databases support these parameters
        engine_kwargs.update(
            {
                "pool_timeout": config.pool_timeout,
                "pool_recycle": config.pool_recycle,
            }
        )

        # PostgreSQL-specific configuration
        if config.is_postgresql():
            engine_kwargs.update(
                {
                    "pool_size": config.pool_size,
                    "max_overflow": config.max_overflow,
                }
            )

    try:
        engine = create_engine(config.database_url, **engine_kwargs)

        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))

        logger.info(f"Database engine created successfully: {config.database_url}")
        return engine

    except Exception as e:
        raise DatabaseError(
            f"Failed to create database engine: {str(e)}",
            error_code="ENGINE_CREATION_FAILED",
        ) from e


def init_database(config: Optional[DatabaseConfig] = None) -> None:
    """Initialize database connection and create tables."""
    global _session_factory, _engine

    if config is None:
        config = DatabaseConfig.from_environment()

    config.validate()

    try:
        # Create engine
        _engine = create_database_engine(config)

        # Create session factory
        _session_factory = sessionmaker(bind=_engine, expire_on_commit=False)

        # Create all tables
        Base.metadata.create_all(_engine)

        # Register cleanup handler
        atexit.register(cleanup_database)

        logger.info("Database initialized successfully")

    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        raise DatabaseError(
            f"Database initialization failed: {str(e)}",
            error_code="DATABASE_INIT_FAILED",
        ) from e


def get_db_session() -> SQLAlchemySession:
    """Get database session."""
    if _session_factory is None:
        raise DatabaseError(
            "Database not initialized. Call init_database() first.",
            error_code="DATABASE_NOT_INITIALIZED",
        )

    return _session_factory()


@contextmanager
def db_session() -> Generator[SQLAlchemySession, None, None]:
    """Context manager for database sessions with automatic cleanup."""
    session = get_db_session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


@contextmanager
def db_transaction() -> Generator[SQLAlchemySession, None, None]:
    """Context manager for database transactions."""
    session = get_db_session()
    transaction = session.begin()
    try:
        yield session
        transaction.commit()
    except Exception:
        transaction.rollback()
        raise
    finally:
        session.close()


def cleanup_database() -> None:
    """Cleanup database connections."""
    global _engine, _session_factory

    if _engine:
        try:
            _engine.dispose()
            logger.info("Database connections closed")
        except Exception as e:
            logger.error(f"Error closing database connections: {str(e)}")
        finally:
            _engine = None
            _session_factory = None


def get_engine() -> Optional[Engine]:
    """Get the current database engine."""
    return _engine


def reset_database() -> None:
    """Reset database (mainly for testing)."""
    global _engine, _session_factory

    if _engine:
        try:
            # Drop all tables
            Base.metadata.drop_all(_engine)
            # Recreate all tables
            Base.metadata.create_all(_engine)
            logger.info("Database reset successfully")
        except Exception as e:
            logger.error(f"Database reset failed: {str(e)}")
            raise DatabaseError(
                f"Database reset failed: {str(e)}", error_code="DATABASE_RESET_FAILED"
            ) from e


class DatabaseHealthCheck:
    """Database health check utilities."""

    @staticmethod
    def check_connection() -> bool:
        """Check if database connection is healthy."""
        try:
            with db_session() as session:
                session.execute(text("SELECT 1"))
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            return False

    @staticmethod
    def get_connection_info() -> dict:
        """Get database connection information."""
        if _engine is None:
            return {"status": "not_initialized"}

        try:
            with _engine.connect() as conn:
                result = conn.execute(text("SELECT 1")).fetchone()
                return {
                    "status": "connected",
                    "url": str(_engine.url).replace(_engine.url.password or "", "***"),
                    "pool_size": getattr(_engine.pool, "size", None),
                    "checked_out": getattr(_engine.pool, "checkedout", None),
                    "test_query": result[0] if result else None,
                }
        except Exception as e:
            return {"status": "error", "error": str(e)}
