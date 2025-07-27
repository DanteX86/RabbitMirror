# RabbitMirror Configuration Guide

## Overview

RabbitMirror provides a flexible and comprehensive configuration system that allows you to customize every aspect of the application's behavior. This guide covers all configuration options, management commands, and best practices for setting up RabbitMirror to meet your specific needs.

## Configuration Architecture

### Configuration Levels

RabbitMirror supports two levels of configuration:

1. **Global Configuration**: User-wide settings stored in your home directory
   - Location: `~/.rabbitmirror_config.json`
   - Applied to all RabbitMirror projects
   - Useful for personal preferences and default settings

2. **Local Configuration**: Project-specific settings stored in the current working directory
   - Location: `./.rabbitmirror_config.json`
   - Overrides global settings for the current project
   - Useful for project-specific customizations

### Configuration Priority

Settings are resolved in the following order (highest to lowest priority):
1. Command-line arguments
2. Local configuration file
3. Global configuration file
4. Default values

## Multi-Platform Configuration

With RabbitMirror, you can manage configurations for different data sources, like YouTube, Netflix, and Spotify.

### Example Multi-Platform Settings

```bash
# YouTube-specific parser settings
rabbitmirror config set youtube.encoding "utf-8"
rabbitmirror config set youtube.strict_mode false

# Netflix-specific parser settings
rabbitmirror config set netflix.fallback_encodings '["utf-8", "latin-1"]'
rabbitmirror config set netflix.max_retries 5

# Spotify-specific parser settings
rabbitmirror config set spotify.data_format "json"
rabbitmirror config set spotify.timeout 45
```

## Configuration Management Commands

### Setting Configuration Values

```bash
# Set local configuration (project-specific)
rabbitmirror config set default_output_format "json"
rabbitmirror config set analysis_threshold "0.7"

# Set global configuration (user-wide)
rabbitmirror config set default_theme "dark" --global
rabbitmirror config set max_workers "4" --global
```

### Getting Configuration Values

```bash
# Get local configuration value
rabbitmirror config get default_output_format

# Get global configuration value
rabbitmirror config get default_theme --global
```

### Listing Configuration

```bash
# List all local configuration (default text format)
rabbitmirror config list

# List global configuration in JSON format
rabbitmirror config list --global --format json

# List configuration in YAML format
rabbitmirror config list --format yaml
```

## Configuration File Formats

### JSON Configuration (.rabbitmirror_config.json)

```json
{
  "default_output_format": "json",
  "analysis_threshold": 0.7,
  "clustering_eps": 0.3,
  "clustering_min_samples": 5,
  "max_workers": 4,
  "default_theme": "dark",
  "output_directory": "exports",
  "enable_progress_bars": true,
  "log_level": "INFO"
}
```

### YAML Configuration (sample_config.yaml)

For more complex configurations, you can use YAML format:

```yaml
rabbitmirror:
  # General settings
  version: "1.0.0"

  # Parser configuration
  parser:
    encoding: "utf-8"
    fallback_encodings: ["utf-8-sig", "latin-1", "cp1252"]
    max_retries: 3
    timeout: 30
    strict_mode: false

  # Export settings
  export:
    default_format: "json"
    output_directory: "exports"
    supported_formats: ["json", "csv", "yaml", "excel", "html"]
    compression: false
    include_metadata: true

  # Analysis configuration
  analysis:
    clustering:
      algorithm: "DBSCAN"
      eps: 0.3
      min_samples: 5
      max_features: 1000
      feature_weights:
        title_similarity: 0.7
        temporal_proximity: 0.3

    pattern_detection:
      enabled: true
      sensitivity: 0.7
      min_confidence: 0.6
      pattern_types: ["suppression", "manipulation", "echo_chamber"]

    trend_analysis:
      enabled: true
      window_size: 7
      smoothing_factor: 0.3
      seasonal_analysis: true
```

