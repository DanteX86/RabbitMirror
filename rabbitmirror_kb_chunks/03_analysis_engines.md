# Analysis Engines

Advanced analytics and machine learning components that form the core of RabbitMirror's analysis capabilities.

## Cluster Engine

**Module:** `rabbitmirror/cluster_engine.py`
**Algorithm:** DBSCAN with TF-IDF vectorization

### Core Algorithm Stack
- **TF-IDF Vectorization**: Convert video titles to feature vectors
- **DBSCAN Clustering**: Density-based clustering algorithm
- **Cosine Similarity**: Distance metric for text similarity

### Key Parameters
- `eps=0.3`: Neighborhood distance threshold
- `min_samples=5`: Minimum samples per cluster
- `vectorizer`: TF-IDF with cosine similarity metrics

### 🔴 Critical Performance Issues

#### Memory Inefficiency
**Problem**: Unnecessary dense matrix conversion causing 10-100x memory increase
```python
# Current inefficient code
labels = self.clustering.fit_predict(tfidf_matrix.toarray())  # ❌

# Optimized version
labels = self.clustering.fit_predict(tfidf_matrix)  # ✅
```

**Impact**: Memory usage bloat from sparse to dense matrix conversion

#### Algorithm Effectiveness
- **Issue**: 80% of clustering scenarios produce zero clusters
- **Root Cause**: Parameter tuning and algorithm configuration
- **Priority**: HIGH - Core functionality degradation

### Output Structure
```json
{
  "clusters": {
    "cluster_0": [...],
    "cluster_1": [...],
    "noise": [...]
  },
  "cluster_info": {
    "total_clusters": int,
    "noise_points": int,
    "cluster_sizes": {...}
  },
  "metadata": {
    "eps": float,
    "min_samples": int,
    "vectorizer_vocabulary_size": int
  }
}
```

### Error Recovery
- `@robust_operation`: Retry mechanism with exponential backoff
- `@monitor_errors`: Error tracking and context preservation
- Comprehensive parameter validation

## Adversarial Profiler

**Module:** `rabbitmirror/adversarial_profiler.py`
**Purpose:** Advanced behavioral profiling and psychological pattern analysis

### Pattern Analysis Categories

#### 1. Psychological Patterns
- **Mood Indicators**: Positive, negative, neutral content detection
- **Cognitive Style**: Analytical, creative, practical preferences
- **Emotional Triggers**: Curiosity, urgency, controversy detection

#### 2. Motivational Patterns
- **Aspiration Indicators**: Goal-oriented content preferences
- **FOMO Detection**: Fear of missing out behavioral patterns
- **Reward-Seeking**: Achievement and gratification patterns

#### 3. Attention Patterns
- **Focused vs Divided Attention**: Concentration pattern analysis
- **Sustained Attention**: Long-form vs short-form preferences
- **Context Switching**: Multi-topic engagement analysis

#### 4. Social Dynamics
- **Collaboration Preferences**: Team vs individual content
- **Support-Seeking**: Help and guidance content patterns
- **Influence Patterns**: Authority and peer influence detection

#### 5. Viewing Habits Analysis
- **Peak Activity**: Time-based viewing pattern analysis
- **Session Recognition**: Binge vs distributed viewing
- **Break Patterns**: Rest and pause behavior analysis

### Advanced Features

#### Confidence Scoring System
- **Temporal Decay**: Confidence decreases over time
- **Multi-dimensional Modeling**: Complex behavioral interactions
- **Statistical Significance**: P-value testing for patterns
- **Contextual Weighting**: Situation-aware pattern evaluation

#### Configuration Parameters
**26 Configurable Thresholds** including:
- Similarity threshold: 0.7 (cosine similarity)
- Session gap threshold: 30 minutes
- Chain detection threshold: 4+ videos
- Confidence decay rates
- Pattern weighting factors

## Trend Analyzer

**Module:** `rabbitmirror/trend_analyzer.py`
**Purpose:** Temporal trend analysis with statistical significance testing

### Analysis Periods
- **Daily**: Day-by-day trend analysis
- **Weekly**: Monday-to-Sunday aggregation patterns
- **Monthly**: Calendar month-based trend detection

