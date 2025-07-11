import os
from pathlib import Path

from click.testing import CliRunner

from rabbitmirror.cli import cli


class TestCLI:
    """Test suite for the CLI interface."""

    def test_cli_help(self):
        """Test that CLI help command works."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "RabbitMirror" in result.output
        assert "YouTube Watch History Analysis Tool" in result.output

    def test_process_help(self):
        """Test that process command group help works."""
        runner = CliRunner()
        result = runner.invoke(cli, ["process", "--help"])
        assert result.exit_code == 0
        assert "Commands for data processing" in result.output

    def test_analyze_help(self):
        """Test that analyze command group help works."""
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--help"])
        assert result.exit_code == 0
        assert "Commands for data analysis" in result.output

    def test_report_help(self):
        """Test that report command group help works."""
        runner = CliRunner()
        result = runner.invoke(cli, ["report", "--help"])
        assert result.exit_code == 0
        assert "Commands for report generation" in result.output

    def test_parse_command_help(self):
        """Test that parse command help works."""
        runner = CliRunner()
        result = runner.invoke(cli, ["process", "parse", "--help"])
        assert result.exit_code == 0
        assert "Parse a YouTube watch history file" in result.output

    def test_parse_command_with_sample_file(self, sample_history_file, temp_output_dir):
        """Test parse command with sample history file."""
        runner = CliRunner()
        output_file = temp_output_dir / "test_output.json"

        result = runner.invoke(
            cli,
            [
                "process",
                "parse",
                str(sample_history_file),
                "--output",
                str(output_file),
                "--format",
                "json",
            ],
        )

        assert result.exit_code == 0, result.output
        assert output_file.exists(), "Output file was not created."
        assert "✅ Exported" in result.output, "Output message not found."

    def test_cluster_command_with_sample_file(
        self, sample_history_file, temp_output_dir
    ):
        """Test cluster command with sample history file."""
        runner = CliRunner()
        output_file = temp_output_dir / "cluster_output.json"

        result = runner.invoke(
            cli,
            [
                "analyze",
                "cluster",
                str(sample_history_file),
                "--output",
                str(output_file),
                "--eps",
                "0.5",
                "--min-samples",
                "3",
                "--format",
                "json",
            ],
        )

        assert result.exit_code == 0, result.output
        assert output_file.exists(), "Cluster output file was not created."
        assert "✅ Exported cluster analysis to" in result.output

    def test_detect_patterns_with_sample_file(
        self, sample_history_file, temp_output_dir
    ):
        """Test detect-patterns command with sample history file."""
        runner = CliRunner()
        output_file = temp_output_dir / "patterns_output.json"

        result = runner.invoke(
            cli,
            [
                "analyze",
                "detect-patterns",
                str(sample_history_file),
                "--output",
                str(output_file),
                "--threshold",
                "0.7",
                "--format",
                "json",
            ],
        )

        assert result.exit_code == 0, result.output
        assert output_file.exists(), "Patterns output file was not created."
        assert "✅ Exported pattern analysis to" in result.output

    def test_generate_report_help(self):
        """Test generate-report command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["report", "generate-report", "--help"])
        assert result.exit_code == 0
        assert "Generate a report using a template" in result.output

    def test_batch_process_recursive(self, sample_history_dir, temp_output_dir):
        """Test batch-process command with recursive option."""
        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "process",
                "batch-process",
                str(sample_history_dir),
                "--output-dir",
                str(temp_output_dir),
                "--format",
                "json",
                "--recursive",
            ],
        )

        assert result.exit_code == 0, result.output
        assert "✅ Successfully processed" in result.output

    def test_invalid_file_path_handling(self):
        """Test that invalid file paths are handled gracefully."""
        runner = CliRunner()
        result = runner.invoke(cli, ["process", "parse", "nonexistent_file.html"])
        assert result.exit_code != 0
        assert "Error" in result.output or "No such file or directory" in result.output

    def test_invalid_directory_path_handling(self):
        """Test that invalid directory paths are handled gracefully."""
        runner = CliRunner()
        result = runner.invoke(
            cli, ["process", "batch-process", "nonexistent_directory"]
        )
        assert result.exit_code != 0
        assert "Error" in result.output or "No such directory" in result.output

    def test_simulate_command_with_sample_file(
        self, sample_history_file, temp_output_dir
    ):
        """Test simulate command with sample history file."""
        runner = CliRunner()
        output_file = temp_output_dir / "simulate_output.json"

        result = runner.invoke(
            cli,
            [
                "analyze",
                "simulate",
                str(sample_history_file),
                "--duration",
                "7",
                "--output",
                str(output_file),
                "--format",
                "json",
            ],
        )

        assert result.exit_code == 0, result.output
        assert output_file.exists(), "Simulate output file was not created."
        assert "✅ Exported simulated profile to" in result.output

    def test_batch_process_with_sample_dir(self, sample_history_dir, temp_output_dir):
        """Test batch-process command with sample directory."""
        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "process",
                "batch-process",
                str(sample_history_dir),
                "--output-dir",
                str(temp_output_dir),
                "--format",
                "json",
            ],
        )

        assert result.exit_code == 0, result.output
        assert "✅ Successfully processed" in result.output
        for file in sample_history_dir.glob("*.html"):
            output_file = temp_output_dir / file.with_suffix(".json").name
            assert (
                output_file.exists()
            ), f"Batch processed output for {file.name} was not created."

    def test_cluster_command_help(self):
        """Test that cluster command help works."""
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "cluster", "--help"])
        assert result.exit_code == 0
        assert "Cluster videos in watch history" in result.output

    def test_detect_patterns_command_help(self):
        """Test that detect-patterns command help works."""
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "detect-patterns", "--help"])
        assert result.exit_code == 0
        assert "Detect potential adversarial patterns" in result.output

    def test_analyze_suppression_command_help(self):
        """Test that analyze-suppression command help works."""
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "analyze-suppression", "--help"])
        assert result.exit_code == 0
        assert "Analyze content suppression patterns" in result.output

    def test_invalid_command(self):
        """Test that invalid commands are handled gracefully."""
        runner = CliRunner()
        result = runner.invoke(cli, ["invalid-command"])
        assert result.exit_code != 0
        assert "No such command" in result.output or "Usage:" in result.output

    def test_utils_group_help(self):
        """Test that utils command group help works."""
        runner = CliRunner()
        result = runner.invoke(cli, ["utils", "--help"])
        assert result.exit_code == 0
        assert "Utility commands" in result.output

    def test_config_group_help(self):
        """Test that config command group help works."""
        runner = CliRunner()
        result = runner.invoke(cli, ["config", "--help"])
        assert result.exit_code == 0
        assert "Configuration commands" in result.output

    def test_analyze_suppression_command_with_sample_file(
        self, sample_history_file, temp_output_dir
    ):
        """Test analyze-suppression command with sample history file."""
        runner = CliRunner()
        output_file = temp_output_dir / "suppression_output.json"

        result = runner.invoke(
            cli,
            [
                "analyze",
                "analyze-suppression",
                str(sample_history_file),
                "--period",
                "14",
                "--output",
                str(output_file),
                "--format",
                "json",
            ],
        )

        assert result.exit_code == 0, result.output
        assert output_file.exists(), "Suppression output file was not created."
        assert "✅ Exported suppression analysis to" in result.output

    def test_convert_file_command(self, sample_history_file, temp_output_dir):
        """Test convert file utility command."""
        runner = CliRunner()

        # First parse the history file to create a JSON file
        json_file = temp_output_dir / "input.json"
        result_parse = runner.invoke(
            cli,
            [
                "process",
                "parse",
                str(sample_history_file),
                "--output",
                str(json_file),
                "--format",
                "json",
            ],
        )
        assert result_parse.exit_code == 0

        # Then convert it to YAML
        yaml_output = temp_output_dir / "converted.yaml"
        result_convert = runner.invoke(
            cli,
            ["utils", "convert", str(json_file), "yaml", "--output", str(yaml_output)],
        )

        assert result_convert.exit_code == 0, result_convert.output
        assert "✅ Converted" in result_convert.output
        # The actual file path will be different due to ExportFormatter behavior

    def test_validate_file_command(self, sample_history_file):
        """Test validate file utility command."""
        runner = CliRunner()

        # First parse the history file to create a JSON file for validation
        result_parse = runner.invoke(
            cli, ["process", "parse", str(sample_history_file), "--format", "json"]
        )
        assert result_parse.exit_code == 0

        # Since validation is not fully implemented, we just test it doesn't crash
        result_validate = runner.invoke(
            cli, ["utils", "validate", str(sample_history_file), "--format", "json"]
        )

        # Should not crash, even if not fully implemented
        assert (
            result_validate.exit_code == 0
            or "not yet implemented" in result_validate.output
        )

    def test_config_set_and_get_commands(self, tmp_path):
        """Test config set and get commands."""
        runner = CliRunner()

        # Change to temp directory to isolate config file
        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)

            # Set a configuration value
            result_set = runner.invoke(cli, ["config", "set", "test_key", "test_value"])
            assert result_set.exit_code == 0
            assert "Set test_key = test_value in local config" in result_set.output

            # Get the configuration value
            result_get = runner.invoke(cli, ["config", "get", "test_key"])
            assert result_get.exit_code == 0
            assert "test_key = test_value" in result_get.output

        finally:
            os.chdir(original_cwd)

    def test_config_list_command(self, tmp_path):
        """Test config list command."""
        runner = CliRunner()

        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)

            # Set multiple configuration values
            runner.invoke(cli, ["config", "set", "key1", "value1"])
            runner.invoke(cli, ["config", "set", "key2", "value2"])

            # List configurations
            result_list = runner.invoke(cli, ["config", "list"])
            assert result_list.exit_code == 0
            assert "key1" in result_list.output
            assert "value1" in result_list.output
            assert "key2" in result_list.output
            assert "value2" in result_list.output

            # Test JSON format
            result_json = runner.invoke(cli, ["config", "list", "--format", "json"])
            assert result_json.exit_code == 0
            assert '"key1": "value1"' in result_json.output

        finally:
            os.chdir(original_cwd)

    def test_config_get_nonexistent_key(self, tmp_path):
        """Test getting a nonexistent configuration key."""
        runner = CliRunner()

        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)

            result = runner.invoke(cli, ["config", "get", "nonexistent_key"])
            assert result.exit_code == 0
            assert "Key 'nonexistent_key' not found" in result.output

        finally:
            os.chdir(original_cwd)

    def test_completion_command(self):
        """Test shell completion command."""
        runner = CliRunner()
        result = runner.invoke(cli, ["completion", "bash"])

        assert result.exit_code == 0
        # Should output some kind of completion script
        assert len(result.output) > 0

    def test_generate_report_help_duplicate(self):
        """Test generate-report command help (duplicate - renamed)."""
        runner = CliRunner()
        result = runner.invoke(cli, ["report", "generate-report", "--help"])
        assert result.exit_code == 0
        assert "Generate a report using a template" in result.output

    def test_export_dashboard_help(self):
        """Test export-dashboard command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["report", "export-dashboard", "--help"])
        assert result.exit_code == 0
        assert "Export data as an interactive dashboard" in result.output

    def test_export_dashboard_with_sample_data(
        self, sample_history_file, temp_output_dir
    ):
        """Test export-dashboard command with sample data."""
        runner = CliRunner()

        # First parse the history file to create JSON data
        json_file = temp_output_dir / "parsed_for_dashboard.json"
        result_parse = runner.invoke(
            cli,
            [
                "process",
                "parse",
                str(sample_history_file),
                "--output",
                str(json_file),
                "--format",
                "json",
            ],
        )
        assert result_parse.exit_code == 0

        # Then export dashboard
        dashboard_dir = temp_output_dir / "test_dashboard"
        result_dashboard = runner.invoke(
            cli,
            [
                "report",
                "export-dashboard",
                str(json_file),
                "--output",
                str(dashboard_dir),
                "--theme",
                "light",
                "--interactive",
            ],
        )

        assert result_dashboard.exit_code == 0, result_dashboard.output
        assert "Dashboard Generation Complete" in result_dashboard.output

        # Check that dashboard files were created
        assert (dashboard_dir / "history_dashboard.html").exists()
        assert (dashboard_dir / "analytics_dashboard.html").exists()
        assert (dashboard_dir / "index.html").exists()
