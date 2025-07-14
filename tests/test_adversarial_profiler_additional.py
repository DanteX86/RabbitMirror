#!/usr/bin/env python3
"""
Additional comprehensive tests for AdversarialProfiler to improve coverage
"""
import os

# Import the class we're testing
import sys
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from rabbitmirror.adversarial_profiler import AdversarialProfiler


class TestAdversarialProfilerAdditional:
    """Additional tests for AdversarialProfiler to improve coverage"""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.profiler = AdversarialProfiler()
        self.sample_entries = [
            {
                "title": "Test Video 1",
                "timestamp": "2024-01-01T10:00:00",
                "channel": "TestChannel",
                "category": "education",
                "duration": 600,
                "watched_duration": 300,
                "interaction_count": 5,
                "location": "US",
                "device_type": "desktop",
                "platform": "web",
                "content_type": "video",
                "resolution": "1080p",
                "device_id": "device1",
                "comment_count": 2,
            },
            {
                "title": "Test Video 2",
                "timestamp": "2024-01-01T10:15:00",
                "channel": "TestChannel",
                "category": "entertainment",
                "duration": 900,
                "watched_duration": 450,
                "interaction_count": 8,
                "location": "US",
                "device_type": "mobile",
                "platform": "app",
                "content_type": "video",
                "resolution": "720p",
                "device_id": "device2",
                "comment_count": 1,
            },
        ]

    def test_analyze_abandonment_points(self):
        """Test _analyze_abandonment_points method"""
        # Test with abandonment points
        points = [0.3, 0.5, 0.7, 0.2, 0.8]
        result = self.profiler._analyze_abandonment_points(points)

        assert "distribution" in result
        assert "avg_point" in result
        assert "std_point" in result
        assert result["avg_point"] == np.mean(points)
        assert result["std_point"] == np.std(points)

        # Test with empty points
        empty_result = self.profiler._analyze_abandonment_points([])
        assert empty_result == {}

    def test_analyze_bias_trend(self):
        """Test _analyze_bias_trend method"""
        # Test with polarization scores
        scores = [0.1, 0.2, 0.3, 0.4, 0.5]
        result = self.profiler._analyze_bias_trend(scores)

        assert "trend" in result
        assert "volatility" in result
        assert isinstance(result["trend"], float)
        assert isinstance(result["volatility"], float)

        # Test with empty scores
        empty_result = self.profiler._analyze_bias_trend([])
        assert empty_result["trend"] == 0.0
        assert empty_result["volatility"] == 0.0

    def test_analyze_trigger_patterns(self):
        """Test _analyze_trigger_patterns method"""
        triggers = [
            {"triggers": ["curiosity", "urgency"], "timestamp": "2024-01-01T10:00:00"},
            {"triggers": ["controversy"], "timestamp": "2024-01-01T10:30:00"},
            {"triggers": ["curiosity"], "timestamp": "2024-01-01T11:00:00"},
        ]

        result = self.profiler._analyze_trigger_patterns(triggers)

        assert "frequency" in result
        assert "patterns" in result
        assert "curiosity" in result["frequency"]
        assert result["frequency"]["curiosity"] == 2

    def test_apply_time_decay(self):
        """Test _apply_time_decay method"""
        # Test with recent timestamp
        recent_time = datetime.now() - timedelta(hours=1)
        decay_recent = self.profiler._apply_time_decay(recent_time)

        # Test with old timestamp
        old_time = datetime.now() - timedelta(days=1)
        decay_old = self.profiler._apply_time_decay(old_time)

        assert decay_recent > decay_old
        assert decay_recent <= 1.0
        assert decay_old >= 0.1  # Minimum decay

    def test_calculate_activity_balance(self):
        """Test _calculate_activity_balance method"""
        activity_durations = {
            "watching": [10, 20, 30],
            "scrolling": [5, 15, 25],
            "clicking": [2, 8, 12],
        }

        balance = self.profiler._calculate_activity_balance(activity_durations)

        assert 0 <= balance <= 1
        assert isinstance(balance, float)

        # Test with empty activity durations
        empty_balance = self.profiler._calculate_activity_balance({})
        assert empty_balance == 0.0

    def test_calculate_attention_stability(self):
        """Test _calculate_attention_stability method"""
        entries = [
            {"duration": 100, "completion_rate": 0.8},
            {"duration": 120, "completion_rate": 0.9},
            {"duration": 80, "completion_rate": 0.7},
        ]

        stability = self.profiler._calculate_attention_stability(entries)

        assert 0 <= stability <= 1
        assert isinstance(stability, float)

        # Test with single entry
        single_stability = self.profiler._calculate_attention_stability([entries[0]])
        assert single_stability == 1.0

    def test_calculate_authenticity_risk(self):
        """Test _calculate_authenticity_risk method"""
        metrics = {
            "interactions": {"response_consistency": 0.05},
            "temporal": {"regularity_score": 0.95},
            "preferences": {"topic_coherence": 0.1},
        }

        risk = self.profiler._calculate_authenticity_risk(metrics)

        assert 0 <= risk <= 1
        assert isinstance(risk, float)

    def test_calculate_automation_risk(self):
        """Test _calculate_automation_risk method"""
        metrics = {
            "interactions": {"avg_response_time": 1.0},
            "patterns": {"behavior_chains": [1, 2, 3, 4, 5, 6]},
            "sessions": {"regularity_score": 0.85},
        }

        risk = self.profiler._calculate_automation_risk(metrics)

        assert 0 <= risk <= 1
        assert isinstance(risk, float)

    def test_calculate_behavioral_consistency(self):
        """Test _calculate_behavioral_consistency method"""
        stability_metrics = {"attention": 0.8, "interaction": 0.7, "navigation": 0.9}

        consistency = self.profiler._calculate_behavioral_consistency(stability_metrics)

        assert 0 <= consistency <= 1
        assert isinstance(consistency, float)

    def test_calculate_engagement_consistency(self):
        """Test _calculate_engagement_consistency method"""
        engagement_levels = [
            {"interactions": 10, "duration": 100},
            {"interactions": 12, "duration": 110},
            {"interactions": 8, "duration": 90},
        ]

        consistency = self.profiler._calculate_engagement_consistency(engagement_levels)

        assert 0 <= consistency <= 1
        assert isinstance(consistency, float)

        # Test with empty engagement levels
        empty_consistency = self.profiler._calculate_engagement_consistency([])
        assert empty_consistency == 0.0

    def test_calculate_engagement_profile(self):
        """Test _calculate_engagement_profile method"""
        engagement_levels = [
            {"interactions": 10, "duration": 100, "comments": 2},
            {"interactions": 15, "duration": 120, "comments": 3},
            {"interactions": 8, "duration": 80, "comments": 1},
        ]

        profile = self.profiler._calculate_engagement_profile(engagement_levels)

        assert "avg_interactions" in profile
        assert "avg_duration" in profile
        assert "avg_comments" in profile
        assert "engagement_score" in profile

        # Test with empty engagement levels
        empty_profile = self.profiler._calculate_engagement_profile([])
        assert empty_profile["avg_interactions"] == 0.0
        assert empty_profile["avg_duration"] == 0.0
        assert empty_profile["engagement_score"] == 0.0

    def test_calculate_intensity_score(self):
        """Test _calculate_intensity_score method"""
        distributions = {
            "weekdays": {9: 10, 10: 15, 11: 20},
            "weekends": {10: 8, 11: 12, 12: 18},
            "holidays": {14: 5, 15: 8, 16: 10},
        }

        intensity = self.profiler._calculate_intensity_score(distributions)

        assert 0 <= intensity <= 1
        assert isinstance(intensity, float)

        # Test with empty distributions
        empty_intensity = self.profiler._calculate_intensity_score({})
        assert empty_intensity == 0.0

    def test_calculate_length_preferences(self):
        """Test _calculate_length_preferences method"""
        durations = [120, 600, 1800, 300, 900]  # Mix of short, medium, long

        preferences = self.profiler._calculate_length_preferences(durations)

        assert "short" in preferences
        assert "medium" in preferences
        assert "long" in preferences
        assert sum(preferences.values()) == 1.0  # Should sum to 1 (probabilities)

        # Test with empty durations
        empty_preferences = self.profiler._calculate_length_preferences([])
        assert empty_preferences == {}

    def test_calculate_manipulation_risk(self):
        """Test _calculate_manipulation_risk method"""
        metrics = {
            "psychological": {"topic_shifts": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]},
            "preferences": {"polarization_score": 0.8},
            "emotional": {"trigger_frequency": 0.6},
        }

        risk = self.profiler._calculate_manipulation_risk(metrics)

        assert 0 <= risk <= 1
        assert isinstance(risk, float)

    def test_calculate_multitask_intensity(self):
        """Test _calculate_multitask_intensity method"""
        concurrent_activities = [2, 3, 4, 1, 5]
        task_switches = [10, 15, 8, 12, 18]

        intensity = self.profiler._calculate_multitask_intensity(
            concurrent_activities, task_switches
        )

        assert 0 <= intensity <= 1
        assert isinstance(intensity, float)

        # Test with empty arrays
        empty_intensity = self.profiler._calculate_multitask_intensity([], [])
        assert empty_intensity == 0.0

    def test_calculate_navigation_complexity(self):
        """Test _calculate_navigation_complexity method"""
        navigation_sequences = [
            {"complexity": 0.5},
            {"complexity": 0.7},
            {"complexity": 0.3},
        ]

        complexity = self.profiler._calculate_navigation_complexity(
            navigation_sequences
        )

        assert 0 <= complexity <= 1
        assert isinstance(complexity, float)

        # Test with empty sequences
        empty_complexity = self.profiler._calculate_navigation_complexity([])
        assert empty_complexity == 0.0

    def test_calculate_overall_risk(self):
        """Test _calculate_overall_risk method"""
        risks = {
            "automation_risk": 0.7,
            "manipulation_risk": 0.5,
            "authenticity_risk": 0.8,
        }

        overall_risk = self.profiler._calculate_overall_risk(risks)

        assert 0 <= overall_risk <= 1
        assert isinstance(overall_risk, float)

    def test_calculate_quality_sensitivity(self):
        """Test _calculate_quality_sensitivity method"""
        quality_prefs = {"professional": 10, "semi_pro": 5, "amateur": 2}

        sensitivity = self.profiler._calculate_quality_sensitivity(quality_prefs)

        assert 0 <= sensitivity <= 1
        assert isinstance(sensitivity, float)

        # Test with empty preferences
        empty_sensitivity = self.profiler._calculate_quality_sensitivity({})
        assert empty_sensitivity == 0.0

    def test_calculate_session_duration(self):
        """Test _calculate_session_duration method"""
        session = [
            {"timestamp": "2024-01-01T10:00:00"},
            {"timestamp": "2024-01-01T10:30:00"},
            {"timestamp": "2024-01-01T11:00:00"},
        ]

        duration = self.profiler._calculate_session_duration(session)

        assert duration == 1.0  # 1 hour
        assert isinstance(duration, float)

        # Test with single entry
        single_duration = self.profiler._calculate_session_duration([session[0]])
        assert single_duration == 0.0

    def test_calculate_style_diversity(self):
        """Test _calculate_style_diversity method"""
        style_prefs = {"scripted": 8, "spontaneous": 5, "interactive": 3}

        diversity = self.profiler._calculate_style_diversity(style_prefs)

        assert 0 <= diversity <= 1
        assert isinstance(diversity, float)

        # Test with empty preferences
        empty_diversity = self.profiler._calculate_style_diversity({})
        assert empty_diversity == 0.0

    def test_contextual_weight_calculations(self):
        """Test various contextual weight calculation methods"""
        # Test temporal weight
        time_val = datetime(2024, 1, 1, 2, 0, 0)  # 2 AM (unusual hour)
        temporal_weight = self.profiler._calculate_temporal_weight(time_val, 0.1)
        assert temporal_weight > 0.1  # Should be amplified

        # Test day weight
        day_weight = self.profiler._calculate_day_weight(time_val, 0.1)
        assert day_weight >= 0.1

        # Test seasonal weight
        seasonal_val = {"hour": 2, "pattern_type": "late_night"}
        seasonal_weight = self.profiler._calculate_seasonal_weight(seasonal_val, 0.1)
        assert seasonal_weight >= 0.1

    def test_detect_anomalies_methods(self):
        """Test anomaly detection methods"""
        # Test interaction anomalies
        interaction_metrics = {
            "avg_response_time": 0.05,  # Very fast
            "response_consistency": 0.01,  # Very consistent
            "action_patterns": list(range(25)),  # Many patterns
        }

        interaction_anomalies = self.profiler._detect_interaction_anomalies(
            interaction_metrics
        )
        assert "anomalies" in interaction_anomalies
        assert "count" in interaction_anomalies
        assert "score" in interaction_anomalies

        # Test preference anomalies
        preference_metrics = {
            "genre_metrics": {
                "genre_distribution": {f"genre_{i}": 1 for i in range(20)}
            },
            "temporal_profile": {"consistency": 0.98},
            "preference_stability": 0.05,
        }

        preference_anomalies = self.profiler._detect_preference_anomalies(
            preference_metrics
        )
        assert "anomalies" in preference_anomalies
        assert "count" in preference_anomalies
        assert "score" in preference_anomalies

        # Test psychological anomalies
        psychological_metrics = {
            "mood_pattern": {"transitions": list(range(60))},
            "emotional_engagement": {"trigger_frequency": 0.9},
            "attention_stability": 0.1,
        }

        psychological_anomalies = self.profiler._detect_psychological_anomalies(
            psychological_metrics
        )
        assert "anomalies" in psychological_anomalies
        assert "count" in psychological_anomalies
        assert "score" in psychological_anomalies

    def test_identify_navigation_style(self):
        """Test _identify_navigation_style method"""
        # Test focused navigation
        focused_sequences = [
            {"coherence": 0.8, "complexity": 2},
            {"coherence": 0.9, "complexity": 1},
        ]

        style = self.profiler._identify_navigation_style(focused_sequences)
        assert style == "focused"

        # Test exploratory navigation
        exploratory_sequences = [
            {"coherence": 0.3, "complexity": 6},
            {"coherence": 0.2, "complexity": 7},
        ]

        style = self.profiler._identify_navigation_style(exploratory_sequences)
        assert style == "exploratory"

        # Test empty sequences
        empty_style = self.profiler._identify_navigation_style([])
        assert empty_style == "unknown"

    def test_identify_viewing_rhythm(self):
        """Test _identify_viewing_rhythm method"""
        # Test binge heavy
        binge_patterns = [
            {"type": "binge", "intensity": 0.8},
            {"type": "binge", "intensity": 0.9},
        ]

        rhythm = self.profiler._identify_viewing_rhythm(binge_patterns)
        assert rhythm == "binge_heavy"

        # Test deep focused
        deep_patterns = [
            {"type": "deep", "intensity": 0.6},
            {"type": "deep", "intensity": 0.7},
        ]

        rhythm = self.profiler._identify_viewing_rhythm(deep_patterns)
        assert rhythm == "deep_focused"

        # Test light casual
        light_patterns = [
            {"type": "casual", "intensity": 0.2},
            {"type": "casual", "intensity": 0.1},
        ]

        rhythm = self.profiler._identify_viewing_rhythm(light_patterns)
        assert rhythm == "light_casual"

    def test_is_holiday_method(self):
        """Test _is_holiday method"""
        # Test with regular date
        regular_date = datetime(2024, 1, 15)
        assert not self.profiler._is_holiday(regular_date)

        # Method currently always returns False as it's a placeholder
        holiday_date = datetime(2024, 12, 25)
        assert not self.profiler._is_holiday(holiday_date)

    def test_is_suspicious_category(self):
        """Test _is_suspicious_category method"""
        # Test with suspicious transitions
        suspicious_category = {"transitions": ["cat1", "cat2", "cat3"]}

        assert self.profiler._is_suspicious_category(suspicious_category)

        # Test with non-suspicious transitions
        normal_category = {"transitions": ["cat1", "cat1", "cat2"]}

        assert not self.profiler._is_suspicious_category(normal_category)

    def test_process_entry_methods(self):
        """Test various entry processing methods"""
        entry = {
            "timestamp": "2024-01-01T10:00:00",
            "duration": 600,
            "watched_duration": 300,
            "content_type": "video",
            "device_type": "mobile",
            "platform": "app",
            "location": "US",
        }

        # Test process_entry_timing
        from collections import defaultdict

        time_distributions = {
            "weekdays": defaultdict(int),
            "weekends": defaultdict(int),
            "holidays": defaultdict(int),
            "monthly": defaultdict(int),
            "seasonal": defaultdict(int),
        }

        self.profiler._process_entry_timing(entry, time_distributions)
        assert len(time_distributions["weekdays"]) > 0

        # Test process_entry_content
        from collections import defaultdict

        content_timing = defaultdict(list)

        self.profiler._process_entry_content(entry, content_timing)
        assert len(content_timing["durations"]) == 1
        assert len(content_timing["completion_rates"]) == 1

        # Test process_entry_device
        device_usage = defaultdict(list)

        self.profiler._process_entry_device(entry, device_usage)
        assert len(device_usage["devices"]) == 1
        assert len(device_usage["platforms"]) == 1

    def test_update_methods(self):
        """Test various update methods"""
        # Test update_activity_patterns
        distributions = {
            "weekdays": {10: 5, 11: 8},
            "weekends": {14: 3, 15: 6},
            "holidays": {16: 2, 17: 4},
        }

        self.profiler._update_activity_patterns(distributions)
        assert "weekdays" in self.profiler.viewing_habits["activity_pattern"]

        # Test update_peak_analysis
        self.profiler._update_peak_analysis(distributions)
        assert "peak_hours" in self.profiler.viewing_habits["peak_analysis"]

        # Test update_session_metrics
        session_metrics = {"avg_duration": 120.0, "avg_videos": 5.0, "consistency": 0.8}

        self.profiler._update_session_metrics(session_metrics)
        assert self.profiler.viewing_habits["session_metrics"]["avg_duration"] == 120.0

    def test_edge_cases_and_error_handling(self):
        """Test edge cases and error handling"""
        # Test with empty arrays and None values
        assert self.profiler._calculate_content_similarity("", "") == 0.0
        assert self.profiler._calculate_content_similarity(None, None) == 0.0

        # Test with malformed data
        malformed_entry = {}
        result = self.profiler._calculate_session_metrics([malformed_entry])
        assert result["video_count"] == 1
        assert result["mean_interval"] == 0.0

        # Test with extreme values
        extreme_intervals = np.array([0.001, 0.002, 0.003])
        assert self.profiler._is_suspicious_interval_pattern(extreme_intervals)

    def test_comprehensive_pattern_detection(self):
        """Test comprehensive pattern detection with realistic data"""
        # Create a more comprehensive dataset
        comprehensive_entries = []
        base_time = datetime(2024, 1, 1, 10, 0, 0)

        for i in range(20):
            entry = {
                "title": f"Video {i}: Tutorial on Python programming",
                "timestamp": (base_time + timedelta(minutes=i * 5)).isoformat(),
                "channel": f"Channel{i % 3}",
                "category": "education" if i % 2 == 0 else "entertainment",
                "duration": 300 + (i * 10),
                "watched_duration": 200 + (i * 5),
                "interaction_count": i % 10,
                "location": "US" if i % 2 == 0 else "UK",
                "device_type": "desktop" if i % 2 == 0 else "mobile",
                "platform": "web",
                "content_type": "video",
                "resolution": "1080p",
                "device_id": f"device_{i % 4}",
                "comment_count": i % 5,
                "click_delay": 0.5 + (i * 0.1),
                "engagement_delay": 1.0 + (i * 0.2),
                "comment_delay": 2.0 + (i * 0.3),
                "share_delay": 3.0 + (i * 0.4),
            }
            comprehensive_entries.append(entry)

        # Test the main pattern identification
        result = self.profiler.identify_adversarial_patterns(comprehensive_entries)

        # Verify structure
        assert "risk_score" in result
        assert "patterns" in result
        assert "entropy_analysis" in result
        assert "temporal_analysis" in result
        assert "similarity_stats" in result

        # Verify patterns are detected
        patterns = result["patterns"]
        for pattern_type in [
            "rapid_views",
            "content_loops",
            "binge_patterns",
            "anomalous_sessions",
            "suspicious_sequences",
        ]:
            assert pattern_type in patterns

    def test_weight_calculation_methods(self):
        """Test weight calculation methods with various scenarios"""
        # Test category weight
        category_val = {"category_switches": 10}
        category_weight = self.profiler._calculate_category_weight(category_val, 0.1)
        assert category_weight >= 0.1

        # Test length weight
        length_val = {
            "duration": 25,
            "completion_rate": 0.3,
        }  # Short video, low completion
        length_weight = self.profiler._calculate_length_weight(length_val, 0.1)
        assert length_weight >= 0.1

        # Test popularity weight
        popularity_val = {
            "view_count": 100,
            "content_age_days": 1000,
        }  # Unpopular content
        popularity_weight = self.profiler._calculate_popularity_weight(
            popularity_val, 0.1
        )
        assert popularity_weight >= 0.1

        # Test reputation weight
        reputation_val = {
            "subscriber_count": 50,
            "channel_age_days": 15,
        }  # New small channel
        reputation_weight = self.profiler._calculate_reputation_weight(
            reputation_val, 0.1
        )
        assert reputation_weight >= 0.1

        # Test IP weight
        ip_val = {"ip_changes": 10, "timespan_hours": 12}  # Frequent IP changes
        ip_weight = self.profiler._calculate_ip_weight(ip_val, 0.1)
        assert ip_weight >= 0.1

        # Test network weight
        network_val = {"network_type": "proxy", "network_changes": 8}
        network_weight = self.profiler._calculate_network_weight(network_val, 0.1)
        assert network_weight >= 0.1

    def test_analyze_session_pattern(self):
        """Test _analyze_session_pattern method"""
        # Test deep session
        deep_session = [
            {"duration": 1900, "category": "education"},
            {"duration": 2000, "category": "education"},
        ]

        pattern = self.profiler._analyze_session_pattern(deep_session)
        assert pattern["type"] == "deep"
        assert pattern["focus"] >= 0.5

        # Test binge session
        binge_session = [{"duration": 300, "category": f"cat{i%3}"} for i in range(15)]

        pattern = self.profiler._analyze_session_pattern(binge_session)
        assert pattern["type"] == "binge"
        assert pattern["video_count"] == 15

        # Test empty session
        empty_pattern = self.profiler._analyze_session_pattern([])
        assert empty_pattern["type"] == "empty"

    def test_find_peak_hours_method(self):
        """Test _find_peak_hours method"""
        counts = {8: 10, 9: 15, 10: 20, 11: 25, 12: 8, 13: 5}

        peak_hours = self.profiler._find_peak_hours(counts)

        assert isinstance(peak_hours, list)
        assert 11 in peak_hours  # Highest count

        # Test with empty counts
        empty_peaks = self.profiler._find_peak_hours({})
        assert empty_peaks == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
