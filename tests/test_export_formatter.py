import pytest
import json
import yaml
import pandas as pd
from pathlib import Path
from rabbitmirror.export_formatter import ExportFormatter


@pytest.fixture
def sample_data():
    """Sample data for export testing."""
    return {
        'entries': [
            {'title': 'Video1', 'url': 'http://example.com/1', 'timestamp': '2025-07-01T10:00:00'},
            {'title': 'Video2', 'url': 'http://example.com/2', 'timestamp': '2025-07-01T11:00:00'}
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
        assert Path(output_path).suffix == '.json'
        
        # Verify content
        with open(output_path, 'r') as f:
            data = json.load(f)
            assert data == sample_data
    
    def test_export_yaml(self, sample_data, temp_export_dir):
        """Test YAML export functionality."""
        formatter = ExportFormatter(output_dir=temp_export_dir)
        filename = "test_output"
        output_path = formatter._export_yaml(sample_data, filename)
        
        assert Path(output_path).exists()
        assert Path(output_path).suffix == '.yaml'
        
        # Verify content
        with open(output_path, 'r') as f:
            data = yaml.safe_load(f)
            assert data == sample_data

    def test_export_csv(self, sample_data, temp_export_dir):
        """Test CSV export functionality."""
        formatter = ExportFormatter(output_dir=temp_export_dir)
        filename = "test_output"
        output_path = formatter._export_csv(sample_data, filename)
        
        assert Path(output_path).exists()
        assert Path(output_path).suffix == '.csv'
        
        # Verify content
        df = pd.read_csv(output_path)
        assert df.shape[0] == len(sample_data['entries'])
        assert set(df.columns) == set(sample_data['entries'][0].keys())
    
    def test_export_excel(self, sample_data, temp_export_dir):
        """Test Excel export functionality."""
        formatter = ExportFormatter(output_dir=temp_export_dir)
        filename = "test_output"
        output_path = formatter._export_excel(sample_data, filename)
        
        assert Path(output_path).exists()
        assert Path(output_path).suffix == '.xlsx'
        
        # Verify content
        df = pd.read_excel(output_path, engine='openpyxl')
        assert df.shape[0] == len(sample_data['entries'])
        assert set(df.columns) == set(sample_data['entries'][0].keys())
    
    def test_unsupported_format(self, sample_data, temp_export_dir):
        """Test handling of unsupported export formats."""
        formatter = ExportFormatter(output_dir=temp_export_dir)
        filename = "test_output"
        
        with pytest.raises(ValueError, match="Unsupported export format"):
            formatter.export_data(sample_data, 'unsupported_format', filename)
    
    def test_load_json_data(self, sample_data, temp_export_dir):
        """Test loading data from JSON file."""
        filename = temp_export_dir / "test_data.json"
        with open(filename, 'w') as f:
            json.dump(sample_data, f)
        
        formatter = ExportFormatter()
        loaded_data = formatter._load_data(filename)
        
        assert loaded_data == sample_data
    
    def test_load_yaml_data(self, sample_data, temp_export_dir):
        """Test loading data from YAML file."""
        filename = temp_export_dir / "test_data.yaml"
        with open(filename, 'w') as f:
            yaml.dump(sample_data, f)
        
        formatter = ExportFormatter()
        loaded_data = formatter._load_data(filename)
        
        assert loaded_data == sample_data
    
    def test_load_csv_data(self, sample_data, temp_export_dir):
        """Test loading data from CSV file."""
        filename = temp_export_dir / "test_data.csv"
        df = pd.DataFrame(sample_data['entries'])
        df.to_csv(filename, index=False)
        
        formatter = ExportFormatter()
        loaded_data = formatter._load_data(filename)
        
        assert len(loaded_data['title']) == len(sample_data['entries'])
        assert set(loaded_data.keys()) == set(sample_data['entries'][0].keys())
    
    def test_invalid_file_format(self, temp_export_dir):
        """Test loading data from an invalid file format."""
        filename = temp_export_dir / "test_data.invalid"
        with open(filename, 'w') as f:
            f.write("INVALID DATA")
        
        formatter = ExportFormatter()
        with pytest.raises(ValueError, match="Unsupported file format"):
            formatter._load_data(filename)
    
    def test_file_not_found(self):
        """Test loading data from a non-existent file."""
        formatter = ExportFormatter()
        with pytest.raises(FileNotFoundError, match="File not found"):
            formatter._load_data("nonexistent_file.json")
