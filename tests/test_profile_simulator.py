from datetime import datetime, timedelta

import numpy as np
import pytest

from rabbitmirror.profile_simulator import ProfileSimulator


@pytest.fixture
def sample_profile():
    """Sample profile data for testing."""
    base_time = datetime(2023, 12, 1, 10, 0, 0)
    return [
        {
            "title": "Python Tutorial - Learn Basics",
            "timestamp": base_time.isoformat(),
            "category": "educational",
        },
        {
            "title": "Amazing Music Video - Artist Name",
            "timestamp": (base_time + timedelta(hours=2)).isoformat(),
            "category": "music",
        },
        {
            "title": "Gaming Stream EP.1 - Game Title",
            "timestamp": (base_time + timedelta(hours=4)).isoformat(),
            "category": "gaming",
        },
        {
            "title": "Daily Vlog [Life Update]",
            "timestamp": (base_time + timedelta(days=1, hours=1)).isoformat(),
            "category": "vlog",
        },
        {
            "title": "How to Guide for Beginners (Tutorial)",
            "timestamp": (base_time + timedelta(days=1, hours=3)).isoformat(),
            "category": "educational",
        },
    ]


class TestProfileSimulator:
    """Test suite for the ProfileSimulator class."""

    def test_initialization_default(self):
        """Test ProfileSimulator initialization with default parameters."""
        simulator = ProfileSimulator()
        assert simulator.time_bins == 24
        assert simulator.interval_bins == 50
        assert simulator.rng is not None
        assert simulator.scaler is not None

    def test_initialization_with_seed(self):
        """Test ProfileSimulator initialization with custom seed."""
        seed = 42
        simulator = ProfileSimulator(seed=seed)
        assert (
            simulator.rng.get_state()[1][0]
            == np.random.RandomState(seed).get_state()[1][0]
        )

    def test_simulate_profile_basic(self, sample_profile):
        """Test basic profile simulation functionality."""
        simulator = ProfileSimulator(seed=42)
        simulated = simulator.simulate_profile(sample_profile, duration_days=5)

        assert isinstance(simulated, list)
        assert len(simulated) > 0

        # Check structure of simulated entries
        for entry in simulated:
            assert "title" in entry
            assert "timestamp" in entry
            assert "category" in entry
            assert "simulated" in entry
            assert entry["simulated"] is True

    def test_simulate_profile_duration(self, sample_profile):
        """Test that simulation respects duration parameter."""
        simulator = ProfileSimulator(seed=42)

        # Test different durations
        short_sim = simulator.simulate_profile(sample_profile, duration_days=1)
        long_sim = simulator.simulate_profile(sample_profile, duration_days=10)

        # Longer duration should generally produce more entries
        assert len(long_sim) >= len(short_sim)

    def test_extract_viewing_patterns(self, sample_profile):
        """Test pattern extraction from profile."""
        simulator = ProfileSimulator()
        patterns = simulator._extract_viewing_patterns(sample_profile)

        required_keys = [
            "time_dist",
            "content_dist",
            "interval_dist",
            "daily_counts",
            "title_patterns",
        ]
        for key in required_keys:
            assert key in patterns

        # Test time distribution
        assert isinstance(patterns["time_dist"], np.ndarray)
        assert len(patterns["time_dist"]) == 24
        assert np.isclose(patterns["time_dist"].sum(), 1.0)

        # Test content distribution
        assert isinstance(patterns["content_dist"], dict)
        assert len(patterns["content_dist"]) > 0
        assert all(isinstance(v, float) for v in patterns["content_dist"].values())

        # Test daily counts
        assert isinstance(patterns["daily_counts"], tuple)
        assert len(patterns["daily_counts"]) == 2  # mean, std

    def test_generate_timeline(self):
        """Test timeline generation."""
        simulator = ProfileSimulator()
        timeline = simulator._generate_timeline(7)

        assert len(timeline) == 7
        assert all(isinstance(dt, datetime) for dt in timeline)

        # Check that dates are consecutive
        for i in range(1, len(timeline)):
            diff = timeline[i] - timeline[i - 1]
            assert diff == timedelta(days=1)

    def test_analyze_time_distribution(self, sample_profile):
        """Test time distribution analysis."""
        simulator = ProfileSimulator()
        time_dist = simulator._analyze_time_distribution(sample_profile)

        assert isinstance(time_dist, np.ndarray)
        assert len(time_dist) == 24
        assert np.isclose(time_dist.sum(), 1.0)
        assert all(prob >= 0 for prob in time_dist)

    def test_analyze_content_distribution(self, sample_profile):
        """Test content distribution analysis."""
        simulator = ProfileSimulator()
        content_dist = simulator._analyze_content_distribution(sample_profile)

        assert isinstance(content_dist, dict)
        assert len(content_dist) > 0

        # Check that probabilities sum to 1
        total_prob = sum(content_dist.values())
        assert np.isclose(total_prob, 1.0)

        # Should identify educational content
        assert "educational" in content_dist
        assert content_dist["educational"] > 0

    def test_analyze_interval_distribution(self, sample_profile):
        """Test interval distribution analysis."""
        simulator = ProfileSimulator()
        interval_dist = simulator._analyze_interval_distribution(sample_profile)

        assert isinstance(interval_dist, np.ndarray)
        assert len(interval_dist) == 50  # interval_bins
        assert np.isclose(interval_dist.sum(), 1.0)

    def test_analyze_interval_distribution_empty(self):
        """Test interval distribution with empty or single entry."""
        simulator = ProfileSimulator()

        # Test with empty profile
        empty_dist = simulator._analyze_interval_distribution([])
        assert isinstance(empty_dist, np.ndarray)
        assert len(empty_dist) == 1
        assert empty_dist[0] == 30  # Default value

        # Test with single entry
        single_entry = [{"timestamp": datetime.now().isoformat()}]
        single_dist = simulator._analyze_interval_distribution(single_entry)
        assert isinstance(single_dist, np.ndarray)

    def test_analyze_daily_counts(self, sample_profile):
        """Test daily count analysis."""
        simulator = ProfileSimulator()
        mean, std = simulator._analyze_daily_counts(sample_profile)

        assert isinstance(mean, (int, float))
        assert isinstance(std, (int, float))
        assert mean > 0
        assert std >= 0

    def test_analyze_title_patterns(self, sample_profile):
        """Test title pattern analysis."""
        simulator = ProfileSimulator()
        title_patterns = simulator._analyze_title_patterns(sample_profile)

        assert isinstance(title_patterns, dict)
        # Should extract patterns from titles with categories
        assert len(title_patterns) >= 0

    def test_extract_title_patterns(self):
        """Test individual title pattern extraction."""
        simulator = ProfileSimulator()

        # Test different title formats
        test_cases = [
            ("Artist - Song Title", ["CREATOR - CONTENT"]),
            ("Game Series EP.1", ["SERIES_WITH_EPISODE"]),
            ("Title with (Details)", ["TITLE_WITH_PARENTHESES"]),
            ("Title with [Info]", ["TITLE_WITH_BRACKETS"]),
            ("Simple Title", ["SIMPLE_TITLE"]),
            (
                "Complex - Title EP.5 (Info) [Tag]",
                [
                    "CREATOR - CONTENT",
                    "SERIES_WITH_EPISODE",
                    "TITLE_WITH_PARENTHESES",
                    "TITLE_WITH_BRACKETS",
                ],
            ),
        ]

        for title, expected_patterns in test_cases:
            patterns = simulator._extract_title_patterns(title)
            for pattern in expected_patterns:
                assert pattern in patterns

    def test_sample_daily_count(self):
        """Test daily count sampling."""
        simulator = ProfileSimulator(seed=42)
        count_stats = (5.0, 2.0)  # mean=5, std=2

        # Sample multiple times to test distribution
        samples = [simulator._sample_daily_count(count_stats) for _ in range(100)]

        assert all(count >= 1 for count in samples)  # Should be at least 1
        assert all(isinstance(count, int) for count in samples)

        # Mean should be roughly around the expected value
        mean_sample = np.mean(samples)
        assert 3 <= mean_sample <= 7  # Allow some variance

    def test_sample_from_distribution(self):
        """Test sampling from probability distribution."""
        simulator = ProfileSimulator(seed=42)
        dist = np.array([0.1, 0.3, 0.4, 0.2])

        # Sample multiple times
        samples = [simulator._sample_from_distribution(dist) for _ in range(1000)]

        # All samples should be valid indices
        assert all(0 <= sample < len(dist) for sample in samples)

        # Distribution should roughly match the input
        sample_counts = np.bincount(samples, minlength=len(dist))
        sample_probs = sample_counts / len(samples)

        # Allow some tolerance for random variation
        for i, expected_prob in enumerate(dist / dist.sum()):
            assert abs(sample_probs[i] - expected_prob) < 0.1

    def test_sample_from_dict(self):
        """Test sampling from dictionary distribution."""
        simulator = ProfileSimulator(seed=42)
        dist = {"educational": 0.4, "music": 0.3, "gaming": 0.2, "other": 0.1}

        # Sample multiple times
        samples = [simulator._sample_from_dict(dist) for _ in range(1000)]

        # All samples should be valid keys
        assert all(sample in dist.keys() for sample in samples)

        # Check rough distribution
        from collections import Counter

        sample_counts = Counter(samples)
        for key, expected_prob in dist.items():
            actual_prob = sample_counts[key] / len(samples)
            assert abs(actual_prob - expected_prob) < 0.1

    def test_generate_title(self):
        """Test title generation."""
        simulator = ProfileSimulator(seed=42)

        # Test with patterns
        patterns = {
            "educational": ["CREATOR - CONTENT", "TITLE_WITH_PARENTHESES"],
            "music": ["CREATOR - CONTENT"],
            "gaming": ["SERIES_WITH_EPISODE"],
        }

        # Test different content types
        for content_type in patterns.keys():
            title = simulator._generate_title(patterns, content_type)
            assert isinstance(title, str)
            assert len(title) > 0

        # Test with unknown content type
        unknown_title = simulator._generate_title(patterns, "unknown")
        assert isinstance(unknown_title, str)
        assert "Simulated Unknown Video" in unknown_title

        # Test with empty patterns
        empty_title = simulator._generate_title({}, "educational")
        assert isinstance(empty_title, str)
        assert "Simulated Educational Video" in empty_title

    def test_generate_daily_entries(self, sample_profile):
        """Test daily entry generation."""
        simulator = ProfileSimulator(seed=42)
        patterns = simulator._extract_viewing_patterns(sample_profile)
        start_time = datetime(2023, 12, 15, 0, 0, 0)
        count = 3

        entries = simulator._generate_daily_entries(start_time, patterns, count)

        assert len(entries) == count
        for entry in entries:
            assert "title" in entry
            assert "timestamp" in entry
            assert "category" in entry
            assert "simulated" in entry
            assert entry["simulated"] is True

            # Check timestamp is on the correct day
            entry_time = datetime.fromisoformat(entry["timestamp"])
            assert entry_time.date() == start_time.date()

    def test_reproducibility_with_seed(self, sample_profile):
        """Test that results are reproducible with the same seed."""
        seed = 42
        duration_days = 3

        sim1 = ProfileSimulator(seed=seed)
        result1 = sim1.simulate_profile(sample_profile, duration_days)

        sim2 = ProfileSimulator(seed=seed)
        result2 = sim2.simulate_profile(sample_profile, duration_days)

        # Results should be identical with same seed
        assert len(result1) == len(result2)
        for entry1, entry2 in zip(result1, result2):
            assert entry1["title"] == entry2["title"]
            assert entry1["timestamp"] == entry2["timestamp"]
            assert entry1["category"] == entry2["category"]

    def test_different_seeds_produce_different_results(self, sample_profile):
        """Test that different seeds produce different results."""
        duration_days = 5

        sim1 = ProfileSimulator(seed=42)
        result1 = sim1.simulate_profile(sample_profile, duration_days)

        sim2 = ProfileSimulator(seed=123)
        result2 = sim2.simulate_profile(sample_profile, duration_days)

        # Results should be different with different seeds
        # (Very unlikely to be identical by chance)
        assert result1 != result2
