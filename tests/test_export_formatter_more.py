import json
from pathlib import Path

import pandas as pd
import pytest
import yaml

from rabbitmirror.exceptions import ExportError, FileOperationError, InvalidFormatError
from rabbitmirror.export_formatter import ExportFormatter


class TestExportFormatterMore:
    def test_load_data_json_yaml_csv(self, tmp_path: Path):
        # Prepare JSON
        json_path = tmp_path / "data.json"
        json_content = {"a": 1, "b": [1, 2, 3]}
        json_path.write_text(json.dumps(json_content), encoding="utf-8")

        # Prepare YAML
        yaml_path = tmp_path / "data.yaml"
        yaml_content = {"x": "y", "nums": [4, 5]}
        yaml_path.write_text(yaml.safe_dump(yaml_content), encoding="utf-8")

        # Prepare CSV
        csv_path = tmp_path / "data.csv"
        pd.DataFrame({"col1": [1, 2], "col2": ["a", "b"]}).to_csv(csv_path, index=False)

        ef = ExportFormatter(output_dir=str(tmp_path / "out"))

        loaded_json = ef.load_data(json_path)
        assert loaded_json == json_content

        loaded_yaml = ef.load_data(yaml_path)
        assert loaded_yaml == yaml_content

        loaded_csv = ef.load_data(csv_path)
        assert isinstance(loaded_csv, dict)
        assert "col1" in loaded_csv and "col2" in loaded_csv

    def test_load_data_errors(self, tmp_path: Path):
        ef = ExportFormatter(output_dir=str(tmp_path / "out"))

        # Unsupported extension
        txt_path = tmp_path / "data.txt"
        txt_path.write_text("hello", encoding="utf-8")
        with pytest.raises(InvalidFormatError):
            ef.load_data(txt_path)

        # Missing file
        with pytest.raises(FileOperationError):
            ef.load_data(tmp_path / "missing.json")

    def test_export_data_all_formats(self, tmp_path: Path):
        ef = ExportFormatter(output_dir=str(tmp_path / "exports"))
        data = {"entries": [{"a": 1, "b": "x"}, {"a": 2, "b": "y"}]}

        out_json = ef.export_data(data, "json", "testj")
        out_yaml = ef.export_data(data, "yaml", "testy")
        out_csv = ef.export_data(data, "csv", "testc")
        out_xlsx = ef.export_data(data, "excel", "teste")

        for p in [out_json, out_yaml, out_csv, out_xlsx]:
            assert Path(p).exists()

        # Unsupported export format
        with pytest.raises(ExportError):
            ef.export_data(data, "bogus", "name")
