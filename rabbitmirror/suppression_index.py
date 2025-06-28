from typing import List, Dict, Any
from collections import Counter
import numpy as np
from datetime import datetime

class SuppressionIndex:
    def __init__(self, baseline_period_days: int = 30):
        self.baseline_period_days = baseline_period_days

    def calculate_suppression(self, entries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate content suppression metrics from watch history."""
        # Sort entries by timestamp
        sorted_entries = sorted(entries, key=lambda x: x['timestamp'])
        
        # Split into baseline and analysis periods
        split_point = self._find_split_point(sorted_entries)
        baseline_entries = sorted_entries[:split_point]
        analysis_entries = sorted_entries[split_point:]
        
        # Calculate metrics
        baseline_metrics = self._calculate_period_metrics(baseline_entries)
        analysis_metrics = self._calculate_period_metrics(analysis_entries)
        
        # Calculate suppression indices
        return {
            'overall_suppression': self._calculate_overall_suppression(
                baseline_metrics, analysis_metrics
            ),
            'category_suppression': self._calculate_category_suppression(
                baseline_metrics, analysis_metrics
            ),
            'temporal_patterns': self._analyze_temporal_patterns(sorted_entries),
            'baseline_metrics': baseline_metrics,
            'analysis_metrics': analysis_metrics
        }

    def _find_split_point(self, entries: List[Dict[str, Any]]) -> int:
        """Find the index that splits entries into baseline and analysis periods."""
        # Implementation would parse timestamps and find the split point
        # based on baseline_period_days
        return len(entries) // 2

    def _calculate_period_metrics(self, entries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate metrics for a given period of entries."""
        return {
            'total_views': len(entries),
            'unique_channels': len(set(entry.get('channel', '') for entry in entries)),
            'category_distribution': self._get_category_distribution(entries),
            'view_velocity': self._calculate_view_velocity(entries)
        }

    def _get_category_distribution(self, entries: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate the distribution of content categories."""
        categories = [entry.get('category', 'unknown') for entry in entries]
        counts = Counter(categories)
        total = sum(counts.values())
        return {cat: count/total for cat, count in counts.items()}

    def _calculate_view_velocity(self, entries: List[Dict[str, Any]]) -> float:
        """Calculate the average velocity of video consumption."""
        # Implementation would calculate views per unit time
        return len(entries) / self.baseline_period_days

    def _calculate_overall_suppression(self, baseline: Dict[str, Any], 
                                     analysis: Dict[str, Any]) -> float:
        """Calculate overall suppression index."""
        if baseline['total_views'] == 0:
            return 0.0
        return 1.0 - (analysis['total_views'] / baseline['total_views'])

    def _calculate_category_suppression(self, baseline: Dict[str, Any], 
                                      analysis: Dict[str, Any]) -> Dict[str, float]:
        """Calculate suppression indices per category."""
        suppression = {}
        for category in baseline['category_distribution']:
            baseline_freq = baseline['category_distribution'].get(category, 0)
            analysis_freq = analysis['category_distribution'].get(category, 0)
            if baseline_freq > 0:
                suppression[category] = 1.0 - (analysis_freq / baseline_freq)
            else:
                suppression[category] = 0.0
        return suppression

    def _analyze_temporal_patterns(self, entries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze temporal patterns in content suppression."""
        # Implementation would analyze how suppression varies over time
        return {}
