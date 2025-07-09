#!/usr/bin/env python3

import click
import click_completion
import click_aliases
from loguru import logger
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from collections import Counter
from scipy.stats import entropy
import numpy as np
import json
import yaml

# Enable shell completion
click_completion.init()

from .parser import HistoryParser
from .cluster_engine import ClusterEngine
from .suppression_index import SuppressionIndex
from .adversarial_profiler import AdversarialProfiler
from .profile_simulator import ProfileSimulator
from .report_generator import ReportGenerator
from .qr_generator import QRGenerator
from .export_formatter import ExportFormatter
from .symbolic_logger import SymbolicLogger
# from .profile_comparator import ProfileComparator
# from .trend_analyzer import TrendAnalyzer
# from .config_manager import ConfigManager
# from .schema_validator import SchemaValidator
# from .dashboard_generator import DashboardGenerator

# Initialize logger
symbolic_logger = SymbolicLogger()

class AliasedGroup(click_aliases.ClickAliasedGroup):
    def get_command(self, ctx, cmd_name):
        # Try to get builtin commands first
        rv = click.Group.get_command(self, ctx, cmd_name)
        if rv is not None:
            return rv
        # Get aliases if builtin doesn't exist
        return click.Group.get_command(self, ctx, cmd_name)

@click.group(cls=AliasedGroup)
def cli():
    """RabbitMirror - Advanced YouTube Watch History Analysis Tool
    
    Analyze and understand your YouTube watch history patterns.
    """
    pass

# Data Processing Commands Group
@cli.group('process', help='Commands for data processing')
def process_group():
    pass

# Analysis Commands Group
@cli.group('analyze', help='Commands for data analysis')
def analyze_group():
    pass

# Report Commands Group
@cli.group('report', help='Commands for report generation')
def report_group():
    pass

# Utility Commands Group
@cli.group('utils', help='Utility commands')
def utils_group():
    pass

# Configuration Commands Group
@cli.group('config', help='Configuration commands')
def config_group():
    pass

@process_group.command(name='parse')
@click.argument('history_file', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(), help='Output file for parsed data')
@click.option('--format', '-f', type=click.Choice(['json', 'csv', 'yaml', 'excel']), default='json')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
def parse(history_file: str, output: Optional[str], format: str, verbose: bool = False):
    """Parse a YouTube watch history file."""
    try:
        parser = HistoryParser(history_file)
        entries = parser.parse()
        
        if output:
            exporter = ExportFormatter()
            output_file = exporter.export_data(
                {'entries': entries}, 
                format, 
                Path(output).stem if output else 'parsed_history'
            )
            click.echo(f"✅ Exported {len(entries)} entries to {output_file}")
        else:
            click.echo(entries)
            
    except Exception as e:
        symbolic_logger.log_error('parse_error', e)
        click.echo(f"❌ Error parsing history: {str(e)}", err=True)

@analyze_group.command(name='cluster')
@click.argument('history_file', type=click.Path(exists=True))
@click.option('--eps', type=float, default=0.3, help='DBSCAN eps parameter')
@click.option('--min-samples', type=int, default=5, help='DBSCAN min_samples parameter')
@click.option('--output', '-o', type=click.Path(), help='Output file for cluster data')
@click.option('--format', '-f', type=click.Choice(['json', 'csv', 'yaml', 'excel']), default='json')
@click.option('--visualization', '-viz', is_flag=True, help='Generate cluster visualization')
def cluster(history_file: str, eps: float, min_samples: int, output: Optional[str], format: str, visualization: bool = False):
    """Cluster videos in watch history."""
    try:
        parser = HistoryParser(history_file)
        entries = parser.parse()
        
        engine = ClusterEngine(eps=eps, min_samples=min_samples)
        clusters = engine.cluster_videos(entries)
        
        if output:
            exporter = ExportFormatter()
            output_file = exporter.export_data(
                clusters, 
                format, 
                Path(output).stem if output else 'video_clusters'
            )
            click.echo(f"✅ Exported cluster analysis to {output_file}")
        else:
            click.echo(clusters)
            
    except Exception as e:
        symbolic_logger.log_error('cluster_error', e)
        click.echo(f"❌ Error clustering videos: {str(e)}", err=True)

