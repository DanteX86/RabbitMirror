# RabbitMirror TUI Structure and Navigation

## Overview

The RabbitMirror Terminal User Interface (TUI) is a modern, interactive interface built using the Textual framework. It provides an intuitive way to analyze YouTube watch history data through a tabbed interface with real-time feedback and comprehensive visualization capabilities.

## Launch and Initialization

### Starting the TUI
```bash
# Launch with default dark theme
rabbitmirror tui

# Launch with light theme
rabbitmirror tui --theme light

# Direct Python execution
python -m rabbitmirror.tui
```

### Dependencies
- **Textual**: Modern TUI framework
- **Rich**: Advanced terminal formatting
- **Click**: Command-line interface creation toolkit

If TUI dependencies are missing, the CLI will display installation instructions:
```bash
pip install textual rich
```

## Main Interface Structure

### Header and Footer
- **Header**: Displays application title and subtitle
  - Title: "🐰 RabbitMirror - YouTube Watch History Analyzer"
  - Subtitle: "Interactive Terminal Interface"
- **Footer**: Shows available key bindings and status information

### Key Bindings (Global)
| Key | Action | Description |
|-----|--------|-------------|
| `Q` | Quit | Exit the application |
| `H` | Help | Show help information |
| `R` | Refresh | Refresh current view |
| `Ctrl+C` | Quit | Alternative quit method |
| `Tab` | Navigate | Navigate between interface elements |

## Tab Structure and Navigation

The TUI is organized into five main tabs, each serving specific functionality:

### 1. Main Tab (`main`)
**Purpose**: Primary workflow and quick actions

#### Layout Structure
```
🎯 Welcome to RabbitMirror TUI
[Introduction Text]

📋 Step 1: Select Your YouTube Watch History File
[File selection instructions and controls]
[📁 Select File] [File Status Display]

📋 Step 2: Parse and Analyze Your Data
[Analysis instructions and quick action buttons]
[🔍 Quick Parse] [📊 Quick Analysis] [📈 View Results]

⏱️ Operation Status
[Status Display] [Progress Bar] [Elapsed Time]

💡 Tips and Navigation Help
```

#### Interactive Elements
- **File Selection Button**: Opens modal file browser
- **Quick Parse Button**: Parses selected file immediately
- **Quick Analysis Button**: Runs basic pattern detection and clustering
- **View Results Button**: Opens results viewer modal
- **Progress Bar**: Shows operation progress (0-100%)
- **Status Display**: Real-time operation updates
- **Elapsed Timer**: Live timing for current operations

#### File Selection Modal
The file selection modal provides:
- **Current Directory Display**: Shows active directory
- **File Browser Tree**: Hierarchical file/directory view
- **Filter Support**: Filters for .html files (YouTube Takeout format)
- **Navigation**: Directory traversal and file selection
- **Action Buttons**: Browse, Select, Cancel

### 2. Analysis Tab (`analysis`)
**Purpose**: Advanced analysis tools and configuration

#### Layout Structure
```
🔬 Advanced Analysis Tools
[Tool descriptions and capabilities]

🔍 Pattern Detection
[Pattern detection tools and options]
[🎯 Detect Patterns] [🔄 Cluster Videos]

📉 Content Analysis
[Content analysis tools]
[📉 Analyze Suppression] [📊 Trend Analysis]

📋 Advanced Tools
[Advanced analysis features]
[🎮 Simulate Profile] [📋 Generate Report]

⚙️ Analysis Options
[Configuration inputs for analysis parameters]
[Threshold Input] [Format Input]
```

#### Interactive Elements
- **Analysis Tool Buttons**: Each tool launches specific analysis
- **Configuration Inputs**:
  - Threshold slider/input (0.1-1.0)
  - Output format selection
- **Parameter Controls**: Tool-specific options

#### Analysis Tools Available
1. **Detect Patterns**: Adversarial pattern detection
2. **Cluster Videos**: Video clustering using DBSCAN
3. **Analyze Suppression**: Content suppression analysis
4. **Trend Analysis**: Temporal pattern analysis
5. **Simulate Profile**: Generate synthetic profiles
6. **Generate Report**: Create comprehensive reports

