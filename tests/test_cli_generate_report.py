from pathlib import Path

from click.testing import CliRunner

from rabbitmirror.cli import report_group


class TestGenerateReportCLI:
    def test_generate_report_happy_path(self, tmp_path: Path):
        # Prepare minimal template and data
        tmpl_dir = tmp_path / "templates"
        tmpl_dir.mkdir()
        template_file = tmpl_dir / "simple.html"
        template_file.write_text(
            "<html><body>{{ title }} - {{ items|length }}</body></html>",
            encoding="utf-8",
        )

        data_file = tmp_path / "data.json"
        data_file.write_text('{"title": "Report", "items": [1,2,3]}', encoding="utf-8")

        out_file = tmp_path / "out.html"

        runner = CliRunner()
        # Invoke the subcommand directly to avoid needing to pass through group parsing
        result = runner.invoke(
            report_group.commands["generate-report"],
            [str(data_file), str(template_file), str(out_file)],
        )

        assert result.exit_code == 0, result.output
        assert out_file.exists()
        content = out_file.read_text(encoding="utf-8")
        assert "Report" in content and "3" in content