@analyze_group.command(name='analyze-suppression')
@click.argument('history_file', type=click.Path(exists=True))
@click.option('--period', type=int, default=30, help='Baseline period in days')
@click.option('--output', '-o', type=click.Path(), help='Output file for suppression data')
@click.option('--format', '-f', type=click.Choice(['json', 'csv', 'yaml', 'excel']), default='json')
@click.option('--threshold', '-t', type=float, default=0.5, help='Suppression threshold')
@click.option('--category-filter', '-cf', multiple=True, help='Filter specific categories')
def analyze_suppression(history_file: str, period: int, output: Optional[str], format: str):
    """Analyze content suppression patterns."""
    try:
        parser = HistoryParser(history_file)
        entries = parser.parse()
        
        analyzer = SuppressionIndex(baseline_period_days=period)
        results = analyzer.calculate_suppression(entries)
        
        if output:
            exporter = ExportFormatter()
            output_file = exporter.export_data(
                results, 
                format, 
                Path(output).stem if output else 'suppression_analysis'
            )
            click.echo(f"✅ Exported suppression analysis to {output_file}")
        else:
            click.echo(results)
            
    except Exception as e:
        symbolic_logger.log_error('suppression_error', e)
        click.echo(f"❌ Error analyzing suppression: {str(e)}", err=True)

@analyze_group.command(name='detect-patterns')
@click.argument('history_file', type=click.Path(exists=True))
@click.option('--threshold', type=float, default=0.7, help='Similarity threshold')
@click.option('--output', '-o', type=click.Path(), help='Output file for adversarial patterns')
@click.option('--format', '-f', type=click.Choice(['json', 'csv', 'yaml', 'excel']), default='json')
@click.option('--pattern-types', '-pt', multiple=True, help='Specific pattern types to detect')
@click.option('--min-confidence', '-mc', type=float, default=0.5, help='Minimum confidence threshold')
def detect_patterns(history_file: str, threshold: float, output: Optional[str], format: str, pattern_types: tuple = (), min_confidence: float = 0.5):
    """Detect potential adversarial patterns."""
    try:
        parser = HistoryParser(history_file)
        entries = parser.parse()
        
        profiler = AdversarialProfiler(similarity_threshold=threshold)
        patterns = profiler.identify_adversarial_patterns(entries)
        
        if output:
            exporter = ExportFormatter()
            output_file = exporter.export_data(
                patterns, 
                format, 
                Path(output).stem if output else 'adversarial_patterns'
            )
            click.echo(f"✅ Exported pattern analysis to {output_file}")
        else:
            click.echo(patterns)
            
    except Exception as e:
        symbolic_logger.log_error('pattern_detection_error', e)
        click.echo(f"❌ Error detecting patterns: {str(e)}", err=True)

@analyze_group.command(name='simulate')
@click.argument('history_file', type=click.Path(exists=True))
@click.option('--duration', type=int, default=30, help='Simulation duration in days')
@click.option('--seed', type=int, help='Random seed for simulation')
@click.option('--output', '-o', type=click.Path(), help='Output file for simulated profile')
@click.option('--format', '-f', type=click.Choice(['json', 'csv', 'yaml', 'excel']), default='json')
@click.option('--profile-type', '-pt', type=click.Choice(['regular', 'binge', 'sporadic']), default='regular')
@click.option('--intensity', '-i', type=float, default=1.0, help='Simulation intensity multiplier')
def simulate(history_file: str, duration: int, seed: Optional[int], output: Optional[str], format: str):
    """Simulate a watch history profile."""
    try:
        parser = HistoryParser(history_file)
        entries = parser.parse()
        
        simulator = ProfileSimulator(seed=seed)
        simulated_profile = simulator.simulate_profile(entries, duration_days=duration)
        
        if output:
            exporter = ExportFormatter()
            output_file = exporter.export_data(
                {'simulated_entries': simulated_profile}, 
                format, 
                Path(output).stem if output else 'simulated_profile'
            )
            click.echo(f"✅ Exported simulated profile to {output_file}")
        else:
            click.echo(simulated_profile)
            
    except Exception as e:
        symbolic_logger.log_error('simulation_error', e)
        click.echo(f"❌ Error simulating profile: {str(e)}", err=True)

