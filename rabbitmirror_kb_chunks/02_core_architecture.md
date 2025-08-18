# Core Architecture

This section covers the foundational system architecture and design patterns that make up RabbitMirror's core infrastructure.

## CLI Framework

**Module:** `rabbitmirror/cli.py`
**Framework:** Click with aliases support

### Command Structure

The CLI is organized into logical command groups:

- **process**: Data processing commands (`parse`, `batch-process`)
- **analyze**: Analysis commands (`cluster`, `detect-patterns`, `simulate`, `trend-analysis`)
- **report**: Report generation (`generate-report`, `export-dashboard`)
- **utils**: Utilities (`validate`, `convert`, `generate-qr`)
- **config**: Configuration management (`set`, `get`, `list`)
- **db**: Database operations (`init`, `migrate`, `cleanup`)

### Key Classes
- `AliasedGroup`: Custom Click group supporting command aliases

### Design Patterns
- **Decorator Pattern**: Command organization and error handling
- **Command Pattern**: Structured command execution

### Error Handling
Comprehensive error handling with symbolic logging and structured error reporting.

## Parser Framework

**Base Module:** `rabbitmirror/parsers/base_parser.py`
**Factory Module:** `rabbitmirror/parsers/factory.py`
**Architecture:** Factory pattern with plugin support

### Supported Platforms
- **YouTube**: HTML export file parsing
- **Netflix**: Viewing history parsing
- **Spotify**: Streaming history parsing

### Key Features

#### Multi-Encoding Support
- UTF-8, UTF-8-BOM, Latin-1, CP1252
- Sequential fallback with error recovery

#### Extensibility
```python
# Runtime parser registration
ParserFactory.register_parser("new_platform", CustomParser)
```

#### Configuration
- `ParserConfig` dataclass with retry policies
- Configurable timeouts and encoding preferences

### Performance Characteristics
- **Speed**: ~0.055 seconds per file
- **Memory Usage**: 2.1GB (⚠️ optimization needed)
- **Success Rate**: Currently 0% (🔴 critical issue identified)

## Database Layer

**Framework:** SQLAlchemy ORM with Alembic migrations

### Core Models

#### YouTubeAnalysis
Main analysis results storage with:
- UUID primary keys
- File hash indexing (SHA-256)
- Status tracking (pending/completed/failed)
- JSON results storage
- Processing time metrics
- Automatic expiration

#### CacheEntry
Advanced caching with:
- TTL (Time-To-Live) support
- Hit count tracking
- Namespace organization
- Multiple data types (JSON/Pickle/Text)
- Last accessed timestamps

#### DataRetentionPolicy
Automated data lifecycle management:
- Configurable retention periods
- Target table specification
- Automatic cleanup scheduling
- Active/inactive policy states

### Features
- **UUID Primary Keys**: Globally unique identifiers
- **Automatic Timestamps**: Created/updated tracking
- **Data Expiration**: TTL-based cleanup
- **Cache Hit Tracking**: Performance monitoring

### Configuration
- **Single-User Mode**: SQLite database
- **Production Mode**: PostgreSQL support
- **Connection Pooling**: Configurable pool sizes
- **Migration Support**: Alembic integration

## Configuration Management

**Module:** `rabbitmirror/config_manager.py`
**Architecture:** JSON-based with local/global support

### Storage Locations
- **Local**: `./rabbitmirror_config.json`
- **Global**: `~/.rabbitmirror_config.json`

### Key Methods
- `set(key, value)`: Store configuration value
- `get(key)`: Retrieve configuration value
- `list()`: List all configuration items

### Features
- Corruption-resistant file handling
- Automatic directory creation
- Backup and recovery mechanisms
- **Optimization Opportunity**: Configuration caching to reduce file I/O

## Design Patterns Summary

### Factory Pattern
- **Parser Framework**: Platform-specific parser creation
- **Enables**: Plugin architecture for new platforms

### Decorator Pattern
- **Error Recovery**: `@with_retry`, `@robust_operation`, `@monitor_errors`
- **CLI Commands**: Command decoration and organization
- **Enables**: Aspect-oriented programming

### Strategy Pattern
- **Analysis Engines**: Multiple algorithms with common interface
- **Export Formats**: Different output format strategies
- **Enables**: Runtime algorithm switching

### Template Method Pattern
- **BaseParser**: Abstract methods with defined structure
- **Enables**: Consistent parsing workflow with customization points

## Module Dependencies

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

## Performance Considerations

### Strengths
- Modular architecture enables independent optimization
- Factory pattern supports plugin extensibility
- Comprehensive error recovery mechanisms

### Areas for Improvement
- Parser memory usage optimization needed
- Configuration caching implementation
- Database connection pooling tuning

---

*Next: [Analysis Engines](03_analysis_engines.md)*
