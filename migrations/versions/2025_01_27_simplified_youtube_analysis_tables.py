"""Simplified YouTube analysis tables - removed multi-user complexity

Revision ID: simplified_youtube_analysis
Revises: 398a6ce9cf4a
Create Date: 2025-01-27 12:00:00.000000

This migration simplifies the database schema for single-user YouTube history analysis:
- Removes User, Session, and AuditLog tables (multi-user complexity)
- Renames AnalysisResult to YouTubeAnalysis (more specific)
- Keeps CacheEntry and DataRetentionPolicy tables (still useful)
"""
import sqlalchemy as sa
import sqlalchemy_utils
from alembic import op

# revision identifiers, used by Alembic.
revision = "simplified_youtube_analysis"
down_revision = "398a6ce9cf4a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop tables that are no longer needed for single-user mode

    # Drop sessions table (complex session management not needed)
    op.drop_index(op.f("ix_sessions_user_id"), table_name="sessions")
    op.drop_index(op.f("ix_sessions_updated_at"), table_name="sessions")
    op.drop_index(op.f("ix_sessions_session_id"), table_name="sessions")
    op.drop_index(op.f("ix_sessions_ip_address"), table_name="sessions")
    op.drop_index(op.f("ix_sessions_expires_at"), table_name="sessions")
    op.drop_index(op.f("ix_sessions_created_at"), table_name="sessions")
    op.drop_table("sessions")

    # Drop audit_logs table (simple file logging is sufficient)
    op.drop_index(op.f("ix_audit_logs_user_id"), table_name="audit_logs")
    op.drop_index(op.f("ix_audit_logs_updated_at"), table_name="audit_logs")
    op.drop_index(op.f("ix_audit_logs_severity"), table_name="audit_logs")
    op.drop_index(op.f("ix_audit_logs_event_type"), table_name="audit_logs")
    op.drop_index(op.f("ix_audit_logs_created_at"), table_name="audit_logs")
    op.drop_table("audit_logs")

    # Drop users table (single-user mode doesn't need user management)
    op.drop_index(op.f("ix_analysis_results_user_id"), table_name="analysis_results")
    op.drop_index(op.f("ix_users_username"), table_name="users")
    op.drop_index(op.f("ix_users_updated_at"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_index(op.f("ix_users_created_at"), table_name="users")
    op.drop_table("users")

    # Rename analysis_results to youtube_analyses and remove user_id foreign key
    op.rename_table("analysis_results", "youtube_analyses")

    # Remove user_id column from youtube_analyses (no longer needed)
    op.drop_column("youtube_analyses", "user_id")

    # Keep cache_entries table (useful for performance)
    # Keep data_retention_policies table (useful for cleanup)


def downgrade() -> None:
    # This downgrade recreates the original complex multi-user schema

    # Recreate users table
    op.create_table(
        "users",
        sa.Column(
            "id", sqlalchemy_utils.types.uuid.UUIDType(binary=False), nullable=False
        ),
        sa.Column("username", sa.String(length=255), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("last_login", sa.DateTime(timezone=True), nullable=True),
        sa.Column("login_count", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_created_at"), "users", ["created_at"], unique=False)
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_updated_at"), "users", ["updated_at"], unique=False)
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=True)

    # Add user_id column back to youtube_analyses
    op.add_column(
        "youtube_analyses",
        sa.Column(
            "user_id", sqlalchemy_utils.types.uuid.UUIDType(binary=False), nullable=True
        ),
    )
    op.create_index(
        op.f("ix_analysis_results_user_id"),
        "youtube_analyses",
        ["user_id"],
        unique=False,
    )
    op.create_foreign_key(None, "youtube_analyses", "users", ["user_id"], ["id"])

    # Rename youtube_analyses back to analysis_results
    op.rename_table("youtube_analyses", "analysis_results")

    # Recreate audit_logs table
    op.create_table(
        "audit_logs",
        sa.Column(
            "id", sqlalchemy_utils.types.uuid.UUIDType(binary=False), nullable=False
        ),
        sa.Column(
            "user_id", sqlalchemy_utils.types.uuid.UUIDType(binary=False), nullable=True
        ),
        sa.Column("event_type", sa.String(length=50), nullable=False),
        sa.Column("event_description", sa.Text(), nullable=True),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.Column("request_path", sa.String(length=255), nullable=True),
        sa.Column("event_data", sa.JSON(), nullable=True),
        sa.Column("severity", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_audit_logs_created_at"), "audit_logs", ["created_at"], unique=False
    )
    op.create_index(
        op.f("ix_audit_logs_event_type"), "audit_logs", ["event_type"], unique=False
    )
    op.create_index(
        op.f("ix_audit_logs_severity"), "audit_logs", ["severity"], unique=False
    )
    op.create_index(
        op.f("ix_audit_logs_updated_at"), "audit_logs", ["updated_at"], unique=False
    )
    op.create_index(
        op.f("ix_audit_logs_user_id"), "audit_logs", ["user_id"], unique=False
    )

    # Recreate sessions table
    op.create_table(
        "sessions",
        sa.Column(
            "id", sqlalchemy_utils.types.uuid.UUIDType(binary=False), nullable=False
        ),
        sa.Column("session_id", sa.String(length=255), nullable=False),
        sa.Column(
            "user_id", sqlalchemy_utils.types.uuid.UUIDType(binary=False), nullable=True
        ),
        sa.Column("data", sa.JSON(), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_sessions_created_at"), "sessions", ["created_at"], unique=False
    )
    op.create_index(
        op.f("ix_sessions_expires_at"), "sessions", ["expires_at"], unique=False
    )
    op.create_index(
        op.f("ix_sessions_ip_address"), "sessions", ["ip_address"], unique=False
    )
    op.create_index(
        op.f("ix_sessions_session_id"), "sessions", ["session_id"], unique=True
    )
    op.create_index(
        op.f("ix_sessions_updated_at"), "sessions", ["updated_at"], unique=False
    )
    op.create_index(op.f("ix_sessions_user_id"), "sessions", ["user_id"], unique=False)