### Analyzed Metrics

#### Core Metrics
- `video_count`: Number of videos watched per period
- `total_duration`: Total watch time accumulation
- `avg_duration`: Average video length preferences
- `unique_channels`: Channel diversity measurement
- `categories_diversity`: Content category distribution
- `viewing_velocity`: Videos consumed per hour of content

#### Statistical Methods
- **Trend Direction Detection**: Increasing/decreasing/stable classification
- **Trend Strength Calculation**: 0.0-1.0 intensity scale
- **Statistical Significance Testing**: P-value validation
- **Change Point Detection**: Behavioral shift identification
- **Seasonal Pattern Recognition**: Cyclical behavior analysis

### Output Structure
```json
{
  "period_type": "daily|weekly|monthly",
  "timeframes": [...],
  "metrics": {
    "metric_name": {
      "values": [...],
      "trend_direction": "increasing|decreasing|stable",
      "trend_strength": float,
      "statistical_significance": float
    }
  },
  "significant_changes": [...],
  "summary": {...}
}
```

## Suppression Index

**Module:** `rabbitmirror/suppression_index.py`
**Purpose:** Content suppression and algorithmic bias detection

### Analysis Types
- **Content Suppression**: Artificially reduced content visibility detection
- **Recommendation Bias**: Algorithmic recommendation pattern analysis
- **Manipulation Detection**: Non-organic viewing pattern identification

### Detection Methods

#### Baseline Period Comparison
- Historical viewing pattern establishment
- Deviation from expected behavior analysis
- Statistical significance of changes

#### Expected vs Actual Distribution Analysis
- Content category distribution modeling
- Anomaly detection in recommendation patterns
- Bias quantification metrics

#### Category-Specific Suppression Scoring
- Per-category suppression index calculation
- Cross-category bias comparison
- Temporal consistency evaluation

#### Temporal Pattern Anomaly Detection
- Time-series analysis of content access
- Sudden change detection algorithms
- Pattern disruption identification

### Metrics Output
- **Suppression Scores**: 0.0-1.0 scale indicators
- **Statistical Confidence Levels**: P-value significance
- **Category-Specific Bias Indicators**: Per-topic analysis
- **Temporal Consistency Measures**: Time-based stability

## Performance Analysis Summary

### Current Performance Issues

| Engine | Issue | Priority | Impact |
|--------|-------|----------|--------|
| Cluster Engine | TF-IDF memory bloat | CRITICAL | 10-100x memory increase |
| Cluster Engine | 80% zero clusters | HIGH | Core functionality failure |
| Parser Integration | 0% success rate | CRITICAL | Complete system failure |
| All Engines | 2.1GB memory baseline | HIGH | Scalability problems |

### Optimization Recommendations

#### Immediate (Week 1)
1. **Fix TF-IDF Dense Conversion**: Remove `.toarray()` call
2. **Debug Parser Failures**: Investigate 100% failure rate
3. **Memory Profiling**: Identify memory leak sources

#### High Priority (Week 2-3)
1. **Algorithm Parameter Tuning**: Fix clustering effectiveness
2. **Caching Implementation**: Parser and vectorizer result caching
3. **Memory Management**: Explicit object cleanup

#### Medium Priority (Month 1)
1. **Algorithm Optimization**: Reduce computational complexity
2. **Parallel Processing**: Multi-threaded analysis support
3. **Result Streaming**: Large dataset handling improvements

## Integration Patterns

### Error Recovery Integration
All analysis engines implement:
- `@robust_operation` decorators for retry logic
- `@monitor_errors` for comprehensive error tracking
- Structured error reporting with context preservation

### Database Integration
- Results stored in `YouTubeAnalysis` model
- Automatic expiration and cleanup policies
- Cache-friendly result structures

### CLI Integration
Each engine exposed through CLI command groups:
- `rabbitmirror analyze cluster`
- `rabbitmirror analyze detect-patterns`
- `rabbitmirror analyze trend-analysis`
- `rabbitmirror analyze analyze-suppression`

---

*Next: [User Interfaces](04_user_interfaces.md)*
