from collections import defaultdict
from datetime import datetime, timedelta

from rabbitmirror.adversarial_profiler import AdversarialProfiler


class TestProfilerUpdateAndAnalyzeBranches:
    def setup_method(self):
        self.p = AdversarialProfiler()

    def test_update_activity_and_peak_analysis(self):
        # Build distributions resembling output of _init_time_distributions and _process_entry_timing
        distributions = {
            "weekdays": {8: 5, 9: 10, 20: 1},  # morning peak
            "weekends": {20: 12, 21: 8},  # evening peak
            "holidays": {10: 2},
            "monthly": {1: 3, 2: 2},
            "seasonal": {1: 5, 2: 4},
        }

        # Exercise update of activity pattern
        self.p._update_activity_patterns(distributions)
        ap = self.p.viewing_habits["activity_pattern"]
        assert isinstance(ap.get("weekdays"), dict)
        assert isinstance(ap.get("weekends"), dict)
        assert isinstance(ap.get("holidays"), dict)

        # Exercise peak analysis update
        self.p._update_peak_analysis(distributions)
        pa = self.p.viewing_habits["peak_analysis"]
        assert isinstance(pa.get("peak_hours"), list)
        assert isinstance(pa.get("off_peak_hours"), list)
        assert isinstance(pa.get("peak_days"), list)
        assert isinstance(pa.get("intensity_score"), float)

    def test_analyze_session_binge_break_and_updates(self):
        # Create two sessions with time gaps
        base = datetime(2025, 7, 1, 10, 0, 0)
        session1 = [
            {"title": "S1V1", "timestamp": (base + timedelta(minutes=0)).isoformat()},
            {"title": "S1V2", "timestamp": (base + timedelta(minutes=30)).isoformat()},
            {"title": "S1V3", "timestamp": (base + timedelta(minutes=60)).isoformat()},
            {"title": "S1V4", "timestamp": (base + timedelta(minutes=90)).isoformat()},
        ]  # duration = 1.5 hours, below binge threshold or length < 5 to avoid preferred_times list path
        session2 = [
            {"title": "S2V1", "timestamp": (base + timedelta(hours=5)).isoformat()},
            {
                "title": "S2V2",
                "timestamp": (base + timedelta(hours=5, minutes=45)).isoformat(),
            },
            {
                "title": "S2V3",
                "timestamp": (base + timedelta(hours=6, minutes=15)).isoformat(),
            },
        ]
        sessions = [session1, session2]

        # Analyze metrics and update corresponding viewing_habits sections
        sess_metrics = self.p._analyze_session_metrics(sessions)
        assert set(["avg_duration", "avg_videos", "consistency"]).issubset(sess_metrics)
        self.p._update_session_metrics(sess_metrics)

        binge_metrics = self.p._analyze_binge_patterns(sessions)
        assert set(
            ["frequency", "avg_duration", "preferred_times", "content_types"]
        ).issubset(binge_metrics)
        self.p._update_binge_metrics(binge_metrics)

        break_metrics = self.p._analyze_break_patterns(sessions)
        assert set(["avg_duration", "consistency", "triggers", "returns"]).issubset(
            break_metrics
        )
        self.p._update_break_patterns(break_metrics)

        # Validate viewing_habits are updated
        vh = self.p.viewing_habits
        assert vh["session_metrics"]["avg_duration"] == sess_metrics["avg_duration"]
        assert vh["binge_metrics"]["frequency"] == binge_metrics["frequency"]
        assert (
            vh["break_patterns"]["avg_break_duration"] == break_metrics["avg_duration"]
        )

    def test_update_content_device_location_and_seasonal(self):
        # Content timing data
        timing = defaultdict(list)
        timing["durations"] = [120, 400, 1300]
        timing["completion_rates"] = [0.5, 0.9, 0.7]
        timing["content_types"] = ["short", "medium", "long"]
        timing["abandonment_points"] = [0.1, 0.6, 0.8]
        self.p._update_content_timing(timing)
        ct = self.p.viewing_habits["content_timing"]
        assert isinstance(ct.get("length_preferences"), dict)
        assert isinstance(ct.get("completion_rates"), dict)
        assert isinstance(ct.get("abandonment_points"), dict)

        # Device patterns data
        device_data = defaultdict(list)
        t0 = datetime(2025, 7, 1, 10, 0, 0)
        device_data["devices"].extend(
            [
                ("mobile", t0),
                ("desktop", t0 + timedelta(minutes=5)),
                ("mobile", t0 + timedelta(minutes=10)),
            ]
        )
        device_data["platforms"].extend(
            [
                ("app", t0),
                ("web", t0 + timedelta(minutes=5)),  # switch
                ("web", t0 + timedelta(minutes=10)),
            ]
        )
        self.p._update_device_patterns(device_data)
        dp = self.p.viewing_habits["device_patterns"]
        assert isinstance(dp.get("device_distribution"), dict)
        assert isinstance(dp.get("platform_switches"), list)

        # Location patterns data
        location_data = defaultdict(list)
        location_data["locations"].extend(
            [
                ("NY", t0),
                ("NY", t0 + timedelta(hours=1)),
                ("SF", t0 + timedelta(hours=2)),
            ]
        )
        self.p._update_location_patterns(location_data)
        lp = self.p.viewing_habits["location_patterns"]
        assert isinstance(lp.get("primary_locations"), list)
        assert isinstance(lp.get("location_preferences"), dict)

        # Seasonal patterns via entries
        entries = [
            {
                "timestamp": datetime(2025, 1, 15, 10, 0, 0).isoformat(),
                "content_type": "educational",
            },
            {
                "timestamp": datetime(2025, 12, 25, 12, 0, 0).isoformat(),
                "content_type": "entertainment",
            },
            {
                "timestamp": datetime(2025, 7, 4, 18, 0, 0).isoformat(),
                "content_type": "news",
            },
        ]
        self.p._update_seasonal_patterns(entries)
        sp = self.p.viewing_habits["seasonal_patterns"]
        assert isinstance(sp.get("monthly_distribution"), dict)
        assert isinstance(sp.get("seasonal_preferences"), dict)
        assert isinstance(sp.get("holiday_behavior"), dict)
