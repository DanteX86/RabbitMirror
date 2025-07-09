import pytest
from rabbitmirror.parser import HistoryParser
from pathlib import Path

# Sample test for HistoryParser

def test_parse_sample_history():
    file_path = Path(__file__).parent / 'fixtures' / 'sample_history.html'
    parser = HistoryParser(file_path)
    entries = parser.parse()
    assert len(entries) == 5, "Should parse 5 entries from the sample history"
    assert entries[0]['title'] == "Python Machine Learning Tutorial", "First title should match"
    assert entries[1]['title'] == "FastAPI Development Guide", "Second title should match"
    assert entries[2]['title'] == "Data Structures in Python", "Third title should match"

