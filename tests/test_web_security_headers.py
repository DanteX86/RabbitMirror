import pytest

pytest.importorskip("flask")


def get_client():
    from rabbitmirror.web.app import app

    app.testing = True
    return app.test_client(), app


def test_csp_headers_present_on_pages():
    client, _ = get_client()
    for path in ["/", "/about", "/benchmarks", "/docs"]:
        resp = client.get(path)
        assert resp.status_code == 200
        csp = resp.headers.get("Content-Security-Policy", "")
        assert "default-src 'self'" in csp
        assert "cdn.jsdelivr.net" in csp
        assert resp.headers.get("X-Content-Type-Options") == "nosniff"
        assert resp.headers.get("Referrer-Policy") == "no-referrer"
        assert resp.headers.get("X-Frame-Options") == "DENY"


def test_api_key_auth_enforced_when_configured(tmp_path, monkeypatch):
    client, app = get_client()
    app.config["UPLOAD_FOLDER"] = str(tmp_path)
    app.config["API_KEY"] = "secret123"

    # create dummy file for API read
    f = tmp_path / "sample.json"
    f.write_text("{}")

    # Missing API key
    r = client.get("/api/analyze/sample.json")
    assert r.status_code == 401

    # Wrong API key
    r2 = client.get("/api/analyze/sample.json", headers={"X-API-Key": "wrong"})
    assert r2.status_code == 401

    # Correct API key
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

    r3 = client.get("/api/analyze/sample.json", headers={"X-API-Key": "secret123"})
    assert r3.status_code == 200
