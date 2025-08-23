import json

import pytest

pytest.importorskip("flask")


def get_client():
    from rabbitmirror.web.app import app

    app.testing = True
    app.config["API_RATE_LIMIT_BYPASS"] = True
    return app.test_client(), app


def test_post_analyze_valid_payload_returns_summary():
    client, app = get_client()
    payload = [
        {"time": "2024-01-01T00:00:00Z", "title": "Video A", "timeWatchedSeconds": 120},
        {
            "time": "2024-01-02T00:00:00Z",
            "titleUrl": "https://youtu.be/xyz",
            "timeWatchedSeconds": 240,
        },
    ]
    resp = client.post(
        "/api/analyze", data=json.dumps(payload), content_type="application/json"
    )
    assert resp.status_code == 200
    data = resp.get_json()
    # Verify required AnalysisSummary shape
    assert set(
        [
            "id",
            "filename",
            "created_at",
            "source",
            "status",
            "total_videos",
            "date_range",
            "cluster_count",
            "suppression_score",
            "risk_score",
            "total_watch_time",
            "version",
        ]
    ).issubset(data.keys())
    assert data["total_videos"] == 2
    assert data["total_watch_time"]["seconds"] == 360


def test_post_analyze_invalid_schema_returns_422_problem():
    client, app = get_client()
    # Missing any of title/titleUrl in the first object
    payload = [
        {"time": "2024-01-01T00:00:00Z"},
        {"time": "invalid-date", "title": "Video B"},
    ]
    resp = client.post(
        "/api/analyze", data=json.dumps(payload), content_type="application/json"
    )
    assert resp.status_code == 422
    problem = resp.get_json()
    assert problem.get("title") == "Validation error"
    assert problem.get("status") == 422
    assert resp.headers.get("Content-Type") == "application/problem+json"
