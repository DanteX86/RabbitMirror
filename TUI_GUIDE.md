# 🐰 RabbitMirror TUI Guide

## Terminal User Interface (TUI) Overview

RabbitMirror now features a modern, interactive Terminal User Interface (TUI) built with [Textual](https://textual.textualize.io/). The TUI provides a user-friendly alternative to command-line operations, offering a visual interface that runs entirely in your terminal.

## 🚀 Getting Started

### Launch the TUI

```bash
# Launch with default dark theme
rabbitmirror tui

# Launch with light theme
rabbitmirror tui --theme light
```

### System Requirements

- **Python 3.9+**: Required for RabbitMirror
- **Terminal**: Any modern terminal (supports 256 colors)
- **Dependencies**: `textual` and `rich` (auto-installed)

## 📱 Interface Overview

The TUI is organized into several tabs:

### 1. **Main Tab** 🎯
- **File Selection**: Browse and select your YouTube watch history file
- **Quick Actions**: Immediate parsing and analysis
- **Status Display**: Shows current file and operation status

### 2. **Analysis Tab** 🔬
- **Pattern Detection**: Find adversarial algorithmic patterns
- **Video Clustering**: Group similar videos
- **Suppression Analysis**: Detect content suppression
- **Profile Simulation**: Generate synthetic viewing profiles
- **Trend Analysis**: Analyze viewing trends over time
- **Report Generation**: Create comprehensive reports

### 3. **Results Tab** 📊
- **Data Table**: View analysis results in tabular format
- **Log Display**: Monitor operations and status messages
- **Result Storage**: Access previously run analyses

### 4. **Settings Tab** ⚙️
- **Configuration**: Set default directories and formats
- **Preferences**: Configure analysis parameters
- **Persistent Settings**: Save your preferences

## 🔧 Key Features

### Interactive File Selection
- **File Browser**: Navigate to your watch history file
- **Drag & Drop**: Easy file selection
- **Path Validation**: Automatic file existence checking

### Real-time Analysis
- **Progress Indicators**: Visual feedback during operations
- **Status Notifications**: Success/error messages
- **Live Updates**: Real-time results display

### Results Visualization
- **Modal Viewers**: Detailed result inspection
- **Markdown Display**: Rich text formatting
- **Export Options**: Multiple output formats

### Persistent Configuration
- **Settings Storage**: Remembers your preferences
- **Default Values**: Pre-configured for common use cases
- **Easy Modification**: Change settings anytime

## 🎮 Navigation & Controls

### Key Bindings
- **Q**: Quit application
- **H**: Show help
- **R**: Refresh current view
- **Ctrl+C**: Emergency quit
- **Tab**: Navigate between elements
- **Enter**: Activate buttons/select items
- **Escape**: Close modals/cancel operations

### Mouse Support
- **Click**: Select buttons and interact with elements
- **Scroll**: Navigate through long content
- **Drag**: Resize elements (where supported)

## 📋 Common Workflows

### 1. **First Time Setup**
```
1. Launch TUI: rabbitmirror tui
2. Go to Settings tab
3. Set default output directory
4. Configure analysis parameters
5. Save settings
```

### 2. **Quick Analysis**
```
1. Main tab → Select File
2. Browse to your watch-history.html
3. Click Quick Parse
4. Click Quick Analysis
5. View Results tab for output
```

### 3. **Detailed Analysis**
```
1. Load file (as above)
2. Go to Analysis tab
3. Choose specific analysis type
4. Configure parameters
5. Run analysis
6. View results in modal
```

### 4. **Generate Report**
```
1. Complete analysis (as above)
2. Analysis tab → Generate Report
3. Report saved as HTML file
4. Open in browser for viewing
```

## 🛠️ Advanced Features

### Modal Windows
- **File Selector**: Enhanced file browsing
- **Results Viewer**: Detailed analysis output
- **Help System**: Contextual assistance

### Analysis Options
- **Threshold Control**: Adjust sensitivity
- **Format Selection**: Choose output format
- **Parameter Tuning**: Fine-tune analysis

### Export Capabilities
- **Multiple Formats**: JSON, CSV, YAML, Excel
- **Rich Reports**: HTML dashboards
- **Batch Processing**: Multiple files (CLI only)

## 🎨 Themes & Customization

### Built-in Themes
- **Dark Theme**: Default, easy on eyes
- **Light Theme**: High contrast, print-friendly

### Color Scheme
- **Primary**: Blue accents
- **Success**: Green for completed operations
- **Warning**: Orange for cautions
- **Error**: Red for failures

### Responsive Design
- **Terminal Size**: Adapts to window dimensions
- **Content Scaling**: Adjusts for small screens
- **Mobile Friendly**: Works in minimal terminals

## 🔍 Troubleshooting

### Common Issues

#### TUI Won't Launch
```bash
# Check dependencies
pip install textual rich

# Verify installation
rabbitmirror tui --help

# Try alternative launch
python -m rabbitmirror.tui
```

#### Display Problems
```bash
# Check terminal compatibility
echo $TERM

# Try different terminal
# Use iTerm2, Terminal.app, or modern alternatives

# Force color mode
TERM=xterm-256color rabbitmirror tui
```

#### File Selection Issues
```bash
# Ensure file exists
ls -la your-watch-history.html

# Check permissions
chmod +r your-watch-history.html

# Use absolute path
/full/path/to/your-watch-history.html
```

#### Analysis Errors
```bash
# Check file format
file your-watch-history.html

# Verify file content
head -n 10 your-watch-history.html

# Try smaller sample
# Use subset of history data
```

### Performance Tips

#### Large Files
- Use Quick Parse for initial testing
- Run analyses on smaller datasets first
- Monitor system resources

#### Memory Management
- Close unused modal windows
- Clear results periodically
- Use batch processing for multiple files

## 📊 Comparison: TUI vs CLI

| Feature | TUI | CLI |
|---------|-----|-----|
| **Ease of Use** | ✅ Visual, intuitive | ❌ Requires memorization |
| **Batch Processing** | ❌ Limited | ✅ Full support |
| **Scripting** | ❌ Not scriptable | ✅ Fully scriptable |
| **Real-time Feedback** | ✅ Visual progress | ❌ Text only |
| **Configuration** | ✅ GUI settings | ❌ Command flags |
| **Learning Curve** | ✅ Gentle | ❌ Steep |
| **Automation** | ❌ Manual operation | ✅ Fully automated |

## 🔮 Future Enhancements

### Planned Features
- **File Tree View**: Enhanced navigation
- **Real-time Graphs**: Live visualization
- **Plugin System**: Extensible analysis
- **Multi-file Support**: Handle multiple histories
- **Cloud Integration**: Remote analysis
- **Export Scheduling**: Automated reports

### Community Contributions
- **Theme Creation**: Custom color schemes
- **Widget Development**: New UI components
- **Analysis Plugins**: Extended functionality
- **Documentation**: User guides and tutorials

## 📚 Additional Resources

### Documentation
- [Textual Documentation](https://textual.textualize.io/)
- [Rich Text Library](https://rich.readthedocs.io/)
- [Click CLI Framework](https://click.palletsprojects.com/)

### Support
- **GitHub Issues**: Report bugs and requests
- **Discussions**: Community support
- **Wiki**: Extended documentation

### Examples
- See `examples/` directory for sample files
- Check `tests/` for usage patterns
- Review `docs/` for detailed guides

---

## 🎯 Quick Reference

### Launch Commands
```bash
rabbitmirror tui                    # Default (dark theme)
rabbitmirror tui --theme light     # Light theme
rabbitmirror tui --help            # Show help
```

### Key Shortcuts
- **Q**: Quit
- **H**: Help
- **R**: Refresh
- **Tab**: Navigate
- **Enter**: Select
- **Escape**: Cancel

### Main Workflow
1. **Select File** → Browse to watch-history.html
2. **Parse Data** → Quick Parse button
3. **Analyze** → Choose analysis type
4. **View Results** → Results tab or modal
5. **Export** → Generate report

The TUI makes RabbitMirror more accessible while maintaining all the powerful analysis capabilities of the command-line interface. Perfect for users who prefer visual interfaces or are new to terminal applications!

---

*For CLI documentation, see [README.md](README.md)*  
*For development setup, see [CONTRIBUTING.md](CONTRIBUTING.md)*