@report_group.command(name='generate-report')
@click.argument('data_file', type=click.Path(exists=True))
@click.argument('template_file', type=click.Path(exists=True))
@click.argument('output_file', type=click.Path())
@click.option('--format', '-f', type=click.Choice(['html', 'pdf', 'md']), default='html')
@click.option('--theme', '-t', type=click.Choice(['light', 'dark']), default='light')
@click.option('--include-viz', '-v', is_flag=True, help='Include visualizations')
def generate_report(data_file: str, template_file: str, output_file: str):
    """Generate a report using a template."""
    try:
        # Load data from file
        exporter = ExportFormatter()
        with open(data_file, 'r') as f:
            data = exporter._load_data(data_file)
        
        # Generate report
        generator = ReportGenerator()
        generator.generate_report(data, template_file, output_file)
        click.echo(f"✅ Generated report at {output_file}")
        
    except Exception as e:
        symbolic_logger.log_error('report_generation_error', e)
        click.echo(f"❌ Error generating report: {str(e)}", err=True)

# New Commands
@process_group.command(name='batch-process')
@click.argument('input_dir', type=click.Path(exists=True))
@click.option('--output-dir', '-o', type=click.Path(), help='Output directory')
@click.option('--format', '-f', type=click.Choice(['json', 'csv', 'yaml', 'excel']), default='json')
@click.option('--recursive', '-r', is_flag=True, help='Process directories recursively')
def batch_process(input_dir: str, output_dir: Optional[str], format: str, recursive: bool):
    """Process multiple history files in a directory."""
    try:
        input_path = Path(input_dir)
        output_path = Path(output_dir) if output_dir else Path('processed_output')
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Find all HTML files
        pattern = '**/*.html' if recursive else '*.html'
        history_files = list(input_path.glob(pattern))
        
        if not history_files:
            click.echo("❌ No history files found in the specified directory")
            return
        
        total_processed = 0
        with click.progressbar(history_files, label='Processing files') as files:
            for file_path in files:
                try:
                    # Parse file
                    parser = HistoryParser(str(file_path))
                    entries = parser.parse()
                    
                    # Generate output filename
                    relative_path = file_path.relative_to(input_path)
                    output_file = output_path / relative_path.with_suffix(f'.{format}')
                    output_file.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Export data
                    exporter = ExportFormatter()
                    exporter.export_data(
                        {'entries': entries},
                        format,
                        str(output_file.with_suffix(''))
                    )
                    total_processed += 1
                    
                except Exception as e:
                    symbolic_logger.log_error(
                        'batch_process_error',
                        e,
                        {'file': str(file_path)}
                    )
                    click.echo(f"\n❌ Error processing {file_path}: {str(e)}", err=True)
        
        click.echo(f"\n✅ Successfully processed {total_processed} files")
        if total_processed < len(history_files):
            click.echo(f"⚠️  Failed to process {len(history_files) - total_processed} files")
            
    except Exception as e:
        symbolic_logger.log_error('batch_process_error', e)
        click.echo(f"❌ Error during batch processing: {str(e)}", err=True)

