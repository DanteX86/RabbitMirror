.PHONY: help install test lint format clean docs build

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

all-checks: format-check lint test security ## Run all quality checks

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
