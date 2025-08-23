"""
Database management CLI commands for RabbitMirror.

Provides command-line interface for database operations including
initialization, migrations, cleanup, and maintenance.
"""

import os
import subprocess  # nosec B404 - usage constrained and shell is not used
import sys
from pathlib import Path
from typing import Optional

import click

from .cache import CacheManager
from .config import DatabaseConfig
from .retention import RetentionManager
from .session import DatabaseHealthCheck, init_database, reset_database


@click.group()
def db():
    """Database management commands."""
    pass


@db.command()
@click.option("--database-url", help="Database URL (overrides environment)")
@click.option("--reset", is_flag=True, help="Reset existing database")
def init(database_url: Optional[str], reset: bool):
    """Initialize the database."""
    try:
        # Set database URL if provided
        if database_url:
            os.environ["DATABASE_URL"] = database_url

        config = DatabaseConfig.from_environment()

        if reset:
            click.echo("Resetting database...")
            reset_database()

        click.echo("Initializing database...")
        init_database(config)

        # Create default retention policies
        retention_manager = RetentionManager()
        retention_manager.create_default_policies()

        click.echo(f"✅ Database initialized successfully: {config.database_url}")

    except Exception as e:
        click.echo(f"❌ Database initialization failed: {str(e)}", err=True)
        sys.exit(1)


@db.command()
def status():
    """Check database status."""
    try:
        health_check = DatabaseHealthCheck()

        # Connection status
        if health_check.check_connection():
            click.echo("✅ Database connection: OK")
        else:
            click.echo("❌ Database connection: FAILED")
            return

        # Connection info
        info = health_check.get_connection_info()
        click.echo(f"Database URL: {info.get('url', 'Unknown')}")
        click.echo(f"Pool size: {info.get('pool_size', 'N/A')}")
        click.echo(f"Checked out: {info.get('checked_out', 'N/A')}")

        # Cache status
        cache_manager = CacheManager()
        cache_stats = cache_manager.get_stats()

        click.echo("\nCache Status:")
        click.echo(f"Redis available: {cache_stats['redis_available']}")
        click.echo(f"Database cache entries: {cache_stats['database_entries']}")

        if cache_stats["redis_available"]:
            redis_info = cache_stats.get("redis_info", {})
            click.echo(f"Redis memory used: {redis_info.get('used_memory', 'Unknown')}")
            click.echo(f"Redis keyspace hits: {redis_info.get('keyspace_hits', 0)}")
            click.echo(f"Redis keyspace misses: {redis_info.get('keyspace_misses', 0)}")

    except Exception as e:
        click.echo(f"❌ Status check failed: {str(e)}", err=True)
        sys.exit(1)


