import pytest

pytest.importorskip("flask")


def get_client():
    from rabbitmirror.web.app import app

    app.testing = True
    return app.test_client(), app


def test_404_renders_template():
    client, _ = get_client()
    resp = client.get("/__nope__")
    assert resp.status_code == 404
    assert b'id="main-content"' in resp.data


def test_500_renders_template():
    client, app = get_client()

    # Add a test-only route that raises an error
    def boom():  # pragma: no cover - intentional error route
        raise RuntimeError("boom")

    app.add_url_rule("/__boom__", view_func=boom)

    resp = client.get("/__boom__")
    assert resp.status_code == 500
    assert b'id="main-content"' in resp.data
