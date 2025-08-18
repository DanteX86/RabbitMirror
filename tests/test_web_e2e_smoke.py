import io
import re
import types

import pytest

pytest.importorskip("flask")


def _install_dummies(monkeypatch):
    # Dummy modules used by analyze/export routes
    class _DummyHistoryParser:
        def __init__(self, path):
            self.path = path

        def parse(self):
            # return minimal list of objects with expected attrs
            return [
                types.SimpleNamespace(
                    title="Video A", watched_at="2024-01-01T00:00:00Z"
                )
            ]

    class _DummyTrendAnalyzer:
        def analyze_trends(self, watch_history):
            return {
                "date_range": {"start": "2024-01-01", "end": "2024-01-31"},
                "summary": {},
            }

    class _DummyClusterEngine:
        def cluster_videos(self, watch_history):
            return {0: watch_history[:1]}

    class _DummySuppressionIndex:
        def calculate_suppression(self, watch_history):
            return {"score": 0.0}

    class _DummyAdversarialProfiler:
        def identify_adversarial_patterns(self, watch_history):
            return types.SimpleNamespace(
                risk_score=0.1, patterns=types.SimpleNamespace(rapid_views=[])
            )

    class _DummyExportFormatter:
        def export_data(self, analysis_results, out_path: str, fmt: str):
            with open(out_path, "w", encoding="utf-8") as f:
                f.write("{}")

    import sys

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
    monkeypatch.setitem(
        sys.modules,
        "rabbitmirror.export_formatter",
        types.SimpleNamespace(ExportFormatter=_DummyExportFormatter),
    )


def get_client():
    from rabbitmirror.web.app import app

    app.testing = True
    return app.test_client(), app


def test_e2e_upload_to_analysis_and_api(tmp_path, monkeypatch):
    _install_dummies(monkeypatch)
    client, app = get_client()
    app.config["UPLOAD_FOLDER"] = str(tmp_path)

    # Minimal valid watch-history JSON (array with time + title)
    payload = b"""
    [
      {"time": "2024-01-01T00:00:00Z", "title": "A"}
    ]
    """

    # Upload via index
    resp = client.post(
        "/",
        data={"file": (io.BytesIO(payload), "watch.json")},
        content_type="multipart/form-data",
        follow_redirects=False,
    )
    assert resp.status_code in (302, 303)
    loc = resp.headers.get("Location", "")
    assert "/analyze/" in loc

    # Extract filename from redirect URL
    m = re.search(r"/analyze/([^/?#]+)", loc)
    assert m, f"could not parse filename from redirect {loc}"
    stored_name = m.group(1)

    # Analyze page renders
    page = client.get(loc)
    assert page.status_code == 200
    assert b"Analysis Results" in page.data

    # API analyze and export work
    r1 = client.get(f"/api/analyze/{stored_name}")
    assert r1.status_code == 200
    j1 = r1.get_json()
    assert j1.get("filename") == stored_name
    assert "total_videos" in j1

    r2 = client.get(f"/api/export/{stored_name}")
    assert r2.status_code == 200
    j2 = r2.get_json()
    assert isinstance(j2, dict)
