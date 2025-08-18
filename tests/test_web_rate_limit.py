import pytest

pytest.importorskip("flask")


def get_client():
    from rabbitmirror.web.app import app

    app.testing = True
    return app.test_client(), app


def test_api_rate_limit_unauthenticated(tmp_path, monkeypatch):
    client, app = get_client()
    app.config["UPLOAD_FOLDER"] = str(tmp_path)
    # small limits for test
    app.config["API_RATE_LIMIT"] = 5
    app.config["API_RATE_WINDOW"] = 1  # 1 second window

    # create dummy file for API to read
    f = tmp_path / "sample.json"
    f.write_text("{}")

    # Patch dependencies to avoid heavy imports
    import sys
    import types

    class _DummyHistoryParser:
        def __init__(self, path):
            pass

        def parse(self):
            return [types.SimpleNamespace(title="V")]

    class _DummyTrendAnalyzer:
        def analyze_trends(self, wh):
            return {"date_range": {"start": "x", "end": "y"}}

    class _DummyClusterEngine:
        def cluster_videos(self, wh):
            return {0: wh}

    class _DummySuppressionIndex:
        def calculate_suppression(self, wh):
            return {"score": 0.1}

    class _DummyAdversarialProfiler:
        def identify_adversarial_patterns(self, wh):
            return types.SimpleNamespace(risk_score=0.05)

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

    # first N requests should pass
    for i in range(5):
        r = client.get("/api/analyze/sample.json")
        assert r.status_code in (200, 404)
    # next one should be rate limited
    r = client.get("/api/analyze/sample.json")
    assert r.status_code == 429
    data = r.get_json()
    assert data.get("error_code") == "rate_limited"
    assert "Retry-After" in r.headers
