import pytest

pytest.importorskip("flask")


def get_client():
    from rabbitmirror.web.app import app

    app.testing = True
    return app.test_client(), app


def test_nav_has_theme_toggle_and_theme_js():
    client, _ = get_client()
    resp = client.get("/")
    assert resp.status_code == 200
    body = resp.data
    assert b'data-testid="nav-theme-toggle"' in body
    # Ensure theme.js is referenced from static
    assert b"/static/js/theme.js" in body
