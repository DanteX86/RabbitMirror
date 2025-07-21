#!/usr/bin/env python3

"""
Test RabbitMirror TUI without CSS
"""

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import (
    Button,
    Footer,
    Header,
    Input,
    Label,
    Static,
    TabbedContent,
    TabPane,
)


class TestRabbitMirrorTUI(App):
    """Test RabbitMirror TUI without CSS"""

    TITLE = "🐰 RabbitMirror - YouTube Watch History Analyzer"
    SUB_TITLE = "Interactive Terminal Interface"

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("ctrl+c", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()

        with TabbedContent(initial="main"):
            # Main tab
            with TabPane("Main", id="main"):
                with Vertical():
                    yield Static("🎯 Welcome to RabbitMirror TUI", id="welcome")

                    with Horizontal():
                        yield Button("📁 Select File", id="select-file")
                        yield Static("No file selected", id="file-status")

                    with Horizontal():
                        yield Button("🔍 Quick Parse", id="quick-parse")
                        yield Button("📊 Quick Analysis", id="quick-analysis")
                        yield Button("📈 View Results", id="view-results")

            # Analysis tab
            with TabPane("Analysis", id="analysis"):
                with Vertical():
                    yield Static("🔬 Analysis Tools", id="analysis-title")

                    with Horizontal():
                        yield Button("🎯 Detect Patterns", id="detect-patterns")
                        yield Button("🔄 Cluster Videos", id="cluster-videos")

                    yield Static("Analysis Options:", id="options-title")
                    with Horizontal():
                        yield Label("Threshold:")
                        yield Input(placeholder="0.7", id="threshold-input")

        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id

        if button_id == "select-file":
            self.query_one("#file-status", Static).update("📄 test-file.html")
            self.notify("File selected!", severity="information")
        elif button_id == "quick-parse":
            self.notify("Parsing file...", severity="information")
        elif button_id == "quick-analysis":
            self.notify("Running analysis...", severity="information")
        elif button_id == "view-results":
            self.notify("No results yet", severity="warning")
        elif button_id == "detect-patterns":
            self.notify("Detecting patterns...", severity="information")
        elif button_id == "cluster-videos":
            self.notify("Clustering videos...", severity="information")

    def action_quit(self) -> None:
        self.exit()


if __name__ == "__main__":
    app = TestRabbitMirrorTUI()
    app.run()
