# 🐰 RabbitMirror TUI Quick Reference

## Getting Started
1. **Launch TUI**: `cd /Users/romulusaugustus/Documents/rabbitmirror && source venv/bin/activate && rabbitmirror tui`
2. **Basic Navigation**: Use Tab to move between elements, Enter to activate buttons
3. **Quit**: Press `Q` or `Ctrl+C` to exit

## Main Tab - Your Starting Point
- **Purpose**: Step-by-step guidance through the analysis process
- **Step 1**: Select your YouTube watch history file (download from Google Takeout)
- **Step 2**: Parse your data and run quick analysis
- **Quick Actions**:
  - 🔍 **Quick Parse**: Loads your watch history data
  - 📊 **Quick Analysis**: Runs pattern detection and clustering
  - 📈 **View Results**: Shows analysis results and statistics

## Analysis Tab - Advanced Tools
- **Purpose**: Detailed analysis tools for understanding YouTube's algorithmic influence

### Pattern Detection
- 🎯 **Detect Patterns**: Identifies algorithmic manipulation in recommendations
- 🔄 **Cluster Videos**: Groups similar videos to find patterns

### Content Analysis
- 📉 **Analyze Suppression**: Detects if certain content types are being suppressed
- 📊 **Trend Analysis**: Shows how viewing patterns change over time

### Advanced Tools
- 🎮 **Simulate Profile**: Creates synthetic viewing profiles for comparison
- 📋 **Generate Report**: Creates comprehensive HTML report with all findings

### Analysis Options
- **Threshold**: Sensitivity for pattern detection (0.1 = sensitive, 1.0 = strict)
- **Format**: Output format for exported data (json, csv, yaml, excel)

## Results Tab - View Your Data
- **Purpose**: Displays analysis results in table format
- **Data Table**: Shows key metrics and statistics
- **Activity Log**: Monitor operations and status messages

## Settings Tab - Configure Defaults
- **Purpose**: Set up default values and preferences

### Output Settings
- **Default Output Directory**: Where results and reports are saved

### Export Settings
- **Default Format**: Choose default export format (json, csv, yaml, excel)

### Analysis Settings
- **Analysis Threshold**: Default sensitivity for pattern detection

## Key Features
- **Real-time Notifications**: Status updates appear in the top-right corner
- **Modal Windows**: Detailed results shown in popup windows
- **Persistent Settings**: Your preferences are saved between sessions
- **Error Handling**: Clear error messages help troubleshoot issues

## Common Workflow
1. Launch TUI and go to Main tab
2. Click "📁 Select File" and choose your watch-history.html
3. Click "🔍 Quick Parse" to load your data
4. Click "📊 Quick Analysis" for a quick overview
5. Go to Analysis tab for detailed tools
6. View results in Results tab
7. Generate comprehensive report when done

## Troubleshooting
- **File not found**: Make sure your watch-history.html file exists
- **Parse errors**: Check that your file is a valid YouTube watch history export
- **Analysis failures**: Ensure you've parsed data first
- **No results**: Run analysis before trying to view results

## Tips
- Use the Settings tab to set up your preferred defaults
- Check the Activity Log for detailed operation information
- Export results in different formats for further analysis
- Generate HTML reports for sharing findings
