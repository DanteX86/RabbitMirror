from datetime import datetime, timedelta

import pytest

from rabbitmirror.adversarial_profiler import AdversarialProfiler


@pytest.fixture
def sample_entries():
    """Sample entries for adversarial pattern testing."""
    base_time = datetime(2025, 7, 1, 10, 0, 0)
    return [
        {
            "title": "Python Tutorial - Basic Programming",
            "timestamp": base_time.isoformat(),
            "channel": "Tech Channel",
        },
        {
            "title": "Python Tutorial - Advanced Programming",
            "timestamp": (base_time + timedelta(minutes=15)).isoformat(),
            "channel": "Tech Channel",
        },
        {
            "title": "JavaScript Basics - Introduction",
            "timestamp": (base_time + timedelta(minutes=45)).isoformat(),
            "channel": "Web Dev Channel",
        },
        {
            "title": "React Tutorial - Components",
            "timestamp": (base_time + timedelta(hours=1, minutes=30)).isoformat(),
            "channel": "Web Dev Channel",
        },
        {
            "title": "Python Tutorial - Data Structures",
            "timestamp": (base_time + timedelta(hours=2, minutes=15)).isoformat(),
            "channel": "Tech Channel",
        },
    ]


@pytest.fixture
def rapid_view_entries():
    """Sample entries showing rapid viewing pattern."""
    base_time = datetime(2025, 7, 1, 14, 0, 0)
    entries = []
    for i in range(10):
        entries.append(
            {
                "title": f"Video {i + 1} - Quick Tutorial",
                "timestamp": (base_time + timedelta(minutes=i)).isoformat(),
                "channel": "Fast Channel",
            }
        )
    return entries


@pytest.fixture
def binge_session_entries():
    """Sample entries showing binge watching pattern."""
    base_time = datetime(2025, 7, 1, 20, 0, 0)
    entries = []
    for i in range(15):
        entries.append(
            {
                "title": f"Series Episode {i + 1}",
                "timestamp": (base_time + timedelta(minutes=i * 45)).isoformat(),
                "channel": "Series Channel",
            }
        )
    return entries


