# Database Setup and Configuration Guide

This guide covers setting up and configuring the database and persistence layer for RabbitMirror.

## Quick Start

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Initialize database:**
```bash
python -m rabbitmirror.database.cli db init
```

3. **Check status:**
```bash
python -m rabbitmirror.database.cli db status
```

## Database Configuration

### Environment Variables

Configure the database using environment variables:

```bash
# Database connection
export DATABASE_URL="sqlite:///rabbitmirror.db"
# or for PostgreSQL:
# export DATABASE_URL="postgresql://user:password@localhost:5432/rabbitmirror"

# Database pool settings (PostgreSQL only)
export DATABASE_POOL_SIZE=10
export DATABASE_MAX_OVERFLOW=20
export DATABASE_POOL_TIMEOUT=30
export DATABASE_POOL_RECYCLE=3600

# Enable SQL echo for debugging
export DATABASE_ECHO=true

# Redis cache
export REDIS_URL="redis://localhost:6379/0"
export CACHE_TTL=3600

# Session configuration
export SESSION_LIFETIME=86400
export CLEANUP_INTERVAL=3600
```

### Supported Databases

#### SQLite (Default)
- **URL format:** `sqlite:///path/to/database.db`
- **Use case:** Development, small deployments
- **Features:** Automatic WAL mode, foreign key constraints enabled

#### PostgreSQL
- **URL format:** `postgresql://user:password@host:port/database`
- **Use case:** Production deployments
- **Features:** Connection pooling, full-text search, JSON operations

## Database Management Commands

### Initialize Database
```bash
# Initialize with default SQLite
python -m rabbitmirror.database.cli db init

# Initialize with custom database URL
python -m rabbitmirror.database.cli db init --database-url "postgresql://user:pass@localhost/rabbitmirror"

# Reset and reinitialize
python -m rabbitmirror.database.cli db init --reset
```

### Check Status
```bash
python -m rabbitmirror.database.cli db status
```

### Migrations
```bash
# Create a new migration
python -m rabbitmirror.database.cli db migrate -m "Add new column"

# Auto-generate migration from model changes
python -m rabbitmirror.database.cli db migrate -m "Auto migration" --autogenerate

# Apply migrations
python -m rabbitmirror.database.cli db upgrade

# Rollback migrations
python -m rabbitmirror.database.cli db downgrade <revision>
```

### Data Maintenance
```bash
# Run cleanup policies
python -m rabbitmirror.database.cli db cleanup

# Run specific policy
python -m rabbitmirror.database.cli db cleanup --policy analysis_results_cleanup

# Dry run to see what would be cleaned
python -m rabbitmirror.database.cli db cleanup --dry-run

# Clear cache
python -m rabbitmirror.database.cli db clear-cache

# Clear specific namespace
python -m rabbitmirror.database.cli db clear-cache --namespace analysis
```

### Database Shell
```bash
# Open database shell
python -m rabbitmirror.database.cli db shell
```

## Data Models

### Core Models

#### User
Stores user information and session management:
- `id`: UUID primary key
- `username`: Unique username (optional)
- `email`: Unique email (optional)
- `is_active`: Account status
- `password_hash`: Hashed password
- `last_login`: Last login timestamp
- `login_count`: Number of logins

#### Session
Persistent session storage:
- `id`: UUID primary key
- `session_id`: Unique session identifier
- `user_id`: Foreign key to User
- `data`: JSON session data
- `expires_at`: Session expiration
- `ip_address`: Client IP address
- `user_agent`: Client user agent

#### AnalysisResult
Stores analysis results with metadata:
- `id`: UUID primary key
- `user_id`: Foreign key to User
- `filename`: Original filename
- `file_hash`: SHA-256 hash of file
- `analysis_type`: Type of analysis (trend, cluster, pattern)
- `status`: Processing status (pending, completed, failed)
- `results`: JSON analysis results
- `summary`: JSON summary data
- `metadata`: Additional metadata
- `processing_time`: Processing duration in ms
- `expires_at`: Result expiration

#### CacheEntry
Distributed cache storage:
- `id`: UUID primary key
- `cache_key`: Cache key
- `namespace`: Cache namespace
- `data`: Cached data (binary)
- `data_type`: Data serialization type
- `ttl`: Time to live in seconds
- `expires_at`: Cache expiration
- `hit_count`: Access count

### Timestamps
All models include automatic timestamps:
- `created_at`: Record creation time
- `updated_at`: Record update time

## Caching Layer

### Redis Integration
- **Primary cache:** Redis for high-performance caching
- **Fallback:** Database cache for reliability
- **Automatic failover:** Seamless fallback when Redis unavailable

