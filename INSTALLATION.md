# RabbitMirror Installation Guide

## Install from GitHub

RabbitMirror is available on GitHub and can be installed directly using pip.

### Quick Installation

```bash
# Install latest version from GitHub
pip install git+https://github.com/DanteX86/RabbitMirror.git

# Or install a specific version
pip install git+https://github.com/DanteX86/RabbitMirror.git@v1.0.0
```

### Download and Install

You can also download the distribution files from GitHub releases:

1. Go to [Releases](https://github.com/DanteX86/RabbitMirror/releases)
2. Download either:
   - `rabbitmirror-1.0.0-py3-none-any.whl` (recommended)
   - `rabbitmirror-1.0.0.tar.gz` (source)

3. Install the downloaded file:
```bash
# Install wheel file
pip install rabbitmirror-1.0.0-py3-none-any.whl

# Or install source distribution
pip install rabbitmirror-1.0.0.tar.gz
```

### Development Installation

For development or to get the latest changes:

```bash
# Clone the repository
git clone https://github.com/DanteX86/RabbitMirror.git
cd RabbitMirror

# Install in development mode
pip install -e .

# Or install with development dependencies
pip install -e ".[dev]"
```

## Verify Installation

After installation, verify it works:

```bash
# Check version
rabbitmirror --version

# Run help
rabbitmirror --help

# Test basic functionality
rabbitmirror parse --help
```

## Requirements

- Python 3.8+
- Dependencies are automatically installed with pip

## Optional Dependencies

Install additional features:

```bash
# Web interface
pip install "rabbitmirror[web] @ git+https://github.com/DanteX86/RabbitMirror.git"

# Development tools
pip install "rabbitmirror[dev] @ git+https://github.com/DanteX86/RabbitMirror.git"

# All features
pip install "rabbitmirror[all] @ git+https://github.com/DanteX86/RabbitMirror.git"
```

## Troubleshooting

### Installation Issues

If you encounter issues:

1. **Update pip**: `pip install --upgrade pip`
2. **Use virtual environment**: 
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install git+https://github.com/DanteX86/RabbitMirror.git
   ```

### Permission Issues

On macOS/Linux, you might need to use `--user`:
```bash
pip install --user git+https://github.com/DanteX86/RabbitMirror.git
```

### Dependency Conflicts

If you have conflicts with existing packages:
```bash
# Install in a fresh virtual environment
python -m venv fresh_env
source fresh_env/bin/activate
pip install git+https://github.com/DanteX86/RabbitMirror.git
```

## Getting Started

After installation, see:
- [README.md](README.md) for basic usage
- [CONTRIBUTING.md](CONTRIBUTING.md) for development
- [docs/](docs/) for detailed documentation

## Support

- [GitHub Issues](https://github.com/DanteX86/RabbitMirror/issues)
- [Documentation](https://github.com/DanteX86/RabbitMirror/tree/main/docs)
- [Examples](https://github.com/DanteX86/RabbitMirror/tree/main/examples)
