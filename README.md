# 🐰 RabbitMirror

**Advanced YouTube Watch History Analysis Tool**

RabbitMirror is a powerful Python-based command-line tool designed to analyze and understand YouTube watch history patterns. It provides deep insights into viewing behavior, detects potential algorithmic manipulation, and offers comprehensive analysis capabilities for researchers, content creators, and curious users.

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

1. **Clone the repository:**
```bash
git clone https://github.com/romulusaugustus/RabbitMirror.git
cd RabbitMirror
```

2. **Create a virtual environment:**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Run the tool:**
```bash
python run.py --help
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
python run.py process parse your-watch-history.html --output parsed_data.json
```

#### Analyze Content Clusters
```bash
python run.py analyze cluster your-watch-history.html --output clusters.json --visualization
```

#### Detect Adversarial Patterns
```bash
python run.py analyze detect-patterns your-watch-history.html --threshold 0.7 --output patterns.json
```

#### Analyze Content Suppression
```bash
python run.py analyze analyze-suppression your-watch-history.html --period 30 --output suppression.json
```

#### Generate Profile Simulation
```bash
python run.py analyze simulate your-watch-history.html --duration 30 --output simulated_profile.json
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
