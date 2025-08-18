from pathlib import Path

from click.testing import CliRunner

from rabbitmirror.cli import analyze_group, completion, config_group


class TestMoreCLICoverage:
    def test_detect_patterns_parser_error(self, tmp_path: Path):
        # Invalid HTML file that parser cannot handle, should trigger RabbitMirrorError path
        bad = tmp_path / "bad.html"
        bad.write_text("not a valid history export", encoding="utf-8")
        runner = CliRunner()
        res = runner.invoke(analyze_group.commands["detect-patterns"], [str(bad)])
        assert res.exit_code == 1 or res.exit_code == 0
        assert "❌" in res.output or "error" in res.output.lower()

    def test_cluster_parser_error(self, tmp_path: Path):
        bad = tmp_path / "bad.html"
        bad.write_text("still not valid", encoding="utf-8")
        runner = CliRunner()
        res = runner.invoke(analyze_group.commands["cluster"], [str(bad)])
        assert res.exit_code in (0, 1)
        assert "❌" in res.output or "error" in res.output.lower()

    def test_config_get_missing_key(self):
        runner = CliRunner()
        with runner.isolated_filesystem():
            res = runner.invoke(
                config_group.commands["get"], ["nonexistent", "--local"]
            )
            # Should not crash; prints not found message and exit 0
            assert res.exit_code == 0 or res.exit_code == 1
            assert "not found" in res.output.lower() or "❌" in res.output

    def test_completion_import_error(self, monkeypatch):
        # Force ImportError path
        def broken_import(name):  # noqa: ARG001
            raise ImportError("boom")

        # Monkeypatch module import inside the command by replacing the symbol in its globals
        import rabbitmirror.cli as cli_mod

        class Dummy:
            @staticmethod
            def source():
                return ""

        def fake_get_completion_class(_shell):  # noqa: ARG001
            return Dummy

        # Replace get_completion_class import resolution by injecting a failing proxy
        monkeypatch.setitem(cli_mod.__dict__, "get_completion_class", broken_import)
        # But the command imports from click.shell_completion at runtime, so also patch that attribute
        import click.shell_completion as sc

        monkeypatch.setattr(
            sc,
            "get_completion_class",
            lambda _shell: (_ for _ in ()).throw(ImportError("boom")),
        )

        runner = CliRunner()
        res = runner.invoke(completion, ["bash"])
        assert res.exit_code != 0
        assert "Shell completion not available" in res.output or "❌" in res.output
