# RabbitMirror Codebase Summary for TUI Design Analysis

## Project Overview
RabbitMirror is a Python-based YouTube Watch History Analysis Tool that provides both Terminal User Interface (TUI) and Command Line Interface (CLI) capabilities. The project analyzes YouTube watch history to detect algorithmic patterns, content suppression, and viewing trends.

## Core Architecture

### Main Components
- **TUI Module**: `rabbitmirror/tui.py` - Modern Textual-based terminal interface
- **CLI Module**: `rabbitmirror/cli.py` - Click-based command-line interface
- **Core Analysis**: Pattern detection, clustering, suppression analysis
- **Export/Import**: Multiple format support (JSON, CSV, YAML, Excel)
- **Web Interface**: Flask-based web dashboard

### Key Technologies
- **TUI Framework**: Textual (modern terminal UI)
- **CLI Framework**: Click (command-line interface)
- **Data Processing**: Pandas, NumPy, SciPy
- **Machine Learning**: scikit-learn
- **Web Framework**: Flask
- **Visualization**: Plotly, Rich
- **Configuration**: JSON/YAML-based

## Terminal User Interface (TUI) Analysis

### Current TUI Structure (`rabbitmirror/tui.py`)

#### Main Application Class: `RabbitMirrorTUI`
- **Framework**: Built with Textual framework
- **Layout**: Tabbed interface with 4 main sections
- **Navigation**: Keyboard shortcuts (Q=quit, H=help, R=refresh)
- **Styling**: CSS-based styling with custom theme

#### Tab Organization:
1. **Main Tab**:
   - File selection workflow
   - Quick actions (Parse, Analysis, View Results)
   - Progress tracking with real-time updates
   - Operation status display

2. **Analysis Tab**:
   - Pattern detection tools
   - Content clustering
   - Suppression analysis
   - Profile simulation
   - Trend analysis
   - Report generation

3. **Results Tab**:
   - DataTable for results display
   - Activity log
   - Result storage and retrieval

4. **Settings Tab**:
   - Configuration management
   - Default values
   - Persistent settings

#### Key TUI Features:
- **Modal Windows**: File selector, results viewer, help system
- **Real-time Progress**: Progress bars, elapsed time tracking
- **Notifications**: Success/error messages with severity levels
- **File Browser**: Interactive directory navigation
- **Settings Persistence**: Configuration saved between sessions

### Current CLI Structure (`rabbitmirror/cli.py`)

#### Command Groups:
1. **process**: Data processing commands
   - `parse`: Parse YouTube watch history
   - `batch-process`: Process multiple files

2. **analyze**: Analysis commands
   - `cluster`: Video clustering
   - `detect-patterns`: Pattern detection
   - `analyze-suppression`: Content suppression analysis
   - `simulate`: Profile simulation
   - `trend-analysis`: Trend analysis

3. **report**: Report generation
   - `generate-report`: Create reports
   - `export-dashboard`: Interactive dashboards

4. **config**: Configuration management
   - `set`: Set configuration values
   - `get`: Get configuration values
   - `list`: List all configurations

5. **utils**: Utility commands
   - `validate`: File validation
   - `convert`: Format conversion
   - `generate-qr`: QR code generation

#### Special Commands:
- `tui`: Launch the TUI interface
- `completion`: Shell completion support

## User Interface Design Patterns

### TUI Design Strengths:
1. **Guided Workflow**: Step-by-step process in Main tab
2. **Progressive Disclosure**: Basic → Advanced features
3. **Visual Feedback**: Progress bars, notifications, status updates
4. **Contextual Help**: Built-in help system
5. **Persistent State**: Settings and results storage

### TUI Design Opportunities:
1. **File Management**: Currently basic file selection
2. **Data Visualization**: Limited visualization capabilities
3. **Batch Operations**: No batch processing in TUI
4. **Real-time Updates**: Could enhance with live data updates
5. **Keyboard Navigation**: Could improve keyboard shortcuts

### CLI Design Strengths:
1. **Comprehensive Commands**: Full feature coverage
2. **Scriptable**: Automation-friendly
3. **Flexible Output**: Multiple export formats
4. **Progress Tracking**: Built-in progress bars
5. **Error Handling**: Comprehensive error messages

## Core Analysis Modules

### Key Analysis Components:
1. **HistoryParser**: Parses YouTube watch history HTML
2. **AdversarialProfiler**: Detects algorithmic manipulation
3. **ClusterEngine**: Groups similar videos
4. **SuppressionIndex**: Analyzes content suppression
5. **TrendAnalyzer**: Temporal pattern analysis
6. **ProfileSimulator**: Generates synthetic profiles

