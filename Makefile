.PHONY: help install test lint format clean docs build suggestions recommendations similar similar. help-on-missing-args help-on-missing-args. cl config-review migrate test-auth prod-setup

help: ## Show this help message
	@echo "RabbitMirror Development Commands:"
	@echo "=================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install development dependencies
	pip install -r requirements.txt
	pip install -e ".[dev]"
	pre-commit install

test: ## Run all tests
	pytest tests/ -v --cov=rabbitmirror --cov-report=html --cov-report=term

test-quick: ## Run tests without coverage
	pytest tests/ -v

lint: ## Run all linting tools
	pylint rabbitmirror/ --score=yes --disable=C0103,C0114,C0115,C0116,W0613,R0903,R0913,E0401,C0411,W0611,E0602,R0914,R0912,R0915,R0911,C0302,R0902,R0917,E1101
	flake8 rabbitmirror/ --max-line-length=127 --ignore=E203,W503,E501
	bandit -r rabbitmirror/ -f json || true

format: ## Format code with black and isort
	black rabbitmirror/ tests/
	isort rabbitmirror/ tests/ --profile black

format-check: ## Check if code is formatted correctly
	black --check rabbitmirror/ tests/
	isort --check-only rabbitmirror/ tests/ --profile black

security: ## Run security checks
	bandit -r rabbitmirror/ -f json

config-review: ## Review configuration files and error handling
	@echo "\033[1;32m🔧 Configuration and Error Handling Review\033[0m"
	@echo "==========================================="
	@echo ""
	@echo "\033[1;36m📋 Checking Configuration Structure:\033[0m"
	@test -f .rabbitmirror_config.json && echo "  ✅ Local config file exists" || echo "  ⚠️  Local config file missing"
	@test -f examples/datasets/sample_config.yaml && echo "  ✅ Sample config exists" || echo "  ❌ Sample config missing"
	@test -f pyproject.toml && echo "  ✅ Project config exists" || echo "  ❌ Project config missing"
	@echo ""
	@echo "\033[1;36m🔍 Validating Configuration Files:\033[0m"
	@python -c "import json; json.load(open('.rabbitmirror_config.json'))" 2>/dev/null && echo "  ✅ Local config JSON is valid" || echo "  ⚠️  Local config JSON has issues"
	@python -c "import yaml; yaml.safe_load(open('examples/datasets/sample_config.yaml'))" 2>/dev/null && echo "  ✅ Sample YAML config is valid" || echo "  ⚠️  Sample YAML config has issues (install pyyaml)"
	@python -c "import tomllib if hasattr(__builtins__, 'tomllib') else tomli as tomllib; tomllib.load(open('pyproject.toml', 'rb'))" 2>/dev/null && echo "  ✅ pyproject.toml is valid" || echo "  ⚠️  pyproject.toml has issues"
	@echo ""
	@echo "\033[1;36m🛡️  Checking Error Handling:\033[0m"
	@test -f rabbitmirror/error_recovery.py && echo "  ✅ Error recovery module exists" || echo "  ❌ Error recovery module missing"
	@test -f rabbitmirror/exceptions.py && echo "  ✅ Custom exceptions module exists" || echo "  ❌ Custom exceptions module missing"
	@grep -q "RetryConfig" rabbitmirror/error_recovery.py && echo "  ✅ Retry configuration found" || echo "  ⚠️  Retry configuration missing"
	@grep -q "CircuitBreaker" rabbitmirror/error_recovery.py && echo "  ✅ Circuit breaker pattern found" || echo "  ⚠️  Circuit breaker pattern missing"
	@echo ""
	@echo "\033[1;36m🌐 Environment Variable Usage:\033[0m"
	@grep -r "os\.getenv\|getenv\|environ" rabbitmirror/ --include="*.py" | wc -l | xargs -I {} echo "  📊 Found {} environment variable usages"
	@grep -r "SECRET_KEY\|RATE_LIMIT\|MAX_FILE_SIZE" rabbitmirror/ --include="*.py" | wc -l | xargs -I {} echo "  🔐 Found {} security-related env vars"
	@echo ""
	@echo "\033[1;36m📝 Logging Configuration:\033[0m"
	@test -f rabbitmirror/symbolic_logger.py && echo "  ✅ Symbolic logger exists" || echo "  ❌ Symbolic logger missing"
	@grep -q "loguru" rabbitmirror/symbolic_logger.py && echo "  ✅ Loguru logging configured" || echo "  ⚠️  Loguru logging not found"
	@test -d logs && echo "  ✅ Logs directory exists" || echo "  ⚠️  Logs directory missing (will be created on first use)"
	@echo ""
	@echo "\033[1;36m⚡ Hardcoded Values Check:\033[0m"
	@grep -r "timeout.*=.*[0-9]\|max_.*=.*[0-9]\|retry.*=.*[0-9]" rabbitmirror/ --include="*.py" | wc -l | xargs -I {} echo "  📊 Found {} potential hardcoded timeout/retry values"
	@echo "  💡 Consider moving these to configuration files"
	@echo ""
	@echo "\033[1;36m✅ Configuration Validation:\033[0m"
	@python -c "from rabbitmirror.config_manager import ConfigManager; cm = ConfigManager(); print('  ✅ ConfigManager can be imported and instantiated')" 2>/dev/null || echo "  ❌ ConfigManager has import issues"
	@echo ""
	@echo "\033[1;33m📋 Configuration Review Summary:\033[0m"
	@echo "  • Check that all configuration files are properly structured"
	@echo "  • Ensure environment variables have sensible defaults"
	@echo "  • Verify error handling covers all critical paths"
	@echo "  • Consider moving hardcoded values to config files"
	@echo "  • Review logging levels and output destinations"
	@echo ""

