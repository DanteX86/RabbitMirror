#!/usr/bin/env python3

import json
from datetime import datetime
from pathlib import Path
from typing import Optional

import click
import click_aliases
import jsonschema
import yaml

from .adversarial_profiler import AdversarialProfiler
from .cluster_engine import ClusterEngine
from .config_manager import ConfigManager
from .dashboard_generator import DashboardGenerator
from .exceptions import RabbitMirrorError, create_error_context, format_error_message
from .export_formatter import ExportFormatter
from .parser import HistoryParser
from .profile_simulator import ProfileSimulator
from .qr_generator import QRGenerator
from .report_generator import ReportGenerator
from .schema_validator import SchemaValidator
from .suppression_index import SuppressionIndex
from .symbolic_logger import SymbolicLogger
from .trend_analyzer import TrendAnalyzer

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


# Data Processing Commands Group
@cli.group("process", help="Commands for data processing")
def process_group():
    pass


# Analysis Commands Group
@cli.group("analyze", help="Commands for data analysis")
def analyze_group():
    pass


# Report Commands Group
@cli.group("report", help="Commands for report generation")
def report_group():
    pass


# Utility Commands Group
@cli.group("utils", help="Utility commands")
def utils_group():
    pass


# Configuration Commands Group
@cli.group("config", help="Configuration commands")
def config_group():
    pass


@process_group.command(name="parse")
@click.argument("history_file", type=click.Path(exists=True))
@click.option("--output", "-o", type=click.Path(), help="Output file for parsed data")
@click.option(
    "--format",
    "-f",
    "output_format",
    type=click.Choice(["json", "csv", "yaml", "excel"]),
    default="json",
)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
def parse(
    history_file: str, output: Optional[str], output_format: str, verbose: bool = False
):
    """Parse a YouTube watch history file."""
    try:
        parser = HistoryParser(history_file)
        entries = parser.parse()

        if output:
            output_path = Path(output)
            exporter = ExportFormatter(output_dir=output_path.parent)
            output_file = exporter.export_data(
                {"entries": entries}, output_format, output_path.stem
            )
            click.echo(f"✅ Exported {len(entries)} entries to {output_file}")
        else:
            click.echo(entries)

    except RabbitMirrorError as e:
        symbolic_logger.log_error("parse_error", e.to_dict())
        click.echo(f"❌ {format_error_message(e)}", err=True)
        raise SystemExit(1) from e
    except Exception as e:
        context = create_error_context("parse_history", file=history_file)
        symbolic_logger.log_error("parse_error", e, context)
        click.echo(f"❌ Unexpected error parsing history: {str(e)}", err=True)
        raise SystemExit(1) from e


@analyze_group.command(name="cluster")
@click.argument("history_file", type=click.Path(exists=True))
@click.option("--eps", type=float, default=0.3, help="DBSCAN eps parameter")
@click.option("--min-samples", type=int, default=5, help="DBSCAN min_samples parameter")
@click.option("--output", "-o", type=click.Path(), help="Output file for cluster data")
@click.option(
    "--format",
    "-f",
    "output_format",
    type=click.Choice(["json", "csv", "yaml", "excel"]),
    default="json",
)
@click.option(
    "--visualization", "-viz", is_flag=True, help="Generate cluster visualization"
)
def cluster(
    history_file: str,
    eps: float,
    min_samples: int,
    output: Optional[str],
    output_format: str,
    visualization: bool = False,
):
    """Cluster videos in watch history."""
    try:
        parser = HistoryParser(history_file)
        entries = parser.parse()

        engine = ClusterEngine(eps=eps, min_samples=min_samples)
        clusters = engine.cluster_videos(entries)

        if output:
            output_path = Path(output)
            exporter = ExportFormatter(output_dir=output_path.parent)
            output_file = exporter.export_data(
                clusters, output_format, output_path.stem
            )
            click.echo(f"✅ Exported cluster analysis to {output_file}")
        else:
            click.echo(clusters)

    except RabbitMirrorError as e:
        symbolic_logger.log_error("cluster_error", e.to_dict())
        click.echo(f"❌ {format_error_message(e)}", err=True)
        raise SystemExit(1) from e
    except Exception as e:
        context = create_error_context("cluster_videos", file=history_file)
        symbolic_logger.log_error("cluster_error", e, context)
        click.echo(f"❌ Unexpected error clustering videos: {str(e)}", err=True)
        raise SystemExit(1) from e


