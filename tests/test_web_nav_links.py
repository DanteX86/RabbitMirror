import pytest

pytest.importorskip("flask")


def get_client():
    from rabbitmirror.web.app import app

    app.testing = True
    return app.test_client(), app


def test_footer_has_health_and_version_links():
    client, _ = get_client()
    resp = client.get("/")
    assert resp.status_code == 200
    body = resp.data
    assert b'data-testid="link-healthz"' in body
    assert b'data-testid="link-version"' in body
    assert b'data-testid="link-openapi"' in body


def test_navbar_has_status_dropdown_with_health_version():
    client, _ = get_client()
    resp = client.get("/")
    assert resp.status_code == 200
    body = resp.data
    assert b'data-testid="nav-status-dropdown"' in body
    assert b'data-testid="nav-healthz"' in body
    assert b'data-testid="nav-version"' in body


def test_navbar_has_docs_link():
    client, _ = get_client()
    resp = client.get("/")
    assert resp.status_code == 200
    assert b'data-testid="nav-docs"' in resp.data
