# RabbitMirror CLI Reference

## Overview

RabbitMirror is an advanced YouTube Watch History Analysis Tool that provides comprehensive CLI commands for data processing, analysis, report generation, and system management. This reference covers all available commands, their syntax, options, and usage examples.

## Installation and Setup

```bash
# Install RabbitMirror
pip install rabbitmirror

# Or run from source
python run.py

# Shell completion (optional)
rabbitmirror completion bash >> ~/.bashrc  # For bash
rabbitmirror completion zsh >> ~/.zshrc    # For zsh
```

## Global Options

All RabbitMirror commands support the following global behaviors:
- **Configuration**: Global (`~/.rabbitmirror_config.json`) and local (`./.rabbitmirror_config.json`) config files
- **Output Formats**: JSON, CSV, YAML, Excel for most commands
- **Error Handling**: Consistent error messages with context and suggestions
- **Logging**: Symbolic logging with error tracking

## Command Groups

### 1. Process Commands (`rabbitmirror process`)

Commands for data processing and parsing.

#### `parse` - Parse History Files

Parse a YouTube watch history file from Google Takeout.

**Syntax:**
```bash
rabbitmirror process parse HISTORY_FILE PLATFORM [OPTIONS]
```

**Arguments:**
- `HISTORY_FILE` - Path to history file (must exist)
- `PLATFORM` - Platform name (e.g., 'youtube')

**Options:**
- `--output, -o PATH` - Output file for parsed data
- `--format, -f {json,csv,yaml,excel}` - Output format (default: json)
- `--verbose, -v` - Enable verbose output

**Examples:**
```bash
# Basic parsing
rabbitmirror process parse watch-history.html youtube

# Parse with specific output
rabbitmirror process parse watch-history.html youtube -o parsed_data.json

# Parse to CSV with verbose output
rabbitmirror process parse data.html youtube --format csv --verbose --output results.csv
```

**Input:** HTML files from YouTube Takeout
**Output:** Structured data in chosen format

---

#### `batch-process` - Process Multiple Files

Process multiple history files in a directory.

**Syntax:**
```bash
rabbitmirror process batch-process INPUT_DIR [OPTIONS]
```

**Arguments:**
- `INPUT_DIR` - Directory containing history files

**Options:**
- `--output-dir, -o PATH` - Output directory (default: processed_output)
- `--format, -f {json,csv,yaml,excel}` - Output format (default: json)
- `--recursive, -r` - Process directories recursively

**Examples:**
```bash
# Process all HTML files in directory
rabbitmirror process batch-process ./history_files/

# Recursive processing with custom output
rabbitmirror process batch-process ./data/ -o ./output/ -f csv -r
```

**Input:** Directory of HTML files
**Output:** Processed files in specified format

---

### 2. Analyze Commands (`rabbitmirror analyze`)

Commands for advanced data analysis and pattern detection.

#### `cluster` - Cluster Videos

Perform clustering analysis on watch history using DBSCAN algorithm.

**Syntax:**
```bash
rabbitmirror analyze cluster HISTORY_FILE [OPTIONS]
```

**Arguments:**
- `HISTORY_FILE` - Path to history file (must exist)

**Options:**
- `--eps FLOAT` - DBSCAN eps parameter (default: 0.3)
- `--min-samples INTEGER` - DBSCAN min_samples parameter (default: 5)
- `--output, -o PATH` - Output file for cluster data
- `--format, -f {json,csv,yaml,excel}` - Output format (default: json)
- `--visualization, -viz` - Generate cluster visualization

**Examples:**
```bash
# Basic clustering
rabbitmirror analyze cluster data.html

# Custom clustering parameters
rabbitmirror analyze cluster data.html --eps 0.5 --min-samples 3 -o clusters.json

# Generate visualization
rabbitmirror analyze cluster data.html --visualization --format csv
```

**Input:** Parsed history data
**Output:** Cluster analysis with video groupings

---

#### `analyze-suppression` - Content Suppression Analysis

Analyze patterns that suggest content suppression or algorithmic filtering.

