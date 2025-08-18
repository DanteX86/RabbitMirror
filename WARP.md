# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

- Repository: RabbitMirror — Advanced YouTube Watch History Analysis Tool
- Language/Tooling: Python 3.9+, pytest, click CLI, Textual TUI, Flask (optional web)
- Entry points: CLI (rabbitmirror), TUI (rabbitmirror tui), dev scripts via Makefile

1) Common commands

Environment setup
- Install dev deps and hooks: make dev-setup
- Install package editable with dev extras: pip install -e .[dev]
- Upgrade dependencies: make upgrade-deps
- Show available commands: make help

Run
- Launch TUI (dark/light): rabbitmirror tui | rabbitmirror tui --theme light
- CLI help and groups: rabbitmirror --help; rabbitmirror process --help; rabbitmirror analyze --help; rabbitmirror report --help; rabbitmirror config --help; rabbitmirror utils --help
- Parse a history file: rabbitmirror process parse watch-history.html --output parsed.json
- Cluster analysis: rabbitmirror analyze cluster watch-history.html --output clusters.json
- Detect patterns: rabbitmirror analyze detect-patterns watch-history.html --threshold 0.7 --output patterns.json
- Suppression analysis: rabbitmirror analyze analyze-suppression watch-history.html --period 30 --output suppression.json
- Profile simulation: rabbitmirror analyze simulate watch-history.html --duration 30 --output simulated_profile.json
- Generate report (CLI): rabbitmirror report generate-report data.json template.html report.html --format html --theme dark

Build/Package
- Build package: make build (python -m build)
- Install built wheel: make install-package
- Clean artifacts: make clean (or make cl)

Lint/Format/Type/Security
- Lint (pylint/flake8/bandit): make lint
- Auto-format: make format
- Check formatting only: make format-check
- Type checking (mypy): make type-check
- Security scan (bandit): make security
- Run all local CI checks: make all-checks or make ci

Tests
- Run full test suite with coverage: make test
- Quick tests (no coverage): make test-quick
- Single file: pytest tests/test_cluster_engine.py -v
- Single test: pytest tests/test_cluster_engine.py::TestClusterEngine::test_cluster_videos_with_sample_data -v
- Respect repo pytest config: see pytest.ini and pyproject.toml [tool.pytest.ini_options]

GitHub Actions reference (read-only)
- CI/CD: .github/workflows/ci.yml — matrix tests 3.9–3.12, lint, bandit, coverage upload
- Tests: .github/workflows/test.yml — type check (mypy), pytest, coverage
- Code Quality: .github/workflows/quality.yml — black, isort, flake8, pylint, bandit, mypy

2) High-level architecture and structure

Overview
- Multi-interface tool with shared analysis core:
  - CLI: rabbitmirror.cli (click) exposed via console script rabbitmirror
  - TUI: textual app (rabbitmirror tui) for guided workflows and live feedback
  - Web (optional): Flask app under rabbitmirror/web for local dashboard
- Core modules operate on parsed YouTube watch-history data and produce structured results (JSON/CSV/YAML/Excel) and reports (HTML/MD).

Key modules and roles
- Parser: rabbitmirror/parser.py — converts Google Takeout watch-history HTML to structured records
- Analysis engines:
  - ClusterEngine (rabbitmirror/cluster_engine.py) — groups videos; DBSCAN/KMeans-style parameters (eps, min-samples)
  - AdversarialProfiler (rabbitmirror/adversarial_profiler.py) — detects manipulation patterns
  - SuppressionIndex (rabbitmirror/suppression_index.py) — baseline vs. deviation suppression metrics
  - ProfileSimulator (rabbitmirror/profile_simulator.py) — synthetic viewing profiles
  - (Trend analysis is referenced in docs; verify module presence before use)
- Reporting/Export:
  - export_formatter.py — JSON/CSV/YAML/Excel serialization
  - report_generator.py — report creation; Jinja2/Plotly supported
  - qr_generator.py — QR code utilities
- Configuration: config_manager.py — layered config (CLI args > local .rabbitmirror_config.json > global ~/.rabbitmirror_config.json > defaults); supports JSON/YAML; schema validation via jsonschema
- Logging: symbolic_logger.py — centralized logging patterns
- CLI/TUI integration: cli.py wires command groups; TUI (Textual) orchestrates parse→analyze→view with progress and notifications
- Web: rabbitmirror/web (Flask) with templates/static for a local UI; optional extra [project.optional-dependencies.web]

