"""
Test cases for TrendAnalyzer class.
"""

from datetime import datetime

import pytest

from rabbitmirror.trend_analyzer import TrendAnalyzer, TrendMetric

# from datetime import timedelta
# from unittest.mock import patch


# from rabbitmirror.trend_analyzer import SignificantChange


class TestTrendAnalyzer:
    """Test cases for TrendAnalyzer."""

    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = TrendAnalyzer()

    def test_initialization_default(self):
        """Test TrendAnalyzer initialization with default parameters."""
        analyzer = TrendAnalyzer()
        assert analyzer.period_type == "daily"
        assert analyzer.normalize is False
        assert analyzer.supported_periods == ["daily", "weekly", "monthly"]

    def test_initialization_custom(self):
        """Test TrendAnalyzer initialization with custom parameters."""
        analyzer = TrendAnalyzer(period_type="weekly", normalize=True)
        assert analyzer.period_type == "weekly"
        assert analyzer.normalize is True

    def test_initialization_invalid_period(self):
        """Test TrendAnalyzer initialization with invalid period type."""
        with pytest.raises(ValueError, match="Period type must be one of"):
            TrendAnalyzer(period_type="invalid")

    def test_analyze_trends_empty_data(self):
        """Test trend analysis with empty data."""
        result = self.analyzer.analyze_trends([])

        assert result["period_type"] == "daily"
        assert result["timeframes"] == []
        assert result["metrics"] == {}
        assert result["significant_changes"] == []
        assert result["total_periods_analyzed"] == 0
        assert result["date_range"]["start"] is None
        assert result["date_range"]["end"] is None

    def test_analyze_trends_basic_data(self):
        """Test trend analysis with basic sample data."""
        entries = [
            {
                "timestamp": "2024-01-01T10:00:00",
                "title": "Video 1",
                "duration": 600,
                "channel": "Channel A",
            },
            {
                "timestamp": "2024-01-01T11:00:00",
                "title": "Video 2",
                "duration": 900,
                "channel": "Channel B",
            },
            {
                "timestamp": "2024-01-02T10:00:00",
                "title": "Video 3",
                "duration": 1200,
                "channel": "Channel A",
            },
        ]

        result = self.analyzer.analyze_trends(entries)

        assert result["period_type"] == "daily"
        assert len(result["timeframes"]) == 2  # 2 days
        assert "video_count" in result["metrics"]
        assert "total_duration" in result["metrics"]
        assert result["total_periods_analyzed"] == 2

    def test_period_key_generation_daily(self):
        """Test period key generation for daily periods."""
        analyzer = TrendAnalyzer(period_type="daily")
        timestamp = datetime(2024, 1, 15, 14, 30, 0)

        key = analyzer._get_period_key(timestamp)
        assert key == "2024-01-15"

    def test_period_key_generation_weekly(self):
        """Test period key generation for weekly periods."""
        analyzer = TrendAnalyzer(period_type="weekly")
        timestamp = datetime(2024, 1, 15, 14, 30, 0)  # Monday

        key = analyzer._get_period_key(timestamp)
        assert key.startswith("2024-W")

    def test_period_key_generation_monthly(self):
        """Test period key generation for monthly periods."""
        analyzer = TrendAnalyzer(period_type="monthly")
        timestamp = datetime(2024, 1, 15, 14, 30, 0)

        key = analyzer._get_period_key(timestamp)
        assert key == "2024-01"

    def test_calculate_period_metrics(self):
        """Test period metrics calculation."""
        time_periods = {
            "2024-01-01": [
                {"duration": 600, "channel": "A", "category": "tech"},
                {"duration": 900, "channel": "B", "category": "music"},
            ],
            "2024-01-02": [{"duration": 1200, "channel": "A", "category": "tech"}],
        }

        metrics = self.analyzer._calculate_period_metrics(time_periods)

        assert metrics["video_count"] == [2, 1]
        assert metrics["total_duration"] == [1500, 1200]
        assert metrics["avg_duration"] == [750, 1200]
        assert metrics["unique_channels"] == [2, 1]
        assert metrics["categories_diversity"] == [2, 1]

    def test_count_sessions_single_session(self):
        """Test session counting with single session."""
        entries = [
            {"timestamp": "2024-01-01T10:00:00"},
            {"timestamp": "2024-01-01T10:05:00"},
            {"timestamp": "2024-01-01T10:10:00"},
        ]

        sessions = self.analyzer._count_sessions(entries, gap_threshold=30)
        assert sessions == 1

    def test_count_sessions_multiple_sessions(self):
        """Test session counting with multiple sessions."""
        entries = [
            {"timestamp": "2024-01-01T10:00:00"},
            {"timestamp": "2024-01-01T10:05:00"},
            {"timestamp": "2024-01-01T12:00:00"},  # 2 hour gap > 30 min threshold
        ]

        sessions = self.analyzer._count_sessions(entries, gap_threshold=30)
        assert sessions == 2

    def test_count_sessions_empty_entries(self):
        """Test session counting with empty entries."""
        sessions = self.analyzer._count_sessions([])
        assert sessions == 0

    def test_analyze_metric_trend_single_value(self):
        """Test metric trend analysis with single value."""
        values = [10]
        timeframes = ["2024-01-01"]

        trend = self.analyzer._analyze_metric_trend("test_metric", values, timeframes)

        assert trend.name == "test_metric"
        assert trend.values == values
        assert trend.trend_direction == "stable"
        assert trend.trend_strength == 0.0

    def test_analyze_metric_trend_increasing(self):
        """Test metric trend analysis with increasing trend."""
        values = [10, 20, 30, 40, 50]
        timeframes = [
            "2024-01-01",
            "2024-01-02",
            "2024-01-03",
            "2024-01-04",
            "2024-01-05",
        ]

        trend = self.analyzer._analyze_metric_trend("test_metric", values, timeframes)

        assert trend.trend_direction == "increasing"
        assert trend.trend_strength > 0.8  # Strong correlation

    def test_analyze_metric_trend_decreasing(self):
        """Test metric trend analysis with decreasing trend."""
        values = [50, 40, 30, 20, 10]
        timeframes = [
            "2024-01-01",
            "2024-01-02",
            "2024-01-03",
            "2024-01-04",
            "2024-01-05",
        ]

        trend = self.analyzer._analyze_metric_trend("test_metric", values, timeframes)

        assert trend.trend_direction == "decreasing"
        assert trend.trend_strength > 0.8  # Strong correlation

    def test_analyze_metric_trend_stable(self):
        """Test metric trend analysis with stable trend."""
        values = [20, 20, 20, 20, 20]  # Completely stable values
        timeframes = [
            "2024-01-01",
            "2024-01-02",
            "2024-01-03",
            "2024-01-04",
            "2024-01-05",
        ]

        trend = self.analyzer._analyze_metric_trend("test_metric", values, timeframes)

        assert trend.trend_direction == "stable"

    def test_detect_significant_changes(self):
        """Test significant change detection."""
        trend_metric = TrendMetric(
            name="test_metric",
            values=[10, 10, 20, 20],  # 100% increase
            timeframes=["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04"],
            trend_direction="increasing",
            trend_strength=0.8,
            statistical_significance=0.9,
        )

        changes = self.analyzer._detect_significant_changes(trend_metric)

        assert len(changes) == 1
        assert changes[0].metric == "test_metric"
        assert changes[0].change_percentage == 100.0

    def test_detect_significant_changes_no_changes(self):
        """Test significant change detection with no significant changes."""
        trend_metric = TrendMetric(
            name="test_metric",
            values=[10, 11, 10, 12],  # Small variations
            timeframes=["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04"],
            trend_direction="stable",
            trend_strength=0.1,
            statistical_significance=0.1,
        )

        changes = self.analyzer._detect_significant_changes(trend_metric)

        assert len(changes) == 0

    def test_generate_summary(self):
        """Test summary generation."""
        trends = {
            "metric1": TrendMetric(
                "metric1", [1, 2, 3], ["a", "b", "c"], "increasing", 0.9, 0.8
            ),
            "metric2": TrendMetric(
                "metric2", [3, 2, 1], ["a", "b", "c"], "decreasing", 0.8, 0.7
            ),
            "metric3": TrendMetric(
                "metric3", [2, 2, 2], ["a", "b", "c"], "stable", 0.1, 0.1
            ),
        }
        changes = []

        summary = self.analyzer._generate_summary(trends, changes)

        assert summary["total_metrics_analyzed"] == 3
        assert summary["significant_changes_detected"] == 0
        assert "metric1" in summary["trending_up"]
        assert "metric2" in summary["trending_down"]
        assert "metric3" in summary["stable_metrics"]
        assert len(summary["strongest_trends"]) == 3

    def test_get_date_range(self):
        """Test date range calculation."""
        entries = [
            {"timestamp": "2024-01-01T10:00:00"},
            {"timestamp": "2024-01-05T15:00:00"},
            {"timestamp": "2024-01-03T12:00:00"},
        ]

        date_range = self.analyzer._get_date_range(entries)

        assert date_range["start"] == "2024-01-01T10:00:00"
        assert date_range["end"] == "2024-01-05T15:00:00"

    def test_get_date_range_empty(self):
        """Test date range calculation with empty entries."""
        date_range = self.analyzer._get_date_range([])

        assert date_range["start"] is None
        assert date_range["end"] is None

    def test_normalization_enabled(self):
        """Test trend analysis with normalization enabled."""
        analyzer = TrendAnalyzer(normalize=True)
        values = [10, 20, 30]
        timeframes = ["2024-01-01", "2024-01-02", "2024-01-03"]

        trend = analyzer._analyze_metric_trend("test_metric", values, timeframes)

        # Values should be normalized to 0-1 scale
        max_normalized = max(trend.values)
        assert max_normalized == 1.0

    def test_group_by_time_period(self):
        """Test grouping entries by time period."""
        entries = [
            {"timestamp": "2024-01-01T10:00:00", "title": "Video 1"},
            {"timestamp": "2024-01-01T11:00:00", "title": "Video 2"},
            {"timestamp": "2024-01-02T10:00:00", "title": "Video 3"},
        ]

        periods = self.analyzer._group_by_time_period(entries)

        assert len(periods) == 2
        assert "2024-01-01" in periods
        assert "2024-01-02" in periods
        assert len(periods["2024-01-01"]) == 2
        assert len(periods["2024-01-02"]) == 1

    def test_weekly_period_analysis(self):
        """Test trend analysis with weekly periods."""
        analyzer = TrendAnalyzer(period_type="weekly")
        entries = [
            {"timestamp": "2024-01-01T10:00:00", "title": "Video 1", "duration": 600},
            {"timestamp": "2024-01-08T10:00:00", "title": "Video 2", "duration": 900},
        ]

        result = analyzer.analyze_trends(entries)

        assert result["period_type"] == "weekly"
        assert len(result["timeframes"]) == 2

    def test_monthly_period_analysis(self):
        """Test trend analysis with monthly periods."""
        analyzer = TrendAnalyzer(period_type="monthly")
        entries = [
            {"timestamp": "2024-01-15T10:00:00", "title": "Video 1", "duration": 600},
            {"timestamp": "2024-02-15T10:00:00", "title": "Video 2", "duration": 900},
        ]

        result = analyzer.analyze_trends(entries)

        assert result["period_type"] == "monthly"
        assert len(result["timeframes"]) == 2

    def test_specific_metrics_analysis(self):
        """Test trend analysis with specific metrics only."""
        entries = [
            {"timestamp": "2024-01-01T10:00:00", "title": "Video 1", "duration": 600},
            {"timestamp": "2024-01-02T10:00:00", "title": "Video 2", "duration": 900},
        ]

        result = self.analyzer.analyze_trends(
            entries, metrics=["video_count", "total_duration"]
        )

        assert "video_count" in result["metrics"]
        assert "total_duration" in result["metrics"]
        assert "avg_duration" not in result["metrics"]  # Not requested

    def test_engagement_metrics_calculation(self):
        """Test calculation of engagement metrics when available."""
        time_periods = {
            "2024-01-01": [{"engagement_score": 0.8}, {"engagement_score": 0.9}]
        }

        metrics = self.analyzer._calculate_period_metrics(time_periods)

        assert "avg_engagement" in metrics
        assert (
            abs(metrics["avg_engagement"][0] - 0.85) < 0.001
        )  # Use approximate equality for floating point

    def test_viewing_velocity_calculation(self):
        """Test viewing velocity calculation."""
        time_periods = {
            "2024-01-01": [
                {"duration": 3600},  # 1 hour
                {"duration": 1800},  # 30 minutes
            ]
        }

        metrics = self.analyzer._calculate_period_metrics(time_periods)

        # 2 videos in 1.5 hours = 1.33 videos per hour
        assert abs(metrics["viewing_velocity"][0] - 1.333) < 0.01

    def test_viewing_velocity_zero_duration(self):
        """Test viewing velocity calculation with zero total duration."""
        time_periods = {"2024-01-01": [{"duration": 0}, {"duration": 0}]}

        metrics = self.analyzer._calculate_period_metrics(time_periods)

        assert metrics["viewing_velocity"][0] == 0
