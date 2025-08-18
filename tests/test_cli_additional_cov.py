import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from rabbitmirror.cli import (
    completion,
    config_group,
    process_group,
    utils_group,
)


class TestAdditionalCLIForCoverage:
    def test_completion_success_output(self):
        runner = CliRunner()
        res = runner.invoke(completion, ["bash"])  # happy path
        assert res.exit_code == 0
        assert res.output.strip() != ""

    def test_completion_get_class_error(self, monkeypatch):
        runner = CliRunner()

        # Force the internal get_completion_class to raise AttributeError
        import click.shell_completion as sc  # import here to monkeypatch

        def boom(_shell):  # noqa: ARG001
            raise AttributeError("no completion for this shell")

        monkeypatch.setattr(sc, "get_completion_class", boom)

        res = runner.invoke(completion, ["bash"])  # valid option, but patched to fail
        # Should exit with error and print a helpful message
        assert res.exit_code != 0
        assert "Shell completion not available" in res.output or "❌" in res.output

    def test_validate_invalid_schema_json_decode(self, tmp_path: Path):
        data = tmp_path / "data.json"
        data.write_text(json.dumps({"x": 1}), encoding="utf-8")
        bad_schema = tmp_path / "schema.json"
        bad_schema.write_text("{ not: valid json }", encoding="utf-8")

        runner = CliRunner()
        # --format controls how files are parsed internally
        res = runner.invoke(
            utils_group.commands["validate"],
            [str(data), "--schema", str(bad_schema), "--format", "json"],
        )
        # Command should handle error and not crash
        assert res.exit_code == 0 or res.exit_code == 1
        assert "Error validating file" in res.output or "❌" in res.output

    def test_validate_schema_error_invalid_structure(self, tmp_path: Path):
        data = tmp_path / "data.json"
        data.write_text(json.dumps({"x": 1}), encoding="utf-8")
        # syntactically valid but invalid as a JSON Schema (unknown type)
        invalid_schema = tmp_path / "schema.json"
        invalid_schema.write_text(
            json.dumps({"type": "definitely-not-valid"}), encoding="utf-8"
        )

        runner = CliRunner()
        res = runner.invoke(
            utils_group.commands["validate"],
            [str(data), "--schema", str(invalid_schema), "--format", "json"],
        )
        # Should be caught by SchemaError branch and printed as a validation error
        assert res.exit_code == 0 or res.exit_code == 1
        assert "Error validating file" in res.output or "❌" in res.output

    def test_convert_unsupported_input_format(self, tmp_path: Path):
        runner = CliRunner()
        # Create a file with an unsupported extension so ExportFormatter.load_data fails
        bad = tmp_path / "data.txt"
        bad.write_text("not supported", encoding="utf-8")
        res = runner.invoke(
            utils_group.commands["convert"],
            [str(bad), "yaml"],
        )
        assert res.exit_code == 0 or res.exit_code == 1
        assert "Error converting file" in res.output or "❌" in res.output

    def test_config_list_json_format(self, tmp_path: Path, monkeypatch):
        # Run in an isolated directory to avoid touching user configs
        runner = CliRunner()
        with runner.isolated_filesystem():
            res = runner.invoke(
                config_group.commands["list"],
                ["--format", "json", "--local"],
            )
            assert res.exit_code == 0
            # Should print some JSON-like string (could be empty dict depending on environment)
            assert res.output.strip() != ""

    def test_parse_unsupported_platform(self, tmp_path: Path):
        history = tmp_path / "dummy.html"
        history.write_text("<html></html>", encoding="utf-8")
        runner = CliRunner()
        res = runner.invoke(
            process_group.commands["parse"],
            [str(history), "unknown"],
        )
        assert res.exit_code == 1
        assert "❌" in res.output or "error" in res.output.lower()

    def test_batch_process_no_files(self, tmp_path: Path):
        runner = CliRunner()
        res = runner.invoke(
            process_group.commands["batch-process"],
            [str(tmp_path)],
        )
        assert res.exit_code == 0
        assert "No history files found" in res.output

    def test_generate_qr_invalid_color(self):
        runner = CliRunner()
        res = runner.invoke(
            utils_group.commands["generate-qr"],
            ["some-data", "--color", "notacolor"],
        )
        # Should hit ValueError branch
        assert res.exit_code == 0 or res.exit_code == 1
        assert "Error generating QR code" in res.output or "❌" in res.output
