from pathlib import Path

from click.testing import CliRunner

from rabbitmirror.cli import report_group, utils_group


class TestCLIErrorBranches:
    def test_generate_report_invalid_json(self, tmp_path: Path):
        # Create invalid JSON file
        bad_json = tmp_path / "bad.json"
        bad_json.write_text("{ this is not json }", encoding="utf-8")
        # Create a template so path exists (won't be used due to early failure)
        tmpl = tmp_path / "tmpl.html"
        tmpl.write_text("template", encoding="utf-8")
        out = tmp_path / "out.html"

        runner = CliRunner()
        res = runner.invoke(
            report_group.commands["generate-report"],
            [str(bad_json), str(tmpl), str(out)],
        )
        # Should be handled by exception branch (no crash), exit code 0 because CLI prints error but doesn't raise SystemExit here
        assert res.exit_code == 0 or res.exit_code == 1
        assert "Error generating report" in res.output or "❌" in res.output

    def test_export_dashboard_invalid_format_file(self, tmp_path: Path):
        # Create a .txt file (unsupported by ExportFormatter)
        bad_file = tmp_path / "data.txt"
        bad_file.write_text("not supported format", encoding="utf-8")

        runner = CliRunner()
        res = runner.invoke(report_group.commands["export-dashboard"], [str(bad_file)])
        # Should print an error via exception branch
        assert res.exit_code == 0 or res.exit_code == 1
        assert "Error exporting dashboard" in res.output or "❌" in res.output

    def test_convert_cli_unsupported_format(self, tmp_path: Path):
        # Create unsupported file
        bad_file = tmp_path / "foo.txt"
        bad_file.write_text("x", encoding="utf-8")

        runner = CliRunner()
        res = runner.invoke(
            utils_group.commands["convert"],
            [str(bad_file), "json", "--output", str(tmp_path / "o.json")],
        )
        assert res.exit_code != 0 or "Error converting file" in res.output
