#!/usr/bin/env python3

"""
Simple TUI test to debug display issues
"""

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Footer, Header, Static


class TestTUI(App):
    """Simple test TUI"""

    TITLE = "Test TUI"
    SUB_TITLE = "Debug Display"

    def compose(self) -> ComposeResult:
        yield Header()

        with Vertical():
            yield Static("Hello World!", id="test-static")
            yield Static("This is a test message", id="test-static2")

            with Horizontal():
                yield Button("Test Button 1", id="btn1")
                yield Button("Test Button 2", id="btn2")

            yield Static("🐰 Emoji test", id="emoji-test")
            yield Static("Colors and formatting test", id="format-test")

        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn1":
            self.query_one("#test-static2", Static).update("Button 1 pressed!")
        elif event.button.id == "btn2":
            self.query_one("#test-static2", Static).update("Button 2 pressed!")


if __name__ == "__main__":
    app = TestTUI()
    app.run()
