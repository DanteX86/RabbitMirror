# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

Repository: RabbitMirror (Python, CLI + TUI + optional Flask web UI)
Status: No existing WARP.md detected; this is the initial version.

Environment assumptions
- macOS arm64; Python via Homebrew at /opt/homebrew/bin/python3
- Use a project-local venv named .venv
- Terminal supports colors (xterm-256color)

Quick start (one-time)
- Create venv and install dev dependencies:
  - /opt/homebrew/bin/python3 -m venv .venv
  - source .venv/bin/activate
  - python -m pip install -U pip setuptools wheel
  - python -m pip install -e .[dev]

Core tooling in this repo
- Task runners: Runfile (run) and lets.yaml (lets) are provided, but all raw equivalents are listed below to avoid external prerequisites.
- Packaging: pyproject.toml (setuptools), setup.py present. Console script: rabbitmirror => rabbitmirror.cli:main
- Tests: pytest configured in pyproject.toml under [tool.pytest.ini_options]
- Linters/formatters: black, isort, flake8, pylint; security: bandit; type-check: mypy
- CI: .github/workflows/quality.yml mirrors the local commands below

Common development commands
- Install (dev)
  - Raw: python -m pip install -e .[dev]
  - Runfile: run install
  - lets: lets install

- Test
  - All tests (quiet defaults come from pyproject):
    - Raw: pytest -v --cov=rabbitmirror --cov-report=term --cov-report=html
    - Runfile: run test (or run tests)
    - lets: lets test
  - Single file:
    - Raw: pytest tests/test_cli.py -v
  - Single test:
    - Raw: pytest tests/test_cli.py::TestCLI::test_cli_help -q

- Lint and format
  - Format (write):
    - Raw: black rabbitmirror/ tests/ && isort rabbitmirror/ tests/ --profile black
    - Runfile: run format
  - Format (check):
    - Raw: black --check rabbitmirror/ tests/ && isort --check-only rabbitmirror/ tests/ --profile black
    - Runfile: run format-check
  - Lint:
    - Raw: flake8 rabbitmirror/ tests/ --max-line-length=127 --ignore=E203,W503,E501
      and pylint rabbitmirror/ --exit-zero (config in Runfile)
    - Runfile: run lint
    - lets: lets lint

- Type-check
  - Raw: mypy rabbitmirror/
  - Runfile: run type-check

- Security
  - Raw: bandit -r rabbitmirror/
  - Runfile: run security (or part of run all-checks)

- Build (sdist + wheel)
  - Raw: python -m build
  - Runfile: run build

- Clean
  - Raw: rm -rf build/ dist/ *.egg-info/ htmlcov/ .coverage .pytest_cache/ && find . -type d -name __pycache__ -delete && find . -type f -name "*.pyc" -delete
  - Runfile: run clean

- Pre-commit
  - Raw: pre-commit install && pre-commit run --all-files
  - Runfile: run pre-commit

How to run the app
- CLI (primary interface)
  - rabbitmirror --help
  - Command groups (see README for details):
    - process: parse, batch-process
    - analyze: cluster, detect-patterns, analyze-suppression, simulate, trend-analysis
    - report: generate-report, export-dashboard
    - utils: convert, validate, generate-qr, completion
    - config: set, get, list
  - Examples:
    - Parse watch history to JSON:
      - rabbitmirror process parse watch-history.html -o parsed.json -f json
    - Cluster with visualization export:
      - rabbitmirror analyze cluster watch-history.html -o clusters.json -f json
    - Detect adversarial patterns:
      - rabbitmirror analyze detect-patterns watch-history.html -o patterns.json -f json --threshold 0.7
    - Suppression analysis:
      - rabbitmirror analyze analyze-suppression watch-history.html -o suppression.json -f json --period 30
    - Trend analysis and export YAML:
      - rabbitmirror analyze trend-analysis watch-history.html -o trends.yaml -f yaml --period weekly
    - Convert formats:
      - rabbitmirror utils convert parsed.json yaml -o parsed.yaml

- TUI (Textual-based; optional dependency already listed in requirements)
  - rabbitmirror tui
  - Themes: rabbitmirror tui --theme light
  - TUI help is built-in (H). Common flow: select file -> Quick Parse -> Quick Analysis -> View Results