## Configuration Categories

### 1. Parser Configuration

Controls how YouTube watch history files are parsed and processed.

#### Available Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `parser_encoding` | string | "utf-8" | Character encoding for HTML files |
| `parser_fallback_encodings` | array | ["utf-8-sig", "latin-1"] | Fallback encodings if primary fails |
| `parser_max_retries` | integer | 3 | Maximum retry attempts for failed parsing |
| `parser_timeout` | integer | 30 | Timeout in seconds for parsing operations |
| `parser_strict_mode` | boolean | false | Enable strict parsing validation |

#### Example Configuration

```bash
# Basic parser settings
rabbitmirror config set parser_encoding "utf-8"
rabbitmirror config set parser_timeout 60
rabbitmirror config set parser_strict_mode true

# Advanced parser settings
rabbitmirror config set parser_fallback_encodings '["utf-8-sig", "latin-1", "cp1252"]'
```

### 2. Clustering Configuration

Configures video clustering algorithms and parameters.

#### Available Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `clustering_algorithm` | string | "DBSCAN" | Clustering algorithm ("DBSCAN", "KMeans", "Hierarchical") |
| `clustering_eps` | float | 0.3 | DBSCAN epsilon parameter |
| `clustering_min_samples` | integer | 5 | DBSCAN minimum samples parameter |
| `clustering_n_clusters` | integer | 8 | Number of clusters for KMeans |
| `clustering_max_features` | integer | 1000 | Maximum features for text analysis |
| `clustering_feature_weights` | object | {} | Weights for different feature types |

#### Example Configuration

```bash
# Basic clustering settings
rabbitmirror config set clustering_algorithm "DBSCAN"
rabbitmirror config set clustering_eps 0.25
rabbitmirror config set clustering_min_samples 3

# Advanced clustering settings
rabbitmirror config set clustering_max_features 2000
rabbitmirror config set clustering_feature_weights '{"title": 0.7, "temporal": 0.3}'
```

### 3. Analysis Configuration

Controls various analysis modules and their behavior.

#### Pattern Detection

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `pattern_detection_enabled` | boolean | true | Enable pattern detection analysis |
| `pattern_detection_sensitivity` | float | 0.7 | Detection sensitivity (0.0-1.0) |
| `pattern_detection_min_confidence` | float | 0.6 | Minimum confidence threshold |
| `pattern_detection_types` | array | ["all"] | Types of patterns to detect |

#### Suppression Analysis

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `suppression_baseline_period` | integer | 30 | Baseline period in days |
| `suppression_detection_threshold` | float | 0.5 | Detection threshold |
| `suppression_categories` | array | [] | Specific categories to analyze |

#### Trend Analysis

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `trend_analysis_enabled` | boolean | true | Enable trend analysis |
| `trend_window_size` | integer | 7 | Analysis window size in days |
| `trend_smoothing_factor` | float | 0.3 | Trend smoothing factor |
| `trend_seasonal_analysis` | boolean | true | Enable seasonal analysis |

#### Example Configuration

```bash
# Pattern detection settings
rabbitmirror config set pattern_detection_enabled true
rabbitmirror config set pattern_detection_sensitivity 0.8
rabbitmirror config set pattern_detection_min_confidence 0.7

# Suppression analysis settings
rabbitmirror config set suppression_baseline_period 45
rabbitmirror config set suppression_detection_threshold 0.6

# Trend analysis settings
rabbitmirror config set trend_window_size 14
rabbitmirror config set trend_smoothing_factor 0.2
```

### 4. Export Configuration

Controls data export formats, destinations, and options.

#### Available Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `default_output_format` | string | "json" | Default export format |
| `output_directory` | string | "exports" | Default output directory |
| `export_compression` | boolean | false | Enable output compression |
| `export_include_metadata` | boolean | true | Include metadata in exports |
| `export_timestamp_format` | string | "iso" | Timestamp format in exports |

