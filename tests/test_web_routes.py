import pytest

pytest.importorskip("flask")


def get_client():
    from rabbitmirror.web.app import app

    app.testing = True
    return app.test_client(), app


def test_route_smoke_get_routes():
    client, app = get_client()
    for path in ["/", "/about", "/benchmarks"]:
        resp = client.get(path)
        assert resp.status_code == 200, f"GET {path} should be 200"
        assert b'id="navbarNav"' in resp.data
        assert b'data-testid="flash-messages"' in resp.data
        assert b"RabbitMirror" in resp.data


def test_index_specific_markers():
    client, app = get_client()
    resp = client.get("/")
    assert resp.status_code == 200
    assert b'data-testid="hero-title"' in resp.data
    assert b"YouTube Watch History Analyzer" in resp.data
    assert b'data-testid="upload-button"' in resp.data


def test_static_asset_resolves():
    client, app = get_client()
    # Use url_for to build the static path
    from flask import url_for

    with app.test_request_context():
        css_url = url_for("static", filename="css/style.css")
    css_resp = client.get(css_url)
    assert css_resp.status_code == 200
