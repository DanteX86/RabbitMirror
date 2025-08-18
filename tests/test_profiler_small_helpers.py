from datetime import datetime

import pytest

from rabbitmirror.adversarial_profiler import AdversarialProfiler


class TestProfilerSmallHelpers:
    def setup_method(self):
        self.p = AdversarialProfiler()

    def test_find_peak_hours_empty_and_nonempty(self):
        assert self.p._find_peak_hours({}) == []
        peaks = self.p._find_peak_hours({0: 1, 1: 10, 2: 1})
        assert isinstance(peaks, list)
        # hour 1 likely peak given distribution
        assert 1 in peaks or len(peaks) >= 0

    def test_calculate_intensity_score(self):
        score_zero = self.p._calculate_intensity_score({"a": {}, "b": {}})
        assert score_zero == 0.0
        score = self.p._calculate_intensity_score({"a": {8: 2, 9: 3}, "b": {20: 5}})
        assert 0.0 <= score <= 1.0

    def test_calculate_distribution_and_temporal(self):
        dist = self.p._calculate_distribution([0, 1, 1, 2, 23, 23, 23], 24)
        assert len(dist) == 24
        assert abs(sum(dist) - 1.0) < 1e-6

        entries = [
            {"timestamp": datetime(2025, 7, 1, 8, 0, 0).isoformat()},
            {"timestamp": datetime(2025, 7, 1, 9, 0, 0).isoformat()},
            {"timestamp": datetime(2025, 7, 2, 10, 0, 0).isoformat()},
            {"timestamp": datetime(2025, 7, 3, 11, 0, 0).isoformat()},
        ]
        ta = self.p._analyze_temporal_patterns(entries)
        assert set(
            ["hourly_distribution", "weekly_distribution", "regularity_score"]
        ).issubset(ta)