#### Supported Formats

- **JSON**: Structured data format (default)
- **CSV**: Comma-separated values for spreadsheets
- **YAML**: Human-readable structured format
- **Excel**: Microsoft Excel format with multiple sheets
- **HTML**: Web-compatible format with styling

#### Example Configuration

```bash
# Basic export settings
rabbitmirror config set default_output_format "csv"
rabbitmirror config set output_directory "my_exports"
rabbitmirror config set export_compression true

# Advanced export settings
rabbitmirror config set export_include_metadata false
rabbitmirror config set export_timestamp_format "human"
```

### 5. Performance Configuration

Controls resource usage and optimization settings.

#### Available Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `max_workers` | integer | 4 | Maximum parallel workers |
| `max_memory_usage` | string | "1GB" | Maximum memory usage |
| `parallel_processing` | boolean | true | Enable parallel processing |
| `cache_enabled` | boolean | true | Enable result caching |
| `cache_size` | string | "100MB" | Maximum cache size |

#### Example Configuration

```bash
# Performance settings
rabbitmirror config set max_workers 8
rabbitmirror config set max_memory_usage "2GB"
rabbitmirror config set parallel_processing true
rabbitmirror config set cache_enabled true
```

### 6. Logging Configuration

Controls logging behavior and output.

#### Available Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `log_level` | string | "INFO" | Logging level ("DEBUG", "INFO", "WARNING", "ERROR") |
| `log_file` | string | "logs/rabbitmirror.log" | Log file path |
| `log_max_size` | string | "10MB" | Maximum log file size |
| `log_backup_count` | integer | 5 | Number of backup log files |
| `log_format` | string | "standard" | Log message format |

#### Example Configuration

```bash
# Logging settings
rabbitmirror config set log_level "DEBUG"
rabbitmirror config set log_file "logs/debug.log"
rabbitmirror config set log_max_size "50MB"
rabbitmirror config set log_backup_count 10
```

### 7. Security Configuration

Controls security-related settings and data privacy.

#### Available Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `data_anonymization_enabled` | boolean | false | Enable data anonymization |
| `hash_urls` | boolean | false | Hash video URLs for privacy |
| `remove_personal_info` | boolean | true | Remove personal information |
| `require_authentication` | boolean | false | Require authentication for web interface |

#### Example Configuration

```bash
# Security settings
rabbitmirror config set data_anonymization_enabled true
rabbitmirror config set hash_urls true
rabbitmirror config set remove_personal_info true
```

### 8. Error Handling Configuration

Controls error recovery and retry behavior.

#### Available Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `retry_attempts` | integer | 3 | Maximum retry attempts |
| `retry_delay` | float | 1.0 | Delay between retries in seconds |
| `circuit_breaker_enabled` | boolean | true | Enable circuit breaker pattern |
| `circuit_breaker_failure_threshold` | integer | 5 | Failure threshold for circuit breaker |
| `timeout_parse` | integer | 30 | Parse operation timeout |
| `timeout_export` | integer | 60 | Export operation timeout |
| `timeout_analysis` | integer | 120 | Analysis operation timeout |

#### Example Configuration

```bash
# Error handling settings
rabbitmirror config set retry_attempts 5
rabbitmirror config set retry_delay 2.0
rabbitmirror config set circuit_breaker_enabled true
rabbitmirror config set timeout_analysis 300
```

## Configuration Profiles

### Creating Configuration Profiles

You can create different configuration profiles for different use cases:

#### 1. Performance Profile (for large datasets)

```bash
# Performance-optimized settings
rabbitmirror config set max_workers 8 --global
rabbitmirror config set max_memory_usage "4GB" --global
rabbitmirror config set parallel_processing true --global
rabbitmirror config set cache_enabled true --global
rabbitmirror config set clustering_max_features 2000 --global
```

#### 2. Privacy Profile (for sensitive data)

