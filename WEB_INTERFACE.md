# Frequently Asked Questions (FAQ) & Support

## General Questions

**What is RabbitMirror?**
RabbitMirror is a comprehensive analysis tool for YouTube watch history, offering both command-line and web interfaces to help users understand their viewing patterns and detect algorithmic behaviors.

**What formats does RabbitMirror support?**
- **HTML**: Google Takeout format
- **JSON**: Pre-processed data

## Installation & Setup

**How do I install RabbitMirror?**
- Clone the repository.
- Create a virtual environment: `python -m venv venv`
- Activate and install dependencies: `source venv/bin/activate; pip install -r requirements.txt`

## Usage

**How do I parse my YouTube history?**
Run the following command:
```bash
python run.py process parse your-watch-history.html --output parsed_data.json
```

**Can I export data to different formats?**
Yes, RabbitMirror supports JSON, CSV, YAML, and Excel.

## Troubleshooting

**What if RabbitMirror crashes during processing?**
- Check log files for errors.
- Restart the application after fixing any identified issues.

## Getting Help

- **GitHub Issues**: Report bugs or request features.
- **Discussions**: Join the community discussions.
- **Wiki**: Access the [Wiki](https://github.com/romulusaugustus/RabbitMirror/wiki) for more detailed documentation.

# 🌐 RabbitMirror Web Interface

## Overview

RabbitMirror now includes a modern, user-friendly web interface that makes analyzing YouTube watch history accessible to everyone. No command-line experience required!

## Features

### 🎯 **Key Features**
- **Drag & Drop Upload**: Easy file upload interface
- **Real-time Analysis**: Instant processing and results
- **Interactive Dashboards**: Visual charts and graphs
- **Comprehensive Analysis**: All CLI features in a web interface
- **Export Results**: Download analysis in multiple formats
- **Responsive Design**: Works on desktop and mobile

### 📊 **Analysis Capabilities**
- **Trend Analysis**: Track viewing patterns over time
- **Content Clustering**: Group similar videos and discover themes
- **Suppression Analysis**: Detect content suppression patterns
- **🚨 Adversarial Pattern Detection**: Identify algorithmic manipulation
- **Risk Assessment**: Overall risk scoring and alerts
- **Raw Data Viewer**: Inspect original data

## Getting Started

### 🚀 **Starting the Web Interface**

```bash
# Method 1: Using lets CLI
lets web

# Method 2: Using lets dev command
lets dev

# Method 3: Direct Python command
source venv/bin/activate
cd rabbitmirror/web
python app.py
```

The web interface will be available at:
- **Local**: http://127.0.0.1:5001
- **Network**: http://192.168.x.x:5001

### 📁 **Supported File Formats**

- **HTML**: Google Takeout watch history files
- **JSON**: Pre-processed watch history data
- **Maximum File Size**: 100MB

### 🔧 **How to Use**

1. **Upload Your File**
   - Click "Choose File" or drag and drop
   - Select your YouTube watch history file
   - Click "Upload and Analyze"

2. **View Results**
   - Navigate through different analysis tabs
   - View interactive charts and visualizations
   - Export results in various formats

3. **Explore Analysis**
   - **Trend Analysis**: Time-based patterns
   - **Clusters**: Content groupings
   - **Suppression**: Content suppression detection
   - **🚨 Adversarial Patterns**: Algorithmic manipulation detection
   - **Raw Data**: Original data inspection

## Analysis Results

### 📈 **Trend Analysis**
- Monthly viewing patterns
- Content consumption trends
- Temporal behavior analysis
- Statistical metrics and insights

### 🎯 **Content Clustering**
- Similar video groupings
- Theme identification
- Category distribution
- Cluster size and characteristics

### 🔍 **Suppression Analysis**
- Content suppression metrics
- Baseline comparison
- Category-specific analysis
- Suppression confidence scores

### 🚨 **Adversarial Pattern Detection**
- **Risk Score**: Overall manipulation risk (0-1 scale)
- **Rapid Viewing**: Unusually fast video consumption
- **Binge Patterns**: Extended viewing sessions
- **Anomalous Sessions**: Suspicious viewing behavior
- **Language Switches**: Unexpected language changes
- **Topic Shifts**: Unusual content transitions

#### Risk Score Interpretation
- **Low (0.0-0.2)**: Normal viewing patterns
- **Medium (0.2-0.5)**: Some unusual patterns detected
- **High (0.5-1.0)**: Significant manipulation indicators

## Export Options

### 📊 **Available Formats**
- **JSON**: Complete analysis data
- **CSV**: Spreadsheet-friendly format
- **YAML**: Human-readable configuration format

### 💾 **Export Features**
- Timestamped filenames
- Complete analysis results
- Structured data for further analysis
- Compatible with external tools

## Technical Details

### 🔧 **Architecture**
- **Backend**: Flask Python web framework
- **Frontend**: Bootstrap 5 + Chart.js
- **Processing**: RabbitMirror analysis engine
- **Storage**: Temporary file handling
- **Security**: Local processing only

### 📱 **Browser Compatibility**
- Chrome/Chromium (recommended)
- Firefox
- Safari
- Edge
- Mobile browsers

### 🛡️ **Security Features**
- Local processing only
- No data transmission to external servers
- Temporary file cleanup
- Secure file handling
- Input validation

## Development

### 🔨 **Development Commands**

```bash
# Start development server
lets dev

# Start web interface only
lets web

# Run tests
lets test

# Clean temporary files
lets clean
```

### 🎨 **Customization**
- **Templates**: `rabbitmirror/web/templates/`
- **Static Files**: `rabbitmirror/web/static/`
- **Styles**: `rabbitmirror/web/static/css/style.css`
- **Configuration**: `rabbitmirror/web/app.py`

## Troubleshooting

### 🐛 **Common Issues**

#### Port Already in Use
```bash
# Kill process on port 5001
lsof -ti:5001 | xargs kill -9
```

#### File Upload Errors
- Check file size (max 100MB)
- Ensure file format is HTML or JSON
- Verify file is not corrupted

#### Analysis Errors
- Check that virtual environment is activated
- Ensure all dependencies are installed
- Verify file format matches expected structure

### 📝 **Debug Mode**
The web interface runs in debug mode by default for development. This provides:
- Detailed error messages
- Automatic reloading on file changes
- Interactive debugger

## Future Enhancements

### 🚀 **Planned Features**
- Real-time analysis progress bars
- Interactive pattern visualization
- Advanced filtering and search
- User session management
- Batch file processing
- API endpoints for external integration

### 🎯 **Roadmap**
- Enhanced mobile experience
- Dark/light theme toggle
- Advanced export options
- Integration with external tools
- Performance optimizations

## Contributing

### 🤝 **How to Contribute**
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### 📋 **Areas for Contribution**
- UI/UX improvements
- New visualization options
- Performance optimizations
- Additional export formats
- Mobile responsiveness
- Accessibility features

## Support

### 📧 **Getting Help**
- Check the main README.md
- Review TESTING_RESULTS.md
- Submit GitHub issues
- Join discussions

### 🔗 **Resources**
- [Main Documentation](README.md)
- [Testing Results](TESTING_RESULTS.md)
- [GitHub Repository](https://github.com/DanteX86/RabbitMirror)

---

**🌟 The RabbitMirror web interface makes YouTube watch history analysis accessible to everyone!**