**Syntax:**
```bash
rabbitmirror analyze analyze-suppression HISTORY_FILE [OPTIONS]
```

**Arguments:**
- `HISTORY_FILE` - Path to history file

**Options:**
- `--period INTEGER` - Baseline period in days (default: 30)
- `--output, -o PATH` - Output file for suppression data
- `--format, -f {json,csv,yaml,excel}` - Output format (default: json)
- `--threshold, -t FLOAT` - Suppression threshold (default: 0.5)
- `--category-filter, -cf TEXT` - Filter specific categories (multiple allowed)

**Examples:**
```bash
# Basic suppression analysis
rabbitmirror analyze analyze-suppression data.html

# Custom parameters
rabbitmirror analyze analyze-suppression data.html --period 14 --threshold 0.7

# Filter specific categories
rabbitmirror analyze analyze-suppression data.html --category-filter news --category-filter politics
```

**Input:** Parsed history data
**Output:** Suppression analysis report

---

#### `detect-patterns` - Adversarial Pattern Detection

Detect potential adversarial algorithmic patterns in recommendations.

**Syntax:**
```bash
rabbitmirror analyze detect-patterns HISTORY_FILE [OPTIONS]
```

**Arguments:**
- `HISTORY_FILE` - Path to history file

**Options:**
- `--threshold FLOAT` - Similarity threshold (default: 0.7)
- `--output, -o PATH` - Output file for pattern analysis
- `--format, -f {json,csv,yaml,excel}` - Output format (default: json)
- `--pattern-types, -pt TEXT` - Specific pattern types to detect (multiple)
- `--min-confidence, -mc FLOAT` - Minimum confidence threshold (default: 0.5)

**Examples:**
```bash
# Basic pattern detection
rabbitmirror analyze detect-patterns data.html

# High sensitivity detection
rabbitmirror analyze detect-patterns data.html --threshold 0.8 --min-confidence 0.6

# Specific pattern types
rabbitmirror analyze detect-patterns data.html --pattern-types recommendation --pattern-types engagement
```

**Input:** Parsed history data
**Output:** Pattern detection report

---

#### `simulate` - Profile Simulation

Generate synthetic watch history profiles based on existing patterns.

**Syntax:**
```bash
rabbitmirror analyze simulate HISTORY_FILE [OPTIONS]
```

**Arguments:**
- `HISTORY_FILE` - Path to history file

**Options:**
- `--duration INTEGER` - Simulation duration in days (default: 30)
- `--seed INTEGER` - Random seed for reproducibility
- `--output, -o PATH` - Output file for simulated profile
- `--format, -f {json,csv,yaml,excel}` - Output format (default: json)
- `--profile-type, -pt {regular,binge,sporadic}` - Profile type (default: regular)
- `--intensity, -i FLOAT` - Simulation intensity multiplier (default: 1.0)

**Examples:**
```bash
# Basic simulation
rabbitmirror analyze simulate data.html

# Binge-watching profile for one week
rabbitmirror analyze simulate data.html --duration 7 --profile-type binge

# Reproducible simulation with custom intensity
rabbitmirror analyze simulate data.html --seed 12345 --intensity 1.5
```

**Input:** Parsed history data
**Output:** Synthetic profile data

---

#### `trend-analysis` - Temporal Trend Analysis

Analyze viewing trends and patterns over time.

**Syntax:**
```bash
rabbitmirror analyze trend-analysis HISTORY_FILE [OPTIONS]
```

**Arguments:**
- `HISTORY_FILE` - Path to history file

**Options:**
- `--period {daily,weekly,monthly}` - Analysis period (default: daily)
- `--metrics, -m TEXT` - Metrics to analyze (multiple allowed)
- `--output, -o PATH` - Output file for trends
- `--format, -f {json,csv,yaml,excel}` - Output format (default: json)
- `--normalize, -n` - Normalize trend values

**Examples:**
```bash
# Basic trend analysis
rabbitmirror analyze trend-analysis data.html

# Weekly trends with normalization
rabbitmirror analyze trend-analysis data.html --period weekly --normalize

# Specific metrics
rabbitmirror analyze trend-analysis data.html --metrics views --metrics duration
```