```bash
# Privacy-focused settings
rabbitmirror config set data_anonymization_enabled true --global
rabbitmirror config set hash_urls true --global
rabbitmirror config set remove_personal_info true --global
rabbitmirror config set log_level "ERROR" --global
```

#### 3. Research Profile (for academic use)

```bash
# Research-oriented settings
rabbitmirror config set pattern_detection_sensitivity 0.9 --global
rabbitmirror config set clustering_eps 0.2 --global
rabbitmirror config set trend_window_size 30 --global
rabbitmirror config set export_include_metadata true --global
rabbitmirror config set log_level "DEBUG" --global
```

#### 4. Quick Analysis Profile (for fast processing)

```bash
# Quick analysis settings
rabbitmirror config set clustering_algorithm "KMeans" --global
rabbitmirror config set clustering_n_clusters 5 --global
rabbitmirror config set pattern_detection_enabled false --global
rabbitmirror config set trend_analysis_enabled false --global
```

## Environment Variables

You can also set configuration options using environment variables with the `RABBITMIRROR_` prefix:

```bash
# Export configuration via environment variables
export RABBITMIRROR_DEFAULT_OUTPUT_FORMAT="csv"
export RABBITMIRROR_MAX_WORKERS="8"
export RABBITMIRROR_LOG_LEVEL="DEBUG"
export RABBITMIRROR_OUTPUT_DIRECTORY="/path/to/exports"

# Run with environment configuration
rabbitmirror analyze cluster my_history.html
```

## Configuration Validation

### Validating Configuration Files

```bash
# Validate configuration file structure
rabbitmirror utils validate .rabbitmirror_config.json --format json

# Validate YAML configuration
rabbitmirror utils validate sample_config.yaml --format yaml

# Validate against custom schema
rabbitmirror utils validate config.json --schema custom_schema.json
```

### Configuration Schema

RabbitMirror validates configuration files against predefined schemas:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "default_output_format": {
      "type": "string",
      "enum": ["json", "csv", "yaml", "excel", "html"]
    },
    "clustering_eps": {
      "type": "number",
      "minimum": 0.1,
      "maximum": 2.0
    },
    "max_workers": {
      "type": "integer",
      "minimum": 1,
      "maximum": 32
    }
  }
}
```

## Best Practices

### 1. Configuration Organization

- Use global configuration for personal preferences
- Use local configuration for project-specific settings
- Keep sensitive settings in local configuration files
- Document custom configuration choices

### 2. Performance Tuning

```bash
# For large datasets (>10,000 videos)
rabbitmirror config set max_workers 8
rabbitmirror config set clustering_max_features 2000
rabbitmirror config set parallel_processing true

# For small datasets (<1,000 videos)
rabbitmirror config set max_workers 2
rabbitmirror config set clustering_max_features 500
rabbitmirror config set cache_enabled false
```

### 3. Memory Management

```bash
# Low memory systems (<4GB RAM)
rabbitmirror config set max_memory_usage "1GB"
rabbitmirror config set max_workers 2
rabbitmirror config set cache_size "50MB"

# High memory systems (>16GB RAM)
rabbitmirror config set max_memory_usage "8GB"
rabbitmirror config set max_workers 12
rabbitmirror config set cache_size "1GB"
```

### 4. Security Considerations

```bash
# For sensitive data processing
rabbitmirror config set data_anonymization_enabled true
rabbitmirror config set hash_urls true
rabbitmirror config set log_level "WARNING"  # Reduce logging detail
```

## Troubleshooting Configuration

### Common Issues

#### 1. Configuration Not Applied

Check configuration priority:
```bash
# Check current effective configuration
rabbitmirror config list --format json

# Check global configuration
rabbitmirror config list --global --format json

# Check for environment variable overrides
env | grep RABBITMIRROR_
```

#### 2. Invalid Configuration Values

```bash
# Validate configuration file
rabbitmirror utils validate .rabbitmirror_config.json

