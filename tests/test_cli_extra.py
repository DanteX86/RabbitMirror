import pytest
from click.testing import CliRunner

from rabbitmirror.cli import cli


def test_parse_command_unsupported_platform(tmp_path):
    # Create a tiny HTML file so the exists=True check passes
    html = tmp_path / "watch.html"
    html.write_text("<html><body><div class='content-cell'>x</div></body></html>")

    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "process",
            "parse",
            str(html),
            "nonexistent-platform",
            "--output",
            str(tmp_path / "out.json"),
        ],
    )
    assert result.exit_code == 1
    # Error message should mention unsupported platform from ParsingError
    assert "Unsupported platform" in result.output
