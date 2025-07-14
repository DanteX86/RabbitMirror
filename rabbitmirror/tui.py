"""
Terminal User Interface for RabbitMirror
Modern, interactive TUI using Textual framework
"""

import os
import sys
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import (
    Header, Footer, Static, Button, Input, Label, 
    DataTable, Tree, Log, TabbedContent, TabPane,
    SelectionList, Switch, ProgressBar, Markdown
)
from textual.screen import Screen, ModalScreen
from textual.binding import Binding
from textual import events
from textual.message import Message
from textual.reactive import reactive
from textual.validation import Function
from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress

# Import RabbitMirror components
try:
    from .parser import parse_watch_history
    from .cluster_engine import ClusterEngine
    from .adversarial_profiler import AdversarialProfiler
    from .suppression_index import SuppressionIndex
    from .profile_simulator import ProfileSimulator
    from .trend_analyzer import TrendAnalyzer
    from .export_formatter import ExportFormatter
    from .dashboard_generator import DashboardGenerator
    from .config_manager import ConfigManager
    from .symbolic_logger import SymbolicLogger
except ImportError:
    # Fallback for development
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from rabbitmirror.parser import parse_watch_history
    from rabbitmirror.cluster_engine import ClusterEngine
    from rabbitmirror.adversarial_profiler import AdversarialProfiler
    from rabbitmirror.suppression_index import SuppressionIndex
    from rabbitmirror.profile_simulator import ProfileSimulator
    from rabbitmirror.trend_analyzer import TrendAnalyzer
    from rabbitmirror.export_formatter import ExportFormatter
    from rabbitmirror.dashboard_generator import DashboardGenerator
    from rabbitmirror.config_manager import ConfigManager
    from rabbitmirror.symbolic_logger import SymbolicLogger