### Data Flow:
1. **Input**: YouTube watch history HTML file
2. **Parsing**: Extract structured data
3. **Analysis**: Apply various algorithms
4. **Output**: Results in multiple formats
5. **Visualization**: Generate reports and dashboards

## Configuration System

### ConfigManager Features:
- **Local/Global**: Project and user-level settings
- **Format Support**: JSON, YAML configuration files
- **Validation**: Schema-based validation
- **Persistence**: Automatic settings storage

### Key Configuration Areas:
- **Output Directories**: Default paths for results
- **Analysis Parameters**: Thresholds, algorithms
- **Export Formats**: Default file formats
- **UI Preferences**: Theme, layout settings

## File Structure Overview

```
RabbitMirror/
├── rabbitmirror/              # Core package
│   ├── __init__.py
│   ├── cli.py                # CLI interface
│   ├── tui.py                # TUI interface
│   ├── parser.py             # HTML parsing
│   ├── cluster_engine.py     # Video clustering
│   ├── adversarial_profiler.py  # Pattern detection
│   ├── suppression_index.py  # Suppression analysis
│   ├── trend_analyzer.py     # Trend analysis
│   ├── profile_simulator.py  # Profile simulation
│   ├── config_manager.py     # Configuration
│   ├── export_formatter.py   # Data export
│   ├── dashboard_generator.py # Report generation
│   ├── symbolic_logger.py    # Logging
│   └── web/                  # Web interface
│       ├── app.py
│       └── static/
├── tests/                    # Test suite
├── docs/                     # Documentation
├── examples/                 # Sample data
├── benchmarks/               # Performance tests
├── data/                     # Input data
├── exports/                  # Output data
├── logs/                     # Application logs
├── reports/                  # Generated reports
├── setup.py                  # Package setup
├── pyproject.toml           # Modern Python config
├── requirements.txt         # Dependencies
└── README.md               # Main documentation
```

## Usage Patterns

### TUI Workflow:
1. Launch: `rabbitmirror tui`
2. Select file using file browser
3. Quick Parse → Quick Analysis → View Results
4. Advanced analysis in Analysis tab
5. Generate comprehensive report

### CLI Workflow:
1. Parse: `rabbitmirror process parse file.html`
2. Analyze: `rabbitmirror analyze cluster file.html`
3. Report: `rabbitmirror report generate-report data.json`

## Technical Considerations

### Dependencies:
- **Core**: Python 3.9+
- **TUI**: Textual, Rich
- **CLI**: Click, Click-aliases
- **Data**: Pandas, NumPy, SciPy
- **ML**: scikit-learn
- **Web**: Flask, Jinja2
- **Export**: openpyxl, PyYAML

### Performance:
- **Async Support**: TUI uses asyncio for responsiveness
- **Progress Tracking**: Real-time progress updates
- **Memory Management**: Efficient data handling
- **Error Recovery**: Comprehensive error handling

### Extensibility:
- **Plugin System**: Modular analysis components
- **Configuration**: Flexible settings system
- **Export Formats**: Multiple output options
- **Theming**: CSS-based TUI styling

## Design Philosophy

### User Experience:
- **Accessibility**: Multiple interface options (TUI/CLI)
- **Discoverability**: Clear navigation and help systems
- **Feedback**: Visual progress and status updates
- **Flexibility**: Configurable workflows

### Technical Design:
- **Modularity**: Separate concerns (UI, analysis, data)
- **Maintainability**: Clear code organization
- **Testing**: Comprehensive test coverage
- **Documentation**: Extensive user and developer docs

## Areas for TUI Enhancement

### Potential Improvements:
1. **Enhanced File Management**: Better file browsing, recent files
2. **Live Data Visualization**: Real-time charts and graphs
3. **Batch Processing**: TUI support for multiple files
4. **Advanced Settings**: More granular configuration options
5. **Plugin Interface**: Extensible analysis modules
6. **Export Preview**: Preview before export
7. **Comparison Tools**: Side-by-side analysis comparison
8. **Search and Filter**: Better data exploration tools

### User Interface Patterns to Consider:
1. **Dashboard Layout**: Overview with key metrics
2. **Wizard Interface**: Step-by-step guided workflows
3. **Split Panes**: Multiple data views simultaneously
4. **Context Menus**: Right-click functionality
5. **Keyboard Shortcuts**: More comprehensive hotkeys
6. **Drag and Drop**: File and data manipulation
7. **Status Bar**: Persistent status information
8. **Tool Palette**: Quick access to common tools

This comprehensive overview provides the foundation for understanding RabbitMirror's current architecture and identifying opportunities for terminal interface improvements.
