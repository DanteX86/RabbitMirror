import math

import pytest

from rabbitmirror.adversarial_profiler import AdversarialProfiler


class TestDurationParsing:
    def setup_method(self):
        self.profiler = AdversarialProfiler()

    @pytest.mark.parametrize(
        "value,expected",
        [
            (0, 0.0),
            (12, 12.0),
            (12.5, 12.5),
            ("0", 0.0),
            ("42", 42.0),
            ("3:07", 187.0),
            ("09:22", 562.0),
            ("  1:2  ", 62.0),
        ],
    )
    def test_parse_time_value_valid(self, value, expected):
        assert self.profiler._parse_time_value(value) == pytest.approx(expected)

    @pytest.mark.parametrize(
        "value",
        [None, "", "  ", "abc", "3:xx", object(), [], {}],
    )
    def test_parse_time_value_invalid(self, value):
        # Invalid inputs should safely return 0.0 without raising
        assert self.profiler._parse_time_value(value) == 0.0

    def test_get_duration_seconds_prefers_numeric_field(self):
        entry = {"duration": "9:22", "duration_seconds": 123.0}
        # Should prefer duration_seconds over parsing the string
        assert self.profiler._get_duration_seconds(entry) == 123.0

    def test_get_duration_seconds_parses_mmss_string(self):
        entry = {"duration": "9:22"}
        assert self.profiler._get_duration_seconds(entry) == 9 * 60 + 22

    def test_attention_patterns_with_mmss_inputs(self):
        # Mix of numeric seconds and mm:ss strings to validate robust parsing path
        entries = [
            {
                "title": "Video A",
                "timestamp": "2025-07-01T10:00:00",
                "duration": "10:00",  # 600s
                "watched_duration": "7:30",  # 450s
                "interaction_count": 6,
            },
            {
                "title": "Video B",
                "timestamp": "2025-07-01T10:15:00",
                "duration_seconds": 300.0,  # 5:00
                "watched_duration": 240,  # 4:00
                "interaction_count": 3,
            },
        ]

        metrics = self.profiler._analyze_attention_patterns(entries)
        assert isinstance(metrics, dict)
        # mean_duration is mean of watched durations (450 and 240)
        assert math.isclose(
            metrics.get("mean_duration", 0.0), (450 + 240) / 2.0, rel_tol=1e-6
        )
        # completion_consistency and engagement_variability should be finite numbers
        assert isinstance(metrics.get("completion_consistency", 1.0), float)
        assert isinstance(metrics.get("engagement_variability", 1.0), float)
