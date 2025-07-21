"""
Terminal User Interface for RabbitMirror
Modern, interactive TUI using Textual framework
"""

import asyncio
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, ScrollableContainer, Vertical
from textual.screen import ModalScreen
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Input,
    Label,
    Log,
    Markdown,
    ProgressBar,
    Static,
    TabbedContent,
    TabPane,
    Tree,
)

# Import RabbitMirror components
try:
    from .adversarial_profiler import AdversarialProfiler
    from .cluster_engine import ClusterEngine
    from .config_manager import ConfigManager
    from .dashboard_generator import DashboardGenerator
    from .parser import HistoryParser
    from .profile_simulator import ProfileSimulator
    from .suppression_index import SuppressionIndex
    from .symbolic_logger import SymbolicLogger
    from .trend_analyzer import TrendAnalyzer
except ImportError:
    # Fallback for development
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from rabbitmirror.adversarial_profiler import AdversarialProfiler
    from rabbitmirror.cluster_engine import ClusterEngine
    from rabbitmirror.config_manager import ConfigManager
    from rabbitmirror.dashboard_generator import DashboardGenerator
    from rabbitmirror.parser import HistoryParser
    from rabbitmirror.profile_simulator import ProfileSimulator
    from rabbitmirror.suppression_index import SuppressionIndex
    from rabbitmirror.symbolic_logger import SymbolicLogger
    from rabbitmirror.trend_analyzer import TrendAnalyzer


class FileSelector(ModalScreen):
    """Modal screen for selecting files with proper file browser"""

    def __init__(self, title: str = "Select File", filter_ext: str = ".html"):
        super().__init__()
        self.title = title
        self.filter_ext = filter_ext
        self.selected_file = None
        self.current_dir = Path.home()  # Start in home directory
        self.show_browser = False

    def compose(self) -> ComposeResult:
        with Container(id="file-selector"):
            yield Static(f"📁 {self.title}", id="file-title")
            yield Input(placeholder="Enter file path or browse...", id="file-input")
            yield Static(f"Current Directory: {self.current_dir}", id="current-dir")

            # File browser tree (initially hidden)
            yield ScrollableContainer(
                Tree("Files", id="file-tree"), id="file-browser", classes="hidden"
            )

            with Horizontal():
                yield Button("Browse", id="browse-btn", variant="primary")
                yield Button("Select", id="select-btn", variant="success")
                yield Button("Cancel", id="cancel-btn", variant="error")

    def on_mount(self) -> None:
        """Initialize the file browser"""
        self.populate_file_tree()

    def populate_file_tree(self) -> None:
        """Populate the file tree with directories and files"""
        tree = self.query_one("#file-tree", Tree)
        tree.clear()

        # Add root node
        root = tree.root
        root.set_label(f"📁 {self.current_dir.name}")

        try:
            # Add parent directory option if not at root
            if self.current_dir != self.current_dir.parent:
                parent_node = root.add("📁 .. (Parent Directory)")
                parent_node.data = self.current_dir.parent
                parent_node.allow_expand = False

            # Add directories first
            dirs = [
                d
                for d in self.current_dir.iterdir()
                if d.is_dir() and not d.name.startswith(".")
            ]
            dirs.sort(key=lambda x: x.name.lower())

            for directory in dirs:
                try:
                    dir_node = root.add(f"📁 {directory.name}")
                    dir_node.data = directory
                    dir_node.allow_expand = False
                except PermissionError:
                    continue

            # Add files matching the filter
            files = [
                f
                for f in self.current_dir.iterdir()
                if f.is_file() and f.suffix.lower() == self.filter_ext.lower()
            ]
            files.sort(key=lambda x: x.name.lower())

            for file in files:
                file_node = root.add(f"📄 {file.name}")
                file_node.data = file
                file_node.allow_expand = False

            # Also add all files for reference
            other_files = [
                f
                for f in self.current_dir.iterdir()
                if f.is_file() and f.suffix.lower() != self.filter_ext.lower()
            ]
            other_files.sort(key=lambda x: x.name.lower())

            for file in other_files[:10]:  # Show first 10 other files
                file_node = root.add(f"📄 {file.name} (not {self.filter_ext})")
                file_node.data = file
                file_node.allow_expand = False

        except PermissionError:
            error_node = root.add("❌ Permission denied")
            error_node.allow_expand = False

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "browse-btn":
            self.toggle_browser()
        elif event.button.id == "select-btn":
            self.select_file()
        elif event.button.id == "cancel-btn":
            self.dismiss(None)

    def toggle_browser(self) -> None:
        """Toggle the file browser visibility"""
        browser = self.query_one("#file-browser")
        if self.show_browser:
            browser.add_class("hidden")
            self.show_browser = False
            self.query_one("#browse-btn", Button).label = "Browse"
        else:
            browser.remove_class("hidden")
            self.show_browser = True
            self.query_one("#browse-btn", Button).label = "Hide Browser"

    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        """Handle tree node selection"""
        if event.node.data is None:
            return

        selected_path = event.node.data

        if selected_path.is_dir():
            # Navigate to directory
            self.current_dir = selected_path
            self.query_one("#current-dir", Static).update(
                f"Current Directory: {self.current_dir}"
            )
            self.populate_file_tree()
        else:
            # Select file
            if selected_path.suffix.lower() == self.filter_ext.lower():
                self.query_one("#file-input", Input).value = str(selected_path)
                self.selected_file = selected_path
                self.notify(f"Selected: {selected_path.name}", severity="information")
            else:
                self.notify(
                    f"Please select a {self.filter_ext} file", severity="warning"
                )

    def select_file(self) -> None:
        """Select the file from input"""
        file_input = self.query_one("#file-input", Input)
        file_path = file_input.value.strip()

        if file_path and Path(file_path).exists():
            selected_path = Path(file_path)
            if selected_path.suffix.lower() == self.filter_ext.lower():
                self.dismiss(file_path)
            else:
                self.notify(
                    f"Please select a {self.filter_ext} file", severity="warning"
                )
        else:
            self.notify("File not found!", severity="error")


