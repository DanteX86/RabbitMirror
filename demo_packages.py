#!/usr/bin/env python3

import rich
import textual
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, DataTable


class DemoTUI(App):
    CSS = """
    Screen {
        layout: vertical;
    }
    #title {
        content-align: center middle;
        height: 3;
    }
    #pkgs {
        height: 8;
        width: 60;
        margin: 1 2;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static("Rich + Textual Demo", id="title")
        table = DataTable(id="pkgs")
        table.add_columns("Package", "Version")
        table.add_row("rich", getattr(rich, "__version__", "unknown"))
        table.add_row("textual", getattr(textual, "__version__", "unknown"))
        yield table
        yield Footer()


if __name__ == "__main__":
    DemoTUI().run()
