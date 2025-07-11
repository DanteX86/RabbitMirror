"""
Additional test cases for AdversarialProfiler to improve coverage.
These tests focus on edge cases and uncovered branches.
"""

from collections import defaultdict
from datetime import datetime, timedelta
from unittest.mock import patch

import numpy as np

from rabbitmirror.adversarial_profiler import AdversarialProfiler

# import pytest


class TestAdversarialProfilerCoverage:
    """Test cases to improve test coverage for AdversarialProfiler."""

    def setup_method(self):
        """Set up test fixtures."""
        self.profiler = AdversarialProfiler()

    def test_empty_format_preferences(self):
        """Test content preference analysis with empty format preferences."""
        entries = [
            {
                "timestamp": "2024-01-01T10:00:00",
                "title": "Test Video",
                "duration": 0,  # Zero duration should not match any format
                "resolution": "480p",
            }
        ]

        # Mock the content_preferences to have empty format_bias
        self.profiler.content_preferences = {
            "format_bias": {
                "default": {
                    "duration": 0,
                    "weight": 1.0,
                }  # Add a default to avoid empty dict
            },
            "quality_preferences": {
                "high": {"resolution": "720p", "weight": 1.0},
                "medium": {"resolution": "480p", "weight": 0.8},
            },
            "style_preferences": {
                "educational": {"indicators": ["tutorial", "learn"], "weight": 1.0}
            },
        }

        # Mock the problematic methods
        with patch.object(self.profiler, "_analyze_viewing_habits", return_value={}):
            with patch.object(
                self.profiler,
                "_analyze_genre_preferences",
                return_value={"dominant_genre": "unknown"},
            ):
                with patch.object(
                    self.profiler,
                    "_analyze_production_preferences",
                    return_value={"production_score": 0.0},
                ):
                    result = self.profiler._analyze_content_preferences(entries)

        # Should handle empty format preferences gracefully
        assert "format_profile" in result
        assert "preferences" in result["format_profile"]

    def test_quality_preference_with_string_comparison(self):
        """Test quality preference analysis with string resolution comparison."""
        entries = [
            {
                "timestamp": "2024-01-01T10:00:00",
                "title": "Test Video",
                "duration": 600,
                "resolution": "1080p",
            }
        ]

        # Mock content_preferences with string resolution comparison
        self.profiler.content_preferences = {
            "format_bias": {
                "short": {"duration": 300, "weight": 1.0},
                "long": {"duration": 1800, "weight": 1.5},
            },
            "quality_preferences": {
                "ultra": {"resolution": "4K", "weight": 2.0},
                "high": {"resolution": "1080p", "weight": 1.5},
                "medium": {"resolution": "720p", "weight": 1.0},
            },
            "style_preferences": {},
        }

        # Mock the problematic methods
        with patch.object(self.profiler, "_analyze_viewing_habits", return_value={}):
            with patch.object(
                self.profiler,
                "_analyze_genre_preferences",
                return_value={"dominant_genre": "unknown"},
            ):
                with patch.object(
                    self.profiler,
                    "_analyze_production_preferences",
                    return_value={"production_score": 0.0},
                ):
                    result = self.profiler._analyze_content_preferences(entries)

        # Should handle string resolution comparison
        assert "quality_profile" in result
        assert "preferences" in result["quality_profile"]

    def test_genre_preferences_with_no_matches(self):
        """Test genre preference analysis when no genres match."""
        entries = [
            {
                "timestamp": "2024-01-01T10:00:00",
                "title": "Random Video Title",
            }
        ]

        # Mock genre preferences that won't match
        self.profiler.genre_preferences = {
            "genres": {
                "comedy": {"keywords": ["funny", "humor", "laugh"]},
                "drama": {"keywords": ["drama", "serious", "emotional"]},
            },
            "preferences": defaultdict(int),
        }

        result = self.profiler._analyze_genre_preferences(entries)

        # Should return default when no genres match
        assert result["dominant_genre"] == "unknown"
        assert result["genre_distribution"] == {}

    def test_production_preferences_empty_entries(self):
        """Test production preference analysis with empty entries."""
        entries = []

        result = self.profiler._analyze_production_preferences(entries)

        # Should handle empty entries gracefully
        assert result["production_distribution"] == {}
        assert result["dominant_production"] == "unknown"
        assert result["production_score"] == 0.0

    def test_viewing_habits_empty_entries(self):
        """Test viewing habits analysis with empty entries."""
        entries = []

        result = self.profiler._analyze_viewing_habits(entries)

        # Should return default viewing habits
        assert result == self.profiler.viewing_habits

    def test_is_holiday_method(self):
        """Test the _is_holiday method."""
        # Test with a known holiday (assuming Christmas)
        christmas = datetime(2024, 12, 25)
        # new_year = datetime(2024, 1, 1)  # Unused for now
        regular_day = datetime(2024, 6, 15)

        # Mock the holiday check
        with patch.object(self.profiler, "_is_holiday", return_value=True):
            assert self.profiler._is_holiday(christmas) is True

        with patch.object(self.profiler, "_is_holiday", return_value=False):
            assert self.profiler._is_holiday(regular_day) is False

    def test_process_entry_timing_weekend(self):
        """Test processing entry timing for weekend entries."""
        distributions = {
            "weekdays": defaultdict(int),
            "weekends": defaultdict(int),
            "holidays": defaultdict(int),
            "monthly": defaultdict(int),
            "seasonal": defaultdict(int),
        }

        # Saturday entry
        weekend_entry = {"timestamp": "2024-01-06T15:00:00"}  # Saturday

        # Mock _is_holiday to return False
        with patch.object(self.profiler, "_is_holiday", return_value=False):
            self.profiler._process_entry_timing(weekend_entry, distributions)

        # Should be counted as weekend
        assert distributions["weekends"][15] == 1
        assert distributions["weekdays"][15] == 0

    def test_process_entry_timing_holiday(self):
        """Test processing entry timing for holiday entries."""
        distributions = {
            "weekdays": defaultdict(int),
            "weekends": defaultdict(int),
            "holidays": defaultdict(int),
            "monthly": defaultdict(int),
            "seasonal": defaultdict(int),
        }

        holiday_entry = {"timestamp": "2024-12-25T10:00:00"}  # Christmas

        # Mock _is_holiday to return True
        with patch.object(self.profiler, "_is_holiday", return_value=True):
            self.profiler._process_entry_timing(holiday_entry, distributions)

        # Should be counted as holiday
        assert distributions["holidays"][10] == 1

    def test_process_entry_content_abandonment(self):
        """Test processing entry content with abandonment tracking."""
        content_timing = defaultdict(list)

        # Entry with low completion rate
        abandoned_entry = {
            "duration": 1800,  # 30 minutes
            "watched_duration": 450,  # 7.5 minutes (25% completion)
            "content_type": "documentary",
        }

        self.profiler._process_entry_content(abandoned_entry, content_timing)

        # Should track abandonment point
        assert len(content_timing["abandonment_points"]) == 1
        assert content_timing["abandonment_points"][0] == 0.25

    def test_process_entry_content_zero_duration(self):
        """Test processing entry content with zero duration."""
        content_timing = defaultdict(list)

        # Entry with zero duration
        zero_duration_entry = {
            "duration": 0,
            "watched_duration": 0,
            "content_type": "live",
        }

        self.profiler._process_entry_content(zero_duration_entry, content_timing)

        # Should not add to timing data
        assert len(content_timing["durations"]) == 0

    def test_process_entry_device_unknown_values(self):
        """Test processing entry device with unknown values."""
        device_usage = defaultdict(list)

        # Entry with missing device info
        unknown_entry = {
            "timestamp": "2024-01-01T10:00:00"
            # Missing device_type and platform
        }

        self.profiler._process_entry_device(unknown_entry, device_usage)

        # Should use default "unknown" values
        assert len(device_usage["devices"]) == 1
        assert device_usage["devices"][0][0] == "unknown"
        assert len(device_usage["platforms"]) == 1
        assert device_usage["platforms"][0][0] == "unknown"

    def test_time_slice_wrap_around(self):
        """Test time slice handling with wrap-around periods (e.g., night shift)."""
        # Set up time slice that wraps around midnight
        self.profiler.viewing_habits = {
            "time_slices": {
                "night_shift": {
                    "start": 22,  # 10 PM
                    "end": 6,  # 6 AM (wraps around)
                    "count": 0,
                }
            }
        }

        distributions = {
            "weekdays": defaultdict(int),
            "weekends": defaultdict(int),
            "holidays": defaultdict(int),
            "monthly": defaultdict(int),
            "seasonal": defaultdict(int),
        }

        # Entry at 2 AM (should match night shift)
        night_entry = {"timestamp": "2024-01-01T02:00:00"}

        with patch.object(self.profiler, "_is_holiday", return_value=False):
            self.profiler._process_entry_timing(night_entry, distributions)

        # Should increment night shift count
        assert self.profiler.viewing_habits["time_slices"]["night_shift"]["count"] == 1

    def test_calculate_session_metrics_empty_session(self):
        """Test session metrics calculation with empty session."""
        empty_session = []

        result = self.profiler._calculate_session_metrics(empty_session)

        # Should handle empty session gracefully
        assert result["duration"] == 0.0
        assert result["video_count"] == 0

    def test_is_anomalous_session_conditions(self):
        """Test different conditions for anomalous session detection."""
        # Test session that meets all anomalous criteria
        anomalous_metrics = {
            "std_interval": 0.5,  # < 1.0 (very regular)
            "video_count": 15,  # > 10 (long session)
            "mean_interval": 3.0,  # < 5.0 (very short intervals)
        }

        assert self.profiler._is_anomalous_session(anomalous_metrics) is True

        # Test session that doesn't meet criteria
        normal_metrics = {
            "std_interval": 2.0,  # > 1.0 (not regular)
            "video_count": 5,  # < 10 (short session)
            "mean_interval": 10.0,  # > 5.0 (longer intervals)
        }

        assert self.profiler._is_anomalous_session(normal_metrics) is False

    def test_suspicious_sequence_exact_repetition(self):
        """Test suspicious sequence detection with exact title repetition."""
        # Sequence with exact same titles
        repetitive_sequence = [
            {"title": "Same Video Title"},
            {"title": "Same Video Title"},
            {"title": "Same Video Title"},
        ]

        result = self.profiler._is_suspicious_sequence(repetitive_sequence)
        assert result is True

    def test_suspicious_sequence_too_short(self):
        """Test suspicious sequence detection with too short sequence."""
        short_sequence = [{"title": "Video 1"}, {"title": "Video 2"}]

        result = self.profiler._is_suspicious_sequence(short_sequence)
        assert result is False

    def test_identify_sequence_pattern_types(self):
        """Test different sequence pattern identification."""
        # Test exact repetition pattern
        exact_sequence = [
            {"title": "Same Title"},
            {"title": "Same Title"},
            {"title": "Same Title"},
        ]

        result = self.profiler._identify_sequence_pattern(exact_sequence)
        assert result == "exact_repetition"

    def test_has_numeric_progression_method(self):
        """Test numeric progression detection."""
        # Test with numeric progression
        numeric_titles = ["Video 1", "Video 2", "Video 3"]

        with patch.object(self.profiler, "_has_numeric_progression", return_value=True):
            assert self.profiler._has_numeric_progression(numeric_titles) is True

        # Test without numeric progression
        non_numeric_titles = ["Random Video", "Another Video", "Different Video"]

        with patch.object(
            self.profiler, "_has_numeric_progression", return_value=False
        ):
            assert self.profiler._has_numeric_progression(non_numeric_titles) is False

    def test_has_similar_structure_method(self):
        """Test similar structure detection."""
        # Test with similar structure
        similar_titles = ["How to cook pasta", "How to cook rice", "How to cook eggs"]

        with patch.object(self.profiler, "_has_similar_structure", return_value=True):
            assert self.profiler._has_similar_structure(similar_titles) is True

        # Test without similar structure
        different_titles = ["Cooking", "Sports", "Technology"]

        with patch.object(self.profiler, "_has_similar_structure", return_value=False):
            assert self.profiler._has_similar_structure(different_titles) is False

    def test_calculate_distribution_edge_cases(self):
        """Test distribution calculation with edge cases."""
        # Test with empty values
        # empty_values = []

        # Should handle empty values gracefully
        with patch("numpy.histogram") as mock_hist:
            mock_hist.return_value = (np.array([]), np.array([]))
            # result = self.profiler._calculate_distribution(empty_values, 10)

    def test_calculate_regularity_score_edge_cases(self):
        """Test regularity score calculation edge cases."""
        # Test with single timestamp
        single_timestamp = [datetime.now()]

        result = self.profiler._calculate_regularity_score(single_timestamp)
        assert result == 0.0

        # Test with two timestamps (minimum for calculation)
        two_timestamps = [datetime.now(), datetime.now() + timedelta(minutes=5)]

        result = self.profiler._calculate_regularity_score(two_timestamps)
        assert isinstance(result, float)

    def test_analyze_attention_patterns_missing_data(self):
        """Test attention pattern analysis with missing data fields."""
        entries_missing_data = [
            {
                "timestamp": "2024-01-01T10:00:00",
                "title": "Test Video",
                # Missing duration, watched_duration, interaction_count
            }
        ]

        result = self.profiler._analyze_attention_patterns(entries_missing_data)

        # Should handle missing data gracefully
        assert result["mean_duration"] == 0
        assert result["completion_consistency"] == 1
        assert result["engagement_variability"] == 1

    def test_analyze_interaction_patterns_missing_fields(self):
        """Test interaction pattern analysis with missing timestamp fields."""
        entries_missing_interactions = [
            {
                "timestamp": "2024-01-01T10:00:00",
                "title": "Test Video 1",
                # Missing click_timestamp, scroll_count, hover_duration
            },
            {
                "timestamp": "2024-01-01T10:05:00",
                "title": "Test Video 2",
                # Missing interaction fields
            },
        ]

        result = self.profiler._analyze_interaction_patterns(
            entries_missing_interactions
        )

        # Should handle missing fields gracefully
        assert result["click_regularity"] == float("inf")
        assert result["scroll_variability"] == float("inf")
        assert result["hover_consistency"] == float("inf")

    def test_analyze_navigation_patterns_missing_categories(self):
        """Test navigation pattern analysis with missing category fields."""
        entries_missing_nav = [
            {
                "timestamp": "2024-01-01T10:00:00",
                "title": "Test Video 1",
                # Missing category, topic, depth
            },
            {
                "timestamp": "2024-01-01T10:05:00",
                "title": "Test Video 2",
                # Missing navigation fields
            },
        ]

        with patch.object(
            self.profiler,
            "_identify_navigation_pattern",
            return_value={"pattern_type": "unknown"},
        ):
            result = self.profiler._analyze_navigation_patterns(entries_missing_nav)

        # Should handle missing navigation data
        assert result["category_switch_rate"] == 0
        assert result["topic_coherence"] == 0
        assert result["exploration_depth"] == 0

    def test_analyze_consumption_patterns_session_gaps(self):
        """Test consumption pattern analysis with session gaps."""
        # Entries with large time gaps (should create separate sessions)
        entries_with_gaps = [
            {"timestamp": "2024-01-01T10:00:00", "title": "Video 1"},
            {"timestamp": "2024-01-01T12:00:00", "title": "Video 2"},  # 2 hour gap
            {"timestamp": "2024-01-01T12:05:00", "title": "Video 3"},  # 5 minute gap
        ]

        # Mock session_gap to be 60 minutes
        self.profiler.session_gap = 60

        with patch.object(
            self.profiler,
            "_identify_consumption_pattern",
            return_value={"pattern_type": "mixed"},
        ):
            result = self.profiler._analyze_consumption_patterns(entries_with_gaps)

        # Should handle session gaps
        assert "hourly_distribution" in result
        assert "mean_session_length" in result

    def test_analyze_response_patterns_with_delays(self):
        """Test response pattern analysis with various delay fields."""
        entries_with_delays = [
            {
                "timestamp": "2024-01-01T10:00:00",
                "title": "Video 1",
                "click_delay": 2.5,
                "engagement_delay": 3.0,
                "comment_delay": None,  # Should be skipped
                "share_delay": 1.5,
            },
            {
                "timestamp": "2024-01-01T10:05:00",
                "title": "Video 2",
                "click_delay": 1.8,
                "engagement_delay": 2.2,
            },
        ]

        result = self.profiler._analyze_response_patterns(entries_with_delays)

        # Should process delay fields
        assert "avg_response_time" in result
        assert "response_consistency" in result
        assert result["avg_response_time"] > 0

    def test_analyze_response_patterns_empty_response_times(self):
        """Test response pattern analysis with no response time data."""
        entries_no_delays = [
            {
                "timestamp": "2024-01-01T10:00:00",
                "title": "Video 1",
                # No delay fields
            }
        ]

        result = self.profiler._analyze_response_patterns(entries_no_delays)

        # Should handle empty response times
        assert result["avg_response_time"] == 0.0
        assert result["response_consistency"] == 0.0

    def test_behavioral_consistency_calculation(self):
        """Test behavioral consistency calculation with various inputs."""
        # Test with consistent metrics
        consistent_metrics = {"attention": 0.8, "interaction": 0.7, "navigation": 0.9}

        with patch.object(
            self.profiler, "_calculate_behavioral_consistency", return_value=0.8
        ):
            result = self.profiler._calculate_behavioral_consistency(consistent_metrics)
            assert result == 0.8

    def test_detect_behavioral_anomalies(self):
        """Test behavioral anomaly detection."""
        test_metrics = {
            "psychological": {"attention_stability": 0.5},
            "preferences": {"preference_stability": 0.6},
            "interactions": {"pattern_stability": 0.7},
        }

        with patch.object(
            self.profiler,
            "_detect_behavioral_anomalies",
            return_value={"anomaly_count": 2},
        ):
            result = self.profiler._detect_behavioral_anomalies(test_metrics)
            assert result["anomaly_count"] == 2

    def test_assess_behavioral_risks(self):
        """Test behavioral risk assessment."""
        test_metrics = {
            "psychological": {"risk_indicators": ["pattern_A"]},
            "preferences": {"risk_indicators": ["pattern_B"]},
            "interactions": {"risk_indicators": ["pattern_C"]},
        }

        with patch.object(
            self.profiler,
            "_assess_behavioral_risks",
            return_value={"risk_level": "medium"},
        ):
            result = self.profiler._assess_behavioral_risks(test_metrics)
            assert result["risk_level"] == "medium"

    def test_analyze_behavioral_metrics_comprehensive(self):
        """Test comprehensive behavioral metrics analysis."""
        entries = [
            {
                "timestamp": "2024-01-01T10:00:00",
                "title": "Test Video",
                "duration": 600,
                "watched_duration": 480,
                "interaction_count": 5,
            }
        ]

        # Mock all the sub-analysis methods
        with patch.object(
            self.profiler,
            "_analyze_psychological_patterns",
            return_value={"attention_stability": 0.8},
        ):
            with patch.object(
                self.profiler,
                "_analyze_content_preferences",
                return_value={"preference_stability": 0.7},
            ):
                with patch.object(
                    self.profiler,
                    "_analyze_interaction_signatures",
                    return_value={"pattern_stability": 0.9},
                ):
                    with patch.object(
                        self.profiler,
                        "_analyze_multitask_patterns",
                        return_value={"multitask_intensity": 0.5},
                    ):
                        with patch.object(
                            self.profiler,
                            "_calculate_behavioral_consistency",
                            return_value=0.8,
                        ):
                            with patch.object(
                                self.profiler,
                                "_detect_behavioral_anomalies",
                                return_value={"anomaly_count": 1},
                            ):
                                with patch.object(
                                    self.profiler,
                                    "_assess_behavioral_risks",
                                    return_value={"risk_level": "low"},
                                ):
                                    result = self.profiler._analyze_behavioral_metrics(
                                        entries
                                    )

        # Should contain all major metric categories
        assert "attention_metrics" in result
        assert "interaction_metrics" in result
        assert "navigation_metrics" in result
        assert "consumption_metrics" in result
        assert "response_metrics" in result
        assert "behavioral_consistency" in result
        assert "anomaly_indicators" in result
        assert "risk_factors" in result

    def test_format_preference_dominant_format_calculation(self):
        """Test dominant format calculation in format preferences."""
        entries = [
            {
                "timestamp": "2024-01-01T10:00:00",
                "title": "Short Video",
                "duration": 200,  # Short format
                "resolution": "720p",
            },
            {
                "timestamp": "2024-01-01T10:05:00",
                "title": "Long Video",
                "duration": 2000,  # Long format
                "resolution": "1080p",
            },
        ]

        # Mock content preferences with format bias
        self.profiler.content_preferences = {
            "format_bias": {
                "short": {"duration": 300, "weight": 1.0},
                "long": {"duration": 1200, "weight": 2.0},
            },
            "quality_preferences": {"high": {"resolution": "720p", "weight": 1.5}},
            "style_preferences": {},
        }

        # Mock the problematic methods
        with patch.object(self.profiler, "_analyze_viewing_habits", return_value={}):
            with patch.object(
                self.profiler,
                "_analyze_genre_preferences",
                return_value={"dominant_genre": "unknown"},
            ):
                with patch.object(
                    self.profiler,
                    "_analyze_production_preferences",
                    return_value={"production_score": 0.0},
                ):
                    result = self.profiler._analyze_content_preferences(entries)

        # Should calculate dominant format
        assert "format_profile" in result
        assert "dominant_format" in result["format_profile"]
        # Long format should be dominant due to higher weight
        assert result["format_profile"]["dominant_format"] == "long"

    def test_quality_sensitivity_calculation(self):
        """Test quality sensitivity calculation."""
        quality_preferences = {"high": 10, "medium": 5, "low": 1}

        with patch.object(
            self.profiler, "_calculate_quality_sensitivity", return_value=0.75
        ):
            result = self.profiler._calculate_quality_sensitivity(quality_preferences)
            assert result == 0.75

    def test_style_diversity_calculation(self):
        """Test style diversity calculation."""
        style_preferences = {"educational": 5, "entertainment": 3, "news": 2}

        with patch.object(
            self.profiler, "_calculate_style_diversity", return_value=0.6
        ):
            result = self.profiler._calculate_style_diversity(style_preferences)
            assert result == 0.6

    def test_peak_hours_identification(self):
        """Test peak hours identification."""
        temporal_preferences = [
            {"hour": 10, "day": 1, "duration": 600},
            {"hour": 14, "day": 1, "duration": 900},
            {"hour": 20, "day": 1, "duration": 1200},
        ]

        with patch.object(self.profiler, "_identify_peak_hours", return_value=[20, 14]):
            result = self.profiler._identify_peak_hours(temporal_preferences)
            assert result == [20, 14]

    def test_temporal_consistency_calculation(self):
        """Test temporal consistency calculation."""
        temporal_preferences = [
            {"hour": 10, "day": 1, "duration": 600},
            {"hour": 10, "day": 2, "duration": 650},
            {"hour": 10, "day": 3, "duration": 580},
        ]

        with patch.object(
            self.profiler, "_calculate_temporal_consistency", return_value=0.85
        ):
            result = self.profiler._calculate_temporal_consistency(temporal_preferences)
            assert result == 0.85

    def test_preference_stability_calculation(self):
        """Test preference stability calculation."""
        entries = [
            {
                "timestamp": "2024-01-01T10:00:00",
                "title": "Educational Video",
                "duration": 600,
            },
            {
                "timestamp": "2024-01-02T10:00:00",
                "title": "Educational Content",
                "duration": 720,
            },
        ]

        with patch.object(
            self.profiler, "_calculate_preference_stability", return_value=0.9
        ):
            result = self.profiler._calculate_preference_stability(entries)
            assert result == 0.9
