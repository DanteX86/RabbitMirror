import pytest

pytest.importorskip("flask")


def get_client():
    from rabbitmirror.web.app import app

    app.testing = True
    return app.test_client(), app


def test_openapi_and_docs_routes():
    client, _ = get_client()
    r1 = client.get("/openapi.json")
    assert r1.status_code == 200
    data = r1.get_json()
    assert data.get("openapi", "").startswith("3.")
    r2 = client.get("/docs")
    assert r2.status_code == 200
    # Swagger UI CSS and Redoc script tags present
    assert b"swagger-ui.css" in r2.data
    assert b"swagger-ui-bundle.js" in r2.data
    assert b"redoc.standalone.js" in r2.data


def test_api_analyze_returns_json_summary(tmp_path, monkeypatch):
    # Install dummy modules to satisfy imports inside route handlers
    import sys
    import types

    class _DummyHistoryParser:
        def __init__(self, path):
            self.path = path

        def parse(self):
            return [
                types.SimpleNamespace(
                    title="Video A", watched_at="2024-01-01T00:00:00Z"
                )
            ]

    class _DummyTrendAnalyzer:
        def analyze_trends(self, watch_history):
            return {"date_range": {"start": "2024-01-01", "end": "2024-01-31"}}

    class _DummyClusterEngine:
        def cluster_videos(self, watch_history):
            return {0: watch_history[:1]}

    class _DummySuppressionIndex:
        def calculate_suppression(self, watch_history):
            return {"score": 0.3}

    class _DummyAdversarialProfiler:
        def identify_adversarial_patterns(self, watch_history):
            return types.SimpleNamespace(risk_score=0.2)

    monkeypatch.setitem(
        sys.modules,
        "rabbitmirror.parser",
        types.SimpleNamespace(HistoryParser=_DummyHistoryParser),
    )
    monkeypatch.setitem(
        sys.modules,
        "rabbitmirror.trend_analyzer",
        types.SimpleNamespace(TrendAnalyzer=_DummyTrendAnalyzer),
    )
    monkeypatch.setitem(
        sys.modules,
        "rabbitmirror.cluster_engine",
        types.SimpleNamespace(ClusterEngine=_DummyClusterEngine),
    )
    monkeypatch.setitem(
        sys.modules,
        "rabbitmirror.suppression_index",
        types.SimpleNamespace(SuppressionIndex=_DummySuppressionIndex),
    )
    monkeypatch.setitem(
        sys.modules,
        "rabbitmirror.adversarial_profiler",
        types.SimpleNamespace(AdversarialProfiler=_DummyAdversarialProfiler),
    )

    client, app = get_client()
    app.config["UPLOAD_FOLDER"] = str(tmp_path)

    # Create a dummy file
    dummy_file = tmp_path / "sample.json"
    dummy_file.write_text("{}")

    resp = client.get("/api/analyze/sample.json")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "filename" in data and data["filename"] == "sample.json"
    assert "total_videos" in data and isinstance(data["total_videos"], int)
    assert "date_range" in data
    assert "cluster_count" in data
    assert "suppression_score" in data
    assert "risk_score" in data


def test_api_export_returns_json_data(tmp_path, monkeypatch):
    import sys
    import types

    class _DummyHistoryParser:
        def __init__(self, path):
            self.path = path

        def parse(self):
            return [types.SimpleNamespace(title="Video A")]

    class _DummyTrendAnalyzer:
        def analyze_trends(self, watch_history):
            return {"summary": "test_data"}

    monkeypatch.setitem(
        sys.modules,
        "rabbitmirror.parser",
        types.SimpleNamespace(HistoryParser=_DummyHistoryParser),
    )
    monkeypatch.setitem(
        sys.modules,
        "rabbitmirror.trend_analyzer",
        types.SimpleNamespace(TrendAnalyzer=_DummyTrendAnalyzer),
    )
    monkeypatch.setitem(
        sys.modules,
        "rabbitmirror.export_formatter",
        types.SimpleNamespace(ExportFormatter=lambda: None),
    )

    client, app = get_client()
    app.config["UPLOAD_FOLDER"] = str(tmp_path)

    dummy_file = tmp_path / "sample.json"
    dummy_file.write_text("{}")

    resp = client.get("/api/export/sample.json")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "summary" in data and data["summary"] == "test_data"


def test_api_analyze_missing_file_returns_404(tmp_path):
    client, app = get_client()
    app.config["UPLOAD_FOLDER"] = str(tmp_path)

    resp = client.get("/api/analyze/nonexistent.json")
    assert resp.status_code == 404
    data = resp.get_json()
    assert "error" in data and "not found" in data["error"].lower()
