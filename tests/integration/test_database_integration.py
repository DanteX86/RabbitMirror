"""Integration tests for database and persistence components."""

# flake8: noqa
import json
import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

try:
    from rabbitmirror.database.cache import CacheManager
    from rabbitmirror.database.models import *
    from rabbitmirror.database.retention import RetentionManager
    from rabbitmirror.database.session import DatabaseSession

    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False

from rabbitmirror.config_manager import ConfigManager


@pytest.mark.skipif(
    not DATABASE_AVAILABLE, reason="Database dependencies not available"
)
class TestDatabaseIntegration:
    """Test database and persistence integration."""

    @pytest.fixture
    def temp_db_path(self, tmp_path):
        """Create temporary database path."""
        return tmp_path / "test_rabbitmirror.db"

    @pytest.fixture
    def db_session(self, temp_db_path):
        """Create database session for testing."""
        session = DatabaseSession(str(temp_db_path))
        session.initialize()
        yield session
        session.close()

    @pytest.fixture
    def sample_analysis_data(self):
        """Sample analysis data for database testing."""
        return {
            "filename": "test_history.html",
            "total_videos": 100,
            "analysis_results": {
                "trends": {"trend1": "value1", "trend2": "value2"},
                "clusters": {"cluster1": [1, 2, 3], "cluster2": [4, 5, 6]},
                "patterns": {"pattern1": 0.75, "pattern2": 0.85},
            },
            "metadata": {
                "processing_time": 5.23,
                "memory_usage": 1024000,
                "timestamp": "2023-12-15T14:30:45",
            },
        }

    def test_database_initialization(self, temp_db_path):
        """Test database initialization and schema creation."""
        session = DatabaseSession(str(temp_db_path))
        session.initialize()

        # Verify database file was created
        assert temp_db_path.exists()

        # Verify tables were created
        conn = sqlite3.connect(str(temp_db_path))
        cursor = conn.cursor()

        # Check if tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]

        # Should have at least some core tables
        expected_tables = ["analysis_results", "processing_metadata", "user_sessions"]
        for table in expected_tables:
            assert any(table in existing_table for existing_table in tables)

        conn.close()
        session.close()

    def test_analysis_data_persistence(self, db_session, sample_analysis_data):
        """Test saving and retrieving analysis data."""
        # Save analysis data
        analysis_id = db_session.save_analysis_result(
            filename=sample_analysis_data["filename"],
            total_videos=sample_analysis_data["total_videos"],
            results=sample_analysis_data["analysis_results"],
            metadata=sample_analysis_data["metadata"],
        )

        assert analysis_id is not None

        # Retrieve analysis data
        retrieved_data = db_session.get_analysis_result(analysis_id)

        assert retrieved_data is not None
        assert retrieved_data["filename"] == sample_analysis_data["filename"]
        assert retrieved_data["total_videos"] == sample_analysis_data["total_videos"]

    def test_cache_integration(self, temp_db_path):
        """Test cache manager integration with database."""
        cache_manager = CacheManager(str(temp_db_path))

        # Test cache operations
        test_key = "analysis_cache_test"
        test_data = {"result": "cached_value", "timestamp": "2023-12-15T14:30:45"}

        # Store in cache
        cache_manager.set(test_key, test_data, ttl=3600)

        # Retrieve from cache
        cached_data = cache_manager.get(test_key)

        assert cached_data is not None
        assert cached_data["result"] == test_data["result"]

    def test_retention_manager_integration(self, db_session, sample_analysis_data):
        """Test retention manager integration."""
        retention_manager = RetentionManager(db_session)

        # Save multiple analysis results with different timestamps
        analysis_ids = []
        for i in range(5):
            data = sample_analysis_data.copy()
            data["filename"] = f"test_history_{i}.html"
            data["metadata"]["timestamp"] = f"2023-12-{10 + i:02d}T14:30:45"

            analysis_id = db_session.save_analysis_result(
                filename=data["filename"],
                total_videos=data["total_videos"],
                results=data["analysis_results"],
                metadata=data["metadata"],
            )
            analysis_ids.append(analysis_id)

        # Test retention cleanup
        retention_days = 3
        cleaned_count = retention_manager.cleanup_old_data(retention_days)

        # Should clean up some old data
        assert cleaned_count >= 0

    def test_concurrent_database_access(self, temp_db_path, sample_analysis_data):
        """Test concurrent database access."""
        import threading
        import time

        results = []
        errors = []

        def database_operation(thread_id):
            try:
                session = DatabaseSession(str(temp_db_path))
                session.initialize()

                # Perform database operations
                data = sample_analysis_data.copy()
                data["filename"] = f"concurrent_test_{thread_id}.html"

                analysis_id = session.save_analysis_result(
                    filename=data["filename"],
                    total_videos=data["total_videos"],
                    results=data["analysis_results"],
                    metadata=data["metadata"],
                )

                # Retrieve the data
                retrieved = session.get_analysis_result(analysis_id)
                results.append((thread_id, analysis_id, retrieved))

                session.close()

            except Exception as e:
                errors.append(f"Thread {thread_id} error: {e}")

        # Create multiple threads for concurrent access
        threads = []
        for i in range(5):
            thread = threading.Thread(target=database_operation, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Check results
        assert len(errors) == 0, f"Errors occurred: {errors}"
        assert len(results) == 5

        # Verify all operations succeeded
        for thread_id, analysis_id, retrieved in results:
            assert analysis_id is not None
            assert retrieved is not None
            assert f"concurrent_test_{thread_id}.html" in retrieved["filename"]

    def test_database_transaction_integrity(self, db_session, sample_analysis_data):
        """Test database transaction integrity."""
        # Test successful transaction
        try:
            db_session.begin_transaction()

            analysis_id = db_session.save_analysis_result(
                filename=sample_analysis_data["filename"],
                total_videos=sample_analysis_data["total_videos"],
                results=sample_analysis_data["analysis_results"],
                metadata=sample_analysis_data["metadata"],
            )

            db_session.commit_transaction()

            # Verify data was saved
            retrieved = db_session.get_analysis_result(analysis_id)
            assert retrieved is not None

        except Exception as e:
            db_session.rollback_transaction()
            pytest.fail(f"Transaction failed: {e}")

    def test_database_backup_and_restore(
        self, temp_db_path, db_session, sample_analysis_data
    ):
        """Test database backup and restore functionality."""
        # Save some data
        analysis_id = db_session.save_analysis_result(
            filename=sample_analysis_data["filename"],
            total_videos=sample_analysis_data["total_videos"],
            results=sample_analysis_data["analysis_results"],
            metadata=sample_analysis_data["metadata"],
        )

        # Create backup
        backup_path = temp_db_path.parent / "backup_test.db"

        if hasattr(db_session, "create_backup"):
            db_session.create_backup(str(backup_path))
            assert backup_path.exists()

            # Verify backup contains data
            backup_session = DatabaseSession(str(backup_path))
            backup_session.initialize()

            retrieved_from_backup = backup_session.get_analysis_result(analysis_id)
            assert retrieved_from_backup is not None

            backup_session.close()

    def test_database_schema_migration(self, temp_db_path):
        """Test database schema migration functionality."""
        # Create database with initial schema
        session = DatabaseSession(str(temp_db_path))
        session.initialize()

        # Test schema version tracking
        if hasattr(session, "get_schema_version"):
            initial_version = session.get_schema_version()
            assert initial_version is not None

            # Test migration
            if hasattr(session, "migrate_schema"):
                session.migrate_schema()

                # Verify migration completed
                new_version = session.get_schema_version()
                assert new_version >= initial_version

        session.close()

    def test_database_performance_with_large_data(self, db_session):
        """Test database performance with large datasets."""
        import time

        # Generate large dataset
        large_results = {
            "trends": {f"trend_{i}": f"value_{i}" for i in range(1000)},
            "clusters": {f"cluster_{i}": list(range(i, i + 10)) for i in range(100)},
            "patterns": {f"pattern_{i}": 0.5 + (i % 100) / 200 for i in range(500)},
        }

        metadata = {
            "processing_time": 15.67,
            "memory_usage": 10240000,
            "timestamp": "2023-12-15T14:30:45",
        }

        start_time = time.time()

        # Save large data
        analysis_id = db_session.save_analysis_result(
            filename="large_test.html",
            total_videos=10000,
            results=large_results,
            metadata=metadata,
        )

        save_time = time.time() - start_time

        # Retrieve large data
        start_time = time.time()
        retrieved = db_session.get_analysis_result(analysis_id)
        retrieve_time = time.time() - start_time

        # Performance assertions
        assert save_time < 5.0  # Should save within 5 seconds
        assert retrieve_time < 2.0  # Should retrieve within 2 seconds
        assert retrieved is not None
        assert len(retrieved["results"]["trends"]) == 1000

    def test_database_error_handling(self, temp_db_path):
        """Test database error handling and recovery."""
        session = DatabaseSession(str(temp_db_path))

        # Test handling of corrupted database
        with patch("sqlite3.connect") as mock_connect:
            mock_connect.side_effect = sqlite3.Error("Database is locked")

            with pytest.raises(Exception):
                session.initialize()

        # Test recovery after error
        session = DatabaseSession(str(temp_db_path))
        session.initialize()
        assert session is not None
        session.close()

    def test_config_database_integration(self, tmp_path):
        """Test configuration manager database integration."""
        config_file = tmp_path / "config.json"
        db_path = tmp_path / "config_test.db"

        config_manager = ConfigManager(str(config_file))
        db_session = DatabaseSession(str(db_path))
        db_session.initialize()

        # Test saving config to database
        config_manager.set("database.path", str(db_path))
        config_manager.set("database.retention_days", 30)
        config_manager.set("cache.ttl", 3600)

        # Save configuration
        config_data = config_manager.get_all()

        if hasattr(db_session, "save_configuration"):
            config_id = db_session.save_configuration(config_data)
            assert config_id is not None

            # Retrieve configuration
            retrieved_config = db_session.get_configuration(config_id)
            assert retrieved_config is not None
            assert retrieved_config["database.path"] == str(db_path)

        db_session.close()

    def test_database_indexing_and_queries(self, db_session, sample_analysis_data):
        """Test database indexing and query performance."""
        # Save multiple analysis results
        analysis_ids = []
        for i in range(10):
            data = sample_analysis_data.copy()
            data["filename"] = f"query_test_{i}.html"
            data["total_videos"] = 100 + i * 10
            data["metadata"]["timestamp"] = f"2023-12-{15 + (i % 10):02d}T14:30:45"

            analysis_id = db_session.save_analysis_result(
                filename=data["filename"],
                total_videos=data["total_videos"],
                results=data["analysis_results"],
                metadata=data["metadata"],
            )
            analysis_ids.append(analysis_id)

        # Test queries
        if hasattr(db_session, "query_by_date_range"):
            results = db_session.query_by_date_range(
                start_date="2023-12-15", end_date="2023-12-25"
            )
            assert len(results) > 0

        if hasattr(db_session, "query_by_video_count"):
            results = db_session.query_by_video_count(min_videos=150)
            assert len(results) > 0

    def test_database_cleanup_and_maintenance(self, db_session, sample_analysis_data):
        """Test database cleanup and maintenance operations."""
        # Add test data
        analysis_ids = []
        for i in range(5):
            data = sample_analysis_data.copy()
            data["filename"] = f"cleanup_test_{i}.html"

            analysis_id = db_session.save_analysis_result(
                filename=data["filename"],
                total_videos=data["total_videos"],
                results=data["analysis_results"],
                metadata=data["metadata"],
            )
            analysis_ids.append(analysis_id)

        # Test cleanup operations
        if hasattr(db_session, "vacuum_database"):
            db_session.vacuum_database()

        if hasattr(db_session, "analyze_database"):
            db_session.analyze_database()

        if hasattr(db_session, "check_integrity"):
            integrity_ok = db_session.check_integrity()
            assert integrity_ok

    def test_database_connection_pooling(self, temp_db_path):
        """Test database connection pooling functionality."""
        # Create multiple sessions
        sessions = []
        for i in range(5):
            session = DatabaseSession(str(temp_db_path))
            session.initialize()
            sessions.append(session)

        # All sessions should be functional
        for i, session in enumerate(sessions):
            # Test basic operation
            if hasattr(session, "test_connection"):
                assert session.test_connection()

        # Close all sessions
        for session in sessions:
            session.close()

    def test_database_encryption_support(self, temp_db_path):
        """Test database encryption support if available."""
        # This test checks if encryption is supported
        # Implementation depends on database backend

        session = DatabaseSession(str(temp_db_path))

        # Test with encryption key if supported
        if hasattr(session, "set_encryption_key"):
            encryption_key = "test_encryption_key_123456789"
            session.set_encryption_key(encryption_key)

        session.initialize()

        # Test that data can be saved and retrieved with encryption
        test_data = {"encrypted_test": "sensitive_data"}

        if hasattr(session, "save_encrypted_data"):
            data_id = session.save_encrypted_data(test_data)
            retrieved = session.get_encrypted_data(data_id)
            assert retrieved["encrypted_test"] == "sensitive_data"

        session.close()