# @analyze_group.command(name='compare-profiles', aliases=['cp', 'compare'])
# @click.argument('profile1', type=click.Path(exists=True))
# @click.argument('profile2', type=click.Path(exists=True))
# @click.option('--metrics', '-m', multiple=True, help='Specific metrics to compare')
# @click.option('--output', '-o', type=click.Path(), help='Output file for comparison')
# @click.option('--format', '-f', type=click.Choice(['json', 'csv', 'yaml', 'excel']), default='json')
# def compare_profiles(profile1: str, profile2: str, metrics: List[str], output: Optional[str], format: str):
#     """Compare two watch history profiles."""
#     try:
#         comparator = ProfileComparator()
#         comparison = comparator.compare_profiles(profile1, profile2, metrics)
        
        # Print summary
        click.echo(f"\nProfile Comparison Results:")
        click.echo(f"Overall Similarity Score: {comparison.similarity_score:.2f}")
        
        # Print metrics
        click.echo("\nDetailed Metrics:")
        for metric in comparison.metrics:
            click.echo(f"- {metric.name}: {metric.value:.2f}")
            if metric.details:
                for key, value in metric.details.items():
                    click.echo(f"  * {key}: {value}")
        
        # Print patterns
        click.echo("\nCommon Patterns:")
        for category, patterns in comparison.common_patterns.items():
            if patterns:  # Only show non-empty categories
                click.echo(f"- {category}:")
                for pattern in patterns[:5]:  # Show top 5 patterns
                    click.echo(f"  * {pattern}")
        
        # Export data if output specified
        if output:
            exporter = ExportFormatter()
            output_file = exporter.export_data(
                {
                    'similarity_score': comparison.similarity_score,
                    'metrics': [{
                        'name': m.name,
                        'value': m.value,
                        'details': m.details
                    } for m in comparison.metrics],
                    'common_patterns': comparison.common_patterns,
                    'unique_patterns': comparison.unique_patterns,
                    'timestamp': comparison.timestamp.isoformat()
                },
                format,
                Path(output).stem if output else 'profile_comparison'
            )
            click.echo(f"\n✅ Exported comparison results to {output_file}")
            
    except Exception as e:
        symbolic_logger.log_error('profile_comparison_error', e)
        click.echo(f"❌ Error comparing profiles: {str(e)}", err=True)

# @analyze_group.command(name='trend-analysis', aliases=['ta', 'trends'])
# @click.argument('history_file', type=click.Path(exists=True))
# @click.option('--period', type=click.Choice(['daily', 'weekly', 'monthly']), default='daily')
# @click.option('--metrics', '-m', multiple=True, help='Metrics to analyze')
# @click.option('--output', '-o', type=click.Path(), help='Output file for trends')
# @click.option('--format', '-f', type=click.Choice(['json', 'csv', 'yaml', 'excel']), default='json')
# @click.option('--normalize', '-n', is_flag=True, help='Normalize trend values')
# def trend_analysis(history_file: str, period: str, metrics: List[str], output: Optional[str], format: str, normalize: bool):
#     """Analyze trends in watch history."""
#     try:
#         # Parse history file
#         parser = HistoryParser(history_file)
#         entries = parser.parse()
#         
#         # Calculate trends
#         analyzer = TrendAnalyzer(
#             period_type=period,
#             normalize=normalize
#         )
#         trends = analyzer.analyze_trends(entries, metrics if metrics else None)
        
        # Print summary
        click.echo(f"\nTrend Analysis Results:")
        click.echo(f"Period: {period}")
        click.echo(f"Total timeframes analyzed: {len(trends['timeframes'])}")
        
        # Print metric trends
        click.echo("\nMetric Trends:")
        for metric, values in trends['metrics'].items():
            click.echo(f"\n{metric}:")
            # Print the most recent N values
            recent_values = list(zip(trends['timeframes'][-5:], values[-5:]))
            for timeframe, value in recent_values:
                click.echo(f"  {timeframe}: {value:.2f}")
        
        # Print significant changes
        if trends.get('significant_changes'):
            click.echo("\nSignificant Changes:")
            for change in trends['significant_changes']:
                click.echo(f"- {change['metric']}: {change['description']}")
                click.echo(f"  From {change['from_value']:.2f} to {change['to_value']:.2f}")
                click.echo(f"  Period: {change['timeframe']}")
        
        # Export data if output specified
        if output:
            exporter = ExportFormatter()
            output_file = exporter.export_data(
                {
                    'trends': trends,
                    'metadata': {
                        'period': period,
                        'metrics': list(trends['metrics'].keys()),
                        'normalized': normalize,
                        'timestamp': datetime.now().isoformat()
                    }
                },
                format,
                Path(output).stem if output else 'trend_analysis'
            )
            click.echo(f"\n✅ Exported trend analysis to {output_file}")
            
    except Exception as e:
        symbolic_logger.log_error('trend_analysis_error', e)
        click.echo(f"❌ Error analyzing trends: {str(e)}", err=True)

