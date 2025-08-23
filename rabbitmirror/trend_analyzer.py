"""
Trend analysis module.

Provides a lightweight TrendAnalyzer that can bucket entries by period and
compute simple trends for metrics like video counts and total watch time.
This implementation is dependency-light and designed to satisfy CLI and web
callers that expect a structured shape.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple

ISO_FMT = "%Y-%m-%dT%H:%M:%SZ"


@dataclass
class TrendAnalyzer:
    period_type: str = "daily"  # one of: daily, weekly, monthly
    normalize: bool = False

    def analyze_trends(
        self, entries: List[dict], metrics: Optional[List[str]] = None
    ) -> Dict:
        """Analyze trends from a list of entries.

        Expected entry shape is flexible; we look for:
          - time (ISO 8601 string) used for bucketing
          - timeWatchedSeconds/duration_seconds/lengthSeconds for watch time

        Returns a dict with keys:
          - date_range: {start, end}
          - timeframes: [label, ...]
          - metrics: {metric_name: {values: [...], trend_direction, trend_strength}}
          - significant_changes: [ {metric, description, from_value, to_value, timeframe }, ... ]
          - summary: {trending_up, trending_down, stable_metrics}
          - total_watch_time_seconds: int
        """
        # Parse timestamps and compute min/max
        timestamps: List[datetime] = []
        for e in entries or []:
            ts = self._parse_time(e)
            if ts is not None:
                timestamps.append(ts)
        timestamps.sort()

        if timestamps:
            start_dt = timestamps[0]
            end_dt = timestamps[-1]
        else:
            now = datetime.now(timezone.utc)
            start_dt = end_dt = now

        # Build buckets per period
        bucket_keys, label_for_key = self._build_periods(start_dt, end_dt)
        buckets = {k: [] for k in bucket_keys}
        for e in entries or []:
            ts = self._parse_time(e)
            if ts is None:
                continue
            key = self._bucket_key(ts)
            if key in buckets:
                buckets[key].append(e)

        # Compute base metrics per bucket
        tf_labels = [label_for_key(k) for k in bucket_keys]
        counts = [len(buckets[k]) for k in bucket_keys]
        watch_secs = [sum(self._watch_seconds(x) for x in buckets[k]) for k in bucket_keys]

        metric_map = {
            "videos_count": counts,
            "watch_time_seconds": watch_secs,
        }

        # Allow custom metric subset
        metric_names = list(metric_map.keys())
        if metrics:
            metric_names = [m for m in metrics if m in metric_map]

        metrics_out: Dict[str, Dict] = {}
        summary = {"trending_up": [], "trending_down": [], "stable_metrics": []}
        significant: List[Dict] = []

        for name in metric_names:
            values = metric_map[name][:]
            if self.normalize and values:
                vmax = max(values) or 1
                values = [v / vmax for v in values]

            direction, strength = self._trend(values)
            metrics_out[name] = {
                "values": values,
                "trend_direction": direction,
                "trend_strength": strength,
            }
            if direction == "increasing":
                summary["trending_up"].append(name)
            elif direction == "decreasing":
                summary["trending_down"].append(name)
            else:
                summary["stable_metrics"].append(name)

            # Detect a simple significant last-step change
            if len(values) >= 2:
                dv = values[-1] - values[-2]
                if abs(dv) > (0.25 * (max(values) or 1)):  # heuristic
                    significant.append(
                        {
                            "metric": name,
                            "description": (
                                "sharp increase" if dv > 0 else "sharp decrease"
                            ),
                            "from_value": values[-2],
                            "to_value": values[-1],
                            "timeframe": tf_labels[-1],
                        }
                    )

        total_watch = int(sum(watch_secs))
        result = {
            "date_range": {
                "start": self._human_date(start_dt),
                "end": self._human_date(end_dt),
            },
            "timeframes": tf_labels,
            "metrics": metrics_out,
            "significant_changes": significant,
            "summary": summary,
            "total_watch_time_seconds": total_watch,
        }
        return result

    # ------------------------
    # Helpers
    # ------------------------
    @staticmethod
    def _parse_time(entry: dict) -> Optional[datetime]:
        t = entry.get("time") or entry.get("timestamp")
        if not isinstance(t, str):
            return None
        try:
            # Allow both Zulu and flexible parse of common formats
            if t.endswith("Z"):
                return datetime.strptime(t, ISO_FMT).replace(tzinfo=timezone.utc)
            # Fallback: try fromisoformat (may require trimming)
            dt = datetime.fromisoformat(t.replace("Z", "+00:00"))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except Exception:
            return None

    @staticmethod
    def _watch_seconds(entry: dict) -> int:
        for key in ("timeWatchedSeconds", "duration_seconds", "lengthSeconds"):
            val = entry.get(key)
            if isinstance(val, int) and val >= 0:
                return val
            if isinstance(val, str) and val.isdigit():
                return int(val)
        return 0

    @staticmethod
    def _human_date(dt: datetime) -> str:
        try:
            return dt.astimezone(timezone.utc).date().isoformat()
        except Exception:
            return "N/A"

    def _bucket_key(self, dt: datetime) -> Tuple[int, int, int]:
        dt = dt.astimezone(timezone.utc)
        y, m, d = dt.year, dt.month, dt.day
        if self.period_type == "monthly":
            return (y, m, 1)
        if self.period_type == "weekly":
            # ISO week: Monday is 1
            iso_year, iso_week, _ = dt.isocalendar()
            return (iso_year, iso_week, 0)
        # daily default
        return (y, m, d)

    def _build_periods(self, start_dt: datetime, end_dt: datetime):
        # Normalize to UTC dates
        s = start_dt.astimezone(timezone.utc)
        e = end_dt.astimezone(timezone.utc)
        keys: List[Tuple[int, int, int]] = []

        def label_for_key(k: Tuple[int, int, int]) -> str:
            if self.period_type == "monthly":
                return f"{k[0]:04d}-{k[1]:02d}"
            if self.period_type == "weekly":
                return f"{k[0]:04d}-W{k[1]:02d}"
            return f"{k[0]:04d}-{k[1]:02d}-{k[2]:02d}"

        if self.period_type == "monthly":
            y, m = s.year, s.month
            while (y < e.year) or (y == e.year and m <= e.month):
                keys.append((y, m, 1))
                m += 1
                if m > 12:
                    m = 1
                    y += 1
        elif self.period_type == "weekly":
            # Start from Monday of start week
            start_monday = s - timedelta(days=(s.isoweekday() - 1))
            cur = start_monday
            while cur <= e:
                iso_year, iso_week, _ = cur.isocalendar()
                keys.append((iso_year, iso_week, 0))
                cur += timedelta(weeks=1)
        else:
            # daily
            cur = s.date()
            end = e.date()
            while cur <= end:
                keys.append((cur.year, cur.month, cur.day))
                cur += timedelta(days=1)

        return keys, label_for_key

    @staticmethod
    def _trend(values: List[float]) -> Tuple[str, float]:
        if not values or len(values) < 2:
            return "stable", 0.0
        # Simple linear trend via first/last and mean absolute deviation as scale
        delta = values[-1] - values[0]
        scale = max(max(values) - min(values), 1e-9)
        strength = float(abs(delta) / scale)
        if delta > (0.05 * scale):
            return "increasing", min(1.0, strength)
        if delta < -(0.05 * scale):
            return "decreasing", min(1.0, strength)
        return "stable", min(1.0, strength)