class ResultsViewer(ModalScreen):
    """Modal screen for viewing analysis results"""

    def __init__(self, title: str, data: Dict[str, Any]):
        super().__init__()
        self.title = title
        self.data = data

    def compose(self) -> ComposeResult:
        with Container(id="results-viewer"):
            yield Static(f"📊 {self.title}", id="results-title")
            yield ScrollableContainer(
                Markdown(self.format_results()), id="results-content"
            )
            yield Button("Close", id="close-btn", variant="primary")

    def format_results(self) -> str:
        """Format results data as markdown"""
        markdown_content = f"# {self.title}\n\n"

        if isinstance(self.data, dict):
            for key, value in self.data.items():
                markdown_content += f"## {key.replace('_', ' ').title()}\n\n"

                if isinstance(value, (list, tuple)):
                    for item in value[:5]:  # Show first 5 items
                        markdown_content += f"- {item}\n"
                    if len(value) > 5:
                        markdown_content += f"... and {len(value) - 5} more items\n\n"
                elif isinstance(value, dict):
                    for k, v in value.items():
                        markdown_content += f"- **{k}**: {v}\n"
                    markdown_content += "\n"
                else:
                    markdown_content += f"{value}\n\n"
        else:
            markdown_content += f"```\n{self.data}\n```\n"

        return markdown_content

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "close-btn":
            self.dismiss()