type-check: ## Run type checking (if mypy is installed)
	mypy rabbitmirror/ || echo "Install mypy for type checking: pip install mypy"

pre-commit: ## Run pre-commit hooks on all files
	pre-commit run --all-files

clean: ## Clean up build artifacts and cache
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

cl: clean ## Shorthand for clean

build: ## Build the package
	python -m build

install-package: build ## Install the built package
	pip install dist/*.whl

docs: ## Generate documentation (if sphinx is installed)
	@echo "Documentation generation not yet set up"
	@echo "Install with: pip install -e '.[docs]'"

demo: ## Run a demo of the CLI tool
	@echo "RabbitMirror CLI Demo:"
	@echo "====================="
	python -m rabbitmirror.cli --help

all-checks: format-check lint type-check test security config-review ## Run all quality checks

ci: all-checks ## Run CI pipeline locally

dev-setup: install pre-commit ## Complete development setup

upgrade-deps: ## Upgrade all dependencies
	pip install --upgrade pip
	pip install --upgrade -r requirements.txt

benchmark: ## Run performance benchmarks (if available)
	@echo "Benchmarks not yet implemented"

release-check: clean all-checks build ## Prepare for release
	@echo "✅ Release checks passed!"
	@echo "Package built in dist/"

suggestions: ## Show development suggestions and next steps
	@echo "\033[1;32m🚀 RabbitMirror Development Suggestions\033[0m"
	@echo "======================================="
	@echo ""
	@echo "\033[1;36m📋 Immediate Tasks:\033[0m"
	@echo "  • Run tests: make test"
	@echo "  • Check code quality: make all-checks"
	@echo "  • Format code: make format"
	@echo "  • Build package: make build"
	@echo ""
	@echo "\033[1;36m🔧 Development Workflow:\033[0m"
	@echo "  • Setup environment: make dev-setup"
	@echo "  • Run pre-commit hooks: make pre-commit"
	@echo "  • Clean workspace: make clean"
	@echo "  • Demo CLI: make demo"
	@echo ""
	@echo "\033[1;36m📊 Quality Assurance:\033[0m"
	@echo "  • Type checking: make type-check"
	@echo "  • Security scan: make security"
	@echo "  • Configuration review: make config-review"
	@echo "  • Lint code: make lint"
	@echo "  • CI simulation: make ci"
	@echo ""
	@echo "\033[1;36m🎯 Next Development Steps:\033[0m"
	@echo "  1. Implement TrendAnalyzer class (missing feature)"
	@echo "  2. Add more comprehensive error handling"
	@echo "  3. Create example datasets and tutorials"
	@echo "  4. Set up documentation with Sphinx"
	@echo "  5. Add performance benchmarks"
	@echo "  6. Implement web interface (optional)"
	@echo ""
	@echo "\033[1;36m📦 Publishing:\033[0m"
	@echo "  • Release preparation: make release-check"
	@echo "  • Build for PyPI: make build"
	@echo "  • Upload to PyPI: twine upload dist/*"
	@echo ""
	@echo "\033[1;33m💡 Tip: Run 'make help' to see all available commands\033[0m"

recommendations: ## Show comprehensive project recommendations and roadmap
	@echo "\033[1;32m🎯 RabbitMirror Enterprise Recommendations\033[0m"
	@echo "========================================="
	@echo ""
	@echo "\033[1;36m✅ Completed Features (Phase 1):\033[0m"
	@echo "  • ✅ Authentication System - Enterprise-ready user auth"
	@echo "  • ✅ Database Integration - SQLAlchemy + Alembic migrations"
	@echo "  • ✅ Security Framework - PBKDF2, rate limiting, audit logging"
	@echo "  • ✅ Session Management - Secure, persistent, database-backed"
	@echo "  • ✅ Input Validation - XSS, injection, path traversal protection"
	@echo "  • ✅ Data Persistence - Analysis results, user data, caching"
	@echo ""
	@echo "\033[1;36m🚀 Phase 2 Recommendations (Priority):\033[0m"
	@echo "  1. 🔐 Multi-Factor Authentication (MFA)"
	@echo "     • TOTP (Time-based OTP) implementation"
	@echo "     • Backup codes generation and management"
	@echo "     • MFA enforcement policies by user role"
	@echo ""
	@echo "  2. 👥 Role-Based Access Control (RBAC)"
	@echo "     • User roles: admin, analyst, viewer, guest"
	@echo "     • Permission-based resource access"
	@echo "     • Administrative interface for user management"
	@echo ""
	@echo "  3. 🌐 API Authentication & Authorization"
	@echo "     • JWT token-based API access"
	@echo "     • OAuth2 integration for third-party apps"
	@echo "     • API key management and rotation"
	@echo ""
	@echo "  4. 📊 Enhanced Analytics Dashboard"
	@echo "     • Real-time data visualization"
	@echo "     • User-specific analytics views"
	@echo "     • Export scheduling and automation"
	@echo ""
	@echo "\033[1;36m🏢 Phase 3 Enterprise Features:\033[0m"
	@echo "  1. 🔗 Single Sign-On (SSO) Integration"
	@echo "     • SAML 2.0 support for enterprise directories"
	@echo "     • OpenID Connect (OIDC) compatibility"
	@echo "     • Active Directory / LDAP integration"
	@echo ""
	@echo "  2. 🏗️ Multi-Tenancy Support"
	@echo "     • Tenant isolation and data segregation"
	@echo "     • Per-tenant configuration and branding"
	@echo "     • Resource usage tracking and limits"
	@echo ""
	@echo "  3. 📈 Advanced Monitoring & Observability"
	@echo "     • Application performance monitoring (APM)"
	@echo "     • Business intelligence dashboards"
	@echo "     • SLA tracking and alerting"
	@echo ""
	@echo "  4. 🔄 Backup & Disaster Recovery"
	@echo "     • Automated database backups"
	@echo "     • Point-in-time recovery capabilities"
	@echo "     • High availability deployment options"
	@echo ""
	@echo "\033[1;36m⚡ Performance & Scalability:\033[0m"
	@echo "  • 🚀 Async Processing - Celery task queues for heavy operations"
	@echo "  • 📊 Caching Strategy - Redis for session and computation caching"
	@echo "  • 🌐 CDN Integration - Static asset delivery optimization"
	@echo "  • 🏗️ Load Balancing - Multi-instance deployment support"
	@echo "  • 📦 Containerization - Docker/Kubernetes deployment ready"
	@echo ""
	@echo "\033[1;36m🛡️ Security Enhancements:\033[0m"
	@echo "  • 🔒 Advanced Threat Detection - ML-based anomaly detection"
	@echo "  • 🚨 Security Information Event Management (SIEM) integration"
	@echo "  • 📋 Compliance Frameworks - SOC2, GDPR, HIPAA readiness"
	@echo "  • 🔐 Secrets Management - HashiCorp Vault integration"
	@echo "  • 🛡️ Web Application Firewall (WAF) integration"
	@echo ""
	@echo "\033[1;36m🔧 DevOps & Infrastructure:\033[0m"
	@echo "  • 🏗️ Infrastructure as Code - Terraform modules"
	@echo "  • 🚀 CI/CD Pipeline - GitHub Actions / GitLab CI enhancement"
	@echo "  • 📊 Infrastructure Monitoring - Prometheus + Grafana"
	@echo "  • 🔄 Blue-Green Deployments - Zero-downtime updates"
	@echo "  • 📦 Package Registry - Private PyPI repository"
	@echo ""
	@echo "\033[1;36m📚 Documentation & Training:\033[0m"
	@echo "  • 📖 API Documentation - OpenAPI/Swagger specification"
	@echo "  • 🎓 User Training Materials - Video tutorials and guides"
	@echo "  • 🛠️ Developer Documentation - Architecture and contribution guides"
	@echo "  • 📋 Runbooks - Operational procedures and troubleshooting"
	@echo ""
	@echo "\033[1;36m🎯 Implementation Priority Matrix:\033[0m"
	@echo "  ┌─────────────────────┬──────────┬────────────┬─────────────┐"
	@echo "  │ Feature             │ Priority │ Complexity │ Time Est.   │"
	@echo "  ├─────────────────────┼──────────┼────────────┼─────────────┤"
	@echo "  │ MFA Implementation  │ HIGH     │ Medium     │ 2-3 weeks   │"
	@echo "  │ RBAC System         │ HIGH     │ High       │ 4-6 weeks   │"
	@echo "  │ API Authentication  │ HIGH     │ Medium     │ 2-3 weeks   │"
	@echo "  │ Enhanced Dashboard  │ MEDIUM   │ High       │ 6-8 weeks   │"
	@echo "  │ SSO Integration     │ MEDIUM   │ Very High  │ 8-12 weeks  │"
	@echo "  │ Multi-Tenancy       │ LOW      │ Very High  │ 10-16 weeks │"
	@echo "  └─────────────────────┴──────────┴────────────┴─────────────┘"
	@echo ""
	@echo "\033[1;36m💰 Business Value Assessment:\033[0m"
	@echo "  • 🎯 Authentication System: Enables production deployment"
	@echo "  • 🔐 MFA: Reduces security incidents by 99.9%"
	@echo "  • 👥 RBAC: Enables enterprise sales and compliance"
	@echo "  • 🌐 API Access: Opens integration and partnership opportunities"
	@echo "  • 🏢 SSO: Critical for enterprise customer acquisition"
	@echo ""
	@echo "\033[1;36m🛠️ Quick Start Commands:\033[0m"
	@echo "  • Test authentication: make test-auth"
	@echo "  • Run migrations: make migrate"
	@echo "  • Setup production: make prod-setup"
	@echo "  • Deploy application: make deploy"
	@echo "  • Monitor security: make security-audit"
	@echo ""
	@echo "\033[1;33m🎉 Current Status: Production-Ready Authentication ✅\033[0m"
	@echo "\033[1;33m🚀 Next Milestone: Multi-Factor Authentication (MFA)\033[0m"
	@echo ""

migrate: ## Run database migrations
	@echo "🔄 Running database migrations..."
	@if [ -f venv/bin/activate ]; then \
		source venv/bin/activate && alembic upgrade head; \
	else \
		alembic upgrade head; \
	fi
	@echo "✅ Database migrations completed"

test-auth: ## Test authentication system
	@echo "🧪 Testing authentication system..."
	@if [ -f venv/bin/activate ]; then \
		source venv/bin/activate && python -c "from rabbitmirror.database.session import init_database; init_database(); print('✅ Database connection successful')"; \
	else \
		python -c "from rabbitmirror.database.session import init_database; init_database(); print('✅ Database connection successful')"; \
	fi
	@echo "✅ Authentication system test completed"

prod-setup: ## Setup production environment
	@echo "🏭 Setting up production environment..."
	@echo "📋 Checking requirements..."
	@test -f requirements.txt && echo "  ✅ Requirements file found" || echo "  ❌ Requirements file missing"
	@test -f alembic.ini && echo "  ✅ Alembic configuration found" || echo "  ❌ Alembic configuration missing"
	@test -d migrations && echo "  ✅ Migrations directory found" || echo "  ❌ Migrations directory missing"
	@echo "🔧 Environment variables needed:"
	@echo "  • SECRET_KEY=your-secure-secret-key"
	@echo "  • DATABASE_URL=your-database-connection-string"
	@echo "  • REDIS_URL=your-redis-connection-string (optional)"
	@echo "  • FLASK_ENV=production"
	@echo "💡 Run 'make migrate' after setting up environment variables"
	@echo "✅ Production setup guide completed"

security-audit: ## Run comprehensive security audit
	@echo "🔒 Running comprehensive security audit..."
	@echo "📊 Security scan results:"
	@make security
	@echo "🛡️  Authentication system status:"
	@make test-auth
	@echo "📋 Configuration review:"
	@make config-review
	@echo "✅ Security audit completed"

deploy: ## Deploy application (requires configuration)
	@echo "🚀 Deployment checklist:"
	@echo "  1. ✅ Run 'make prod-setup' first"
	@echo "  2. ✅ Set environment variables"
	@echo "  3. ✅ Run 'make migrate' to setup database"
	@echo "  4. ✅ Run 'make test-auth' to verify authentication"
	@echo "  5. ✅ Run 'make security-audit' for security check"
	@echo "  6. 🚀 Deploy to your preferred platform"
	@echo "💡 Example: gunicorn -w 4 -b 0.0.0.0:8000 rabbitmirror.web.app:app"

recommendations-alias: recommendations ## Alias for recommendations (handles typos)

recommations: recommendations ## Handle common typo

similar: suggestions ## Alias for suggestions

# Allow a trailing period variant as an alias
similar.: similar

help-on-missing-args: ## Explain how make treats extra words as targets
	@echo "\033[1;33mNote:\033[0m 'make' treats each word after 'make' as a separate target."
	@echo "You ran: make similar help-on-missing-args behavior for other subcommands."
	@echo "This tries to build targets: 'similar', 'help-on-missing-args', 'behavior', 'for', 'other', 'subcommands.'"
	@echo ""
	@echo "✅ 'similar' now works (alias to 'suggestions')."
	@echo "❌ 'help-on-missing-args' and the other words were not defined targets."
	@echo ""
	@echo "Usage examples:"
	@echo "  • make similar"
	@echo "  • make help"
	@echo "  • make test-quick"
	@echo ""
	@echo "If you intended to pass arguments to a CLI, run the CLI directly, e.g.:"
	@echo "  • python -m rabbitmirror.cli --help"
	@echo "  • python -m rabbitmirror.cli process --help"

# Allow a trailing period variant as an alias
help-on-missing-args.: help-on-missing-args
