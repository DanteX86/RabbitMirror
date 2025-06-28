from typing import List, Dict, Any, Tuple
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import KMeans
from collections import Counter, defaultdict
import numpy as np
from datetime import datetime, timedelta
import re

class ProfileSimulator:
    def __init__(self, seed: int = None):
        self.rng = np.random.RandomState(seed)
        self.scaler = MinMaxScaler()
        self.time_bins = 24  # 24 hours
        self.interval_bins = 50  # For interval distribution

    def simulate_profile(self, base_profile: List[Dict[str, Any]], 
                        duration_days: int = 30) -> List[Dict[str, Any]]:
        """Simulate a watch history profile based on existing patterns."""
        # Extract patterns from base profile
        viewing_patterns = self._extract_viewing_patterns(base_profile)
        
        # Generate simulated timeline
        timeline = self._generate_timeline(duration_days)
        
        # Generate simulated entries
        simulated_entries = []
        current_time = timeline[0]
        
        for day in timeline:
            # Generate number of videos to watch based on average daily count
            daily_count = self._sample_daily_count(viewing_patterns['daily_counts'])
            
            # Generate entries for the day
            daily_entries = self._generate_daily_entries(
                current_time, 
                viewing_patterns, 
                daily_count
            )
            
            simulated_entries.extend(daily_entries)
            current_time += timedelta(days=1)
            
        return simulated_entries

    def _extract_viewing_patterns(self, profile: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract viewing patterns from the base profile."""
        # Sort profile by timestamp
        sorted_profile = sorted(profile, key=lambda x: x['timestamp'])
        
        # Extract all pattern types
        time_dist = self._analyze_time_distribution(sorted_profile)
        content_dist = self._analyze_content_distribution(sorted_profile)
        interval_dist = self._analyze_interval_distribution(sorted_profile)
        daily_counts = self._analyze_daily_counts(sorted_profile)
        title_patterns = self._analyze_title_patterns(sorted_profile)
        
        return {
            'time_dist': time_dist,
            'content_dist': content_dist,
            'interval_dist': interval_dist,
            'daily_counts': daily_counts,
            'title_patterns': title_patterns
        }

    def _generate_timeline(self, duration_days: int) -> List[datetime]:
        """Generate a timeline for the simulated profile."""
        start_date = datetime.now() - timedelta(days=duration_days)
        # Ensure we start at midnight
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        return [start_date + timedelta(days=x) for x in range(duration_days)]

    def _generate_daily_entries(self, start_time: datetime,
                               patterns: Dict[str, Any],
                               count: int) -> List[Dict[str, Any]]:
        """Generate watch history entries for a single day."""
        entries = []
        current_time = start_time

        for _ in range(count):
            # Sample time of day based on distribution
            hour = self._sample_from_distribution(patterns['time_dist'])
            current_time = current_time.replace(hour=hour)
            
            # Sample content type and generate title
            content_type = self._sample_from_dict(patterns['content_dist'])
            title = self._generate_title(patterns['title_patterns'], content_type)
            
            # Add random minutes within the hour
            minutes = self.rng.randint(0, 60)
            current_time = current_time.replace(minute=minutes)
            
            entries.append({
                'title': title,
                'timestamp': current_time.isoformat(),
                'category': content_type,
                'simulated': True
            })
            
            # Add interval to next video
            if patterns['interval_dist'].size > 0:
                interval = self._sample_from_distribution(patterns['interval_dist'])
                current_time += timedelta(minutes=int(interval))
        
        return entries

    def _analyze_time_distribution(self, profile: List[Dict[str, Any]]) -> np.ndarray:
        """Analyze the distribution of view times throughout the day."""
        hours = []
        for entry in profile:
            dt = datetime.fromisoformat(entry['timestamp'])
            hours.append(dt.hour)
            
        # Create histogram of hours
        hist, _ = np.histogram(hours, bins=self.time_bins, range=(0, 24))
        return hist / hist.sum()  # Normalize to probabilities

    def _analyze_content_distribution(self, profile: List[Dict[str, Any]]) -> Dict[str, float]:
        """Analyze the distribution of content types using title clustering."""
        # Extract titles and perform simple categorization
        categories = defaultdict(int)
        total = len(profile)
        
        for entry in profile:
            title = entry['title'].lower()
            # Simple rule-based categorization
            if any(word in title for word in ['tutorial', 'how to', 'guide']):
                categories['educational'] += 1
            elif any(word in title for word in ['music', 'song', 'audio']):
                categories['music'] += 1
            elif any(word in title for word in ['game', 'gaming', 'playthrough']):
                categories['gaming'] += 1
            elif any(word in title for word in ['vlog', 'daily', 'life']):
                categories['vlog'] += 1
            else:
                categories['other'] += 1
        
        # Convert to probabilities
        return {k: v/total for k, v in categories.items()}

    def _analyze_interval_distribution(self, profile: List[Dict[str, Any]]) -> np.ndarray:
        """Analyze the distribution of intervals between views."""
        intervals = []
        for i in range(1, len(profile)):
            current = datetime.fromisoformat(profile[i]['timestamp'])
            previous = datetime.fromisoformat(profile[i-1]['timestamp'])
            interval = (current - previous).total_seconds() / 60  # Convert to minutes
            if interval < 24*60:  # Only consider intervals less than 24 hours
                intervals.append(interval)
        
        if not intervals:
            return np.array([30])  # Default 30-minute interval if no data
            
        # Create histogram of intervals
        hist, _ = np.histogram(intervals, bins=self.interval_bins)
        return hist / hist.sum()  # Normalize to probabilities

    def _analyze_daily_counts(self, profile: List[Dict[str, Any]]) -> Tuple[float, float]:
        """Analyze the distribution of daily video counts."""
        daily_counts = defaultdict(int)
        for entry in profile:
            date = datetime.fromisoformat(entry['timestamp']).date()
            daily_counts[date] += 1
            
        counts = list(daily_counts.values())
        return np.mean(counts), np.std(counts)

    def _analyze_title_patterns(self, profile: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Analyze patterns in video titles for each content type."""
        title_patterns = defaultdict(list)
        for entry in profile:
            title = entry['title']
            # Extract common title patterns (e.g., "Artist - Song", "GameName EP.1")
            patterns = self._extract_title_patterns(title)
            if 'category' in entry:
                title_patterns[entry['category']].extend(patterns)
            
        return dict(title_patterns)

    def _extract_title_patterns(self, title: str) -> List[str]:
        """Extract common patterns from a title."""
        patterns = []
        # Common YouTube title patterns
        if ' - ' in title:
            patterns.append('CREATOR - CONTENT')
        if re.search(r'EP\.?\s*\d+', title, re.I):
            patterns.append('SERIES_WITH_EPISODE')
        if re.search(r'\(.*\)', title):
            patterns.append('TITLE_WITH_PARENTHESES')
        if re.search(r'\[.*\]', title):
            patterns.append('TITLE_WITH_BRACKETS')
        if not patterns:
            patterns.append('SIMPLE_TITLE')
        return patterns

    def _sample_daily_count(self, count_stats: Tuple[float, float]) -> int:
        """Sample the number of videos to watch in a day."""
        mean, std = count_stats
        count = int(self.rng.normal(mean, std))
        return max(1, count)  # Ensure at least 1 video per day

    def _sample_from_distribution(self, dist: np.ndarray) -> int:
        """Sample an index from a probability distribution."""
        return self.rng.choice(len(dist), p=dist/dist.sum())

    def _sample_from_dict(self, dist: Dict[str, float]) -> str:
        """Sample a key from a dictionary of probabilities."""
        keys = list(dist.keys())
        probs = list(dist.values())
        return self.rng.choice(keys, p=probs)

    def _generate_title(self, patterns: Dict[str, List[str]], content_type: str) -> str:
        """Generate a title based on learned patterns."""
        if content_type not in patterns or not patterns[content_type]:
            return f"Simulated {content_type.title()} Video"
            
        pattern = self.rng.choice(patterns[content_type])
        
        if pattern == 'CREATOR - CONTENT':
            return f"Creator{self.rng.randint(1, 100)} - Content{self.rng.randint(1, 100)}"
        elif pattern == 'SERIES_WITH_EPISODE':
            return f"Series{self.rng.randint(1, 20)} EP.{self.rng.randint(1, 50)}"
        elif pattern == 'TITLE_WITH_PARENTHESES':
            return f"Title{self.rng.randint(1, 100)} (Detail{self.rng.randint(1, 20)})"
        elif pattern == 'TITLE_WITH_BRACKETS':
            return f"Title{self.rng.randint(1, 100)} [Info{self.rng.randint(1, 20)}]"
        else:
            return f"Simple Title {self.rng.randint(1, 1000)}"