@analyze_group.command(name="analyze-suppression")
@click.argument("history_file", type=click.Path(exists=True))
@click.option("--period", type=int, default=30, help="Baseline period in days")
@click.option(
    "--output", "-o", type=click.Path(), help="Output file for suppression data"
)
@click.option(
    "--format",
    "-f",
    "output_format",
    type=click.Choice(["json", "csv", "yaml", "excel"]),
    default="json",
)
@click.option(
    "--threshold", "-t", type=float, default=0.5, help="Suppression threshold"
)
@click.option(
    "--category-filter", "-cf", multiple=True, help="Filter specific categories"
)
def analyze_suppression(
    history_file: str,
    period: int,
    output: Optional[str],
    output_format: str,
    threshold: float = 0.5,
    category_filter: tuple = (),
):
    """Analyze content suppression patterns."""
    try:
        parser = HistoryParser(history_file)
        entries = parser.parse()

        analyzer = SuppressionIndex(baseline_period_days=period)
        results = analyzer.calculate_suppression(entries)

        if output:
            output_path = Path(output)
            exporter = ExportFormatter(output_dir=output_path.parent)
            output_file = exporter.export_data(results, output_format, output_path.stem)
            click.echo(f"✅ Exported suppression analysis to {output_file}")
        else:
            click.echo(results)

    except RabbitMirrorError as e:
        symbolic_logger.log_error("suppression_error", e.to_dict())
        click.echo(f"❌ {format_error_message(e)}", err=True)
        raise SystemExit(1) from e
    except Exception as e:
        context = create_error_context("analyze_suppression", file=history_file)
        symbolic_logger.log_error("suppression_error", e, context)
        click.echo(f"❌ Unexpected error analyzing suppression: {str(e)}", err=True)
        raise SystemExit(1) from e


@analyze_group.command(name="detect-patterns")
@click.argument("history_file", type=click.Path(exists=True))
@click.option("--threshold", type=float, default=0.7, help="Similarity threshold")
@click.option(
    "--output", "-o", type=click.Path(), help="Output file for adversarial patterns"
)
@click.option(
    "--format",
    "-f",
    "output_format",
    type=click.Choice(["json", "csv", "yaml", "excel"]),
    default="json",
)
@click.option(
    "--pattern-types", "-pt", multiple=True, help="Specific pattern types to detect"
)
@click.option(
    "--min-confidence",
    "-mc",
    type=float,
    default=0.5,
    help="Minimum confidence threshold",
)
def detect_patterns(
    history_file: str,
    threshold: float,
    output: Optional[str],
    output_format: str,
    pattern_types: tuple = (),
    min_confidence: float = 0.5,
):
    """Detect potential adversarial patterns."""
    try:
        parser = HistoryParser(history_file)
        entries = parser.parse()

        profiler = AdversarialProfiler(similarity_threshold=threshold)
        patterns = profiler.identify_adversarial_patterns(entries)

        if output:
            output_path = Path(output)
            exporter = ExportFormatter(output_dir=output_path.parent)
            output_file = exporter.export_data(
                patterns, output_format, output_path.stem
            )
            click.echo(f"✅ Exported pattern analysis to {output_file}")
        else:
            click.echo(patterns)

    except RabbitMirrorError as e:
        symbolic_logger.log_error("pattern_detection_error", e.to_dict())
        click.echo(f"❌ {format_error_message(e)}", err=True)
        raise SystemExit(1) from e
    except Exception as e:
        context = create_error_context("detect_patterns", file=history_file)
        symbolic_logger.log_error("pattern_detection_error", e, context)
        click.echo(f"❌ Unexpected error detecting patterns: {str(e)}", err=True)
        raise SystemExit(1) from e