class FileSelector(ModalScreen):
    """Modal screen for selecting files"""
    
    def __init__(self, title: str = "Select File", filter_ext: str = ".html"):
        super().__init__()
        self.title = title
        self.filter_ext = filter_ext
        self.selected_file = None
    
    def compose(self) -> ComposeResult:
        with Container(id="file-selector"):
            yield Static(f"📁 {self.title}", id="file-title")
            yield Input(placeholder="Enter file path or browse...", id="file-input")
            with Horizontal():
                yield Button("Browse", id="browse-btn", variant="primary")
                yield Button("Select", id="select-btn", variant="success")
                yield Button("Cancel", id="cancel-btn", variant="error")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "browse-btn":
            self.browse_files()
        elif event.button.id == "select-btn":
            self.select_file()
        elif event.button.id == "cancel-btn":
            self.dismiss(None)
    
    def browse_files(self) -> None:
        """Browse for files in current directory"""
        current_dir = Path.cwd()
        files = [f for f in current_dir.glob(f"*{self.filter_ext}") if f.is_file()]
        
        if files:
            file_input = self.query_one("#file-input", Input)
            file_input.value = str(files[0])
    
    def select_file(self) -> None:
        """Select the file from input"""
        file_input = self.query_one("#file-input", Input)
        file_path = file_input.value.strip()
        
        if file_path and Path(file_path).exists():
            self.dismiss(file_path)
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
                Markdown(self.format_results()),
                id="results-content"
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
    
    CSS_PATH = "tui.css"
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
    
    def compose(self) -> ComposeResult:
        """Create the main layout"""
        yield Header()
        
        with TabbedContent(initial="main"):
            # Main tab
            with TabPane("Main", id="main"):
                with Vertical():
                    yield Static("🎯 Welcome to RabbitMirror TUI", id="welcome")
                    
                    with Horizontal(id="file-section"):
                        yield Button("📁 Select File", id="select-file", variant="primary")
                        yield Static("No file selected", id="file-status")
                    
                    with Horizontal(id="quick-actions"):
                        yield Button("🔍 Quick Parse", id="quick-parse", variant="success")
                        yield Button("📊 Quick Analysis", id="quick-analysis", variant="success")
                        yield Button("📈 View Results", id="view-results", variant="default")
            
            # Analysis tab
            with TabPane("Analysis", id="analysis"):
                with Vertical():
                    yield Static("🔬 Analysis Tools", id="analysis-title")
                    
                    with Horizontal():
                        yield Button("🎯 Detect Patterns", id="detect-patterns")
                        yield Button("🔄 Cluster Videos", id="cluster-videos")
                        yield Button("📉 Analyze Suppression", id="analyze-suppression")
                    
                    with Horizontal():
                        yield Button("🎮 Simulate Profile", id="simulate-profile")
                        yield Button("📊 Trend Analysis", id="trend-analysis")
                        yield Button("📋 Generate Report", id="generate-report")
                    
                    yield Static("Analysis Options:", id="options-title")
                    with Horizontal():
                        yield Label("Threshold:")
                        yield Input(placeholder="0.7", id="threshold-input")
                        yield Label("Format:")
                        yield Input(placeholder="json", id="format-input")
            
            # Results tab
            with TabPane("Results", id="results"):
                with Vertical():
                    yield Static("📊 Analysis Results", id="results-title")
                    yield DataTable(id="results-table")
                    yield Log(id="results-log")
            
            # Settings tab
            with TabPane("Settings", id="settings"):
                with Vertical():
                    yield Static("⚙️ Configuration", id="settings-title")
                    
                    with Horizontal():
                        yield Label("Default Output Directory:")
                        yield Input(placeholder="/path/to/output", id="output-dir")
                    
                    with Horizontal():
                        yield Label("Default Format:")
                        yield Input(placeholder="json", id="default-format")
                    
                    with Horizontal():
                        yield Label("Analysis Threshold:")
                        yield Input(placeholder="0.7", id="default-threshold")
                    
                    yield Button("💾 Save Settings", id="save-settings", variant="success")
        
        yield Footer()
    
    def on_mount(self) -> None:
        """Initialize the application"""
        self.notify("🐰 RabbitMirror TUI started!", severity="information")
        self.load_settings()
    
    def load_settings(self) -> None:
        """Load saved settings"""
        try:
            # Load configuration
            settings = self.config.get_all_config()
            
            # Update UI with saved settings
            if "output_dir" in settings:
                self.query_one("#output-dir", Input).value = str(settings["output_dir"])
            if "default_format" in settings:
                self.query_one("#default-format", Input).value = str(settings["default_format"])
            if "default_threshold" in settings:
                self.query_one("#default-threshold", Input).value = str(settings["default_threshold"])
                
        except Exception as e:
            self.logger.log_error(f"Failed to load settings: {e}")
    
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
                self.query_one("#file-status", Static).update(f"📄 {Path(file_path).name}")
                self.notify(f"Selected: {Path(file_path).name}", severity="information")
            
        self.push_screen(FileSelector("Select YouTube Watch History File", ".html"), handle_file_selection)
    
    def quick_parse(self) -> None:
        """Quick parse of selected file"""
        if not self.current_file:
            self.notify("Please select a file first!", severity="error")
            return
        
        try:
            self.notify("🔄 Parsing file...", severity="information")
            
            # Parse the file
            self.current_data = parse_watch_history(self.current_file)
            
            # Update results table
            self.update_results_table({
                "total_entries": len(self.current_data),
                "file_parsed": Path(self.current_file).name,
                "parse_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            
            self.notify(f"✅ Parsed {len(self.current_data)} entries", severity="success")
            
        except Exception as e:
            self.notify(f"❌ Parse failed: {str(e)}", severity="error")
            self.logger.log_error(f"Parse error: {e}")
    
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
                "analysis_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Update results table
            self.update_results_table({
                "patterns_found": len(patterns.get("patterns", [])),
                "clusters_found": len(clusters.get("clusters", [])),
                "analysis_complete": "✅ Yes"
            })
            
            self.notify("✅ Quick analysis complete!", severity="success")
            
        except Exception as e:
            self.notify(f"❌ Analysis failed: {str(e)}", severity="error")
            self.logger.log_error(f"Analysis error: {e}")
    
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
            self.logger.log_error(f"Pattern detection error: {e}")
    
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
            self.logger.log_error(f"Clustering error: {e}")
    
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
            self.logger.log_error(f"Suppression analysis error: {e}")
    
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
            self.logger.log_error(f"Profile simulation error: {e}")
    
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
            self.logger.log_error(f"Trend analysis error: {e}")
    
    def generate_report(self) -> None:
        """Generate comprehensive report"""
        if not self.analysis_results:
            self.notify("No analysis results to generate report from!", severity="error")
            return
        
        try:
            self.notify("📋 Generating report...", severity="information")
            
            # Generate report
            dashboard_generator = DashboardGenerator()
            report_path = dashboard_generator.generate_comprehensive_dashboard(
                self.analysis_results,
                output_path="rabbitmirror_report.html"
            )
            
            self.notify(f"✅ Report generated: {report_path}", severity="success")
            
        except Exception as e:
            self.notify(f"❌ Report generation failed: {str(e)}", severity="error")
            self.logger.log_error(f"Report generation error: {e}")
    
    def save_settings(self) -> None:
        """Save current settings"""
        try:
            # Get values from inputs
            output_dir = self.query_one("#output-dir", Input).value
            default_format = self.query_one("#default-format", Input).value
            default_threshold = self.query_one("#default-threshold", Input).value
            
            # Save to config
            if output_dir:
                self.config.set_config("output_dir", output_dir)
            if default_format:
                self.config.set_config("default_format", default_format)
            if default_threshold:
                self.config.set_config("default_threshold", default_threshold)
            
            self.notify("✅ Settings saved!", severity="success")
            
        except Exception as e:
            self.notify(f"❌ Failed to save settings: {str(e)}", severity="error")
            self.logger.log_error(f"Settings save error: {e}")
    
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
