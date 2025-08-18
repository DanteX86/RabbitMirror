import re

from rabbitmirror.parser import HistoryParser


def test_convert_timestamp_unknown_returns_now():
    hp = HistoryParser(file_path="/tmp/nowhere.html")
    out = hp._convert_timestamp("Unknown")
    assert re.match(r"\d{4}-\d{2}-\d{2}T", out)


def test_parse_entry_no_caption_uses_now_timestamp():
    hp = HistoryParser(file_path="/tmp/nowhere.html")

    class _Entry:
        def __init__(self):
            pass

        def find(self, name, class_=None):
            if name == "a":

                class _A:
                    def get_text(self, strip=False):
                        return "Z"

                    def get(self, key, default=None):
                        if key == "href":
                            return "/u"
                        return default

                return _A()
            if name == "div" and class_ == "mdl-typography--caption":
                return None
            return None

    out = hp._parse_entry(_Entry())
    assert out["title"] == "Z"
    assert re.match(r"\d{4}-\d{2}-\d{2}T", out["timestamp"]) is not None
