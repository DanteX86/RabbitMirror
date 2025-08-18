from datetime import datetime
from typing import Any, List

from rabbitmirror.parser import HistoryParser


class _FakeTag:
    def __init__(self, text: str = "", href: str = ""):
        self._text = text
        self._href = href

    def get_text(self, strip: bool = False):
        return self._text.strip() if strip else self._text

    def get(self, key: str, default: str = ""):
        if key == "href":
            return self._href
        return default


class _FakeEntry:
    def __init__(
        self,
        title: str = "Video Title",
        href: str = "http://example.com",
        ts: str = "Dec 15, 2023, 2:30:45 PM",
    ):
        self._title = title
        self._href = href
        self._ts = ts

    def find(self, name: str, class_: str = None):  # noqa: D401
        # Mimic BeautifulSoup API minimally
        if name == "a":
            if self._title is None:
                return None
            return _FakeTag(self._title, self._href)
        if name == "div" and class_ == "mdl-typography--caption":
            return _FakeTag(self._ts)
        return None


class _BadEntry:
    def find(self, *args, **kwargs):  # noqa: D401
        # Force an AttributeError path inside _extract_entries
        raise AttributeError("broken entry")


class _FakeSoup:
    def __init__(self, entries: List[Any]):
        self._entries = entries

    def select(self, selector: str):
        assert selector == "div.content-cell"
        return self._entries


def test_extract_entries_mixed_success_and_failures(monkeypatch):
    # Create soup with: one good, one missing title_tag (None), one empty title text, one raising exception
    good = _FakeEntry(
        title="Some Title", href="/watch?v=123", ts="Dec 15, 2023, 2:30:45 PM"
    )
    missing_title_tag = _FakeEntry(
        title=None
    )  # causes _parse_entry to return None early
    empty_title = _FakeEntry(title="   ")  # causes _parse_entry to return None early
    bad = _BadEntry()

    soup = _FakeSoup([good, missing_title_tag, empty_title, bad])
    p = HistoryParser("/tmp/whatever.html")

    entries = p._extract_entries(soup)  # noqa: SLF001
    # Only the good one should be returned
    assert isinstance(entries, list)
    assert len(entries) == 1
    assert entries[0]["title"] == "Some Title"


def test_parse_with_fallback_success(tmp_path):
    # Build minimal HTML similar to Google Takeout export
    html = tmp_path / "watch.html"
    html.write_text(
        """
        <html><body>
          <div class="content-cell">
            <a href="https://www.youtube.com/watch?v=abc">Example Video</a>
            <div class="mdl-typography--caption">Dec 15, 2023, 2:30:45 PM</div>
          </div>
        </body></html>
        """,
        encoding="utf-8",
    )

    p = HistoryParser(str(html))
    result = p._parse_with_fallback()  # noqa: SLF001
    assert isinstance(result, list)
    assert result and result[0]["title"] == "Example Video"
    # Timestamp should be ISO format
    datetime.fromisoformat(result[0]["timestamp"])  # will raise if invalid


def test_parse_entry_invalid_timestamp_falls_back(monkeypatch):
    entry = _FakeEntry(title="T", href="/x", ts="not-a-time")
    p = HistoryParser("/tmp/whatever.html")
    data = p._parse_entry(entry)  # noqa: SLF001
    assert data is not None
    # Should fallback to now-ish ISO string
    datetime.fromisoformat(data["timestamp"])  # no assertion on recency, only format