@analyze_group.command(name="simulate")
@click.argument("history_file", type=click.Path(exists=True))
@click.option("--duration", type=int, default=30, help="Simulation duration in days")
@click.option("--seed", type=int, help="Random seed for simulation")
@click.option(
    "--output", "-o", type=click.Path(), help="Output file for simulated profile"
)
@click.option(
    "--format",
    "-f",
    "output_format",
    type=click.Choice(["json", "csv", "yaml", "excel"]),
    default="json",
)
@click.option(
    "--profile-type",
    "-pt",
    type=click.Choice(["regular", "binge", "sporadic"]),
    default="regular",
)
@click.option(
    "--intensity", "-i", type=float, default=1.0, help="Simulation intensity multiplier"
)
def simulate(
    history_file: str,
    duration: int,
    seed: Optional[int],
    output: Optional[str],
    output_format: str,
    profile_type: str = "regular",
    intensity: float = 1.0,
):
    """Simulate a watch history profile."""
    try:
        parser = HistoryParser(history_file)
        entries = parser.parse()

        simulator = ProfileSimulator(seed=seed)
        simulated_profile = simulator.simulate_profile(entries, duration_days=duration)

        if output:
            output_path = Path(output)
            exporter = ExportFormatter(output_dir=output_path.parent)
            output_file = exporter.export_data(
                {"simulated_entries": simulated_profile},
                output_format,
                output_path.stem,
            )
            click.echo(f"✅ Exported simulated profile to {output_file}")
        else:
            click.echo(simulated_profile)

    except (FileNotFoundError, ValueError, json.JSONDecodeError) as e:
        symbolic_logger.log_error("simulation_error", e)
        click.echo(f"❌ Error simulating profile: {str(e)}", err=True)


@report_group.command(name="generate-report")
@click.argument("data_file", type=click.Path(exists=True))
@click.argument("template_file", type=click.Path(exists=True))
@click.argument("output_file", type=click.Path())
@click.option(
    "--format", "-f", type=click.Choice(["html", "pdf", "md"]), default="html"
)
@click.option("--theme", "-t", type=click.Choice(["light", "dark"]), default="light")
@click.option("--include-viz", "-v", is_flag=True, help="Include visualizations")
def generate_report(data_file: str, template_file: str, output_file: str):
    """Generate a report using a template."""
    try:
        # Load data from file
        exporter = ExportFormatter()
        data = exporter.load_data(data_file)

        # Generate report
        generator = ReportGenerator()
        generator.generate_report(data, template_file, output_file)
        click.echo(f"✅ Generated report at {output_file}")

    except (FileNotFoundError, ValueError, json.JSONDecodeError) as e:
        symbolic_logger.log_error("report_generation_error", e)
        click.echo(f"❌ Error generating report: {str(e)}", err=True)


