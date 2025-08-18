# RabbitMirror Module Summaries

**Generated:** 2024-12-28
**Project:** RabbitMirror v1.0.0
**Purpose:** Advanced YouTube Watch History Analysis Tool

## Table of Contents

- [Core Modules](#core-modules)
- [Analysis Engines](#analysis-engines)
- [Parser Framework](#parser-framework)
- [Database Layer](#database-layer)
- [User Interfaces](#user-interfaces)
- [Utility Modules](#utility-modules)
- [Testing Infrastructure](#testing-infrastructure)
- [Architecture Overview](#architecture-overview)

---

## Core Modules

### CLI Module (`rabbitmirror/cli.py`)

**Purpose:** Command-line interface entry point with Click-based commands

**Key Classes:**
- `AliasedGroup`: Custom Click group with command alias support

**Key Functions:**
- `main()`: Application entry point
- `parse()`: Parse history files from various platforms
- `cluster()`: Perform video clustering analysis
- `tui_command()`: Launch terminal user interface

**Dependencies:**
- `click`, `click_aliases`: Command-line interface framework
- `jsonschema`, `yaml`: Data validation and serialization
- All analysis engine modules

**Command Groups:**
- `process`: Data processing commands (parse, validate)
- `analyze`: Analysis commands (cluster, profile, trends)
- `report`: Report generation commands
- `utils`: Utility commands
- `config`: Configuration management

**Design Notes:**
- Uses decorator pattern for command organization
- Implements comprehensive error handling with symbolic logging
- Supports both interactive and batch processing modes

---

### Parser Module (`rabbitmirror/parser.py`)

**Purpose:** Main parsing controller that delegates to platform-specific parsers

**Key Classes:**
- `HistoryParser`: Main parser controller class

**Key Methods:**
- `parse()`: Parse file using appropriate platform parser
- `_parse_with_fallback()`: Handle multiple encoding attempts
- `_extract_entries()`: Extract individual entries from parsed content
- `_parse_entry()`: Parse single watch history entry
- `_convert_timestamp()`: Convert timestamps to ISO format

**Error Recovery:**
- Multiple encoding fallback (UTF-8, UTF-8-BOM, Latin-1, CP1252)
- Graceful handling of malformed entries
- Detailed error logging with context preservation

**Dependencies:**
- `BeautifulSoup4`: HTML parsing
- `parsers.factory`: Platform-specific parser creation
- Custom exception hierarchy

---

### Configuration Manager (`rabbitmirror/config_manager.py`)

**Purpose:** Configuration management with JSON-based storage

**Key Classes:**
- `ConfigManager`: Simple key-value configuration storage

**Key Methods:**
- `set(key, value)`: Store configuration value
- `get(key)`: Retrieve configuration value
- `list()`: List all configuration items

**Features:**
- Local vs global configuration support
- JSON-based persistent storage
- Automatic directory creation
- Corruption-resistant file handling

**Storage Location:**
- Local: `./rabbitmirror_config.json`
- Global: `~/.rabbitmirror_config.json`

---

### Exception Hierarchy (`rabbitmirror/exceptions.py`)

**Purpose:** Comprehensive custom exception hierarchy for structured error handling

**Base Exception:**
```python
class RabbitMirrorError(Exception):
    - message: str
    - error_code: str
    - details: Dict[str, Any]
    - to_dict(): Convert to serializable format
```

**Exception Inheritance Tree:**
```
RabbitMirrorError
├── DataProcessingError
│   ├── ParsingError
│   │   └── InvalidFormatError
│   ├── DataValidationError
│   └── SchemaValidationError
├── FileOperationError
├── ConfigurationError
├── AnalysisError
│   ├── ClusteringError
│   ├── PatternDetectionError
│   └── TrendAnalysisError
├── SimulationError
├── ExportError
├── NetworkError
├── ResourceError
└── DependencyError
```

**Features:**
- Context preservation through error chain
- Machine-readable error codes
- Structured error details
- JSON serialization support

---

## Analysis Engines

### Cluster Engine (`rabbitmirror/cluster_engine.py`)

**Purpose:** Video clustering using DBSCAN and TF-IDF vectorization

**Key Classes:**
- `ClusterEngine`: Main clustering implementation

**Algorithm Stack:**
- **TF-IDF Vectorization**: Convert video titles to feature vectors
- **DBSCAN Clustering**: Density-based clustering algorithm
- **Cosine Similarity**: Distance metric for text similarity

**Key Methods:**
- `cluster_videos(entries)`: Main clustering method with error recovery
- Parameter validation and sanitization
- Comprehensive result statistics

**Output Structure:**
```python
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

**Decorators:**
- `@robust_operation`: Retry mechanism with exponential backoff
- `@monitor_errors`: Error tracking and context preservation

---

### Adversarial Profiler (`rabbitmirror/adversarial_profiler.py`)

**Purpose:** Advanced behavioral profiling and psychological pattern analysis

**Key Classes:**
- `AdversarialProfiler`: Sophisticated behavioral analysis engine

**Pattern Analysis Categories:**

1. **Psychological Patterns**
   - Content mood indicators (positive, negative, neutral)
   - Cognitive style patterns (analytical, creative, practical)
   - Emotional trigger detection (curiosity, urgency, controversy)

2. **Motivational Patterns**
   - Aspiration indicators
   - Fear of missing out (FOMO) detection
   - Reward-seeking behavior

3. **Attention Patterns**
   - Focused vs divided attention analysis
   - Sustained attention measurement
   - Context switching behavior

4. **Social Dynamics**
   - Collaboration vs competition preferences
   - Support-seeking behavior
   - Social influence patterns

5. **Viewing Habits Analysis**
   - Peak activity analysis
   - Session pattern recognition
   - Binge behavior detection
   - Break pattern analysis

**Advanced Features:**
- Confidence scoring system with temporal decay
- Multi-dimensional behavioral modeling
- Statistical significance testing
- Contextual pattern weighting

**Thresholds and Configuration:**
- 20+ configurable analysis parameters
- Similarity threshold: 0.7 (cosine similarity)
- Session gap threshold: 30 minutes
- Chain detection threshold: 4+ videos

---

### Trend Analyzer (`rabbitmirror/trend_analyzer.py`)

**Purpose:** Temporal trend analysis with statistical significance testing

**Key Classes:**
- `TrendAnalyzer`: Main trend analysis engine
- `TrendMetric`: Individual metric representation
- `SignificantChange`: Change detection result

**Supported Analysis Periods:**
- Daily: Day-by-day analysis
- Weekly: Monday-to-Sunday aggregation
- Monthly: Calendar month aggregation

**Analyzed Metrics:**
- `video_count`: Number of videos watched
- `total_duration`: Total watch time
- `avg_duration`: Average video length
- `unique_channels`: Channel diversity
- `categories_diversity`: Content category spread
- `viewing_velocity`: Videos per hour of content

**Statistical Methods:**
- Trend direction detection (increasing/decreasing/stable)
- Trend strength calculation (0.0-1.0 scale)
- Statistical significance testing
- Change point detection
- Seasonal pattern recognition

**Output Structure:**
```python
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

---

### Suppression Index (`rabbitmirror/suppression_index.py`)

**Purpose:** Content suppression detection and algorithmic bias analysis

**Key Classes:**
- `SuppressionIndex`: Algorithmic bias detection engine

**Analysis Types:**
- **Content Suppression**: Detection of artificially reduced content visibility
- **Recommendation Bias**: Analysis of algorithmic recommendation patterns
- **Algorithmic Manipulation**: Identification of non-organic viewing patterns

**Detection Methods:**
- Baseline period comparison
- Expected vs actual distribution analysis
- Category-specific suppression scoring
- Temporal pattern anomaly detection

**Metrics:**
- Suppression scores (0.0-1.0 scale)
- Statistical confidence levels
- Category-specific bias indicators
- Temporal consistency measures

---

## Parser Framework

### Base Architecture (`rabbitmirror/parsers/`)

**Design Pattern:** Factory Pattern with Plugin Support

**Purpose:** Extensible multi-platform parser framework supporting YouTube, Netflix, Spotify, and custom parsers

### Base Parser (`rabbitmirror/parsers/base_parser.py`)

**Key Classes:**

1. **`ParserConfig`** (dataclass):
   ```python
   - file_path: Union[str, Path]
   - encoding: Optional[str] = None
   - fallback_encodings: List[str] = ["utf-8", "utf-8-sig", "latin-1", "cp1252"]
   - max_retries: int = 3
   - retry_delay: float = 0.5
   - skip_invalid_entries: bool = True
   - normalize_timestamps: bool = True
   - platform_options: Dict[str, Any] = {}
   ```

2. **`ParserResult`** (dataclass):
   ```python
   - entries: List[Dict[str, Any]]
   - platform: str
   - total_entries: int
   - successful_entries: int
   - failed_entries: int
   - processing_time: float
   - success_rate: property
   ```

3. **`BaseParser`** (Abstract Base Class):
   - Abstract methods: `validate_format()`, `_extract_entries()`, `_parse_entry()`
   - Built-in retry mechanisms with exponential backoff
   - Error recovery and logging
   - Encoding fallback handling

**Decorators:**
- `@with_retry`: Automatic retry with configurable policies
- `@monitor_errors`: Error tracking and context preservation

### Parser Factory (`rabbitmirror/parsers/factory.py`)

**Key Classes:**
- `ParserFactory`: Factory for platform-specific parser creation

**Supported Platforms:**
- `youtube`: YouTube HTML export files
- `netflix`: Netflix viewing history
- `spotify`: Spotify streaming history

**Methods:**
- `get_parser(platform, config)`: Create parser instance
- `get_supported_platforms()`: List available platforms
- `register_parser(platform, parser_class)`: Plugin registration

**Extensibility:**
Custom parsers can be registered at runtime:
```python
ParserFactory.register_parser("custom_platform", CustomParser)
```

### YouTube Parser (`rabbitmirror/parsers/youtube_parser.py`)

**Key Classes:**
- `YouTubeParser`: Specialized parser for YouTube HTML exports

**Supported Formats:** `.html`, `.htm`

**Parsing Process:**
1. Format validation with YouTube-specific markers
2. BeautifulSoup HTML parsing with lxml backend
3. Entry extraction using CSS selectors (`div.content-cell`)
4. Individual entry parsing with error recovery

**Key Methods:**
- `_extract_video_id()`: Extract YouTube video ID from URL
- `_extract_channel_name()`: Extract channel information
- `_convert_youtube_timestamp()`: Convert YouTube timestamp formats

**Fallback Strategies:**
- Multiple CSS selector attempts
- Alternative timestamp format support
- Missing data graceful handling
- Encoding detection and fallback

---

## Database Layer

**Framework:** SQLAlchemy ORM
**Purpose:** Persistent storage for single-user analysis results

### Models (`rabbitmirror/database/models.py`)

**Base Components:**
- `Base`: SQLAlchemy declarative base
- `TimestampMixin`: Automatic created_at/updated_at fields

**Core Models:**

1. **`YouTubeAnalysis`**:
   ```sql
   Table: youtube_analyses
   - id: UUID (Primary Key)
   - filename: String(255), indexed
   - file_hash: String(64), indexed (SHA-256)
   - analysis_type: String(50), indexed
   - status: String(20), indexed (pending/completed/failed)
   - results: JSON
   - summary: JSON
   - processing_time: Integer (milliseconds)
   - expires_at: DateTime, indexed
   ```

2. **`CacheEntry`**:
   ```sql
   Table: cache_entries
   - id: UUID (Primary Key)
   - cache_key: String(255), indexed
   - namespace: String(100), indexed
   - data: LargeBinary (Pickled data)
   - data_type: String(50) (json/pickle/text)
   - ttl: Integer (seconds)
   - expires_at: DateTime, indexed
   - hit_count: Integer
   - last_accessed: DateTime
   ```

3. **`DataRetentionPolicy`**:
   ```sql
   Table: data_retention_policies
   - id: UUID (Primary Key)
   - name: String(100), unique
   - target_table: String(100), indexed
   - retention_days: Integer
   - is_active: Boolean
   - last_run: DateTime
   - next_run: DateTime, indexed
   ```

**Features:**
- Automatic timestamp management
- Data expiration support
- Cache hit tracking
- Retention policy automation
- UUID-based primary keys

### Session Management (`rabbitmirror/database/session.py`)

**Key Functions:**
- `init_database()`: Database initialization and schema creation
- `get_db_session()`: Session factory for database operations

**Configuration:**
- SQLite database for single-user mode
- Connection pooling and management
- Transaction handling
- Migration support

---

## User Interfaces

### Web Interface (`rabbitmirror/web/app.py`)

**Framework:** Flask with comprehensive security features

**Security Features:**
- Rate limiting with IP-based throttling
- Input validation and sanitization
- Secure file upload handling
- CSRF protection
- Security headers (CSP, HSTS, etc.)
- Simple authentication for single-user mode

**Key Routes:**
- `GET/POST /`: File upload interface
- `GET /analyze/<filename>`: Analysis results display
- `GET/POST /simple_login`: Authentication
- `GET /logout`: Session termination

**Security Components:**
- `input_validator`: Path and filename validation
- `rate_limiter`: Request throttling
- `security_auditor`: Security event logging
- `secret_manager`: Secure key management

**File Handling:**
- Maximum file size limits
- Extension filtering
- Secure filename handling
- Temporary storage management

### Terminal User Interface (`rabbitmirror/tui.py`)

**Framework:** Textual (Modern Python TUI framework)

**Key Components:**

1. **`FileSelector`** (Modal Screen):
   - Interactive file browser
   - Directory navigation
   - File filtering by extension
   - Path validation

2. **Main Application Components**:
   - `DataTable`: Results display
   - `ProgressBar`: Analysis progress
   - `TabbedContent`: Multiple analysis views
   - `Log`: Real-time logging

**Features:**
- Modern terminal interface with rich text support
- Interactive file browser with tree navigation
- Real-time progress updates
- Keyboard shortcuts and bindings
- Theme support (dark/light modes)

**Navigation:**
- Vim-like keybindings
- Mouse support
- Modal dialogs for file selection
- Context-sensitive help

---

## Utility Modules

### Export Formatter (`rabbitmirror/export_formatter.py`)

**Purpose:** Multi-format data export with robust error handling

**Supported Formats:**
- JSON: Human-readable with proper indentation
- YAML: Configuration-friendly format
- CSV: Tabular data export with pandas
- Excel: Multi-sheet workbook support

**Key Features:**
- Automatic format detection from file extensions
- Robust error handling with retries
- Memory-efficient processing
- Data validation before export

**Methods:**
- `load_data()`: Load data from multiple formats
- `export_data()`: Export to specified format
- Format-specific exporters with timeout protection

**Decorators:**
- `@robust_operation`: Retry mechanism
- `@with_timeout`: Operation timeouts
- `@monitor_errors`: Error tracking

### Schema Validator (`rabbitmirror/schema_validator.py`)

**Purpose:** JSON Schema validation for data structure integrity

**Supported Schemas:**
1. **Watch History**: Video entries with metadata validation
2. **Cluster Analysis**: Clustering results structure validation
3. **Suppression Analysis**: Bias detection results validation
4. **Pattern Analysis**: Behavioral pattern results validation

**Validation Features:**
- JSONSchema Draft-07 compliance
- Detailed error reporting
- Type checking and constraints
- Required field validation
- Custom format validators

**Schema Structure Example:**
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "YouTube Watch History Schema",
  "type": "object",
  "properties": {
    "entries": {
      "type": "array",
      "items": {
        "required": ["timestamp", "title"],
        "properties": {
          "timestamp": {"type": "string"},
          "title": {"type": "string", "minLength": 1}
        }
      }
    }
  }
}
```

### Symbolic Logger (`rabbitmirror/symbolic_logger.py`)

**Purpose:** Structured logging with Loguru framework

**Features:**
- JSON-formatted log entries
- Automatic log rotation (daily)
- Log retention (1 month)
- Structured event logging
- Error context preservation

**Log Types:**
- `log_event()`: Application events with structured data
- `log_error()`: Error logging with exception context

**Configuration:**
- Log directory: `logs/`
- Rotation: Daily
- Retention: 1 month
- Format: JSON with timestamps

### Dashboard Generator (`rabbitmirror/dashboard_generator.py`)

**Purpose:** Interactive dashboard generation with Plotly

**Features:**
- Multi-theme support (light/dark)
- Interactive Plotly charts
- Jinja2 templating
- Responsive design
- Export capabilities

**Supported Chart Types:**
- Time series analysis
- Bar charts for categories
- Scatter plots for correlations
- Heatmaps for patterns
- Distribution histograms

**Dashboard Types:**
- History analysis dashboard
- Cluster analysis visualization
- Suppression analysis charts
- Pattern detection displays

**Themes:**
```python
# Dark Theme Colors
{
    "background": "#2E2E2E",
    "paper": "#3E3E3E",
    "text": "#FFFFFF",
    "primary": "#3498DB"
}

# Light Theme Colors
{
    "background": "#FFFFFF",
    "paper": "#F8F9FA",
    "text": "#333333",
    "primary": "#2980B9"
}
```

### Error Recovery (`rabbitmirror/error_recovery.py`)

**Purpose:** Advanced error handling with retry mechanisms and circuit breakers

**Key Classes:**

1. **`RetryConfig`**:
   ```python
   - max_attempts: int = 3
   - base_delay: float = 1.0
   - max_delay: float = 60.0
   - exponential_base: float = 2.0
   - jitter: bool = True
   - retryable_exceptions: List[Type[Exception]]
   ```

2. **`CircuitBreaker`**:
   - Failure threshold configuration
   - Recovery timeout management
   - State management (CLOSED/OPEN/HALF_OPEN)
   - Success/failure tracking

3. **`ErrorRecoveryManager`**:
   - Recovery strategy registration
   - Circuit breaker management
   - Context-aware error handling

**Decorators:**
- `@with_retry`: Configurable retry behavior
- `@robust_operation`: Combined retry + timeout + monitoring
- `@monitor_errors`: Error tracking and logging

**Retry Strategies:**
- Exponential backoff with jitter
- Selective exception handling
- Context preservation through retries
- Maximum delay limiting

---

## Testing Infrastructure

### Framework: pytest with comprehensive fixtures

**Test Organization:**

1. **Unit Tests** (`tests/`):
   - `test_parser.py`: Parser functionality testing
   - `test_cluster_engine.py`: Clustering algorithm testing
   - `test_config_manager.py`: Configuration management testing
   - `test_adversarial_profiler.py`: Behavioral analysis testing
   - `test_trend_analyzer.py`: Trend analysis testing

2. **Integration Tests** (`tests/integration/`):
   - `test_cli_integration.py`: Command-line interface testing
   - `test_database_integration.py`: Database operation testing
   - `test_web_endpoints.py`: Web interface testing
   - `test_component_integration.py`: Cross-module integration

3. **Performance Tests** (`benchmarks/`):
   - `test_clustering_performance.py`: Clustering performance benchmarks
   - `test_parser_performance.py`: Parsing performance benchmarks

### Test Fixtures (`tests/conftest.py`)

**Key Fixtures:**
- `sample_history_file`: Path to test HTML file
- `sample_parser`: Pre-configured parser instance
- `sample_entries`: Parsed test data
- `mock_history_data`: Programmatic test data
- `temp_output_dir`: Temporary directory for test outputs
- `sample_history_dir`: Directory with multiple test files

**Fixture Design:**
- Reusable across test modules
- Automatic cleanup
- Realistic test data
- Error scenario coverage

### Test Data Structure

**Sample Test Entry:**
```python
{
    "title": "Python Machine Learning Tutorial",
    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "timestamp": "2023-12-15T14:30:45-08:00"
}
```

**Coverage Areas:**
- Happy path scenarios
- Error conditions and edge cases
- Invalid input handling
- Performance under load
- Integration between modules

---

## Architecture Overview

### Design Patterns Implementation

1. **Factory Pattern**:
   - `ParserFactory`: Platform-specific parser creation
   - Enables plugin architecture for new platforms

2. **Decorator Pattern**:
   - Error recovery decorators (`@with_retry`, `@robust_operation`)
   - Monitoring decorators (`@monitor_errors`)
   - Enables aspect-oriented programming

3. **Strategy Pattern**:
   - Multiple analysis engines with common interface
   - Export format strategies
   - Enables algorithm switching at runtime

4. **Observer Pattern**:
   - Event logging system
   - Progress tracking
   - Enables loose coupling for notifications

5. **Template Method Pattern**:
   - `BaseParser` abstract methods
   - Defines algorithm structure with customizable steps

### Module Dependencies

**Dependency Flow:**
```
CLI Layer
├── Analysis Engines (cluster, adversarial, trend, suppression)
├── Parser Framework (factory → platform parsers)
├── Utility Modules (export, validation, logging)
└── Database Layer (models, session management)

User Interfaces (Web/TUI)
├── All Analysis Engines
├── Security Components
└── Database Layer
```

**External Dependencies:**
- **Data Science**: pandas, numpy, scikit-learn
- **Web**: Flask, Jinja2
- **Parsing**: BeautifulSoup4, lxml
- **CLI**: Click, Click-aliases
- **Visualization**: Plotly
- **Database**: SQLAlchemy, SQLAlchemy-utils
- **Logging**: Loguru
- **Validation**: JSONSchema
- **UI**: Textual, Rich
- **Serialization**: PyYAML

### Extensibility Points

1. **Parser Plugins**:
   ```python
   ParserFactory.register_parser("new_platform", CustomParser)
   ```

2. **Analysis Engines**: New modules can be added to CLI command groups

3. **Export Formats**: `ExportFormatter` extensible with new format handlers

4. **Dashboard Themes**: `DashboardGenerator` supports custom themes

5. **Error Recovery**: Custom strategies via `ErrorRecoveryManager`

### Performance Optimizations

1. **Caching**:
   - Database-backed result caching
   - In-memory computation caching

2. **Lazy Loading**:
   - Large file processing
   - Progressive parsing

3. **Batch Processing**:
   - Bulk analysis operations
   - Streaming data processing

4. **Memory Management**:
   - Generator-based parsing
   - Chunked file reading

5. **Parallel Processing**:
   - Multi-threading for I/O operations
   - Async operations where applicable

### Security Considerations

1. **Input Validation**:
   - Filename sanitization
   - Path traversal protection
   - Schema validation

2. **Rate Limiting**:
   - Per-IP request limits
   - Exponential backoff

3. **File Handling**:
   - Secure uploads with size limits
   - Extension filtering
   - Temporary file management

4. **Authentication**:
   - Simple password authentication
   - Session management
   - Secure secret handling

5. **Error Handling**:
   - Secure error messages
   - Comprehensive audit logging
   - Context preservation without information leakage

This architecture provides a robust, extensible, and secure foundation for advanced YouTube watch history analysis with multiple interfaces and comprehensive error handling.