@db.command()
@click.option("--message", "-m", required=True, help="Migration message")
@click.option(
    "--autogenerate", is_flag=True, help="Auto-generate migration from model changes"
)
def migrate(message: str, autogenerate: bool):
    """Create a new database migration."""
    try:
        # Ensure alembic is available
        project_root = Path(__file__).parent.parent.parent
        alembic_ini = project_root / "alembic.ini"

        if not alembic_ini.exists():
            click.echo(
                "❌ alembic.ini not found. Run 'alembic init migrations' first.",
                err=True,
            )
            sys.exit(1)

        # Build alembic command
        cmd = ["alembic", "revision", "-m", message]
        if autogenerate:
            cmd.append("--autogenerate")

        # Run alembic command
        # Inputs come from CLI options with constrained values; shell is not used.
        result = subprocess.run(
            cmd, cwd=project_root, capture_output=True, text=True
        )  # nosec B603

        if result.returncode == 0:
            click.echo(f"✅ Migration created: {message}")
            if result.stdout:
                click.echo(result.stdout)
        else:
            click.echo(f"❌ Migration creation failed: {result.stderr}", err=True)
            sys.exit(1)

    except FileNotFoundError:
        click.echo("❌ Alembic not found. Install with: pip install alembic", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Migration failed: {str(e)}", err=True)
        sys.exit(1)


@db.command()
@click.option("--revision", help="Target revision (default: head)")
def upgrade(revision: Optional[str]):
    """Apply database migrations."""
    try:
        project_root = Path(__file__).parent.parent.parent

        cmd = ["alembic", "upgrade", revision or "head"]
        # Inputs come from CLI options with constrained values; shell is not used.
        result = subprocess.run(
            cmd, cwd=project_root, capture_output=True, text=True
        )  # nosec B603

        if result.returncode == 0:
            click.echo("✅ Database upgraded successfully")
            if result.stdout:
                click.echo(result.stdout)
        else:
            click.echo(f"❌ Database upgrade failed: {result.stderr}", err=True)
            sys.exit(1)

    except FileNotFoundError:
        click.echo("❌ Alembic not found. Install with: pip install alembic", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Upgrade failed: {str(e)}", err=True)
        sys.exit(1)


@db.command()
@click.option("--revision", help="Target revision")
def downgrade(revision: str):
    """Rollback database migrations."""
    try:
        project_root = Path(__file__).parent.parent.parent

        cmd = ["alembic", "downgrade", revision]
        # Inputs come from CLI options with constrained values; shell is not used.
        result = subprocess.run(
            cmd, cwd=project_root, capture_output=True, text=True
        )  # nosec B603

        if result.returncode == 0:
            click.echo("✅ Database downgraded successfully")
            if result.stdout:
                click.echo(result.stdout)
        else:
            click.echo(f"❌ Database downgrade failed: {result.stderr}", err=True)
            sys.exit(1)

    except FileNotFoundError:
        click.echo("❌ Alembic not found. Install with: pip install alembic", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Downgrade failed: {str(e)}", err=True)
        sys.exit(1)


@db.command()
@click.option("--policy", help="Specific policy to run")
@click.option(
    "--dry-run", is_flag=True, help="Show what would be cleaned up without doing it"
)
def cleanup(policy: Optional[str], dry_run: bool):
    """Run data retention cleanup."""
    try:
        retention_manager = RetentionManager()

        if dry_run:
            stats = retention_manager.get_retention_stats()
            click.echo("Retention Statistics:")
            for table, data in stats.items():
                if isinstance(data, dict):
                    expired = data.get("expired", 0)
                    total = data.get("total", 0)
                    click.echo(f"  {table}: {expired} expired out of {total} total")
                else:
                    click.echo(f"  {table}: {data} total")
            return

        click.echo("Running data retention cleanup...")
        results = retention_manager.run_cleanup(policy)

        total_cleaned = 0
        for policy_name, count in results.items():
            if count >= 0:
                click.echo(f"✅ {policy_name}: cleaned up {count} records")
                total_cleaned += count
            else:
                click.echo(f"❌ {policy_name}: failed")

        click.echo(f"\n✅ Total records cleaned up: {total_cleaned}")

    except Exception as e:
        click.echo(f"❌ Cleanup failed: {str(e)}", err=True)
        sys.exit(1)


@db.command()
@click.option("--namespace", help="Cache namespace to clear")
def clear_cache(namespace: Optional[str]):
    """Clear cache entries."""
    try:
        cache_manager = CacheManager()

        if namespace:
            count = cache_manager.clear_namespace(namespace)
            click.echo(f"✅ Cleared {count} entries from namespace '{namespace}'")
        else:
            # Clear all common namespaces
            namespaces = ["default", "analysis", "trends", "clusters", "patterns"]
            total_cleared = 0

            for ns in namespaces:
                count = cache_manager.clear_namespace(ns)
                if count > 0:
                    click.echo(f"✅ Cleared {count} entries from namespace '{ns}'")
                    total_cleared += count

            # Also clean up expired entries
            expired_count = cache_manager.cleanup_expired()
            total_cleared += expired_count

            click.echo(f"\n✅ Total cache entries cleared: {total_cleared}")

    except Exception as e:
        click.echo(f"❌ Cache clear failed: {str(e)}", err=True)
        sys.exit(1)


@db.command()
@click.confirmation_option(prompt="Are you sure you want to reset the database?")
def reset():
    """Reset the database (WARNING: This will delete all data)."""
    try:
        click.echo("Resetting database...")
        reset_database()

        # Recreate default policies
        retention_manager = RetentionManager()
        retention_manager.create_default_policies()

        click.echo("✅ Database reset successfully")

    except Exception as e:
        click.echo(f"❌ Database reset failed: {str(e)}", err=True)
        sys.exit(1)


@db.command()
def shell():
    """Open database shell."""
    try:
        config = DatabaseConfig.from_environment()

        if config.is_sqlite():
            # SQLite shell
            db_path = config.database_url.replace("sqlite:///", "")
            cmd = ["sqlite3", db_path]
        elif config.is_postgresql():
            # PostgreSQL shell
            cmd = ["psql", config.database_url]
        else:
            click.echo(
                "❌ Database shell not supported for this database type", err=True
            )
            sys.exit(1)

        click.echo(f"Opening database shell for: {config.database_url}")
        # Interactive DB shells are user-invoked; arguments are constructed safely.
        subprocess.run(cmd)  # nosec B603

    except FileNotFoundError as e:
        click.echo(f"❌ Database client not found: {e.filename}", err=True)
        click.echo("Install the appropriate database client (sqlite3, psql, etc.)")
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Shell failed: {str(e)}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    db()