# Check specific setting
rabbitmirror config get problematic_setting
```

#### 3. Performance Issues

```bash
# Check resource-intensive settings
rabbitmirror config get max_workers
rabbitmirror config get max_memory_usage
rabbitmirror config get clustering_max_features

# Reset to defaults
rabbitmirror config set max_workers 4
rabbitmirror config set clustering_eps 0.3
```

### Configuration Reset

```bash
# Remove local configuration (reset to global/defaults)
rm .rabbitmirror_config.json

# Remove global configuration (reset to defaults)
rm ~/.rabbitmirror_config.json

# Verify reset
rabbitmirror config list
```

## Advanced Configuration

### Custom Configuration Loading

You can load configuration from custom files:

```bash
# Load custom configuration
export RABBITMIRROR_CONFIG_FILE="/path/to/custom_config.yaml"
rabbitmirror analyze cluster my_history.html
```

### Configuration Inheritance

Create a base configuration and extend it:

```yaml
# base_config.yaml
rabbitmirror:
  parser:
    encoding: "utf-8"
    timeout: 30
  export:
    default_format: "json"
```

```yaml
# project_config.yaml
extends: "base_config.yaml"
rabbitmirror:
  analysis:
    clustering:
      eps: 0.2
      min_samples: 3
```

### Dynamic Configuration

Some settings can be modified at runtime:

```python
from rabbitmirror.config_manager import ConfigManager

# Runtime configuration changes
config = ConfigManager()
config.set("clustering_eps", 0.25)
config.set("max_workers", 6)

# Apply changes immediately
config.reload()
```

## Migration Guide

### Upgrading Configuration

When upgrading RabbitMirror versions, configuration may need migration:

```bash
# Backup current configuration
cp .rabbitmirror_config.json .rabbitmirror_config.json.backup

# Validate against new schema
rabbitmirror utils validate .rabbitmirror_config.json

# Update deprecated settings (if any)
rabbitmirror config set new_setting_name "value"
```

### Configuration Version Compatibility

RabbitMirror maintains backward compatibility for configuration files:

| Version | Configuration Changes | Migration Required |
|---------|----------------------|-------------------|
| 1.0.0   | Initial configuration system | No |
| 1.1.0   | Added security settings | No |
| 1.2.0   | Enhanced clustering options | No |

## Reference

### Complete Configuration Example

```json
{
  "default_output_format": "json",
  "output_directory": "exports",
  "clustering_algorithm": "DBSCAN",
  "clustering_eps": 0.3,
  "clustering_min_samples": 5,
  "clustering_max_features": 1000,
  "pattern_detection_enabled": true,
  "pattern_detection_sensitivity": 0.7,
  "pattern_detection_min_confidence": 0.6,
  "suppression_baseline_period": 30,
  "suppression_detection_threshold": 0.5,
  "trend_analysis_enabled": true,
  "trend_window_size": 7,
  "trend_smoothing_factor": 0.3,
  "max_workers": 4,
  "max_memory_usage": "1GB",
  "parallel_processing": true,
  "cache_enabled": true,
  "cache_size": "100MB",
  "log_level": "INFO",
  "log_file": "logs/rabbitmirror.log",
  "log_max_size": "10MB",
  "log_backup_count": 5,
  "data_anonymization_enabled": false,
  "hash_urls": false,
  "remove_personal_info": true,
  "retry_attempts": 3,
  "retry_delay": 1.0,
  "circuit_breaker_enabled": true,
  "timeout_parse": 30,
  "timeout_export": 60,
  "timeout_analysis": 120
}
```

## See Also

- [API Reference](api_reference.md)
- [Getting Started Guide](tutorials/01_getting_started.md)
- [Advanced Usage](tutorials/02_advanced_usage.md)
- [Performance Tuning Guide](performance_tuning.md)
- [FAQ](FAQ.md)