**Input:** Parsed history data
**Output:** Trend analysis with time-series data

---

### 3. Report Commands (`rabbitmirror report`)

Commands for generating reports and dashboards.

#### `generate-report` - Template-Based Reports

Generate reports using predefined templates.

**Syntax:**
```bash
rabbitmirror report generate-report DATA_FILE TEMPLATE_FILE OUTPUT_FILE [OPTIONS]
```

**Arguments:**
- `DATA_FILE` - Data file for report (must exist)
- `TEMPLATE_FILE` - Template file (must exist)
- `OUTPUT_FILE` - Output file path

**Options:**
- `--format, -f {html,pdf,md}` - Report format (default: html)
- `--theme, -t {light,dark}` - Report theme (default: light)
- `--include-viz, -v` - Include visualizations

**Examples:**
```bash
# HTML report
rabbitmirror report generate-report data.json template.html report.html

# PDF report with dark theme
rabbitmirror report generate-report data.json template.md report.pdf --format pdf --theme dark
```

**Input:** JSON/CSV/YAML data, HTML/Markdown templates
**Output:** HTML, PDF, or Markdown reports

---

#### `export-dashboard` - Interactive Dashboards

Export data as interactive web dashboards.

**Syntax:**
```bash
rabbitmirror report export-dashboard DATA_FILE [OPTIONS]
```

**Arguments:**
- `DATA_FILE` - Data file for dashboard

**Options:**
- `--template, -t {basic,advanced,custom}` - Dashboard template (default: basic)
- `--output, -o PATH` - Output directory (default: dashboard_output)
- `--interactive, -i` - Generate interactive dashboard
- `--theme, -th {light,dark}` - Dashboard theme (default: light)
- `--include-plots, -p` - Include plot visualizations

**Examples:**
```bash
# Basic dashboard
rabbitmirror report export-dashboard data.json

# Advanced interactive dashboard
rabbitmirror report export-dashboard data.json --template advanced --interactive --theme dark
```

**Input:** JSON/CSV/YAML data
**Output:** HTML dashboard with assets

---

### 4. Utils Commands (`rabbitmirror utils`)

Utility commands for data validation, conversion, and QR code generation.

#### `validate` - Data Validation

Validate data files against schemas.

**Syntax:**
```bash
rabbitmirror utils validate FILE [OPTIONS]
```

**Arguments:**
- `FILE` - File to validate (must exist)

**Options:**
- `--schema, -s PATH` - Custom schema file
- `--format, -f {json,yaml}` - File format (default: json)

**Examples:**
```bash
# Validate with auto-detection
rabbitmirror utils validate data.json

# Validate against custom schema
rabbitmirror utils validate data.yaml --format yaml --schema custom_schema.json
```

**Input:** JSON/YAML files
**Output:** Validation report

---

#### `convert` - Format Conversion

Convert files between different formats.

**Syntax:**
```bash
rabbitmirror utils convert INPUT_FILE OUTPUT_FORMAT [OPTIONS]
```

**Arguments:**
- `INPUT_FILE` - Input file to convert
- `OUTPUT_FORMAT` - Target format {json,csv,yaml,excel}

**Options:**
- `--output, -o PATH` - Output file path

**Examples:**
```bash
# Convert JSON to CSV
rabbitmirror utils convert data.json csv

# Convert with custom output path
rabbitmirror utils convert input.yaml excel --output converted.xlsx
```

**Input:** JSON/CSV/YAML/Excel files
**Output:** Converted file in target format

---

#### `generate-qr` - QR Code Generation

Generate QR codes for data sharing.

**Syntax:**
```bash
rabbitmirror utils generate-qr DATA [OPTIONS]
```

**Arguments:**
- `DATA` - Data to encode in QR code

**Options:**
- `--output, -o PATH` - Output file for QR code
- `--size, -s INTEGER` - QR code size (default: 10)
- `--error-correction, -e {L,M,Q,H}` - Error correction level (default: M)
- `--color, -c TEXT` - QR code color (default: black)