# New Commands
@process_group.command(name="batch-process")
@click.argument("input_dir", type=click.Path(exists=True))
@click.option("--output-dir", "-o", type=click.Path(), help="Output directory")
@click.option(
    "--format",
    "-f",
    "output_format",
    type=click.Choice(["json", "csv", "yaml", "excel"]),
    default="json",
)
@click.option("--recursive", "-r", is_flag=True, help="Process directories recursively")
def batch_process(
    input_dir: str, output_dir: Optional[str], output_format: str, recursive: bool
):
    """Process multiple history files in a directory."""
    try:
        input_path = Path(input_dir)
        output_path = Path(output_dir) if output_dir else Path("processed_output")
        output_path.mkdir(parents=True, exist_ok=True)

        # Find all HTML files
        pattern = "**/*.html" if recursive else "*.html"
        history_files = list(input_path.glob(pattern))

        if not history_files:
            click.echo("❌ No history files found in the specified directory")
            return

        total_processed = 0
        with click.progressbar(history_files, label="Processing files") as files:
            for file_path in files:
                try:
                    # Parse file
                    parser = HistoryParser(str(file_path))
                    entries = parser.parse()

                    # Generate output filename
                    relative_path = file_path.relative_to(input_path)
                    output_file = output_path / relative_path.with_suffix(
                        f".{output_format}"
                    )
                    output_file.parent.mkdir(parents=True, exist_ok=True)

                    # Export data
                    exporter = ExportFormatter()
                    exporter.export_data(
                        {"entries": entries},
                        output_format,
                        str(output_file.with_suffix("")),
                    )
                    total_processed += 1

                except (FileNotFoundError, ValueError, json.JSONDecodeError) as e:
                    symbolic_logger.log_error(
                        "batch_process_error", e, {"file": str(file_path)}
                    )
                    click.echo(f"\n❌ Error processing {file_path}: {str(e)}", err=True)

        click.echo(f"\n✅ Successfully processed {total_processed} files")
        if total_processed < len(history_files):
            click.echo(
                f"⚠️  Failed to process {len(history_files) - total_processed} files"
            )

    except (FileNotFoundError, ValueError, json.JSONDecodeError, OSError) as e:
        symbolic_logger.log_error("batch_process_error", e)
        click.echo(f"❌ Error during batch processing: {str(e)}", err=True)

    # @analyze_group.command(name='compare-profiles', aliases=['cp', 'compare'])
    # @click.argument('profile1', type=click.Path(exists=True))
    # @click.argument('profile2', type=click.Path(exists=True))
    # @click.option('--metrics', '-m', multiple=True,
    #               help='Specific metrics to compare')
    # @click.option('--output', '-o', type=click.Path(),
    #               help='Output file for comparison')
    # @click.option('--format', '-f',
    #               type=click.Choice(['json', 'csv', 'yaml', 'excel']),
    #               default='json')
    # def compare_profiles(profile1: str, profile2: str, metrics: List[str],
    #                      output: Optional[str], format: str):
    #     """Compare two watch history profiles."""
    #     try:
    #         comparator = ProfileComparator()
    #         comparison = comparator.compare_profiles(profile1, profile2, metrics)
    #
    #        # Print summary
    #        click.echo(f"\nProfile Comparison Results:")
    #        click.echo(f"Overall Similarity Score: {comparison.similarity_score:.2f}")
    #
    #        # Print metrics
    #        click.echo("\nDetailed Metrics:")
    #        for metric in comparison.metrics:
    #            click.echo(f"- {metric.name}: {metric.value:.2f}")
    #            if metric.details:
    #                for key, value in metric.details.items():
    #                    click.echo(f"  * {key}: {value}")
    #
    #        # Print patterns
    #        click.echo("\nCommon Patterns:")
    #        for category, patterns in comparison.common_patterns.items():
    #            if patterns:  # Only show non-empty categories
    #                click.echo(f"- {category}:")
    #                for pattern in patterns[:5]:  # Show top 5 patterns
    #                    click.echo(f"  * {pattern}")
    #
    #        # Export data if output specified
    #        if output:
    #            exporter = ExportFormatter()
    #            output_file = exporter.export_data(
    #                {
    #                    'similarity_score': comparison.similarity_score,
    #                    'metrics': [{
    #                        'name': m.name,
    #                        'value': m.value,
    #                        'details': m.details
    #                    } for m in comparison.metrics],
    #                    'common_patterns': comparison.common_patterns,
    #                    'unique_patterns': comparison.unique_patterns,
    #                    'timestamp': comparison.timestamp.isoformat()
    #                },
    #                format,
    #                Path(output).stem if output else 'profile_comparison'
    #            )
    #            click.echo(f"\n✅ Exported comparison results to {output_file}")
    #
    #    except (FileNotFoundError, ValueError, json.JSONDecodeError) as e:
    #        symbolic_logger.log_error("profile_comparison_error", e)
    #        click.echo(f"❌ Error comparing profiles: {str(e)}", err=True)


