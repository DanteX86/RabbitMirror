# Quick Lookup Index

Fast reference for common queries and lookup patterns optimized for GPT interactions.

## By Functionality

### Parsing & Data Processing
- **Primary Modules**: `rabbitmirror/parser.py`, `rabbitmirror/parsers/`
- **Key Classes**: `HistoryParser`, `YouTubeParser`, `ParserFactory`
- **Use Cases**: HTML file parsing, Multi-platform support, Error recovery
- **Performance Issues**: Memory usage (2.1GB), Success rate (0%), Encoding detection
- **Quick Fix**: Debug parser failures - CRITICAL priority

### Video Clustering
- **Primary Module**: `rabbitmirror/cluster_engine.py`
- **Key Class**: `ClusterEngine`
- **Algorithms**: DBSCAN, TF-IDF, Cosine similarity
- **Critical Fix**: Remove dense matrix conversion (`tfidf_matrix.toarray()`)
- **Parameters**: `eps=0.3`, `min_samples=5`

### Web Interface
- **Primary Module**: `rabbitmirror/web/app.py`
- **Framework**: Flask with comprehensive security
- **Security Features**: Rate limiting, Input validation, CSRF protection
- **Performance Issue**: Synchronous processing (10-60 second blocks)
- **Solution**: Implement async processing with progress tracking

### Authentication
- **Modules**: `rabbitmirror/auth.py`, `rabbitmirror/security.py`
- **Status**: Framework exists but NOT integrated
- **Missing**: User registration, Login endpoints, Session management
- **Priority**: CRITICAL - no access control currently

## By Performance Priority

### CRITICAL Issues (Fix Immediately)
1. **Parser Failures**: 100% failure rate in all scenarios
2. **Memory Bloat**: TF-IDF dense conversion (10-100x increase)
3. **Authentication Missing**: No user access control

### HIGH Priority (Week 2-3)
1. **Clustering Effectiveness**: 80% scenarios produce zero clusters
2. **Web Interface Blocking**: Synchronous operations freeze UI
3. **Memory Baseline**: 2.1GB usage for small operations

### MEDIUM Priority (Month 1)
1. **Configuration Caching**: Reduce file I/O overhead
2. **Dashboard Generation**: Memory accumulation in visualizations
3. **Monitoring Integration**: APM and health checks missing

## By Component Quick Access

### CLI Commands
- **Entry Point**: `rabbitmirror/cli.py`
- **Groups**: `process`, `analyze`, `report`, `utils`, `config`, `db`
- **Framework**: Click with aliases
- **Documentation**: `cli_reference.md`

### TUI Interface
- **Entry Point**: `rabbitmirror/tui.py`
- **Framework**: Textual (modern Python TUI)
- **Components**: FileSelector, DataTable, ProgressBar
- **Documentation**: `TUI_GUIDE.md`

### Database Layer
- **Framework**: SQLAlchemy + Alembic
- **Models**: YouTubeAnalysis, CacheEntry, DataRetentionPolicy
- **Features**: UUID keys, TTL support, Automatic cleanup

## By Analysis Type Quick Reference

### Clustering Analysis
- **Algorithm**: DBSCAN with TF-IDF
- **Module**: `rabbitmirror/cluster_engine.py`
- **Default Parameters**: `eps=0.3, min_samples=5`
- **Current Issue**: 80% scenarios produce zero clusters
- **CLI Command**: `rabbitmirror analyze cluster <file>`

### Pattern Detection
- **Module**: `rabbitmirror/adversarial_profiler.py`
- **Categories**: Psychological, Motivational, Attention, Social, Viewing habits
- **Parameters**: 26 configurable thresholds
- **CLI Command**: `rabbitmirror analyze detect-patterns <file>`

### Trend Analysis
- **Module**: `rabbitmirror/trend_analyzer.py`
- **Periods**: Daily, Weekly, Monthly
- **Metrics**: Video count, Duration, Channels, Categories
- **CLI Command**: `rabbitmirror analyze trend-analysis <file>`

### Suppression Detection
- **Module**: `rabbitmirror/suppression_index.py`
- **Methods**: Baseline comparison, Distribution analysis, Anomaly detection
- **CLI Command**: `rabbitmirror analyze analyze-suppression <file>`

## Security Quick Reference

### Currently Implemented ✅
- **Input Validation**: Comprehensive validation framework
- **Rate Limiting**: IP-based throttling (`@limiter.limit('60 per minute')`)
- **Audit Logging**: Security event tracking
- **File Upload Security**: Size limits and extension filtering

### Missing - Critical Gaps ❌
- **User Authentication**: No registration/login system
- **Session Management**: Basic session handling only
- **Authorization**: No role-based access control
- **Data Encryption**: Basic utilities not integrated

## Error Recovery Quick Reference

### Key Decorators
- `@with_retry`: Automatic retry with configurable policies
- `@robust_operation`: Combined retry + timeout + monitoring
- `@monitor_errors`: Error tracking and logging

### Configuration Classes
- **RetryConfig**: Exponential backoff policies
- **CircuitBreaker**: Failure threshold management
- **ErrorRecoveryManager**: Recovery strategy coordination

## Configuration Quick Reference

### File Locations
- **Local**: `./rabbitmirror_config.json`
- **Global**: `~/.rabbitmirror_config.json`

### Key Commands
```bash
rabbitmirror config set <key> <value>    # Set configuration
rabbitmirror config get <key>            # Get configuration
rabbitmirror config list                 # List all settings
```

### Environment Variables
- `DATABASE_URL`: Database connection
- `SECRET_KEY`: Flask secret (required for web)
- `FLASK_DEBUG`: Debug mode toggle

## Performance Optimization Quick Reference

### Memory Issues (Priority Order)
1. **cluster_engine.py**: Remove `.toarray()` - 10-100x reduction
2. **parser.py**: Debug 2.1GB usage for small files
3. **dashboard_generator.py**: Visualization object cleanup

### Speed Optimizations (Impact Order)
1. **Parser Caching**: 10-50x improvement possible
2. **Async Web Processing**: Eliminate UI blocking
3. **Configuration Cache**: 2-3x improvement

### Caching Opportunities
```python
# Proposed caching architecture
class CacheManager:
    parser_cache = LRUCache(maxsize=100)      # High impact
    vectorizer_cache = LRUCache(maxsize=10)   # Medium impact
    dashboard_cache = LRUCache(maxsize=50)    # Medium impact
    config_cache = LRUCache(maxsize=20)       # Low impact
```

## Testing Quick Reference

### Test Coverage
- **Overall**: 80%
- **Framework**: pytest with comprehensive fixtures
- **Benchmarks**: pytest-benchmark with performance tracking

### Current Benchmark Issues
- **Parser**: 100% failure rate (CRITICAL)
- **Clustering**: Only 20% effectiveness
- **Memory**: 2.1GB baseline across all operations

### Test Commands
```bash
pytest tests/                    # Run all tests
pytest benchmarks/              # Run performance benchmarks
pytest --cov=rabbitmirror       # Coverage report
```

## Development Quick Reference

### Key Dependencies
- **Data Science**: pandas, numpy, scikit-learn, scipy
- **Web**: Flask, Jinja2, SQLAlchemy
- **CLI**: Click, Rich, Textual
- **Security**: bcrypt, flask-jwt-extended
- **Parsing**: BeautifulSoup4, lxml

### Build Commands
```bash
pip install -e .                # Development install
python -m build                 # Build package
pre-commit run --all-files      # Code quality checks
```

---

*This index provides quick access to the most commonly queried information about RabbitMirror for efficient GPT interactions.*
