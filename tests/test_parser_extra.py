import importlib
import io
import json
from datetime import datetime, timedelta

import pytest

from rabbitmirror.exceptions import DependencyError, InvalidFormatError, ParsingError
from rabbitmirror.parser import HistoryParser


def test_convert_timestamp_various_formats():
    p = HistoryParser("/tmp/nowhere.html")
    samples = [
        ("Dec 15, 2023, 2:30:45 PM", "%Y-%m-%dT%H:%M:%S"),
        ("Dec 15, 2023 2:30:45 PM", "%Y-%m-%dT%H:%M:%S"),
        ("2023-12-15 14:30:45", "%Y-%m-%dT%H:%M:%S"),
        ("2023-12-15T14:30:45", "%Y-%m-%dT%H:%M:%S"),
        ("2023-12-15", "%Y-%m-%dT%H:%M:%S"),
        ("Dec 15, 2023, 2:30:45 PM UTC", "%Y-%m-%dT%H:%M:%S"),  # trailing TZ trimmed
    ]
    for s, fmt in samples:
        iso = p._convert_timestamp(
            s
        )  # noqa: SLF001 (testing private method intentionally)
        # Should be ISO-8601 parseable prefix
        datetime.strptime(iso[:19], fmt)


def test_convert_timestamp_unknown_returns_recent_time():
    p = HistoryParser("/tmp/nowhere.html")
    iso = p._convert_timestamp("Unknown")  # noqa: SLF001
    ts = datetime.fromisoformat(iso)
    assert datetime.now() - ts < timedelta(seconds=5)


def test_convert_timestamp_invalid_raises():
    p = HistoryParser("/tmp/nowhere.html")
    with pytest.raises(InvalidFormatError):
        p._convert_timestamp("Not a real time string")  # noqa: SLF001


def test_get_parser_unsupported_platform_raises():
    p = HistoryParser("/tmp/file.html", platform="nonexistent")
    with pytest.raises(ParsingError):
        p._get_parser()  # noqa: SLF001


def test_parse_with_fallback_bs4_missing(tmp_path, monkeypatch):
    # Create a minimal file so open() succeeds
    f = tmp_path / "empty.html"
    f.write_text("<html></html>")

    # Force bs4 import failure inside the fallback path
    def fake_import(name):
        if name == "bs4":
            raise ImportError("bs4 not installed")
        return importlib.import_module(name)

    monkeypatch.setattr(importlib, "import_module", fake_import)

    p = HistoryParser(str(f))
    # Call the fallback directly to isolate behavior without factory
    with pytest.raises(DependencyError):
        p._parse_with_fallback()  # noqa: SLF001