**Examples:**
```bash
# Basic QR code
rabbitmirror utils generate-qr "https://example.com"

# Custom QR code
rabbitmirror utils generate-qr "My data" --size 15 --color red --output qr.png
```

**Input:** Text/URL strings
**Output:** PNG image files

---

### 5. Config Commands (`rabbitmirror config`)

Configuration management commands.

#### `set` - Set Configuration Values

**Syntax:**
```bash
rabbitmirror config set KEY VALUE [OPTIONS]
```

**Arguments:**
- `KEY` - Configuration key
- `VALUE` - Configuration value

**Options:**
- `--global/--local` - Store in global or local config (default: local)

**Examples:**
```bash
# Set local configuration
rabbitmirror config set output_dir /path/to/output

# Set global configuration
rabbitmirror config set default_format json --global
```

---

#### `get` - Get Configuration Values

**Syntax:**
```bash
rabbitmirror config get KEY [OPTIONS]
```

**Arguments:**
- `KEY` - Configuration key to retrieve

**Options:**
- `--global/--local` - Read from global or local config (default: local)

**Examples:**
```bash
rabbitmirror config get output_dir
rabbitmirror config get default_threshold --global
```

---

#### `list` - List All Configuration

**Syntax:**
```bash
rabbitmirror config list [OPTIONS]
```

**Options:**
- `--global/--local` - List global or local config (default: local)
- `--format, -f {text,json,yaml}` - Output format (default: text)

**Examples:**
```bash
rabbitmirror config list
rabbitmirror config list --format json --global
```

---

### 6. Database Commands (`rabbitmirror db`)

Database management and maintenance commands.

#### `init` - Initialize Database

**Syntax:**
```bash
rabbitmirror db init [OPTIONS]
```

**Options:**
- `--database-url TEXT` - Database URL (overrides environment)
- `--reset` - Reset existing database

**Examples:**
```bash
rabbitmirror db init
rabbitmirror db init --database-url sqlite:///data.db --reset
```

---

#### `status` - Check Database Status

**Syntax:**
```bash
rabbitmirror db status
```

Shows database connection status, pool information, and cache statistics.

---

#### `migrate` - Create Migrations

**Syntax:**
```bash
rabbitmirror db migrate [OPTIONS]
```

**Options:**
- `--message, -m TEXT` - Migration message (required)
- `--autogenerate` - Auto-generate from model changes

**Examples:**
```bash
rabbitmirror db migrate -m "Add new table"
rabbitmirror db migrate -m "Update schema" --autogenerate
```

---

#### `upgrade` - Apply Migrations

**Syntax:**
```bash
rabbitmirror db upgrade [OPTIONS]
```

**Options:**
- `--revision TEXT` - Target revision (default: head)

**Examples:**
```bash
rabbitmirror db upgrade
rabbitmirror db upgrade --revision abc123
```

---

#### `downgrade` - Rollback Migrations

**Syntax:**
```bash
rabbitmirror db downgrade REVISION
```

**Arguments:**
- `REVISION` - Target revision to rollback to

---

#### `cleanup` - Data Retention

**Syntax:**
```bash
rabbitmirror db cleanup [OPTIONS]
```

**Options:**
- `--policy TEXT` - Specific cleanup policy
- `--dry-run` - Show what would be cleaned without doing it

**Examples:**
```bash
rabbitmirror db cleanup
rabbitmirror db cleanup --policy old_entries --dry-run
```

---

#### `clear-cache` - Cache Management

**Syntax:**
```bash
rabbitmirror db clear-cache [OPTIONS]
```

**Options:**
- `--namespace TEXT` - Specific cache namespace to clear

**Examples:**
```bash
rabbitmirror db clear-cache
rabbitmirror db clear-cache --namespace analysis
```

---

#### `reset` - Reset Database

**Syntax:**
```bash
rabbitmirror db reset
```

**⚠️ WARNING:** This command deletes all data. Requires confirmation.

---

#### `shell` - Database Shell

**Syntax:**
```bash
rabbitmirror db shell
```

Opens interactive database shell (sqlite3, psql, etc.).

---

## Standalone Commands

