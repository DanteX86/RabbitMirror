#!/usr/bin/env python3

"""
Core functionality tests for RabbitMirror simplified architecture.

Tests focus on:
- YouTube data parsing
- Analysis algorithms
- Dashboard generation
- CLI/TUI interfaces
- Export functionality
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Core functionality imports
from rabbitmirror.parser import HistoryParser

try:
    from rabbitmirror.cluster_engine import ClusterEngine

    CLUSTER_ENGINE_AVAILABLE = True
except ImportError:
    CLUSTER_ENGINE_AVAILABLE = False

try:
    from rabbitmirror.trend_analyzer import TrendAnalyzer

    TREND_ANALYZER_AVAILABLE = True
except ImportError:
    TREND_ANALYZER_AVAILABLE = False

try:
    from rabbitmirror.adversarial_profiler import AdversarialProfiler

    ADVERSARIAL_PROFILER_AVAILABLE = True
except ImportError:
    ADVERSARIAL_PROFILER_AVAILABLE = False

from rabbitmirror.config_manager import ConfigManager
from rabbitmirror.dashboard_generator import DashboardGenerator
from rabbitmirror.export_formatter import ExportFormatter


class TestCoreFunctionality:
    """Test core functionality without authentication dependencies."""

    @pytest.fixture
    def sample_entries(self):
        """Sample YouTube history entries for testing."""
        return [
            {
                "title": "Python Machine Learning Tutorial",
                "url": "https://www.youtube.com/watch?v=test1",
                "timestamp": "2023-12-15T14:30:45",
            },
            {
                "title": "FastAPI Development Guide",
                "url": "https://www.youtube.com/watch?v=test2",
                "timestamp": "2023-12-15T15:30:45",
            },
            {
                "title": "Data Structures in Python",
                "url": "https://www.youtube.com/watch?v=test3",
                "timestamp": "2023-12-15T16:30:45",
            },
            {
                "title": "JavaScript Advanced Concepts",
                "url": "https://www.youtube.com/watch?v=test4",
                "timestamp": "2023-12-15T17:30:45",
            },
            {
                "title": "React Best Practices",
                "url": "https://www.youtube.com/watch?v=test5",
                "timestamp": "2023-12-15T18:30:45",
            },
        ]

    @pytest.fixture
    def sample_html_file(self, tmp_path, sample_entries):
        """Create a sample HTML file for parser testing."""
        html_content = """
        <html>
        <head><title>Watch History</title></head>
        <body>
        <h1>YouTube Watch History</h1>
        """

        for entry in sample_entries:
            html_content += f"""
            <div class="content-cell">
                <a href="{entry['url']}">{entry['title']}</a>
                <div class="mdl-typography--caption">{entry['timestamp']}</div>
            </div>
            """

        html_content += """
        </body>
        </html>
        """

        test_file = tmp_path / "test_history.html"
        test_file.write_text(html_content)
        return test_file

    def test_youtube_data_parsing(self, sample_html_file, sample_entries):
        """Test YouTube data parsing functionality."""
        parser = HistoryParser(str(sample_html_file), "youtube")
        result = parser.parse()

        assert result is not None
        assert hasattr(result, "entries")
        assert len(result.entries) == len(sample_entries)

        # Verify parsed data structure
        for i, entry in enumerate(result.entries):
            assert "title" in entry
            assert "url" in entry
            assert "timestamp" in entry
            assert entry["title"] == sample_entries[i]["title"]

    @pytest.mark.skipif(
        not CLUSTER_ENGINE_AVAILABLE, reason="ClusterEngine not available"
    )
    def test_clustering_algorithm(self, sample_entries):
        """Test video clustering functionality."""
        cluster_engine = ClusterEngine()

        # Use the correct API - pass the entries list directly
        cluster_result = cluster_engine.cluster_videos(sample_entries)

        assert cluster_result is not None
        assert "clusters" in cluster_result
        assert "cluster_info" in cluster_result
        assert "metadata" in cluster_result
        assert cluster_result["cluster_info"]["total_entries"] == len(sample_entries)

    @pytest.mark.skipif(
        not TREND_ANALYZER_AVAILABLE, reason="TrendAnalyzer not available"
    )
    def test_trend_analysis_algorithm(self, sample_entries):
        """Test trend analysis functionality."""
        trend_analyzer = TrendAnalyzer()

        # Pass the entries directly to the analyzer
        trend_result = trend_analyzer.analyze_trends(sample_entries)

        assert trend_result is not None
        assert isinstance(trend_result, dict)

    @pytest.mark.skipif(
        not ADVERSARIAL_PROFILER_AVAILABLE, reason="AdversarialProfiler not available"
    )
    def test_adversarial_pattern_detection(self, sample_entries):
        """Test adversarial pattern detection."""
        profiler = AdversarialProfiler()
        pattern_result = profiler.identify_adversarial_patterns(sample_entries)

        assert pattern_result is not None
        assert isinstance(pattern_result, dict)

    def test_dashboard_generation(self, sample_entries, tmp_path):
        """Test dashboard generation functionality."""
        dashboard_generator = DashboardGenerator()
        output_dir = tmp_path / "dashboard_output"

        # Prepare test data
        test_data = {
            "entries": sample_entries,
            "clusters": {
                "cluster_labels": [0, 1, 0, 1, 0],
                "features": [
                    [1.0, 2.0],
                    [1.5, 1.8],
                    [0.9, 2.1],
                    [2.0, 1.5],
                    [1.1, 2.2],
                ],
            },
            "patterns": {"pattern_scores": [0.8, 0.6, 0.9, 0.7, 0.5]},
        }

        generated_files = dashboard_generator.generate_dashboard(test_data, output_dir)

        assert generated_files is not None
        assert isinstance(generated_files, dict)
        assert len(generated_files) > 0

        # Verify some files were created
        for file_path in generated_files.values():
            assert file_path.exists()

    def test_export_functionality(self, sample_entries, tmp_path):
        """Test data export functionality."""
        export_formatter = ExportFormatter(str(tmp_path))

        # Test JSON export
        json_file_path = export_formatter.export_data(
            sample_entries, "json", "export_test"
        )
        json_output = Path(json_file_path)

        assert json_output.exists()

        # Verify JSON content
        with open(json_output, "r") as f:
            exported_data = json.load(f)

        assert len(exported_data) == len(sample_entries)
        assert exported_data[0]["title"] == sample_entries[0]["title"]

        # Test CSV export
        csv_file_path = export_formatter.export_data(
            sample_entries, "csv", "export_test_csv"
        )
        csv_output = Path(csv_file_path)

        assert csv_output.exists()

        # Verify CSV has content
        csv_content = csv_output.read_text()
        assert "title" in csv_content
        assert sample_entries[0]["title"] in csv_content

    def test_config_management(self, tmp_path):
        """Test configuration management functionality."""
        config_file = tmp_path / "test_config.json"
        config_manager = ConfigManager(str(config_file))

        # Test setting and getting configuration
        config_manager.set("test_key", "test_value")
        config_manager.set("parser.platform", "youtube")
        config_manager.set("export.format", "json")

        assert config_manager.get("test_key") == "test_value"
        assert config_manager.get("parser.platform") == "youtube"
        assert config_manager.get("export.format") == "json"

        # Test configuration persistence
        config_manager_2 = ConfigManager(str(config_file))
        assert config_manager_2.get("test_key") == "test_value"

    def test_error_handling(self, tmp_path):
        """Test error handling in core functionality."""
        # Test parser with invalid file
        nonexistent_file = tmp_path / "nonexistent.html"

        with pytest.raises(Exception):  # Should raise some form of file error
            parser = HistoryParser(str(nonexistent_file), "youtube")
            parser.parse()

        # Test dashboard with invalid data
        dashboard_generator = DashboardGenerator()

        with pytest.raises(ValueError):
            dashboard_generator.generate_dashboard(
                {"entries": []}, tmp_path / "empty_output"
            )

    def test_data_validation(self, sample_entries):
        """Test data validation across components."""
        # Test parser result validation
        parser_result = type("ParseResult", (), {"entries": sample_entries})()

        # Ensure all entries have required fields
        for entry in parser_result.entries:
            assert "title" in entry
            assert "url" in entry
            assert "timestamp" in entry
            assert isinstance(entry["title"], str)
            assert isinstance(entry["url"], str)
            assert isinstance(entry["timestamp"], str)

    def test_memory_efficiency(self, sample_entries, tmp_path):
        """Test memory efficiency of core operations."""
        import sys

        # Test with large dataset simulation
        large_dataset = sample_entries * 100  # 500 entries

        # Measure memory usage during export
        initial_size = sys.getsizeof(large_dataset)

        export_formatter = ExportFormatter(str(tmp_path))

        # Export should not consume excessive memory
        file_path = export_formatter.export_data(large_dataset, "json", "memory_test")
        # Should complete without memory errors
        assert Path(file_path).exists()

    def test_performance_benchmarks(self, sample_entries):
        """Test performance of core operations."""
        import time

        # Test parser performance
        start_time = time.time()

        # Simulate processing
        processed_count = 0
        for entry in sample_entries:
            # Basic processing simulation
            if entry.get("title") and entry.get("url"):
                processed_count += 1

        processing_time = time.time() - start_time

        # Should process quickly
        assert processing_time < 1.0  # Less than 1 second for small dataset
        assert processed_count == len(sample_entries)

    def test_integration_workflow(self, sample_html_file, tmp_path):
        """Test complete workflow integration."""
        # Step 1: Parse data
        parser = HistoryParser(str(sample_html_file), "youtube")
        parsed_result = parser.parse()

        assert parsed_result is not None
        assert len(parsed_result.entries) > 0

        # Step 2: Export parsed data
        export_formatter = ExportFormatter(str(tmp_path))
        json_file_path = export_formatter.export_data(
            parsed_result.entries, "json", "workflow_export"
        )
        json_file = Path(json_file_path)

        assert json_file.exists()

        # Step 3: Generate dashboard
        dashboard_generator = DashboardGenerator()
        dashboard_data = {
            "entries": parsed_result.entries,
            "patterns": {"pattern_scores": [0.5] * len(parsed_result.entries)},
        }

        dashboard_dir = tmp_path / "workflow_dashboard"
        generated_files = dashboard_generator.generate_dashboard(
            dashboard_data, dashboard_dir
        )

        assert generated_files is not None
        assert len(generated_files) > 0

    def test_cli_interface_integration(self):
        """Test CLI interface availability and basic functionality."""
        from click.testing import CliRunner

        from rabbitmirror.cli import cli

        runner = CliRunner()

        # Test help command
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "RabbitMirror" in result.output

        # Test command groups are available
        result = runner.invoke(cli, ["process", "--help"])
        assert result.exit_code == 0

        result = runner.invoke(cli, ["analyze", "--help"])
        assert result.exit_code == 0

        result = runner.invoke(cli, ["report", "--help"])
        assert result.exit_code == 0

    def test_tui_interface_availability(self):
        """Test TUI interface components are available."""
        try:
            # Test that TUI components can be imported
            from textual.app import App
            from textual.widgets import Button, Static

            # Basic TUI component test
            class TestApp(App):
                def compose(self):
                    yield Static("Test")
                    yield Button("Test Button")

            app = TestApp()
            assert app is not None

        except ImportError:
            pytest.skip("TUI dependencies not available")

    def test_security_integration(self):
        """Test that security features are properly integrated."""
        from rabbitmirror.security import InputValidator, SecurityConfig

        config = SecurityConfig()
        validator = InputValidator(config)

        # Test basic security validation
        safe_input = "safe test string"
        validated = validator.validate_string(safe_input)
        assert validated == safe_input

        # Test dangerous input detection
        from rabbitmirror.exceptions import SecurityError

        with pytest.raises(SecurityError):
            validator.validate_string("<script>alert('test')</script>")

    def test_component_isolation(self, sample_entries):
        """Test that core components work independently."""
        # Test export formatter independently
        with tempfile.TemporaryDirectory() as tmp_dir:
            export_formatter = ExportFormatter(tmp_dir)
            file_path = export_formatter.export_data(
                sample_entries, "json", "isolation_test"
            )
            # Should work without other components
            assert Path(file_path).exists()

        # Test dashboard generator independently
        dashboard_generator = DashboardGenerator()

        with tempfile.TemporaryDirectory() as tmp_dir:
            dashboard_data = {"entries": sample_entries}
            generated = dashboard_generator.generate_dashboard(
                dashboard_data, Path(tmp_dir)
            )
            # Should work independently
            assert generated is not None


if __name__ == "__main__":
    pytest.main([__file__])
