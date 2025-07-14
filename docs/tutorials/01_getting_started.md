# Getting Started with RabbitMirror

## Overview

RabbitMirror is a powerful Python tool for analyzing YouTube watch history data. It provides comprehensive parsing, clustering, analysis, and visualization capabilities to help you understand your viewing patterns and behaviors.

## Prerequisites

- Python 3.8 or higher
- pip package manager
- Basic familiarity with command line interface

## Installation

### Option 1: Install from Source

1. Clone the repository:
```bash
git clone https://github.com/yourusername/RabbitMirror.git
cd RabbitMirror
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install the package in development mode:
```bash
pip install -e .
```

### Option 2: Install from PyPI (when available)

```bash
pip install rabbitmirror
```

## Getting Your YouTube Watch History

Before you can use RabbitMirror, you need to download your YouTube watch history:

1. Go to [Google Takeout](https://takeout.google.com/)
2. Select "YouTube and YouTube Music"
3. Choose "history" and make sure "watch-history.html" is selected
4. Download your data
5. Extract the ZIP file and locate the `watch-history.html` file

## Quick Start

### 1. Basic Parsing

Parse your YouTube watch history file:

```bash
python -m rabbitmirror.cli parse examples/datasets/sample_watch_history.html
```

This will:
- Parse the HTML file
- Extract video titles, URLs, and timestamps
- Display basic statistics
- Save parsed data to `parsed_data.json`

### 2. Export to Different Formats

Export your data to various formats:

```bash
# Export to CSV
python -m rabbitmirror.cli export parsed_data.json --format csv --output my_history

# Export to Excel
python -m rabbitmirror.cli export parsed_data.json --format excel --output my_history

# Export to YAML
python -m rabbitmirror.cli export parsed_data.json --format yaml --output my_history
```

### 3. Cluster Analysis

Analyze your viewing patterns by clustering similar videos:

```bash
python -m rabbitmirror.cli cluster parsed_data.json --output clusters.json
```

This will:
- Group similar videos together based on titles
- Identify viewing patterns
- Generate clustering statistics

### 4. Generate Reports

Create comprehensive HTML reports:

```bash
python -m rabbitmirror.cli report parsed_data.json --output-dir reports/
```

This generates:
- Interactive HTML dashboard
- Viewing statistics
- Clustering visualizations
- Trend analysis charts

## Configuration

RabbitMirror can be configured using a YAML configuration file:

```bash
# Copy the example configuration
cp examples/datasets/sample_config.yaml config.yaml

# Edit the configuration
nano config.yaml

# Use the configuration
python -m rabbitmirror.cli --config config.yaml parse your_history.html
```

## Example Workflow

Here's a complete example workflow:

```bash
# 1. Parse your watch history
python -m rabbitmirror.cli parse examples/datasets/sample_watch_history.html

# 2. Perform clustering analysis
python -m rabbitmirror.cli cluster parsed_data.json --eps 0.3 --min-samples 5

# 3. Generate comprehensive report
python -m rabbitmirror.cli report parsed_data.json --include-clusters

# 4. Export to multiple formats
python -m rabbitmirror.cli export parsed_data.json --format csv
python -m rabbitmirror.cli export parsed_data.json --format excel

# 5. Analyze trends
python -m rabbitmirror.cli analyze parsed_data.json --trend-analysis
```

## Understanding the Output

### Parsed Data Structure

```json
{
  "metadata": {
    "source": "YouTube Watch History",
    "parsed_at": "2023-12-15T14:30:45Z",
    "total_entries": 20,
    "date_range": {
      "start": "2023-11-26T07:35:15Z",
      "end": "2023-12-15T14:30:45Z"
    }
  },
  "entries": [
    {
      "title": "Video Title",
      "url": "https://www.youtube.com/watch?v=...",
      "timestamp": "2023-12-15T14:30:45Z"
    }
  ]
}
```

### Clustering Results

```json
{
  "clusters": {
    "cluster_0": [...],
    "cluster_1": [...],
    "noise": [...]
  },
  "cluster_info": {
    "total_clusters": 5,
    "noise_points": 2,
    "total_entries": 20
  }
}
```

## Common Use Cases

1. **Personal Analytics**: Understand your viewing habits and preferences
2. **Content Research**: Identify trending topics and content types
3. **Time Management**: Analyze when and how much you watch
4. **Privacy Review**: Audit your digital footprint
5. **Academic Research**: Study digital behavior patterns

## Next Steps

- Read the [Advanced Usage Guide](02_advanced_usage.md)
- Explore [Configuration Options](03_configuration.md)
- Learn about [API Usage](04_api_usage.md)
- Check out [Examples and Recipes](05_examples_and_recipes.md)

## Troubleshooting

### Common Issues

1. **File Not Found**: Ensure the HTML file path is correct
2. **Encoding Errors**: Try different encoding options in the config
3. **Memory Issues**: For large files, increase memory limits in config
4. **Permission Errors**: Check file permissions and output directory access

### Getting Help

- Check the [FAQ](../FAQ.md)
- Review the [API Documentation](../api/index.md)
- Report issues on [GitHub Issues](https://github.com/yourusername/RabbitMirror/issues)
- Join our [Community Discussion](https://github.com/yourusername/RabbitMirror/discussions)

## License

RabbitMirror is open source software released under the MIT License. See the [LICENSE](../../LICENSE) file for details.
