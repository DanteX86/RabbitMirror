# RabbitMirror API Reference

## Overview

This document provides a comprehensive API reference for RabbitMirror's core modules and classes. The API is designed to be both powerful and accessible, allowing developers to integrate RabbitMirror's functionality into their own applications.

## Core Modules

### `rabbitmirror.parser`

The parser module handles the extraction and processing of history data from multiple platforms including YouTube, Netflix, Spotify, and others.

#### HistoryParser

```python
class HistoryParser:
    """
    Main class for parsing YouTube watch history HTML files.

    Args:
        encoding (str, optional): File encoding. Defaults to 'utf-8'.
        strict_mode (bool, optional): Enable strict parsing mode. Defaults to False.
        progress_callback (callable, optional): Progress callback function.
    """

    def __init__(self, encoding='utf-8', strict_mode=False, progress_callback=None):
        pass

    def parse(self, file_path: str) -> Dict[str, Any]:
        """
        Parse YouTube watch history HTML file.

        Args:
            file_path (str): Path to the HTML file

        Returns:
            Dict[str, Any]: Parsed data with metadata and entries

        Raises:
            ParsingError: If file cannot be parsed
            FileNotFoundError: If file doesn't exist
        """
        pass

    def validate_file(self, file_path: str) -> bool:
        """
        Validate if file is a proper YouTube watch history export.

        Args:
            file_path (str): Path to the HTML file

        Returns:
            bool: True if file is valid
        """
        pass
```

**Example Usage:**
```python
from rabbitmirror.parser import HistoryParser

parser = HistoryParser(encoding='utf-8')
data = parser.parse('watch-history.html')
print(f"Parsed {data['metadata']['total_entries']} entries")
```

### `rabbitmirror.cluster_engine`

The cluster engine provides video clustering and similarity analysis functionality.

#### ClusterEngine

```python
class ClusterEngine:
    """
    Advanced clustering engine for video content analysis.

    Args:
        algorithm (str): Clustering algorithm ('dbscan', 'kmeans', 'hierarchical')
        eps (float): DBSCAN epsilon parameter
        min_samples (int): DBSCAN minimum samples parameter
        n_clusters (int): Number of clusters for KMeans
        feature_weights (Dict[str, float]): Weights for different features
    """

    def __init__(self, algorithm='dbscan', eps=0.3, min_samples=5,
                 n_clusters=8, feature_weights=None):
        pass

    def cluster_videos(self, data: List[Dict]) -> Dict[str, Any]:
        """
        Cluster videos based on content similarity.

        Args:
            data (List[Dict]): List of video entries

        Returns:
            Dict[str, Any]: Clustering results with cluster assignments
        """
        pass

    def get_cluster_statistics(self, clustering_results: Dict) -> Dict[str, Any]:
        """
        Generate comprehensive cluster statistics.

        Args:
            clustering_results (Dict): Results from cluster_videos()

        Returns:
            Dict[str, Any]: Detailed cluster statistics
        """
        pass
```

**Example Usage:**
```python
from rabbitmirror.cluster_engine import ClusterEngine

engine = ClusterEngine(algorithm='dbscan', eps=0.3, min_samples=5)
clusters = engine.cluster_videos(parsed_data['entries'])
stats = engine.get_cluster_statistics(clusters)
```

### `rabbitmirror.adversarial_profiler`

Detects potential algorithmic manipulation and adversarial patterns.

#### AdversarialProfiler

```python
class AdversarialProfiler:
    """
    Advanced pattern detection for algorithmic manipulation analysis.

    Args:
        sensitivity (float): Detection sensitivity (0.0-1.0)
        min_confidence (float): Minimum confidence threshold
        pattern_types (List[str]): Types of patterns to detect
    """

    def __init__(self, sensitivity=0.7, min_confidence=0.6, pattern_types=None):
        pass

    def detect_patterns(self, data: List[Dict]) -> Dict[str, Any]:
        """
        Detect adversarial patterns in viewing history.

        Args:
            data (List[Dict]): Video viewing history data

        Returns:
            Dict[str, Any]: Detected patterns with confidence scores
        """
        pass

    def analyze_echo_chambers(self, data: List[Dict]) -> Dict[str, Any]:
        """
        Analyze potential echo chamber formation.

        Args:
            data (List[Dict]): Video viewing history data

        Returns:
            Dict[str, Any]: Echo chamber analysis results
        """
        pass
```

### `rabbitmirror.suppression_index`

Analyzes content suppression patterns in recommendation systems.