Data flow
- Input: watch-history HTML (Google Takeout) → Parser → normalized dataset
- Processing: dataset → analysis engines (cluster, detect-patterns, suppression, simulate, optional trend)
- Output: results and reports via export_formatter/report_generator (JSON/CSV/YAML/Excel/HTML)
- Interfaces: CLI commands and TUI actions call the same underlying modules; web interface uses the same core from Flask views

Configuration system
- Files: local ./.rabbitmirror_config.json overrides global ~/.rabbitmirror_config.json
- Priority: CLI args > local > global > defaults
- Common toggles: default_output_format, analysis thresholds, clustering params, performance knobs (max_workers), logging
- Env support: RABBITMIRROR_* variables (see docs/configuration.md)

Conventions and quality gates (from repo configs)
- Python version: requires-python >= 3.9 (pyproject)
- Linting thresholds and ignores are encoded in Makefile and tool configs
- Coverage gates: pytest.ini sets --cov-fail-under=70; pyproject sets coverage.report fail_under=80 for local tools — respect both when running different entry points
- Bandit skips: B101, B601; exclude tests/ and venvs (pyproject)
- Packaging includes rabbitmirror and rabbitmirror.web with package data (templates/static)

Notes specific to WARP sessions
- Prefer make targets for common workflows; they aggregate tool flags the repo expects
- For one-off tests, use pytest directly with -k or node ids; respect repository markers (see pytest.ini and pyproject markers)
- Some documentation references additional modules (e.g., trend analyzer, dashboard generator). If a command or import fails, check module presence in rabbitmirror/ before invoking
- When launching the web interface, ensure web extras are installed: pip install -e .[web] or pip install 'rabbitmirror[web]'

Common debugging (minimal)
- Activate venv and reinstall deps (fixes missing sklearn, etc.):
  - source venv/bin/activate && pip install -r requirements.txt && pip install -e .[dev]
- Run a single failing test verbosely, keep prints, drop into debugger on failure:
  - pytest tests/test_file.py::TestClass::test_case -v -s --pdb
- Type-check only the module you’re changing:
  - mypy rabbitmirror/<module>.py || echo "Install mypy: pip install mypy"
- Verify CLI wiring without running full app:
  - rabbitmirror --help; rabbitmirror analyze --help; rabbitmirror process --help
- TUI rendering issues in some terminals: ensure 256-color TERM and try light theme
  - TERM=xterm-256color rabbitmirror tui --theme light

Direct links to key files
- README: README.md
- Development guide: DEVELOPMENT.md
- Codebase overview: CODEBASE_SUMMARY.md
- Configuration guide: docs/configuration.md
- Make targets: Makefile
- Project config: pyproject.toml
- Pytest config: pytest.ini
- CI: .github/workflows/ci.yml
- Tests workflow: .github/workflows/test.yml
- Quality workflow: .github/workflows/quality.yml
- CLI entrypoint: rabbitmirror/cli.py
- TUI (if present): rabbitmirror/tui.py
- Parser: rabbitmirror/parser.py
- Cluster engine: rabbitmirror/cluster_engine.py
- Adversarial profiler: rabbitmirror/adversarial_profiler.py
- Suppression index: rabbitmirror/suppression_index.py
- Profile simulator: rabbitmirror/profile_simulator.py
- Report generator: rabbitmirror/report_generator.py
- Export formatter: rabbitmirror/export_formatter.py
- Config manager: rabbitmirror/config_manager.py
- Logging: rabbitmirror/symbolic_logger.py
- Web app (optional): rabbitmirror/web/

Important docs to consult quickly
- README.md — user-facing usage examples (CLI/TUI), install paths
- DEVELOPMENT.md — dev setup and canonical make targets; examples for running single tests
- CODEBASE_SUMMARY.md — big-picture module map (CLI, TUI, analysis engines, config, web)
- docs/configuration.md — config file locations, precedence, env vars, and example settings
- .github/workflows/*.yml — quality expectations mirrored in make ci/all-checks
