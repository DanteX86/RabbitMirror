# RabbitMirror Algorithm Details

## Overview

This document provides detailed technical documentation of all analysis algorithms implemented in RabbitMirror. Each algorithm is documented with its mathematical foundations, parameter tuning guidelines, and implementation details.

## Table of Contents

- [Pattern Detection Algorithms](#pattern-detection-algorithms)
- [Content Clustering Methods](#content-clustering-methods)
- [Suppression Analysis Logic](#suppression-analysis-logic)
- [Profile Simulation Approaches](#profile-simulation-approaches)
- [Temporal Analysis Techniques](#temporal-analysis-techniques)
- [Algorithm Parameters Reference](#algorithm-parameters-reference)
- [Performance Considerations](#performance-considerations)

---

## Pattern Detection Algorithms

### 1. Rapid Views Detection Algorithm

**Module**: `adversarial_profiler.py`
**Method**: `_detect_rapid_views()`

#### Algorithm Description
Identifies unusually rapid viewing patterns that may indicate automated behavior or algorithmic manipulation.

#### Mathematical Foundation
```
interval = (current_timestamp - previous_timestamp) / 60  # Convert to minutes
is_rapid = interval < rapid_view_threshold
confidence = calculate_confidence(interval)
```

#### Parameters
- **`rapid_view_threshold`**: Maximum interval in minutes (default: 5)
- **Confidence calculation**: Based on interval deviation from normal viewing patterns

#### Implementation Details
1. Iterates through sorted watch history entries
2. Calculates time intervals between consecutive videos
3. Identifies intervals below the threshold
4. Assigns confidence scores based on deviation severity

#### Tuning Guidelines
- **Lower threshold (1-3 minutes)**: More sensitive, may catch human rapid browsing
- **Higher threshold (10-15 minutes)**: Less sensitive, focuses on extreme automation
- **Recommended**: 5 minutes for balanced detection

---

### 2. Content Loops Detection Algorithm

**Module**: `adversarial_profiler.py`
**Method**: `_detect_content_loops()`

#### Algorithm Description
Detects repeated viewing patterns of similar content using TF-IDF vectorization and cosine similarity analysis.

#### Mathematical Foundation
```
TF-IDF Matrix: X = vectorizer.fit_transform(titles)
Cosine Similarity: S = cosine_similarity(X)
Loop Detection: For each video i, find videos j where S[i,j] > similarity_threshold
Loop Formation: count(similar_videos) >= repetition_threshold
```

#### Parameters
- **`similarity_threshold`**: Minimum cosine similarity (default: 0.7, range: 0.0-1.0)
- **`repetition_threshold`**: Minimum similar videos for loop pattern (default: 3)

#### Implementation Details
1. **Text Preprocessing**: TF-IDF vectorization with English stop words removal
2. **Similarity Calculation**: Pairwise cosine similarity matrix computation
3. **Loop Identification**: Find videos with multiple high-similarity matches
4. **Pattern Analysis**: Calculate temporal distribution of similar content

#### Algorithmic Complexity
- **Time**: O(n²) for similarity matrix calculation
- **Space**: O(n²) for similarity storage + O(v) for vocabulary
- **Optimization**: Can be reduced to O(n log n) with approximate methods

---

### 3. Binge Pattern Detection Algorithm

**Module**: `adversarial_profiler.py`
**Method**: `_detect_binge_patterns()`

#### Algorithm Description
Identifies automated binge-watching patterns by analyzing viewing session regularity and interval consistency.

#### Mathematical Foundation
```
Session Split: gap > session_gap_threshold → new session
Interval Analysis: intervals = [t[i+1] - t[i] for each video in session]
Regularity Score: 1.0 - (std(intervals) / mean(intervals))
Suspicious Pattern: std(intervals) < 1.0 AND len(session) > 10
```

#### Parameters
- **`session_gap`**: Gap threshold for session boundaries (default: 30 minutes)
- **`minimum_session_length`**: Minimum videos per session for analysis (default: 10)
- **`regularity_threshold`**: Maximum standard deviation for suspicious patterns (default: 1.0)

#### Implementation Details
1. **Session Splitting**: Group videos based on temporal gaps
2. **Interval Calculation**: Compute inter-video intervals within sessions
3. **Statistical Analysis**: Calculate mean, standard deviation of intervals
4. **Pattern Classification**: Identify unnaturally regular patterns

---

### 4. Anomalous Session Detection Algorithm

**Module**: `adversarial_profiler.py`
**Method**: `_detect_anomalous_sessions()`

#### Algorithm Description
Detects viewing sessions with anomalous patterns suggesting non-human behavior.

#### Detection Criteria
```python
anomalous_session = (
    session_metrics["std_interval"] < 1.0 AND        # Very regular intervals
    session_metrics["video_count"] > 10 AND          # Long session
    session_metrics["mean_interval"] < 5.0           # Very short intervals
)
```

#### Statistical Measures
- **Standard Deviation Threshold**: < 1.0 minute
- **Video Count Threshold**: > 10 videos
- **Mean Interval Threshold**: < 5.0 minutes

---

### 5. Psychological Pattern Analysis

**Module**: `adversarial_profiler.py`
**Method**: `_analyze_psychological_patterns()`

#### Algorithm Description
Analyzes psychological patterns in content consumption to detect manipulation attempts.

#### Pattern Categories

##### Mood Indicators
```python
mood_patterns = {
    "positive": ["uplifting", "happy", "funny", "inspiration"],
    "negative": ["drama", "conflict", "controversy", "criticism"],
    "neutral": ["educational", "informative", "documentary"]
}
```

##### Cognitive Patterns
```python
cognitive_patterns = {
    "analytical": ["analysis", "review", "explanation", "tutorial"],
    "creative": ["art", "design", "music", "creation"],
    "practical": ["how-to", "guide", "tips", "solution"]
}
```

##### Emotional Triggers
```python
emotional_triggers = {
    "curiosity": ["mystery", "secret", "revealed", "hidden"],
    "urgency": ["breaking", "urgent", "latest", "now"],
    "controversy": ["vs", "debate", "fight", "drama"]
}
```

#### Analysis Process
1. **Content Classification**: Categorize videos by psychological indicators
2. **Transition Analysis**: Track mood and cognitive pattern transitions
3. **Trigger Detection**: Identify emotional manipulation attempts
4. **Polarization Scoring**: Measure content bias and polarization

---

## Content Clustering Methods

### DBSCAN Clustering Algorithm

**Module**: `cluster_engine.py`
**Class**: `ClusterEngine`

#### Algorithm Description
Groups similar videos using Density-Based Spatial Clustering of Applications with Noise (DBSCAN).

#### Mathematical Foundation
```
Core Point: |N(p)| >= min_samples
Border Point: |N(p)| < min_samples but in neighborhood of core point
Noise Point: Neither core nor border point
Cluster Formation: Connected components of core and border points
```

#### Parameters
- **`eps`**: Maximum distance between samples (default: 0.3)
- **`min_samples`**: Minimum samples for dense region (default: 5)

#### Implementation Pipeline
1. **Text Vectorization**: TF-IDF transformation of video titles
2. **Feature Matrix**: Create numerical representation of content
3. **Distance Calculation**: Euclidean distance in TF-IDF space
4. **Cluster Formation**: Apply DBSCAN algorithm
5. **Result Processing**: Group videos by cluster labels

#### Advantages
- **No cluster count assumption**: Automatically determines cluster count
- **Noise handling**: Identifies outlier videos as noise
- **Arbitrary shapes**: Can find non-spherical clusters

#### Parameter Tuning Guidelines
- **Low eps (0.1-0.2)**: Smaller, more specific clusters
- **High eps (0.5-0.8)**: Larger, more general clusters
- **Low min_samples (2-3)**: More clusters, sensitive to small groups
- **High min_samples (10+)**: Fewer clusters, requires strong patterns

---

## Suppression Analysis Logic

### Baseline Comparison Algorithm

**Module**: `suppression_index.py`
**Method**: `calculate_suppression()`

#### Algorithm Description
Detects content suppression by comparing recommendation frequencies between baseline and analysis periods.

#### Mathematical Foundation
```
Baseline Period: First baseline_period_days of data
Analysis Period: Remaining data after baseline period
Overall Suppression: 1.0 - (analysis_views / baseline_views)
Category Suppression: 1.0 - (analysis_freq[category] / baseline_freq[category])
```

#### Metrics Calculated
1. **Overall Suppression Index**: Global recommendation reduction
2. **Category-Specific Suppression**: Per-category analysis
3. **View Velocity**: Videos per unit time comparison
4. **Channel Diversity**: Unique channel count analysis

#### Implementation Steps
1. **Data Splitting**: Divide history into baseline and analysis periods
2. **Metric Calculation**: Compute frequency metrics for each period
3. **Suppression Index**: Calculate relative frequency changes
4. **Temporal Analysis**: Track suppression patterns over time

#### Suppression Index Interpretation
- **0.0**: No suppression detected
- **0.1-0.3**: Mild suppression
- **0.3-0.6**: Moderate suppression
- **0.6-1.0**: Severe suppression

---

### Temporal Pattern Analysis

**Module**: `suppression_index.py`
**Method**: `_analyze_temporal_patterns()`

#### Algorithm Description
Analyzes how content suppression varies over different time periods.

#### Analysis Dimensions
- **Hourly Patterns**: Time-of-day suppression variations
- **Daily Patterns**: Day-of-week suppression patterns
- **Seasonal Patterns**: Long-term suppression trends
- **Event Correlation**: Suppression around specific events

---

## Profile Simulation Approaches

### Statistical Pattern Extraction

**Module**: `profile_simulator.py`
**Class**: `ProfileSimulator`

#### Algorithm Description
Extracts statistical patterns from existing profiles to generate synthetic viewing histories.

#### Pattern Extraction Methods

##### Time Distribution Analysis
```python
def _analyze_time_distribution(profile):
    hours = [datetime.fromisoformat(entry["timestamp"]).hour for entry in profile]
    hist, _ = np.histogram(hours, bins=24, range=(0, 24))
    return hist / hist.sum()  # Normalize to probabilities
```

##### Content Distribution Analysis
```python
def _analyze_content_distribution(profile):
    categories = classify_content(profile)  # Rule-based classification
    total = len(profile)
    return {category: count/total for category, count in categories.items()}
```

##### Interval Distribution Analysis
```python
def _analyze_interval_distribution(profile):
    intervals = []
    for i in range(1, len(profile)):
        interval = (current_time - previous_time).total_seconds() / 60
        if interval < 24 * 60:  # Filter out day-long gaps
            intervals.append(interval)
    hist, _ = np.histogram(intervals, bins=50)
    return hist / hist.sum()
```

#### Simulation Generation Process
1. **Pattern Learning**: Extract statistical distributions from base profile
2. **Timeline Generation**: Create temporal framework for simulation
3. **Content Generation**: Sample content types based on learned distributions
4. **Temporal Placement**: Place videos according to time patterns
5. **Title Generation**: Create realistic titles using pattern templates

#### Title Pattern Templates
```python
title_patterns = {
    "CREATOR - CONTENT": "Creator{id} - Content{id}",
    "SERIES_WITH_EPISODE": "Series{id} EP.{episode}",
    "TITLE_WITH_PARENTHESES": "Title{id} (Detail{id})",
    "TITLE_WITH_BRACKETS": "Title{id} [Info{id}]",
    "SIMPLE_TITLE": "Simple Title {id}"
}
```

---

## Temporal Analysis Techniques

### Trend Detection Algorithm

**Module**: `trend_analyzer.py`
**Class**: `TrendAnalyzer`

#### Algorithm Description
Analyzes temporal trends using statistical methods including linear regression and correlation analysis.

#### Mathematical Foundation
```
Linear Regression: y = mx + b
Slope Calculation: m = Σ((x - x̄)(y - ȳ)) / Σ((x - x̄)²)
Correlation: r = Σ((x - x̄)(y - ȳ)) / √(Σ(x - x̄)² × Σ(y - ȳ)²)
Trend Strength: |r|
Trend Direction: sign(m)
```

#### Metrics Analyzed
- **Video Count**: Number of videos watched per period
- **Total Duration**: Total watch time per period
- **Average Duration**: Mean video length per period
- **Unique Channels**: Channel diversity per period
- **Categories Diversity**: Content category variety
- **Viewing Velocity**: Videos per hour of content
- **Session Count**: Number of viewing sessions

#### Time Periods Supported
- **Daily**: Day-by-day analysis
- **Weekly**: Week-by-week analysis (Monday-based weeks)
- **Monthly**: Month-by-month analysis

#### Trend Classification
```python
def classify_trend(slope, std_threshold):
    if abs(slope) < std_threshold:
        return "stable"
    elif slope > 0:
        return "increasing"
    else:
        return "decreasing"
```

### Significant Change Detection

**Module**: `trend_analyzer.py`
**Method**: `_detect_significant_changes()`

#### Algorithm Description
Identifies sudden, significant changes in viewing patterns using percentage change thresholds.

#### Change Detection Logic
```python
def detect_significant_change(current_value, previous_value, threshold=50.0):
    if previous_value != 0:
        change_percentage = ((current_value - previous_value) / previous_value) * 100
        return abs(change_percentage) > threshold
    return False
```

#### Significance Thresholds
- **Major Change**: > 50% change between consecutive periods
- **Statistical Significance**: Correlation-based significance scoring
- **Minimum Data Points**: Requires at least 2 data points for analysis

---

## Algorithm Parameters Reference

### Global Configuration Parameters

#### Clustering Parameters
```yaml
clustering:
  algorithm: "DBSCAN"           # Algorithm type
  eps: 0.3                     # Distance threshold
  min_samples: 5               # Minimum cluster size
  max_features: 1000           # TF-IDF feature limit
  feature_weights:
    title_similarity: 0.7      # Title weight
    temporal_proximity: 0.3    # Time weight
```

#### Pattern Detection Parameters
```yaml
pattern_detection:
  enabled: true                # Enable/disable detection
  sensitivity: 0.7             # Detection sensitivity (0.0-1.0)
  min_confidence: 0.6          # Minimum confidence threshold
  rapid_view_threshold: 5      # Minutes for rapid viewing
  similarity_threshold: 0.7    # Content similarity threshold
  repetition_threshold: 3      # Loop formation threshold
  session_gap: 30             # Session boundary (minutes)
```

#### Suppression Analysis Parameters
```yaml
suppression_analysis:
  baseline_period: 30          # Baseline period (days)
  detection_threshold: 0.5     # Suppression detection threshold
  categories: []               # Specific categories to analyze
```

#### Trend Analysis Parameters
```yaml
trend_analysis:
  enabled: true                # Enable/disable analysis
  window_size: 7              # Analysis window (days)
  smoothing_factor: 0.3       # Trend smoothing
  seasonal_analysis: true     # Enable seasonal patterns
  change_threshold: 50.0      # Significant change threshold (%)
```

#### Performance Parameters
```yaml
performance:
  max_workers: 4              # Parallel processing workers
  max_memory_usage: "1GB"     # Memory limit
  parallel_processing: true    # Enable parallelization
  cache_enabled: true         # Enable result caching
  cache_size: "100MB"         # Cache memory limit
```

---

## Performance Considerations

### Computational Complexity

#### Algorithm Complexity Analysis
- **TF-IDF Vectorization**: O(n × m) where n=documents, m=vocabulary
- **DBSCAN Clustering**: O(n²) in worst case, O(n log n) with optimizations
- **Similarity Matrix**: O(n²) space and time complexity
- **Pattern Detection**: O(n) for most algorithms, O(n²) for similarity-based

#### Memory Usage Patterns
- **Small datasets (<1,000 videos)**: < 100MB memory usage
- **Medium datasets (1,000-10,000 videos)**: 100MB - 1GB memory usage
- **Large datasets (>10,000 videos)**: > 1GB memory usage

### Optimization Strategies

#### Memory Optimization
1. **Streaming Processing**: Process data in chunks for large datasets
2. **Sparse Matrices**: Use sparse matrix representations for TF-IDF
3. **Result Caching**: Cache intermediate calculations
4. **Garbage Collection**: Explicit memory cleanup in Python

#### Performance Optimization
1. **Parallel Processing**: Use multiprocessing for independent calculations
2. **Vectorized Operations**: Leverage NumPy/scikit-learn optimizations
3. **Algorithm Selection**: Choose appropriate algorithms based on data size
4. **Parameter Tuning**: Optimize parameters for specific use cases

#### Scalability Guidelines
- **< 1,000 videos**: All algorithms run efficiently with default parameters
- **1,000-10,000 videos**: Consider increasing eps parameter, enable caching
- **> 10,000 videos**: Use streaming processing, reduce feature dimensions
- **> 100,000 videos**: Consider approximate algorithms, distributed processing

---

## Future Algorithm Enhancements

### Planned Improvements
1. **Advanced Clustering**: Support for hierarchical and k-means clustering
2. **Deep Learning**: Neural network-based pattern recognition
3. **Anomaly Detection**: Isolation forests and one-class SVM
4. **Time Series Analysis**: ARIMA models for trend prediction
5. **Graph Analysis**: Network-based content relationship analysis

### Research Directions
1. **Federated Learning**: Privacy-preserving collaborative analysis
2. **Causal Inference**: Causal relationship detection in viewing patterns
3. **Multi-modal Analysis**: Integration with audio/visual content features
4. **Real-time Processing**: Streaming algorithm implementations

---

*Generated on 2025-01-27 for RabbitMirror v1.0.0*