#### SuppressionAnalyzer

```python
class SuppressionAnalyzer:
    """
    Analyzer for detecting content suppression patterns.

    Args:
        baseline_period (int): Baseline period in days
        detection_threshold (float): Suppression detection threshold
        categories (List[str]): Content categories to analyze
    """

    def __init__(self, baseline_period=30, detection_threshold=0.5, categories=None):
        pass

    def analyze_suppression(self, data: List[Dict]) -> Dict[str, Any]:
        """
        Analyze content suppression patterns.

        Args:
            data (List[Dict]): Video viewing history data

        Returns:
            Dict[str, Any]: Suppression analysis results
        """
        pass

    def detect_category_suppression(self, data: List[Dict]) -> Dict[str, List]:
        """
        Detect suppression by content category.

        Args:
            data (List[Dict]): Video viewing history data

        Returns:
            Dict[str, List]: Suppressed categories with details
        """
        pass
```

### `rabbitmirror.trend_analyzer`

Provides temporal analysis and trend detection capabilities.

#### TrendAnalyzer

```python
class TrendAnalyzer:
    """
    Advanced trend analysis for temporal viewing patterns.

    Args:
        window_size (int): Analysis window size in days
        smoothing_factor (float): Trend smoothing factor
        seasonal_analysis (bool): Enable seasonal analysis
    """

    def __init__(self, window_size=7, smoothing_factor=0.3, seasonal_analysis=True):
        pass

    def analyze_temporal_patterns(self, data: List[Dict]) -> Dict[str, Any]:
        """
        Analyze temporal viewing patterns.

        Args:
            data (List[Dict]): Video viewing history data

        Returns:
            Dict[str, Any]: Temporal analysis results
        """
        pass

    def detect_binge_sessions(self, data: List[Dict], threshold_minutes=30) -> List[Dict]:
        """
        Detect binge-watching sessions.

        Args:
            data (List[Dict]): Video viewing history data
            threshold_minutes (int): Time threshold for session grouping

        Returns:
            List[Dict]: Detected binge sessions
        """
        pass
```

### `rabbitmirror.export_formatter`

Handles data export to various formats.

#### ExportFormatter

```python
class ExportFormatter:
    """
    Flexible data export formatter supporting multiple output formats.

    Args:
        output_dir (str): Output directory path
        compression (bool): Enable output compression
        custom_templates (Dict[str, str]): Custom format templates
    """

    def __init__(self, output_dir='exports/', compression=False, custom_templates=None):
        pass

    def export_json(self, data: Dict, filename: str) -> str:
        """Export data to JSON format."""
        pass

    def export_csv(self, data: Dict, filename: str) -> str:
        """Export data to CSV format."""
        pass

    def export_excel(self, data: Dict, filename: str) -> str:
        """Export data to Excel format with multiple sheets."""
        pass

    def export_yaml(self, data: Dict, filename: str) -> str:
        """Export data to YAML format."""
        pass
```

### `rabbitmirror.config_manager`

Manages application configuration and settings.

#### ConfigManager

```python
class ConfigManager:
    """
    Centralized configuration management system.

    Args:
        config_file (str): Path to configuration file
        global_config (bool): Use global configuration
        auto_save (bool): Automatically save changes
    """

    def __init__(self, config_file=None, global_config=False, auto_save=True):
        pass

    def get(self, key: str, default=None) -> Any:
        """Get configuration value."""
        pass

    def set(self, key: str, value: Any, persist=True) -> None:
        """Set configuration value."""
        pass

    def load_config(self, config_file: str) -> None:
        """Load configuration from file."""
        pass

    def save_config(self, config_file: str = None) -> None:
        """Save current configuration to file."""
        pass
```

## Error Handling

### Exception Classes

```python
class RabbitMirrorError(Exception):
    """Base exception class for RabbitMirror."""
    pass

class ParsingError(RabbitMirrorError):
    """Raised when parsing fails."""
    pass

class AnalysisError(RabbitMirrorError):
    """Raised during analysis operations."""
    pass

class ExportError(RabbitMirrorError):
    """Raised during data export."""
    pass

class ConfigurationError(RabbitMirrorError):
    """Raised for configuration issues."""
    pass
```

## Data Structures

### Video Entry

```python
@dataclass
class VideoEntry:
    """Represents a single video entry from watch history."""
    title: str
    url: str
    timestamp: datetime
    channel: Optional[str] = None
    duration: Optional[timedelta] = None
    category: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
```

### Cluster Result