### `tui` - Terminal User Interface

Launch the interactive TUI application.

**Syntax:**
```bash
rabbitmirror tui [OPTIONS]
```

**Options:**
- `--theme {dark,light}` - TUI theme (default: dark)

**Examples:**
```bash
rabbitmirror tui
rabbitmirror tui --theme light
```

---

### `completion` - Shell Completion

Generate shell completion scripts.

**Syntax:**
```bash
rabbitmirror completion SHELL
```

**Arguments:**
- `SHELL` - Shell type {bash,zsh,fish}

**Examples:**
```bash
# Generate completion for bash
rabbitmirror completion bash

# Install completion for zsh
rabbitmirror completion zsh >> ~/.zshrc
```

---

## Configuration

### Configuration Files

- **Global**: `~/.rabbitmirror_config.json`
- **Local**: `./.rabbitmirror_config.json`

### Available Configuration Keys

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `output_dir` | string | current directory | Default output directory |
| `default_format` | string | json | Default output format |
| `default_threshold` | float | 0.7 | Default analysis threshold (0.1-1.0) |

### Environment Variables

- `DATABASE_URL` - Database connection URL
- `REDIS_URL` - Redis cache connection URL
- `RABBITMIRROR_CONFIG` - Config file path override

## Input/Output Formats

### Supported Input Formats
- **HTML**: YouTube Takeout watch history files
- **JSON**: Parsed data files
- **CSV**: Comma-separated values
- **YAML**: YAML data files
- **Excel**: Excel spreadsheet files

### Supported Output Formats
- **JSON**: JavaScript Object Notation
- **CSV**: Comma-separated values
- **YAML**: YAML Ain't Markup Language
- **Excel**: Microsoft Excel format (.xlsx)
- **HTML**: Reports and dashboards
- **PDF**: Portable Document Format reports
- **Markdown**: Text format for reports
- **PNG**: Images (QR codes, visualizations)

## Error Handling

### Exit Codes
- `0` - Success
- `1` - General error (file not found, parsing error, validation failure, etc.)

### Error Messages
- **Success**: `✅ Success message with details`
- **Error**: `❌ Error message with context and suggestions`
- **Warning**: `⚠️ Warning message`
- **Info**: `ℹ️ Information message`

## Common Usage Patterns

### Basic Analysis Workflow
```bash
# 1. Parse YouTube data
rabbitmirror process parse watch-history.html youtube -o parsed.json

# 2. Run analysis
rabbitmirror analyze detect-patterns parsed.json -o patterns.json
rabbitmirror analyze cluster parsed.json -o clusters.json

# 3. Generate report
rabbitmirror report export-dashboard patterns.json --interactive
```

### Batch Processing
```bash
# Process multiple files
rabbitmirror process batch-process ./youtube-data/ -o ./results/ -f json -r

# Analyze all results
for file in ./results/*.json; do
  rabbitmirror analyze detect-patterns "$file" -o "analysis_$(basename "$file")"
done
```

### Configuration Management
```bash
# Set up default preferences
rabbitmirror config set output_dir ~/rabbitmirror-analysis
rabbitmirror config set default_format json
rabbitmirror config set default_threshold 0.8

# View current settings
rabbitmirror config list --format json
```

## Troubleshooting

### Common Issues

1. **File not found errors**: Ensure file paths are correct and files exist
2. **Permission errors**: Check file and directory permissions
3. **Format errors**: Verify input files are in expected format
4. **Database errors**: Check DATABASE_URL environment variable
5. **Memory issues**: Use batch processing for large datasets

### Debug Options

- Use `--verbose` flag for detailed output
- Check configuration with `rabbitmirror config list`
- Validate data files with `rabbitmirror utils validate`
- Check database status with `rabbitmirror db status`

### Getting Help

- Command help: `rabbitmirror COMMAND --help`
- Group help: `rabbitmirror GROUP --help`
- General help: `rabbitmirror --help`
- TUI help: Press 'H' in the TUI interface

---

*For more information and examples, visit the [RabbitMirror documentation](https://romulusaugustus.github.io/RabbitMirror/).*
