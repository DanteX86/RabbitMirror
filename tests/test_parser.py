from pathlib import Path

from rabbitmirror.parser import HistoryParser

# Sample test for HistoryParser


def test_parse_sample_history():
    file_path = Path(__file__).parent / "fixtures" / "sample_history.html"
    parser = HistoryParser(file_path)
    entries = parser.parse()
    assert len(entries) == 5, "Should parse 5 entries from the sample history"
    assert (
        entries[0]["title"] == "Python Machine Learning Tutorial"
    ), "First title should match"
    assert (
        entries[1]["title"] == "FastAPI Development Guide"
    ), "Second title should match"
    assert (
        entries[2]["title"] == "Data Structures in Python"
    ), "Third title should match"


def test_parse_entry_with_missing_title(tmp_path):
    """Test parsing entry without title tag."""
    html_content = """
    <html>
    <body>
        <div class="content-cell">
            <div class="mdl-typography--caption">Dec 15, 2023, 2:30:45 PM PST</div>
        </div>
    </body>
    </html>
    """

    test_file = tmp_path / "test_no_title.html"
    test_file.write_text(html_content)

    parser = HistoryParser(str(test_file))
    entries = parser.parse()
    assert len(entries) == 0, "Should return empty list when no title tag found"


def test_convert_timestamp_unknown():
    """Test timestamp conversion with 'Unknown' input."""
    parser = HistoryParser("dummy_path")
    result = parser._convert_timestamp("Unknown")
    # Should return current time in ISO format
    assert isinstance(result, str)
    assert "T" in result  # ISO format contains 'T'


def test_convert_timestamp_valid():
    """Test timestamp conversion with valid YouTube format."""
    parser = HistoryParser("dummy_path")
    result = parser._convert_timestamp("Dec 15, 2023, 2:30:45 PM PST")
    assert result == "2023-12-15T14:30:45"


def test_convert_timestamp_invalid():
    """Test timestamp conversion with invalid format."""
    parser = HistoryParser("dummy_path")
    result = parser._convert_timestamp("Invalid timestamp format")
    # Should return current time in ISO format when parsing fails
    assert isinstance(result, str)
    assert "T" in result  # ISO format contains 'T'


def test_parse_entry_with_missing_timestamp(tmp_path):
    """Test parsing entry without timestamp tag."""
    html_content = """
    <html>
    <body>
        <div class="content-cell">
            <a href="https://www.youtube.com/watch?v=test">Test Video</a>
        </div>
    </body>
    </html>
    """

    test_file = tmp_path / "test_no_timestamp.html"
    test_file.write_text(html_content)

    parser = HistoryParser(str(test_file))
    entries = parser.parse()
    assert len(entries) == 1
    assert entries[0]["title"] == "Test Video"
    assert "T" in entries[0]["timestamp"]  # Should have ISO timestamp


def test_parse_entry_with_missing_url(tmp_path):
    """Test parsing entry without href attribute."""
    html_content = """
    <html>
    <body>
        <div class="content-cell">
            <a>Test Video Without URL</a>
            <div class="mdl-typography--caption">Dec 15, 2023, 2:30:45 PM PST</div>
        </div>
    </body>
    </html>
    """

    test_file = tmp_path / "test_no_url.html"
    test_file.write_text(html_content)

    parser = HistoryParser(str(test_file))
    entries = parser.parse()
    assert len(entries) == 1
    assert entries[0]["title"] == "Test Video Without URL"
    assert entries[0]["url"] == ""  # Should default to empty string


def test_parse_empty_html(tmp_path):
    """Test parsing empty HTML file."""
    html_content = "<html><body></body></html>"

    test_file = tmp_path / "empty.html"
    test_file.write_text(html_content)

    parser = HistoryParser(str(test_file))
    entries = parser.parse()
    assert len(entries) == 0, "Should return empty list for empty HTML"
