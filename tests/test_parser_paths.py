from pathlib import Path

import pytest

from rabbitmirror.exceptions import ParsingError
from rabbitmirror.parser import HistoryParser


class TestParserPaths:
    def test_get_parser_unsupported(self, tmp_path: Path):
        p = HistoryParser(str(tmp_path / "f.html"), platform="unknown")
        with pytest.raises(ParsingError):
            p._get_parser()

    def test_parse_with_fallback_encoding_failure(self, tmp_path: Path, monkeypatch):
        # Create a file that is not valid HTML content for our selector
        bad_file = tmp_path / "bad.html"
        bad_file.write_bytes(b"\xff\xfe\x00\x00\x00invalid\x00")

        # Monkeypatch import to ensure bs4 import error path is not triggered
        # and we hit the encoding loop and final ParsingError
        parser = HistoryParser(str(bad_file), platform="youtube")

        # Force encodings to fail by patching open to raise UnicodeDecodeError
        class DummyE(UnicodeDecodeError):
            def __init__(self):
                super().__init__("utf-8", b"", 0, 1, "reason")

        def bad_open(*args, **kwargs):  # noqa: ARG001
            raise DummyE()

        monkeypatch.setattr("builtins.open", bad_open)

        with pytest.raises(ParsingError):
            parser._parse_with_fallback()
