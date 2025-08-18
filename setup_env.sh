#!/bin/bash

# RabbitMirror Environment Setup Script
# This script loads environment variables from .env file and validates the setup

set -e  # Exit on any error

echo "🔧 Setting up RabbitMirror environment..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "Please create a .env file with the required environment variables."
    exit 1
fi

# Load environment variables from .env file
echo "📋 Loading environment variables from .env file..."
export $(grep -v '^#' .env | xargs)

echo "✅ Environment variables loaded successfully!"

# Validate critical environment variables
echo "🔍 Validating environment setup..."

if [ -z "$SECRET_KEY" ]; then
    echo "❌ ERROR: SECRET_KEY is not set!"
    exit 1
else
    echo "✅ SECRET_KEY is configured (${#SECRET_KEY} characters)"
fi

if [ -z "$DATABASE_URL" ]; then
    echo "❌ ERROR: DATABASE_URL is not set!"
    exit 1
else
    echo "✅ DATABASE_URL is configured: $DATABASE_URL"
fi

if [ -z "$FLASK_ENV" ]; then
    echo "⚠️  WARNING: FLASK_ENV is not set, defaulting to production"
    export FLASK_ENV=production
else
    echo "✅ FLASK_ENV is set to: $FLASK_ENV"
fi

# Create necessary directories
echo "📁 Creating necessary directories..."

mkdir -p uploads
echo "✅ uploads/ directory ready"

mkdir -p logs
echo "✅ logs/ directory ready"

mkdir -p exports
echo "✅ exports/ directory ready"

# Check if virtual environment is active
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  WARNING: No virtual environment detected!"
    echo "💡 Consider activating your virtual environment: source venv/bin/activate"
else
    echo "✅ Virtual environment active: $VIRTUAL_ENV"
fi

# Test database connection
echo "🧪 Testing database connection..."
if command -v python3 &> /dev/null; then
    python3 -c "
import os
try:
    from rabbitmirror.database.session import init_database
    from rabbitmirror.database.config import DatabaseConfig

    # Test database configuration
    config = DatabaseConfig.from_environment()
    print('✅ Database configuration loaded successfully')

    # Test database initialization
    init_database(config)
    print('✅ Database connection successful')
    print(f'✅ Database type: {\"SQLite\" if config.is_sqlite() else \"PostgreSQL\" if config.is_postgresql() else \"Other\"}')

except ImportError as e:
    print(f'⚠️  WARNING: Could not import database modules: {e}')
    print('💡 Make sure to install requirements: pip install -r requirements.txt')
except Exception as e:
    print(f'❌ Database connection failed: {e}')
    exit(1)
"
else
    echo "⚠️  WARNING: python3 not found, skipping database test"
fi

# Display configuration summary
echo ""
echo "📊 Environment Configuration Summary:"
echo "======================================="
echo "🔧 Flask Environment: $FLASK_ENV"
echo "🗄️  Database URL: $DATABASE_URL"
echo "🔐 Secret Key Length: ${#SECRET_KEY} characters"
echo "⏱️  Session Lifetime: ${SESSION_LIFETIME:-86400} seconds"
echo "🚀 Rate Limit: ${RATE_LIMIT_REQUESTS:-100} requests per ${RATE_LIMIT_WINDOW:-3600} seconds"
echo "📁 Max File Size: ${MAX_FILE_SIZE:-104857600} bytes"

if [ ! -z "$REDIS_URL" ]; then
    echo "🔴 Redis URL: $REDIS_URL"
else
    echo "🔴 Redis: Not configured (optional)"
fi

echo ""
echo "🎉 Environment setup completed successfully!"
echo ""
echo "🚀 Next steps:"
echo "  1. Run 'make migrate' to set up the database"
echo "  2. Run 'make test-auth' to verify authentication system"
echo "  3. Run 'make security-audit' for security validation"
echo "  4. Start the application with your preferred method"
echo ""
echo "💡 To use these environment variables in your current shell session:"
echo "   source setup_env.sh"
echo ""
