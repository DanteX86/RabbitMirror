# RabbitMirror Examples and Recipes

## Overview

This document provides practical examples and step-by-step recipes to help you leverage RabbitMirror effectively in real-world scenarios. Whether you're a researcher, content creator, privacy advocate, or curious user, these examples will guide you through common tasks and advanced use cases.

## Table of Contents

1. [Quick Start Examples](#quick-start-examples)
2. [Academic Research Recipes](#academic-research-recipes)
3. [Content Creator Analysis](#content-creator-analysis)
4. [Privacy and Security Workflows](#privacy-and-security-workflows)
5. [Data Processing Recipes](#data-processing-recipes)
6. [Automation Scripts](#automation-scripts)
7. [Troubleshooting Examples](#troubleshooting-examples)
8. [Integration Examples](#integration-examples)

## Quick Start Examples

### Example 1: First-Time Analysis (YouTube)

**Goal:** Get started with your first YouTube watch history analysis.

```bash
# Step 1: Parse your YouTube watch history
rabbitmirror process parse watch-history.html youtube --output my_data.json

# Step 2: Quick cluster analysis
rabbitmirror analyze cluster my_data.json --output clusters.json

# Step 3: Generate a basic report
rabbitmirror report generate-report my_data.json --output-dir reports/

# Step 4: View results
open reports/index.html  # macOS
# or
xdg-open reports/index.html  # Linux
```

### Example 1b: Multi-Platform Analysis

**Goal:** Parse and analyze data from different streaming platforms.

```bash
# Parse YouTube data
rabbitmirror process parse youtube-history.html youtube --output youtube_data.json

# Parse Netflix data
rabbitmirror process parse netflix-history.json netflix --output netflix_data.json

# Parse Spotify data
rabbitmirror process parse spotify-history.json spotify --output spotify_data.json

# Generate combined report
rabbitmirror report generate-multi-platform --inputs youtube_data.json netflix_data.json spotify_data.json --output-dir multi_platform_analysis/
```

### Example 2: Using the TUI (Recommended for Beginners)

**Goal:** Use the interactive Terminal User Interface for guided analysis.

```bash
# Launch the TUI
rabbitmirror tui

# Follow the on-screen prompts:
# 1. Select your watch history file
# 2. Choose analysis type
# 3. Configure output settings
# 4. Review results
```

### Example 3: Quick Export to Excel

**Goal:** Export your data for analysis in Excel or other spreadsheet applications.

```bash
# Parse and export directly to Excel
rabbitmirror process parse watch-history.html --output data.json
rabbitmirror export data.json --format excel --output my_youtube_analysis

# Result: my_youtube_analysis.xlsx with multiple sheets
```

## Advanced Recipes

### Recipe 1: Batch Processing Multiple Files

**Scenario:** You have a directory of history files you want to process in bulk.

```bash
# Recursively process multiple history files and export results
rabbitmirror process batch-process ./history_files/ --output-dir ./processed/ --recursive
```

### Recipe 2: Automated Analysis Pipeline

**Scenario:** Automate an entire analysis workflow using a shell script.

```bash
#! /bin/bash

HISTORY_FILE="my_watch_history.html"
OUTPUT_DIR="my_analysis_results"
mkdir -p $OUTPUT_DIR

# Parse history file
rabbitmirror process parse $HISTORY_FILE --output $OUTPUT_DIR/parsed.json

# Analyze clusters
rabbitmirror analyze cluster $OUTPUT_DIR/parsed.json --output $OUTPUT_DIR/clusters.json

# Detect adversarial patterns
rabbitmirror analyze detect-patterns $OUTPUT_DIR/parsed.json --output $OUTPUT_DIR/patterns.json

# Generate report
rabbitmirror report generate-report $OUTPUT_DIR/parsed.json --output-dir $OUTPUT_DIR/

echo "Analysis complete! Results saved to $OUTPUT_DIR/"
```

### Recipe 3: Customized Clustering

**Scenario:** Fine-tune clustering parameters for specific analysis needs.

```bash
# Perform clustering with custom parameters
rabbitmirror analyze cluster parsed_data.json --eps 0.2 --min-samples 3 --algorithm kmeans --n-clusters 5 --output custom_clusters.json
```

### Recipe 4: Using Configuration Profiles

**Scenario:** Switching between different configuration profiles for various analysis tasks.

```bash
# Activate a privacy-focused configuration
cat <<EOF > privacy_profile.json
{
  "data_anonymization_enabled": true,
  "hash_urls": true
}
EOF

rabbitmirror config set --config privacy_profile.json

# Run analysis with the privacy profile
rabbitmirror analyze cluster parsed_data.json --output clusters.json
```

### Recipe 5: Using Environment Variables for Configuration

**Scenario:** Configure RabbitMirror using environment variables for quick adjustments.

```bash
# Set environment variables for configuration
export RABBITMIRROR_DEFAULT_OUTPUT_FORMAT="csv"
export RABBITMIRROR_LOG_LEVEL="DEBUG"

# Run analysis with environment configuration
rabbitmirror analyze cluster parsed_data.json
```

## Example Workflows

### Workflow 1: Research Analysis

1. **Objective:** Conduct an in-depth analysis of YouTube viewing behavior.
2. **Setup:**
   - Install RabbitMirror and dependencies
   - Download YouTube watch history via Google Takeout
3. **Process:**
   - Parse the data: `rabbitmirror process parse my_watch_history.html`
   - Perform clustering: `rabbitmirror analyze cluster parsed_data.json`
   - Detect patterns: `rabbitmirror analyze detect-patterns parsed_data.json`
   - Generate detailed report: `rabbitmirror report generate-report parsed_data.json`
4. **Result:**
   - Comprehensive insights into viewing patterns, content clustering, and potential recommendation biases.

### Workflow 2: Data Privacy Review

1. **Objective:** Ensure data privacy when analyzing personal watch history.
2. **Setup:**
   - Enable data anonymization in settings
3. **Process:**
   - Parse with anonymization: `rabbitmirror process parse my_watch_history.html --anonymize`
   - Output in non-personal format: `rabbitmirror report generate-report parsed_data.json`
4. **Result:**
   - Analysis reports that respect data privacy and protect personal information.

### Workflow 3: Content Suppression Analysis

1. **Objective:** Identify content suppression patterns in recommendations.
2. **Setup:**
   - Access to watch history data
3. **Process:**
   - Parse the history: `rabbitmirror process parse my_watch_history.html`
   - Analyze suppression: `rabbitmirror analyze analyze-suppression parsed_data.json`
   - Review results: Check `suppression.json` for detailed findings
4. **Result:**
   - Insights into potential content suppression by recommendation algorithms.

## Tips and Best Practices

### 1. Use Configuration Profiles
- Save and switch between different analysis profiles for convenience.

### 2. Automate Routine Tasks
- Leverage shell scripts to automate common workflows and reduce manual effort.

### 3. Monitor Resource Usage
- Use monitoring tools and logs to assess performance and optimize resource allocation.

### 4. Validate Output Regularly
- Regularly validate the output files to ensure accuracy and consistency in processing.

### 5. Stay Updated
- Follow the latest updates and best practices in the RabbitMirror documentation and community.

## Conclusion

These examples and recipes demonstrate the versatility and power of RabbitMirror for analyzing YouTube viewing histories. Use these guides to tailor your analyses to your specific needs, and explore the full capabilities of RabbitMirror in your research and analysis tasks.

## See Also

- [Performance Tuning Guide](performance_tuning.md)
- [Configuration Guide](configuration.md)
- [Advanced Usage](tutorials/02_advanced_usage.md)
- [API Reference](api_reference.md)
- [Troubleshooting FAQ](FAQ.md)
