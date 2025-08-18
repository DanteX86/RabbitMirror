"""
Cache management for RabbitMirror.

Provides caching functionality with Redis as primary cache
and database as fallback storage.
"""

import json
import logging
import pickle
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import redis
from redis.exceptions import RedisError

from .config import DatabaseConfig
from .models import CacheEntry
from .session import db_session

logger = logging.getLogger(__name__)


class CacheManager:
    """Manages caching with Redis primary and database fallback."""

    def __init__(self, config: Optional[DatabaseConfig] = None):
        """Initialize cache manager."""
        if config is None:
            config = DatabaseConfig.from_environment()

        self.config = config
        self.redis_client = None
        self.redis_available = False

        # Initialize Redis connection
        self._init_redis()

    def _init_redis(self) -> None:
        """Initialize Redis connection."""
        try:
            self.redis_client = redis.from_url(
                self.config.redis_url,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30,
            )

            # Test connection
            self.redis_client.ping()
            self.redis_available = True
            logger.info(f"Redis connection established: {self.config.redis_url}")

        except Exception as e:
            logger.warning(
                f"Redis connection failed, using database fallback: {str(e)}"
            )
            self.redis_available = False

    def get(self, key: str, namespace: str = "default") -> Optional[Any]:
        """Get value from cache."""
        cache_key = self._make_key(key, namespace)

        # Try Redis first
        if self.redis_available:
            try:
                data = self.redis_client.get(cache_key)
                if data is not None:
                    return self._deserialize(data)
            except RedisError as e:
                logger.warning(f"Redis get failed: {str(e)}")
                self.redis_available = False

        # Fallback to database
        return self._get_from_db(key, namespace)

    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        namespace: str = "default",
    ) -> bool:
        """Set value in cache."""
        if ttl is None:
            ttl = self.config.cache_ttl

        cache_key = self._make_key(key, namespace)
        serialized_data = self._serialize(value)

        success = False

        # Try Redis first
        if self.redis_available:
            try:
                self.redis_client.setex(cache_key, ttl, serialized_data)
                success = True
            except RedisError as e:
                logger.warning(f"Redis set failed: {str(e)}")
                self.redis_available = False

        # Also store in database as backup
        try:
            self._set_in_db(key, value, ttl, namespace)
            success = True
        except Exception as e:
            logger.error(f"Database cache set failed: {str(e)}")

        return success

    def delete(self, key: str, namespace: str = "default") -> bool:
        """Delete value from cache."""
        cache_key = self._make_key(key, namespace)

        redis_success = False
        db_success = False

        # Delete from Redis
        if self.redis_available:
            try:
                self.redis_client.delete(cache_key)
                redis_success = True
            except RedisError as e:
                logger.warning(f"Redis delete failed: {str(e)}")
                self.redis_available = False

        # Delete from database
        try:
            self._delete_from_db(key, namespace)
            db_success = True
        except Exception as e:
            logger.error(f"Database cache delete failed: {str(e)}")

        return redis_success or db_success

    def exists(self, key: str, namespace: str = "default") -> bool:
        """Check if key exists in cache."""
        cache_key = self._make_key(key, namespace)

        # Check Redis first
        if self.redis_available:
            try:
                return bool(self.redis_client.exists(cache_key))
            except RedisError as e:
                logger.warning(f"Redis exists failed: {str(e)}")
                self.redis_available = False

        # Check database
        return self._exists_in_db(key, namespace)

    def clear_namespace(self, namespace: str = "default") -> int:
        """Clear all keys in a namespace."""
        cleared_count = 0

        # Clear from Redis
        if self.redis_available:
            try:
                pattern = self._make_key("*", namespace)
                keys = self.redis_client.keys(pattern)
                if keys:
                    cleared_count += self.redis_client.delete(*keys)
            except RedisError as e:
                logger.warning(f"Redis clear namespace failed: {str(e)}")
                self.redis_available = False

        # Clear from database
        try:
            cleared_count += self._clear_namespace_db(namespace)
        except Exception as e:
            logger.error(f"Database clear namespace failed: {str(e)}")

        return cleared_count

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        stats = {
            "redis_available": self.redis_available,
            "redis_info": {},
            "database_entries": 0,
        }

        # Redis stats
        if self.redis_available:
            try:
                info = self.redis_client.info()
                stats["redis_info"] = {
                    "used_memory": info.get("used_memory_human", "unknown"),
                    "total_connections": info.get("total_connections_received", 0),
                    "keyspace_hits": info.get("keyspace_hits", 0),
                    "keyspace_misses": info.get("keyspace_misses", 0),
                }
            except RedisError as e:
                logger.warning(f"Redis stats failed: {str(e)}")
                self.redis_available = False

        # Database stats
        try:
            with db_session() as session:
                count = session.query(CacheEntry).count()
                stats["database_entries"] = count
        except Exception as e:
            logger.error(f"Database stats failed: {str(e)}")

        return stats

    def cleanup_expired(self) -> int:
        """Clean up expired cache entries from database."""
        try:
            with db_session() as session:
                now = datetime.now(timezone.utc)
                expired_entries = (
                    session.query(CacheEntry).filter(CacheEntry.expires_at < now).all()
                )

                count = len(expired_entries)
                for entry in expired_entries:
                    session.delete(entry)

                session.commit()
                logger.info(f"Cleaned up {count} expired cache entries")
                return count

        except Exception as e:
            logger.error(f"Cache cleanup failed: {str(e)}")
            return 0

    def _make_key(self, key: str, namespace: str) -> str:
        """Create namespaced cache key."""
        return f"rabbitmirror:{namespace}:{key}"

    def _serialize(self, value: Any) -> str:
        """Serialize value for storage."""
        try:
            return json.dumps(value)
        except (TypeError, ValueError):
            # Fall back to pickle for non-JSON serializable objects
            return pickle.dumps(value).hex()

    def _deserialize(self, data: str) -> Any:
        """Deserialize value from storage."""
        try:
            return json.loads(data)
        except (json.JSONDecodeError, TypeError):
            # Try pickle
            try:
                return pickle.loads(bytes.fromhex(data))
            except Exception:
                return data

    def _get_from_db(self, key: str, namespace: str) -> Optional[Any]:
        """Get value from database cache."""
        try:
            with db_session() as session:
                entry = (
                    session.query(CacheEntry)
                    .filter(
                        CacheEntry.cache_key == key, CacheEntry.namespace == namespace
                    )
                    .first()
                )

                if entry is None:
                    return None

                # Check expiration
                if entry.is_expired():
                    session.delete(entry)
                    session.commit()
                    return None

                # Update access stats
                entry.increment_hit_count()
                session.commit()

                # Deserialize data
                if entry.data_type == "json":
                    return json.loads(entry.data.decode())
                elif entry.data_type == "pickle":
                    return pickle.loads(entry.data)
                else:
                    return entry.data.decode()

        except Exception as e:
            logger.error(f"Database cache get failed: {str(e)}")
            return None

    def _set_in_db(self, key: str, value: Any, ttl: int, namespace: str) -> None:
        """Set value in database cache."""
        with db_session() as session:
            # Remove existing entry
            existing = (
                session.query(CacheEntry)
                .filter(CacheEntry.cache_key == key, CacheEntry.namespace == namespace)
                .first()
            )

            if existing:
                session.delete(existing)

            # Serialize data
            try:
                data = json.dumps(value).encode()
                data_type = "json"
            except (TypeError, ValueError):
                data = pickle.dumps(value)
                data_type = "pickle"

            # Create new entry
            expires_at = datetime.now(timezone.utc) + timedelta(seconds=ttl)

            entry = CacheEntry(
                cache_key=key,
                namespace=namespace,
                data=data,
                data_type=data_type,
                ttl=ttl,
                expires_at=expires_at,
            )

            session.add(entry)
            session.commit()

    def _delete_from_db(self, key: str, namespace: str) -> None:
        """Delete value from database cache."""
        with db_session() as session:
            entry = (
                session.query(CacheEntry)
                .filter(CacheEntry.cache_key == key, CacheEntry.namespace == namespace)
                .first()
            )

            if entry:
                session.delete(entry)
                session.commit()

    def _exists_in_db(self, key: str, namespace: str) -> bool:
        """Check if key exists in database cache."""
        try:
            with db_session() as session:
                entry = (
                    session.query(CacheEntry)
                    .filter(
                        CacheEntry.cache_key == key, CacheEntry.namespace == namespace
                    )
                    .first()
                )

                if entry is None:
                    return False

                # Check if expired
                if entry.is_expired():
                    session.delete(entry)
                    session.commit()
                    return False

                return True

        except Exception as e:
            logger.error(f"Database cache exists check failed: {str(e)}")
            return False

    def _clear_namespace_db(self, namespace: str) -> int:
        """Clear namespace from database cache."""
        with db_session() as session:
            entries = (
                session.query(CacheEntry)
                .filter(CacheEntry.namespace == namespace)
                .all()
            )

            count = len(entries)
            for entry in entries:
                session.delete(entry)

            session.commit()
            return count
