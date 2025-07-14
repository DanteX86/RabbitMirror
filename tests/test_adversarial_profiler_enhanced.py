#!/usr/bin/env python3

"""
Enhanced tests for AdversarialProfiler to achieve higher coverage.
This module focuses on testing specific methods and edge cases.
"""

from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import numpy as np
import pytest

from rabbitmirror.adversarial_profiler import AdversarialProfiler


class TestAdversarialProfilerEnhanced:
    """Enhanced test suite for AdversarialProfiler focusing on coverage gaps."""

    @pytest.fixture
    def profiler(self):
        """Create a standard profiler instance."""
        return AdversarialProfiler()

    @pytest.fixture
    def custom_profiler(self):
        """Create a profiler with custom parameters."""
        return AdversarialProfiler(
            similarity_threshold=0.8,
            rapid_view_threshold=3,
            session_gap=15,
            repetition_threshold=2,
            entropy_threshold=0.7,
            chain_threshold=5,
            time_zone_threshold=2,
            engagement_variance_threshold=0.5,
            confidence_decay_rate=0.05,
            context_weight=0.4,
            pattern_weight=0.3,
            temporal_weight=0.3,
        )

    @pytest.fixture
    def minimal_entries(self):
        """Minimal valid entries for testing."""
        base_time = datetime(2025, 7, 1, 10, 0, 0)
        return [
            {
                "title": "Test Video 1",
                "timestamp": base_time.isoformat(),
                "channel": "Test Channel",
                "url": "https://example.com/1",
            },
            {
                "title": "Test Video 2",
                "timestamp": (base_time + timedelta(minutes=30)).isoformat(),
                "channel": "Test Channel",
                "url": "https://example.com/2",
            },
        ]

    @pytest.fixture
    def comprehensive_entries(self):
        """Comprehensive entries with various fields for testing."""
        base_time = datetime(2025, 7, 1, 10, 0, 0)
        entries = []

        for i in range(20):
            entry = {
                "title": f"Video {i+1} - Programming Tutorial",
                "timestamp": (base_time + timedelta(minutes=i * 30)).isoformat(),
                "channel": f"Channel {i%3}",
                "url": f"https://example.com/video{i+1}",
                "duration": 600 + (i * 60),  # 10-30 minutes
                "watched_duration": 300 + (i * 30),  # 5-15 minutes
                "interaction_count": i * 2,
                "location": f"Location {i%5}",
                "device": ["mobile", "desktop", "tablet"][i % 3],
                "language": ["en", "es", "fr"][i % 3],
                "category": ["education", "entertainment", "news"][i % 3],
            }
            entries.append(entry)

        return entries

    @pytest.fixture
    def rapid_entries(self):
        """Entries with rapid viewing patterns."""
        base_time = datetime(2025, 7, 1, 14, 0, 0)
        entries = []

        for i in range(15):
            entries.append(
                {
                    "title": f"Quick Video {i+1}",
                    "timestamp": (base_time + timedelta(seconds=i * 30)).isoformat(),
                    "channel": "Fast Channel",
                    "url": f"https://example.com/quick{i+1}",
                }
            )

        return entries

    @pytest.fixture
    def similar_content_entries(self):
        """Entries with highly similar content."""
        base_time = datetime(2025, 7, 1, 15, 0, 0)
        return [
            {
                "title": "Python Programming Tutorial Part 1",
                "timestamp": base_time.isoformat(),
                "channel": "Code Channel",
            },
            {
                "title": "Python Programming Tutorial Part 2",
                "timestamp": (base_time + timedelta(minutes=30)).isoformat(),
                "channel": "Code Channel",
            },
            {
                "title": "Python Programming Tutorial Part 3",
                "timestamp": (base_time + timedelta(hours=1)).isoformat(),
                "channel": "Code Channel",
            },
            {
                "title": "Python Programming Tutorial Part 4",
                "timestamp": (base_time + timedelta(hours=1, minutes=30)).isoformat(),
                "channel": "Code Channel",
            },
        ]

    @pytest.fixture
    def binge_entries(self):
        """Entries representing a binge watching session."""
        base_time = datetime(2025, 7, 1, 19, 0, 0)
        entries = []

        for i in range(12):
            entries.append(
                {
                    "title": f"Netflix Series S01E{i+1:02d}",
                    "timestamp": (base_time + timedelta(minutes=i * 50)).isoformat(),
                    "channel": "Netflix",
                    "duration": 2400,  # 40 minutes
                    "watched_duration": 2300,  # Almost complete
                }
            )

        return entries

    def test_empty_result_structure(self, profiler):
        """Test the structure of empty result."""
        result = profiler._empty_result()

        assert isinstance(result, dict)
        assert "risk_score" in result
        assert "patterns" in result
        assert "entropy_analysis" in result
        assert "temporal_analysis" in result
        assert "similarity_stats" in result

        assert result["risk_score"] == 0.0
        assert isinstance(result["patterns"], dict)
        assert isinstance(result["entropy_analysis"], dict)

    def test_identify_patterns_empty_input(self, profiler):
        """Test pattern identification with empty input."""
        result = profiler.identify_adversarial_patterns([])

        assert isinstance(result, dict)
        assert result["risk_score"] == 0.0
        assert all(
            len(pattern_list) == 0 for pattern_list in result["patterns"].values()
        )

    def test_detect_rapid_views_comprehensive(self, profiler, rapid_entries):
        """Test rapid view detection with comprehensive analysis."""
        rapid_views = profiler._detect_rapid_views(rapid_entries)

        assert isinstance(rapid_views, list)
        assert len(rapid_views) > 0

        # Check structure of rapid view entries
        for rapid_view in rapid_views:
            assert "timestamp" in rapid_view
            assert "interval" in rapid_view
            assert "previous_title" in rapid_view
            assert "current_title" in rapid_view
            assert "confidence" in rapid_view
            assert isinstance(rapid_view["confidence"], float)
            assert 0.0 <= rapid_view["confidence"] <= 1.0

    def test_detect_content_loops_with_similar_content(
        self, profiler, similar_content_entries
    ):
        """Test content loop detection with similar content."""
        profiler.similarity_threshold = 0.3  # Lower threshold for testing

        # Create TF-IDF matrix manually
        titles = [entry["title"] for entry in similar_content_entries]
        tfidf_matrix = profiler.vectorizer.fit_transform(titles)

        from sklearn.metrics.pairwise import cosine_similarity

        similarity_matrix = cosine_similarity(tfidf_matrix)

        loops = profiler._detect_content_loops(
            similarity_matrix, similar_content_entries
        )

        assert isinstance(loops, list)
        assert len(loops) > 0

        # Check structure of loop entries
        for loop in loops:
            assert "base_entry" in loop
            assert "similar_entries" in loop
            assert "pattern_duration" in loop
            assert "confidence" in loop
            assert isinstance(loop["confidence"], float)

    def test_detect_binge_patterns_comprehensive(self, profiler, binge_entries):
        """Test binge pattern detection with comprehensive analysis."""
        binge_patterns = profiler._detect_binge_patterns(binge_entries)

        assert isinstance(binge_patterns, list)

        # Check structure of binge patterns
        for pattern in binge_patterns:
            assert "start_time" in pattern
            assert "end_time" in pattern
            assert "video_count" in pattern
            assert "mean_interval" in pattern
            assert "std_interval" in pattern
            assert "confidence" in pattern
            assert isinstance(pattern["confidence"], float)

    def test_detect_anomalous_sessions(self, profiler, comprehensive_entries):
        """Test anomalous session detection."""
        anomalous_sessions = profiler._detect_anomalous_sessions(comprehensive_entries)

        assert isinstance(anomalous_sessions, list)

        # Check structure of anomalous sessions
        for session in anomalous_sessions:
            assert "start_time" in session
            assert "end_time" in session
            assert "video_count" in session
            assert "metrics" in session
            assert "confidence" in session
            assert isinstance(session["metrics"], dict)

    def test_detect_suspicious_sequences(self, profiler, comprehensive_entries):
        """Test suspicious sequence detection."""
        sequences = profiler._detect_suspicious_sequences(comprehensive_entries)

        assert isinstance(sequences, list)

        # Check structure of suspicious sequences
        for sequence in sequences:
            assert "start_time" in sequence
            assert "end_time" in sequence
            assert "titles" in sequence
            assert "pattern_type" in sequence
            assert "confidence" in sequence
            assert isinstance(sequence["titles"], list)
            assert len(sequence["titles"]) >= 3

    def test_calculate_content_entropy(self, profiler, comprehensive_entries):
        """Test content entropy calculation."""
        titles = [entry["title"] for entry in comprehensive_entries]
        entropy = profiler._calculate_content_entropy(titles)

        assert isinstance(entropy, float)
        assert entropy >= 0.0

        # Test with identical titles (should have low entropy)
        identical_titles = ["Same Title"] * 10
        low_entropy = profiler._calculate_content_entropy(identical_titles)
        assert low_entropy < entropy

    def test_calculate_channel_entropy(self, profiler, comprehensive_entries):
        """Test channel entropy calculation."""
        entropy = profiler._calculate_channel_entropy(comprehensive_entries)

        assert isinstance(entropy, float)
        assert entropy >= 0.0

        # Test with entries missing channel info
        entries_no_channel = [{"title": "Test"} for _ in range(5)]
        entropy_no_channel = profiler._calculate_channel_entropy(entries_no_channel)
        assert entropy_no_channel == 0.0

    def test_analyze_temporal_patterns(self, profiler, comprehensive_entries):
        """Test temporal pattern analysis."""
        analysis = profiler._analyze_temporal_patterns(comprehensive_entries)

        assert isinstance(analysis, dict)
        assert "hourly_distribution" in analysis
        assert "weekly_distribution" in analysis
        assert "regularity_score" in analysis

        assert isinstance(analysis["hourly_distribution"], list)
        assert len(analysis["hourly_distribution"]) == 24
        assert isinstance(analysis["weekly_distribution"], list)
        assert len(analysis["weekly_distribution"]) == 7
        assert isinstance(analysis["regularity_score"], float)

    def test_calculate_risk_score(self, profiler):
        """Test risk score calculation."""
        # Test with various metrics
        metrics = {
            "rapid_views": 5,
            "content_loops": 3,
            "binge_patterns": 2,
            "anomalous_sessions": 1,
            "suspicious_sequences": 4,
            "content_entropy": 0.3,
            "channel_entropy": 0.2,
        }

        risk_score = profiler._calculate_risk_score(metrics)

        assert isinstance(risk_score, float)
        assert 0.0 <= risk_score <= 1.0

        # Test with zero metrics
        zero_metrics = {key: 0 for key in metrics.keys()}
        zero_risk = profiler._calculate_risk_score(zero_metrics)
        assert zero_risk > 0.0  # Should be > 0 due to entropy factors

    def test_split_into_sessions(self, profiler, comprehensive_entries):
        """Test session splitting functionality."""
        sessions = profiler._split_into_sessions(comprehensive_entries)

        assert isinstance(sessions, list)
        assert len(sessions) > 0

        # Check that each session contains valid entries
        for session in sessions:
            assert isinstance(session, list)
            assert len(session) > 0
            for entry in session:
                assert isinstance(entry, dict)
                assert "timestamp" in entry

    def test_split_into_sessions_single_entry(self, profiler):
        """Test session splitting with single entry."""
        single_entry = [{"title": "Test", "timestamp": "2025-07-01T10:00:00"}]
        sessions = profiler._split_into_sessions(single_entry)

        assert len(sessions) == 1
        assert len(sessions[0]) == 1

    def test_calculate_intervals(self, profiler, comprehensive_entries):
        """Test interval calculation between entries."""
        intervals = profiler._calculate_intervals(comprehensive_entries)

        assert isinstance(intervals, np.ndarray)
        assert len(intervals) == len(comprehensive_entries) - 1
        assert all(interval > 0 for interval in intervals)

    def test_calculate_intervals_empty_list(self, profiler):
        """Test interval calculation with empty list."""
        intervals = profiler._calculate_intervals([])

        assert isinstance(intervals, np.ndarray)
        assert len(intervals) == 0

    def test_calculate_intervals_single_entry(self, profiler):
        """Test interval calculation with single entry."""
        single_entry = [{"timestamp": "2025-07-01T10:00:00"}]
        intervals = profiler._calculate_intervals(single_entry)

        assert isinstance(intervals, np.ndarray)
        assert len(intervals) == 0

    def test_is_suspicious_interval_pattern(self, profiler):
        """Test suspicious interval pattern detection."""
        # Test with regular intervals (suspicious)
        regular_intervals = np.array([5.0, 5.0, 5.0, 5.0])
        assert profiler._is_suspicious_interval_pattern(regular_intervals) == True

        # Test with irregular intervals (not suspicious)
        irregular_intervals = np.array([2.0, 15.0, 8.0, 25.0])
        assert profiler._is_suspicious_interval_pattern(irregular_intervals) == False

        # Test with too few intervals
        few_intervals = np.array([5.0, 5.0])
        assert profiler._is_suspicious_interval_pattern(few_intervals) == False

    def test_calculate_session_metrics(self, profiler, comprehensive_entries):
        """Test session metrics calculation."""
        session = comprehensive_entries[:5]  # Take first 5 entries
        metrics = profiler._calculate_session_metrics(session)

        assert isinstance(metrics, dict)
        assert "duration" in metrics
        assert "mean_interval" in metrics
        assert "std_interval" in metrics
        assert "video_count" in metrics

        assert metrics["video_count"] == 5
        assert isinstance(metrics["duration"], float)
        assert isinstance(metrics["mean_interval"], float)
        assert isinstance(metrics["std_interval"], float)

    def test_calculate_session_metrics_single_entry(self, profiler):
        """Test session metrics with single entry."""
        single_session = [{"timestamp": "2025-07-01T10:00:00"}]
        metrics = profiler._calculate_session_metrics(single_session)

        assert metrics["duration"] == 0.0
        assert metrics["mean_interval"] == 0.0
        assert metrics["std_interval"] == 0.0
        assert metrics["video_count"] == 1

    def test_is_anomalous_session(self, profiler):
        """Test anomalous session detection."""
        # Test with anomalous metrics
        anomalous_metrics = {
            "std_interval": 0.5,  # Very regular
            "video_count": 15,  # Long session
            "mean_interval": 3.0,  # Short intervals
            "duration": 45.0,
        }
        assert profiler._is_anomalous_session(anomalous_metrics) == True

        # Test with normal metrics
        normal_metrics = {
            "std_interval": 5.0,  # Variable
            "video_count": 5,  # Normal length
            "mean_interval": 10.0,  # Normal intervals
            "duration": 50.0,
        }
        assert profiler._is_anomalous_session(normal_metrics) == False

    def test_is_suspicious_sequence(self, profiler):
        """Test suspicious sequence detection."""
        # Test with identical titles
        identical_sequence = [
            {"title": "Same Title"},
            {"title": "Same Title"},
            {"title": "Same Title"},
        ]
        assert profiler._is_suspicious_sequence(identical_sequence) == True

        # Test with different titles
        different_sequence = [
            {"title": "Different Title 1"},
            {"title": "Completely Different Title"},
            {"title": "Another Unique Title"},
        ]
        assert profiler._is_suspicious_sequence(different_sequence) == False

        # Test with too few entries
        short_sequence = [{"title": "Title 1"}, {"title": "Title 2"}]
        assert profiler._is_suspicious_sequence(short_sequence) == False

    def test_identify_sequence_pattern(self, profiler):
        """Test sequence pattern identification."""
        # Test exact repetition
        exact_sequence = [
            {"title": "Same Title"},
            {"title": "Same Title"},
            {"title": "Same Title"},
        ]
        pattern = profiler._identify_sequence_pattern(exact_sequence)
        assert pattern == "exact_repetition"

        # Test different titles
        different_sequence = [
            {"title": "Title 1"},
            {"title": "Title 2"},
            {"title": "Title 3"},
        ]
        pattern = profiler._identify_sequence_pattern(different_sequence)
        assert pattern in [
            "numeric_progression",
            "similar_structure",
            "high_similarity",
        ]

    def test_calculate_distribution(self, profiler):
        """Test distribution calculation."""
        values = [
            0,
            1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9,
            10,
            11,
            12,
            13,
            14,
            15,
            16,
            17,
            18,
            19,
            20,
            21,
            22,
            23,
        ]
        distribution = profiler._calculate_distribution(values, 24)

        assert isinstance(distribution, list)
        assert len(distribution) == 24
        assert all(isinstance(val, float) for val in distribution)
        assert abs(sum(distribution) - 1.0) < 0.001  # Should sum to 1

    def test_calculate_regularity_score(self, profiler):
        """Test regularity score calculation."""
        # Test with regular timestamps
        base_time = datetime(2025, 7, 1, 10, 0, 0)
        regular_timestamps = [base_time + timedelta(minutes=i * 30) for i in range(10)]
        regular_score = profiler._calculate_regularity_score(regular_timestamps)

        assert isinstance(regular_score, float)
        assert 0.0 <= regular_score <= 1.0

        # Test with irregular timestamps
        irregular_timestamps = [
            base_time + timedelta(minutes=i * i * 10) for i in range(10)
        ]
        irregular_score = profiler._calculate_regularity_score(irregular_timestamps)

        assert regular_score > irregular_score

        # Test with single timestamp
        single_timestamp = [base_time]
        single_score = profiler._calculate_regularity_score(single_timestamp)
        assert single_score == 0.0

    def test_has_numeric_progression(self, profiler):
        """Test numeric progression detection."""
        # Test with numeric progression
        numeric_titles = ["Episode 1", "Episode 2", "Episode 3"]
        assert profiler._has_numeric_progression(numeric_titles) == True

        # Test without numeric progression
        non_numeric_titles = ["Random Title", "Another Title", "Different Title"]
        assert profiler._has_numeric_progression(non_numeric_titles) == False

    def test_has_similar_structure(self, profiler):
        """Test similar structure detection."""
        # Test with similar structure
        similar_titles = ["Tutorial Part 1", "Tutorial Part 2", "Tutorial Part 3"]
        result = profiler._has_similar_structure(similar_titles)
        assert isinstance(result, bool)

        # Test with different structure
        different_titles = [
            "Completely Different",
            "Another Topic",
            "Unrelated Content",
        ]
        result2 = profiler._has_similar_structure(different_titles)
        assert isinstance(result2, bool)

    def test_calculate_confidence_methods(self, profiler):
        """Test various confidence calculation methods."""
        # Test calculate_confidence
        confidence = profiler._calculate_confidence(2.0)
        assert isinstance(confidence, float)
        assert 0.0 <= confidence <= 1.0

        # Test calculate_loop_confidence
        similar_entries = [
            {"timestamp": "2025-07-01T10:00:00", "similarity": 0.8},
            {"timestamp": "2025-07-01T10:30:00", "similarity": 0.9},
            {"timestamp": "2025-07-01T11:00:00", "similarity": 0.85},
        ]
        loop_confidence = profiler._calculate_loop_confidence(similar_entries)
        assert isinstance(loop_confidence, float)
        assert 0.0 <= loop_confidence <= 1.0

        # Test calculate_binge_confidence
        intervals = np.array([5.0, 5.0, 5.0, 5.0])
        binge_confidence = profiler._calculate_binge_confidence(intervals)
        assert isinstance(binge_confidence, float)
        assert 0.0 <= binge_confidence <= 1.0

        # Test calculate_anomaly_confidence
        metrics = {
            "std_interval": 0.5,
            "video_count": 15,
            "mean_interval": 3.0,
            "duration": 45.0,
        }
        anomaly_confidence = profiler._calculate_anomaly_confidence(metrics)
        assert isinstance(anomaly_confidence, float)
        assert 0.0 <= anomaly_confidence <= 1.0

        # Test calculate_sequence_confidence
        sequence = [
            {"title": "Same Title"},
            {"title": "Same Title"},
            {"title": "Same Title"},
        ]
        sequence_confidence = profiler._calculate_sequence_confidence(sequence)
        assert isinstance(sequence_confidence, float)
        assert 0.0 <= sequence_confidence <= 1.0

    def test_calculate_pattern_duration(self, profiler):
        """Test pattern duration calculation."""
        entries = [
            {"timestamp": "2025-07-01T10:00:00"},
            {"timestamp": "2025-07-01T10:30:00"},
            {"timestamp": "2025-07-01T11:00:00"},
        ]
        duration = profiler._calculate_pattern_duration(entries)

        assert isinstance(duration, float)
        assert duration == 1.0  # 1 hour (method returns duration in hours)

    def test_geographic_anomalies_detection(self, profiler, comprehensive_entries):
        """Test geographic anomalies detection."""
        geo_anomalies = profiler._detect_geographic_anomalies(comprehensive_entries)

        assert isinstance(geo_anomalies, list)

        for anomaly in geo_anomalies:
            assert "timestamp" in anomaly
            assert "previous_location" in anomaly
            assert "current_location" in anomaly
            assert "time_difference" in anomaly

    def test_engagement_patterns_detection(self, profiler, binge_entries):
        """Test engagement pattern detection."""
        engagement_patterns = profiler._detect_engagement_patterns(binge_entries)

        assert isinstance(engagement_patterns, list)

        for pattern in engagement_patterns:
            assert "start_time" in pattern
            assert "end_time" in pattern
            assert "metrics" in pattern
            assert "anomaly_type" in pattern

    def test_language_switches_detection(self, profiler, comprehensive_entries):
        """Test language switches detection."""
        language_switches = profiler._detect_language_switches(comprehensive_entries)

        assert isinstance(language_switches, list)

        for switch in language_switches:
            assert "timestamp" in switch
            assert "from_language" in switch
            assert "to_language" in switch

    def test_topic_shifts_detection(self, profiler, comprehensive_entries):
        """Test topic shifts detection."""
        titles = [entry["title"] for entry in comprehensive_entries]
        tfidf_matrix = profiler.vectorizer.fit_transform(titles)

        from sklearn.metrics.pairwise import cosine_similarity

        similarity_matrix = cosine_similarity(tfidf_matrix)

        topic_shifts = profiler._detect_topic_shifts(
            comprehensive_entries, similarity_matrix
        )

        assert isinstance(topic_shifts, list)

        for shift in topic_shifts:
            assert "timestamp" in shift
            assert "previous_topic" in shift
            assert "new_topic" in shift

    def test_behavior_chains_detection(self, profiler, binge_entries):
        """Test behavior chains detection."""
        behavior_chains = profiler._detect_behavior_chains(binge_entries)

        assert isinstance(behavior_chains, list)

        for chain in behavior_chains:
            assert "start_time" in chain
            assert "end_time" in chain
            assert "length" in chain
            assert "pattern_type" in chain

    def test_advanced_pattern_detection_methods(self, profiler, comprehensive_entries):
        """Test advanced pattern detection methods."""
        # Test behavior chain detection
        behavior_chains = profiler._detect_behavior_chains(comprehensive_entries)
        assert isinstance(behavior_chains, list)

        # Test geographic anomaly detection
        geographic_anomalies = profiler._detect_geographic_anomalies(
            comprehensive_entries
        )
        assert isinstance(geographic_anomalies, list)

        # Test engagement pattern detection
        engagement_patterns = profiler._detect_engagement_patterns(
            comprehensive_entries
        )
        assert isinstance(engagement_patterns, list)

        # Test language switch detection
        language_switches = profiler._detect_language_switches(comprehensive_entries)
        assert isinstance(language_switches, list)

        # Test topic shift detection
        titles = [entry["title"] for entry in comprehensive_entries]
        tfidf_matrix = profiler.vectorizer.fit_transform(titles)
        from sklearn.metrics.pairwise import cosine_similarity

        similarity_matrix = cosine_similarity(tfidf_matrix)

        topic_shifts = profiler._detect_topic_shifts(
            comprehensive_entries, similarity_matrix
        )
        assert isinstance(topic_shifts, list)

    def test_comprehensive_pattern_analysis(self, profiler, comprehensive_entries):
        """Test comprehensive pattern analysis."""
        result = profiler.identify_adversarial_patterns(comprehensive_entries)

        # Verify complete structure
        assert "risk_score" in result
        assert "patterns" in result
        assert "entropy_analysis" in result
        assert "temporal_analysis" in result
        assert "similarity_stats" in result

        # Verify all pattern types are present
        patterns = result["patterns"]
        expected_patterns = [
            "rapid_views",
            "content_loops",
            "binge_patterns",
            "anomalous_sessions",
            "suspicious_sequences",
            "behavior_chains",
            "geographic_anomalies",
            "engagement_patterns",
            "language_switches",
            "topic_shifts",
        ]

        for pattern_type in expected_patterns:
            assert pattern_type in patterns
            assert isinstance(patterns[pattern_type], list)

        # Verify entropy analysis
        entropy_analysis = result["entropy_analysis"]
        assert "content_entropy" in entropy_analysis
        assert "channel_entropy" in entropy_analysis
        assert isinstance(entropy_analysis["content_entropy"], float)
        assert isinstance(entropy_analysis["channel_entropy"], float)

        # Verify temporal analysis
        temporal_analysis = result["temporal_analysis"]
        assert "hourly_distribution" in temporal_analysis
        assert "weekly_distribution" in temporal_analysis
        assert "regularity_score" in temporal_analysis

        # Verify similarity stats
        similarity_stats = result["similarity_stats"]
        assert "mean" in similarity_stats
        assert "std" in similarity_stats
        assert "max" in similarity_stats

    def test_edge_cases_and_error_handling(self, profiler):
        """Test edge cases and error handling."""
        # Test with malformed timestamps
        malformed_entries = [
            {"title": "Test 1", "timestamp": "invalid-timestamp"},
            {"title": "Test 2", "timestamp": "2025-07-01T10:00:00"},
        ]

        with pytest.raises(ValueError):
            profiler._detect_rapid_views(malformed_entries)

        # Test with missing required fields
        incomplete_entries = [
            {"title": "Test 1"},  # Missing timestamp
            {"timestamp": "2025-07-01T10:00:00"},  # Missing title
        ]

        with pytest.raises(KeyError):
            profiler._detect_rapid_views(incomplete_entries)

    def test_custom_profiler_parameters(self, custom_profiler):
        """Test profiler with custom parameters."""
        assert custom_profiler.similarity_threshold == 0.8
        assert custom_profiler.rapid_view_threshold == 3
        assert custom_profiler.session_gap == 15
        assert custom_profiler.repetition_threshold == 2
        assert custom_profiler.entropy_threshold == 0.7
        assert custom_profiler.chain_threshold == 5
        assert custom_profiler.time_zone_threshold == 2
        assert custom_profiler.engagement_variance_threshold == 0.5
        assert custom_profiler.confidence_decay_rate == 0.05
        assert custom_profiler.context_weight == 0.4
        assert custom_profiler.pattern_weight == 0.3
        assert custom_profiler.temporal_weight == 0.3

    def test_profiler_initialization_validation(self):
        """Test profiler initialization with various parameter combinations."""
        # Test with extreme values
        extreme_profiler = AdversarialProfiler(
            similarity_threshold=0.1,
            rapid_view_threshold=60,
            session_gap=1,
            repetition_threshold=10,
            entropy_threshold=0.1,
        )

        assert extreme_profiler.similarity_threshold == 0.1
        assert extreme_profiler.rapid_view_threshold == 60
        assert extreme_profiler.session_gap == 1
        assert extreme_profiler.repetition_threshold == 10
        assert extreme_profiler.entropy_threshold == 0.1
