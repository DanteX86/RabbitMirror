from datetime import datetime

import pytest

from rabbitmirror.report_generator import ReportGenerator


@pytest.fixture
def temp_template_dir(tmp_path):
    """Fixture providing a temporary template directory."""
    template_dir = tmp_path / "templates"
    template_dir.mkdir()

    # Create a simple test template
    template_content = """
<!DOCTYPE html>
<html>
<head>
    <title>{{ title }}</title>
</head>
<body>
    <h1>{{ title }}</h1>
    <p>Generated at: {{ generated_at }}</p>
    <ul>
    {% for entry in entries %}
        <li>{{ entry.title }} - {{ entry.timestamp }}</li>
    {% endfor %}
    </ul>
</body>
</html>
    """.strip()

    template_file = template_dir / "test_template.html"
    template_file.write_text(template_content)

    return template_dir


@pytest.fixture
def sample_report_data():
    """Sample data for report generation."""
    return {
        "title": "Watch History Report",
        "entries": [
            {"title": "Video 1", "timestamp": "2025-07-01T10:00:00"},
            {"title": "Video 2", "timestamp": "2025-07-01T11:00:00"},
        ],
        "summary": {"total_videos": 2, "total_duration": "2 hours"},
    }


class TestReportGenerator:
    """Test suite for the ReportGenerator class."""

    def test_initialization_default(self):
        """Test ReportGenerator initialization with default parameters."""
        report_gen = ReportGenerator()
        assert report_gen.env is not None

    def test_initialization_custom_template_dir(self, temp_template_dir):
        """Test ReportGenerator initialization with custom template directory."""
        report_gen = ReportGenerator(template_dir=str(temp_template_dir))
        assert report_gen.env is not None

    def test_generate_report_basic(
        self, temp_template_dir, sample_report_data, tmp_path
    ):
        """Test basic report generation."""
        report_gen = ReportGenerator(template_dir=str(temp_template_dir))
        output_path = tmp_path / "test_report.html"

        report_gen.generate_report(
            data=sample_report_data,
            template_name="test_template.html",
            output_path=str(output_path),
        )

        assert output_path.exists()
        content = output_path.read_text()

        # Check that template variables were replaced
        assert sample_report_data["title"] in content
        assert "Video 1" in content
        assert "Video 2" in content
        assert "Generated at:" in content

    def test_generate_report_with_metadata(
        self, temp_template_dir, sample_report_data, tmp_path
    ):
        """Test that generated_at metadata is added to report data."""
        report_gen = ReportGenerator(template_dir=str(temp_template_dir))
        output_path = tmp_path / "test_report.html"

        # Store original data to verify it's not modified
        sample_report_data.copy()

        report_gen.generate_report(
            data=sample_report_data,
            template_name="test_template.html",
            output_path=str(output_path),
        )

        # Check that generated_at was added
        assert "generated_at" in sample_report_data
        assert isinstance(sample_report_data["generated_at"], str)

        # Verify it's a valid ISO format timestamp
        datetime.fromisoformat(sample_report_data["generated_at"])

    def test_generate_report_output_directory_creation(
        self, temp_template_dir, sample_report_data, tmp_path
    ):
        """Test that output directory is created if it doesn't exist."""
        report_gen = ReportGenerator(template_dir=str(temp_template_dir))

        # Create path with non-existent directory
        output_dir = tmp_path / "reports" / "subdirectory"
        output_path = output_dir / "test_report.html"

        assert not output_dir.exists()

        report_gen.generate_report(
            data=sample_report_data,
            template_name="test_template.html",
            output_path=str(output_path),
        )

        assert output_path.exists()
        assert output_dir.exists()

    def test_generate_report_empty_data(self, temp_template_dir, tmp_path):
        """Test report generation with empty data."""
        report_gen = ReportGenerator(template_dir=str(temp_template_dir))
        output_path = tmp_path / "empty_report.html"

        empty_data = {"title": "Empty Report", "entries": []}

        report_gen.generate_report(
            data=empty_data,
            template_name="test_template.html",
            output_path=str(output_path),
        )

        assert output_path.exists()
        content = output_path.read_text()
        assert "Empty Report" in content

    def test_template_not_found(self, temp_template_dir, sample_report_data, tmp_path):
        """Test handling of non-existent template."""
        report_gen = ReportGenerator(template_dir=str(temp_template_dir))
        output_path = tmp_path / "test_report.html"

        with pytest.raises(Exception):  # jinja2.TemplateNotFound
            report_gen.generate_report(
                data=sample_report_data,
                template_name="nonexistent_template.html",
                output_path=str(output_path),
            )

    def test_complex_template_data(self, temp_template_dir, tmp_path):
        """Test report generation with complex nested data."""
        # Create a more complex template
        complex_template_content = """
<html>
<head><title>{{ report.title }}</title></head>
<body>
    <h1>{{ report.title }}</h1>
    <h2>Summary</h2>
    <p>Total: {{ summary.total }}</p>
    <p>Average: {{ summary.average }}</p>

    <h2>Categories</h2>
    {% for category, data in categories.items() %}
        <h3>{{ category }}</h3>
        <ul>
        {% for item in data.videos %}
            <li>{{ item.name }} ({{ item.count }})</li>
        {% endfor %}
        </ul>
    {% endfor %}
</body>
</html>
        """.strip()

        complex_template_file = temp_template_dir / "complex_template.html"
        complex_template_file.write_text(complex_template_content)

        complex_data = {
            "report": {"title": "Complex Analysis Report"},
            "summary": {"total": 100, "average": 25.5},
            "categories": {
                "Educational": {
                    "videos": [
                        {"name": "Python Tutorial", "count": 5},
                        {"name": "Math Lessons", "count": 3},
                    ]
                },
                "Entertainment": {
                    "videos": [
                        {"name": "Comedy Videos", "count": 7},
                        {"name": "Music Videos", "count": 10},
                    ]
                },
            },
        }

        report_gen = ReportGenerator(template_dir=str(temp_template_dir))
        output_path = tmp_path / "complex_report.html"

        report_gen.generate_report(
            data=complex_data,
            template_name="complex_template.html",
            output_path=str(output_path),
        )

        assert output_path.exists()
        content = output_path.read_text()

        # Verify complex data was rendered correctly
        assert "Complex Analysis Report" in content
        assert "Total: 100" in content
        assert "Average: 25.5" in content
        assert "Educational" in content
        assert "Entertainment" in content
        assert "Python Tutorial" in content
        assert "Comedy Videos" in content

    def test_autoescape_functionality(self, temp_template_dir, tmp_path):
        """Test that HTML content is properly escaped in templates."""
        # Create template that might have XSS vulnerability
        escape_template_content = """
<html>
<body>
    <h1>{{ title }}</h1>
    <p>{{ description }}</p>
</body>
</html>
        """.strip()

        escape_template_file = temp_template_dir / "escape_template.html"
        escape_template_file.write_text(escape_template_content)

        # Data with potential XSS content
        dangerous_data = {
            "title": "Test Report",
            "description": '<script>alert("XSS")</script>This should be escaped',
        }

        report_gen = ReportGenerator(template_dir=str(temp_template_dir))
        output_path = tmp_path / "escape_test.html"

        report_gen.generate_report(
            data=dangerous_data,
            template_name="escape_template.html",
            output_path=str(output_path),
        )

        assert output_path.exists()
        content = output_path.read_text()

        # Script should be escaped
        assert "<script>" not in content
        assert "&lt;script&gt;" in content or "&amp;lt;script&amp;gt;" in content

    def test_unicode_content(self, temp_template_dir, tmp_path):
        """Test report generation with Unicode content."""
        unicode_data = {
            "title": "Unicode Test Report 🐰",
            "entries": [
                {"title": "Video with émojis 📺", "timestamp": "2025-07-01T10:00:00"},
                {"title": "Açcénted chäractérs", "timestamp": "2025-07-01T11:00:00"},
                {
                    "title": "中文测试 Japanese テスト",
                    "timestamp": "2025-07-01T12:00:00",
                },
            ],
        }

        report_gen = ReportGenerator(template_dir=str(temp_template_dir))
        output_path = tmp_path / "unicode_report.html"

        report_gen.generate_report(
            data=unicode_data,
            template_name="test_template.html",
            output_path=str(output_path),
        )

        assert output_path.exists()
        content = output_path.read_text(encoding="utf-8")

        # Verify Unicode content is preserved
        assert "🐰" in content
        assert "📺" in content
        assert "émojis" in content
        assert "中文测试" in content
        assert "テスト" in content
