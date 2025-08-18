import pytest

pytest.importorskip("flask")


def get_client():
    from rabbitmirror.web.app import app

    app.testing = True
    return app.test_client(), app


def test_healthz_returns_status_and_metrics():
    client, _ = get_client()
    resp = client.get("/healthz")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "ok"
    assert "uptime_seconds" in data and isinstance(data["uptime_seconds"], (int, float))
    assert "timestamp" in data and isinstance(data["timestamp"], str)
    assert "version" in data and isinstance(data["version"], str)


def test_version_returns_app_and_version():
    client, _ = get_client()
    resp = client.get("/version")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["app"] == "rabbitmirror"
    assert isinstance(data["version"], str) and len(data["version"]) > 0


def test_api_healthz_matches_fields():
    client, _ = get_client()
    resp = client.get("/api/healthz")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "ok"
    assert "uptime_seconds" in data
    assert "timestamp" in data
    assert "version" in data
