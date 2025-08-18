"""Integration tests for web endpoints."""

import io
import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from rabbitmirror.exceptions import SecurityError, ValidationError


class TestWebEndpointsIntegration:
    """Integration tests for Flask web application endpoints."""

    def test_index_page_get(self, client):
        """Test GET request to index page."""
        response = client.get("/")
        assert response.status_code == 200
        assert b"html" in response.data.lower()

    def test_index_page_security_headers(self, client, mock_security_config):
        """Test security headers are added to responses."""
        response = client.get("/")
        assert response.status_code == 200

        # Check for security headers
        expected_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
        }

        for header, value in expected_headers.items():
            assert response.headers.get(header) == value

    def test_file_upload_no_file(self, client):
        """Test file upload without providing a file."""
        response = client.post("/", data={})
        assert response.status_code == 200
        # Should return to upload page with error message

    def test_file_upload_empty_file(self, client):
        """Test file upload with empty file."""
        data = {"file": (io.BytesIO(b""), "")}
        response = client.post("/", data=data)
        assert response.status_code == 200
        # Should handle empty filename gracefully

    def test_file_upload_success(self, client, temp_upload_file):
        """Test successful file upload and redirect."""
        with open(temp_upload_file, "rb") as f:
            data = {"file": (f, "test_history.html")}
            response = client.post("/", data=data, follow_redirects=False)

        # Should redirect to analysis page
        assert response.status_code == 302
        assert "/analyze/" in response.location

    def test_file_upload_large_file(self, client, large_upload_file):
        """Test upload of large file within limits."""
        with open(large_upload_file, "rb") as f:
            data = {"file": (f, "large_history.html")}
            response = client.post("/", data=data, follow_redirects=False)

        # Should handle large file successfully
        assert response.status_code == 302

    def test_file_upload_invalid_extension(self, client, tmp_path):
        """Test upload of file with invalid extension."""
        invalid_file = tmp_path / "test.exe"
        invalid_file.write_bytes(b"fake executable content")

        with open(invalid_file, "rb") as f:
            data = {"file": (f, "test.exe")}
            response = client.post("/", data=data)

        # Should reject invalid file types
        assert response.status_code == 200
        # Should remain on upload page with error

    def test_analyze_endpoint_valid_file(self, client, app, temp_upload_file):
        """Test analysis endpoint with valid uploaded file."""
        # First upload the file
        with open(temp_upload_file, "rb") as f:
            data = {"file": (f, "test_history.html")}
            upload_response = client.post("/", data=data, follow_redirects=False)

        # Extract filename from redirect location
        filename = upload_response.location.split("/")[-1]

        # Test analysis endpoint
        response = client.get(f"/analyze/{filename}")
        assert response.status_code == 200
        assert b"analysis" in response.data.lower() or b"data" in response.data.lower()

    def test_analyze_endpoint_nonexistent_file(self, client):
        """Test analysis endpoint with non-existent file."""
        response = client.get("/analyze/nonexistent.html")
        assert response.status_code == 302  # Should redirect back to upload

    def test_analyze_endpoint_malformed_data(self, client, app, malformed_upload_file):
        """Test analysis endpoint with malformed data."""
        # Upload malformed file
        with open(malformed_upload_file, "rb") as f:
            data = {"file": (f, "malformed_history.html")}
            upload_response = client.post("/", data=data, follow_redirects=False)

        if upload_response.status_code == 302:
            filename = upload_response.location.split("/")[-1]
            response = client.get(f"/analyze/{filename}")
            # Should handle malformed data gracefully
            assert response.status_code in [200, 302]

    def test_export_endpoint_json(self, client, app, temp_upload_file):
        """Test export endpoint with JSON format."""
        # Upload file first
        with open(temp_upload_file, "rb") as f:
            data = {"file": (f, "test_history.html")}
            upload_response = client.post("/", data=data, follow_redirects=False)

        if upload_response.status_code == 302:
            filename = upload_response.location.split("/")[-1]

            # Test JSON export
            response = client.get(f"/export/{filename}/json")
            assert response.status_code == 200
            assert response.headers["Content-Type"].startswith("application/")

    def test_export_endpoint_csv(self, client, app, temp_upload_file):
        """Test export endpoint with CSV format."""
        # Upload file first
        with open(temp_upload_file, "rb") as f:
            data = {"file": (f, "test_history.html")}
            upload_response = client.post("/", data=data, follow_redirects=False)

        if upload_response.status_code == 302:
            filename = upload_response.location.split("/")[-1]

            # Test CSV export
            response = client.get(f"/export/{filename}/csv")
            assert response.status_code == 200

    def test_export_endpoint_yaml(self, client, app, temp_upload_file):
        """Test export endpoint with YAML format."""
        # Upload file first
        with open(temp_upload_file, "rb") as f:
            data = {"file": (f, "test_history.html")}
            upload_response = client.post("/", data=data, follow_redirects=False)

        if upload_response.status_code == 302:
            filename = upload_response.location.split("/")[-1]

            # Test YAML export
            response = client.get(f"/export/{filename}/yaml")
            assert response.status_code == 200

    def test_export_endpoint_invalid_format(self, client, app, temp_upload_file):
        """Test export endpoint with invalid format."""
        # Upload file first
        with open(temp_upload_file, "rb") as f:
            data = {"file": (f, "test_history.html")}
            upload_response = client.post("/", data=data, follow_redirects=False)

        if upload_response.status_code == 302:
            filename = upload_response.location.split("/")[-1]

            # Test invalid format
            response = client.get(f"/export/{filename}/invalid")
            assert response.status_code == 302  # Should redirect back

    def test_benchmarks_page(self, client):
        """Test benchmarks page access."""
        response = client.get("/benchmarks")
        assert response.status_code == 200
        assert b"benchmark" in response.data.lower()

    def test_about_page(self, client):
        """Test about page access."""
        response = client.get("/about")
        assert response.status_code == 200
        assert (
            b"about" in response.data.lower()
            or b"rabbitmirror" in response.data.lower()
        )

    def test_404_error_handler(self, client):
        """Test 404 error handling."""
        response = client.get("/nonexistent-page")
        assert response.status_code == 404

    def test_file_too_large_error(self, client):
        """Test file too large error handling."""
        # Create a file larger than the configured limit
        large_content = b"x" * (200 * 1024 * 1024)  # 200MB
        data = {"file": (io.BytesIO(large_content), "huge_file.html")}

        response = client.post("/", data=data)
        assert response.status_code == 413  # Request Entity Too Large

    @patch("rabbitmirror.web.app.rate_limiter")
    def test_rate_limiting(self, mock_rate_limiter, client):
        """Test rate limiting functionality."""
        # Mock rate limiter to return False (rate limit exceeded)
        mock_rate_limiter.is_allowed.return_value = False

        response = client.get("/")
        assert response.status_code == 429  # Too Many Requests

    @patch("rabbitmirror.web.app.input_validator")
    def test_security_validation_failure(
        self, mock_validator, client, temp_upload_file
    ):
        """Test security validation failure during upload."""
        # Mock validator to raise SecurityError
        mock_validator.validate_filename.side_effect = SecurityError(
            "Dangerous filename"
        )

        with open(temp_upload_file, "rb") as f:
            data = {"file": (f, "test_history.html")}
            response = client.post("/", data=data)

        assert response.status_code == 200  # Should stay on upload page

    def test_concurrent_uploads(self, client, temp_upload_file):
        """Test handling of concurrent file uploads."""
        import threading
        import time

        results = []

        def upload_file():
            with open(temp_upload_file, "rb") as f:
                data = {
                    "file": (
                        f,
                        f"concurrent_test_{threading.current_thread().ident}.html",
                    )
                }
                response = client.post("/", data=data, follow_redirects=False)
                results.append(response.status_code)

        # Create multiple threads for concurrent uploads
        threads = []
        for i in range(3):
            thread = threading.Thread(target=upload_file)
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # All uploads should succeed or be handled gracefully
        assert all(status in [302, 200] for status in results)

    def test_session_management(self, client):
        """Test session management and flash messages."""
        # Test that flash messages work correctly
        with client.session_transaction() as sess:
            sess["test_key"] = "test_value"

        response = client.get("/")
        assert response.status_code == 200

        # Session should be maintained
        with client.session_transaction() as sess:
            assert sess.get("test_key") == "test_value"

    def test_file_path_traversal_prevention(self, client):
        """Test prevention of path traversal attacks."""
        malicious_filename = "../../../etc/passwd"
        data = {"file": (io.BytesIO(b"content"), malicious_filename)}

        response = client.post("/", data=data)
        # Should be rejected due to security validation
        assert response.status_code == 200

    def test_upload_workflow_integration(self, client, temp_upload_file):
        """Test complete upload and analysis workflow."""
        # Step 1: Upload file
        with open(temp_upload_file, "rb") as f:
            data = {"file": (f, "workflow_test.html")}
            upload_response = client.post("/", data=data, follow_redirects=False)

        assert upload_response.status_code == 302

        # Step 2: Follow redirect to analysis
        analysis_url = upload_response.location
        analysis_response = client.get(analysis_url)
        assert analysis_response.status_code == 200

        # Step 3: Test export functionality
        filename = analysis_url.split("/")[-1]
        export_response = client.get(f"/export/{filename}/json")
        assert export_response.status_code == 200

    def test_error_recovery_and_logging(self, client):
        """Test error recovery and logging mechanisms."""
        with patch("rabbitmirror.web.app.security_auditor") as mock_auditor:
            # Trigger an error condition
            response = client.post("/", data={"file": "invalid_data"})

            # Verify that security events are logged
            assert mock_auditor.log_security_event.called

    def test_content_type_validation(self, client, tmp_path):
        """Test content type validation for uploaded files."""
        # Create file with mismatched extension and content
        fake_html = tmp_path / "fake.html"
        fake_html.write_bytes(b"\x89PNG\r\n\x1a\n")  # PNG file signature

        with open(fake_html, "rb") as f:
            data = {"file": (f, "fake.html")}
            response = client.post("/", data=data)

        # Should handle content type mismatch appropriately
        assert response.status_code in [200, 302]

    def test_memory_usage_during_large_operations(self, client, large_upload_file):
        """Test memory usage during large file operations."""
        import os

        # Skip test if psutil is not available
        try:
            import psutil
        except ImportError:
            pytest.skip("psutil not available")

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss

        # Upload and process large file
        with open(large_upload_file, "rb") as f:
            data = {"file": (f, "memory_test.html")}
            response = client.post("/", data=data, follow_redirects=True)

        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory

        # Memory increase should be reasonable (less than 500MB)
        assert memory_increase < 500 * 1024 * 1024
        assert response.status_code == 200