```python
@dataclass
class ClusterResult:
    """Represents clustering analysis results."""
    cluster_id: int
    videos: List[VideoEntry]
    centroid: Optional[np.ndarray]
    characteristics: Dict[str, Any]
    quality_metrics: Dict[str, float]
```

### Pattern Detection Result

```python
@dataclass
class PatternResult:
    """Represents detected patterns in viewing history."""
    pattern_type: str
    confidence: float
    description: str
    timeframe: Tuple[datetime, datetime]
    affected_videos: List[VideoEntry]
    evidence: Dict[str, Any]
```

## Utility Functions

### Data Validation

```python
def validate_watch_history_data(data: Dict) -> bool:
    """
    Validate the structure and content of parsed watch history data.

    Args:
        data (Dict): Parsed watch history data

    Returns:
        bool: True if data is valid

    Raises:
        ValidationError: If data structure is invalid
    """
    pass
```

### Date Utilities

```python
def parse_youtube_timestamp(timestamp_str: str) -> datetime:
    """Parse YouTube timestamp string to datetime object."""
    pass

def calculate_viewing_duration(entries: List[VideoEntry]) -> timedelta:
    """Calculate total viewing duration from entries."""
    pass

def group_by_time_period(entries: List[VideoEntry], period: str) -> Dict[str, List[VideoEntry]]:
    """Group entries by time period (hour, day, week, month)."""
    pass
```

### Analysis Helpers

```python
def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
    """Extract keywords from video titles."""
    pass

def calculate_similarity_matrix(entries: List[VideoEntry]) -> np.ndarray:
    """Calculate content similarity matrix."""
    pass

def detect_outliers(data: np.ndarray, method: str = 'isolation_forest') -> List[int]:
    """Detect outlier entries in the data."""
    pass
```

## Integration Examples

### Basic Analysis Pipeline

```python
from rabbitmirror import (
    HistoryParser, ClusterEngine, AdversarialProfiler,
    SuppressionAnalyzer, TrendAnalyzer, ExportFormatter
)

# Initialize components
parser = HistoryParser()
cluster_engine = ClusterEngine()
profiler = AdversarialProfiler()
suppression_analyzer = SuppressionAnalyzer()
trend_analyzer = TrendAnalyzer()
exporter = ExportFormatter()

# Parse data
data = parser.parse('watch-history.html')

# Perform analysis
clusters = cluster_engine.cluster_videos(data['entries'])
patterns = profiler.detect_patterns(data['entries'])
suppression = suppression_analyzer.analyze_suppression(data['entries'])
trends = trend_analyzer.analyze_temporal_patterns(data['entries'])

# Export results
results = {
    'parsed_data': data,
    'clusters': clusters,
    'patterns': patterns,
    'suppression': suppression,
    'trends': trends
}

exporter.export_json(results, 'comprehensive_analysis')
exporter.export_excel(results, 'analysis_report')
```

### Custom Analysis Extension

```python
class CustomAnalyzer:
    """Example custom analyzer implementation."""

    def __init__(self, parameters):
        self.parameters = parameters

    def analyze(self, data):
        """Perform custom analysis."""
        # Custom analysis logic
        return analysis_results

    def visualize(self, results):
        """Create custom visualizations."""
        # Visualization logic
        return charts

# Register custom analyzer
from rabbitmirror.registry import register_analyzer
register_analyzer('custom', CustomAnalyzer)
```

## Performance Considerations

### Memory Management

- Use streaming parsers for large files (>100MB)
- Process data in chunks when memory is limited
- Enable compression for large exports
- Use generator functions for large dataset iteration

### Optimization Tips

1. **Clustering**: Adjust `eps` and `min_samples` parameters for optimal performance
2. **Feature Extraction**: Limit vocabulary size for text features
3. **Parallel Processing**: Use multiprocessing for CPU-intensive operations
4. **Caching**: Cache intermediate results for repeated operations

### Monitoring and Logging

```python
import logging
from rabbitmirror.logging import setup_logging

# Configure logging
setup_logging(
    level=logging.INFO,
    file='logs/api.log',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
```

## Version Compatibility

- **Python**: 3.8+
- **NumPy**: 1.19+
- **Pandas**: 1.2+
- **scikit-learn**: 0.24+
- **Flask**: 2.0+ (for web interface)

## See Also

- [Getting Started Guide](tutorials/01_getting_started.md)
- [Advanced Usage](tutorials/02_advanced_usage.md)
- [Configuration Reference](configuration.md)
- [Examples and Recipes](examples_and_recipes.md)
