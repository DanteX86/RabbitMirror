import builtins
import importlib
import io
import re
import types

import pytest

from rabbitmirror.exceptions import DependencyError, InvalidFormatError, ParsingError
from rabbitmirror.parser import HistoryParser


class FakeTag:
    def __init__(self, text=None, href=None, cls=None):
        self._text = text
        self._href = href
        self._cls = cls

    def get_text(self, strip=False):
        return (
            self._text.strip() if strip and isinstance(self._text, str) else self._text
        )

    def get(self, key, default=None):
        if key == "href":
            return self._href if self._href is not None else default
        return default


class FakeEntry:
    def __init__(self, title_text=None, href=None, caption_text=None, broken=False):
        self.title_text = title_text
        self.href = href
        self.caption_text = caption_text
        self.broken = broken

    def find(self, name, class_=None):
        if self.broken:
            # Simulate an AttributeError during parsing
            raise AttributeError("broken entry")
        if name == "a":
            if self.title_text is None:
                return None
            return FakeTag(text=self.title_text, href=self.href)
        if name == "div" and class_ == "mdl-typography--caption":
            if self.caption_text is None:
                return None
            return FakeTag(text=self.caption_text)
        return None


class FakeSoup:
    def __init__(self, entries):
        self._entries = entries

    def select(self, selector):
        assert selector == "div.content-cell"
        return self._entries


def test_extract_entries_outer_exception_logging(monkeypatch, caplog):
    # Force _parse_entry itself to raise, so _extract_entries catches and logs at WARNING,
    # and then emits the INFO summary for failed entries.
    hp = HistoryParser(file_path="/tmp/nowhere.html")

    def boom(entry):
        raise ValueError("explode")

    monkeypatch.setattr(HistoryParser, "_parse_entry", boom)

    soup = FakeSoup([FakeEntry(title_text="X", caption_text="2023-12-15 14:30:45")])
    with caplog.at_level("INFO"):
        entries = hp._extract_entries(soup)

    assert entries == []
    assert any(
        r.levelname == "WARNING" and "Failed to parse entry" in r.message
        for r in caplog.records
    )
    assert any(
        r.levelname == "INFO" and "Successfully parsed" in r.message
        for r in caplog.records
    )


def test_convert_timestamp_multiple_formats():
    hp = HistoryParser(file_path="/tmp/nowhere.html")
    samples = [
        ("Dec 15, 2023, 2:30:45 PM", "2023-12-15T14:30:45"),
        ("Dec 15, 2023 2:30:45 PM", "2023-12-15T14:30:45"),
        ("2023-12-15 14:30:45", "2023-12-15T14:30:45"),
        ("2023-12-15T14:30:45", "2023-12-15T14:30:45"),
        ("2023-12-15", "2023-12-15T00:00:00"),
    ]
    for s, starts in samples:
        iso = hp._convert_timestamp(s)
        assert iso.startswith(starts)


def test_convert_timestamp_invalid_raises():
    hp = HistoryParser(file_path="/tmp/nowhere.html")
    with pytest.raises(InvalidFormatError):
        hp._convert_timestamp("not-a-timestamp")


def test_extract_entries_mixed_success_and_failure(caplog):
    good = FakeEntry(
        title_text="Video A",
        href="https://youtu.be/x",
        caption_text="2023-12-15 14:30:45",
    )
    bad = FakeEntry(broken=True)
    soup = FakeSoup([good, bad])
    hp = HistoryParser(file_path="/tmp/nowhere.html")

    with caplog.at_level("INFO"):
        entries = hp._extract_entries(soup)

    assert len(entries) == 1
    assert entries[0]["title"] == "Video A"
    # The broken entry path should log a warning
    assert any(
        r.levelname == "WARNING" and "Failed to parse entry" in r.message
        for r in caplog.records
    )


def test_get_parser_unsupported_platform(monkeypatch):
    # Force ParserFactory.get_parser to return None so HistoryParser raises ParsingError
    from rabbitmirror import parsers as parsers_pkg

    def fake_get_parser(platform, config):
        return None

    monkeypatch.setattr(parsers_pkg.ParserFactory, "get_parser", fake_get_parser)

    hp = HistoryParser(file_path="/tmp/nowhere.html", platform="unknown-site")
    with pytest.raises(ParsingError):
        hp._get_parser()


def test_parse_with_fallback_all_encodings_fail(monkeypatch, tmp_path):
    # Create a path that will be opened; patch open to raise UnicodeDecodeError for all reads
    fpath = tmp_path / "history.html"
    fpath.write_bytes(b"\xff\xfe\x00\x00")

    def fake_open(*args, **kwargs):
        # Simulate decode error consistently
        raise UnicodeDecodeError("utf-8", b"\x80", 0, 1, "invalid start byte")

    monkeypatch.setattr(builtins, "open", fake_open)

    hp = HistoryParser(file_path=str(fpath))
    with pytest.raises(ParsingError) as ei:
        hp._parse_with_fallback()

    err = ei.value
    assert getattr(err, "error_code", None) == "ENCODING_FAILED"


def test_parse_with_fallback_missing_bs4(monkeypatch, tmp_path):
    # Provide decodable content but make bs4 import fail to trigger DependencyError
    fpath = tmp_path / "history.html"
    fpath.write_text(
        "<html><div class='content-cell'><a href='u'>t</a></div></html>",
        encoding="utf-8",
    )

    def fake_import_module(name):
        if name == "bs4":
            raise ImportError("no bs4")
        return importlib.import_module(name)

    import importlib as _importlib

    monkeypatch.setattr(_importlib, "import_module", fake_import_module)

    hp = HistoryParser(file_path=str(fpath))
    with pytest.raises(DependencyError):
        hp._parse_with_fallback()


def test_parse_with_fallback_success(monkeypatch, tmp_path):
    # Provide decodable content and a fake bs4 that returns a FakeSoup with no entries
    fpath = tmp_path / "history.html"
    fpath.write_text("<html><body></body></html>", encoding="utf-8")

    class _FakeBS4:
        class BeautifulSoup:
            def __init__(self, fobj, parser):
                # Emulate a soup object with no content-cell entries
                self._fake = FakeSoup([])

            def select(self, selector):
                return self._fake.select(selector)

    import importlib as _importlib

    def fake_import_module(name):
        if name == "bs4":
            return _FakeBS4
        return importlib.import_module(name)

    monkeypatch.setattr(_importlib, "import_module", fake_import_module)

    hp = HistoryParser(file_path=str(fpath))
    # Should return empty list without raising, covering the successful bs4 path
    results = hp._parse_with_fallback()
    assert results == []


def test_parse_entry_title_missing_and_invalid_timestamp():
    hp = HistoryParser(file_path="/tmp/nowhere.html")
    # Missing title_tag path returns None
    no_title = FakeEntry(title_text=None, caption_text="2023-12-15 14:30:45")
    assert hp._parse_entry(no_title) is None

    # Title present but invalid timestamp triggers InvalidFormatError branch and fallback to now
    invalid_ts = FakeEntry(title_text="T", href="/u", caption_text="not-a-ts")
    out = hp._parse_entry(invalid_ts)
    assert out["title"] == "T"
    assert re.match(r"\d{4}-\d{2}-\d{2}T", out["timestamp"]) is not None
