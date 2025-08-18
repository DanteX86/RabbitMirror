.PHONY: help install test lint format clean docs build suggestions cl venv-shell ensure-venv venv-pip-upgrade

# Venv settings
VENV_DIR ?= .venv
PYTHON ?= /opt/homebrew/bin/python3
VENV_BIN := $(VENV_DIR)/bin

help: ## Show this help message
	@echo "RabbitMirror Development Commands:"
	@echo "=================================="
	@grep -E '^[a-zA-Z_.-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ensure-venv ## Install development dependencies
	"$(VENV_BIN)/pip" install --upgrade pip
	@if [ -f requirements.txt ]; then "$(VENV_BIN)/pip" install -r requirements.txt; fi
	"$(VENV_BIN)/pip" install -e ".[dev]"
	"$(VENV_BIN)/pre-commit" install

test: ensure-venv ## Run all tests
	"$(VENV_BIN)/pytest" tests/ -v --cov=rabbitmirror --cov-report=html --cov-report=term

test-quick: ensure-venv ## Run tests without coverage
	"$(VENV_BIN)/pytest" tests/ -v

lint: ensure-venv ## Run all linting tools
	"$(VENV_BIN)/pylint" rabbitmirror/ --score=yes --disable=C0103,C0114,C0115,C0116,W0613,R0903,R0913,E0401,C0411,W0611,E0602,R0914,R0912,R0915,R0911,C0302,R0902,R0917,E1101
	"$(VENV_BIN)/flake8" rabbitmirror/ --max-line-length=127 --ignore=E203,W503,E501
	"$(VENV_BIN)/bandit" -r rabbitmirror/ -f json || true

format: ensure-venv ## Format code with black and isort
	"$(VENV_BIN)/black" rabbitmirror/ tests/
	"$(VENV_BIN)/isort" rabbitmirror/ tests/ --profile black

format-check: ensure-venv ## Check if code is formatted correctly
	"$(VENV_BIN)/black" --check rabbitmirror/ tests/
	"$(VENV_BIN)/isort" --check-only rabbitmirror/ tests/ --profile black

security: ensure-venv ## Run security checks
	"$(VENV_BIN)/bandit" -r rabbitmirror/ -f json

type-check: ensure-venv ## Run type checking (if mypy is installed)
	"$(VENV_BIN)/mypy" rabbitmirror/ || echo "Install mypy for type checking: $(VENV_BIN)/pip install mypy"

pre-commit: ensure-venv ## Run pre-commit hooks on all files
	"$(VENV_BIN)/pre-commit" run --all-files

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

build: ensure-venv ## Build the package
	"$(VENV_BIN)/python" -m build

install-package: build ## Install the built package
	"$(VENV_BIN)/pip" install dist/*.whl

docs: ## Generate documentation (if sphinx is installed)
	@echo "Documentation generation not yet set up"
	@echo "Install with: $(VENV_BIN)/pip install -e '.[docs]'"

demo: ensure-venv ## Run a demo of the CLI tool
	@echo "RabbitMirror CLI Demo:"
	@echo "====================="
	"$(VENV_BIN)/python" -m rabbitmirror.cli --help

all-checks: format-check lint type-check test security ## Run all quality checks

ci: all-checks ## Run CI pipeline locally

dev-setup: install pre-commit ## Complete development setup

upgrade-deps: ensure-venv ## Upgrade all dependencies
	"$(VENV_BIN)/pip" install --upgrade pip
	"$(VENV_BIN)/pip" install --upgrade -r requirements.txt

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

# Venv helpers
ensure-venv:
	@if [ ! -d "$(VENV_DIR)" ]; then echo "Creating venv in $(VENV_DIR) with $(PYTHON)"; "$(PYTHON)" -m venv "$(VENV_DIR)"; fi

venv-pip-upgrade: ensure-venv
	"$(VENV_BIN)/python" -m pip install --upgrade pip

venv-shell: ensure-venv ## Open a subshell with the venv activated
	@echo "Activating virtual environment at $(VENV_DIR). Exit the shell to deactivate."
	@. "$(VENV_BIN)/activate"; exec "$(SHELL)" -l

# Convenience aliases
.PHONY: similar similar.
similar: suggestions ## Alias for 'suggestions'
	@true

similar.: suggestions ## Alias for 'suggestions' (handles trailing dot)
	@true

# Demo workflow: parse → analyze → patterns → combine → report
.PHONY: demo-workflow
_demo_python := /Users/romulusaugustus/Documents/RabbitMirror/.venv/bin/python

demo-workflow: ## Run end-to-end demo (parse, analyze, patterns, report)
	@echo "\n==> Ensuring output directories exist"
	@mkdir -p exports report_output templates
	@echo "\n==> Parsing watch-history.html"
	@$(_demo_python) -m rabbitmirror.cli process parse watch-history.html youtube -o exports/parsed.json -f json
	@echo "\n==> Clustering entries"
	@$(_demo_python) -m rabbitmirror.cli analyze cluster watch-history.html --eps 0.3 --min-samples 5 -o exports/clusters.json -f json
	@echo "\n==> Detecting adversarial patterns"
	@$(_demo_python) -m rabbitmirror.cli analyze detect-patterns watch-history.html --threshold 0.7 -o exports/patterns.json -f json
	@echo "\n==> Combining outputs into a single data file"
	@$(_demo_python) scripts/combine_demo.py
	@echo "\n==> Preparing report template"
	@test -f templates/demo_report.html || cp demo_report.html templates/demo_report.html || true
	@echo "\n==> Generating HTML report"
	@$(_demo_python) -m rabbitmirror.cli report generate-report exports/demo_data.json templates/demo_report.html report_output/demo_report.html -f html
	@echo "\n✅ Demo workflow complete. View report_output/demo_report.html"
	@echo "REPORT_PATH=report_output/demo_report.html"