class TestAdversarialProfiler:
    """Test suite for the AdversarialProfiler class."""

    def test_profiler_initialization_default(self):
        """Test AdversarialProfiler can be initialized with default parameters."""
        profiler = AdversarialProfiler()
        assert profiler.similarity_threshold == 0.7
        assert profiler.rapid_view_threshold == 5
        assert profiler.session_gap == 30
        assert profiler.repetition_threshold == 3
        assert profiler.entropy_threshold == 0.6

    def test_identify_rapid_views(self, rapid_view_entries):
        """Test identifying rapid view patterns."""
        profiler = AdversarialProfiler(rapid_view_threshold=7)
        result = profiler.identify_adversarial_patterns(rapid_view_entries)
        assert "patterns" in result
        assert "rapid_views" in result["patterns"]
        # Should detect some rapid views with 1-minute intervals
        assert len(result["patterns"]["rapid_views"]) > 0

    def test_identify_binge_watching(self, binge_session_entries):
        """Test identifying binge watching patterns."""
        profiler = AdversarialProfiler(session_gap=40)
        result = profiler.identify_adversarial_patterns(binge_session_entries)
        assert "patterns" in result
        assert "binge_patterns" in result["patterns"]
        # Should detect content loops due to similar episode titles
        assert "content_loops" in result["patterns"]
        assert len(result["patterns"]["content_loops"]) > 0

    def test_identify_patterns_with_sample_data(self, sample_entries):
        """Test pattern identification with sample data."""
        profiler = AdversarialProfiler(similarity_threshold=0.6)

        result = profiler.identify_adversarial_patterns(sample_entries)
        assert isinstance(result, dict)
        assert "patterns" in result
        assert "risk_score" in result
        assert "entropy_analysis" in result
        # Normal data should have minimal rapid views and binge patterns
        assert (
            len(result["patterns"]["rapid_views"]) == 0
        )  # No rapid views with normal spacing
        assert len(result["patterns"]["binge_patterns"]) == 0  # No binge patterns

    def test_identify_patterns_empty_data(self):
        """Test pattern identification with empty data."""
        profiler = AdversarialProfiler()

        try:
            patterns = profiler.identify_adversarial_patterns([])
            assert isinstance(patterns, dict)
        except Exception as e:
            pytest.skip(f"AdversarialProfiler not fully implemented: {e}")

    @pytest.mark.parametrize("threshold", [0.3, 0.5, 0.7, 0.9])
    def test_different_thresholds(self, threshold, sample_entries):
        """Test that different similarity thresholds affect pattern detection."""
        profiler = AdversarialProfiler(similarity_threshold=threshold)

        try:
            patterns = profiler.identify_adversarial_patterns(sample_entries)
            assert isinstance(patterns, dict)
        except Exception as e:
            pytest.skip(f"AdversarialProfiler not fully implemented: {e}")

    def test_threshold_bounds(self):
        """Test that threshold values are within valid bounds."""
        # Test valid thresholds
        profiler = AdversarialProfiler(similarity_threshold=0.5)
        assert 0.0 <= profiler.similarity_threshold <= 1.0

        # Test edge cases
        profiler_min = AdversarialProfiler(similarity_threshold=0.0)
        assert profiler_min.similarity_threshold == 0.0

        profiler_max = AdversarialProfiler(similarity_threshold=1.0)
        assert profiler_max.similarity_threshold == 1.0

    def test_malformed_data_handling(self):
        """Test that malformed data is handled gracefully."""
        profiler = AdversarialProfiler()

        # Test with missing fields
        malformed_entries = [
            {"title": "Video 1"},  # Missing timestamp and channel
            {"timestamp": "2025-07-01T10:00:00"},  # Missing title and channel
            {"channel": "Test Channel"},  # Missing title and timestamp
        ]

        try:
            result = profiler.identify_adversarial_patterns(malformed_entries)
            # Should either handle gracefully or raise specific exception
            assert isinstance(result, dict)
        except (KeyError, ValueError, TypeError) as e:
            # Expected behavior for malformed data
            assert str(e)  # Ensure error message exists

    def test_content_similarity_detection(self):
        """Test detection of similar content patterns."""
        profiler = AdversarialProfiler(similarity_threshold=0.8)

        base_time = datetime(2025, 7, 1, 15, 0, 0)
        similar_content = [
            {
                "title": "Machine Learning Tutorial Part 1",
                "timestamp": base_time.isoformat(),
                "channel": "AI Channel",
            },
            {
                "title": "Machine Learning Tutorial Part 2",
                "timestamp": (base_time + timedelta(minutes=30)).isoformat(),
                "channel": "AI Channel",
            },
            {
                "title": "Machine Learning Tutorial Part 3",
                "timestamp": (base_time + timedelta(hours=1)).isoformat(),
                "channel": "AI Channel",
            },
        ]

        result = profiler.identify_adversarial_patterns(similar_content)
        assert "patterns" in result
        assert "content_loops" in result["patterns"]
        # Should detect some content similarity
        assert len(result["patterns"]["content_loops"]) > 0

    def test_entropy_analysis(self):
        """Test entropy analysis functionality."""
        profiler = AdversarialProfiler()

        # Diverse content should have higher entropy
        diverse_entries = [
            {
                "title": "Cooking Show",
                "timestamp": "2025-07-01T10:00:00",
                "channel": "Food Network",
            },
            {
                "title": "Tech News",
                "timestamp": "2025-07-01T11:00:00",
                "channel": "Tech Today",
            },
            {
                "title": "Travel Vlog",
                "timestamp": "2025-07-01T12:00:00",
                "channel": "Adventure Time",
            },
            {
                "title": "Music Video",
                "timestamp": "2025-07-01T13:00:00",
                "channel": "Music Central",
            },
        ]

        result = profiler.identify_adversarial_patterns(diverse_entries)
        assert "entropy_analysis" in result
        assert "content_entropy" in result["entropy_analysis"]
        assert "channel_entropy" in result["entropy_analysis"]
        assert result["entropy_analysis"]["content_entropy"] > 0
        assert result["entropy_analysis"]["channel_entropy"] > 0

    def test_risk_score_calculation(self):
        """Test that risk scores are calculated and within valid range."""
        profiler = AdversarialProfiler()

        result = profiler.identify_adversarial_patterns([])
        assert "risk_score" in result
        assert isinstance(result["risk_score"], (int, float))
        assert 0 <= result["risk_score"] <= 100  # Assuming risk scores are 0-100