@analyze_group.command(name="trend-analysis")
@click.argument("history_file", type=click.Path(exists=True))
@click.option(
    "--period", type=click.Choice(["daily", "weekly", "monthly"]), default="daily"
)
@click.option("--metrics", "-m", multiple=True, help="Metrics to analyze")
@click.option("--output", "-o", type=click.Path(), help="Output file for trends")
@click.option(
    "--format",
    "-f",
    "output_format",
    type=click.Choice(["json", "csv", "yaml", "excel"]),
    default="json",
)
@click.option("--normalize", "-n", is_flag=True, help="Normalize trend values")
def trend_analysis(
    history_file: str,
    period: str,
    metrics: tuple,
    output: Optional[str],
    output_format: str,
    normalize: bool,
):
    """Analyze trends in watch history."""
    try:
        # Parse history file
        parser = HistoryParser(history_file)
        entries = parser.parse()

        # Calculate trends
        analyzer = TrendAnalyzer(period_type=period, normalize=normalize)
        trends = analyzer.analyze_trends(entries, list(metrics) if metrics else None)

        # Print summary
        click.echo("\n📈 Trend Analysis Results:")
        click.echo(f"Period: {period}")
        click.echo(f"Total timeframes analyzed: {len(trends['timeframes'])}")
        click.echo(
            f"Date range: {trends['date_range']['start']} to "
            f"{trends['date_range']['end']}"
        )

        # Print metric trends
        click.echo("\n📊 Metric Trends:")
        for metric, data in trends["metrics"].items():
            direction_emoji = {
                "increasing": "↗️",
                "decreasing": "↘️",
                "stable": "➡️",
            }.get(data["trend_direction"], "➡️")

            click.echo(f"\n{direction_emoji} {metric}:")
            click.echo(f"  Direction: {data['trend_direction']}")
            click.echo(f"  Strength: {data['trend_strength']:.2f}")

            # Show recent values
            if len(data["values"]) > 0:
                recent_count = min(5, len(data["values"]))
                recent_values = data["values"][-recent_count:]
                recent_timeframes = trends["timeframes"][-recent_count:]

                click.echo("  Recent values:")
                for timeframe, value in zip(recent_timeframes, recent_values):
                    click.echo(f"    {timeframe}: {value:.2f}")

        # Print significant changes
        if trends.get("significant_changes"):
            click.echo("\n⚠️  Significant Changes:")
            for change in trends["significant_changes"]:
                click.echo(f"- {change['metric']}: {change['description']}")
                click.echo(
                    f"  From {change['from_value']:.2f} to {change['to_value']:.2f}"
                )
                click.echo(f"  Period: {change['timeframe']}")
        else:
            click.echo("\n✅ No significant changes detected")

        # Print summary statistics
        summary = trends["summary"]
        if summary["trending_up"]:
            click.echo(f"\n↗️ Trending Up: {', '.join(summary['trending_up'])}")
        if summary["trending_down"]:
            click.echo(f"↘️ Trending Down: {', '.join(summary['trending_down'])}")
        if summary["stable_metrics"]:
            click.echo(f"➡️ Stable: {', '.join(summary['stable_metrics'])}")

        # Export data if output specified
        if output:
            exporter = ExportFormatter()
            output_file = exporter.export_data(
                {
                    "trends": trends,
                    "metadata": {
                        "period": period,
                        "metrics": list(trends["metrics"].keys()),
                        "normalized": normalize,
                        "timestamp": datetime.now().isoformat(),
                    },
                },
                output_format,
                Path(output).stem if output else "trend_analysis",
            )
            click.echo(f"\n✅ Exported trend analysis to {output_file}")

    except (FileNotFoundError, ValueError, json.JSONDecodeError) as e:
        symbolic_logger.log_error("trend_analysis_error", e)
        click.echo(f"❌ Error analyzing trends: {str(e)}", err=True)


@report_group.command(name="export-dashboard")
@click.argument("data_file", type=click.Path(exists=True))
@click.option(
    "--template",
    "-t",
    type=click.Choice(["basic", "advanced", "custom"]),
    default="basic",
)
@click.option("--output", "-o", type=click.Path(), help="Output directory")
@click.option(
    "--interactive", "-i", is_flag=True, help="Generate interactive dashboard"
)
@click.option("--theme", "-th", type=click.Choice(["light", "dark"]), default="light")
@click.option("--include-plots", "-p", is_flag=True, help="Include plot visualizations")
def export_dashboard(
    data_file: str,
    template: str,
    output: Optional[str],
    interactive: bool,
    theme: str,
    include_plots: bool,
):
    """Export data as an interactive dashboard."""
    try:
        # Load data
        exporter = ExportFormatter()
        data = exporter.load_data(data_file)

        # Determine output path
        output_path = Path(output) if output else Path("dashboard_output")
        output_path.mkdir(parents=True, exist_ok=True)

        # Create dashboard
        dashboard = DashboardGenerator(
            template=template,
            interactive=interactive,
            theme=theme,
            include_plots=include_plots,
        )

        # Generate dashboard files
        dashboard_files = dashboard.generate_dashboard(data, output_path)

        # Print summary (commented out due to missing implementation)
        click.echo("\nDashboard Generation Complete:")
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
            click.echo("2. Start a local server: python -m http.server")
            click.echo("3. Open in browser: http://localhost:8000")
        else:
            click.echo(f"\nDashboard exported to: {output_path}")

    except (FileNotFoundError, ValueError, json.JSONDecodeError) as e:
        symbolic_logger.log_error("dashboard_export_error", e)
        click.echo(f"❌ Error exporting dashboard: {str(e)}", err=True)