# @report_group.command(name='export-dashboard', aliases=['ed', 'dashboard'])
# @click.argument('data_file', type=click.Path(exists=True))
# @click.option('--template', '-t', type=click.Choice(['basic', 'advanced', 'custom']), default='basic')
# @click.option('--output', '-o', type=click.Path(), help='Output directory')
# @click.option('--interactive', '-i', is_flag=True, help='Generate interactive dashboard')
# @click.option('--theme', '-th', type=click.Choice(['light', 'dark']), default='light')
# @click.option('--include-plots', '-p', is_flag=True, help='Include plot visualizations')
# def export_dashboard(data_file: str, template: str, output: Optional[str], interactive: bool, theme: str, include_plots: bool):
#     """Export data as an interactive dashboard."""
#     try:
#         # Load data
#         exporter = ExportFormatter()
#         with open(data_file, 'r') as f:
#             data = exporter._load_data(data_file)
#             
#         # Determine output path
#         output_path = Path(output) if output else Path('dashboard_output')
#         output_path.mkdir(parents=True, exist_ok=True)
#         
#         # Create dashboard
#         dashboard = DashboardGenerator(
#             template=template,
#             interactive=interactive,
#             theme=theme,
#             include_plots=include_plots
#         )
#         
#         # Generate dashboard files
#         dashboard_files = dashboard.generate_dashboard(data, output_path)
        
        # Print summary
        click.echo(f"\nDashboard Generation Complete:")
        click.echo(f"Template: {template}")
        click.echo(f"Interactive: {'Yes' if interactive else 'No'}")
        click.echo(f"Theme: {theme}")
        
        # List generated files
        click.echo("\nGenerated Files:")
        for file_type, file_path in dashboard_files.items():
            click.echo(f"- {file_type}: {file_path}")
            
        # Print instructions for viewing
        if interactive:
            click.echo("\nTo view the dashboard:")
            click.echo(f"1. Navigate to: {output_path}")
            click.echo(f"2. Start a local server: python -m http.server")
            click.echo(f"3. Open in browser: http://localhost:8000")
        else:
            click.echo(f"\nDashboard exported to: {output_path}")
            
    except Exception as e:
        symbolic_logger.log_error('dashboard_export_error', e)
        click.echo(f"❌ Error exporting dashboard: {str(e)}", err=True)

# @config_group.command(name='set', aliases=['s'])
# @click.argument('key', type=str)
# @click.argument('value', type=str)
# @click.option('--global/--local', default=False, help='Store in global or local config')
# def set_config(key: str, value: str, global_: bool):
#     """Set a configuration value."""
#     try:
#         config = ConfigManager(use_global=global_)
#         config.set(key, value)
#         click.echo(f"✅ Set {key} = {value} in {'global' if global_ else 'local'} config")
#     except Exception as e:
#         symbolic_logger.log_error('config_set_error', e)
#         click.echo(f"❌ Error setting config: {str(e)}", err=True)

@config_group.command(name='get')
@click.argument('key', type=str)
@click.option('--global/--local', default=False, help='Read from global or local config')
def get_config(key: str, global_: bool):
    """Get a configuration value."""
    click.echo("Configuration management not yet implemented")

