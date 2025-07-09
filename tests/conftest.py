import pytest
from pathlib import Path
from rabbitmirror.parser import HistoryParser


@pytest.fixture
def sample_history_file():
    """Fixture providing path to sample history HTML file."""
    return Path(__file__).parent / 'fixtures' / 'sample_history.html'


@pytest.fixture
def sample_parser(sample_history_file):
    """Fixture providing a HistoryParser instance with sample data."""
    return HistoryParser(sample_history_file)


@pytest.fixture
def sample_entries(sample_parser):
    """Fixture providing parsed entries from sample history."""
    return sample_parser.parse()


@pytest.fixture
def mock_history_data():
    """Fixture providing mock history data structure."""
    return [
        {
            'title': 'Python Machine Learning Tutorial',
            'url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
            'timestamp': '2023-12-15T14:30:45-08:00'
        },
        {
            'title': 'FastAPI Development Guide',
            'url': 'https://www.youtube.com/watch?v=abc123def456',
            'timestamp': '2023-12-15T13:15:22-08:00'
        },
        {
            'title': 'Data Structures in Python',
            'url': 'https://www.youtube.com/watch?v=xyz789uvw012',
            'timestamp': '2023-12-14T20:20:33-08:00'
        }
    ]


@pytest.fixture
def temp_output_dir(tmp_path):
    """Fixture providing a temporary directory for test outputs."""
    output_dir = tmp_path / "test_outputs"
    output_dir.mkdir()
    return output_dir