class RabbitMirrorTUI(App):
    """Main Terminal User Interface for RabbitMirror"""

    CSS_PATH = "/Users/romulusaugustus/Documents/RabbitMirror/rabbitmirror/tui.css"
    TITLE = "🐰 RabbitMirror - YouTube Watch History Analyzer"
    SUB_TITLE = "Interactive Terminal Interface"

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("h", "help", "Help"),
        Binding("r", "refresh", "Refresh"),
        Binding("ctrl+c", "quit", "Quit"),
    ]

    def __init__(self):
        super().__init__()
        self.config = ConfigManager()
        self.logger = SymbolicLogger()
        self.current_data = None
        self.current_file = None
        self.analysis_results = {}
        self.operation_start_time = None
        self.timer_task = None

    def compose(self) -> ComposeResult:
        """Create the main layout"""
        yield Header()

        with TabbedContent(initial="main"):
            # Main tab
            with TabPane("Main", id="main"):
                with Vertical():
                    yield Static("🎯 Welcome to RabbitMirror TUI", id="welcome")
                    yield Static(
                        "RabbitMirror analyzes your YouTube watch history to detect algorithmic patterns,\n"
                        "content suppression, and viewing trends. Get started by selecting your watch history file.",
                        id="intro-text",
                    )

                    yield Static(
                        "📋 Step 1: Select Your YouTube Watch History File", id="step1"
                    )
                    yield Static(
                        "Download your YouTube data from Google Takeout (watch-history.html)",
                        id="file-help",
                    )
                    with Horizontal(id="file-section"):
                        yield Button(
                            "📁 Select File", id="select-file", variant="primary"
                        )
                        yield Static("No file selected", id="file-status")

                    yield Static("📋 Step 2: Parse and Analyze Your Data", id="step2")
                    yield Static(
                        "Quick Parse: Load your watch history data\n"
                        "Quick Analysis: Run pattern detection and clustering\n"
                        "View Results: See analysis results and statistics",
                        id="analysis-help",
                    )
                    with Horizontal(id="quick-actions"):
                        yield Button(
                            "🔍 Quick Parse", id="quick-parse", variant="success"
                        )
                        yield Button(
                            "📊 Quick Analysis", id="quick-analysis", variant="success"
                        )
                        yield Button(
                            "📈 View Results", id="view-results", variant="default"
                        )

                    yield Static("⏱️ Operation Status", id="status-header")
                    yield Static("Ready to process data", id="operation-status")
                    yield ProgressBar(id="main-progress", show_eta=False)
                    yield Static("Elapsed: 0:00:00", id="elapsed-time")

                    yield Static(
                        "💡 Tip: Use Tab key to navigate between sections, Q to quit",
                        id="tips",
                    )

            # Analysis tab
            with TabPane("Analysis", id="analysis"):
                with Vertical():
                    yield Static("🔬 Advanced Analysis Tools", id="analysis-title")
                    yield Static(
                        "These tools help you understand YouTube's algorithmic influence on your viewing patterns.",
                        id="analysis-desc",
                    )

                    yield Static("🔍 Pattern Detection", id="pattern-header")
                    yield Static(
                        "Detect Patterns: Identifies algorithmic manipulation patterns in your recommendations",
                        id="pattern-desc",
                    )
                    with Horizontal():
                        yield Button("🎯 Detect Patterns", id="detect-patterns")
                        yield Button("🔄 Cluster Videos", id="cluster-videos")

                    yield Static("📉 Content Analysis", id="content-header")
                    yield Static(
                        "Analyze Suppression: Detects if certain content types are being suppressed\n"
                        "Trend Analysis: Shows how your viewing patterns change over time",
                        id="content-desc",
                    )
                    with Horizontal():
                        yield Button("📉 Analyze Suppression", id="analyze-suppression")
                        yield Button("📊 Trend Analysis", id="trend-analysis")

                    yield Static("📋 Advanced Tools", id="advanced-header")
                    yield Static(
                        "Simulate Profile: Creates synthetic viewing profiles for comparison\n"
                        "Generate Report: Creates comprehensive HTML report with all findings",
                        id="advanced-desc",
                    )
                    with Horizontal():
                        yield Button("🎮 Simulate Profile", id="simulate-profile")
                        yield Button("📋 Generate Report", id="generate-report")

                    yield Static("⚙️ Analysis Options", id="options-title")
                    yield Static(
                        "Threshold: Sensitivity for pattern detection (0.1-1.0)\n"
                        "Format: Output format for exported data",
                        id="options-desc",
                    )
                    with Horizontal():
                        yield Label("Threshold:")
                        yield Input(placeholder="0.7", id="threshold-input")
                        yield Label("Format:")
                        yield Input(placeholder="json", id="format-input")

            # Results tab
            with TabPane("Results", id="results"):
                with Vertical():
                    yield Static("📊 Analysis Results", id="results-title")
                    yield Static(
                        "This tab displays the results of your analysis in a table format.\n"
                        "Run analysis from the Main tab or Analysis tab to see results here.",
                        id="results-desc",
                    )
                    yield DataTable(id="results-table")
                    yield Static("📜 Activity Log", id="log-title")
                    yield Log(id="results-log")

            # Settings tab
            with TabPane("Settings", id="settings"):
                with Vertical():
                    yield Static("⚙️ Configuration", id="settings-title")
                    yield Static(
                        "Configure default values and preferences for RabbitMirror analysis.",
                        id="settings-desc",
                    )

                    yield Static("📁 Output Settings", id="output-header")
                    yield Static(
                        "Set where analysis results and reports will be saved by default.",
                        id="output-desc",
                    )
                    with Horizontal():
                        yield Label("Default Output Directory:")
                        yield Input(placeholder="/path/to/output", id="output-dir")

                    yield Static("📄 Export Settings", id="export-header")
                    yield Static(
                        "Choose the default format for exporting analysis data (json, csv, yaml, excel).",
                        id="export-desc",
                    )
                    with Horizontal():
                        yield Label("Default Format:")
                        yield Input(placeholder="json", id="default-format")

                    yield Static("🎯 Analysis Settings", id="analysis-settings-header")
                    yield Static(
                        "Set the default sensitivity threshold for pattern detection (0.1 = sensitive, 1.0 = strict).",
                        id="analysis-settings-desc",
                    )
                    with Horizontal():
                        yield Label("Analysis Threshold:")
                        yield Input(placeholder="0.7", id="default-threshold")

                    yield Button(
                        "💾 Save Settings", id="save-settings", variant="success"
                    )

        yield Footer()

    def on_mount(self) -> None:
        """Initialize the application"""
        self.notify("🐰 RabbitMirror TUI started!", severity="information")
        self.load_settings()

    def load_settings(self) -> None:
        """Load saved settings"""
        try:
            # Load configuration
            settings = self.config.list()

            # Update UI with saved settings
            if "output_dir" in settings:
                self.query_one("#output-dir", Input).value = str(settings["output_dir"])
            if "default_format" in settings:
                self.query_one("#default-format", Input).value = str(
                    settings["default_format"]
                )
            if "default_threshold" in settings:
                self.query_one("#default-threshold", Input).value = str(
                    settings["default_threshold"]
                )

        except Exception as e:
            self.logger.log_error("SettingsError", e)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        button_id = event.button.id

        if button_id == "select-file":
            self.select_file()
        elif button_id == "quick-parse":
            self.quick_parse()
        elif button_id == "quick-analysis":
            self.quick_analysis()
        elif button_id == "view-results":
            self.view_results()
        elif button_id == "detect-patterns":
            self.detect_patterns()
        elif button_id == "cluster-videos":
            self.cluster_videos()
        elif button_id == "analyze-suppression":
            self.analyze_suppression()
        elif button_id == "simulate-profile":
            self.simulate_profile()
        elif button_id == "trend-analysis":
            self.trend_analysis()
        elif button_id == "generate-report":
            self.generate_report()
        elif button_id == "save-settings":
            self.save_settings()

    def select_file(self) -> None:
        """Open file selector"""

        def handle_file_selection(file_path: Optional[str]) -> None:
            if file_path:
                self.current_file = file_path
                self.query_one("#file-status", Static).update(
                    f"📄 {Path(file_path).name}"
                )
                self.notify(f"Selected: {Path(file_path).name}", severity="information")

        self.push_screen(
            FileSelector("Select YouTube Watch History File", ".html"),
            handle_file_selection,
        )

    def quick_parse(self) -> None:
        """Quick parse of selected file"""
        if not self.current_file:
            self.notify("Please select a file first!", severity="error")
            return

        try:
            self.start_operation("File Parsing")
            self.notify("🔄 Parsing file...", severity="information")

            # Simulate progress updates
            self.update_operation_progress(20, "Reading file...")

            # Parse the file
            parser = HistoryParser(self.current_file)
            self.update_operation_progress(60, "Processing entries...")
            self.current_data = parser.parse()

            self.update_operation_progress(90, "Finalizing...")

            # Update results table
            self.update_results_table(
                {
                    "total_entries": len(self.current_data),
                    "file_parsed": Path(self.current_file).name,
                    "parse_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }
            )

            self.complete_operation(True, f"✅ Parsed {len(self.current_data)} entries")
            self.notify(
                f"✅ Parsed {len(self.current_data)} entries", severity="success"
            )

        except Exception as e:
            self.complete_operation(False, f"❌ Parse failed: {str(e)}")
            self.notify(f"❌ Parse failed: {str(e)}", severity="error")
            self.logger.log_error("ParseError", e)

    def quick_analysis(self) -> None:
        """Quick analysis of current data"""
        if not self.current_data:
            self.notify("Please parse a file first!", severity="error")
            return

        try:
            self.notify("🔄 Running quick analysis...", severity="information")

            # Quick pattern detection
            profiler = AdversarialProfiler()
            patterns = profiler.identify_patterns(self.current_data)

            # Quick clustering
            cluster_engine = ClusterEngine()
            clusters = cluster_engine.cluster_videos(self.current_data)

            # Store results
            self.analysis_results = {
                "patterns": patterns,
                "clusters": clusters,
                "analysis_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

            # Update results table
            self.update_results_table(
                {
                    "patterns_found": len(patterns.get("patterns", [])),
                    "clusters_found": len(clusters.get("clusters", [])),
                    "analysis_complete": "✅ Yes",
                }
            )

            self.notify("✅ Quick analysis complete!", severity="success")

        except Exception as e:
            self.notify(f"❌ Analysis failed: {str(e)}", severity="error")
            self.logger.log_error("AnalysisError", e)

    def view_results(self) -> None:
        """View analysis results"""
        if not self.analysis_results:
            self.notify("No results to view. Run analysis first!", severity="warning")
            return

        self.push_screen(ResultsViewer("Analysis Results", self.analysis_results))

    def detect_patterns(self) -> None:
        """Detect adversarial patterns"""
        if not self.current_data:
            self.notify("Please parse a file first!", severity="error")
            return

        try:
            self.notify("🔍 Detecting patterns...", severity="information")

            # Get threshold from input
            threshold_input = self.query_one("#threshold-input", Input)
            threshold = float(threshold_input.value) if threshold_input.value else 0.7

            # Run pattern detection
            profiler = AdversarialProfiler(threshold=threshold)
            patterns = profiler.identify_patterns(self.current_data)

            # Store and display results
            self.analysis_results["patterns"] = patterns
            self.push_screen(ResultsViewer("Pattern Detection Results", patterns))

            self.notify("✅ Pattern detection complete!", severity="success")

        except Exception as e:
            self.notify(f"❌ Pattern detection failed: {str(e)}", severity="error")
            self.logger.log_error("PatternDetectionError", e)

    def cluster_videos(self) -> None:
        """Cluster videos"""
        if not self.current_data:
            self.notify("Please parse a file first!", severity="error")
            return

        try:
            self.notify("🔄 Clustering videos...", severity="information")

            # Run clustering
            cluster_engine = ClusterEngine()
            clusters = cluster_engine.cluster_videos(self.current_data)

            # Store and display results
            self.analysis_results["clusters"] = clusters
            self.push_screen(ResultsViewer("Clustering Results", clusters))

            self.notify("✅ Clustering complete!", severity="success")

        except Exception as e:
            self.notify(f"❌ Clustering failed: {str(e)}", severity="error")
            self.logger.log_error("ClusteringError", e)

    def analyze_suppression(self) -> None:
        """Analyze content suppression"""
        if not self.current_data:
            self.notify("Please parse a file first!", severity="error")
            return

        try:
            self.notify("📉 Analyzing suppression...", severity="information")

            # Run suppression analysis
            suppression_index = SuppressionIndex()
            suppression = suppression_index.calculate_suppression(self.current_data)

            # Store and display results
            self.analysis_results["suppression"] = suppression
            self.push_screen(ResultsViewer("Suppression Analysis Results", suppression))

            self.notify("✅ Suppression analysis complete!", severity="success")

        except Exception as e:
            self.notify(f"❌ Suppression analysis failed: {str(e)}", severity="error")
            self.logger.log_error("SuppressionAnalysisError", e)

    def simulate_profile(self) -> None:
        """Simulate viewing profile"""
        if not self.current_data:
            self.notify("Please parse a file first!", severity="error")
            return

        try:
            self.notify("🎮 Simulating profile...", severity="information")

            # Run profile simulation
            simulator = ProfileSimulator()
            simulation = simulator.simulate_profile(self.current_data)

            # Store and display results
            self.analysis_results["simulation"] = simulation
            self.push_screen(ResultsViewer("Profile Simulation Results", simulation))

            self.notify("✅ Profile simulation complete!", severity="success")

        except Exception as e:
            self.notify(f"❌ Profile simulation failed: {str(e)}", severity="error")
            self.logger.log_error("ProfileSimulationError", e)

    def trend_analysis(self) -> None:
        """Analyze trends"""
        if not self.current_data:
            self.notify("Please parse a file first!", severity="error")
            return

        try:
            self.notify("📊 Analyzing trends...", severity="information")

            # Run trend analysis
            trend_analyzer = TrendAnalyzer()
            trends = trend_analyzer.analyze_trends(self.current_data)

            # Store and display results
            self.analysis_results["trends"] = trends
            self.push_screen(ResultsViewer("Trend Analysis Results", trends))

            self.notify("✅ Trend analysis complete!", severity="success")

        except Exception as e:
            self.notify(f"❌ Trend analysis failed: {str(e)}", severity="error")
            self.logger.log_error("TrendAnalysisError", e)

    def generate_report(self) -> None:
        """Generate comprehensive report"""
        if not self.analysis_results:
            self.notify(
                "No analysis results to generate report from!", severity="error"
            )
            return

        try:
            self.notify("📋 Generating report...", severity="information")

            # Generate report
            dashboard_generator = DashboardGenerator()
            report_path = dashboard_generator.generate_comprehensive_dashboard(
                self.analysis_results, output_path="rabbitmirror_report.html"
            )

            self.notify(f"✅ Report generated: {report_path}", severity="success")

        except Exception as e:
            self.notify(f"❌ Report generation failed: {str(e)}", severity="error")
            self.logger.log_error("ReportGenerationError", e)

    def save_settings(self) -> None:
        """Save current settings"""
        try:
            # Get values from inputs
            output_dir = self.query_one("#output-dir", Input).value
            default_format = self.query_one("#default-format", Input).value
            default_threshold = self.query_one("#default-threshold", Input).value

            # Save to config
            if output_dir:
                self.config.set("output_dir", output_dir)
            if default_format:
                self.config.set("default_format", default_format)
            if default_threshold:
                self.config.set("default_threshold", default_threshold)

            self.notify("✅ Settings saved!", severity="success")

        except Exception as e:
            self.notify(f"❌ Failed to save settings: {str(e)}", severity="error")
            self.logger.log_error("SettingsSaveError", e)

    def update_results_table(self, data: Dict[str, Any]) -> None:
        """Update the results table with new data"""
        table = self.query_one("#results-table", DataTable)
        table.clear()

        # Add columns if not present
        if not table.columns:
            table.add_column("Property", key="property")
            table.add_column("Value", key="value")

        # Add data rows
        for key, value in data.items():
            table.add_row(key.replace("_", " ").title(), str(value))

    def start_operation(self, operation_name: str) -> None:
        """Start tracking an operation with progress and timing"""
        self.operation_start_time = time.time()
        self.query_one("#operation-status", Static).update(f"Running: {operation_name}")
        self.query_one("#main-progress", ProgressBar).update(progress=0)
        self.start_timer()

    def update_operation_progress(self, progress: float, status: str = None) -> None:
        """Update operation progress (0-100)"""
        progress_bar = self.query_one("#main-progress", ProgressBar)
        progress_bar.update(progress=progress)

        if status:
            self.query_one("#operation-status", Static).update(status)

    def complete_operation(self, success: bool, final_status: str) -> None:
        """Complete an operation and update status"""
        self.query_one("#main-progress", ProgressBar).update(progress=100)
        self.query_one("#operation-status", Static).update(final_status)
        self.stop_timer()

        if success:
            elapsed = (
                time.time() - self.operation_start_time
                if self.operation_start_time
                else 0
            )
            self.query_one("#elapsed-time", Static).update(
                f"Completed in: {self.format_time(elapsed)}"
            )
        else:
            self.query_one("#elapsed-time", Static).update("Operation failed")

    def start_timer(self) -> None:
        """Start the elapsed time timer"""
        if self.timer_task:
            self.timer_task.cancel()
        self.timer_task = asyncio.create_task(self.update_timer())

    def stop_timer(self) -> None:
        """Stop the elapsed time timer"""
        if self.timer_task:
            self.timer_task.cancel()
            self.timer_task = None

    async def update_timer(self) -> None:
        """Update the elapsed time display"""
        while True:
            if self.operation_start_time:
                elapsed = time.time() - self.operation_start_time
                self.query_one("#elapsed-time", Static).update(
                    f"Elapsed: {self.format_time(elapsed)}"
                )
            await asyncio.sleep(1)

    def format_time(self, seconds: float) -> str:
        """Format seconds into H:MM:SS format"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        return f"{hours}:{minutes:02d}:{seconds:02d}"

    def action_help(self) -> None:
        """Show help information"""
        help_text = """
# RabbitMirror TUI Help

## Key Bindings
- **Q**: Quit application
- **H**: Show this help
- **R**: Refresh current view
- **Ctrl+C**: Quit application

## Getting Started
1. Select a YouTube watch history file (HTML format)
2. Parse the file to load data
3. Run various analysis tools
4. View results and generate reports

## Analysis Tools
- **Detect Patterns**: Find adversarial algorithm patterns
- **Cluster Videos**: Group similar videos
- **Analyze Suppression**: Detect content suppression
- **Simulate Profile**: Generate synthetic profiles
- **Trend Analysis**: Analyze viewing trends

## Tips
- Use the Settings tab to configure default values
- Results are stored and can be viewed anytime
- Reports are generated as HTML files
"""
        self.push_screen(ResultsViewer("Help", {"help": help_text}))

    def action_refresh(self) -> None:
        """Refresh the current view"""
        self.notify("🔄 Refreshing...", severity="information")
        # Refresh logic can be added here

    def action_quit(self) -> None:
        """Quit the application"""
        self.exit()


def main():
    """Main entry point for the TUI"""
    app = RabbitMirrorTUI()
    app.run()


if __name__ == "__main__":
    main()
