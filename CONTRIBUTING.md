# Contributing to RabbitMirror

Thank you for your interest in contributing to RabbitMirror! This document provides guidelines and information for contributors.

## 🎯 Project Vision

RabbitMirror aims to provide transparency into how YouTube's algorithm shapes viewing behavior while respecting user privacy. Our core values are:

- **Privacy First**: All analysis happens locally on the user's machine
- **Transparency**: Clear, understandable insights into algorithmic influence
- **User Empowerment**: Tools to help users understand their digital consumption
- **Open Source**: Community-driven development and improvement

## 🚀 Getting Started

### Prerequisites
- Python 3.9 or higher
- Git for version control
- Virtual environment tool (venv, conda, etc.)

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/your-username/RabbitMirror.git
   cd RabbitMirror
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

4. **Install Pre-commit Hooks**
   ```bash
   pre-commit install
   ```

5. **Run Tests**
   ```bash
   pytest tests/ -v
   ```

## 🔄 Development Workflow

### Branch Strategy
- `main`: Stable production code
- `develop`: Integration branch for new features
- `feature/*`: New features and enhancements
- `bugfix/*`: Bug fixes
- `hotfix/*`: Critical fixes for production

### Making Changes

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**
   - Write clear, concise code
   - Follow existing code style
   - Add appropriate tests
   - Update documentation

3. **Test Your Changes**
   ```bash
   # Run all tests
   pytest tests/ -v

   # Run specific test file
   pytest tests/test_your_module.py -v

   # Run with coverage
   pytest tests/ --cov=rabbitmirror --cov-report=html
   ```

4. **Code Quality Checks**
   ```bash
   # Type checking
   mypy rabbitmirror/

   # Linting
   flake8 rabbitmirror/

   # Security scan
   bandit -r rabbitmirror/

   # Format code
   black rabbitmirror/
   isort rabbitmirror/
   ```

5. **Commit Changes**
   ```bash
   git add .
   git commit -m "feat: add new feature description"
   ```

### Commit Message Format
We use conventional commits:
- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation changes
- `style:` Code style changes
- `refactor:` Code refactoring
- `test:` Test additions/changes
- `chore:` Maintenance tasks

## 📝 Code Style Guidelines

### Python Code Style
- Follow PEP 8 guidelines
- Use type hints for all functions and methods
- Maximum line length: 88 characters
- Use black for code formatting
- Use isort for import sorting

### Documentation
- Write clear docstrings for all public functions and classes
- Use Google-style docstrings
- Include examples in docstrings where helpful
- Update README.md for user-facing changes

### Testing
- Write tests for all new functionality
- Maintain test coverage above 80%
- Use descriptive test names
- Follow AAA pattern (Arrange, Act, Assert)
- Mock external dependencies

## 🐛 Bug Reports

When reporting bugs, please include:

1. **Environment Information**
   - Operating system and version
   - Python version
   - RabbitMirror version
   - Relevant dependency versions

2. **Steps to Reproduce**
   - Minimal code example
   - Input data (anonymized if necessary)
   - Expected behavior
   - Actual behavior

3. **Additional Context**
   - Error messages and stack traces
   - Log files (if applicable)
   - Screenshots (if relevant)

## 💡 Feature Requests

For new features, please provide:

1. **Use Case Description**
   - Problem you're trying to solve
   - How it aligns with project goals
   - Target user personas

2. **Proposed Solution**
   - High-level design approach
   - API design (if applicable)
   - Implementation considerations

3. **Alternatives Considered**
   - Other approaches evaluated
   - Trade-offs and decisions

## 🧪 Testing Guidelines

### Test Structure
```
tests/
├── unit/           # Unit tests
├── integration/    # Integration tests
├── fixtures/       # Test data and fixtures
└── conftest.py     # Test configuration
```

### Test Categories
- **Unit Tests**: Test individual functions/methods
- **Integration Tests**: Test component interactions
- **End-to-End Tests**: Test complete workflows
- **Performance Tests**: Test performance characteristics

### Writing Tests
```python
def test_function_description():
    """Test that function does what it should."""
    # Arrange
    input_data = create_test_data()

    # Act
    result = function_under_test(input_data)

    # Assert
    assert result == expected_result
```

## 📚 Documentation Guidelines

### Code Documentation
- Document all public APIs
- Include usage examples
- Explain complex algorithms
- Document edge cases and limitations

### User Documentation
- Keep README.md up to date
- Provide clear installation instructions
- Include usage examples
- Document troubleshooting steps

## 🔍 Code Review Process

### Before Submitting
- [ ] All tests pass
- [ ] Code is properly formatted
- [ ] Documentation is updated
- [ ] Commit messages follow convention
- [ ] No security vulnerabilities

### Review Criteria
- **Functionality**: Does it work as intended?
- **Code Quality**: Is it readable and maintainable?
- **Performance**: Are there any performance implications?
- **Security**: Are there any security concerns?
- **Documentation**: Is it properly documented?

## 🚢 Release Process

### Version Numbering
We follow [Semantic Versioning](https://semver.org/):
- `MAJOR.MINOR.PATCH`
- Major: Breaking changes
- Minor: New features (backward compatible)
- Patch: Bug fixes (backward compatible)

### Release Checklist
- [ ] All tests pass
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Version numbers updated
- [ ] Git tag created
- [ ] PyPI package published

## 🏆 Recognition

Contributors will be recognized in:
- GitHub contributors list
- CHANGELOG.md for significant contributions
- Documentation acknowledgments
- Project README.md

## 📞 Getting Help

- **GitHub Issues**: For bug reports and feature requests
- **GitHub Discussions**: For general questions and ideas
- **Email**: dev@rabbitmirror.com for private matters

## 📋 Development Environment

### Recommended Tools
- **IDE**: VS Code, PyCharm, or similar
- **Git GUI**: GitKraken, SourceTree, or command line
- **Terminal**: iTerm2 (Mac), Windows Terminal, or built-in
- **Python**: pyenv for version management

### VS Code Extensions
- Python
- Pylance
- Black Formatter
- isort
- GitLens
- Python Test Explorer

### Environment Variables
```bash
# For development
export PYTHONPATH="${PYTHONPATH}:${PWD}"
export RABBITMIRROR_DEBUG=1
export RABBITMIRROR_LOG_LEVEL=DEBUG
```

## 🔒 Security

### Reporting Security Issues
Please report security vulnerabilities to dev@rabbitmirror.com rather than creating public issues.

### Security Guidelines
- Never commit sensitive data
- Use secure defaults
- Validate all inputs
- Follow OWASP guidelines
- Regular dependency updates

## 📄 License

By contributing to RabbitMirror, you agree that your contributions will be licensed under the MIT License.

Thank you for contributing to RabbitMirror! Your contributions help make YouTube analysis more transparent and accessible to everyone.