@config_group.command(name="set")
@click.argument("key", type=str)
@click.argument("value", type=str)
@click.option(
    "--global/--local", "global_", default=False, help="Store in global or local config"
)
def set_config(key: str, value: str, global_: bool):
    """Set a configuration value."""
    try:
        config = ConfigManager(use_global=global_)
        config.set(key, value)
        click.echo(
            f"✅ Set {key} = {value} in {'global' if global_ else 'local'} config"
        )
    except (FileNotFoundError, ValueError, OSError) as e:
        symbolic_logger.log_error("config_set_error", e)
        click.echo(f"❌ Error setting config: {str(e)}", err=True)


@config_group.command(name="get")
@click.argument("key", type=str)
@click.option(
    "--global/--local",
    "is_global",
    default=False,
    help="Read from global or local config",
)
def get_config(key: str, is_global: bool):
    """Get a configuration value."""
    try:
        config = ConfigManager(use_global=is_global)
        value = config.get(key)
        if value is not None:
            click.echo(f"{key} = {value}")
        else:
            click.echo(f"❌ Key '{key}' not found.", err=True)
    except (FileNotFoundError, ValueError, KeyError) as e:
        symbolic_logger.log_error("config_get_error", e)
        click.echo(f"❌ Error getting config: {str(e)}", err=True)


@config_group.command(name="list")
@click.option(
    "--global/--local", "is_global", default=False, help="List global or local config"
)
@click.option(
    "--format",
    "-f",
    "output_format",
    type=click.Choice(["text", "json", "yaml"]),
    default="text",
)
def list_config(is_global: bool, output_format: str):
    """List all configuration values."""
    try:
        config = ConfigManager(use_global=is_global)
        config_list = config.list(as_json=output_format == "json")
        click.echo(config_list)
    except (FileNotFoundError, ValueError, OSError) as e:
        symbolic_logger.log_error("config_list_error", e)
        click.echo(f"❌ Error listing config: {str(e)}", err=True)


@utils_group.command(name="validate")
@click.argument("file", type=click.Path(exists=True))
@click.option(
    "--schema", "-s", type=click.Path(exists=True), help="Schema file for validation"
)
@click.option(
    "--format",
    "-f",
    "output_format",
    type=click.Choice(["json", "yaml"]),
    default="json",
)
def validate_file(file: str, schema: Optional[str], output_format: str):
    """Validate a data file against a schema."""
    try:
        # Load data file
        with open(file, "r", encoding="utf-8") as f:
            if output_format == "json":
                data = json.load(f)
            else:
                data = yaml.safe_load(f)

        # Load custom schema if provided
        if schema:
            with open(schema, "r", encoding="utf-8") as f:
                custom_schema = (
                    json.load(f) if output_format == "json" else yaml.safe_load(f)
                )

            # Validate against custom schema
            try:
                jsonschema.validate(instance=data, schema=custom_schema)
                click.echo(f"✅ {file} is valid against custom schema.")
            except jsonschema.exceptions.ValidationError as ve:
                click.echo(f"❌ Validation failed: {ve.message}")
                path_str = (
                    " -> ".join(str(p) for p in ve.absolute_path)
                    if ve.absolute_path
                    else "root"
                )
                click.echo(f"   Path: {path_str}")
                return
        else:
            # Validate against default schemas with auto-detection
            schema_validator = SchemaValidator()

            # Try auto-detection first
            detected_schema = schema_validator.auto_detect_schema(data)

            if detected_schema:
                # Validate against detected schema
                validation_result = schema_validator.validate_with_details(
                    data, detected_schema
                )

                if validation_result["valid"]:
                    click.echo(
                        f"✅ {file} is valid against {detected_schema} schema "
                        f"(auto-detected)."
                    )
                else:
                    click.echo(
                        f"❌ {file} failed validation against {detected_schema} schema:"
                    )
                    click.echo(f"   Error: {validation_result['error']}")
                    if validation_result.get("path"):
                        path_str = " -> ".join(
                            str(p) for p in validation_result["path"]
                        )
                        click.echo(f"   Path: {path_str}")
            else:
                # Manual schema checking if auto-detection fails
                available_schemas = schema_validator.get_available_schemas()
                validation_success = False

                click.echo(
                    "⚠️  Could not auto-detect schema. Trying all available schemas..."
                )

                for schema_type in available_schemas:
                    validation_result = schema_validator.validate_with_details(
                        data, schema_type
                    )

                    if validation_result["valid"]:
                        click.echo(f"✅ {file} is valid against {schema_type} schema.")
                        validation_success = True
                        break

                if not validation_success:
                    click.echo(f"❌ {file} does not match any known schema types.")
                    click.echo(
                        f"   Available schema types: {', '.join(available_schemas)}"
                    )

                    # Show similarity scores for debugging
                    click.echo("\n   Similarity analysis:")
                    for schema_type in available_schemas[:3]:  # Show top 3
                        score = schema_validator._calculate_structure_similarity(
                            data, schema_type
                        )
                        click.echo(f"   - {schema_type}: {score}% similarity")

    except (
        FileNotFoundError,
        ValueError,
        json.JSONDecodeError,
        jsonschema.exceptions.SchemaError,
    ) as e:
        symbolic_logger.log_error("validation_error", e)
        click.echo(f"❌ Error validating file: {str(e)}", err=True)


