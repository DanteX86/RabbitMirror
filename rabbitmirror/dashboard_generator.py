#!/usr/bin/env python3

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import plotly.express as px
import plotly.graph_objects as go
from jinja2 import Template
from plotly.subplots import make_subplots

from .symbolic_logger import SymbolicLogger


class DashboardGenerator:
    """Generates interactive dashboards for RabbitMirror analysis results."""

    def __init__(
        self,
        template: str = "basic",
        interactive: bool = True,
        theme: str = "light",
        include_plots: bool = True,
    ):
        """
        Initialize the dashboard generator.

        Args:
            template: Dashboard template type ('basic', 'advanced', 'custom')
            interactive: Whether to generate interactive elements
            theme: Color theme ('light', 'dark')
            include_plots: Whether to include plot visualizations
        """
        self.template = template
        self.interactive = interactive
        self.theme = theme
        self.include_plots = include_plots
        self.logger = SymbolicLogger()

        # Set theme colors
        self.colors = self._get_theme_colors()

    def _get_theme_colors(self) -> Dict[str, str]:
        """Get color scheme based on theme."""
        if self.theme == "dark":
            return {
                "background": "#2E2E2E",
                "paper": "#3E3E3E",
                "text": "#FFFFFF",
                "primary": "#3498DB",
                "secondary": "#E74C3C",
                "accent": "#F39C12",
            }
        else:
            return {
                "background": "#FFFFFF",
                "paper": "#F8F9FA",
                "text": "#333333",
                "primary": "#2980B9",
                "secondary": "#C0392B",
                "accent": "#D68910",
            }

    def generate_dashboard(
        self, data: Dict[str, Any], output_path: Path
    ) -> Dict[str, Path]:
        """
        Generate an interactive dashboard and save it to the specified directory.

        Args:
            data: Analysis data to visualize
            output_path: Directory to save dashboard files

        Returns:
            Dictionary mapping file types to their paths
        """
        try:
            # Ensure output directory exists
            output_path.mkdir(parents=True, exist_ok=True)

            generated_files = {}

            # Generate different dashboard components based on data type
            if "entries" in data:
                # Watch history analysis dashboard
                dashboard_file = self._generate_history_dashboard(data, output_path)
                generated_files["history_dashboard"] = dashboard_file

                # Enhanced analytics dashboard
                analytics_file = self._generate_analytics_dashboard(data, output_path)
                generated_files["analytics_dashboard"] = analytics_file

            if "clusters" in data:
                # Cluster analysis dashboard
                cluster_file = self._generate_cluster_dashboard(data, output_path)
                generated_files["cluster_dashboard"] = cluster_file

            if "suppression_results" in data:
                # Suppression analysis dashboard
                suppression_file = self._generate_suppression_dashboard(
                    data, output_path
                )
                generated_files["suppression_dashboard"] = suppression_file

            if "patterns" in data:
                # Pattern analysis dashboard
                pattern_file = self._generate_pattern_dashboard(data, output_path)
                generated_files["pattern_dashboard"] = pattern_file

            # Generate main dashboard index if multiple components
            if len(generated_files) > 1:
                index_file = self._generate_index_dashboard(
                    generated_files, output_path
                )
                generated_files["index"] = index_file

            # Generate CSS and JS files if needed
            if self.interactive:
                css_file = self._generate_css_file(output_path)
                generated_files["styles"] = css_file

            self.logger.log_event(
                "dashboard_generated",
                {
                    "files_count": len(generated_files),
                    "template": self.template,
                    "theme": self.theme,
                },
            )

            return generated_files

        except Exception as e:
            self.logger.log_error("dashboard_generation_error", e)
            raise

    def _generate_history_dashboard(
        self, data: Dict[str, Any], output_path: Path
    ) -> Path:
        """Generate dashboard for watch history analysis."""
        entries = data.get("entries", [])

        if not entries:
            raise ValueError("No entries found in data")

        # Create subplots
        fig = make_subplots(
            rows=3,
            cols=2,
            subplot_titles=(
                "Watch Activity Over Time",
                "Top Watched Videos",
                "Top Categories",
                "Viewing Time Distribution",
                "Video Count by Day",
                "Daily Watch Trends",
            ),
            specs=[
                [{"secondary_y": True}, {"type": "bar"}],
                [{"type": "bar"}, {"type": "bar"}],
                [{"type": "scatter"}, {"type": "scatter"}],
            ],
        )

        # Add time series plot
        timestamps = [entry.get("timestamp", "") for entry in entries]
        daily_counts = self._aggregate_daily_counts(timestamps)

        fig.add_trace(
            go.Scatter(
                x=list(daily_counts.keys()),
                y=list(daily_counts.values()),
                mode="lines+markers",
                name="Daily Watch Count",
            ),
            row=1,
            col=1,
        )

        # Add category distribution
        categories = self._extract_categories(entries)
        fig.add_trace(
            go.Bar(
                x=list(categories.keys()),
                y=list(categories.values()),
                name="Category Distribution",
            ),
            row=1,
            col=2,
        )

        # Add top videos bar chart
        top_videos = self._extract_top_videos(entries)
        fig.add_trace(
            go.Bar(
                x=[video["title"] for video in top_videos],
                y=[video["count"] for video in top_videos],
                name="Top Watched Videos",
            ),
            row=1,
            col=2,
        )

        # Add top categories bar chart
        categories = self._extract_categories(entries)
        fig.add_trace(
            go.Bar(
                x=list(categories.keys()),
                y=list(categories.values()),
                name="Category Distribution",
            ),
            row=2,
            col=1,
        )

        # Add viewing time distribution
        times = self._extract_viewing_times(entries)
        fig.add_trace(
            go.Histogram(x=times, nbinsx=24, name="Viewing Time Distribution"),
            row=2,
            col=2,
        )

        # Add video count by day
        daily_video_counts = self._aggregate_daily_counts(timestamps)
        fig.add_trace(
            go.Bar(
                x=list(daily_video_counts.keys()),
                y=list(daily_video_counts.values()),
                name="Video Count by Day",
            ),
            row=3,
            col=1,
        )

        # Add daily watch trends line chart
        fig.add_trace(
            go.Scatter(
                x=list(daily_counts.keys()),
                y=list(daily_counts.values()),
                mode="lines",
                name="Daily Watch Trends",
            ),
            row=3,
            col=2,
        )

        # Update layout
        fig.update_layout(
            title="Enhanced YouTube Watch History Dashboard",
            template="plotly_dark" if self.theme == "dark" else "plotly_white",
            height=1200,
        )

        # Save dashboard
        dashboard_file = output_path / "history_dashboard.html"
        fig.write_html(str(dashboard_file))

        return dashboard_file

    def _generate_analytics_dashboard(
        self, data: Dict[str, Any], output_path: Path
    ) -> Path:
        """Generate enhanced analytics dashboard with advanced insights."""
        entries = data.get("entries", [])

        if not entries:
            raise ValueError("No entries found in data")

        # Create subplots for advanced analytics
        fig = make_subplots(
            rows=3,
            cols=2,
            subplot_titles=(
                "Top Keywords in Titles",
                "Channel Distribution",
                "Watch Velocity Metrics",
                "Hourly Viewing Pattern",
                "Weekly Activity Pattern",
                "Video Popularity Index",
            ),
            specs=[
                [{"type": "bar"}, {"type": "pie"}],
                [{"type": "indicator"}, {"type": "bar"}],
                [{"type": "bar"}, {"type": "scatter"}],
            ],
        )

        # Top keywords analysis
        keywords = self._analyze_title_keywords(entries)
        fig.add_trace(
            go.Bar(
                x=list(keywords.keys()),
                y=list(keywords.values()),
                name="Top Keywords",
                marker_color="skyblue",
            ),
            row=1,
            col=1,
        )

        # Channel distribution pie chart
        channels = self._extract_channels(entries)
        fig.add_trace(
            go.Pie(
                labels=list(channels.keys()),
                values=list(channels.values()),
                name="Channel Distribution",
            ),
            row=1,
            col=2,
        )

        # Watch velocity metrics
        velocity = self._calculate_watch_velocity(entries)
        fig.add_trace(
            go.Indicator(
                mode="gauge+number+delta",
                value=velocity.get("average_velocity", 0),
                title={"text": "Avg Videos/Day"},
                gauge={
                    "axis": {"range": [None, 10]},
                    "bar": {"color": "darkblue"},
                    "steps": [
                        {"range": [0, 2], "color": "lightgray"},
                        {"range": [2, 5], "color": "gray"},
                    ],
                    "threshold": {
                        "line": {"color": "red", "width": 4},
                        "thickness": 0.75,
                        "value": velocity.get("peak_day_count", 0),
                    },
                },
            ),
            row=2,
            col=1,
        )

        # Hourly viewing pattern
        viewing_times = self._extract_viewing_times(entries)
        hour_counts = {}
        for hour in viewing_times:
            hour_counts[hour] = hour_counts.get(hour, 0) + 1

        fig.add_trace(
            go.Bar(
                x=list(hour_counts.keys()),
                y=list(hour_counts.values()),
                name="Hourly Pattern",
                marker_color="orange",
            ),
            row=2,
            col=2,
        )

        # Weekly activity pattern
        timestamps = [entry.get("timestamp", "") for entry in entries]
        weekly_pattern = self._analyze_weekly_pattern(timestamps)

        fig.add_trace(
            go.Bar(
                x=list(weekly_pattern.keys()),
                y=list(weekly_pattern.values()),
                name="Weekly Activity",
                marker_color="green",
            ),
            row=3,
            col=1,
        )

        # Video popularity index (mock data for demonstration)
        popularity_data = self._calculate_popularity_index(entries)
        fig.add_trace(
            go.Scatter(
                x=list(range(len(popularity_data))),
                y=popularity_data,
                mode="markers+lines",
                name="Popularity Index",
                marker=dict(size=8, color="red"),
            ),
            row=3,
            col=2,
        )

        # Update layout
        fig.update_layout(
            title="Advanced YouTube Analytics Dashboard",
            template="plotly_dark" if self.theme == "dark" else "plotly_white",
            height=1200,
        )

        # Save dashboard
        analytics_file = output_path / "analytics_dashboard.html"
        fig.write_html(str(analytics_file))

        return analytics_file

    def _generate_cluster_dashboard(
        self, data: Dict[str, Any], output_path: Path
    ) -> Path:
        """Generate dashboard for cluster analysis."""
        clusters = data.get("clusters", {})

        # Create cluster visualization
        fig = go.Figure()

        # Add cluster scatter plot if we have cluster data
        if "cluster_labels" in clusters and "features" in clusters:
            features = clusters["features"]
            if features and len(features) > 0:
                # Extract x and y coordinates from features
                x_coords = [point[0] if len(point) > 0 else 0 for point in features]
                y_coords = [point[1] if len(point) > 1 else 0 for point in features]

                fig.add_trace(
                    go.Scatter(
                        x=x_coords,
                        y=y_coords,
                        mode="markers",
                        marker=dict(
                            color=clusters["cluster_labels"], colorscale="viridis"
                        ),
                        name="Video Clusters",
                    )
                )

        fig.update_layout(
            title="Video Clustering Analysis",
            template="plotly_dark" if self.theme == "dark" else "plotly_white",
        )

        dashboard_file = output_path / "cluster_dashboard.html"
        fig.write_html(str(dashboard_file))

        return dashboard_file

    def _generate_suppression_dashboard(
        self, data: Dict[str, Any], output_path: Path
    ) -> Path:
        """Generate dashboard for suppression analysis."""
        suppression_data = data.get("suppression_results", {})

        fig = go.Figure()

        # Add suppression metrics visualization
        if "suppression_scores" in suppression_data:
            scores = suppression_data["suppression_scores"]
            fig.add_trace(
                go.Bar(x=list(range(len(scores))), y=scores, name="Suppression Scores")
            )

        fig.update_layout(
            title="Content Suppression Analysis",
            template="plotly_dark" if self.theme == "dark" else "plotly_white",
        )

        dashboard_file = output_path / "suppression_dashboard.html"
        fig.write_html(str(dashboard_file))

        return dashboard_file

    def _generate_pattern_dashboard(
        self, data: Dict[str, Any], output_path: Path
    ) -> Path:
        """Generate dashboard for pattern analysis."""
        patterns = data.get("patterns", {})

        fig = go.Figure()

        # Add pattern visualization
        if "pattern_scores" in patterns:
            scores = patterns["pattern_scores"]
            fig.add_trace(
                go.Scatter(y=scores, mode="lines+markers", name="Pattern Scores")
            )

        fig.update_layout(
            title="Adversarial Pattern Analysis",
            template="plotly_dark" if self.theme == "dark" else "plotly_white",
        )

        dashboard_file = output_path / "pattern_dashboard.html"
        fig.write_html(str(dashboard_file))

        return dashboard_file

    def _generate_index_dashboard(
        self, generated_files: Dict[str, Path], output_path: Path
    ) -> Path:
        """Generate main index dashboard linking all components."""
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>RabbitMirror Dashboard</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    background-color: {{ colors.background }};
                    color: {{ colors.text }};
                    margin: 0;
                    padding: 20px;
                }
                .dashboard-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: 20px;
                    margin-top: 20px;
                }
                .dashboard-card {
                    background-color: {{ colors.paper }};
                    border-radius: 8px;
                    padding: 20px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                .dashboard-card h3 {
                    color: {{ colors.primary }};
                    margin-top: 0;
                }
                .dashboard-link {
                    display: inline-block;
                    background-color: {{ colors.primary }};
                    color: white;
                    padding: 10px 20px;
                    text-decoration: none;
                    border-radius: 4px;
                    margin-top: 10px;
                }
                .dashboard-link:hover {
                    background-color: {{ colors.secondary }};
                }
            </style>
        </head>
        <body>
            <h1>RabbitMirror Analysis Dashboard</h1>
            <p>Generated on {{ timestamp }}</p>

            <div class="dashboard-grid">
                {% for name, path in dashboards.items() %}
                <div class="dashboard-card">
                    <h3>{{ name.replace('_', ' ').title() }}</h3>
                    <p>Interactive analysis dashboard</p>
                    <a href="{{ path.name }}" class="dashboard-link">View Dashboard</a>
                </div>
                {% endfor %}
            </div>
        </body>
        </html>
        """

        template = Template(html_template)
        html_content = template.render(
            colors=self.colors,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            dashboards=generated_files,
        )

        index_file = output_path / "index.html"
        with open(index_file, "w", encoding="utf-8") as f:
            f.write(html_content)

        return index_file

    def _generate_css_file(self, output_path: Path) -> Path:
        """Generate CSS file for dashboard styling."""
        css_content = f"""
        :root {{
            --bg-color: {self.colors['background']};
            --paper-color: {self.colors['paper']};
            --text-color: {self.colors['text']};
            --primary-color: {self.colors['primary']};
            --secondary-color: {self.colors['secondary']};
            --accent-color: {self.colors['accent']};
        }}

        body {{
            background-color: var(--bg-color);
            color: var(--text-color);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }}

        .dashboard-container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        """

        css_file = output_path / "dashboard.css"
        with open(css_file, "w", encoding="utf-8") as f:
            f.write(css_content)

        return css_file

    def _aggregate_daily_counts(self, timestamps: List[str]) -> Dict[str, int]:
        """Aggregate watch counts by day."""
        daily_counts = {}
        for timestamp in timestamps:
            if timestamp:
                try:
                    # Extract date from timestamp
                    date = (
                        timestamp.split("T")[0]
                        if "T" in timestamp
                        else timestamp.split(" ")[0]
                    )
                    daily_counts[date] = daily_counts.get(date, 0) + 1
                except (IndexError, ValueError):
                    continue
        return daily_counts

    def _extract_top_videos(
        self, entries: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Extract and count videos from entries for top-watched analysis."""
        video_counts = {}
        for entry in entries:
            title = entry.get("title", "Unknown")
            video_counts[title] = video_counts.get(title, 0) + 1

        # Sort and return top 5 videos
        top_videos = sorted(
            video_counts.items(), key=lambda item: item[1], reverse=True
        )
        return [{"title": title, "count": count} for title, count in top_videos[:5]]

    def _extract_categories(self, entries: List[Dict[str, Any]]) -> Dict[str, int]:
        """Extract and count categories from entries."""
        categories = {}
        for entry in entries:
            category = entry.get("category", "General")
            categories[category] = categories.get(category, 0) + 1
        return categories

    def _extract_viewing_times(self, entries: List[Dict[str, Any]]) -> List[int]:
        """Extract viewing times (hours) from timestamps."""
        viewing_times = []
        for entry in entries:
            timestamp = entry.get("timestamp")
            if timestamp:
                try:
                    # Assumes timestamp is in "YYYY-MM-DDTHH:MM:SS"
                    hour = int(timestamp.split("T")[1].split(":")[0])
                    viewing_times.append(hour)
                except (IndexError, ValueError):
                    continue
        return viewing_times

    def _extract_channels(self, entries: List[Dict[str, Any]]) -> Dict[str, int]:
        """Extract and count channels from entries."""
        channels = {}
        for entry in entries:
            url = entry.get("url", "")
            # Extract channel from URL or use title as proxy
            if "youtube.com" in url:
                # For real implementation, you'd extract channel from URL
                channel = f"Channel_{len(url) % 5}"  # Mock channel extraction
            else:
                channel = "Unknown"
            channels[channel] = channels.get(channel, 0) + 1
        return channels

    def _analyze_title_keywords(self, entries: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze keywords in video titles."""
        keywords = {}
        common_words = {
            "a",
            "an",
            "and",
            "the",
            "to",
            "for",
            "with",
            "in",
            "on",
            "at",
            "by",
            "of",
            "or",
        }

        for entry in entries:
            title = entry.get("title", "").lower()
            words = title.split()
            for word in words:
                # Remove punctuation and filter common words
                clean_word = "".join(c for c in word if c.isalnum())
                if len(clean_word) > 2 and clean_word not in common_words:
                    keywords[clean_word] = keywords.get(clean_word, 0) + 1

        # Return top 10 keywords
        top_keywords = sorted(keywords.items(), key=lambda x: x[1], reverse=True)[:10]
        return dict(top_keywords)

    def _calculate_watch_velocity(
        self, entries: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """Calculate watching velocity over time periods."""
        velocity_data = {}
        timestamps = [
            entry.get("timestamp") for entry in entries if entry.get("timestamp")
        ]

        if len(timestamps) < 2:
            return {"average_velocity": 0.0}

        # Sort timestamps
        timestamps.sort()

        # Calculate videos per day
        daily_counts = self._aggregate_daily_counts(timestamps)
        total_days = len(daily_counts)
        total_videos = sum(daily_counts.values())

        velocity_data["average_velocity"] = (
            total_videos / total_days if total_days > 0 else 0
        )
        velocity_data["peak_day_count"] = (
            max(daily_counts.values()) if daily_counts else 0
        )
        velocity_data["total_days_active"] = total_days

        return velocity_data

    def _analyze_weekly_pattern(self, timestamps: List[str]) -> Dict[str, int]:
        """Analyze weekly viewing patterns."""
        from datetime import datetime

        weekly_counts = {
            "Monday": 0,
            "Tuesday": 0,
            "Wednesday": 0,
            "Thursday": 0,
            "Friday": 0,
            "Saturday": 0,
            "Sunday": 0,
        }

        for timestamp in timestamps:
            if timestamp:
                try:
                    # Parse timestamp and get day of week
                    dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                    day_name = dt.strftime("%A")
                    weekly_counts[day_name] += 1
                except (ValueError, AttributeError):
                    continue

        return weekly_counts

    def _calculate_popularity_index(self, entries: List[Dict[str, Any]]) -> List[float]:
        """Calculate a popularity index for videos (mock implementation)."""
        # This is a mock implementation. In practice, you might use
        # video engagement metrics, view counts, etc.
        popularity_scores = []

        for i, entry in enumerate(entries):
            # Mock calculation based on title length and position
            title_length = len(entry.get("title", ""))
            position_score = (len(entries) - i) / len(
                entries
            )  # Newer videos get higher scores

            # Combine factors for a popularity score
            score = (title_length * 0.1 + position_score * 0.9) * 100
            popularity_scores.append(score)

        return popularity_scores
