import json
import sys
import types
from uuid import uuid4

import pytest

from rabbitmirror.web.app import app as flask_app


@pytest.fixture()
def client(tmp_path, monkeypatch):
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

    return flask_app.test_client(), write_history, monkeypatch


def test_analyze_includes_total_watch_time_from_analyzer(client):
    c, write_history, monkeypatch = client

    entries = [
        {"time": "2024-01-01T00:00:00Z", "title": "A"},
        {"time": "2024-01-02T00:00:00Z", "title": "B"},
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

    # Provide minimal stubs for other imports used in analyze
    m_cluster = types.ModuleType("rabbitmirror.cluster_engine")

    class ClusterEngine:
        def cluster_videos(self, history):
            return [{"items": [1, 2, 3]}]

    m_cluster.ClusterEngine = ClusterEngine

    m_suppr = types.ModuleType("rabbitmirror.suppression_index")

    class SuppressionIndex:
        def calculate_suppression(self, history):
            return {"score": 0.2}

    m_suppr.SuppressionIndex = SuppressionIndex

    m_adv = types.ModuleType("rabbitmirror.adversarial_profiler")

    class AdversarialProfiler:
        def identify_adversarial_patterns(self, history):
            return types.SimpleNamespace(risk_score=0.1)

    m_adv.AdversarialProfiler = AdversarialProfiler

    monkeypatch.setitem(sys.modules, "rabbitmirror.parser", m_parser)
    monkeypatch.setitem(sys.modules, "rabbitmirror.trend_analyzer", m_trend)
    monkeypatch.setitem(sys.modules, "rabbitmirror.cluster_engine", m_cluster)
    monkeypatch.setitem(sys.modules, "rabbitmirror.suppression_index", m_suppr)
    monkeypatch.setitem(sys.modules, "rabbitmirror.adversarial_profiler", m_adv)

    resp = c.get(f"/api/analyze/{filename}")
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["total_watch_time"]["seconds"] == 3900
    human = body["total_watch_time"]["human"]
    assert isinstance(human, str) and "1h" in human and "5m" in human


def test_analyze_includes_total_watch_time_fallback_sum(client):
    c, write_history, monkeypatch = client

    entries = [
        {"time": "2024-01-01T00:00:00Z", "title": "A", "duration_seconds": 120},
        {"time": "2024-01-02T00:00:00Z", "title": "B", "lengthSeconds": 300},
        {"time": "2024-01-03T00:00:00Z", "title": "C", "timeWatchedSeconds": 60},
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

    # Provide minimal stubs for other imports used in analyze
    m_cluster = types.ModuleType("rabbitmirror.cluster_engine")

    class ClusterEngine:
        def cluster_videos(self, history):
            return [{"items": [1]}]

    m_cluster.ClusterEngine = ClusterEngine

    m_suppr = types.ModuleType("rabbitmirror.suppression_index")

    class SuppressionIndex:
        def calculate_suppression(self, history):
            return {"score": 0.1}

    m_suppr.SuppressionIndex = SuppressionIndex

    m_adv = types.ModuleType("rabbitmirror.adversarial_profiler")

    class AdversarialProfiler:
        def identify_adversarial_patterns(self, history):
            return types.SimpleNamespace(risk_score=0.0)

    m_adv.AdversarialProfiler = AdversarialProfiler

    monkeypatch.setitem(sys.modules, "rabbitmirror.parser", m_parser)
    monkeypatch.setitem(sys.modules, "rabbitmirror.trend_analyzer", m_trend)
    monkeypatch.setitem(sys.modules, "rabbitmirror.cluster_engine", m_cluster)
    monkeypatch.setitem(sys.modules, "rabbitmirror.suppression_index", m_suppr)
    monkeypatch.setitem(sys.modules, "rabbitmirror.adversarial_profiler", m_adv)

    resp = c.get(f"/api/analyze/{filename}")
    assert resp.status_code == 200
    body = resp.get_json()
    # 120 + 300 + 60 = 480 seconds -> 8m
    assert body["total_watch_time"]["seconds"] == 480
    human = body["total_watch_time"]["human"]
    assert isinstance(human, str) and "8m" in human
