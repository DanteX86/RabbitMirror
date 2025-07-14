"""
TrendAnalyzer - Analyze trends in watch history data over time.

This module provides functionality to analyze temporal patterns, growth trends,
and behavioral changes in viewing data across different time periods.
"""

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import numpy as np


@dataclass
class TrendMetric:
    """Represents a trend metric with statistical information."""

    name: str
    values: List[float]
    timeframes: List[str]
    trend_direction: str  # 'increasing', 'decreasing', 'stable'
    trend_strength: float  # 0.0 to 1.0
    statistical_significance: float


@dataclass
class SignificantChange:
    """Represents a significant change detected in the data."""

    metric: str
    timeframe: str
    from_value: float
    to_value: float
    change_percentage: float
    description: str


class TrendAnalyzer:
    """Analyze trends and patterns in watch history data over time."""

    def __init__(self, period_type: str = "daily", normalize: bool = False):
        """
        Initialize the TrendAnalyzer.

        Args:
            period_type: Type of time period ('daily', 'weekly', 'monthly')
            normalize: Whether to normalize trend values (0-1 scale)
        """
        self.period_type = period_type
        self.normalize = normalize
        self.supported_periods = ["daily", "weekly", "monthly"]

        if period_type not in self.supported_periods:
            raise ValueError(f"Period type must be one of {self.supported_periods}")

    def analyze_trends(
        self, entries: List[Dict[str, Any]], metrics: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Analyze trends in the watch history data.

        Args:
            entries: List of watch history entries
            metrics: Specific metrics to analyze (if None, analyzes all)

        Returns:
            Dictionary containing trend analysis results
        """
        if not entries:
            return self._empty_result()

        # Default metrics to analyze
        default_metrics = [
            "video_count",
            "total_duration",
            "avg_duration",
            "unique_channels",
            "categories_diversity",
            "viewing_velocity",
        ]

        analysis_metrics = metrics or default_metrics

        # Group data by time periods
        time_periods = self._group_by_time_period(entries)

        # Calculate metrics for each time period
        period_metrics = self._calculate_period_metrics(time_periods)

        # Analyze trends for each metric
        trend_results = {}
        significant_changes = []

        for metric in analysis_metrics:
            if metric in period_metrics:
                trend_metric = self._analyze_metric_trend(
                    metric, period_metrics[metric], list(time_periods.keys())
                )
                trend_results[metric] = trend_metric

                # Detect significant changes
                changes = self._detect_significant_changes(trend_metric)
                significant_changes.extend(changes)

        return {
            "period_type": self.period_type,
            "timeframes": list(time_periods.keys()),
            "metrics": {
                name: self._trend_metric_to_dict(tm)
                for name, tm in trend_results.items()
            },
            "significant_changes": [
                self._change_to_dict(sc) for sc in significant_changes
            ],
            "summary": self._generate_summary(trend_results, significant_changes),
            "total_periods_analyzed": len(time_periods),
            "date_range": self._get_date_range(entries),
        }

    def _group_by_time_period(
        self, entries: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Group entries by time period."""
        periods = defaultdict(list)

        for entry in entries:
            timestamp = datetime.fromisoformat(entry["timestamp"])
            period_key = self._get_period_key(timestamp)
            periods[period_key].append(entry)

        # Sort periods chronologically
        sorted_periods = dict(sorted(periods.items()))
        return sorted_periods

    def _get_period_key(self, timestamp: datetime) -> str:
        """Generate a period key based on the timestamp."""
        if self.period_type == "daily":
            return timestamp.strftime("%Y-%m-%d")
        if self.period_type == "weekly":
            # Get Monday of the week
            monday = timestamp - timedelta(days=timestamp.weekday())
            return monday.strftime("%Y-W%U")
        if self.period_type == "monthly":
            return timestamp.strftime("%Y-%m")
        raise ValueError(f"Unsupported period type: {self.period_type}")

    def _calculate_period_metrics(
        self, time_periods: Dict[str, List[Dict[str, Any]]]
    ) -> Dict[str, List[float]]:
        """Calculate metrics for each time period."""
        metrics = defaultdict(list)

        for _, entries in time_periods.items():
            # Video count
            metrics["video_count"].append(len(entries))

            # Total duration
            total_duration = sum(entry.get("duration", 0) for entry in entries)
            metrics["total_duration"].append(total_duration)

            # Average duration
            avg_duration = total_duration / len(entries) if entries else 0
            metrics["avg_duration"].append(avg_duration)

            # Unique channels
            channels = set(entry.get("channel", "unknown") for entry in entries)
            metrics["unique_channels"].append(len(channels))

            # Category diversity (unique categories)
            categories = set(entry.get("category", "unknown") for entry in entries)
            metrics["categories_diversity"].append(len(categories))

            # Viewing velocity (videos per hour of total content)
            viewing_velocity = (
                len(entries) / (total_duration / 3600) if total_duration > 0 else 0
            )
            metrics["viewing_velocity"].append(viewing_velocity)

            # Engagement metrics (if available)
            if any("engagement_score" in entry for entry in entries):
                engagement_scores = [
                    entry.get("engagement_score", 0) for entry in entries
                ]
                metrics["avg_engagement"].append(np.mean(engagement_scores))

            # Session metrics
            session_count = self._count_sessions(entries)
            metrics["session_count"].append(session_count)

        return dict(metrics)

    def _count_sessions(
        self, entries: List[Dict[str, Any]], gap_threshold: int = 30
    ) -> int:
        """Count viewing sessions in a period."""
        if not entries:
            return 0

        # Only count sessions if timestamp data is available
        timestamped_entries = [e for e in entries if "timestamp" in e]
        if not timestamped_entries:
            return 1  # Assume single session if no timestamp data

        # Sort entries by timestamp
        sorted_entries = sorted(
            timestamped_entries, key=lambda x: datetime.fromisoformat(x["timestamp"])
        )

        sessions = 1
        for i in range(1, len(sorted_entries)):
            current_time = datetime.fromisoformat(sorted_entries[i]["timestamp"])
            prev_time = datetime.fromisoformat(sorted_entries[i - 1]["timestamp"])

            gap_minutes = (current_time - prev_time).total_seconds() / 60
            if gap_minutes > gap_threshold:
                sessions += 1

        return sessions

    def _analyze_metric_trend(
        self, metric_name: str, values: List[float], timeframes: List[str]
    ) -> TrendMetric:
        """Analyze trend for a specific metric."""
        if len(values) < 2:
            return TrendMetric(
                name=metric_name,
                values=values,
                timeframes=timeframes,
                trend_direction="stable",
                trend_strength=0.0,
                statistical_significance=0.0,
            )

        # Normalize values if requested
        if self.normalize and max(values) > 0:
            max_val = max(values)
            normalized_values = [v / max_val for v in values]
        else:
            normalized_values = values

        # Calculate trend direction and strength using linear regression
        x = np.arange(len(values))
        y = np.array(values)

        # Simple linear regression
        if len(values) > 1:
            slope, _ = np.polyfit(x, y, 1)
            # Check if arrays have zero variance before correlation calculation
            if len(values) > 2 and np.std(x) > 0 and np.std(y) > 0:
                correlation = np.corrcoef(x, y)[0, 1]
            else:
                correlation = 0.0
        else:
            slope, correlation = 0.0, 0.0

        # Determine trend direction
        std_threshold = np.std(values) * 0.1 if np.std(values) > 0 else 0.01
        if abs(slope) < std_threshold:
            direction = "stable"
        elif slope > 0:
            direction = "increasing"
        else:
            direction = "decreasing"

        # Calculate trend strength (normalized correlation coefficient)
        strength = abs(correlation) if not np.isnan(correlation) else 0.0

        # Statistical significance (simplified)
        significance = min(1.0, strength * len(values) / 10)

        return TrendMetric(
            name=metric_name,
            values=normalized_values if self.normalize else values,
            timeframes=timeframes,
            trend_direction=direction,
            trend_strength=strength,
            statistical_significance=significance,
        )

    def _detect_significant_changes(
        self, trend_metric: TrendMetric
    ) -> List[SignificantChange]:
        """Detect significant changes in a trend metric."""
        changes = []
        values = trend_metric.values
        timeframes = trend_metric.timeframes

        if len(values) < 2:
            return changes

        # Detect sudden changes (threshold: 50% change)
        for i in range(1, len(values)):
            if values[i - 1] != 0:  # Avoid division by zero
                change_pct = ((values[i] - values[i - 1]) / values[i - 1]) * 100

                if abs(change_pct) > 50:  # Significant change threshold
                    direction = "increase" if change_pct > 0 else "decrease"
                    changes.append(
                        SignificantChange(
                            metric=trend_metric.name,
                            timeframe=timeframes[i],
                            from_value=values[i - 1],
                            to_value=values[i],
                            change_percentage=change_pct,
                            description=f"Significant {direction} of "
                            f"{abs(change_pct):.1f}%",
                        )
                    )

        return changes

    def _generate_summary(
        self, trends: Dict[str, TrendMetric], changes: List[SignificantChange]
    ) -> Dict[str, Any]:
        """Generate a summary of the trend analysis."""
        return {
            "total_metrics_analyzed": len(trends),
            "significant_changes_detected": len(changes),
            "trending_up": [
                name
                for name, tm in trends.items()
                if tm.trend_direction == "increasing"
            ],
            "trending_down": [
                name
                for name, tm in trends.items()
                if tm.trend_direction == "decreasing"
            ],
            "stable_metrics": [
                name for name, tm in trends.items() if tm.trend_direction == "stable"
            ],
            "strongest_trends": sorted(
                [(name, tm.trend_strength) for name, tm in trends.items()],
                key=lambda x: x[1],
                reverse=True,
            )[:3],
        }

    def _get_date_range(self, entries: List[Dict[str, Any]]) -> Dict[str, str]:
        """Get the date range of the entries."""
        if not entries:
            return {"start": None, "end": None}

        timestamps = [datetime.fromisoformat(entry["timestamp"]) for entry in entries]
        return {
            "start": min(timestamps).isoformat(),
            "end": max(timestamps).isoformat(),
        }

    def _empty_result(self) -> Dict[str, Any]:
        """Return empty result structure."""
        return {
            "period_type": self.period_type,
            "timeframes": [],
            "metrics": {},
            "significant_changes": [],
            "summary": {
                "total_metrics_analyzed": 0,
                "significant_changes_detected": 0,
                "trending_up": [],
                "trending_down": [],
                "stable_metrics": [],
                "strongest_trends": [],
            },
            "total_periods_analyzed": 0,
            "date_range": {"start": None, "end": None},
        }

    def _trend_metric_to_dict(self, tm: TrendMetric) -> Dict[str, Any]:
        """Convert TrendMetric to dictionary."""
        return {
            "values": tm.values,
            "trend_direction": tm.trend_direction,
            "trend_strength": tm.trend_strength,
            "statistical_significance": tm.statistical_significance,
        }

    def _change_to_dict(self, sc: SignificantChange) -> Dict[str, Any]:
        """Convert SignificantChange to dictionary."""
        return {
            "metric": sc.metric,
            "timeframe": sc.timeframe,
            "from_value": sc.from_value,
            "to_value": sc.to_value,
            "change_percentage": sc.change_percentage,
            "description": sc.description,
        }
