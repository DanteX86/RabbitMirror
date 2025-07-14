# RabbitMirror FAQ

## General Questions

### What is RabbitMirror?
RabbitMirror is a comprehensive Python tool for analyzing YouTube watch history data. It provides powerful parsing, clustering, analysis, and visualization capabilities to help you understand your viewing patterns and behaviors.

### What makes RabbitMirror different from other tools?
- **Privacy-First**: All processing happens locally on your device
- **Comprehensive Analysis**: Multiple analysis types from basic clustering to advanced pattern detection
- **Robust Error Handling**: Advanced error recovery with circuit breakers and retry mechanisms
- **Extensible**: Modular design allows for easy extension and customization
- **Research-Ready**: Perfect for academic research and algorithmic auditing

### Is RabbitMirror free to use?
Yes, RabbitMirror is open source software released under the MIT License. You can use it freely for personal, academic, and commercial purposes.

## Installation & Setup

### What are the system requirements?
- Python 3.8 or higher
- pip package manager
- At least 1GB of free disk space
- Internet connection for downloading dependencies

### How do I install RabbitMirror?
```bash
# Clone the repository
git clone https://github.com/romulusaugustus/RabbitMirror.git
cd RabbitMirror

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### I'm getting import errors. What should I do?
1. Ensure you're in the virtual environment: `source venv/bin/activate`
2. Reinstall dependencies: `pip install -r requirements.txt`
3. Try installing in development mode: `pip install -e .`

### How do I update RabbitMirror?
```bash
git pull origin main
pip install -r requirements.txt
```

## Getting YouTube Data

### How do I get my YouTube watch history?
1. Go to [Google Takeout](https://takeout.google.com/)
2. Select "YouTube and YouTube Music"
3. Choose "history" and make sure "watch-history.html" is selected
4. Download your data and extract the ZIP file

### What formats does RabbitMirror support?
- **Primary**: YouTube's HTML export format (`watch-history.html`)
- **Secondary**: JSON format (for processed data)
- **Future**: Direct API integration (planned)

### My YouTube export is very large. Can RabbitMirror handle it?
Yes! RabbitMirror is designed to handle large datasets efficiently. Features include:
- Streaming parsers for memory efficiency
- Batch processing capabilities
- Progress tracking for long operations
- Robust error handling for interrupted processes

### Can I analyze someone else's YouTube data?
You should only analyze data you have permission to use. Always respect privacy and follow applicable laws and terms of service.

## Usage Questions

### How do I parse my YouTube history?
```bash
python run.py process parse your-watch-history.html --output parsed_data.json
```

### What analysis types are available?
- **Clustering**: Group similar videos and discover viewing themes
- **Pattern Detection**: Identify adversarial patterns and algorithmic manipulation
- **Suppression Analysis**: Detect content suppression patterns
- **Profile Simulation**: Generate synthetic viewing profiles
- **Trend Analysis**: Track viewing patterns over time

### How do I generate reports?
```bash
python run.py report generate-report parsed_data.json template.html report.html
```

### Can I export data to different formats?
Yes! RabbitMirror supports multiple export formats:
- JSON (default)
- CSV
- YAML
- Excel
- HTML reports

### How do I process multiple files at once?
```bash
python run.py process batch-process ./history_files/ --output-dir ./processed/ --recursive
```

## Error Handling

### What if RabbitMirror crashes during processing?
RabbitMirror includes robust error handling:
- **Automatic retries** for transient failures
- **Circuit breakers** to prevent cascading failures
- **Progress saving** to resume interrupted operations
- **Detailed error logging** for troubleshooting

### I'm getting timeout errors. What should I do?
1. Increase timeout values in configuration
2. Process data in smaller batches
3. Check your system resources (CPU, memory)
4. Report persistent issues on GitHub

### How do I debug parsing errors?
1. Check the log files in the `logs/` directory
2. Verify the HTML file format is correct
3. Try with a smaller sample of your data
4. Use the `--verbose` flag for detailed output

## Configuration

### How do I configure RabbitMirror?
RabbitMirror uses a built-in configuration system:
```bash
# Set configuration values
python run.py config set default_output_format "json"
python run.py config set analysis_threshold "0.7"

