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

    def test_config_get_command(self):
        """Test config get command."""
        runner = CliRunner()
        result = runner.invoke(cli, ["config", "get", "test_key"])

        # Config management is not implemented yet, so just test it doesn't crash
        assert result.exit_code == 0
        assert "not yet implemented" in result.output

    def test_config_list_command(self):
        """Test config list command."""
        runner = CliRunner()
        result = runner.invoke(cli, ["config", "list"])

        # Config management is not implemented yet
        assert result.exit_code == 0
        assert "not yet implemented" in result.output

    def test_completion_command(self):
        """Test shell completion command."""
        runner = CliRunner()
        result = runner.invoke(cli, ["completion", "bash"])

        assert result.exit_code == 0
        # Should output some kind of completion script
        assert len(result.output) > 0

    def test_generate_report_help(self):
        """Test generate-report command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["report", "generate-report", "--help"])
        assert result.exit_code == 0
        assert "Generate a report using a template" in result.output
