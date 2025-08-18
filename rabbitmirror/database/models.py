"""
Database models for RabbitMirror - Simplified for single-user YouTube history analysis.

Defines SQLAlchemy models for persistent storage of YouTube analysis results
and cache entries. Complex multi-user features have been removed.
"""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Index,
    Integer,
    LargeBinary,
    String,
    Text,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy_utils import UUIDType

from ..exceptions import ValidationError

Base = declarative_base()


class TimestampMixin:
    """Mixin for adding timestamp fields to models."""

    created_at = Column(
        DateTime(timezone=True), default=func.now(), nullable=False, index=True
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=func.now(),
        onupdate=func.now(),
        nullable=False,
        index=True,
    )


class YouTubeAnalysis(Base, TimestampMixin):
    """Simplified model for storing YouTube history analysis results."""

    __tablename__ = "youtube_analyses"

    id = Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)

    # File information
    filename = Column(String(255), nullable=False, index=True)
    file_hash = Column(String(64), nullable=True, index=True)  # SHA-256 hash
    file_size = Column(Integer, nullable=True)

    # Analysis metadata
    analysis_type = Column(
        String(50), nullable=False, index=True
    )  # 'trend', 'cluster', 'pattern', etc.
    status = Column(
        String(20), default="pending", nullable=False, index=True
    )  # pending, completed, failed

    # Results data
    results = Column(JSON, nullable=True)
    summary = Column(JSON, nullable=True)
    analysis_metadata = Column(JSON, nullable=True)

    # Performance metrics
    processing_time = Column(Integer, nullable=True)  # milliseconds
    data_points = Column(Integer, nullable=True)

    # Simple retention (optional expiration)
    expires_at = Column(DateTime(timezone=True), nullable=True, index=True)

    def is_expired(self) -> bool:
        """Check if analysis result is expired."""
        if self.expires_at is None:
            return False
        return datetime.now(timezone.utc) > self.expires_at

    def get_results(self) -> Dict[str, Any]:
        """Get results as dictionary."""
        return self.results or {}

    def set_results(self, results: Dict[str, Any]) -> None:
        """Set analysis results."""
        if not isinstance(results, dict):
            raise ValidationError("Results must be a dictionary")
        self.results = results

    def __repr__(self) -> str:
        return f"<YouTubeAnalysis(id={self.id}, filename={self.filename}, type={self.analysis_type})>"


class CacheEntry(Base, TimestampMixin):
    """Model for caching analysis results and computed data."""

    __tablename__ = "cache_entries"

    id = Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)

    # Cache key and namespace
    cache_key = Column(String(255), nullable=False, index=True)
    namespace = Column(String(100), nullable=False, default="default", index=True)

    # Cached data
    data = Column(LargeBinary, nullable=True)  # Pickled data
    data_type = Column(String(50), nullable=False, default="json")  # json, pickle, text

    # Cache metadata
    ttl = Column(Integer, nullable=False)  # Time to live in seconds
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    hit_count = Column(Integer, default=0, nullable=False)
    last_accessed = Column(DateTime(timezone=True), default=func.now())

    # Composite unique constraint
    __table_args__ = (
        Index("ix_cache_key_namespace", "cache_key", "namespace", unique=True),
    )

    def is_expired(self) -> bool:
        """Check if cache entry is expired."""
        return datetime.now(timezone.utc) > self.expires_at

    def increment_hit_count(self) -> None:
        """Increment hit count and update last accessed time."""
        self.hit_count += 1
        self.last_accessed = datetime.now(timezone.utc)

    def __repr__(self) -> str:
        return f"<CacheEntry(key={self.cache_key}, namespace={self.namespace})>"


class DataRetentionPolicy(Base, TimestampMixin):
    """Model for managing data retention policies."""

    __tablename__ = "data_retention_policies"

    id = Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)

    # Policy configuration
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)

    # Target configuration
    target_table = Column(String(100), nullable=False, index=True)
    target_column = Column(
        String(100), nullable=False
    )  # Column to check for expiration

    # Retention settings
    retention_days = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # Execution tracking
    last_run = Column(DateTime(timezone=True), nullable=True)
    next_run = Column(DateTime(timezone=True), nullable=True, index=True)
    run_count = Column(Integer, default=0, nullable=False)

    def __repr__(self) -> str:
        return f"<DataRetentionPolicy(name={self.name}, table={self.target_table})>"


class Session(Base, TimestampMixin):
    """Model for user sessions."""

    __tablename__ = "sessions"

    id = Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)

    # Session data
    session_key = Column(String(255), unique=True, nullable=False, index=True)
    user_id = Column(String(100), nullable=True)

    # Session metadata
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    last_accessed = Column(DateTime(timezone=True), default=func.now())

    def is_expired(self) -> bool:
        """Check if session is expired."""
        return datetime.now(timezone.utc) > self.expires_at

    def __repr__(self) -> str:
        return f"<Session(id={self.id}, key={self.session_key})>"


class AnalysisResult(Base, TimestampMixin):
    """Model for storing analysis results - alias to YouTubeAnalysis for compatibility."""

    __tablename__ = "analysis_results"

    id = Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)

    # Analysis metadata
    analysis_type = Column(String(50), nullable=False, index=True)
    status = Column(String(20), default="pending", nullable=False, index=True)

    # Results data
    results = Column(JSON, nullable=True)
    analysis_metadata = Column(JSON, nullable=True)

    # Expiration
    expires_at = Column(DateTime(timezone=True), nullable=True, index=True)

    def is_expired(self) -> bool:
        """Check if analysis result is expired."""
        if self.expires_at is None:
            return False
        return datetime.now(timezone.utc) > self.expires_at

    def __repr__(self) -> str:
        return f"<AnalysisResult(id={self.id}, type={self.analysis_type})>"


class AuditLog(Base, TimestampMixin):
    """Model for audit logging."""

    __tablename__ = "audit_logs"

    id = Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)

    # Audit data
    action = Column(String(100), nullable=False, index=True)
    resource = Column(String(255), nullable=True)
    user_id = Column(String(100), nullable=True)

    # Log metadata
    details = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)  # IPv6 compatible

    def __repr__(self) -> str:
        return f"<AuditLog(id={self.id}, action={self.action})>"
