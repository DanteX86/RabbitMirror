"""Integration test configuration and fixtures."""

import os

# Add the project root to Python path
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from flask import Flask

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from rabbitmirror.web.app import app as flask_app


@pytest.fixture
def app():
    """Create and configure a test Flask application."""
    # Create a temporary directory for uploads during testing
    with tempfile.TemporaryDirectory() as temp_dir:
        flask_app.config.update(
            {
                "TESTING": True,
                "WTF_CSRF_ENABLED": False,
                "UPLOAD_FOLDER": temp_dir,
                "MAX_CONTENT_LENGTH": 100 * 1024 * 1024,  # 100MB
                "SECRET_KEY": "test-secret-key-for-testing-only",
            }
        )

        # Ensure upload directory exists
        os.makedirs(temp_dir, exist_ok=True)

        yield flask_app


@pytest.fixture
def client(app):
    """Create a test client for the Flask application."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create a test runner for the Flask application."""
    return app.test_cli_runner()


@pytest.fixture
def sample_html_content():
    """Sample YouTube watch history HTML content for testing."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>YouTube Watch History</title>
    </head>
    <body>
        <div class="content-cell">
            <a href="https://www.youtube.com/watch?v=dQw4w9WgXcQ">Rick Astley - Never Gonna Give You Up</a>
            <div class="mdl-typography--caption">Dec 15, 2023, 2:30:45 PM PST</div>
        </div>
        <div class="content-cell">
            <a href="https://www.youtube.com/watch?v=abc123def456">Python Tutorial - Learn Programming</a>
            <div class="mdl-typography--caption">Dec 14, 2023, 1:15:30 PM PST</div>
        </div>
        <div class="content-cell">
            <a href="https://www.youtube.com/watch?v=xyz789uvw012">Machine Learning Basics</a>
            <div class="mdl-typography--caption">Dec 13, 2023, 10:45:22 AM PST</div>
        </div>
    </body>
    </html>
    """


@pytest.fixture
def sample_large_html_content():
    """Large sample HTML content for performance testing."""
    base_content = """
    <div class="content-cell">
        <a href="https://www.youtube.com/watch?v=test{id}">Test Video {id}</a>
        <div class="mdl-typography--caption">Dec {day}, 2023, {hour}:30:45 PM PST</div>
    </div>
    """

    content_items = []
    for i in range(1000):  # Generate 1000 video entries
        day = 15 - (i % 30)  # Vary the day
        hour = 1 + (i % 12)  # Vary the hour
        content_items.append(base_content.format(id=i, day=day, hour=hour))

    return f"""
    <!DOCTYPE html>
    <html>
    <head><title>YouTube Watch History</title></head>
    <body>
        {''.join(content_items)}
    </body>
    </html>
    """


@pytest.fixture
def malformed_html_content():
    """Malformed HTML content for error handling tests."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Malformed Watch History</title>
    </head>
    <body>
        <div class="content-cell">
            <a href="https://www.youtube.com/watch?v=test1">Video without timestamp</a>
        </div>
        <div class="content-cell">
            <div class="mdl-typography--caption">Dec 15, 2023, 2:30:45 PM PST</div>
            <!-- Missing link -->
        </div>
        <div class="content-cell">
            <a>Video without URL</a>
            <div class="mdl-typography--caption">Invalid timestamp format</div>
        </div>
    </body>
    </html>
    """


@pytest.fixture
def mock_security_config():
    """Mock security configuration for testing."""
    with patch("rabbitmirror.web.app.security_config") as mock_config:
        mock_config.max_file_size = 100 * 1024 * 1024
        mock_config.security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
        }
        yield mock_config


@pytest.fixture
def temp_upload_file(tmp_path, sample_html_content):
    """Create a temporary upload file for testing."""
    temp_file = tmp_path / "test_history.html"
    temp_file.write_text(sample_html_content)
    return temp_file


@pytest.fixture
def large_upload_file(tmp_path, sample_large_html_content):
    """Create a large temporary upload file for testing."""
    temp_file = tmp_path / "large_history.html"
    temp_file.write_text(sample_large_html_content)
    return temp_file


@pytest.fixture
def malformed_upload_file(tmp_path, malformed_html_content):
    """Create a malformed temporary upload file for testing."""
    temp_file = tmp_path / "malformed_history.html"
    temp_file.write_text(malformed_html_content)
    return temp_file
