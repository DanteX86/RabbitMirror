import os
from pathlib import Path

import pytest

from rabbitmirror.dashboard_generator import DashboardGenerator


@pytest.fixture
def test_data():
    """Sample test data for the dashboard generator."""
    return {
        "entries": [
            {
                "timestamp": "2025-07-10T12:00:00",
                "title": "Python Tutorial",
                "category": "Education",
                "url": "https://youtube.com/watch?v=xyz",
            },
            {
                "timestamp": "2025-07-10T13:00:00",
                "title": "Golang Basics",
                "category": "Programming",
                "url": "https://youtube.com/watch?v=abc",
            },
            {
                "timestamp": "2025-07-10T14:00:00",
                "title": "React Native Advanced",
                "category": "Web Development",
                "url": "https://youtube.com/watch?v=123",
            },
        ],
        "clusters": {
            "cluster_labels": [0, 1, 0],
            "features": [[1.0, 2.0], [1.5, 1.8], [0.9, 2.1]],
        },
        "suppression_results": {"suppression_scores": [0.5, 0.3, 0.7]},
        "patterns": {"pattern_scores": [0.8, 0.6, 0.9]},
    }


def test_dashboard_generator(test_data, tmp_path):
    """Test the dashboard generator with sample data."""
    output_dir = tmp_path / "dashboard_test_output"
    dashboard = DashboardGenerator(
        template="basic", interactive=True, theme="light", include_plots=True
    )

    # Run generator and create dashboard files
    generated_files = dashboard.generate_dashboard(test_data, output_dir)

    # Check that specific files are created
    assert "history_dashboard" in generated_files
    assert generated_files["history_dashboard"].exists()

    assert "analytics_dashboard" in generated_files
    assert generated_files["analytics_dashboard"].exists()

    # Basic file content check
    with open(generated_files["history_dashboard"], "r") as f:
        history_content = f.read()

    assert "Enhanced YouTube Watch History Dashboard" in history_content

    with open(generated_files["analytics_dashboard"], "r") as f:
        analytics_content = f.read()

    assert "Advanced YouTube Analytics Dashboard" in analytics_content


