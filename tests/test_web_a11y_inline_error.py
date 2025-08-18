import pytest

pytest.importorskip("flask")


def get_client():
    from rabbitmirror.web.app import app

    app.testing = True
    return app.test_client(), app


def test_upload_inline_error_has_aria_describedby(tmp_path):
    client, app = get_client()
    app.config["UPLOAD_FOLDER"] = str(tmp_path)

    # Create a request that triggers an inline upload error (bad JSON magic sniff)
    import io

    fake = b"\xff\xd8\xff\xe0" + b"0" * 100  # JPEG header
    data = {"file": (io.BytesIO(fake), "bad.json")}
    resp = client.post(
        "/", data=data, content_type="multipart/form-data", follow_redirects=False
    )
    # Inline error should render directly with 400 status
    assert resp.status_code == 400
    body = resp.data
    # Error element and file input should be present
    assert b'id="upload-error"' in body
    assert b'id="historyFile"' in body
    # The input should reference the error via aria-describedby when error exists
    assert b'aria-describedby="upload-error"' in body
