import os
import sys
import types

import pytest

pytest.importorskip("flask")


class _DummyHistoryParser:
    def __init__(self, path: str):
        self.path = path

    def parse(self):
        # minimal watch history entries
        return [
            types.SimpleNamespace(title="Video A", watched_at="2024-01-01T00:00:00Z"),
            types.SimpleNamespace(title="Video B", watched_at="2024-01-02T00:00:00Z"),
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


def _install_dummies(monkeypatch):
    # Create dummy modules to satisfy imports inside route handlers
    dummy_parser_mod = types.SimpleNamespace(HistoryParser=_DummyHistoryParser)
    dummy_trend_mod = types.SimpleNamespace(TrendAnalyzer=_DummyTrendAnalyzer)
    dummy_cluster_mod = types.SimpleNamespace(ClusterEngine=_DummyClusterEngine)
    dummy_suppression_mod = types.SimpleNamespace(
        SuppressionIndex=_DummySuppressionIndex
    )
    dummy_adv_mod = types.SimpleNamespace(AdversarialProfiler=_DummyAdversarialProfiler)
    dummy_export_mod = types.SimpleNamespace(ExportFormatter=_DummyExportFormatter)

    monkeypatch.setitem(sys.modules, "rabbitmirror.parser", dummy_parser_mod)
    monkeypatch.setitem(sys.modules, "rabbitmirror.trend_analyzer", dummy_trend_mod)
    monkeypatch.setitem(sys.modules, "rabbitmirror.cluster_engine", dummy_cluster_mod)
    monkeypatch.setitem(
        sys.modules, "rabbitmirror.suppression_index", dummy_suppression_mod
    )
    monkeypatch.setitem(sys.modules, "rabbitmirror.adversarial_profiler", dummy_adv_mod)
    monkeypatch.setitem(sys.modules, "rabbitmirror.export_formatter", dummy_export_mod)


def get_client():
    from rabbitmirror.web.app import app

    app.testing = True
    return app.test_client(), app


def test_analyze_route_renders_with_dummies(tmp_path, monkeypatch):
    _install_dummies(monkeypatch)
    client, app = get_client()

    # Ensure upload folder and sample file exist
    app.config["UPLOAD_FOLDER"] = str(tmp_path)
    sample_path = os.path.join(str(tmp_path), "sample.json")
    with open(sample_path, "wb") as f:
        f.write(b"{}")

    resp = client.get("/analyze/sample.json")
    assert resp.status_code == 200
    assert b"Analysis Results" in resp.data


@pytest.mark.parametrize("fmt", ["json", "csv", "yaml"])
def test_export_route_downloads_with_dummies(tmp_path, monkeypatch, fmt):
    _install_dummies(monkeypatch)
    client, app = get_client()

    app.config["UPLOAD_FOLDER"] = str(tmp_path)
    sample_path = os.path.join(str(tmp_path), "sample.json")
    with open(sample_path, "wb") as f:
        f.write(b"{}")

    resp = client.get(f"/export/sample.json/{fmt}", follow_redirects=False)
    assert resp.status_code == 200
    cd = resp.headers.get("Content-Disposition", "")
    assert "attachment" in cd and f"analysis_sample.json_{fmt}_" in cd