- Web interface (Flask; optional for local use)
  - From repo root:
    - source .venv/bin/activate
    - python rabbitmirror/web/app.py
  - Default: http://localhost:5001/ (uploads to rabbitmirror/web/static/uploads)
  - Exposes analysis of uploaded files and exports via /export/<filename>/<format>

CSV and YAML export checks (user preference)
- After producing an export, quick assertions:
  - CSV basic check:
    - python - <<'PY'
import csv, sys, pathlib as p
f = p.Path('output.csv'); r = list(csv.DictReader(f.open()))
assert isinstance(r, list)
print('rows=', len(r)); print('headers=', r[0].keys() if r else [])
PY
  - YAML basic check:
    - python - <<'PY'
import yaml, sys
with open('output.yaml') as fh:
    d = yaml.safe_load(fh)
assert isinstance(d, (dict, list))
print('yaml-ok')
PY
- In pytest (example pattern):
  - pytest -q -k export  # project already includes tests for CLI subcommands producing JSON; adapt as needed for CSV/YAML

High-level architecture (big picture)
- Entry points
  - CLI (rabbitmirror.cli) defines command groups: process, analyze, report, utils, config. Each command orchestrates core services.
  - TUI (rabbitmirror.tui) wraps the same core analyzers behind an interactive interface.
  - Web (rabbitmirror/web/app.py) exposes selected analysis flows over HTTP using Flask.

- Core pipeline (modules)
  - Parsing: HistoryParser (rabbitmirror.parser) reads Google Takeout watch-history.html into normalized entries.
  - Analysis engines:
    - ClusterEngine (rabbitmirror.cluster_engine): DBSCAN-based clustering and related summaries.
    - AdversarialProfiler (rabbitmirror.adversarial_profiler): pattern detection and risk indicators.
    - SuppressionIndex (rabbitmirror.suppression_index): calculates suppression metrics over time windows.
    - TrendAnalyzer (rabbitmirror.trend_analyzer): computes periodized metrics and detects significant changes.
    - ProfileSimulator (rabbitmirror.profile_simulator): synthesizes profiles from inputs.
  - Export/report:
    - ExportFormatter (rabbitmirror.export_formatter): JSON, CSV, YAML, Excel export; also used for conversions.
    - Dashboard/Report generation (rabbitmirror.dashboard_generator, rabbitmirror.report_generator): produce HTML dashboards/reports.
  - Configuration/logging/errors:
    - ConfigManager centralizes local/global config operations (CLI config group mirrors this).
    - SymbolicLogger and rich/Click messages surface human-readable errors; typed exceptions in rabbitmirror.exceptions map errors to CLI exits.

- Data flow
  - Inputs (HTML/JSON) -> parse -> in-memory normalized entries -> analysis engines -> structured results -> optional exports (JSON/CSV/YAML/Excel) and/or HTML dashboards -> CLI/TUI/Web present to user.

CI parity and hooks
- Local commands approximate CI (see .github/workflows/quality.yml):
  - black --check, isort --check-only, flake8, pylint, bandit, mypy
  - Build validation with python -m build
- Pre-commit hooks configured in .pre-commit-config.yaml; to mirror CI locally:
  - pre-commit install
  - pre-commit run --all-files

Troubleshooting notes (macOS arm64)
- Ensure you’re using the venv’s Python (which python should resolve inside .venv/bin)
- If PATH in Warp lacks Homebrew init, start a login shell so ~/.zprofile is applied: exec zsh -l
- If Textual or Flask is missing, ensure dev install was used: python -m pip install -e .[dev]
- For tests involving pandas/scikit-learn on M-series Macs, verify wheels installed by using a current pip (python -m pip install -U pip)

References in repo for details
- pyproject.toml: pytest, black, isort, mypy, coverage settings
- Runfile: curated dev commands (test, lint, format, build, etc.)
- lets.yaml: alternative command aliases
- README.md: end-user CLI/TUI usage, examples, and parameters
- WEB_INTERFACE.md: additional usage for the Flask UI
- .pre-commit-config.yaml and .github/workflows/quality.yml: quality gates mirrored above
