from pathlib import Path

import pytest

try:
    import bs4  # type: ignore  # noqa: F401

    _HAS_BS4 = True
except Exception:  # pragma: no cover - optional dependency for HTML parsing
    _HAS_BS4 = False

from rabbitmirror.parser import HistoryParser


@pytest.fixture
def sample_history_file():
    """Fixture providing path to sample history HTML file."""
    return Path(__file__).parent / "fixtures" / "sample_history.html"


@pytest.fixture
def sample_parser(sample_history_file):
    """Fixture providing a HistoryParser instance with sample data."""
    if not _HAS_BS4:
        pytest.skip("Skipping HTML parsing tests: beautifulsoup4 (bs4) not installed")
    return HistoryParser(str(sample_history_file), "youtube")


@pytest.fixture
def sample_entries(sample_parser):
    """Fixture providing parsed entries from sample history."""
    if not _HAS_BS4:
        pytest.skip("Skipping HTML parsing tests: beautifulsoup4 (bs4) not installed")
    result = sample_parser.parse()
    return result.entries


@pytest.fixture
def mock_history_data():
    """Fixture providing mock history data structure."""
    return [
        {
            "title": "Python Machine Learning Tutorial",
            "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "timestamp": "2023-12-15T14:30:45-08:00",
        },
        {
            "title": "FastAPI Development Guide",
            "url": "https://www.youtube.com/watch?v=abc123def456",
            "timestamp": "2023-12-15T13:15:22-08:00",
        },
        {
            "title": "Data Structures in Python",
            "url": "https://www.youtube.com/watch?v=xyz789uvw012",
            "timestamp": "2023-12-14T20:20:33-08:00",
        },
    ]


@pytest.fixture
def temp_output_dir(tmp_path):
    """Fixture providing a temporary directory for test outputs."""
    output_dir = tmp_path / "test_outputs"
    output_dir.mkdir()
    return output_dir


@pytest.fixture
def sample_history_dir(tmp_path):
    """Fixture providing a directory with sample history files for batch processing."""
    if not _HAS_BS4:
        pytest.skip("Skipping HTML parsing tests: beautifulsoup4 (bs4) not installed")
    history_dir = tmp_path / "history_files"
    history_dir.mkdir()

    # Copy the sample history file to the temp directory
    sample_file = Path(__file__).parent / "fixtures" / "sample_history.html"

    # Create multiple sample files for batch processing
    for i in range(2):
        dest_file = history_dir / f"history_{i + 1}.html"
        dest_file.write_text(sample_file.read_text())

    return history_dir
