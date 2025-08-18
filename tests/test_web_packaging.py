import pytest

pytest.importorskip("flask")


def test_web_templates_render_index(tmp_path):
    # Import after skip guard
    from rabbitmirror.web.app import app

    # Ensure Flask uses package templates/static
    app.testing = True
    client = app.test_client()

    # The index route should render the template
    resp = client.get("/")
    assert resp.status_code == 200
    # Look for stable markers present in the current templates
    assert b"YouTube Watch History Analyzer" in resp.data  # h2 title substring
    assert b"Upload and Analyze" in resp.data  # primary CTA button text
    assert b'id="navbarNav"' in resp.data  # stable attribute from base.html navbar


def test_web_templates_render_about(tmp_path):
    from rabbitmirror.web.app import app

    app.testing = True
    client = app.test_client()

    resp = client.get("/about")
    assert resp.status_code == 200
    assert b"About RabbitMirror" in resp.data