class TestDashboardGenerator:
    """Test class for comprehensive dashboard functionality."""

    def test_initialization(self):
        """Test dashboard generator initialization."""
        dashboard = DashboardGenerator(
            template="basic", interactive=True, theme="light", include_plots=True
        )

        assert dashboard.template == "basic"
        assert dashboard.interactive is True
        assert dashboard.theme == "light"
        assert dashboard.include_plots is True
        assert "background" in dashboard.colors

    def test_theme_colors(self):
        """Test theme color schemes."""
        light_dashboard = DashboardGenerator(theme="light")
        dark_dashboard = DashboardGenerator(theme="dark")

        # Test light theme
        assert light_dashboard.colors["background"] == "#FFFFFF"
        assert light_dashboard.colors["text"] == "#333333"

        # Test dark theme
        assert dark_dashboard.colors["background"] == "#2E2E2E"
        assert dark_dashboard.colors["text"] == "#FFFFFF"

    def test_empty_entries_error(self, tmp_path):
        """Test error handling for empty entries."""
        dashboard = DashboardGenerator()
        empty_data = {"entries": []}
        output_dir = tmp_path / "test_empty"

        with pytest.raises(ValueError, match="No entries found in data"):
            dashboard.generate_dashboard(empty_data, output_dir)

    def test_cluster_dashboard_generation(self, tmp_path):
        """Test cluster dashboard generation."""
        dashboard = DashboardGenerator()
        cluster_data = {
            "clusters": {
                "cluster_labels": [0, 1, 0, 1],
                "features": [[1.0, 2.0], [1.5, 1.8], [0.9, 2.1], [2.0, 1.5]],
            }
        }
        output_dir = tmp_path / "cluster_test"

        generated_files = dashboard.generate_dashboard(cluster_data, output_dir)

        assert "cluster_dashboard" in generated_files
        assert generated_files["cluster_dashboard"].exists()

        # Verify file content
        with open(generated_files["cluster_dashboard"], "r") as f:
            content = f.read()
        assert "Video Clustering Analysis" in content

    def test_suppression_dashboard_generation(self, tmp_path):
        """Test suppression analysis dashboard generation."""
        dashboard = DashboardGenerator()
        suppression_data = {
            "suppression_results": {"suppression_scores": [0.1, 0.3, 0.5, 0.7, 0.9]}
        }
        output_dir = tmp_path / "suppression_test"

        generated_files = dashboard.generate_dashboard(suppression_data, output_dir)

        assert "suppression_dashboard" in generated_files
        assert generated_files["suppression_dashboard"].exists()

        # Verify file content
        with open(generated_files["suppression_dashboard"], "r") as f:
            content = f.read()
        assert "Content Suppression Analysis" in content

    def test_pattern_dashboard_generation(self, tmp_path):
        """Test pattern analysis dashboard generation."""
        dashboard = DashboardGenerator()
        pattern_data = {"patterns": {"pattern_scores": [0.2, 0.4, 0.6, 0.8]}}
        output_dir = tmp_path / "pattern_test"

        generated_files = dashboard.generate_dashboard(pattern_data, output_dir)

        assert "pattern_dashboard" in generated_files
        assert generated_files["pattern_dashboard"].exists()

        # Verify file content
        with open(generated_files["pattern_dashboard"], "r") as f:
            content = f.read()
        assert "Adversarial Pattern Analysis" in content

    def test_index_dashboard_generation(self, test_data, tmp_path):
        """Test index dashboard generation when multiple components exist."""
        dashboard = DashboardGenerator()
        output_dir = tmp_path / "index_test"

        generated_files = dashboard.generate_dashboard(test_data, output_dir)

        # Should have multiple dashboards, so index should be created
        assert "index" in generated_files
        assert generated_files["index"].exists()

        # Verify index content
        with open(generated_files["index"], "r") as f:
            index_content = f.read()

        assert "RabbitMirror Analysis Dashboard" in index_content
        assert "History Dashboard" in index_content
        assert "Analytics Dashboard" in index_content

    def test_css_generation(self, test_data, tmp_path):
        """Test CSS file generation for interactive dashboards."""
        dashboard = DashboardGenerator(interactive=True)
        output_dir = tmp_path / "css_test"

        generated_files = dashboard.generate_dashboard(test_data, output_dir)

        assert "styles" in generated_files
        assert generated_files["styles"].exists()

        # Verify CSS content
        with open(generated_files["styles"], "r") as f:
            css_content = f.read()

        assert ":root" in css_content
        assert "--bg-color" in css_content

    def test_data_extraction_methods(self, test_data):
        """Test individual data extraction methods."""
        dashboard = DashboardGenerator()
        entries = test_data["entries"]

        # Test daily counts aggregation
        timestamps = [entry["timestamp"] for entry in entries]
        daily_counts = dashboard._aggregate_daily_counts(timestamps)
        assert isinstance(daily_counts, dict)
        assert len(daily_counts) > 0

        # Test category extraction
        categories = dashboard._extract_categories(entries)
        assert "Education" in categories
        assert "Programming" in categories
        assert "Web Development" in categories

        # Test top videos extraction
        top_videos = dashboard._extract_top_videos(entries)
        assert isinstance(top_videos, list)
        assert len(top_videos) > 0
        assert "title" in top_videos[0]
        assert "count" in top_videos[0]

        # Test viewing times extraction
        viewing_times = dashboard._extract_viewing_times(entries)
        assert isinstance(viewing_times, list)
        assert all(isinstance(hour, int) for hour in viewing_times)
        assert all(0 <= hour <= 23 for hour in viewing_times)

        # Test channel extraction
        channels = dashboard._extract_channels(entries)
        assert isinstance(channels, dict)

        # Test keyword analysis
        keywords = dashboard._analyze_title_keywords(entries)
        assert isinstance(keywords, dict)
        assert "python" in keywords or "tutorial" in keywords

        # Test weekly pattern analysis
        weekly_pattern = dashboard._analyze_weekly_pattern(timestamps)
        assert isinstance(weekly_pattern, dict)
        assert all(
            day in weekly_pattern
            for day in [
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday",
                "Sunday",
            ]
        )

        # Test watch velocity calculation
        velocity = dashboard._calculate_watch_velocity(entries)
        assert isinstance(velocity, dict)
        assert "average_velocity" in velocity
        assert "peak_day_count" in velocity
        assert "total_days_active" in velocity

        # Test popularity index calculation
        popularity = dashboard._calculate_popularity_index(entries)
        assert isinstance(popularity, list)
        assert len(popularity) == len(entries)
        assert all(isinstance(score, float) for score in popularity)

    def test_malformed_data_handling(self, tmp_path):
        """Test handling of malformed or incomplete data."""
        dashboard = DashboardGenerator()

        # Test with missing timestamps
        malformed_data = {
            "entries": [
                {"title": "Video 1"},
                {"timestamp": "invalid-timestamp", "title": "Video 2"},
                {"timestamp": "2025-07-10T12:00:00", "title": "Video 3"},
            ]
        }

        output_dir = tmp_path / "malformed_test"

        # Should not crash, but handle gracefully
        generated_files = dashboard.generate_dashboard(malformed_data, output_dir)

        assert "history_dashboard" in generated_files
        assert generated_files["history_dashboard"].exists()

    def test_different_themes(self, test_data, tmp_path):
        """Test dashboard generation with different themes."""
        for theme in ["light", "dark"]:
            dashboard = DashboardGenerator(theme=theme)
            output_dir = tmp_path / f"theme_{theme}_test"

            generated_files = dashboard.generate_dashboard(test_data, output_dir)

            assert len(generated_files) > 0

            # Verify theme is applied - check that dashboard was generated successfully
            # The actual theme application happens in the Plotly rendering
            with open(generated_files["history_dashboard"], "r") as f:
                content = f.read()

            # Just verify that the HTML contains Plotly content and title
            assert "Enhanced YouTube Watch History Dashboard" in content
            assert "plotly.js" in content or "Plotly" in content
