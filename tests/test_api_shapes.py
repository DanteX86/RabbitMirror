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

    # Create a minimal valid YouTube Takeout-like JSON file
    data = [
        {
            "time": "2024-01-01T00:00:00Z",
            "title": "Video A",
            "subtitles": [{"name": "ChannelX"}],
        },
        {
            "time": "2024-01-02T00:00:00Z",
            "title": "Video B",
            "subtitles": [{"name": "ChannelY"}],
        },
    ]
    filename = f"{uuid4().hex}.json"
    (upload_dir / filename).write_text(json.dumps(data), encoding="utf-8")

    # Mock HistoryParser and TrendAnalyzer
    m_parser = types.ModuleType("rabbitmirror.parser")

    class HistoryParser:
        def __init__(self, path):
            self._path = path

        def parse(self):
            return data

    m_parser.HistoryParser = HistoryParser

    m_trend = types.ModuleType("rabbitmirror.trend_analyzer")

    class TrendAnalyzer:
        def analyze_trends(self, history):
            return {
                "date_range": {"start": "2024-01-01", "end": "2024-01-31"},
                "total_watch_time_seconds": 3600,
            }

    m_trend.TrendAnalyzer = TrendAnalyzer

    # Optional dependencies used in analyze endpoint; provide minimal stubs
    m_cluster = types.ModuleType("rabbitmirror.cluster_engine")

    class ClusterEngine:
        def cluster_videos(self, history):
            return [[{"title": "Video A"}], [[{"title": "Video B"}]]]

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

    with flask_app.test_client() as c:
        yield c, filename


def test_export_analysis_results_shape(client):
    c, filename = client
    resp = c.get(f"/api/export/{filename}")
    assert resp.status_code == 200
    body = resp.get_json()
    # Check presence of structured fields
    assert "summary" in body
    assert body["summary"]["total_videos"] == 2
    assert "created_at" in body and "id" in body
    assert body.get("source") == "uploaded"
    assert body["metrics"]["total_videos"] == 2
    # Top channels/categories populated
    assert isinstance(body.get("top_channels"), list)
    assert isinstance(body.get("top_categories"), list)
    assert body["top_channels"][0]["video_count"] >= 1


def test_analyze_summary_shape(client):
    c, filename = client
    resp = c.get(f"/api/analyze/{filename}")
    assert resp.status_code == 200
    summary = resp.get_json()
    assert summary["filename"].endswith(".json")
    assert summary["total_videos"] == 2
    assert summary["status"] == "complete"
    assert "id" in summary and "created_at" in summary


def test_problem_json_examples_referenced():
    # Ensure openapi includes Problem+JSON examples for 401,404,413,429
    from rabbitmirror.web.app import _OPENAPI_SPEC

    comps = _OPENAPI_SPEC["components"]["responses"]
    assert (
        "examples" in comps["UnauthorizedError"]["content"]["application/problem+json"]
    )
    assert "examples" in comps["NotFoundError"]["content"]["application/problem+json"]
    assert "examples" in comps["TooManyRequests"]["content"]["application/problem+json"]
    assert "examples" in comps["ValidationError"]["content"]["application/problem+json"]


def test_unauthorized_problem_json(client, monkeypatch):
    # Enable API key and omit it
    from rabbitmirror.web.app import app as appref

    appref.config["API_KEY"] = "secret"
    c, filename = client
    resp = c.get(f"/api/analyze/{filename}")
    assert resp.status_code == 401
    assert resp.headers["Content-Type"].startswith("application/problem+json")
    body = resp.get_json()
    assert body["title"] == "Unauthorized"
    assert body["status"] == 401
    appref.config["API_KEY"] = None


def test_not_found_problem_json(client):
    c, _filename = client
    resp = c.get("/api/export/does-not-exist.json")
    assert resp.status_code == 404
    body = resp.get_json()
    assert body["status"] == 404
    assert body["title"] == "Not Found"


def test_payload_too_large_problem_json_real_payload(client):
    from rabbitmirror.web.app import app as appref

    appref.config["MAX_CONTENT_LENGTH"] = 50  # bytes
    c, _filename = client
    # Send a real oversized payload to an /api path so our 413 Problem+JSON handler applies
    resp = c.post(
        "/api/healthz", data=b"X" * 200, content_type="application/octet-stream"
    )
    assert resp.status_code == 413
    assert resp.headers["Content-Type"].startswith("application/problem+json")
    body = resp.get_json()
    assert body["title"] == "Payload too large"
    assert body["status"] == 413
    # after_request resets size in tests
