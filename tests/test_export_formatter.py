import json
from pathlib import Path

import pandas as pd
import pytest
import yaml

from rabbitmirror.exceptions import ExportError, FileOperationError, InvalidFormatError
from rabbitmirror.export_formatter import ExportFormatter


@pytest.fixture
def sample_data():
    """Sample data for export testing."""
    return {
        "entries": [
            {
                "title": "Video1",
                "url": "http://example.com/1",
                "timestamp": "2025-07-01T10:00:00",
            },
            {
                "title": "Video2",
                "url": "http://example.com/2",
                "timestamp": "2025-07-01T11:00:00",
            },
        ]
    }


@pytest.fixture
def temp_export_dir(tmp_path):
    """Fixture providing a temporary export directory."""
    export_dir = tmp_path / "exports"
    export_dir.mkdir()
    return export_dir


class TestExportFormatter:
    """Test suite for the ExportFormatter class."""

    def test_export_json(self, sample_data, temp_export_dir):
        """Test JSON export functionality."""
        formatter = ExportFormatter(output_dir=temp_export_dir)
        filename = "test_output"
        output_path = formatter._export_json(sample_data, filename)

        assert Path(output_path).exists()
        assert Path(output_path).suffix == ".json"

        # Verify content
        with open(output_path, "r") as f:
            data = json.load(f)
            assert data == sample_data

    def test_export_yaml(self, sample_data, temp_export_dir):
        """Test YAML export functionality."""
        formatter = ExportFormatter(output_dir=temp_export_dir)
        filename = "test_output"
        output_path = formatter._export_yaml(sample_data, filename)

        assert Path(output_path).exists()
        assert Path(output_path).suffix == ".yaml"

        # Verify content
        with open(output_path, "r") as f:
            data = yaml.safe_load(f)
            assert data == sample_data

    def test_export_csv(self, sample_data, temp_export_dir):
        """Test CSV export functionality."""
        formatter = ExportFormatter(output_dir=temp_export_dir)
        filename = "test_output"
        output_path = formatter._export_csv(sample_data, filename)

        assert Path(output_path).exists()
        assert Path(output_path).suffix == ".csv"

        # Verify content
        df = pd.read_csv(output_path)
        assert df.shape[0] == len(sample_data["entries"])
        assert set(df.columns) == set(sample_data["entries"][0].keys())

    def test_export_excel(self, sample_data, temp_export_dir):
        """Test Excel export functionality."""
        formatter = ExportFormatter(output_dir=temp_export_dir)
        filename = "test_output"
        output_path = formatter._export_excel(sample_data, filename)

        assert Path(output_path).exists()
        assert Path(output_path).suffix == ".xlsx"

        # Verify content
        df = pd.read_excel(output_path, engine="openpyxl")
        assert df.shape[0] == len(sample_data["entries"])
        assert set(df.columns) == set(sample_data["entries"][0].keys())

    def test_unsupported_format(self, sample_data, temp_export_dir):
        """Test handling of unsupported export formats."""
        formatter = ExportFormatter(output_dir=temp_export_dir)
        filename = "test_output"

        with pytest.raises(ExportError, match="Unsupported export format"):
            formatter.export_data(sample_data, "unsupported_format", filename)

    def test_load_json_data(self, sample_data, temp_export_dir):
        """Test loading data from JSON file."""
        filename = temp_export_dir / "test_data.json"
        with open(filename, "w") as f:
            json.dump(sample_data, f)

        formatter = ExportFormatter()
        loaded_data = formatter.load_data(filename)

        assert loaded_data == sample_data

    def test_load_yaml_data(self, sample_data, temp_export_dir):
        """Test loading data from YAML file."""
        filename = temp_export_dir / "test_data.yaml"
        with open(filename, "w") as f:
            yaml.dump(sample_data, f)

        formatter = ExportFormatter()
        loaded_data = formatter.load_data(filename)

        assert loaded_data == sample_data

    def test_load_csv_data(self, sample_data, temp_export_dir):
        """Test loading data from CSV file."""
        filename = temp_export_dir / "test_data.csv"
        df = pd.DataFrame(sample_data["entries"])
        df.to_csv(filename, index=False)

        formatter = ExportFormatter()
        loaded_data = formatter.load_data(filename)

        assert len(loaded_data["title"]) == len(sample_data["entries"])
        assert set(loaded_data.keys()) == set(sample_data["entries"][0].keys())

    def test_invalid_file_format(self, temp_export_dir):
        """Test loading data from an invalid file format."""
        filename = temp_export_dir / "test_data.invalid"
        with open(filename, "w") as f:
            f.write("INVALID DATA")

        formatter = ExportFormatter()
        with pytest.raises(InvalidFormatError, match="Unsupported file format"):
            formatter.load_data(filename)

    def test_file_not_found(self):
        """Test loading data from a non-existent file."""
        formatter = ExportFormatter()
        with pytest.raises(FileOperationError, match="File not found"):
            formatter.load_data("nonexistent_file.json")

    def test_flatten_dict_method(self, temp_export_dir):
        """Test the _flatten_dict method with various nested structures."""
        formatter = ExportFormatter(output_dir=temp_export_dir)

        nested_dict = {
            "level1": {
                "level2": {"level3": "deep_value"},
                "simple_key": "simple_value",
            },
            "top_level": "top_value",
        }

        flat_dict = formatter._flatten_dict(nested_dict)

        expected = {
            "level1_level2_level3": "deep_value",
            "level1_simple_key": "simple_value",
            "top_level": "top_value",
        }

        assert flat_dict == expected

    def test_export_list_of_dicts(self, temp_export_dir):
        """Test exporting a list of dictionaries directly."""
        formatter = ExportFormatter(output_dir=temp_export_dir)

        list_data = [
            {"name": "Video 1", "views": 1000},
            {"name": "Video 2", "views": 2000},
        ]

        # CSV export
        output_csv = formatter._export_csv(list_data, "list_test")
        df_csv = pd.read_csv(output_csv)
        assert len(df_csv) == 2
        assert df_csv["name"].tolist() == ["Video 1", "Video 2"]

        # Excel export
        output_excel = formatter._export_excel(list_data, "list_excel_test")
        df_excel = pd.read_excel(output_excel)
        assert len(df_excel) == 2
        assert df_excel["views"].tolist() == [1000, 2000]

    def test_export_dict_of_lists(self, temp_export_dir):
        """Test exporting a dictionary where values are lists."""
        formatter = ExportFormatter(output_dir=temp_export_dir)

        dict_of_lists = {
            "names": ["Video 1", "Video 2"],
            "views": [1000, 2000],
            "categories": ["Tech", "Entertainment"],
        }

        output_csv = formatter._export_csv(dict_of_lists, "dict_lists_test")
        df = pd.read_csv(output_csv)
        assert len(df) == 2
        assert df["names"].tolist() == ["Video 1", "Video 2"]
        assert df["views"].tolist() == [1000, 2000]

    def test_export_complex_nested_data(self, temp_export_dir):
        """Test exporting complex nested data that requires flattening."""
        formatter = ExportFormatter(output_dir=temp_export_dir)

        complex_data = {
            "analysis": {
                "summary": {"total": 100, "unique": 50},
                "metrics": {"avg_duration": 5.5},
            },
            "simple_field": "value",
        }

        # This should trigger the flattening logic
        output_csv = formatter._export_csv(complex_data, "complex_test")
        df = pd.read_csv(output_csv)
        assert "analysis_summary_total" in df.columns
        assert "analysis_metrics_avg_duration" in df.columns
        assert "simple_field" in df.columns

    def test_load_excel_data(self, sample_data, temp_export_dir):
        """Test loading data from Excel file."""
        filename = temp_export_dir / "test_data.xlsx"
        df = pd.DataFrame(sample_data["entries"])
        df.to_excel(filename, index=False)

        formatter = ExportFormatter()
        loaded_data = formatter.load_data(filename)

        assert len(loaded_data["title"]) == len(sample_data["entries"])
        assert set(loaded_data.keys()) == set(sample_data["entries"][0].keys())

    def test_load_corrupted_json(self, temp_export_dir):
        """Test loading corrupted JSON file."""
        filename = temp_export_dir / "corrupted.json"
        with open(filename, "w") as f:
            f.write("{ invalid json }")

        formatter = ExportFormatter()
        with pytest.raises(InvalidFormatError, match="Invalid file format"):
            formatter.load_data(filename)

    def test_empty_data_export(self, temp_export_dir):
        """Test exporting empty data structures."""
        formatter = ExportFormatter(output_dir=temp_export_dir)

        # Test empty entries list
        empty_entries = {"entries": []}
        output_csv = formatter._export_csv(empty_entries, "empty_csv_test")

        # Empty CSV might not be readable by pandas, so just check file exists
        assert Path(output_csv).exists()

        output_excel = formatter._export_excel(empty_entries, "empty_excel_test")
        assert Path(output_excel).exists()
