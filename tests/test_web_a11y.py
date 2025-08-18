import pytest

pytest.importorskip("flask")


def get_client():
    from rabbitmirror.web.app import app

    app.testing = True
    return app.test_client(), app


def test_page_title_present_on_core_routes():
    client, _ = get_client()
    for path in ["/", "/about", "/benchmarks"]:
        resp = client.get(path)
        assert resp.status_code == 200
        assert b'data-testid="page-title"' in resp.data
