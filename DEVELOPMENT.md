# RabbitMirror Development Guide

## 🚀 Quick Start

### Prerequisites
- Python 3.9+ (recommended: 3.11+)
- Git
- Virtual environment tool (venv, conda, etc.)

### Setup Development Environment

1. **Clone and enter the repository:**
   ```bash
   git clone https://github.com/yourusername/rabbitmirror.git
   cd rabbitmirror
   ```

2. **Create and activate virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install development dependencies:**
   ```bash
   make dev-setup
   # OR manually:
   pip install -r requirements.txt
   pip install -e ".[dev]"
   pre-commit install
   ```

## 🛠️ Development Commands

Use our Makefile for common development tasks:

```bash
make help              # Show all available commands
make test              # Run full test suite with coverage
make test-quick        # Run tests without coverage
make lint              # Run all linting tools
make format            # Auto-format code
make security          # Run security checks
make pre-commit        # Run pre-commit hooks
make clean             # Clean build artifacts
make build             # Build the package
make all-checks        # Run complete quality checks
make ci                # Run full CI pipeline locally
```

## 🏗️ Project Structure

```
rabbitmirror/
├── rabbitmirror/           # Main package
│   ├── __init__.py
│   ├── cli.py             # Command-line interface
│   ├── parser.py          # HTML parsing logic
│   ├── cluster_engine.py  # Video clustering
│   ├── adversarial_profiler.py  # Pattern detection
│   ├── profile_simulator.py     # Profile simulation
│   ├── export_formatter.py      # Data export
│   ├── suppression_index.py     # Content suppression analysis
│   ├── qr_generator.py          # QR code generation
│   ├── report_generator.py      # Report generation
│   └── symbolic_logger.py       # Logging utilities
├── tests/                 # Test suite
│   ├── fixtures/         # Test data
│   ├── conftest.py       # Test configuration
│   └── test_*.py         # Test modules
├── .github/workflows/    # CI/CD pipelines
├── requirements.txt      # Dependencies
├── setup.py             # Package configuration
├── Makefile            # Development commands
└── README.md          # Project documentation
```

## 🧪 Testing

### Running Tests
```bash
# Full test suite with coverage
make test

# Quick tests without coverage
make test-quick

# Specific test file
pytest tests/test_cluster_engine.py -v

# Specific test
pytest tests/test_cluster_engine.py::TestClusterEngine::test_cluster_videos_with_sample_data -v
```

### Writing Tests
- Place tests in `tests/` directory
- Name test files as `test_*.py`
- Use pytest fixtures from `conftest.py`
- Aim for high test coverage (currently 100%)

### Test Data
Test fixtures are in `tests/fixtures/`:
- `sample_history.html` - Sample YouTube history file
- Add new fixtures as needed for your tests

## 🔍 Code Quality

### Linting Tools
- **Pylint**: Code quality and style
- **Flake8**: Style guide enforcement
- **Bandit**: Security vulnerability scanning
- **Black**: Code formatting
- **isort**: Import sorting

### Pre-commit Hooks
Automatic code quality checks run on every commit:
- Trailing whitespace removal
- YAML validation
- Code formatting
- Linting
- Security checks
- Test execution

### Code Style Guidelines
- Follow PEP 8
- Use type hints
- Add docstrings to public functions
- Keep functions focused and small
- Handle errors gracefully

## 📦 Building and Installation

### Development Installation
```bash
# Install in development mode
pip install -e .

# Install with development dependencies
pip install -e ".[dev]"
```

### Building Distribution
```bash
make build
# OR
python -m build
```

### Installing Built Package
```bash
make install-package
# OR
pip install dist/*.whl
```

## 🚀 CI/CD Pipeline

### GitHub Actions
The project includes automated CI/CD in `.github/workflows/ci.yml`:
- **Multi-version testing**: Python 3.9, 3.10, 3.11, 3.12
- **Code quality checks**: Linting, formatting, security
- **Test execution**: Full test suite with coverage
- **Build verification**: Package building
- **Coverage reporting**: Codecov integration

### Local CI Simulation
```bash
make ci  # Run full CI pipeline locally
```

## 🔧 Contributing

### Workflow
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Run quality checks: `make all-checks`
5. Commit your changes: `git commit -m 'Add amazing feature'`
6. Push to your fork: `git push origin feature/amazing-feature`
7. Open a Pull Request

### Code Review Checklist
- [ ] Tests pass (`make test`)
- [ ] Code quality passes (`make lint`)
- [ ] Security checks pass (`make security`)
- [ ] Code is formatted (`make format-check`)
- [ ] Documentation updated
- [ ] Type hints added
- [ ] Changelog updated (if applicable)

## 🐛 Debugging

### Common Issues
1. **Import errors**: Ensure you're in the virtual environment
2. **Test failures**: Check if test data files exist
3. **Linting errors**: Run `make format` to auto-fix style issues

### Debugging Tools
```bash
# Run specific tests with detailed output
pytest tests/test_file.py -v -s

# Run with debugger
pytest tests/test_file.py -v -s --pdb

# Profile code performance
python -m cProfile -o profile.stats your_script.py
```

## 📊 Performance

### Benchmarking
```bash
make benchmark  # (Not yet implemented)
```

### Profiling
- Use `cProfile` for performance analysis
- Monitor memory usage with `memory_profiler`
- Test with large datasets

## 🔐 Security

### Security Checks
```bash
make security
```

### Security Guidelines
- Never commit sensitive data
- Use environment variables for secrets
- Validate all user inputs
- Follow secure coding practices

## 📚 Documentation

### Code Documentation
- Use clear, descriptive docstrings
- Follow Google or NumPy docstring style
- Document complex algorithms
- Include examples in docstrings

### Building Documentation
```bash
make docs  # (Not yet implemented)
```

## 🌟 Code Quality Metrics

Current project status:
- **Code Quality Score**: 9.19/10 (Pylint)
- **Test Coverage**: 100% (124/124 tests passing)
- **Security**: No known vulnerabilities
- **Dependencies**: Up to date

## 🤝 Getting Help

- **Issues**: Report bugs via GitHub Issues
- **Discussions**: Use GitHub Discussions for questions
- **Documentation**: Check README.md and this guide
- **Code Review**: Request reviews on Pull Requests

## 📝 Release Process

### Preparing a Release
```bash
make release-check
```

### Version Bumping
1. Update version in `setup.py`
2. Update CHANGELOG.md
3. Create release tag
4. Build and publish to PyPI

---

Happy coding! 🎉
