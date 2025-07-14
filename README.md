# 🐰 RabbitMirror

**Advanced YouTube Watch History Analysis Tool**

[![Tests](https://github.com/romulusaugustus/RabbitMirror/workflows/tests/badge.svg)](https://github.com/romulusaugustus/RabbitMirror/actions)
[![Coverage](https://codecov.io/gh/romulusaugustus/RabbitMirror/branch/main/graph/badge.svg)](https://codecov.io/gh/romulusaugustus/RabbitMirror)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![PyPI](https://img.shields.io/pypi/v/rabbitmirror.svg)](https://pypi.org/project/rabbitmirror/)

RabbitMirror is a powerful Python-based command-line tool designed to analyze and understand YouTube watch history patterns. It provides deep insights into viewing behavior, detects potential algorithmic manipulation, and offers comprehensive analysis capabilities for researchers, content creators, and curious users.

## 🎯 Why RabbitMirror?

- **🔍 Transparency**: Understand how algorithms shape your viewing experience
- **🛡️ Privacy-First**: All processing happens locally on your device
- **📊 Comprehensive**: Multiple analysis types from basic clustering to advanced pattern detection
- **🚀 Easy to Use**: Simple CLI interface with powerful features
- **🧪 Research-Ready**: Perfect for academic research and algorithmic auditing
- **📈 Actionable Insights**: Get clear, actionable information about your viewing patterns

## ✨ Features

### 🔍 **Core Analysis Capabilities**
- **Pattern Detection**: Identify adversarial patterns and algorithmic manipulation
- **Content Clustering**: Group similar videos and discover viewing themes
- **Suppression Analysis**: Detect content suppression patterns in recommendations
- **Profile Simulation**: Generate synthetic viewing profiles for testing
- **Temporal Analysis**: Track viewing patterns over time

### 📊 **Data Processing**
- **Multiple Export Formats**: JSON, CSV, YAML, Excel
- **Batch Processing**: Process multiple history files simultaneously
- **Flexible Parsing**: Handle YouTube's exported watch history format
- **Progress Tracking**: Visual progress bars for long operations

### 📋 **Reporting & Visualization**
- **Customizable Reports**: Generate detailed analysis reports
- **Multiple Themes**: Light and dark report themes
- **Export Options**: HTML, PDF, and Markdown reports
- **QR Code Generation**: Create QR codes for sharing results

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation

RabbitMirror can be installed directly from GitHub.

#### Quick Installation
```bash
# Install latest version from GitHub
pip install git+https://github.com/DanteX86/RabbitMirror.git

# Or install a specific version
pip install git+https://github.com/DanteX86/RabbitMirror.git@v1.0.0
```

#### Download and Install
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

#### Development Installation

For development or to get the latest changes:

```bash
# Clone the repository
git clone https://github.com/DanteX86/RabbitMirror.git
cd RabbitMirror

# Install in development mode
pip install -e .

# Or install with development dependencies
pip install -e .[dev]
```

### Getting Your YouTube Watch History

1. Go to [Google Takeout](https://takeout.google.com/)
2. Select "YouTube and YouTube Music"
3. Choose "history" > "watch-history.html"
4. Download and extract the file

## 📖 Usage

### Basic Commands

#### Parse Watch History
```bash
rabbitmirror process parse your-watch-history.html --output parsed_data.json
```

#### Analyze Content Clusters
```bash
rabbitmirror analyze cluster your-watch-history.html --output clusters.json --visualization
```

#### Detect Adversarial Patterns
```bash
rabbitmirror analyze detect-patterns your-watch-history.html --threshold 0.7 --output patterns.json
```

#### Analyze Content Suppression
```bash
rabbitmirror analyze analyze-suppression your-watch-history.html --period 30 --output suppression.json
```

#### Generate Profile Simulation
```bash
rabbitmirror analyze simulate your-watch-history.html --duration 30 --output simulated_profile.json
```

### Advanced Usage

#### Batch Processing
Process multiple history files in a directory:
```bash
python run.py process batch-process ./history_files/ --output-dir ./processed/ --recursive
```

#### Generate Reports
```bash
python run.py report generate-report data.json template.html report.html --format html --theme dark
```

### Command Groups

- **`process`**: Data processing commands (parse, batch-process)
- **`analyze`**: Analysis commands (cluster, detect-patterns, analyze-suppression, simulate)
- **`report`**: Report generation commands (generate-report)
- **`utils`**: Utility commands
- **`config`**: Configuration commands

## 🔧 Configuration

### Configuration Management

RabbitMirror includes a built-in configuration system to manage persistent settings:

#### Set Configuration Values
```bash
# Set local configuration (project-specific)
python run.py config set api_key "your-api-key"
python run.py config set default_output_format "json"

# Set global configuration (user-wide)
python run.py config set default_theme "dark" --global
python run.py config set analysis_threshold "0.7" --global
```

#### Get Configuration Values
```bash
# Get local configuration
python run.py config get api_key

# Get global configuration
python run.py config get default_theme --global
```

#### List All Configuration
```bash
# List all configuration (text format)
python run.py config list

# List in JSON format
python run.py config list --format json

# List in YAML format
python run.py config list --format yaml
```

### Output Formats
RabbitMirror supports multiple output formats:
- **JSON**: Default format, preserves all data structure
- **CSV**: Tabular format for spreadsheet analysis
- **YAML**: Human-readable configuration format
- **Excel**: Spreadsheet format with multiple sheets

### Analysis Parameters

#### Clustering Parameters
- `--eps`: DBSCAN epsilon parameter (default: 0.3)
- `--min-samples`: Minimum samples for cluster formation (default: 5)

#### Pattern Detection Parameters
- `--threshold`: Similarity threshold for pattern detection (default: 0.7)
- `--min-confidence`: Minimum confidence for pattern validity (default: 0.5)

#### Suppression Analysis Parameters
- `--period`: Baseline period in days (default: 30)
- `--threshold`: Suppression detection threshold (default: 0.5)

## 🛠️ Troubleshooting

### Common Issues

#### ModuleNotFoundError: No module named 'sklearn'

If you encounter this error when running tests or the application:

1. **Ensure you're in the virtual environment:**
   ```bash
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install or reinstall dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run tests with virtual environment:**
   ```bash
   source venv/bin/activate && make test
   ```

#### Python Version Compatibility

RabbitMirror requires Python 3.8 or higher. Check your Python version:
```bash
python --version
```

If you're using an older version, please upgrade Python or use a virtual environment with the correct version.

#### Virtual Environment Issues

If you're having issues with the virtual environment:

1. **Recreate the virtual environment:**
   ```bash
   rm -rf venv
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Verify the virtual environment is active:**
   ```bash
   which python  # Should show path to venv/bin/python
   ```

## 📁 Project Structure

```
RabbitMirror/
├── rabbitmirror/                 # Core package
│   ├── cli.py                   # Command-line interface
│   ├── parser.py                # HTML parsing logic
│   ├── cluster_engine.py        # Video clustering algorithms
│   ├── adversarial_profiler.py  # Pattern detection engine
│   ├── suppression_index.py     # Suppression analysis
│   ├── profile_simulator.py     # Profile simulation
│   ├── report_generator.py      # Report generation
│   ├── export_formatter.py      # Data export utilities
│   ├── qr_generator.py          # QR code generation
│   ├── config_manager.py        # Configuration management
│   └── symbolic_logger.py       # Logging utilities
├── data/                        # Input data directory
├── exports/                     # Output data directory
├── logs/                        # Application logs
├── reports/                     # Generated reports
├── venv/                        # Virtual environment
├── requirements.txt             # Python dependencies
├── run.py                       # Main entry point
└── README.md                    # This file
```

## 🔍 Analysis Types

### 1. **Adversarial Pattern Detection**
Identifies potential algorithmic manipulation patterns:
- Unusual recommendation sequences
- Content suppression indicators
- Engagement manipulation signs
- Echo chamber detection

### 2. **Content Clustering**
Groups similar videos based on:
- Title similarity
- Temporal patterns
- Viewing frequency
- Content categories

### 3. **Suppression Analysis**
Detects content suppression by analyzing:
- Recommendation frequency changes
- Category-specific suppression
- Temporal suppression patterns
- Baseline deviation metrics

### 4. **Profile Simulation**
Generates synthetic profiles for:
- Algorithm testing
- Privacy-preserving analysis
- Comparative studies
- Research purposes

## 📊 Sample Output

### Cluster Analysis
```json
{
  "clusters": [
    {
      "id": 0,
      "size": 25,
      "dominant_theme": "Machine Learning",
      "videos": ["video1", "video2", "..."],
      "characteristics": {
        "avg_watch_time": "15:30",
        "peak_hours": ["19:00", "21:00"],
        "common_keywords": ["python", "neural", "networks"]
      }
    }
  ]
}
```

### Pattern Detection
```json
{
  "patterns": [
    {
      "type": "suppression",
      "confidence": 0.85,
      "description": "Reduced recommendations for political content",
      "timeframe": "2023-11-01 to 2023-11-30",
      "affected_categories": ["news", "politics"]
    }
  ]
}
```

## 🛠️ Development

### Setting Up Development Environment

1. **Fork and clone the repository**
2. **Create a development branch:**
```bash
git checkout -b feature/your-feature-name
```

3. **Install development dependencies:**
```bash
pip install -e .
```

4. **Run tests:**
```bash
pytest tests/
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

### Code Style
- Follow PEP 8 guidelines
- Use type hints where appropriate
- Add docstrings to all functions and classes
- Maintain test coverage above 80%

## 🔒 Privacy & Security

RabbitMirror is designed with privacy in mind:

- **Local Processing**: All analysis is performed locally on your machine
- **No Data Transmission**: Your watch history never leaves your device
- **Anonymization Options**: Built-in data anonymization features
- **Secure Handling**: Secure data processing practices

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Support

- **Issues**: Report bugs and request features on [GitHub Issues](https://github.com/romulusaugustus/RabbitMirror/issues)
- **Discussions**: Join the conversation on [GitHub Discussions](https://github.com/romulusaugustus/RabbitMirror/discussions)
- **Wiki**: Check the [Wiki](https://github.com/romulusaugustus/RabbitMirror/wiki) for detailed documentation

## 🎯 Roadmap

### Upcoming Features
- [ ] Web-based dashboard
- [ ] Real-time analysis capabilities
- [ ] Machine learning model improvements
- [ ] Multi-platform support (Netflix, Spotify, etc.)
- [ ] Advanced visualization tools
- [ ] API for third-party integrations

### Recently Added
- ✅ Batch processing capabilities
- ✅ Multiple export formats
- ✅ Progress tracking
- ✅ Comprehensive CLI interface

## 🏆 Acknowledgments

- Thanks to all contributors who have helped improve RabbitMirror
- Inspired by the need for transparent algorithm analysis
- Built with Python and open-source libraries

## 📈 Examples

### Complete Analysis Workflow

```bash
# 1. Parse your watch history
python run.py process parse watch-history.html --output parsed.json

# 2. Analyze clusters
python run.py analyze cluster watch-history.html --output clusters.json

# 3. Detect patterns
python run.py analyze detect-patterns watch-history.html --output patterns.json

# 4. Analyze suppression
python run.py analyze analyze-suppression watch-history.html --output suppression.json

# 5. Generate comprehensive report
python run.py report generate-report parsed.json template.html report.html
```

### Scripted Analysis
```bash
#!/bin/bash
# Complete analysis pipeline
HISTORY_FILE="watch-history.html"
OUTPUT_DIR="analysis_results"

mkdir -p $OUTPUT_DIR

python run.py process parse $HISTORY_FILE --output $OUTPUT_DIR/parsed.json
python run.py analyze cluster $HISTORY_FILE --output $OUTPUT_DIR/clusters.json
python run.py analyze detect-patterns $HISTORY_FILE --output $OUTPUT_DIR/patterns.json
python run.py analyze analyze-suppression $HISTORY_FILE --output $OUTPUT_DIR/suppression.json

echo "Analysis complete! Results saved to $OUTPUT_DIR/"
```

---

**Made with ❤️ by the RabbitMirror team**

*Empowering users with insights into their digital consumption patterns*
