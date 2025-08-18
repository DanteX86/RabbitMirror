import json
from pathlib import Path

from click.testing import CliRunner

from rabbitmirror.cli import config_group, utils_group


class TestEvenMoreCLICoverage:
    def test_config_set_and_get_local(self):
        runner = CliRunner()
        with runner.isolated_filesystem():
            # set a value
            res_set = runner.invoke(
                config_group.commands["set"],
                ["foo", "bar", "--local"],
            )
            assert res_set.exit_code == 0
            assert "Set foo = bar" in res_set.output

            # get the value
            res_get = runner.invoke(
                config_group.commands["get"],
                ["foo", "--local"],
            )
            assert res_get.exit_code == 0
            assert "foo = bar" in res_get.output

    def test_convert_json_to_yaml_success(self, tmp_path: Path):
        data = {"a": 1, "b": [1, 2, 3]}
        src = tmp_path / "data.json"
        src.write_text(json.dumps(data), encoding="utf-8")

        runner = CliRunner()
        res = runner.invoke(
            utils_group.commands["convert"],
            [str(src), "yaml", "-o", str(tmp_path / "out.yaml")],
        )
        assert res.exit_code == 0
        assert "Converted" in res.output or "✅" in res.output

    def test_validate_auto_detect_fallback(self, tmp_path: Path):
        # Create a JSON file that likely doesn't match known schemas to exercise fallback path
        src = tmp_path / "weird.json"
        src.write_text(
            json.dumps({"weird": True, "data": [1, {"x": "y"}]}), encoding="utf-8"
        )
        runner = CliRunner()
        res = runner.invoke(
            utils_group.commands["validate"],
            [str(src), "--format", "json"],
        )
        # Should either validate against some schema or go through fallback with messages; ensure no crash
        assert res.exit_code in (0, 1)
        assert res.output.strip() != ""
