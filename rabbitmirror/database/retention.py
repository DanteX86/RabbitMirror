"""
Data retention and cleanup management for RabbitMirror.

Handles automatic cleanup of expired data, implements retention policies,
and provides utilities for data archival.
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

from ..exceptions import RetentionError
from .models import AnalysisResult, AuditLog, CacheEntry, DataRetentionPolicy
from .models import Session as UserSession
from .session import db_session

logger = logging.getLogger(__name__)


class RetentionManager:
    """Manages data retention policies and cleanup operations."""

    def __init__(self):
        """Initialize retention manager."""
        self.policies = {}
        self._load_policies()

    def _load_policies(self) -> None:
        """Load retention policies from database."""
        try:
            with db_session() as session:
                policies = (
                    session.query(DataRetentionPolicy)
                    .filter(DataRetentionPolicy.is_active.is_(True))
                    .all()
                )

                for policy in policies:
                    self.policies[policy.name] = policy

                logger.info(f"Loaded {len(policies)} retention policies")

        except Exception as e:
            logger.error(f"Failed to load retention policies: {str(e)}")

    def create_default_policies(self) -> None:
        """Create default retention policies."""
        default_policies = [
            {
                "name": "analysis_results_cleanup",
                "description": "Clean up expired analysis results",
                "target_table": "analysis_results",
                "target_column": "expires_at",
                "retention_days": 30,
            },
            {
                "name": "session_cleanup",
                "description": "Clean up expired user sessions",
                "target_table": "sessions",
                "target_column": "expires_at",
                "retention_days": 7,
            },
            {
                "name": "cache_cleanup",
                "description": "Clean up expired cache entries",
                "target_table": "cache_entries",
                "target_column": "expires_at",
                "retention_days": 1,
            },
            {
                "name": "audit_log_cleanup",
                "description": "Clean up old audit log entries",
                "target_table": "audit_logs",
                "target_column": "created_at",
                "retention_days": 90,
            },
        ]

        try:
            with db_session() as session:
                for policy_data in default_policies:
                    existing = (
                        session.query(DataRetentionPolicy)
                        .filter(DataRetentionPolicy.name == policy_data["name"])
                        .first()
                    )

                    if not existing:
                        policy = DataRetentionPolicy(**policy_data)
                        session.add(policy)

                session.commit()
                logger.info("Created default retention policies")

        except Exception as e:
            logger.error(f"Failed to create default policies: {str(e)}")
            raise RetentionError(
                f"Failed to create default retention policies: {str(e)}",
                error_code="POLICY_CREATION_FAILED",
            ) from e

    def run_cleanup(self, policy_name: Optional[str] = None) -> Dict[str, int]:
        """Run cleanup operations for specified policy or all policies."""
        results = {}

        policies_to_run = []
        if policy_name:
            if policy_name in self.policies:
                policies_to_run = [self.policies[policy_name]]
            else:
                raise RetentionError(
                    f"Policy '{policy_name}' not found", error_code="POLICY_NOT_FOUND"
                )
        else:
            policies_to_run = list(self.policies.values())

        for policy in policies_to_run:
            try:
                count = self._execute_policy(policy)
                results[policy.name] = count
                logger.info(f"Policy '{policy.name}' cleaned up {count} records")

            except Exception as e:
                logger.error(f"Policy '{policy.name}' failed: {str(e)}")
                results[policy.name] = -1

        return results

    def _execute_policy(self, policy: DataRetentionPolicy) -> int:
        """Execute a specific retention policy."""
        with db_session() as session:
            # Calculate cutoff date
            cutoff_date = datetime.now(timezone.utc) - timedelta(
                days=policy.retention_days
            )

            # Execute cleanup based on target table
            if policy.target_table == "analysis_results":
                count = self._cleanup_analysis_results(session, cutoff_date)
            elif policy.target_table == "sessions":
                count = self._cleanup_sessions(session, cutoff_date)
            elif policy.target_table == "cache_entries":
                count = self._cleanup_cache_entries(session, cutoff_date)
            elif policy.target_table == "audit_logs":
                count = self._cleanup_audit_logs(session, cutoff_date)
            else:
                # Generic cleanup using raw SQL
                count = self._generic_cleanup(session, policy, cutoff_date)

            # Update policy execution tracking
            policy.last_run = datetime.now(timezone.utc)
            policy.run_count += 1
            policy.next_run = policy.last_run + timedelta(hours=24)  # Daily by default

            session.commit()
            return count

    def _cleanup_analysis_results(self, session: Session, cutoff_date: datetime) -> int:
        """Clean up expired analysis results."""
        expired_results = (
            session.query(AnalysisResult)
            .filter(AnalysisResult.expires_at < cutoff_date)
            .all()
        )

        count = len(expired_results)
        for result in expired_results:
            session.delete(result)

        return count

    def _cleanup_sessions(self, session: Session, cutoff_date: datetime) -> int:
        """Clean up expired user sessions."""
        expired_sessions = (
            session.query(UserSession)
            .filter(UserSession.expires_at < cutoff_date)
            .all()
        )

        count = len(expired_sessions)
        for user_session in expired_sessions:
            session.delete(user_session)

        return count

    def _cleanup_cache_entries(self, session: Session, cutoff_date: datetime) -> int:
        """Clean up expired cache entries."""
        expired_entries = (
            session.query(CacheEntry).filter(CacheEntry.expires_at < cutoff_date).all()
        )

        count = len(expired_entries)
        for entry in expired_entries:
            session.delete(entry)

        return count

    def _cleanup_audit_logs(self, session: Session, cutoff_date: datetime) -> int:
        """Clean up old audit log entries."""
        old_logs = (
            session.query(AuditLog).filter(AuditLog.created_at < cutoff_date).all()
        )

        count = len(old_logs)
        for log in old_logs:
            session.delete(log)

        return count

    def _generic_cleanup(
        self, session: Session, policy: DataRetentionPolicy, cutoff_date: datetime
    ) -> int:
        """Generic cleanup using raw SQL."""
        # Validate table and column names to prevent injection
        allowed_tables = {
            "analysis_results",
            "sessions",
            "cache_entries",
            "audit_logs",
            "user_sessions",
            "export_results",
            "notifications",
        }
        allowed_columns = {"expires_at", "created_at", "updated_at", "last_access"}

        if policy.target_table not in allowed_tables:
            raise RetentionError(
                f"Invalid target table: {policy.target_table}",
                error_code="INVALID_TABLE",
            )

        if policy.target_column not in allowed_columns:
            raise RetentionError(
                f"Invalid target column: {policy.target_column}",
                error_code="INVALID_COLUMN",
            )

        # Build delete query with validated identifiers
        # nosec B608: Identifiers are validated against allowlists above.
        query = text(
            f"DELETE FROM {policy.target_table} WHERE {policy.target_column} < :cutoff_date"  # nosec B608
        )

        result = session.execute(query, {"cutoff_date": cutoff_date})
        return result.rowcount

    def get_retention_stats(self) -> Dict[str, Dict]:
        """Get statistics about data retention."""
        stats = {}

        try:
            with db_session() as session:
                # Analysis results stats
                now = datetime.now(timezone.utc)

                analysis_total = session.query(AnalysisResult).count()
                analysis_expired = (
                    session.query(AnalysisResult)
                    .filter(AnalysisResult.expires_at < now)
                    .count()
                )

                stats["analysis_results"] = {
                    "total": analysis_total,
                    "expired": analysis_expired,
                    "active": analysis_total - analysis_expired,
                }

                # Session stats
                session_total = session.query(UserSession).count()
                session_expired = (
                    session.query(UserSession)
                    .filter(UserSession.expires_at < now)
                    .count()
                )

                stats["sessions"] = {
                    "total": session_total,
                    "expired": session_expired,
                    "active": session_total - session_expired,
                }

                # Cache stats
                cache_total = session.query(CacheEntry).count()
                cache_expired = (
                    session.query(CacheEntry)
                    .filter(CacheEntry.expires_at < now)
                    .count()
                )

                stats["cache_entries"] = {
                    "total": cache_total,
                    "expired": cache_expired,
                    "active": cache_total - cache_expired,
                }

                # Audit log stats
                audit_total = session.query(AuditLog).count()
                stats["audit_logs"] = {"total": audit_total}

        except Exception as e:
            logger.error(f"Failed to get retention stats: {str(e)}")

        return stats

    def schedule_cleanup(self, policy_name: str, hours_from_now: int = 24) -> None:
        """Schedule cleanup for a specific policy."""
        try:
            with db_session() as session:
                policy = (
                    session.query(DataRetentionPolicy)
                    .filter(DataRetentionPolicy.name == policy_name)
                    .first()
                )

                if not policy:
                    raise RetentionError(
                        f"Policy '{policy_name}' not found",
                        error_code="POLICY_NOT_FOUND",
                    )

                policy.next_run = datetime.now(timezone.utc) + timedelta(
                    hours=hours_from_now
                )
                session.commit()

                logger.info(
                    f"Scheduled cleanup for policy '{policy_name}' in {hours_from_now} hours"
                )

        except Exception as e:
            logger.error(f"Failed to schedule cleanup: {str(e)}")
            raise RetentionError(
                f"Failed to schedule cleanup: {str(e)}", error_code="SCHEDULE_FAILED"
            ) from e

    def get_due_policies(self) -> List[DataRetentionPolicy]:
        """Get policies that are due for execution."""
        try:
            with db_session() as session:
                now = datetime.now(timezone.utc)
                due_policies = (
                    session.query(DataRetentionPolicy)
                    .filter(
                        DataRetentionPolicy.is_active.is_(True),
                        DataRetentionPolicy.next_run <= now,
                    )
                    .all()
                )

                return due_policies

        except Exception as e:
            logger.error(f"Failed to get due policies: {str(e)}")
            return []


class DataArchiver:
    """Handles data archival operations."""

    def __init__(self):
        """Initialize data archiver."""
        pass

    def archive_analysis_results(self, older_than_days: int = 90) -> int:
        """Archive old analysis results to JSON files."""
        # This would implement archival logic
        # For now, just return 0
        return 0

    def archive_audit_logs(self, older_than_days: int = 365) -> int:
        """Archive old audit logs."""
        # This would implement archival logic
        # For now, just return 0
        return 0
