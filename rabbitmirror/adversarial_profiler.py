import re
from collections import Counter, defaultdict
from datetime import datetime
from typing import Any, Dict, List

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class AdversarialProfiler:
    def __init__(
        self,
        similarity_threshold: float = 0.7,
        rapid_view_threshold: int = 5,  # minutes
        session_gap: int = 30,  # minutes
        repetition_threshold: int = 3,
        entropy_threshold: float = 0.6,
        chain_threshold: int = 4,  # minimum chain length
        time_zone_threshold: int = 3,  # hours
        engagement_variance_threshold: float = 0.3,
        confidence_decay_rate: float = 0.1,  # Confidence decay over time
        context_weight: float = 0.3,  # Weight for contextual factors
        pattern_weight: float = 0.4,  # Weight for pattern strength
        temporal_weight: float = 0.3,
    ):
        self.vectorizer = TfidfVectorizer(stop_words="english")
        self.similarity_threshold = similarity_threshold
        self.rapid_view_threshold = rapid_view_threshold
        self.session_gap = session_gap
        self.repetition_threshold = repetition_threshold
        self.entropy_threshold = entropy_threshold
        self.chain_threshold = chain_threshold
        self.time_zone_threshold = time_zone_threshold
        self.engagement_variance_threshold = engagement_variance_threshold
        self.confidence_decay_rate = confidence_decay_rate
        self.context_weight = context_weight
        self.pattern_weight = pattern_weight
        self.temporal_weight = temporal_weight

        # Initialize the confidence scoring system
        self.confidence_weights = {
            "pattern_strength": 0.35,
            "temporal_consistency": 0.25,
            "contextual_relevance": 0.20,
            "historical_precedent": 0.20,
        }

        # Pattern-specific confidence modifiers
        self.pattern_modifiers = {
            "exact_match": 1.0,
            "high_similarity": 0.8,
            "temporal_pattern": 0.7,
            "structural_pattern": 0.6,
            "weak_correlation": 0.4,
        }

        # Advanced behavioral definitions
        self.psychological_patterns = {
            # Mood indicators
            "content_mood": {
                "positive": ["uplifting", "happy", "funny", "inspiration"],
                "negative": ["drama", "conflict", "controversy", "criticism"],
                "neutral": ["educational", "informative", "documentary"],
            },
            # Cognitive patterns
            "cognitive_style": {
                "analytical": ["analysis", "review", "explanation", "tutorial"],
                "creative": ["art", "design", "music", "creation"],
                "practical": ["how-to", "guide", "tips", "solution"],
            },
            # Emotional triggers
            "emotional_triggers": {
                "curiosity": ["mystery", "secret", "revealed", "hidden"],
                "urgency": ["breaking", "urgent", "latest", "now"],
                "controversy": ["vs", "debate", "fight", "drama"],
            },
        }

        # Motivation indicators
        self.motivational_patterns = {
            "aspiration": ["goal", "success", "achievement", "dream"],
            "fear_of_missing_out": [
                "exclusive",
                "limited",
                "don't miss",
                "opportunity",
            ],
            "reward": ["bonus", "win", "offer", "deal"],
        }

        # Attention types
        self.attention_patterns = {
            "focused": ["detailed", "deep dive", "analysis"],
            "divided": ["multitask", "overview", "broad"],
            "sustained": ["continuous", "series", "episode"],
        }

        # Social dynamics
        self.social_patterns = {
            "collaboration": ["team", "group", "together"],
            "competition": ["vs", "challenge", "battle"],
            "support": ["help", "support", "assist"],
        }

        # Advanced content preferences
        self.genre_preferences = {
            "genres": {
                "documentary": {"keywords": ["documentary", "history", "nature"]},
                "music": {"keywords": ["music", "concert", "album"]},
                "gaming": {"keywords": ["game", "gaming", "playthrough"]},
                "cooking": {"keywords": ["recipe", "cooking", "food"]},
                "sports": {"keywords": ["match", "game", "tournament"]},
                "news": {"keywords": ["news", "update", "report"]},
            },
            "preferences": defaultdict(int),
        }

        # Enhance content preferences
        self.viewing_habits = {
            # Basic activity patterns
            "activity_pattern": {"weekdays": {}, "weekends": {}, "holidays": {}},
            # Peak analysis
            "peak_analysis": {
                "peak_hours": [],
                "off_peak_hours": [],
                "peak_days": [],
                "intensity_score": 0.0,
            },
            # Session metrics
            "session_metrics": {
                "avg_duration": 0.0,
                "avg_videos_per_session": 0.0,
                "session_consistency": 0.0,
                "break_patterns": [],
            },
            # Time slice patterns
            "time_slices": {
                "morning": {"start": 5, "end": 11, "count": 0},
                "afternoon": {"start": 11, "end": 17, "count": 0},
                "evening": {"start": 17, "end": 23, "count": 0},
                "night": {"start": 23, "end": 5, "count": 0},
            },
            # Seasonal patterns
            "seasonal_patterns": {
                "monthly_distribution": {},
                "seasonal_preferences": {},
                "holiday_behavior": {},
                "weather_correlation": {},
            },
            # Binge patterns
            "binge_metrics": {
                "frequency": 0.0,
                "avg_duration": 0.0,
                "preferred_times": [],
                "content_types": {},
            },
            # Break patterns
            "break_patterns": {
                "avg_break_duration": 0.0,
                "break_consistency": 0.0,
                "break_triggers": [],
                "return_patterns": {},
            },
            # Content timing
            "content_timing": {
                "length_preferences": {},
                "completion_rates": {},
                "abandonment_points": [],
                "rewatch_patterns": {},
            },
            # Device patterns
            "device_patterns": {
                "device_distribution": {},
                "device_preferences": {},
                "cross_device_behavior": {},
                "platform_switches": [],
            },
            # Location patterns
            "location_patterns": {
                "primary_locations": [],
                "location_preferences": {},
                "mobility_patterns": {},
                "travel_impact": {},
            },
        }

        # Production type settings
        self.production_types = {
            "cinematic": {"indicators": ["film", "cinema", "epic"]},
            "vlog": {"indicators": ["vlog", "diary", "daily"]},
            "animation": {"indicators": ["animation", "cartoon", "animated"]},
        }

        self.content_preferences = {
            # Format preferences
            "format_bias": {
                "long_form": {"duration": 1200, "weight": 1.5},  # 20+ minutes
                "medium_form": {"duration": 600, "weight": 1.0},  # 10-20 minutes
                "short_form": {"duration": 180, "weight": 0.8},  # 0-3 minutes
            },
            # Production quality
            "quality_preferences": {
                "professional": {"resolution": "1080p+", "weight": 1.2},
                "semi_pro": {"resolution": "720p", "weight": 1.0},
                "amateur": {"resolution": "480p", "weight": 0.8},
            },
            # Content style
            "style_preferences": {
                "scripted": {"indicators": ["edited", "produced", "series"]},
                "spontaneous": {"indicators": ["live", "vlog", "reaction"]},
                "interactive": {"indicators": ["stream", "Q&A", "chat"]},
            },
        }

        # Advanced interaction patterns
        self.interaction_signatures = {
            # Viewing rhythm patterns
            "viewing_rhythm": {
                "binge": {"consecutive_hours": 3, "videos_per_hour": 12},
                "paced": {"break_interval": 30, "session_limit": 120},
                "sporadic": {"session_gap": 120, "variance": 0.5},
                "cyclical": {"period_hours": 24, "consistency": 0.8},
                "adaptive": {"context_switches": 5, "adaptation_rate": 0.3},
            },
            # Engagement depth patterns
            "engagement_depth": {
                "passive": {
                    "interaction_rate": 0.1,
                    "comment_rate": 0.01,
                    "share_rate": 0.005,
                    "save_rate": 0.02,
                    "completion_rate": 0.3,
                },
                "active": {
                    "interaction_rate": 0.3,
                    "comment_rate": 0.05,
                    "share_rate": 0.02,
                    "save_rate": 0.05,
                    "completion_rate": 0.7,
                },
                "highly_engaged": {
                    "interaction_rate": 0.5,
                    "comment_rate": 0.1,
                    "share_rate": 0.05,
                    "save_rate": 0.1,
                    "completion_rate": 0.9,
                },
                "creator": {
                    "interaction_rate": 0.8,
                    "comment_rate": 0.2,
                    "share_rate": 0.15,
                    "save_rate": 0.2,
                    "completion_rate": 0.95,
                },
            },
            # Mouse/touch interaction patterns
            "interaction_patterns": {
                "scroll_behavior": {
                    "smooth": {"variance": 0.1, "speed": "moderate"},
                    "erratic": {"variance": 0.8, "speed": "variable"},
                    "methodical": {"variance": 0.2, "speed": "slow"},
                    "skimming": {"variance": 0.4, "speed": "fast"},
                },
                "click_patterns": {
                    "deliberate": {"interval": 2.0, "accuracy": 0.9},
                    "rapid": {"interval": 0.3, "accuracy": 0.6},
                    "exploratory": {"interval": 1.0, "accuracy": 0.7},
                    "automated": {"interval": 0.1, "accuracy": 0.99},
                },
                "hover_behavior": {
                    "focused": {"duration": 2.0, "movement": "minimal"},
                    "scanning": {"duration": 0.5, "movement": "continuous"},
                    "erratic": {"duration": 0.2, "movement": "random"},
                    "targeted": {"duration": 1.0, "movement": "direct"},
                },
            },
            # Navigation style patterns
            "navigation_style": {
                "methodical": {
                    "pattern": "sequential",
                    "backtrack_rate": 0.1,
                    "depth_first": True,
                    "completion_bias": 0.9,
                },
                "exploratory": {
                    "pattern": "branching",
                    "backtrack_rate": 0.3,
                    "breadth_first": True,
                    "novelty_bias": 0.7,
                },
                "chaotic": {
                    "pattern": "random",
                    "backtrack_rate": 0.5,
                    "session_focus": "low",
                    "topic_variance": 0.8,
                },
                "focused": {
                    "pattern": "targeted",
                    "backtrack_rate": 0.05,
                    "topic_consistency": 0.9,
                    "session_focus": "high",
                },
            },
            # Feature interaction patterns
            "feature_usage": {
                "basic": {
                    "features_used": ["play", "pause", "seek"],
                    "usage_frequency": "low",
                    "complexity": 0.2,
                },
                "intermediate": {
                    "features_used": ["play", "pause", "seek", "quality", "speed"],
                    "usage_frequency": "medium",
                    "complexity": 0.5,
                },
                "advanced": {
                    "features_used": [
                        "play",
                        "pause",
                        "seek",
                        "quality",
                        "speed",
                        "annotations",
                        "chapters",
                    ],
                    "usage_frequency": "high",
                    "complexity": 0.8,
                },
                "power_user": {
                    "features_used": [
                        "play",
                        "pause",
                        "seek",
                        "quality",
                        "speed",
                        "annotations",
                        "chapters",
                        "shortcuts",
                        "pip",
                    ],
                    "usage_frequency": "very_high",
                    "complexity": 1.0,
                },
            },
            # Social interaction patterns
            "social_engagement": {
                "lurker": {
                    "comment_frequency": 0.01,
                    "reply_rate": 0.0,
                    "community_participation": "passive",
                },
                "casual": {
                    "comment_frequency": 0.05,
                    "reply_rate": 0.2,
                    "community_participation": "occasional",
                },
                "active": {
                    "comment_frequency": 0.2,
                    "reply_rate": 0.5,
                    "community_participation": "regular",
                },
                "influencer": {
                    "comment_frequency": 0.4,
                    "reply_rate": 0.8,
                    "community_participation": "leader",
                },
            },
            # Time-based interaction patterns
            "temporal_patterns": {
                "consistent": {
                    "regularity": 0.9,
                    "session_timing": "fixed",
                    "duration_variance": 0.1,
                },
                "variable": {
                    "regularity": 0.5,
                    "session_timing": "flexible",
                    "duration_variance": 0.5,
                },
                "opportunistic": {
                    "regularity": 0.2,
                    "session_timing": "random",
                    "duration_variance": 0.8,
                },
                "scheduled": {
                    "regularity": 0.95,
                    "session_timing": "periodic",
                    "duration_variance": 0.05,
                },
            },
            # Device switching patterns
            "device_patterns": {
                "single_device": {
                    "device_count": 1,
                    "switch_frequency": 0,
                    "preferred_device": "primary",
                },
                "multi_device": {
                    "device_count": 3,
                    "switch_frequency": 0.3,
                    "context_aware": True,
                },
                "adaptive": {
                    "device_count": 5,
                    "switch_frequency": 0.6,
                    "context_aware": True,
                },
                "specialized": {
                    "device_count": 2,
                    "switch_frequency": 0.2,
                    "content_specific": True,
                },
            },
        }

        # Behavioral pattern definitions
        self.behavioral_patterns = {
            # Watch time patterns
            "attention_span": {
                "short": {"duration": 0, "threshold": 30},  # 0-30 seconds
                "medium": {"duration": 30, "threshold": 300},  # 30s-5min
                "long": {"duration": 300, "threshold": 1800},  # 5-30min
            },
            # Interaction patterns
            "interaction_patterns": {
                "passive": {"clicks": 0, "scrolls": 0, "hovers": 0},
                "normal": {"clicks": 1, "scrolls": 5, "hovers": 3},
                "hyperactive": {"clicks": 5, "scrolls": 20, "hovers": 10},
            },
            # Navigation patterns
            "navigation_patterns": {
                "linear": "sequential_progression",
                "random": "random_access",
                "depth_first": "topic_exploration",
                "breadth_first": "category_browsing",
            },
            # Consumption patterns
            "consumption_patterns": {
                "binge": {
                    "videos_per_hour": 12,
                    "duration": 3,
                },  # 12+ videos/hour for 3+ hours
                "sporadic": {"max_gap": 120},  # 2+ hour gaps between sessions
                "consistent": {"std_deviation": 0.2},  # Low variance in viewing times
            },
            # Search patterns
            "search_patterns": {
                "focused": {"topic_variance": 0.2},  # Low topic variance
                "exploratory": {"topic_variance": 0.8},  # High topic variance
                "systematic": {"query_interval": 30},  # Regular search intervals
            },
            # Response patterns
            "response_patterns": {
                "instant": {"delay": 1},  # 1 second response
                "natural": {"delay": 5},  # 5 seconds response
                "considered": {"delay": 30},  # 30 seconds response
            },
            # Multi-tasking patterns
            "multitask_patterns": {
                "single": {"concurrent_activities": 1},
                "moderate": {"concurrent_activities": 3},
                "intensive": {"concurrent_activities": 5},
            },
        }

        # Response time thresholds (in seconds)
        self.response_thresholds = {
            "click": {"min": 0.1, "max": 2.0},
            "scroll": {"min": 0.2, "max": 3.0},
            "hover": {"min": 0.3, "max": 5.0},
            "pause": {"min": 0.5, "max": 10.0},
            "resume": {"min": 0.2, "max": 4.0},
        }

        # Activity transition probabilities
        self.activity_transitions = {
            "watch": {"pause": 0.3, "scroll": 0.3, "click": 0.2, "exit": 0.2},
            "pause": {"resume": 0.7, "exit": 0.2, "scroll": 0.1},
            "scroll": {"watch": 0.4, "click": 0.3, "pause": 0.2, "exit": 0.1},
            "click": {"watch": 0.5, "scroll": 0.3, "pause": 0.1, "exit": 0.1},
        }

        # Context confidence factors
        self.context_factors = {
            # Temporal factors
            "time_of_day": 0.10,
            "day_of_week": 0.10,
            "session_position": 0.10,
            "seasonal_pattern": 0.05,
            # User behavior factors
            "user_history": 0.08,
            "interaction_pattern": 0.08,
            "device_consistency": 0.04,
            "speed_pattern": 0.04,
            "attention_pattern": 0.04,
            "navigation_style": 0.04,
            "multitask_behavior": 0.04,
            "response_timing": 0.04,
            # Content factors
            "content_category": 0.10,
            "content_length": 0.05,
            "content_popularity": 0.05,
            "channel_reputation": 0.05,
            # Network factors
            "ip_pattern": 0.05,
            "network_type": 0.05,
            # Engagement factors
            "completion_rate": 0.05,
            "interaction_depth": 0.05,
            "social_signals": 0.05,
        }

        # Seasonal patterns for context
        self.seasonal_patterns = {
            "weekday_working": {"start": 9, "end": 17},  # 9 AM - 5 PM
            "weekday_evening": {"start": 17, "end": 23},  # 5 PM - 11 PM
            "weekend_daytime": {"start": 10, "end": 20},  # 10 AM - 8 PM
            "late_night": {"start": 23, "end": 5},  # 11 PM - 5 AM
        }

        # Device type patterns
        self.device_patterns = {
            "mobile": {"min_interval": 0.5, "max_duration": 30},
            "tablet": {"min_interval": 1, "max_duration": 45},
            "desktop": {"min_interval": 2, "max_duration": 120},
            "tv": {"min_interval": 5, "max_duration": 180},
        }

        # Content engagement thresholds
        self.engagement_thresholds = {
            "short_form": {"duration": 5, "completion_rate": 0.8},
            "medium_form": {"duration": 20, "completion_rate": 0.7},
            "long_form": {"duration": 60, "completion_rate": 0.6},
        }

        # Social interaction patterns
        self.social_patterns = {
            "likes_per_view": 0.01,  # 1% like rate is typical
            "comments_per_view": 0.002,  # 0.2% comment rate is typical
            "shares_per_view": 0.005,  # 0.5% share rate is typical
        }

    def identify_adversarial_patterns(
        self, entries: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Identify potential adversarial patterns in watch history."""
        if not entries:
            return self._empty_result()

        # Sort entries by timestamp
        sorted_entries = sorted(entries, key=lambda x: x["timestamp"])
        titles = [entry["title"] for entry in sorted_entries]

        # Create TF-IDF matrix and similarity analysis
        tfidf_matrix = self.vectorizer.fit_transform(titles)
        similarity_matrix = cosine_similarity(tfidf_matrix)

        # Detect various patterns
        rapid_views = self._detect_rapid_views(sorted_entries)
        content_loops = self._detect_content_loops(similarity_matrix, sorted_entries)
        binge_patterns = self._detect_binge_patterns(sorted_entries)
        anomalous_sessions = self._detect_anomalous_sessions(sorted_entries)
        suspicious_sequences = self._detect_suspicious_sequences(sorted_entries)
        behavior_chains = self._detect_behavior_chains(sorted_entries)
        geographic_anomalies = self._detect_geographic_anomalies(sorted_entries)
        engagement_patterns = self._detect_engagement_patterns(sorted_entries)
        language_switches = self._detect_language_switches(sorted_entries)
        topic_shifts = self._detect_topic_shifts(sorted_entries, similarity_matrix)

        # Calculate content entropy
        content_entropy = self._calculate_content_entropy(titles)
        channel_entropy = self._calculate_channel_entropy(sorted_entries)

        # Analyze temporal patterns
        temporal_analysis = self._analyze_temporal_patterns(sorted_entries)

        return {
            "risk_score": self._calculate_risk_score(
                {
                    "rapid_views": len(rapid_views),
                    "content_loops": len(content_loops),
                    "binge_patterns": len(binge_patterns),
                    "anomalous_sessions": len(anomalous_sessions),
                    "suspicious_sequences": len(suspicious_sequences),
                    "content_entropy": content_entropy,
                    "channel_entropy": channel_entropy,
                }
            ),
            "patterns": {
                "rapid_views": rapid_views,
                "content_loops": content_loops,
                "binge_patterns": binge_patterns,
                "anomalous_sessions": anomalous_sessions,
                "suspicious_sequences": suspicious_sequences,
                "behavior_chains": behavior_chains,
                "geographic_anomalies": geographic_anomalies,
                "engagement_patterns": engagement_patterns,
                "language_switches": language_switches,
                "topic_shifts": topic_shifts,
            },
            "entropy_analysis": {
                "content_entropy": content_entropy,
                "channel_entropy": channel_entropy,
            },
            "temporal_analysis": temporal_analysis,
            "similarity_stats": {
                "mean": float(np.mean(similarity_matrix)),
                "std": float(np.std(similarity_matrix)),
                "max": float(np.max(similarity_matrix)),
            },
        }

    def _detect_rapid_views(
        self, entries: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Detect unusually rapid viewing patterns."""
        rapid_views = []
        for i in range(1, len(entries)):
            current = datetime.fromisoformat(entries[i]["timestamp"])
            previous = datetime.fromisoformat(entries[i - 1]["timestamp"])
            interval = (current - previous).total_seconds() / 60

            if interval < self.rapid_view_threshold:
                rapid_views.append(
                    {
                        "timestamp": entries[i]["timestamp"],
                        "interval": interval,
                        "previous_title": entries[i - 1]["title"],
                        "current_title": entries[i]["title"],
                        "confidence": self._calculate_confidence(interval),
                    }
                )
        return rapid_views

    def _detect_content_loops(
        self, similarity_matrix: np.ndarray, entries: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Detect repeated viewing patterns of similar content."""
        loops = []
        for i, _ in enumerate(similarity_matrix):
            similar_indices = np.where(
                similarity_matrix[i] > self.similarity_threshold
            )[0]
            if len(similar_indices) >= self.repetition_threshold:
                # Get temporal sequence of similar videos
                similar_entries = [
                    {
                        "title": entries[j]["title"],
                        "timestamp": entries[j]["timestamp"],
                        "similarity": float(similarity_matrix[i][j]),
                    }
                    for j in similar_indices
                    if j != i
                ]

                loops.append(
                    {
                        "base_entry": {
                            "title": entries[i]["title"],
                            "timestamp": entries[i]["timestamp"],
                        },
                        "similar_entries": similar_entries,
                        "pattern_duration": self._calculate_pattern_duration(
                            similar_entries
                        ),
                        "confidence": self._calculate_loop_confidence(similar_entries),
                    }
                )
        return loops

    def _detect_binge_patterns(
        self, entries: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Detect binge-watching patterns that might indicate automation."""
        sessions = self._split_into_sessions(entries)
        binge_patterns = []

        for session in sessions:
            if len(session) > 10:  # Minimum session length for binge analysis
                intervals = self._calculate_intervals(session)
                if self._is_suspicious_interval_pattern(intervals):
                    binge_patterns.append(
                        {
                            "start_time": session[0]["timestamp"],
                            "end_time": session[-1]["timestamp"],
                            "video_count": len(session),
                            "mean_interval": float(np.mean(intervals)),
                            "std_interval": float(np.std(intervals)),
                            "confidence": self._calculate_binge_confidence(intervals),
                        }
                    )
        return binge_patterns

    def _detect_anomalous_sessions(
        self, entries: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Detect viewing sessions with anomalous patterns."""
        sessions = self._split_into_sessions(entries)
        anomalous_sessions = []

        for session in sessions:
            metrics = self._calculate_session_metrics(session)
            if self._is_anomalous_session(metrics):
                anomalous_sessions.append(
                    {
                        "start_time": session[0]["timestamp"],
                        "end_time": session[-1]["timestamp"],
                        "video_count": len(session),
                        "metrics": metrics,
                        "confidence": self._calculate_anomaly_confidence(metrics),
                    }
                )
        return anomalous_sessions

    def _detect_suspicious_sequences(
        self, entries: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Detect suspicious sequences of video views."""
        sequences = []
        for i in range(len(entries) - 2):  # Look at sequences of 3 videos
            seq = entries[i : i + 3]
            if self._is_suspicious_sequence(seq):
                sequences.append(
                    {
                        "start_time": seq[0]["timestamp"],
                        "end_time": seq[-1]["timestamp"],
                        "titles": [entry["title"] for entry in seq],
                        "pattern_type": self._identify_sequence_pattern(seq),
                        "confidence": self._calculate_sequence_confidence(seq),
                    }
                )
        return sequences

    def _calculate_content_entropy(self, titles: List[str]) -> float:
        """Calculate entropy of content diversity."""
        words = " ".join(titles).lower().split()
        word_counts = Counter(words)
        total = sum(word_counts.values())
        probabilities = [count / total for count in word_counts.values()]
        return float(-sum(p * np.log2(p) for p in probabilities))

    def _calculate_channel_entropy(self, entries: List[Dict[str, Any]]) -> float:
        """Calculate entropy of channel diversity."""
        channels = [entry.get("channel", "unknown") for entry in entries]
        channel_counts = Counter(channels)
        total = sum(channel_counts.values())
        probabilities = [count / total for count in channel_counts.values()]
        return float(-sum(p * np.log2(p) for p in probabilities))

    def _analyze_temporal_patterns(
        self, entries: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze temporal patterns in viewing behavior."""
        timestamps = [datetime.fromisoformat(entry["timestamp"]) for entry in entries]
        hours = [ts.hour for ts in timestamps]
        weekdays = [ts.weekday() for ts in timestamps]

        return {
            "hourly_distribution": self._calculate_distribution(hours, 24),
            "weekly_distribution": self._calculate_distribution(weekdays, 7),
            "regularity_score": self._calculate_regularity_score(timestamps),
        }

    def _calculate_risk_score(self, metrics: Dict[str, float]) -> float:
        """Calculate overall risk score based on detected patterns."""
        weights = {
            "rapid_views": 0.2,
            "content_loops": 0.2,
            "binge_patterns": 0.15,
            "anomalous_sessions": 0.15,
            "suspicious_sequences": 0.1,
            "content_entropy": 0.1,
            "channel_entropy": 0.1,
        }

        score = 0.0
        for key, weight in weights.items():
            if key in ["content_entropy", "channel_entropy"]:
                # Lower entropy increases risk
                score += weight * (1 - metrics[key])
            else:
                # More patterns increase risk
                score += weight * min(1.0, metrics[key] / 10.0)

        return float(min(1.0, score))

    # Helper methods
    def _split_into_sessions(
        self, entries: List[Dict[str, Any]]
    ) -> List[List[Dict[str, Any]]]:
        """Split entries into viewing sessions based on time gaps."""
        sessions = []
        current_session = [entries[0]]

        for entry in entries[1:]:
            current = datetime.fromisoformat(entry["timestamp"])
            previous = datetime.fromisoformat(current_session[-1]["timestamp"])
            gap = (current - previous).total_seconds() / 60

            if gap > self.session_gap:
                sessions.append(current_session)
                current_session = []
            current_session.append(entry)

        if current_session:
            sessions.append(current_session)

        return sessions

    def _calculate_intervals(self, entries: List[Dict[str, Any]]) -> np.ndarray:
        """Calculate intervals between consecutive views in minutes."""
        intervals = []
        for i in range(1, len(entries)):
            current = datetime.fromisoformat(entries[i]["timestamp"])
            previous = datetime.fromisoformat(entries[i - 1]["timestamp"])
            intervals.append((current - previous).total_seconds() / 60)
        return np.array(intervals)

    def _is_suspicious_interval_pattern(self, intervals: np.ndarray) -> bool:
        """Check if interval pattern is suspiciously regular."""
        if len(intervals) < 3:
            return False
        return float(np.std(intervals)) < 1.0  # Very regular intervals

    def _calculate_session_metrics(
        self, session: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """Calculate various metrics for a viewing session."""
        intervals = self._calculate_intervals(session)

        # Handle case where session has only one entry (no intervals)
        if len(intervals) == 0:
            return {
                "duration": 0.0,
                "mean_interval": 0.0,
                "std_interval": 0.0,
                "video_count": len(session),
            }

        return {
            "duration": float(sum(intervals)),
            "mean_interval": float(np.mean(intervals)),
            "std_interval": float(np.std(intervals)),
            "video_count": len(session),
        }

    def _is_anomalous_session(self, metrics: Dict[str, float]) -> bool:
        """Determine if a session is anomalous based on its metrics."""
        return (
            metrics["std_interval"] < 1.0
            and metrics["video_count"] > 10  # Very regular intervals
            and metrics["mean_interval"] < 5.0  # Long session  # Very short intervals
        )

    def _is_suspicious_sequence(self, sequence: List[Dict[str, Any]]) -> bool:
        """Check if a sequence of videos appears suspicious."""
        if len(sequence) < 3:
            return False

        # Check for exact title repetition
        titles = [entry["title"] for entry in sequence]
        if len(set(titles)) == 1:
            return True

        # Check for very similar titles
        tfidf_matrix = self.vectorizer.fit_transform(titles)
        similarity_matrix = cosine_similarity(tfidf_matrix)
        return np.min(similarity_matrix) > self.similarity_threshold

    def _identify_sequence_pattern(self, sequence: List[Dict[str, Any]]) -> str:
        """Identify the type of suspicious sequence pattern."""
        titles = [entry["title"] for entry in sequence]
        if len(set(titles)) == 1:
            return "exact_repetition"
        if self._has_numeric_progression(titles):
            return "numeric_progression"
        if self._has_similar_structure(titles):
            return "similar_structure"
        return "high_similarity"

    def _calculate_distribution(self, values: List[int], bins: int) -> List[float]:
        """Calculate normalized distribution of values."""
        hist, _ = np.histogram(values, bins=bins, range=(0, bins))
        return [float(x) for x in (hist / hist.sum())]

    def _calculate_regularity_score(self, timestamps: List[datetime]) -> float:
        """Calculate how regular the viewing pattern is (0-1)."""
        intervals = np.diff([ts.timestamp() for ts in timestamps])
        if len(intervals) < 2:
            return 0.0
        return float(1.0 - min(1.0, np.std(intervals) / np.mean(intervals)))

    def _analyze_behavioral_metrics(
        self, entries: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze comprehensive behavioral metrics from the watch history."""
        psych_metrics = self._analyze_psychological_patterns(entries)
        preference_metrics = self._analyze_content_preferences(entries)
        interaction_metrics = self._analyze_interaction_signatures(entries)

        return {
            # Core behavioral metrics
            "attention_metrics": self._analyze_attention_patterns(entries),
            "interaction_metrics": self._analyze_interaction_patterns(entries),
            "navigation_metrics": self._analyze_navigation_patterns(entries),
            "consumption_metrics": self._analyze_consumption_patterns(entries),
            "response_metrics": self._analyze_response_patterns(entries),
            "multitask_metrics": self._analyze_multitask_patterns(entries),
            # Advanced behavioral metrics
            "psychological_metrics": psych_metrics,
            "preference_metrics": preference_metrics,
            "interaction_signature_metrics": interaction_metrics,
            # Derived metrics
            "behavioral_consistency": self._calculate_behavioral_consistency(
                {
                    "attention": psych_metrics["attention_stability"],
                    "interaction": interaction_metrics["pattern_stability"],
                    "navigation": preference_metrics["preference_stability"],
                }
            ),
            "anomaly_indicators": self._detect_behavioral_anomalies(
                {
                    "psychological": psych_metrics,
                    "preferences": preference_metrics,
                    "interactions": interaction_metrics,
                }
            ),
            "risk_factors": self._assess_behavioral_risks(
                {
                    "psychological": psych_metrics,
                    "preferences": preference_metrics,
                    "interactions": interaction_metrics,
                }
            ),
        }

    def _analyze_attention_patterns(
        self, entries: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """Analyze user attention patterns based on video completion and engagement."""
        watch_durations = []
        completion_rates = []
        engagement_scores = []

        for entry in entries:
            duration = entry.get("duration", 0)
            watched = entry.get("watched_duration", 0)
            interactions = entry.get("interaction_count", 0)

            if duration > 0:
                completion = watched / duration
                engagement = interactions / (duration / 60)  # interactions per minute

                watch_durations.append(watched)
                completion_rates.append(completion)
                engagement_scores.append(engagement)

        return {
            "mean_duration": float(np.mean(watch_durations)) if watch_durations else 0,
            "completion_consistency": (
                float(np.std(completion_rates)) if completion_rates else 1
            ),
            "engagement_variability": (
                float(np.std(engagement_scores)) if engagement_scores else 1
            ),
        }

    def _analyze_interaction_patterns(
        self, entries: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """Analyze user interaction patterns and timing."""
        click_intervals = []
        scroll_patterns = []
        hover_durations = []

        for i in range(1, len(entries)):
            current = entries[i]
            previous = entries[i - 1]

            # Analyze click timing
            if "click_timestamp" in current and "click_timestamp" in previous:
                interval = (
                    datetime.fromisoformat(current["click_timestamp"])
                    - datetime.fromisoformat(previous["click_timestamp"])
                ).total_seconds()
                click_intervals.append(interval)

            # Analyze scroll behavior
            if "scroll_count" in current:
                scroll_patterns.append(current["scroll_count"])

            # Analyze hover timing
            if "hover_duration" in current:
                hover_durations.append(current["hover_duration"])

        return {
            "click_regularity": (
                float(np.std(click_intervals)) if click_intervals else float("inf")
            ),
            "scroll_variability": (
                float(np.std(scroll_patterns)) if scroll_patterns else float("inf")
            ),
            "hover_consistency": (
                float(np.std(hover_durations)) if hover_durations else float("inf")
            ),
        }

    def _analyze_navigation_patterns(
        self, entries: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze user navigation patterns through content."""
        category_transitions = []
        topic_sequences = []
        depth_scores = []

        for i in range(1, len(entries)):
            current = entries[i]
            previous = entries[i - 1]

            # Analyze category changes
            if "category" in current and "category" in previous:
                category_transitions.append(
                    1 if current["category"] != previous["category"] else 0
                )

            # Analyze topic progression
            if "topic" in current and "topic" in previous:
                # For simple similarity between topics as strings
                topic_sim = 1.0 if current["topic"] == previous["topic"] else 0.0
                topic_sequences.append(topic_sim)

            # Analyze exploration depth
            if "depth" in current:
                depth_scores.append(current["depth"])

        return {
            "category_switch_rate": (
                float(np.mean(category_transitions)) if category_transitions else 0
            ),
            "topic_coherence": (
                float(np.mean(topic_sequences)) if topic_sequences else 0
            ),
            "exploration_depth": float(np.mean(depth_scores)) if depth_scores else 0,
            "pattern_type": self._identify_navigation_pattern(entries)["pattern_type"],
        }

    def _analyze_consumption_patterns(
        self, entries: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze content consumption patterns."""
        hourly_counts = defaultdict(int)
        session_durations = []
        intervals = []

        current_session = []
        for entry in entries:
            timestamp = datetime.fromisoformat(entry["timestamp"])
            hourly_counts[timestamp.hour] += 1

            if not current_session:
                current_session = [entry]
            else:
                last_timestamp = datetime.fromisoformat(
                    current_session[-1]["timestamp"]
                )
                interval = (timestamp - last_timestamp).total_seconds() / 60

                if interval > self.session_gap:
                    session_durations.append(len(current_session))
                    current_session = [entry]
                else:
                    current_session.append(entry)
                    intervals.append(interval)

        if current_session:
            session_durations.append(len(current_session))

        return {
            "hourly_distribution": dict(hourly_counts),
            "mean_session_length": (
                float(np.mean(session_durations)) if session_durations else 0
            ),
            "interval_consistency": (
                float(np.std(intervals)) if intervals else float("inf")
            ),
            "pattern_type": self._identify_consumption_pattern(entries)["pattern_type"],
        }

    def _analyze_response_patterns(
        self, entries: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze user response patterns to different content types."""
        response_times = defaultdict(list)
        action_sequences = []

        # Analyze response delays from test data
        all_response_times = []

        for entry in entries:
            # Check for various delay fields from test data
            for delay_field in [
                "click_delay",
                "engagement_delay",
                "comment_delay",
                "share_delay",
            ]:
                if delay_field in entry and entry[delay_field] is not None:
                    all_response_times.append(entry[delay_field])

        for i in range(1, len(entries)):
            current = entries[i]
            previous = entries[i - 1]

            # Analyze response times for different actions
            for action in ["click", "scroll", "hover", "pause", "resume"]:
                if (
                    f"{action}_timestamp" in current
                    and f"{action}_timestamp" in previous
                ):
                    response_time = (
                        datetime.fromisoformat(current[f"{action}_timestamp"])
                        - datetime.fromisoformat(previous[f"{action}_timestamp"])
                    ).total_seconds()
                    response_times[action].append(response_time)
                    all_response_times.append(response_time)

            # Analyze action sequences
            if "actions" in current:
                action_sequences.append(current["actions"])

        # Calculate overall response consistency
        if all_response_times:
            avg_response_time = float(np.mean(all_response_times))
            response_consistency = (
                float(np.std(all_response_times)) / avg_response_time
                if avg_response_time > 0
                else 0.0
            )
        else:
            avg_response_time = 0.0
            response_consistency = 0.0

        return {
            "avg_response_time": avg_response_time,
            "response_times": {k: float(np.mean(v)) for k, v in response_times.items()},
            "response_consistency": response_consistency,
            "response_details": {
                k: float(np.std(v)) for k, v in response_times.items()
            },
            "action_patterns": self._analyze_action_sequences(action_sequences),
        }

    def _analyze_psychological_patterns(
        self, entries: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze psychological patterns in viewing behavior."""
        mood_transitions = []
        cognitive_patterns = []
        emotional_triggers = []
        content_polarization = []

        for i in range(1, len(entries)):
            current = entries[i]
            previous = entries[i - 1]

            # Analyze mood transitions
            curr_mood = self._detect_content_mood(current["title"])
            prev_mood = self._detect_content_mood(previous["title"])
            if curr_mood != prev_mood:
                mood_transitions.append(
                    {
                        "from": prev_mood,
                        "to": curr_mood,
                        "timestamp": current["timestamp"],
                    }
                )

            # Analyze cognitive engagement
            cognitive_style = self._detect_cognitive_style(current)
            cognitive_patterns.append(cognitive_style)

            # Detect emotional triggers
            triggers = self._detect_emotional_triggers(current)
            if triggers:
                emotional_triggers.append(
                    {"triggers": triggers, "timestamp": current["timestamp"]}
                )

            # Analyze content polarization
            polarization = self._calculate_content_polarization(current)
            content_polarization.append(polarization)

        return {
            "mood_pattern": {
                "transitions": mood_transitions,
                "stability": self._calculate_pattern_stability(mood_transitions),
            },
            "cognitive_profile": {
                "dominant_style": self._get_dominant_pattern(cognitive_patterns),
                "style_consistency": self._calculate_pattern_consistency(
                    cognitive_patterns
                ),
            },
            "emotional_engagement": {
                "trigger_frequency": len(emotional_triggers) / len(entries),
                "trigger_patterns": self._analyze_trigger_patterns(emotional_triggers),
            },
            "content_bias": {
                "polarization_score": float(np.mean(content_polarization)),
                "bias_trend": self._analyze_bias_trend(content_polarization),
            },
            "attention_stability": self._calculate_attention_stability(entries),
        }

    def _analyze_content_preferences(
        self, entries: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze detailed content preferences and viewing patterns."""
        format_preferences = defaultdict(int)
        quality_preferences = defaultdict(int)
        style_preferences = defaultdict(int)
        temporal_preferences = []

        for entry in entries:
            # Analyze format preferences
            duration = entry.get("duration", 0)
            for format_type, criteria in self.content_preferences[
                "format_bias"
            ].items():
                if duration >= criteria["duration"]:
                    format_preferences[format_type] += criteria["weight"]

            # Analyze quality preferences
            resolution = entry.get("resolution", "480p")
            for quality, criteria in self.content_preferences[
                "quality_preferences"
            ].items():
                if resolution >= criteria["resolution"]:
                    quality_preferences[quality] += criteria["weight"]

            # Analyze style preferences
            for style, criteria in self.content_preferences[
                "style_preferences"
            ].items():
                if any(
                    indicator in entry.get("title", "").lower()
                    for indicator in criteria["indicators"]
                ):
                    style_preferences[style] += 1

            # Track temporal preferences
            timestamp = datetime.fromisoformat(entry["timestamp"])
            temporal_preferences.append(
                {
                    "hour": timestamp.hour,
                    "day": timestamp.weekday(),
                    "duration": duration,
                }
            )

        # Calculate genre metrics
        genre_metrics = self._analyze_genre_preferences(entries)

        # Calculate habit metrics
        habit_metrics = self._analyze_viewing_habits(entries)

        # Calculate production metrics
        production_metrics = self._analyze_production_preferences(entries)

        return {
            # Calculated metrics
            "genre_metrics": genre_metrics,
            "habit_metrics": habit_metrics,
            "production_metrics": production_metrics,
            # Format preferences
            "format_profile": {
                "preferences": dict(format_preferences),
                "dominant_format": max(format_preferences.items(), key=lambda x: x[1])[
                    0
                ],
            },
            "quality_profile": {
                "preferences": dict(quality_preferences),
                "quality_sensitivity": self._calculate_quality_sensitivity(
                    quality_preferences
                ),
            },
            "style_profile": {
                "preferences": dict(style_preferences),
                "style_diversity": self._calculate_style_diversity(style_preferences),
            },
            "temporal_profile": {
                "peak_hours": self._identify_peak_hours(temporal_preferences),
                "consistency": self._calculate_temporal_consistency(
                    temporal_preferences
                ),
            },
            "preference_stability": self._calculate_preference_stability(entries),
        }

    def _analyze_genre_preferences(
        self, entries: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze user preferences by genre."""
        for entry in entries:
            title = entry["title"].lower()
            for genre, settings in self.genre_preferences["genres"].items():
                if any(keyword in title for keyword in settings["keywords"]):
                    self.genre_preferences["preferences"][genre] += 1

        dominant_genre = max(
            self.genre_preferences["preferences"],
            key=self.genre_preferences["preferences"].get,
            default="unknown",
        )

        return {
            "genre_distribution": dict(self.genre_preferences["preferences"]),
            "dominant_genre": dominant_genre,
        }

    def _analyze_viewing_habits(self, entries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Enhanced analysis of user's viewing habits over time."""
        if not entries:
            return self.viewing_habits

        # Initialize aggregators
        time_distributions = self._init_time_distributions()
        sessions = self._split_into_sessions(entries)
        device_usage = self._init_device_tracking(entries)
        content_timing = defaultdict(list)
        location_data = defaultdict(list)

        # Process each entry
        for entry in entries:
            self._process_entry_timing(entry, time_distributions)
            self._process_entry_content(entry, content_timing)
            self._process_entry_device(entry, device_usage)
            self._process_entry_location(entry, location_data)

        # Analyze sessions
        session_metrics = self._analyze_session_metrics(sessions)
        binge_metrics = self._analyze_binge_patterns(sessions)
        break_metrics = self._analyze_break_patterns(sessions)

        # Update viewing habits
        self._update_activity_patterns(time_distributions)
        self._update_peak_analysis(time_distributions)
        self._update_session_metrics(session_metrics)
        self._update_binge_metrics(binge_metrics)
        self._update_break_patterns(break_metrics)
        self._update_content_timing(content_timing)
        self._update_device_patterns(device_usage)
        self._update_location_patterns(location_data)
        self._update_seasonal_patterns(entries)

        return self.viewing_habits

    def _analyze_production_preferences(
        self, entries: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze user preferences for different production types."""
        production_counts = defaultdict(int)
        total_entries = len(entries)

        for entry in entries:
            title = entry.get("title", "").lower()

            # Check for production type indicators
            for production_type, settings in self.production_types.items():
                if any(indicator in title for indicator in settings["indicators"]):
                    production_counts[production_type] += 1

        if total_entries == 0:
            return {
                "production_distribution": {},
                "dominant_production": "unknown",
                "production_score": 0.0,
            }

        # Calculate production preferences as percentages
        production_distribution = {
            prod_type: count / total_entries
            for prod_type, count in production_counts.items()
        }

        dominant_production = max(
            production_distribution.items(),
            key=lambda x: x[1],
            default=("unknown", 0.0),
        )[0]

        production_score = max(production_distribution.values(), default=0.0)

        return {
            "production_distribution": production_distribution,
            "dominant_production": dominant_production,
            "production_score": production_score,
        }

    def _init_time_distributions(self) -> Dict[str, Dict[int, int]]:
        """Initialize time distribution trackers."""
        return {
            "weekdays": defaultdict(int),
            "weekends": defaultdict(int),
            "holidays": defaultdict(int),
            "monthly": defaultdict(int),
            "seasonal": defaultdict(int),
        }

    def _process_entry_timing(
        self, entry: Dict[str, Any], distributions: Dict[str, Dict[int, int]]
    ) -> None:
        """Process timing information from an entry."""
        timestamp = datetime.fromisoformat(entry["timestamp"])
        weekday = timestamp.weekday()
        hour = timestamp.hour
        month = timestamp.month
        season = (month % 12 + 3) // 3

        # Update distributions
        if weekday >= 5:  # Weekends
            distributions["weekends"][hour] += 1
        else:
            distributions["weekdays"][hour] += 1

        if self._is_holiday(timestamp):
            distributions["holidays"][hour] += 1

        distributions["monthly"][month] += 1
        distributions["seasonal"][season] += 1

        # Update time slice counts
        for slice_name, slice_info in self.viewing_habits["time_slices"].items():
            if slice_info["start"] <= hour < slice_info["end"] or (
                slice_info["start"] > slice_info["end"]
                and (hour >= slice_info["start"] or hour < slice_info["end"])
            ):
                self.viewing_habits["time_slices"][slice_name]["count"] += 1

    def _process_entry_content(
        self, entry: Dict[str, Any], content_timing: defaultdict
    ) -> None:
        """Process content-related timing information."""
        duration = entry.get("duration", 0)
        watched = entry.get("watched_duration", 0)
        content_type = entry.get("content_type", "unknown")

        if duration > 0:
            completion_rate = watched / duration
            content_timing["durations"].append(duration)
            content_timing["completion_rates"].append(completion_rate)
            content_timing["content_types"].append(content_type)

            if completion_rate < 0.9:  # Track abandonment points
                content_timing["abandonment_points"].append(watched / duration)

    def _process_entry_device(
        self, entry: Dict[str, Any], device_usage: defaultdict
    ) -> None:
        """Process device-related information."""
        device = entry.get("device_type", "unknown")
        platform = entry.get("platform", "unknown")
        timestamp = datetime.fromisoformat(entry["timestamp"])

        device_usage["devices"].append((device, timestamp))
        device_usage["platforms"].append((platform, timestamp))

    def _process_entry_location(
        self, entry: Dict[str, Any], location_data: defaultdict
    ) -> None:
        """Process location-related information."""
        location = entry.get("location", "unknown")
        timestamp = datetime.fromisoformat(entry["timestamp"])

        location_data["locations"].append((location, timestamp))

    def _analyze_session_metrics(
        self, sessions: List[List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """Analyze detailed session metrics."""
        if not sessions:
            return {}

        durations = []
        videos_per_session = []
        consistency_scores = []

        for session in sessions:
            if len(session) < 2:
                continue

            # Calculate session duration
            start_time = datetime.fromisoformat(session[0]["timestamp"])
            end_time = datetime.fromisoformat(session[-1]["timestamp"])
            duration = (end_time - start_time).total_seconds() / 3600  # hours
            durations.append(duration)

            # Calculate videos per session
            videos_per_session.append(len(session))

            # Calculate session consistency
            intervals = self._calculate_intervals(session)
            consistency = (
                1.0 - min(1.0, np.std(intervals) / np.mean(intervals))
                if len(intervals) > 0 and np.mean(intervals) > 0
                else 0.0
            )
            consistency_scores.append(consistency)

        return {
            "avg_duration": float(np.mean(durations)) if durations else 0.0,
            "avg_videos": (
                float(np.mean(videos_per_session)) if videos_per_session else 0.0
            ),
            "consistency": (
                float(np.mean(consistency_scores)) if consistency_scores else 0.0
            ),
        }

    def _analyze_binge_patterns(
        self, sessions: List[List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """Analyze binge watching patterns."""
        binge_sessions = []
        content_types = defaultdict(int)
        preferred_times = []

        for session in sessions:
            if len(session) < 5:  # Minimum length for binge watching
                continue

            duration = self._calculate_session_duration(session)
            if duration < 2:  # Minimum 2 hours for binge
                continue

            binge_sessions.append(duration)
            start_time = datetime.fromisoformat(session[0]["timestamp"])
            preferred_times.append(start_time.hour)

            # Track content types in binge sessions
            for entry in session:
                content_types[entry.get("content_type", "unknown")] += 1

        return {
            "frequency": len(binge_sessions) / len(sessions) if sessions else 0.0,
            "avg_duration": float(np.mean(binge_sessions)) if binge_sessions else 0.0,
            "preferred_times": self._find_peak_hours(preferred_times),
            "content_types": dict(content_types),
        }

    def _analyze_break_patterns(
        self, sessions: List[List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """Analyze patterns in breaks between sessions."""
        break_durations = []
        break_triggers = defaultdict(int)
        return_patterns = defaultdict(int)

        for i in range(1, len(sessions)):
            if len(sessions[i - 1]) == 0 or len(sessions[i]) == 0:
                continue

            prev_session_end = datetime.fromisoformat(sessions[i - 1][-1]["timestamp"])
            curr_session_start = datetime.fromisoformat(sessions[i][0]["timestamp"])
            break_duration = (
                curr_session_start - prev_session_end
            ).total_seconds() / 3600

            if break_duration > 1:  # Minimum 1 hour for a break
                break_durations.append(break_duration)
                # Analyze last video before break
                break_triggers[sessions[i - 1][-1].get("content_type", "unknown")] += 1
                # Analyze first video after break
                return_patterns[sessions[i][0].get("content_type", "unknown")] += 1

        return {
            "avg_duration": float(np.mean(break_durations)) if break_durations else 0.0,
            "consistency": (
                float(1.0 - np.std(break_durations) / np.mean(break_durations))
                if break_durations and np.mean(break_durations) > 0
                else 0.0
            ),
            "triggers": dict(break_triggers),
            "returns": dict(return_patterns),
        }

    def _update_activity_patterns(
        self, distributions: Dict[str, Dict[int, int]]
    ) -> None:
        """Update activity pattern metrics."""
        self.viewing_habits["activity_pattern"].update(
            {
                "weekdays": dict(distributions["weekdays"]),
                "weekends": dict(distributions["weekends"]),
                "holidays": dict(distributions["holidays"]),
            }
        )

    def _update_peak_analysis(self, distributions: Dict[str, Dict[int, int]]) -> None:
        """Update peak analysis metrics."""
        # Find peak hours
        weekday_peaks = self._find_peak_hours(distributions["weekdays"])
        weekend_peaks = self._find_peak_hours(distributions["weekends"])

        # Find peak days
        total_by_day = defaultdict(int)
        for hour, count in distributions["weekdays"].items():
            total_by_day[hour // 24] += count
        peak_days = [
            day
            for day, count in total_by_day.items()
            if count
            > np.mean(list(total_by_day.values())) + np.std(list(total_by_day.values()))
        ]

        self.viewing_habits["peak_analysis"].update(
            {
                "peak_hours": weekday_peaks + weekend_peaks,
                "off_peak_hours": [
                    h for h in range(24) if h not in (weekday_peaks + weekend_peaks)
                ],
                "peak_days": peak_days,
                "intensity_score": self._calculate_intensity_score(distributions),
            }
        )

    def _update_session_metrics(self, metrics: Dict[str, Any]) -> None:
        """Update session metrics."""
        self.viewing_habits["session_metrics"].update(
            {
                "avg_duration": metrics.get("avg_duration", 0.0),
                "avg_videos_per_session": metrics.get("avg_videos", 0.0),
                "session_consistency": metrics.get("consistency", 0.0),
            }
        )

    def _update_binge_metrics(self, metrics: Dict[str, Any]) -> None:
        """Update binge watching metrics."""
        self.viewing_habits["binge_metrics"].update(metrics)

    def _update_break_patterns(self, metrics: Dict[str, Any]) -> None:
        """Update break pattern metrics."""
        self.viewing_habits["break_patterns"].update(
            {
                "avg_break_duration": metrics.get("avg_duration", 0.0),
                "break_consistency": metrics.get("consistency", 0.0),
                "break_triggers": metrics.get("triggers", {}),
                "return_patterns": metrics.get("returns", {}),
            }
        )

    def _update_content_timing(self, timing_data: defaultdict) -> None:
        """Update content timing metrics."""
        if not timing_data:
            return

        durations = timing_data.get("durations", [])
        completion_rates = timing_data.get("completion_rates", [])
        content_types = timing_data.get("content_types", [])
        abandonment_points = timing_data.get("abandonment_points", [])

        # Calculate length preferences
        length_preferences = self._calculate_length_preferences(durations)

        # Calculate completion rates by content type
        completion_by_type = defaultdict(list)
        for content_type, rate in zip(content_types, completion_rates):
            completion_by_type[content_type].append(rate)

        self.viewing_habits["content_timing"].update(
            {
                "length_preferences": length_preferences,
                "completion_rates": {
                    ct: float(np.mean(rates))
                    for ct, rates in completion_by_type.items()
                },
                "abandonment_points": self._analyze_abandonment_points(
                    abandonment_points
                ),
            }
        )

    def _update_device_patterns(self, device_data: defaultdict) -> None:
        """Update device usage pattern metrics."""
        if not device_data:
            return

        devices = device_data.get("devices", [])
        platforms = device_data.get("platforms", [])

        # Calculate device distribution
        device_counts = Counter(device for device, _ in devices)
        total_devices = sum(device_counts.values())
        device_distribution = (
            {device: count / total_devices for device, count in device_counts.items()}
            if total_devices > 0
            else {}
        )

        # Analyze platform switches
        platform_switches = []
        for i in range(1, len(platforms)):
            if platforms[i][0] != platforms[i - 1][0]:  # Platform changed
                platform_switches.append(
                    {
                        "from": platforms[i - 1][0],
                        "to": platforms[i][0],
                        "timestamp": platforms[i][1],
                    }
                )

        self.viewing_habits["device_patterns"].update(
            {
                "device_distribution": device_distribution,
                "platform_switches": platform_switches,
            }
        )

    def _update_location_patterns(self, location_data: defaultdict) -> None:
        """Update location pattern metrics."""
        if not location_data:
            return

        locations = location_data.get("locations", [])
        location_counts = Counter(loc for loc, _ in locations)

        # Find primary locations (top 3 most frequent)
        primary_locations = [loc for loc, _ in location_counts.most_common(3)]

        # Calculate location preferences by time
        location_prefs = defaultdict(lambda: defaultdict(int))
        for loc, timestamp in locations:
            hour = timestamp.hour
            location_prefs[loc][hour] += 1

        self.viewing_habits["location_patterns"].update(
            {
                "primary_locations": primary_locations,
                "location_preferences": {
                    loc: dict(hours) for loc, hours in location_prefs.items()
                },
            }
        )

    def _update_seasonal_patterns(self, entries: List[Dict[str, Any]]) -> None:
        """Update seasonal pattern metrics."""
        if not entries:
            return

        monthly_dist = defaultdict(int)
        seasonal_prefs = defaultdict(lambda: defaultdict(int))
        holiday_behavior = defaultdict(list)

        for entry in entries:
            timestamp = datetime.fromisoformat(entry["timestamp"])
            month = timestamp.month
            season = (month % 12 + 3) // 3

            monthly_dist[month] += 1
            seasonal_prefs[season][entry.get("content_type", "unknown")] += 1

            if self._is_holiday(timestamp):
                holiday_behavior["content_types"].append(
                    entry.get("content_type", "unknown")
                )
                holiday_behavior["durations"].append(entry.get("duration", 0))

        self.viewing_habits["seasonal_patterns"].update(
            {
                "monthly_distribution": dict(monthly_dist),
                "seasonal_preferences": {
                    season: dict(prefs) for season, prefs in seasonal_prefs.items()
                },
                "holiday_behavior": {
                    "popular_content": Counter(
                        holiday_behavior["content_types"]
                    ).most_common(3),
                    "avg_duration": (
                        float(np.mean(holiday_behavior["durations"]))
                        if holiday_behavior["durations"]
                        else 0.0
                    ),
                },
            }
        )

    def _find_peak_hours(self, counts: Dict[int, int]) -> List[int]:
        """Find peak hours based on activity counts."""
        if not counts:
            return []

        mean = np.mean(list(counts.values()))
        std = np.std(list(counts.values()))
        threshold = mean + std

        return [hour for hour, count in counts.items() if count > threshold]

    def _calculate_intensity_score(
        self, distributions: Dict[str, Dict[int, int]]
    ) -> float:
        """Calculate viewing intensity score."""
        total_views = sum(sum(dist.values()) for dist in distributions.values())
        peak_intensity = max(
            max(dist.values()) for dist in distributions.values() if dist
        )

        if total_views == 0:
            return 0.0

        return float(peak_intensity / total_views)

    def _calculate_length_preferences(self, durations: List[float]) -> Dict[str, float]:
        """Calculate preferences for different content lengths."""
        if not durations:
            return {}

        categories = {
            "short": (0, 300),  # 0-5 minutes
            "medium": (300, 1200),  # 5-20 minutes
            "long": (1200, None),  # 20+ minutes
        }

        counts = defaultdict(int)
        total = len(durations)

        for duration in durations:
            for category, (min_dur, max_dur) in categories.items():
                if min_dur <= duration and (max_dur is None or duration < max_dur):
                    counts[category] += 1
                    break

        return (
            {category: count / total for category, count in counts.items()}
            if total > 0
            else {}
        )

    def _analyze_abandonment_points(self, points: List[float]) -> Dict[str, Any]:
        """Analyze patterns in video abandonment."""
        if not points:
            return {}

        # Group abandonment points into ranges
        ranges = {"early": (0, 0.25), "mid": (0.25, 0.75), "late": (0.75, 1.0)}

        distribution = defaultdict(int)
        for point in points:
            for range_name, (start, end) in ranges.items():
                if start <= point < end:
                    distribution[range_name] += 1
                    break

        total = len(points)
        return {
            "distribution": (
                {
                    range_name: count / total
                    for range_name, count in distribution.items()
                }
                if total > 0
                else {}
            ),
            "avg_point": float(np.mean(points)),
            "std_point": float(np.std(points)),
        }

    def _calculate_session_duration(self, session: List[Dict[str, Any]]) -> float:
        """Calculate duration of a session in hours."""
        if len(session) < 2:
            return 0.0

        start_time = datetime.fromisoformat(session[0]["timestamp"])
        end_time = datetime.fromisoformat(session[-1]["timestamp"])
        return (end_time - start_time).total_seconds() / 3600

    def _analyze_production_types(
        self, entries: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze user preference for various production types."""
        production_preferences = defaultdict(int)

        for entry in entries:
            title = entry["title"].lower()
            for production_type, settings in self.production_types.items():
                if any(indicator in title for indicator in settings["indicators"]):
                    production_preferences[production_type] += 1

        dominant_production = max(
            production_preferences, key=production_preferences.get, default="unknown"
        )

        return {
            "production_distribution": dict(production_preferences),
            "dominant_production": dominant_production,
        }

    def _analyze_interaction_signatures(
        self, entries: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze detailed interaction patterns and signatures."""
        viewing_patterns = []
        engagement_levels = []
        navigation_sequences = []

        current_session = []
        for entry in entries:
            # Analyze viewing patterns
            if not current_session:
                current_session = [entry]
            else:
                gap = (
                    datetime.fromisoformat(entry["timestamp"])
                    - datetime.fromisoformat(current_session[-1]["timestamp"])
                ).total_seconds() / 60

                if (
                    gap
                    > self.interaction_signatures["viewing_rhythm"]["sporadic"][
                        "session_gap"
                    ]
                ):
                    viewing_patterns.append(
                        self._analyze_session_pattern(current_session)
                    )
                    current_session = [entry]
                else:
                    current_session.append(entry)

            # Analyze engagement levels
            engagement_levels.append(
                {
                    "interactions": entry.get("interaction_count", 0),
                    "duration": entry.get("duration", 0),
                    "comments": entry.get("comment_count", 0),
                }
            )

            # Analyze navigation sequences
            if len(current_session) > 1:
                navigation_sequences.append(
                    self._analyze_navigation_sequence(current_session[-2:])
                )

        if current_session:
            viewing_patterns.append(self._analyze_session_pattern(current_session))

        return {
            "viewing_signature": {
                "patterns": viewing_patterns,
                "rhythm_type": self._identify_viewing_rhythm(viewing_patterns),
            },
            "engagement_signature": {
                "profile": self._calculate_engagement_profile(engagement_levels),
                "consistency": self._calculate_engagement_consistency(
                    engagement_levels
                ),
            },
            "navigation_signature": {
                "style": self._identify_navigation_style(navigation_sequences),
                "complexity": self._calculate_navigation_complexity(
                    navigation_sequences
                ),
            },
            "pattern_stability": self._calculate_pattern_stability(entries),
        }

    def _analyze_multitask_patterns(
        self, entries: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze patterns indicating multiple simultaneous activities."""
        concurrent_activities = []
        task_switches = []
        activity_durations = defaultdict(list)

        for entry in entries:
            if "concurrent_count" in entry:
                concurrent_activities.append(entry["concurrent_count"])

            if "task_switches" in entry:
                task_switches.append(entry["task_switches"])

            if "activity_durations" in entry:
                for activity, duration in entry["activity_durations"].items():
                    activity_durations[activity].append(duration)

        return {
            "avg_concurrent_activities": (
                float(np.mean(concurrent_activities)) if concurrent_activities else 0
            ),
            "task_switch_frequency": (
                float(np.mean(task_switches)) if task_switches else 0
            ),
            "activity_balance": self._calculate_activity_balance(activity_durations),
            "multitask_intensity": self._calculate_multitask_intensity(
                concurrent_activities, task_switches
            ),
        }

    def _detect_behavior_chains(
        self, entries: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Detect chains of related behaviors that might indicate automated patterns."""
        # Enhanced with new behavioral metrics
        chains = []
        current_chain = []

        for i in range(1, len(entries)):
            current = entries[i]
            previous = entries[i - 1]

            # Check for behavior continuity
            if self._are_behaviors_related(previous, current):
                if not current_chain:
                    current_chain = [previous]
                current_chain.append(current)
            else:
                if len(current_chain) >= self.chain_threshold:
                    chains.append(
                        {
                            "start_time": current_chain[0]["timestamp"],
                            "end_time": current_chain[-1]["timestamp"],
                            "length": len(current_chain),
                            "pattern_type": self._identify_chain_pattern(current_chain),
                            "confidence": self._calculate_chain_confidence(
                                current_chain
                            ),
                        }
                    )
                current_chain = []

        # Handle last chain
        if len(current_chain) >= self.chain_threshold:
            chains.append(
                {
                    "start_time": current_chain[0]["timestamp"],
                    "end_time": current_chain[-1]["timestamp"],
                    "length": len(current_chain),
                    "pattern_type": self._identify_chain_pattern(current_chain),
                    "confidence": self._calculate_chain_confidence(current_chain),
                }
            )

        return chains

    def _detect_geographic_anomalies(
        self, entries: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Detect anomalies in geographic access patterns based on timestamps."""
        anomalies = []

        for i in range(1, len(entries)):
            current = datetime.fromisoformat(entries[i]["timestamp"])
            previous = datetime.fromisoformat(entries[i - 1]["timestamp"])

            # Calculate time difference and expected travel time
            time_diff = (current - previous).total_seconds() / 3600  # hours

            if time_diff < self.time_zone_threshold and self._has_location_change(
                entries[i - 1], entries[i]
            ):
                anomalies.append(
                    {
                        "timestamp": entries[i]["timestamp"],
                        "previous_location": self._extract_location(entries[i - 1]),
                        "current_location": self._extract_location(entries[i]),
                        "time_difference": time_diff,
                        "confidence": self._calculate_geographic_confidence(time_diff),
                    }
                )

        return anomalies

    def _detect_engagement_patterns(
        self, entries: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Detect suspicious patterns in video engagement metrics."""
        patterns = []
        sessions = self._split_into_sessions(entries)

        for session in sessions:
            metrics = self._calculate_engagement_metrics(session)
            if self._is_suspicious_engagement(metrics):
                patterns.append(
                    {
                        "start_time": session[0]["timestamp"],
                        "end_time": session[-1]["timestamp"],
                        "metrics": metrics,
                        "anomaly_type": self._identify_engagement_anomaly(metrics),
                        "confidence": self._calculate_engagement_confidence(metrics),
                    }
                )

        return patterns

    def _detect_language_switches(
        self, entries: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Detect suspicious patterns in language switching behavior."""
        switches = []
        current_language = None
        switch_count = 0

        for i, _ in enumerate(entries):
            detected_language = self._detect_language(entries[i]["title"])

            if current_language and detected_language != current_language:
                switch_count += 1
                if switch_count >= 3:  # Multiple rapid language switches
                    switches.append(
                        {
                            "timestamp": entries[i]["timestamp"],
                            "from_language": current_language,
                            "to_language": detected_language,
                            "confidence": self._calculate_language_switch_confidence(
                                switch_count
                            ),
                        }
                    )
            else:
                switch_count = 0

            current_language = detected_language

        return switches

    def _detect_topic_shifts(
        self, entries: List[Dict[str, Any]], similarity_matrix: np.ndarray
    ) -> List[Dict[str, Any]]:
        """Detect abrupt and suspicious shifts in video topics."""
        shifts = []
        window_size = 5

        for i in range(window_size, len(entries)):
            # Calculate average similarity within previous window
            window_similarity = np.mean(
                similarity_matrix[i - window_size : i, i - window_size : i]
            )
            # Calculate similarity to current video
            current_similarity = np.mean(similarity_matrix[i - window_size : i, i])

            if current_similarity < window_similarity * 0.5:  # Significant topic shift
                shifts.append(
                    {
                        "timestamp": entries[i]["timestamp"],
                        "previous_topic": self._extract_topic(entries[i - 1]),
                        "new_topic": self._extract_topic(entries[i]),
                        "shift_magnitude": float(
                            window_similarity - current_similarity
                        ),
                        "confidence": self._calculate_topic_shift_confidence(
                            window_similarity, current_similarity
                        ),
                    }
                )

        return shifts

    def _are_behaviors_related(
        self, prev_entry: Dict[str, Any], curr_entry: Dict[str, Any]
    ) -> bool:
        """Check if two consecutive entries show related behavior patterns."""
        # Check title similarity
        titles = [prev_entry["title"], curr_entry["title"]]
        tfidf_matrix = self.vectorizer.fit_transform(titles)
        similarity = cosine_similarity(tfidf_matrix)[0][1]

        # Check time proximity
        time_diff = (
            datetime.fromisoformat(curr_entry["timestamp"])
            - datetime.fromisoformat(prev_entry["timestamp"])
        ).total_seconds() / 60

        return similarity > 0.3 and time_diff < self.session_gap

    def _identify_chain_pattern(self, chain: List[Dict[str, Any]]) -> str:
        """Identify the type of behavior chain pattern."""
        titles = [entry["title"] for entry in chain]

        if self._has_numeric_progression(titles):
            return "sequential_consumption"
        if self._has_similar_structure(titles):
            return "structural_pattern"
        if self._has_temporal_regularity(chain):
            return "temporal_pattern"
        return "content_similarity"

    def _has_location_change(
        self, prev_entry: Dict[str, Any], curr_entry: Dict[str, Any]
    ) -> bool:
        """Check if there's a significant location change between entries."""
        prev_loc = self._extract_location(prev_entry)
        curr_loc = self._extract_location(curr_entry)
        return prev_loc != curr_loc

    def _extract_location(self, entry: Dict[str, Any]) -> str:
        """Extract location information from entry metadata."""
        # This would normally use actual location data if available
        return entry.get("location", "unknown")

    def _calculate_engagement_metrics(
        self, session: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """Calculate engagement metrics for a viewing session."""
        durations = []
        interactions = []

        for entry in session:
            durations.append(float(entry.get("duration", 0)))
            interactions.append(float(entry.get("interaction_count", 0)))

        return {
            "mean_duration": float(np.mean(durations)) if durations else 0.0,
            "std_duration": float(np.std(durations)) if durations else 0.0,
            "mean_interactions": float(np.mean(interactions)) if interactions else 0.0,
            "std_interactions": float(np.std(interactions)) if interactions else 0.0,
        }

    def _is_suspicious_engagement(self, metrics: Dict[str, float]) -> bool:
        """Determine if engagement metrics are suspicious."""
        if metrics["mean_duration"] == 0 or metrics["mean_interactions"] == 0:
            return False

        duration_cv = metrics["std_duration"] / metrics["mean_duration"]
        interaction_cv = metrics["std_interactions"] / metrics["mean_interactions"]

        return (
            duration_cv < self.engagement_variance_threshold
            or interaction_cv < self.engagement_variance_threshold
        )

    def _detect_language(self, text: str) -> str:
        """Detect the language of a text string."""
        # This would normally use a language detection library
        # For now, we'll use a simple heuristic based on common words
        text = text.lower()
        if any(word in text for word in ["the", "and", "or", "in"]):
            return "en"
        if any(word in text for word in ["el", "la", "los", "las"]):
            return "es"
        return "unknown"

    def _extract_topic(self, entry: Dict[str, Any]) -> str:
        """Extract the main topic from a video entry."""
        title = entry["title"].lower()
        # Simple topic detection based on keywords
        if any(word in title for word in ["tutorial", "guide", "how to"]):
            return "educational"
        if any(word in title for word in ["game", "gaming", "playthrough"]):
            return "gaming"
        if any(word in title for word in ["music", "song", "audio"]):
            return "music"
        if any(word in title for word in ["news", "update", "report"]):
            return "news"
        return "other"

    def _has_temporal_regularity(self, entries: List[Dict[str, Any]]) -> bool:
        """Check if entries follow a regular temporal pattern."""
        if len(entries) < 3:
            return False

        intervals = self._calculate_intervals(entries)
        return float(np.std(intervals)) < 1.0  # Very regular intervals

    def _calculate_chain_confidence(self, chain: List[Dict[str, Any]]) -> float:
        """Calculate confidence score for behavior chain detection."""
        if len(chain) < 2:
            return 0.0

        # Consider multiple factors
        temporal_regularity = self._calculate_regularity_score(
            [datetime.fromisoformat(entry["timestamp"]) for entry in chain]
        )
        pattern_strength = self._calculate_pattern_strength(chain)

        return float((temporal_regularity + pattern_strength) / 2)

    def _calculate_geographic_confidence(self, time_diff: float) -> float:
        """Calculate confidence score for geographic anomaly detection."""
        return float(1.0 - min(1.0, time_diff / self.time_zone_threshold))

    # Enhanced confidence calculation helper methods
    def _calculate_temporal_confidence(self, context: Dict[str, Any]) -> float:
        """Calculate confidence based on temporal patterns."""
        confidence = 0.0
        count = 0

        if "time_of_day" in context:
            hour = context["time_of_day"].hour
            # Higher confidence for unusual hours (very late night/early morning)
            time_confidence = 1.0 if (0 <= hour <= 4) else 0.6
            confidence += time_confidence
            count += 1

        if "day_of_week" in context:
            day = context["day_of_week"].weekday()
            # Higher confidence for unusual days (e.g., consistent patterns on holidays)
            day_confidence = 1.0 if day in [5, 6] else 0.7  # Weekend vs weekday
            confidence += day_confidence
            count += 1

        if "interval_consistency" in context:
            # Higher confidence for very regular intervals
            std = context["interval_consistency"].get("std", float("inf"))
            mean = context["interval_consistency"].get("mean", 0)
            if mean > 0:
                consistency = 1.0 - min(1.0, std / mean)
                confidence += consistency
                count += 1

        return float(confidence / max(1, count))

    def _calculate_pattern_confidence(self, context: Dict[str, Any]) -> float:
        """Calculate confidence based on pattern characteristics."""
        confidence = 0.0
        count = 0

        if "pattern_type" in context:
            confidence += self.pattern_modifiers.get(context["pattern_type"], 0.5)
            count += 1

        if "pattern_length" in context:
            # Longer patterns increase confidence
            length_confidence = min(
                1.0, context["pattern_length"] / 10
            )  # Scale to 10 items
            confidence += length_confidence
            count += 1

        if "pattern_similarity" in context:
            confidence += context["pattern_similarity"]
            count += 1

        return float(confidence / max(1, count))

    def _calculate_historical_confidence(self, context: Dict[str, Any]) -> float:
        """Calculate confidence based on historical patterns."""
        confidence = 0.0
        count = 0

        if "historical_frequency" in context:
            # Higher confidence for patterns that rarely occur naturally
            freq = context["historical_frequency"]
            confidence += 1.0 - min(1.0, freq / 100)  # Scale to 100 occurrences
            count += 1

        if "user_history" in context:
            history = context["user_history"]
            if "pattern_frequency" in history:
                # Compare current pattern to historical patterns
                freq = history["pattern_frequency"]
                confidence += 1.0 - min(1.0, freq / 50)  # Scale to 50 occurrences
                count += 1

        return float(confidence / max(1, count))

    def _apply_time_decay(self, timestamp: datetime) -> float:
        """Apply time-based decay to confidence scores."""
        now = datetime.now()
        time_diff = (now - timestamp).total_seconds() / 3600  # Convert to hours
        decay = np.exp(-self.confidence_decay_rate * time_diff)
        return float(max(0.1, decay))  # Maintain minimum confidence of 0.1

    def _calculate_contextual_weight(self, context_type: str, value: Any) -> float:
        """Calculate weight for a specific context type with enhanced context
        analysis."""
        base_weight = self.context_factors.get(context_type, 0.1)

        # Temporal context factors
        if context_type == "time_of_day":
            return self._calculate_temporal_weight(value, base_weight)

        if context_type == "day_of_week":
            return self._calculate_day_weight(value, base_weight)

        if context_type == "seasonal_pattern":
            return self._calculate_seasonal_weight(value, base_weight)

        # User behavior factors
        if context_type == "session_position":
            return self._calculate_session_weight(value, base_weight)

        if context_type == "interaction_pattern":
            return self._calculate_interaction_weight(value, base_weight)

        if context_type == "device_consistency":
            return self._calculate_device_weight(value, base_weight)

        if context_type == "speed_pattern":
            return self._calculate_speed_weight(value, base_weight)

        # Content factors
        if context_type == "content_category":
            return self._calculate_category_weight(value, base_weight)

        if context_type == "content_length":
            return self._calculate_length_weight(value, base_weight)

        if context_type == "content_popularity":
            return self._calculate_popularity_weight(value, base_weight)

        if context_type == "channel_reputation":
            return self._calculate_reputation_weight(value, base_weight)

        # Network factors
        if context_type == "ip_pattern":
            return self._calculate_ip_weight(value, base_weight)

        if context_type == "network_type":
            return self._calculate_network_weight(value, base_weight)

        # Engagement factors
        if context_type == "completion_rate":
            return self._calculate_completion_weight(value, base_weight)

        if context_type == "interaction_depth":
            return self._calculate_depth_weight(value, base_weight)

        if context_type == "social_signals":
            return self._calculate_social_weight(value, base_weight)

        return base_weight

    def _calculate_temporal_weight(self, value: datetime, base_weight: float) -> float:
        """Calculate weight based on time of day."""
        hour = value.hour
        # Higher weight for unusual hours
        if 0 <= hour <= 4:  # Very late night
            return base_weight * 2.0
        if 4 < hour <= 6:  # Early morning
            return base_weight * 1.5
        if 22 <= hour <= 23:  # Late night
            return base_weight * 1.3
        return base_weight

    def _calculate_day_weight(self, value: datetime, base_weight: float) -> float:
        """Calculate weight based on day of week."""
        day = value.weekday()
        # Higher weight for weekends and holidays
        if day >= 5:  # Weekend
            return base_weight * 1.3
        if self._is_holiday(value):  # Holiday
            return base_weight * 1.5
        return base_weight

    def _calculate_seasonal_weight(
        self, value: Dict[str, Any], base_weight: float
    ) -> float:
        """Calculate weight based on seasonal patterns."""
        current_hour = value["hour"]
        pattern_type = value["pattern_type"]
        pattern = self.seasonal_patterns.get(pattern_type, {})

        if pattern and pattern["start"] <= current_hour <= pattern["end"]:
            return base_weight * 1.0
        return base_weight * 1.5  # Outside normal pattern

    def _calculate_session_weight(
        self, value: Dict[str, Any], base_weight: float
    ) -> float:
        """Calculate weight based on session position."""
        position = float(value["current"]) / float(value["total"])
        if position < 0.1 or position > 0.9:  # Very early or late in session
            return base_weight * 1.5
        if position < 0.2 or position > 0.8:  # Early or late in session
            return base_weight * 1.3
        return base_weight

    def _calculate_interaction_weight(
        self, value: Dict[str, Any], base_weight: float
    ) -> float:
        """Calculate weight based on interaction patterns."""
        if "clicks_per_minute" in value:
            clicks = value["clicks_per_minute"]
            if clicks > 20:  # Unusually high interaction rate
                return base_weight * 2.0
            if clicks > 10:
                return base_weight * 1.5
        return base_weight

    def _calculate_device_weight(
        self, value: Dict[str, Any], base_weight: float
    ) -> float:
        """Calculate weight based on device consistency."""
        device_type = value.get("device_type")
        if not device_type:
            return base_weight

        pattern = self.device_patterns.get(device_type, {})
        interval = value.get("interval", 0)
        duration = value.get("duration", 0)

        if interval < pattern.get("min_interval", 0) or duration > pattern.get(
            "max_duration", float("inf")
        ):
            return base_weight * 1.5
        return base_weight

    def _calculate_speed_weight(
        self, value: Dict[str, Any], base_weight: float
    ) -> float:
        """Calculate weight based on viewing speed patterns."""
        speed = value.get("playback_speed", 1.0)
        consistency = value.get("speed_consistency", 1.0)

        if speed > 2.0 or speed < 0.5:  # Unusual playback speed
            return base_weight * 1.5
        if consistency < 0.5:  # Inconsistent speed changes
            return base_weight * 1.3
        return base_weight

    def _calculate_category_weight(
        self, value: Dict[str, Any], base_weight: float
    ) -> float:
        """Calculate weight based on content category."""
        if self._is_suspicious_category(value):
            return base_weight * 1.5
        if "category_switches" in value and value["category_switches"] > 5:
            return base_weight * 1.3
        return base_weight

    def _calculate_length_weight(
        self, value: Dict[str, Any], base_weight: float
    ) -> float:
        """Calculate weight based on content length patterns."""
        duration = value.get("duration", 0)
        completion = value.get("completion_rate", 0)

        if duration < 30 and completion < 0.5:  # Short videos with low completion
            return base_weight * 1.5
        if (
            duration > 3600 and completion > 0.95
        ):  # Long videos with suspiciously high completion
            return base_weight * 1.3
        return base_weight

    def _calculate_popularity_weight(
        self, value: Dict[str, Any], base_weight: float
    ) -> float:
        """Calculate weight based on content popularity."""
        views = value.get("view_count", 0)
        age = value.get("content_age_days", 1)

        if views / age < 1:  # Very unpopular content
            return base_weight * 1.5
        if views / age > 1000000:  # Extremely viral content
            return base_weight * 1.3
        return base_weight

    def _calculate_reputation_weight(
        self, value: Dict[str, Any], base_weight: float
    ) -> float:
        """Calculate weight based on channel reputation."""
        subscriber_count = value.get("subscriber_count", 0)
        age_days = value.get("channel_age_days", 1)

        if subscriber_count < 100 and age_days < 30:  # New, small channels
            return base_weight * 1.5
        if subscriber_count > 1000000:  # Very large channels
            return base_weight * 0.8
        return base_weight

    def _calculate_ip_weight(self, value: Dict[str, Any], base_weight: float) -> float:
        """Calculate weight based on IP patterns."""
        changes = value.get("ip_changes", 0)
        timespan_hours = value.get("timespan_hours", 24)

        if changes / timespan_hours > 0.5:  # More than 1 IP change per 2 hours
            return base_weight * 2.0
        if changes / timespan_hours > 0.2:
            return base_weight * 1.5
        return base_weight

    def _calculate_network_weight(
        self, value: Dict[str, Any], base_weight: float
    ) -> float:
        """Calculate weight based on network type."""
        network_type = value.get("network_type", "")
        changes = value.get("network_changes", 0)

        if network_type in ("proxy", "vpn"):
            return base_weight * 1.5
        if changes > 5:  # Frequent network type changes
            return base_weight * 1.3
        return base_weight

    def _calculate_completion_weight(
        self, value: Dict[str, Any], base_weight: float
    ) -> float:
        """Calculate weight based on video completion patterns."""
        completion_rate = value.get("completion_rate", 0)
        content_type = value.get("content_type", "medium_form")
        threshold = self.engagement_thresholds.get(content_type, {}).get(
            "completion_rate", 0.7
        )

        if completion_rate > threshold + 0.2:  # Suspiciously high completion
            return base_weight * 1.5
        if completion_rate < threshold - 0.4:  # Very low completion
            return base_weight * 1.3
        return base_weight

    def _calculate_depth_weight(
        self, value: Dict[str, Any], base_weight: float
    ) -> float:
        """Calculate weight based on interaction depth."""
        depth = value.get("interaction_depth", 0)
        duration = value.get("duration_minutes", 1)

        if depth / duration > 5:  # More than 5 interactions per minute
            return base_weight * 1.5
        if depth == 0 and duration > 30:  # No interaction on long videos
            return base_weight * 1.3
        return base_weight

    def _calculate_social_weight(
        self, value: Dict[str, Any], base_weight: float
    ) -> float:
        """Calculate weight based on social signals."""
        likes = value.get("likes_per_view", 0)
        comments = value.get("comments_per_view", 0)
        shares = value.get("shares_per_view", 0)

        if any(
            [
                likes > self.social_patterns["likes_per_view"] * 10,
                comments > self.social_patterns["comments_per_view"] * 10,
                shares > self.social_patterns["shares_per_view"] * 10,
            ]
        ):
            return base_weight * 1.5
        return base_weight

    def _is_holiday(self, date: datetime) -> bool:
        """Check if a date is a holiday (simplified example)."""
        # This would normally check against a holiday calendar
        return False

    def _is_suspicious_category(self, category_info: Dict[str, Any]) -> bool:
        """Determine if a category combination is suspicious."""
        if "transitions" in category_info:
            # Check for rapid transitions between unrelated categories
            transitions = category_info["transitions"]
            if len(transitions) >= 3:
                # Check if all transitions are between different categories
                categories = set(transitions)
                return len(categories) == len(transitions)
        return False

    def _calculate_engagement_confidence(
        self, metrics: Dict[str, float], context: Dict[str, Any] = None
    ) -> float:
        """Calculate enhanced confidence score for engagement pattern detection."""
        # Calculate base confidence from engagement metrics
        duration_cv = (
            metrics["std_duration"] / metrics["mean_duration"]
            if metrics["mean_duration"]
            else 0
        )
        interaction_cv = (
            metrics["std_interactions"] / metrics["mean_interactions"]
            if metrics["mean_interactions"]
            else 0
        )
        base_confidence = 1.0 - min(1.0, (duration_cv + interaction_cv) / 2)

        if not context:
            return float(base_confidence)

        # Apply contextual modifiers
        contextual_confidence = 0.0
        context_count = 0

        for context_type, value in context.items():
            if context_type in self.context_factors:
                weight = self._calculate_contextual_weight(context_type, value)
                contextual_confidence += base_confidence * weight
                context_count += 1

        if context_count > 0:
            final_confidence = (
                base_confidence + contextual_confidence / context_count
            ) / 2
        else:
            final_confidence = base_confidence

        # Apply time decay if timestamp is provided
        if "timestamp" in context:
            final_confidence *= self._apply_time_decay(context["timestamp"])

        return float(min(1.0, final_confidence))

    def _calculate_language_switch_confidence(self, switch_count: int) -> float:
        """Calculate confidence score for language switching detection."""
        return float(min(1.0, switch_count / 5))  # Scale to max of 5 switches

    def _calculate_topic_shift_confidence(
        self, window_similarity: float, current_similarity: float
    ) -> float:
        """Calculate confidence score for topic shift detection."""
        return float(
            min(1.0, (window_similarity - current_similarity) / window_similarity)
        )

    def _calculate_pattern_strength(self, entries: List[Dict[str, Any]]) -> float:
        """Calculate the strength of patterns in a sequence of entries."""
        titles = [entry["title"] for entry in entries]

        # Calculate title similarity
        tfidf_matrix = self.vectorizer.fit_transform(titles)
        similarities = cosine_similarity(tfidf_matrix)

        return float(np.mean(similarities))

    def _detect_content_mood(self, title: str) -> str:
        """Detect the emotional mood of content based on title."""
        title = title.lower()

        for mood, indicators in self.psychological_patterns["content_mood"].items():
            if any(indicator in title for indicator in indicators):
                return mood
        return "neutral"

    def _detect_cognitive_style(self, entry: Dict[str, Any]) -> str:
        """Detect the cognitive engagement style of content."""
        title = entry["title"].lower()

        for style, indicators in self.psychological_patterns["cognitive_style"].items():
            if any(indicator in title for indicator in indicators):
                return style
        return "general"

    def _detect_emotional_triggers(self, entry: Dict[str, Any]) -> List[str]:
        """Detect emotional triggers in content."""
        title = entry["title"].lower()
        triggers = []

        for trigger_type, indicators in self.psychological_patterns[
            "emotional_triggers"
        ].items():
            if any(indicator in title for indicator in indicators):
                triggers.append(trigger_type)
        return triggers

    def _calculate_content_polarization(self, entry: Dict[str, Any]) -> float:
        """Calculate content polarization score."""
        title = entry["title"].lower()
        positive_count = sum(
            1
            for word in self.psychological_patterns["content_mood"]["positive"]
            if word in title
        )
        negative_count = sum(
            1
            for word in self.psychological_patterns["content_mood"]["negative"]
            if word in title
        )

        if positive_count + negative_count == 0:
            return 0.0
        return float(
            abs(positive_count - negative_count) / (positive_count + negative_count)
        )

    def _analyze_trigger_patterns(
        self, triggers: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze patterns in emotional triggers."""
        trigger_counts = Counter()
        trigger_sequences = []

        for trigger_data in triggers:
            trigger_counts.update(trigger_data["triggers"])
            if trigger_sequences:
                time_diff = (
                    datetime.fromisoformat(trigger_data["timestamp"])
                    - datetime.fromisoformat(trigger_sequences[-1]["timestamp"])
                ).total_seconds()
                trigger_sequences.append(
                    {"triggers": trigger_data["triggers"], "interval": time_diff}
                )
            else:
                trigger_sequences.append(
                    {"triggers": trigger_data["triggers"], "interval": 0}
                )

        return {
            "frequency": dict(trigger_counts),
            "patterns": self._identify_trigger_sequences(trigger_sequences),
        }

    def _analyze_bias_trend(self, polarization_scores: List[float]) -> Dict[str, float]:
        """Analyze trend in content bias."""
        if not polarization_scores:
            return {"trend": 0.0, "volatility": 0.0}

        # Calculate trend using linear regression
        x = np.arange(len(polarization_scores))
        y = np.array(polarization_scores)
        trend = np.polyfit(x, y, 1)[0] if len(x) > 1 else 0.0

        return {"trend": float(trend), "volatility": float(np.std(polarization_scores))}

    def _calculate_pattern_stability(self, entries: List[Dict[str, Any]]) -> float:
        """Calculate stability score for behavioral patterns."""
        if len(entries) < 2:
            return 1.0

        pattern_changes = 0
        for i in range(1, len(entries)):
            if self._is_pattern_change(entries[i - 1], entries[i]):
                pattern_changes += 1

        return float(1.0 - min(1.0, pattern_changes / len(entries)))

    def _calculate_attention_stability(self, entries: List[Dict[str, Any]]) -> float:
        """Calculate stability of attention patterns."""
        if len(entries) < 2:
            return 1.0

        durations = [entry.get("duration", 0) for entry in entries]
        completion_rates = [entry.get("completion_rate", 0) for entry in entries]

        duration_stability = (
            1.0 - min(1.0, np.std(durations) / np.mean(durations))
            if np.mean(durations) > 0
            else 0.0
        )
        completion_stability = (
            1.0 - min(1.0, np.std(completion_rates)) if completion_rates else 0.0
        )

        return float((duration_stability + completion_stability) / 2)

    def _calculate_quality_sensitivity(self, quality_prefs: Dict[str, int]) -> float:
        """Calculate sensitivity to content quality."""
        if not quality_prefs:
            return 0.0

        total = sum(quality_prefs.values())
        if total == 0:
            return 0.0

        weights = {"professional": 1.0, "semi_pro": 0.6, "amateur": 0.3}

        weighted_sum = sum(
            count * weights.get(quality, 0.0)
            for quality, count in quality_prefs.items()
        )
        return float(weighted_sum / total)

    def _calculate_style_diversity(self, style_prefs: Dict[str, int]) -> float:
        """Calculate diversity in content style preferences."""
        if not style_prefs:
            return 0.0

        total = sum(style_prefs.values())
        if total == 0:
            return 0.0

        probabilities = [count / total for count in style_prefs.values()]
        entropy = -sum(p * np.log2(p) for p in probabilities if p > 0)
        max_entropy = np.log2(len(style_prefs)) if len(style_prefs) > 0 else 1.0

        return float(entropy / max_entropy) if max_entropy > 0 else 0.0

    def _calculate_behavioral_consistency(
        self, stability_metrics: Dict[str, float]
    ) -> float:
        """Calculate overall behavioral consistency score."""
        weights = {"attention": 0.4, "interaction": 0.3, "navigation": 0.3}

        weighted_sum = sum(
            stability_metrics.get(metric, 0.0) * weight
            for metric, weight in weights.items()
        )
        return float(weighted_sum)

    def _detect_behavioral_anomalies(
        self, metrics: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Detect anomalies in behavioral patterns."""
        anomalies = {
            "psychological": self._detect_psychological_anomalies(
                metrics["psychological"]
            ),
            "preference": self._detect_preference_anomalies(metrics["preferences"]),
            "interaction": self._detect_interaction_anomalies(metrics["interactions"]),
        }

        return {
            "detected_anomalies": anomalies,
            "anomaly_score": self._calculate_anomaly_score(anomalies),
        }

    def _assess_behavioral_risks(
        self, metrics: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Assess risks based on behavioral patterns."""
        risks = {
            "automation_risk": self._calculate_automation_risk(metrics),
            "manipulation_risk": self._calculate_manipulation_risk(metrics),
            "authenticity_risk": self._calculate_authenticity_risk(metrics),
        }

        return {
            "risk_factors": risks,
            "overall_risk_score": self._calculate_overall_risk(risks),
        }

    def _empty_result(self) -> Dict[str, Any]:
        """Return empty result structure when no entries are provided."""
        return {
            "risk_score": 0.0,
            "patterns": {
                "rapid_views": [],
                "content_loops": [],
                "binge_patterns": [],
                "anomalous_sessions": [],
                "suspicious_sequences": [],
                "behavior_chains": [],
                "geographic_anomalies": [],
                "engagement_patterns": [],
                "language_switches": [],
                "topic_shifts": [],
            },
            "entropy_analysis": {"content_entropy": 0.0, "channel_entropy": 0.0},
            "temporal_analysis": {
                "hourly_distribution": [0.0] * 24,
                "weekly_distribution": [0.0] * 7,
                "regularity_score": 0.0,
            },
            "similarity_stats": {"mean": 0.0, "std": 0.0, "max": 0.0},
        }

    # Confidence calculation methods
    def _calculate_confidence(
        self, interval: float, context: Dict[str, Any] = None
    ) -> float:
        """Calculate enhanced confidence score for rapid view detection.

        Args:
            interval: Time interval between views
            context: Additional contextual information for confidence calculation
        """
        # Base confidence from interval
        base_confidence = 1.0 - min(1.0, interval / self.rapid_view_threshold)

        if not context:
            return float(base_confidence)

        # Temporal context adjustment
        temporal_factor = self._calculate_temporal_confidence(context)

        # Pattern context adjustment
        pattern_factor = self._calculate_pattern_confidence(context)

        # Historical context adjustment
        historical_factor = self._calculate_historical_confidence(context)

        # Weight and combine factors
        weighted_confidence = (
            base_confidence * self.pattern_weight
            + temporal_factor * self.temporal_weight
            + ((pattern_factor + historical_factor) / 2) * self.context_weight
        )

        # Apply time decay if timestamp is provided
        if "timestamp" in context:
            weighted_confidence *= self._apply_time_decay(context["timestamp"])

        return float(min(1.0, weighted_confidence))

    def _calculate_loop_confidence(
        self, similar_entries: List[Dict[str, Any]]
    ) -> float:
        """Calculate confidence score for content loop detection."""
        similarities = [entry["similarity"] for entry in similar_entries]
        return float(np.mean(similarities))

    def _calculate_binge_confidence(self, intervals: np.ndarray) -> float:
        """Calculate confidence score for binge pattern detection."""
        if len(intervals) < 2:
            return 0.0
        regularity = 1.0 - min(1.0, np.std(intervals) / np.mean(intervals))
        intensity = 1.0 - min(1.0, np.mean(intervals) / 60)  # Scale to hour
        return float((regularity + intensity) / 2)

    def _calculate_anomaly_confidence(self, metrics: Dict[str, float]) -> float:
        """Calculate confidence score for anomalous session detection."""
        regularity = 1.0 - min(1.0, metrics["std_interval"] / metrics["mean_interval"])
        intensity = min(1.0, metrics["video_count"] / 50)  # Scale to 50 videos
        return float((regularity + intensity) / 2)

    def _calculate_sequence_confidence(self, sequence: List[Dict[str, Any]]) -> float:
        """Calculate confidence score for suspicious sequence detection."""
        titles = [entry["title"] for entry in sequence]
        tfidf_matrix = self.vectorizer.fit_transform(titles)
        similarity_matrix = cosine_similarity(tfidf_matrix)
        return float(np.mean(similarity_matrix))

    def _has_numeric_progression(self, titles: List[str]) -> bool:
        """Check if titles follow a numeric progression pattern."""
        numbers = []
        for title in titles:
            matches = re.findall(r"\d+", title)
            if matches:
                numbers.extend(map(int, matches))
        if len(numbers) >= len(titles):
            diffs = np.diff(numbers[: len(titles)])
            return len(set(diffs)) == 1
        return False

    def _has_similar_structure(self, titles: List[str]) -> bool:
        """Check if titles have similar structural patterns."""
        patterns = [re.sub(r"[\w\d]+", "X", title) for title in titles]
        return len(set(patterns)) == 1

    def _calculate_pattern_duration(self, entries: List[Dict[str, Any]]) -> float:
        """Calculate the duration of a pattern in hours."""
        if not entries:
            return 0.0
        start = datetime.fromisoformat(min(entry["timestamp"] for entry in entries))
        end = datetime.fromisoformat(max(entry["timestamp"] for entry in entries))
        return float((end - start).total_seconds() / 3600)  # Convert to hours

    def _identify_engagement_anomaly(self, metrics: Dict[str, float]) -> str:
        """Identify the type of engagement anomaly based on metrics."""
        duration_cv = (
            metrics["std_duration"] / metrics["mean_duration"]
            if metrics["mean_duration"] > 0
            else 0
        )
        interaction_cv = (
            metrics["std_interactions"] / metrics["mean_interactions"]
            if metrics["mean_interactions"] > 0
            else 0
        )

        if duration_cv < 0.1 and interaction_cv < 0.1:
            return "highly_regular_engagement"
        if duration_cv < 0.2:
            return "regular_duration_pattern"
        if interaction_cv < 0.2:
            return "regular_interaction_pattern"
        if metrics["mean_interactions"] == 0:
            return "no_interaction_pattern"
        return "unknown_anomaly"

    def _init_device_tracking(self, entries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Initialize device tracking for behavioral analysis.

        Args:
            entries: List of viewing history entries

        Returns:
            Dictionary with device tracking information
        """
        device_info = {}
        for entry in entries:
            device_id = entry.get("device_id", "unknown")
            if device_id not in device_info:
                device_info[device_id] = {
                    "first_seen": entry.get("timestamp"),
                    "last_seen": entry.get("timestamp"),
                    "view_count": 0,
                    "channels": set(),
                    "categories": set(),
                }

            device_info[device_id]["view_count"] += 1
            device_info[device_id]["last_seen"] = entry.get("timestamp")
            if "channel" in entry:
                device_info[device_id]["channels"].add(entry["channel"])
            if "category" in entry:
                device_info[device_id]["categories"].add(entry["category"])

        # Convert sets to lists for JSON serialization
        for device_id, device_data in device_info.items():
            device_data["channels"] = list(device_data["channels"])
            device_data["categories"] = list(device_data["categories"])

        return device_info

    def _identify_trigger_sequences(
        self, entries: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Identify sequences that may trigger specific behavioral responses.

        Args:
            entries: List of viewing history entries

        Returns:
            List of identified trigger sequences
        """
        trigger_sequences = []
        trigger_keywords = [
            "viral",
            "trending",
            "breaking",
            "exclusive",
            "shocking",
            "must see",
        ]

        for i in range(len(entries) - 2):
            sequence = entries[i : i + 3]
            titles = [entry.get("title", "").lower() for entry in sequence]

            # Check if sequence contains trigger keywords
            trigger_count = sum(
                1
                for title in titles
                for keyword in trigger_keywords
                if keyword in title
            )

            if trigger_count >= 2:
                # Calculate time intervals
                timestamps = [
                    datetime.fromisoformat(entry["timestamp"]) for entry in sequence
                ]
                intervals = [
                    (timestamps[j + 1] - timestamps[j]).total_seconds()
                    for j in range(len(timestamps) - 1)
                ]

                trigger_sequences.append(
                    {
                        "start_index": i,
                        "sequence": sequence,
                        "trigger_count": trigger_count,
                        "intervals": intervals,
                        "confidence": min(1.0, trigger_count / 3.0),
                    }
                )

        return trigger_sequences

    def _is_pattern_change(
        self, before: List[Dict[str, Any]], after: List[Dict[str, Any]]
    ) -> bool:
        """Determine if there's a significant pattern change between two periods.

        Args:
            before: Entries from the earlier period
            after: Entries from the later period

        Returns:
            True if significant pattern change detected
        """
        if not before or not after:
            return False

        # Compare channel preferences
        before_channels = [entry.get("channel", "") for entry in before]
        after_channels = [entry.get("channel", "") for entry in after]

        before_channel_dist = {}
        after_channel_dist = {}

        for channel in before_channels:
            before_channel_dist[channel] = before_channel_dist.get(channel, 0) + 1
        for channel in after_channels:
            after_channel_dist[channel] = after_channel_dist.get(channel, 0) + 1

        # Normalize distributions
        before_total = len(before_channels)
        after_total = len(after_channels)

        if before_total == 0 or after_total == 0:
            return False

        for channel in before_channel_dist:
            before_channel_dist[channel] /= before_total
        for channel in after_channel_dist:
            after_channel_dist[channel] /= after_total

        # Calculate KL divergence or similar metric
        all_channels = set(before_channel_dist.keys()) | set(after_channel_dist.keys())
        divergence = 0

        for channel in all_channels:
            p = before_channel_dist.get(channel, 0.001)  # Small epsilon to avoid log(0)
            q = after_channel_dist.get(channel, 0.001)
            if p > 0 and q > 0:
                divergence += p * np.log(p / q)

        return divergence > 0.5  # Threshold for significant change

    def _calculate_topic_similarity(
        self, entries1: List[Dict[str, Any]], entries2: List[Dict[str, Any]]
    ) -> float:
        """Calculate similarity between topics in two sets of entries.

        Args:
            entries1: First set of entries
            entries2: Second set of entries

        Returns:
            Similarity score between 0 and 1
        """
        if not entries1 or not entries2:
            return 0.0

        titles1 = [entry.get("title", "") for entry in entries1]
        titles2 = [entry.get("title", "") for entry in entries2]

        all_titles = titles1 + titles2

        if not all_titles or all(not title.strip() for title in all_titles):
            return 0.0

        try:
            tfidf_matrix = self.vectorizer.fit_transform(all_titles)

            # Split matrices
            matrix1 = tfidf_matrix[: len(titles1)]
            matrix2 = tfidf_matrix[len(titles1) :]

            # Calculate average vectors
            avg_vector1 = np.mean(matrix1.toarray(), axis=0)
            avg_vector2 = np.mean(matrix2.toarray(), axis=0)

            # Calculate cosine similarity
            similarity = np.dot(avg_vector1, avg_vector2) / (
                np.linalg.norm(avg_vector1) * np.linalg.norm(avg_vector2)
            )

            return float(similarity) if not np.isnan(similarity) else 0.0
        except (ValueError, ZeroDivisionError):
            return 0.0

    def _identify_navigation_pattern(
        self, entries: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Identify navigation patterns in viewing behavior.

        Args:
            entries: List of viewing history entries

        Returns:
            Dictionary with navigation pattern information
        """
        if not entries:
            return {"pattern_type": "none", "confidence": 0.0}

        # Analyze channel switching patterns
        channels = [entry.get("channel", "") for entry in entries]
        channel_switches = sum(
            1 for i in range(1, len(channels)) if channels[i] != channels[i - 1]
        )

        switch_rate = channel_switches / len(entries) if entries else 0

        # Analyze viewing duration patterns
        durations = [
            entry.get("duration", 0) for entry in entries if "duration" in entry
        ]

        if durations:
            avg_duration = np.mean(durations)
            duration_std = np.std(durations)
            duration_cv = duration_std / avg_duration if avg_duration > 0 else 0
        else:
            duration_cv = 0

        # Determine pattern type
        if switch_rate > 0.7:
            pattern_type = "channel_hopping"
            confidence = min(1.0, switch_rate)
        elif switch_rate < 0.1 and duration_cv < 0.3:
            pattern_type = "focused_viewing"
            confidence = min(1.0, 1.0 - switch_rate)
        elif duration_cv > 0.8:
            pattern_type = "erratic_engagement"
            confidence = min(1.0, duration_cv)
        else:
            pattern_type = "mixed_pattern"
            confidence = 0.5

        return {
            "pattern_type": pattern_type,
            "confidence": confidence,
            "switch_rate": switch_rate,
            "duration_cv": duration_cv,
        }

    def _identify_consumption_pattern(
        self, entries: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Identify content consumption patterns.

        Args:
            entries: List of viewing history entries

        Returns:
            Dictionary with consumption pattern information
        """
        if not entries:
            return {"pattern_type": "none", "confidence": 0.0}

        # Analyze temporal patterns
        timestamps = [datetime.fromisoformat(entry["timestamp"]) for entry in entries]
        hours = [ts.hour for ts in timestamps]

        # Calculate viewing time distribution
        hour_counts = np.bincount(hours, minlength=24)
        peak_hours = np.where(hour_counts == np.max(hour_counts))[0]

        # Analyze session lengths
        session_lengths = []
        current_session = [timestamps[0]]

        for i in range(1, len(timestamps)):
            time_diff = (
                timestamps[i] - timestamps[i - 1]
            ).total_seconds() / 60  # minutes
            if time_diff <= 60:  # Same session if within 1 hour
                current_session.append(timestamps[i])
            else:
                if len(current_session) > 1:
                    session_length = (
                        current_session[-1] - current_session[0]
                    ).total_seconds() / 60
                    session_lengths.append(session_length)
                current_session = [timestamps[i]]

        if len(current_session) > 1:
            session_length = (
                current_session[-1] - current_session[0]
            ).total_seconds() / 60
            session_lengths.append(session_length)

        # Determine pattern type
        if len(session_lengths) == 0:
            pattern_type = "single_views"
            confidence = 0.3
        elif np.mean(session_lengths) > 120:  # 2+ hours
            pattern_type = "binge_consumption"
            confidence = min(1.0, np.mean(session_lengths) / 180)
        elif len(peak_hours) <= 2:
            pattern_type = "scheduled_viewing"
            confidence = 0.8
        else:
            pattern_type = "distributed_consumption"
            confidence = 0.6

        return {
            "pattern_type": pattern_type,
            "confidence": confidence,
            "avg_session_length": np.mean(session_lengths) if session_lengths else 0,
            "peak_hours": peak_hours.tolist(),
            "session_count": len(session_lengths),
        }

    def _analyze_action_sequences(
        self, entries: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Analyze sequences of actions for behavioral patterns.

        Args:
            entries: List of viewing history entries

        Returns:
            List of identified action sequences
        """
        sequences = []
        if len(entries) < 3:
            return sequences

        # Define action types based on viewing patterns
        for i in range(len(entries) - 2):
            sequence = entries[i : i + 3]

            # Calculate intervals between actions
            timestamps = [
                datetime.fromisoformat(entry["timestamp"]) for entry in sequence
            ]
            intervals = [
                (timestamps[j + 1] - timestamps[j]).total_seconds() for j in range(2)
            ]

            # Analyze action types
            channels = [entry.get("channel", "") for entry in sequence]

            # Check for rapid sequential actions
            if all(interval < 30 for interval in intervals):  # Less than 30 seconds
                action_type = "rapid_sequence"
                confidence = 0.9
            elif all(interval < 300 for interval in intervals):  # Less than 5 minutes
                action_type = "quick_sequence"
                confidence = 0.7
            elif len(set(channels)) == 1:  # Same channel
                action_type = "channel_focused"
                confidence = 0.6
            else:
                action_type = "mixed_sequence"
                confidence = 0.4

            sequences.append(
                {
                    "start_index": i,
                    "sequence": sequence,
                    "action_type": action_type,
                    "confidence": confidence,
                    "intervals": intervals,
                    "channels": channels,
                }
            )

        return sequences

    def _get_dominant_pattern(self, patterns: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get the dominant pattern from a list of patterns.

        Args:
            patterns: List of pattern dictionaries

        Returns:
            The dominant pattern or empty dict if no patterns
        """
        if not patterns:
            return {}

        # Sort by confidence and frequency
        pattern_scores = {}
        for pattern in patterns:
            pattern_type = pattern.get(
                "pattern_type", pattern.get("action_type", "unknown")
            )
            confidence = pattern.get("confidence", 0.0)

            if pattern_type not in pattern_scores:
                pattern_scores[pattern_type] = {"count": 0, "total_confidence": 0.0}

            pattern_scores[pattern_type]["count"] += 1
            pattern_scores[pattern_type]["total_confidence"] += confidence

        # Calculate weighted scores
        best_pattern = None
        best_score = 0

        for pattern_type, stats in pattern_scores.items():
            # Weight by both frequency and confidence
            score = stats["count"] * (stats["total_confidence"] / stats["count"])
            if score > best_score:
                best_score = score
                best_pattern = pattern_type

        if best_pattern:
            return {
                "pattern_type": best_pattern,
                "confidence": pattern_scores[best_pattern]["total_confidence"]
                / pattern_scores[best_pattern]["count"],
                "frequency": pattern_scores[best_pattern]["count"],
                "score": best_score,
            }

        return {}

    def _calculate_pattern_consistency(self, patterns: List[Dict[str, Any]]) -> float:
        """Calculate consistency score for a set of patterns.

        Args:
            patterns: List of pattern dictionaries

        Returns:
            Consistency score between 0 and 1
        """
        if not patterns:
            return 0.0

        # Group patterns by type
        pattern_types = []
        for pattern in patterns:
            pattern_type = pattern.get(
                "pattern_type", pattern.get("action_type", "unknown")
            )
            pattern_types.append(pattern_type)

        if not pattern_types:
            return 0.0

        # Calculate consistency as inverse of entropy
        type_counts = {}
        for ptype in pattern_types:
            type_counts[ptype] = type_counts.get(ptype, 0) + 1

        total_patterns = len(pattern_types)
        entropy = 0

        for count in type_counts.values():
            probability = count / total_patterns
            if probability > 0:
                entropy -= probability * np.log2(probability)

        # Normalize entropy (max entropy is log2(n) where n is number of unique types)
        max_entropy = np.log2(len(type_counts)) if len(type_counts) > 1 else 1
        normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0

        # Consistency is inverse of normalized entropy
        consistency = 1.0 - normalized_entropy

        return float(consistency)

    def _identify_peak_hours(self, entries: List[Dict[str, Any]]) -> List[int]:
        """Identify peak viewing hours from entries.

        Args:
            entries: List of viewing history entries

        Returns:
            List of peak hours (0-23)
        """
        if not entries:
            return []

        # Extract hours from timestamps
        hours = []
        for entry in entries:
            try:
                timestamp = datetime.fromisoformat(entry["timestamp"])
                hours.append(timestamp.hour)
            except (ValueError, KeyError):
                continue

        if not hours:
            return []

        # Count views per hour
        hour_counts = np.bincount(hours, minlength=24)

        # Find peak hours (above 75th percentile)
        threshold = np.percentile(hour_counts, 75)
        peak_hours = [
            hour
            for hour, count in enumerate(hour_counts)
            if count >= threshold and count > 0
        ]

        return peak_hours

    def _calculate_temporal_consistency(self, entries: List[Dict[str, Any]]) -> float:
        """Calculate temporal consistency of viewing patterns.

        Args:
            entries: List of viewing history entries

        Returns:
            Consistency score between 0 and 1
        """
        if len(entries) < 2:
            return 0.0

        # Extract timestamps and calculate intervals
        timestamps = []
        for entry in entries:
            try:
                timestamp = datetime.fromisoformat(entry["timestamp"])
                timestamps.append(timestamp)
            except (ValueError, KeyError):
                continue

        if len(timestamps) < 2:
            return 0.0

        # Sort timestamps
        timestamps.sort()

        # Calculate intervals between consecutive views
        intervals = []
        for i in range(1, len(timestamps)):
            interval = (
                timestamps[i] - timestamps[i - 1]
            ).total_seconds() / 3600  # hours
            intervals.append(interval)

        if not intervals:
            return 0.0

        # Calculate coefficient of variation (inverse of consistency)
        mean_interval = np.mean(intervals)
        std_interval = np.std(intervals)

        if mean_interval == 0:
            return 0.0

        cv = std_interval / mean_interval

        # Convert to consistency score (higher CV = lower consistency)
        consistency = 1.0 / (1.0 + cv)

        return float(consistency)

    def _calculate_preference_stability(self, entries: List[Dict[str, Any]]) -> float:
        """Calculate stability of content preferences over time.

        Args:
            entries: List of viewing history entries

        Returns:
            Stability score between 0 and 1
        """
        if len(entries) < 4:
            return 0.0

        # Split entries into early and late periods
        mid_point = len(entries) // 2
        early_entries = entries[:mid_point]
        late_entries = entries[mid_point:]

        # Calculate preference distributions for each period
        early_channels = [entry.get("channel", "") for entry in early_entries]
        late_channels = [entry.get("channel", "") for entry in late_entries]

        # Count channel preferences
        early_prefs = {}
        late_prefs = {}

        for channel in early_channels:
            early_prefs[channel] = early_prefs.get(channel, 0) + 1
        for channel in late_channels:
            late_prefs[channel] = late_prefs.get(channel, 0) + 1

        # Normalize to probabilities
        early_total = len(early_channels)
        late_total = len(late_channels)

        if early_total == 0 or late_total == 0:
            return 0.0

        for channel in early_prefs:
            early_prefs[channel] /= early_total
        for channel in late_prefs:
            late_prefs[channel] /= late_total

        # Calculate similarity between preference distributions
        all_channels = set(early_prefs.keys()) | set(late_prefs.keys())

        if not all_channels:
            return 0.0

        # Use cosine similarity
        early_vector = [early_prefs.get(channel, 0) for channel in all_channels]
        late_vector = [late_prefs.get(channel, 0) for channel in all_channels]

        # Calculate cosine similarity
        dot_product = np.dot(early_vector, late_vector)
        early_norm = np.linalg.norm(early_vector)
        late_norm = np.linalg.norm(late_vector)

        if early_norm == 0 or late_norm == 0:
            return 0.0

        similarity = dot_product / (early_norm * late_norm)

        return float(similarity) if not np.isnan(similarity) else 0.0
