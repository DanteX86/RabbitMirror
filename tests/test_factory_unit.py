import importlib

from rabbitmirror.parsers.base_parser import ParserConfig
from rabbitmirror.parsers.factory import ParserFactory


def test_get_supported_platforms_contains_expected():
    plats = ParserFactory.get_supported_platforms()
    assert isinstance(plats, list)
    assert "youtube" in plats


def test_get_parser_returns_none_when_import_fails(monkeypatch):
    # Patch import_module to raise for the youtube module to exercise the exception branch
    import importlib as _importlib

    def boom(name):
        if name == "rabbitmirror.parsers.youtube_parser":
            raise ImportError("module missing")
        return importlib.import_module(name)

    monkeypatch.setattr(_importlib, "import_module", boom)

    cfg = ParserConfig(file_path="/tmp/x")
    p = ParserFactory.get_parser("youtube", cfg)
    assert p is None
