import io
import os

import pytest

pytest.importorskip("flask")


def get_client():
    from rabbitmirror.web.app import app

    app.testing = True
    return app.test_client(), app


def test_missing_file_returns_400_and_flash():
    client, _ = get_client()
    resp = client.post("/", data={}, content_type="multipart/form-data")
    assert resp.status_code == 400
    assert b"No file selected" in resp.data
    # Inline validation elements present
    assert b'data-testid="upload-error"' in resp.data
    assert (
        b'class="form-control is-invalid"' in resp.data or b'is-invalid"' in resp.data
    )


def test_upload_invalid_extension_redirects_with_flash(tmp_path):
    client, app = get_client()
    app.config["UPLOAD_FOLDER"] = str(tmp_path)

    data = {"file": (io.BytesIO(b"hello"), "not_allowed.txt")}
    resp = client.post(
        "/", data=data, content_type="multipart/form-data", follow_redirects=False
    )
    assert resp.status_code in (302, 303)
    assert resp.headers["Location"].endswith("/")


def test_upload_valid_file_redirects_to_analyze_without_following(tmp_path):
    client, app = get_client()
    app.config["UPLOAD_FOLDER"] = str(tmp_path)

    payload = b'{\n  "test": true\n}'
    data = {"file": (io.BytesIO(payload), "sample.json")}
    resp = client.post(
        "/", data=data, content_type="multipart/form-data", follow_redirects=False
    )
    # Expect a redirect to /analyze/\u003cfilename\u003e
    assert resp.status_code in (302, 303)
    assert "/analyze/" in resp.headers.get("Location", "")
    # File should be saved with a UUID name
    # Extract filename from redirect
    location = resp.headers.get("Location", "")
    uuid_name = location.rsplit("/", 1)[-1]
    assert uuid_name.endswith(".json") and len(uuid_name.split(".")[0]) == 32
    assert os.path.exists(os.path.join(str(tmp_path), uuid_name))


def test_upload_too_large_triggers_413_handler(tmp_path):
    client, app = get_client()
    app.config["UPLOAD_FOLDER"] = str(tmp_path)
    # Set a tiny MAX_CONTENT_LENGTH to trigger 413
    app.config["MAX_CONTENT_LENGTH"] = 10  # bytes

    big_payload = b"x" * 100  # 100 bytes
    data = {"file": (io.BytesIO(big_payload), "big.json")}
    resp = client.post(
        "/", data=data, content_type="multipart/form-data", follow_redirects=False
    )
    # Werkzeug should return 413, then our handler should redirect back to index
    # Depending on Flask/Werkzeug, either a 413 or a redirect (302/303) may be observed directly.
    assert resp.status_code in (302, 303, 413)
    if resp.status_code in (302, 303):
        assert resp.headers["Location"].endswith("/")


def test_magic_sniff_rejects_non_json_with_json_ext(tmp_path):
    client, app = get_client()
    app.config["UPLOAD_FOLDER"] = str(tmp_path)

    # JPEG header masquerading as .json
    fake = b"\xff\xd8\xff\xe0" + b"0" * 100
    data = {"file": (io.BytesIO(fake), "bad.json")}
    resp = client.post("/", data=data, content_type="multipart/form-data")
    assert resp.status_code == 400
    assert b"does not look like valid JSON" in resp.data
    # Inline validation elements present
    assert b'data-testid="upload-error"' in resp.data
    assert b"is-invalid" in resp.data


def test_json_schema_validation_rejects_non_takeout_structure(tmp_path):
    client, app = get_client()
    app.config["UPLOAD_FOLDER"] = str(tmp_path)

    # Valid JSON, wrong shape for Takeout watch history (object instead of array)
    bad = b'{"foo": 1}'
    resp = client.post(
        "/",
        data={"file": (io.BytesIO(bad), "data.json")},
        content_type="multipart/form-data",
    )
    assert resp.status_code == 400
    assert b"not a valid YouTube Takeout watch history" in resp.data

    # Array but missing required fields
    bad2 = b'[{"no_time": "x"}]'
    resp2 = client.post(
        "/",
        data={"file": (io.BytesIO(bad2), "data.json")},
        content_type="multipart/form-data",
    )
    assert resp2.status_code == 400
    assert b"not a valid YouTube Takeout watch history" in resp2.data


def test_json_schema_accepts_valid_takeout_and_redirects(tmp_path):
    client, app = get_client()
    app.config["UPLOAD_FOLDER"] = str(tmp_path)

    valid = b'[{"time": "2024-01-01T00:00:00Z", "title": "Watched Something"}]'
    resp = client.post(
        "/",
        data={"file": (io.BytesIO(valid), "watch-history.json")},
        content_type="multipart/form-data",
        follow_redirects=False,
    )
    assert resp.status_code in (302, 303)
    assert "/analyze/" in resp.headers.get("Location", "")


def test_json_schema_accepts_variants(tmp_path):
    client, app = get_client()
    app.config["UPLOAD_FOLDER"] = str(tmp_path)

    # Variant: entry with titleUrl only
    v1 = b'[{"time": "2024-01-01T00:00:00Z", "titleUrl": "https://youtube.com/watch?v=abc"}]'
    r1 = client.post(
        "/",
        data={"file": (io.BytesIO(v1), "watch-history.json")},
        content_type="multipart/form-data",
        follow_redirects=False,
    )
    assert r1.status_code in (302, 303)

    # Variant: entry with subtitles only (channel info), no title/titleUrl
    v2 = b'[{"time": "2024-01-02T00:00:00Z", "subtitles": [{"name": "Channel"}]}]'
    r2 = client.post(
        "/",
        data={"file": (io.BytesIO(v2), "watch-history.json")},
        content_type="multipart/form-data",
        follow_redirects=False,
    )
    assert r2.status_code in (302, 303)

    # Variant: top-level object with watchHistory array
    v3 = b'{"watchHistory": [{"time": "2024-01-03T00:00:00Z", "title": "X"}]}'
    r3 = client.post(
        "/",
        data={"file": (io.BytesIO(v3), "watch-history.json")},
        content_type="multipart/form-data",
        follow_redirects=False,
    )
    assert r3.status_code in (302, 303)


def test_magic_sniff_rejects_non_html_with_html_ext(tmp_path):
    client, app = get_client()
    app.config["UPLOAD_FOLDER"] = str(tmp_path)

    not_html = b'{"k":1}'
    data = {"file": (io.BytesIO(not_html), "bad.html")}
    resp = client.post("/", data=data, content_type="multipart/form-data")
    assert resp.status_code == 400
    assert b"does not look like valid HTML" in resp.data


def test_filename_too_long_is_rejected(tmp_path):
    client, app = get_client()
    app.config["UPLOAD_FOLDER"] = str(tmp_path)

    long_name = ("a" * 200) + ".json"
    data = {"file": (io.BytesIO(b"{}"), long_name)}
    resp = client.post("/", data=data, content_type="multipart/form-data")
    assert resp.status_code == 400
    assert b"Filename too long" in resp.data