@utils_group.command(name="convert")
@click.argument("input_file", type=click.Path(exists=True))
@click.argument("output_format", type=click.Choice(["json", "csv", "yaml", "excel"]))
@click.option("--output", "-o", type=click.Path(), help="Output file")
def convert_file(input_file: str, output_format: str, output: Optional[str]):
    """Convert a file between formats."""
    try:
        # Load input file using ExportFormatter
        exporter = ExportFormatter()
        data = exporter.load_data(input_file)

        # Generate output filename if not provided
        if not output:
            output = str(Path(input_file).with_suffix(f".{output_format}"))

        # Export to new format
        output_file = exporter.export_data(data, output_format, Path(output).stem)

        click.echo(f"✅ Converted {input_file} to {output_file}")

    except (FileNotFoundError, ValueError, json.JSONDecodeError) as e:
        symbolic_logger.log_error("conversion_error", e)
        click.echo(f"❌ Error converting file: {str(e)}", err=True)


@cli.command(name="completion", help="Output shell completion code")
@click.argument("shell", type=click.Choice(["bash", "zsh", "fish"]))
def completion(shell: str):
    """Generate shell completion script."""
    # Modern Click 8.0+ uses built-in completion
    try:
        from click.shell_completion import get_completion_class

        completion_class = get_completion_class(shell)
        complete_var = "_RABBITMIRROR_COMPLETE"
        completion_instance = completion_class(cli, {}, "rabbitmirror", complete_var)

        # Generate completion script
        script = completion_instance.source()
        click.echo(script)
    except (ImportError, AttributeError) as e:
        click.echo(f"❌ Shell completion not available for {shell}: {e}", err=True)
        raise SystemExit(1)


@utils_group.command(name="generate-qr")
@click.argument("data", type=str)
@click.option("--output", "-o", type=click.Path(), help="Output file for QR code")
@click.option("--size", "-s", type=int, default=10, help="QR code size")
@click.option(
    "--error-correction", "-e", type=click.Choice(["L", "M", "Q", "H"]), default="M"
)
@click.option("--color", "-c", type=str, default="black", help="QR code color")
def generate_qr(
    data: str, output: Optional[str], size: int, error_correction: str, color: str
):
    """Generate a QR code for the given data."""
    try:
        generator = QRGenerator(
            size=size, error_correction=error_correction, color=color
        )
        qr_file = generator.generate_qr(
            data, filename=Path(output).stem if output else None
        )
        click.echo(f"✅ Generated QR code at {qr_file}")

    except (ValueError, OSError) as e:
        symbolic_logger.log_error("qr_generation_error", e)
        click.echo(f"❌ Error generating QR code: {str(e)}", err=True)


def main():
    # Modern Click 8.0+ has built-in completion support
    cli()


if __name__ == "__main__":
    main()