### 3. Results Tab (`results`)
**Purpose**: View and manage analysis results

#### Layout Structure
```
📊 Analysis Results
[Results table and visualization area]

📜 Activity Log
[Operation log and messages]
```

#### Interactive Elements
- **Results DataTable**:
  - Two-column format (Property | Value)
  - Dynamic content based on analysis
  - Sortable and filterable
- **Activity Log**:
  - Scrollable log widget
  - Real-time message updates
  - Color-coded message types

#### Data Display Format
Results are displayed in structured tables showing:
- **Parse Results**: Entry counts, file info, timing
- **Analysis Results**: Pattern counts, cluster info, metrics
- **Operation Status**: Success/failure indicators
- **Timestamps**: When operations completed

### 4. Settings Tab (`settings`)
**Purpose**: Configuration management and preferences

#### Layout Structure
```
⚙️ Configuration
[Configuration management interface]

📁 Output Settings
[Default output directory configuration]
[Directory Input Field]

📄 Export Settings
[Default format and export preferences]
[Format Selection Input]

🎯 Analysis Settings
[Default analysis parameters]
[Threshold Input Field]

[💾 Save Settings]
```

#### Configuration Options
| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| Output Directory | Path | Current directory | Default save location |
| Default Format | Choice | json | Default export format |
| Analysis Threshold | Float | 0.7 | Default sensitivity (0.1-1.0) |

#### Interactive Elements
- **Input Fields**: Text inputs for configuration values
- **Save Button**: Persists settings to config file
- **Validation**: Real-time input validation
- **Reset Options**: Restore default values

### 5. Modal Screens

#### File Selection Modal (`FileSelector`)
**Purpose**: Browse and select input files

##### Features
- **Directory Tree Navigation**: Hierarchical browsing
- **File Filtering**: Shows .html files prominently
- **Path Input**: Direct path entry
- **Real-time Updates**: Dynamic directory listings

##### Navigation Flow
```
[Current Directory Display]
├── File Tree Browser
│   ├── 📁 Directories (expandable)
│   ├── 📄 Target Files (.html)
│   └── 📄 Other Files (reference only)
├── [Browse] [Select] [Cancel]
└── Direct path input field
```

#### Results Viewer Modal (`ResultsViewer`)
**Purpose**: Display detailed analysis results

##### Features
- **Markdown Rendering**: Formatted result display
- **Scrollable Content**: Handle large result sets
- **Structured Layout**: Organized sections and headings
- **Data Formatting**: Automatic formatting of complex data

##### Content Structure
Results are formatted as Markdown with:
- **Headers**: Analysis type and summary
- **Sections**: Organized by data type
- **Lists**: Enumerated findings
- **Statistics**: Key metrics and counts
- **Timestamps**: Operation completion times

## Navigation Flow and User Journey

### Typical Workflow
1. **Launch TUI**: Start with Main tab active
2. **File Selection**: Click "Select File" → File browser modal
3. **File Parsing**: Click "Quick Parse" → Progress display
4. **Analysis**: Switch to Analysis tab → Run tools
5. **Results Review**: Switch to Results tab → View data
6. **Configuration**: Adjust settings in Settings tab
7. **Report Generation**: Create reports from Analysis tab

### Modal Interactions
- **File Selection Flow**:
  ```
  Main Tab → Select File → File Modal → Directory Navigation → File Selection → Return to Main
  ```
- **Results Viewing Flow**:
  ```
  Main/Analysis Tab → View Results → Results Modal → Content Review → Close → Return to Tab
  ```

### Error Handling in Navigation
- **File Not Found**: Modal displays error, stays open
- **Parse Errors**: Status display shows error, suggests fixes
- **Analysis Failures**: Log entries with error context
- **Configuration Errors**: Input validation with user feedback

## Real-Time Features

### Progress Tracking
- **Progress Bar**: Visual progress indicator (0-100%)
- **Status Messages**: Descriptive operation updates
- **Timer Display**: Live elapsed time counter
- **Operation Stages**: Multi-stage progress reporting

### Live Updates
- **File Status**: Updates when files are selected
- **Analysis Status**: Real-time analysis progress
- **Result Counts**: Live updating of result statistics
- **Configuration Changes**: Immediate validation feedback

