import json
import sys
import types
from uuid import uuid4

import pytest

from rabbitmirror.web.app import app as flask_app


@pytest.fixture()
def client(tmp_path, monkeypatch):
    # Prepare upload folder
    upload_dir = tmp_path / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)
    flask_app.config["UPLOAD_FOLDER"] = str(upload_dir)
    flask_app.testing = True
    flask_app.config["API_RATE_LIMIT_BYPASS"] = True
    flask_app.config["API_KEY"] = None

    def write_history(entries):
        filename = f"{uuid4().hex}.json"
        (upload_dir / filename).write_text(json.dumps(entries), encoding="utf-8")
        return filename

    # Minimal stubs for parser and trend analyzer will be supplied in tests
    return flask_app.test_client(), write_history, monkeypatch


def test_export_includes_total_watch_time_from_analyzer(client):
    c, write_history, monkeypatch = client

    # Create entries (durations ignored because analyzer provides total)
    entries = [
        {"time": "2024-01-01T00:00:00Z", "title": "A", "duration_seconds": 120},
        {"time": "2024-01-02T00:00:00Z", "title": "B", "duration_seconds": 300},
    ]
    filename = write_history(entries)

    # Mock HistoryParser
    m_parser = types.ModuleType("rabbitmirror.parser")

    class HistoryParser:
        def __init__(self, path):
            self._path = path

        def parse(self):
            return entries

    m_parser.HistoryParser = HistoryParser

    # Mock TrendAnalyzer to provide total seconds
    m_trend = types.ModuleType("rabbitmirror.trend_analyzer")

    class TrendAnalyzer:
        def analyze_trends(self, history):
            return {
                "date_range": {"start": "2024-01-01", "end": "2024-01-31"},
                "total_watch_time_seconds": 3900,  # 1h 5m
            }

    m_trend.TrendAnalyzer = TrendAnalyzer

    monkeypatch.setitem(sys.modules, "rabbitmirror.parser", m_parser)
    monkeypatch.setitem(sys.modules, "rabbitmirror.trend_analyzer", m_trend)

    resp = c.get(f"/api/export/{filename}")
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["summary"]["total_watch_time"]["seconds"] == 3900
    # Allow either '1h 5m' or '1h 5m 0s' depending on formatter; must contain '1h' and '5m'
    human = body["summary"]["total_watch_time"]["human"]
    assert isinstance(human, str)
    assert "1h" in human and "5m" in human
    assert body["metrics"]["total_watch_time_seconds"] == 3900


def test_export_includes_total_watch_time_fallback_sum(client):
    c, write_history, monkeypatch = client

    # Create entries with per-item durations; analyzer won't return total
    entries = [
        {"time": "2024-01-01T00:00:00Z", "title": "A", "duration_seconds": 120},
        {"time": "2024-01-02T00:00:00Z", "title": "B", "duration_seconds": 300},
        {"time": "2024-01-03T00:00:00Z", "title": "C", "duration_seconds": 60},
    ]
    filename = write_history(entries)

    # Mock HistoryParser
    m_parser = types.ModuleType("rabbitmirror.parser")

    class HistoryParser:
        def __init__(self, path):
            self._path = path

        def parse(self):
            return entries

    m_parser.HistoryParser = HistoryParser

    # Mock TrendAnalyzer to omit total seconds
    m_trend = types.ModuleType("rabbitmirror.trend_analyzer")

    class TrendAnalyzer:
        def analyze_trends(self, history):
            return {"date_range": {"start": "2024-01-01", "end": "2024-01-31"}}

    m_trend.TrendAnalyzer = TrendAnalyzer

    monkeypatch.setitem(sys.modules, "rabbitmirror.parser", m_parser)
    monkeypatch.setitem(sys.modules, "rabbitmirror.trend_analyzer", m_trend)

    resp = c.get(f"/api/export/{filename}")
    assert resp.status_code == 200
    body = resp.get_json()
    # 120 + 300 + 60 = 480 seconds -> 8m
    assert body["summary"]["total_watch_time"]["seconds"] == 480
    human = body["summary"]["total_watch_time"]["human"]
    assert isinstance(human, str)
    assert "8m" in human
    assert body["metrics"]["total_watch_time_seconds"] == 480