### Cache Usage
```python
from rabbitmirror.database import CacheManager

cache = CacheManager()

# Set cache value
cache.set('analysis_123', results, ttl=3600, namespace='analysis')

# Get cache value
results = cache.get('analysis_123', namespace='analysis')

# Check existence
if cache.exists('analysis_123', namespace='analysis'):
    # Use cached result
    pass

# Clear namespace
cache.clear_namespace('analysis')
```

## Data Retention and Cleanup

### Retention Policies
Default policies automatically clean up:
- **Analysis results:** 30 days
- **User sessions:** 7 days
- **Cache entries:** 1 day
- **Audit logs:** 90 days

### Custom Policies
Create custom retention policies:
```python
from rabbitmirror.database import RetentionManager
from rabbitmirror.database.models import DataRetentionPolicy

# Create custom policy
policy = DataRetentionPolicy(
    name='custom_cleanup',
    description='Clean up custom data',
    target_table='custom_table',
    target_column='expires_at',
    retention_days=14
)

# Schedule cleanup
retention_manager = RetentionManager()
retention_manager.schedule_cleanup('custom_cleanup', hours_from_now=24)
```

## Session Management

### Persistent Sessions
Replace Flask's default session with persistent storage:

```python
from rabbitmirror.database.models import Session, User
from rabbitmirror.database.session import db_session

# Create session
with db_session() as db:
    user_session = Session(
        session_id=session_id,
        user_id=user_id,
        data={'key': 'value'},
        expires_at=expiry_time,
        ip_address=request.remote_addr
    )
    db.add(user_session)
```

### Session Cleanup
Expired sessions are automatically cleaned up by retention policies.

## Performance Optimization

### Database Optimization
- **Connection pooling:** Configured for PostgreSQL
- **Query optimization:** Proper indexing on all models
- **JSON operations:** Efficient JSON queries for PostgreSQL

### Cache Optimization
- **Multi-layer caching:** Redis + database fallback
- **Namespace isolation:** Separate cache namespaces
- **Automatic expiration:** TTL-based cleanup

### Monitoring
```python
from rabbitmirror.database.session import DatabaseHealthCheck
from rabbitmirror.database.cache import CacheManager

# Database health
health = DatabaseHealthCheck()
if health.check_connection():
    info = health.get_connection_info()
    print(f"Pool size: {info['pool_size']}")

# Cache statistics
cache = CacheManager()
stats = cache.get_stats()
print(f"Redis available: {stats['redis_available']}")
```

## Security Considerations

### Data Protection
- **Password hashing:** Secure password storage
- **Session security:** Tamper-resistant session data
- **IP tracking:** Session IP validation
- **Audit logging:** Complete audit trail

### Access Control
- **User-based isolation:** Data scoped to users
- **Session validation:** Automatic session expiry
- **Input validation:** All data validated before storage

## Troubleshooting

### Common Issues

#### Connection Errors
```bash
# Check database status
python -m rabbitmirror.database.cli db status

# Verify database URL
echo $DATABASE_URL

# Test connection manually
python -c "from rabbitmirror.database.session import init_database; init_database()"
```

#### Migration Issues
```bash
# Check migration status
alembic current

# Reset migrations (DANGER: deletes data)
python -m rabbitmirror.database.cli db reset
```

#### Cache Issues
```bash
# Check Redis connection
redis-cli ping

# Clear all cache
python -m rabbitmirror.database.cli db clear-cache

# Check cache stats
python -c "from rabbitmirror.database.cache import CacheManager; print(CacheManager().get_stats())"
```

#### Performance Issues
- Monitor connection pool usage
- Check query performance with SQL logging
- Monitor cache hit rates
- Review retention policy frequency

### Logging
Enable detailed database logging:
```bash
export DATABASE_ECHO=true
export PYTHONPATH=.
python -m rabbitmirror.database.cli db status
```

## Migration from File-Based Storage

To migrate existing file-based data:

1. **Initialize database:**
```bash
python -m rabbitmirror.database.cli db init
```

2. **Create migration script:**
```python
# migration_script.py
from rabbitmirror.database import init_database, db_session
from rabbitmirror.database.models import AnalysisResult
import json
import os

init_database()

# Migrate existing JSON files
for filename in os.listdir('results/'):
    if filename.endswith('.json'):
        with open(f'results/{filename}') as f:
            data = json.load(f)

        with db_session() as session:
            result = AnalysisResult(
                filename=filename,
                analysis_type='trend',
                status='completed',
                results=data
            )
            session.add(result)
```

3. **Run migration:**
```bash
python migration_script.py
```

This completes the database and persistence implementation for RabbitMirror!