# View current configuration
python run.py config list
```

### Can I customize analysis parameters?
Yes! You can customize:
- **Clustering parameters**: `--eps`, `--min-samples`
- **Pattern detection**: `--threshold`, `--min-confidence`
- **Suppression analysis**: `--period`, `--threshold`
- **Export formats**: `--format`

### Where are configuration files stored?
- **Local config**: `.rabbitmirror/config.json` (project-specific)
- **Global config**: `~/.rabbitmirror/config.json` (user-wide)

## Performance & Optimization

### How can I speed up analysis?
1. **Use appropriate clustering parameters**: Lower `eps` and `min-samples` for faster clustering
2. **Process in batches**: Use batch processing for large datasets
3. **Optimize memory usage**: Close unnecessary applications
4. **Use SSD storage**: Faster disk I/O improves performance

### How much memory does RabbitMirror use?
Memory usage depends on your data size:
- **Small datasets** (< 1,000 videos): ~100MB
- **Medium datasets** (1,000-10,000 videos): ~500MB
- **Large datasets** (> 10,000 videos): ~1GB+

### Can I run RabbitMirror on a server?
Yes! RabbitMirror works well on servers:
- No GUI required
- Supports headless operation
- Can be automated with scripts
- Integrates with CI/CD pipelines

## Privacy & Security

### Is my data safe?
Yes! RabbitMirror is designed with privacy in mind:
- **Local processing**: All analysis happens on your device
- **No data transmission**: Your data never leaves your computer
- **Secure handling**: Follows secure coding practices
- **Open source**: Code is transparent and auditable

### Can I anonymize my data?
Yes! RabbitMirror includes data anonymization features:
- Remove personally identifiable information
- Replace video titles with generic identifiers
- Anonymize timestamps and metadata

### How do I delete my processed data?
Simply delete the output files and directories:
```bash
rm -rf exports/
rm -rf reports/
rm parsed_data.json
```

## Development & Contribution

### How can I contribute to RabbitMirror?
1. **Report bugs**: Use GitHub Issues
2. **Suggest features**: Create feature requests
3. **Submit code**: Fork the repository and submit pull requests
4. **Improve documentation**: Help improve guides and examples

### How do I set up a development environment?
```bash
# Clone and set up development environment
git clone https://github.com/romulusaugustus/RabbitMirror.git
cd RabbitMirror
make dev-setup

# Run tests
make test

# Run quality checks
make all-checks
```

### What's the test coverage?
RabbitMirror maintains high test coverage:
- **Overall coverage**: 70%+
- **Critical modules**: 80%+
- **Error handling**: 86%+
- **Total tests**: 360+ tests

### How do I add new analysis types?
1. Create a new analyzer class in the appropriate module
2. Add CLI commands in `cli.py`
3. Write comprehensive tests
4. Update documentation
5. Submit a pull request

## Troubleshooting

### Common Error Messages

#### "File not found" errors
- Check that the file path is correct
- Ensure the file exists and is readable
- Verify file permissions

#### "Encoding errors"
- Try different encoding options in configuration
- Check if the HTML file is corrupted
- Verify the file is a valid YouTube export

#### "Memory errors"
- Process data in smaller batches
- Increase system memory
- Close unnecessary applications

#### "Permission denied"
- Check file and directory permissions
- Ensure write access to output directories
- Run with appropriate privileges

### Performance Issues

#### Slow processing
- Reduce clustering parameters
- Use smaller batch sizes
- Check available system resources

#### High memory usage
- Process data in chunks
- Use streaming parsers
- Optimize configuration parameters

### Getting Help

#### Where can I get support?
- **GitHub Issues**: For bug reports and feature requests
- **GitHub Discussions**: For questions and community support
- **Documentation**: Comprehensive guides and API reference
- **Source code**: Well-documented and commented

#### How do I report a bug?
1. Check if the issue already exists
2. Create a new GitHub issue
3. Include:
   - RabbitMirror version
   - Python version
   - Operating system
   - Error messages
   - Steps to reproduce
   - Sample data (if possible)

#### How do I request a feature?
1. Search existing feature requests
2. Create a new GitHub issue with "Feature Request" label
3. Describe the feature and its benefits
4. Include use cases and examples

## Advanced Usage

### Can I integrate RabbitMirror with other tools?
Yes! RabbitMirror provides:
- **Python API**: Use as a library in your code
- **CLI interface**: Integrate with scripts and workflows
- **Standard formats**: Export to common formats (JSON, CSV, Excel)
- **Extensible architecture**: Add custom analyzers and exporters

### How do I use RabbitMirror in my research?
RabbitMirror is perfect for research:
- **Academic studies**: Analyze digital behavior patterns
- **Algorithm auditing**: Detect bias and manipulation
- **Privacy research**: Study data collection practices
- **Comparative analysis**: Compare different users' patterns

### Can I automate RabbitMirror?
Yes! RabbitMirror supports automation:
```bash
#!/bin/bash
# Example automation script
python run.py process parse data.html --output parsed.json
python run.py analyze cluster parsed.json --output clusters.json
python run.py report generate-report parsed.json --output-dir reports/
```

### How do I extend RabbitMirror?
1. **Create custom analyzers**: Extend base analyzer classes
2. **Add new export formats**: Implement export formatter interfaces
3. **Create plugins**: Use the plugin system for modular extensions
4. **Contribute back**: Share your extensions with the community

## Future Development

### What's on the roadmap?
- **Web-based dashboard**: Interactive web interface
- **Real-time analysis**: Live data processing
- **Multi-platform support**: Netflix, Spotify, etc.
- **Machine learning improvements**: Better pattern detection
- **API integrations**: Direct platform connections

### How often is RabbitMirror updated?
- **Regular updates**: Monthly releases with bug fixes
- **Feature releases**: Quarterly releases with new features
- **Security updates**: Immediate releases for security issues

### Can I influence development priorities?
Yes! Community feedback drives development:
- **Feature requests**: Vote on GitHub issues
- **Bug reports**: Help prioritize fixes
- **Contributions**: Submit code and improvements
- **Discussions**: Participate in community conversations

---

## Still Have Questions?

If you can't find the answer to your question here, please:
1. Check the [documentation](docs/index.rst)
2. Search [GitHub Issues](https://github.com/romulusaugustus/RabbitMirror/issues)
3. Ask on [GitHub Discussions](https://github.com/romulusaugustus/RabbitMirror/discussions)
4. Create a new issue if needed

We're here to help! 🐰
