import pytest

pytest.importorskip("flask")


def get_client():
    from rabbitmirror.web.app import app

    app.testing = True
    return app.test_client(), app


def test_skip_link_present_and_targets_main():
    client, _ = get_client()
    resp = client.get("/")
    assert resp.status_code == 200
    body = resp.data
    assert b'data-testid="skip-link"' in body
    assert b'href="#main-content"' in body