### Notification System
- **Success Notifications**: Green checkmark with details
- **Error Notifications**: Red X with error context
- **Warning Notifications**: Yellow warning with suggestions
- **Info Notifications**: Blue info with helpful tips

## Data Flow and State Management

### Application State
The TUI maintains several key state variables:
- `current_file`: Selected input file path
- `current_data`: Parsed history data
- `analysis_results`: Stored analysis outputs
- `operation_start_time`: Timing for operations
- `config`: Configuration manager instance

### Data Persistence
- **Configuration**: Saved to `~/.rabbitmirror_config.json`
- **Temporary Data**: Held in memory during session
- **Analysis Results**: Optionally exported to files
- **Session State**: Not persisted between runs

### State Transitions
```
Application Start → File Selection → Data Parsing → Analysis → Results → Report Generation
        ↓               ↓              ↓           ↓         ↓            ↓
   Initialize UI → Load File → Parse Data → Run Tools → Display → Export/Save
```

## Styling and Theming

### CSS Structure
The TUI uses CSS for styling with the following organization:
- **Layout Containers**: Grid and flexbox layouts
- **Component Styling**: Individual widget appearances
- **Color Schemes**: Theme-based color management
- **Responsive Design**: Adapts to terminal size

### Theme Support
- **Dark Theme**: Default high-contrast dark theme
- **Light Theme**: Optional light theme variant
- **Color Coding**: Consistent color meanings across interface
- **Accessibility**: High contrast and clear visual hierarchy

### Visual Hierarchy
1. **Headers**: Large, prominent section titles
2. **Buttons**: Distinct interactive elements
3. **Status Info**: Highlighted operational feedback
4. **Data Display**: Clear, readable table/list formatting
5. **Help Text**: Subtle guidance and tips

## Error Handling and User Feedback

### Error Display Strategy
- **Contextual Errors**: Errors shown near relevant controls
- **Modal Errors**: Critical errors in modal dialogs
- **Status Bar Errors**: General errors in status display
- **Log Errors**: Detailed errors in activity log

### User Guidance
- **Tooltips**: Hover information (where supported)
- **Help Text**: Built-in guidance for complex features
- **Status Messages**: Clear operational feedback
- **Progress Indicators**: Visual progress communication

### Recovery Mechanisms
- **Graceful Failures**: Continue operation when possible
- **Retry Options**: Allow users to retry failed operations
- **Alternative Paths**: Provide alternate workflows
- **Safe Defaults**: Sensible fallback values

## Performance and Responsiveness

### Optimization Strategies
- **Lazy Loading**: Load data only when needed
- **Progressive Updates**: Update UI incrementally
- **Background Processing**: Non-blocking operations where possible
- **Memory Management**: Efficient data handling

### Scalability Considerations
- **Large Files**: Progress indicators for large file operations
- **Complex Analysis**: Chunked processing with updates
- **Result Display**: Pagination for large result sets
- **Resource Monitoring**: Memory and CPU awareness

### Response Time Targets
- **UI Updates**: < 100ms for interactive elements
- **File Operations**: Progress updates every 500ms
- **Analysis Tasks**: Status updates every 1-2 seconds
- **Navigation**: Instant tab switching

## Integration with CLI

### Shared Components
The TUI leverages the same core components as the CLI:
- **HistoryParser**: File parsing engine
- **Analysis Engines**: Pattern detection, clustering, etc.
- **Export Formatters**: Data export capabilities
- **Configuration Manager**: Settings persistence

### Command Equivalence
TUI operations map directly to CLI commands:
- **Quick Parse** → `rabbitmirror process parse`
- **Detect Patterns** → `rabbitmirror analyze detect-patterns`
- **Cluster Videos** → `rabbitmirror analyze cluster`
- **Generate Report** → `rabbitmirror report generate-report`

### Data Compatibility
- **Input Formats**: Same HTML parsing as CLI
- **Output Formats**: Compatible export formats
- **Configuration**: Shared config files
- **Results**: Equivalent analysis outputs

---

*This TUI structure provides an intuitive, powerful interface for YouTube watch history analysis while maintaining full compatibility with the command-line interface.*