@config_group.command(name='list')
@click.option('--global/--local', default=False, help='List global or local config')
@click.option('--format', '-f', type=click.Choice(['text', 'json', 'yaml']), default='text')
def list_config(global_: bool, format: str):
    """List all configuration values."""
    click.echo("Configuration management not yet implemented")

@utils_group.command(name='validate')
@click.argument('file', type=click.Path(exists=True))
@click.option('--schema', '-s', type=click.Path(exists=True), help='Schema file for validation')
@click.option('--format', '-f', type=click.Choice(['json', 'yaml']), default='json')
def validate_file(file: str, schema: Optional[str], format: str):
    """Validate a data file against a schema."""
    try:
        # Load data file
        with open(file, 'r') as f:
            if format == 'json':
                data = json.load(f)
            else:
                data = yaml.safe_load(f)

        # Load schema if provided, otherwise use default schema
        if schema:
            with open(schema, 'r') as f:
                schema_data = json.load(f) if format == 'json' else yaml.safe_load(f)
        else:
            schema_data = default_schema = {
                "type": "object",
                "properties": {
                    "entries": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "required": ["timestamp", "title"],
                            "properties": {
                                "timestamp": {"type": "string", "format": "date-time"},
                                "title": {"type": "string"},
                                "videoId": {"type": "string"},
                                "channelId": {"type": "string"}
                            }
                        }
                    }
                }
            }

        # Schema validation not yet implemented
        click.echo("Schema validation not yet implemented")

    except Exception as e:
        symbolic_logger.log_error('validation_error', e)
        click.echo(f"❌ Error validating file: {str(e)}", err=True)

@utils_group.command(name='convert')
@click.argument('input_file', type=click.Path(exists=True))
@click.argument('output_format', type=click.Choice(['json', 'csv', 'yaml', 'excel']))
@click.option('--output', '-o', type=click.Path(), help='Output file')
def convert_file(input_file: str, output_format: str, output: Optional[str]):
    """Convert a file between formats."""
    try:
        # Load input file using ExportFormatter
        exporter = ExportFormatter()
        data = exporter._load_data(input_file)
        
        # Generate output filename if not provided
        if not output:
            output = str(Path(input_file).with_suffix(f'.{output_format}'))
        
        # Export to new format
        output_file = exporter.export_data(
            data,
            output_format,
            Path(output).stem
        )
        
        click.echo(f"✅ Converted {input_file} to {output_file}")
        
    except Exception as e:
        symbolic_logger.log_error('conversion_error', e)
        click.echo(f"❌ Error converting file: {str(e)}", err=True)

@cli.command(name='completion', help='Output shell completion code')
@click.argument('shell', type=click.Choice(['bash', 'zsh', 'fish']))
def completion(shell: str):
    """Generate shell completion script."""
    click.echo(click_completion.get_code(shell))

@utils_group.command(name='generate-qr')
@click.argument('data', type=str)
@click.option('--output', '-o', type=click.Path(), help='Output file for QR code')
@click.option('--size', '-s', type=int, default=10, help='QR code size')
@click.option('--error-correction', '-e', type=click.Choice(['L', 'M', 'Q', 'H']), default='M')
@click.option('--color', '-c', type=str, default='black', help='QR code color')
def generate_qr(data: str, output: Optional[str], size: int, error_correction: str, color: str):
    """Generate a QR code for the given data."""
    try:
        generator = QRGenerator(
            size=size,
            error_correction=error_correction,
            color=color
        )
        qr_file = generator.generate_qr(data, filename=Path(output).stem if output else None)
        click.echo(f"✅ Generated QR code at {qr_file}")
        
    except Exception as e:
        symbolic_logger.log_error('qr_generation_error', e)
        click.echo(f"❌ Error generating QR code: {str(e)}", err=True)

def main():
    # Register shell completion
    click_completion.init()
    cli()

if __name__ == '__main__':
    main()
