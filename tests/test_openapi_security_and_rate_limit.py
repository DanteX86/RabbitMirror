import pytest

pytest.importorskip("flask")


def get_client():
    from rabbitmirror.web.app import app

    app.testing = True
    return app.test_client(), app


def test_openapi_has_apikey_and_429_components():
    client, _ = get_client()
    resp = client.get("/openapi.json")
    assert resp.status_code == 200
    spec = resp.get_json()

    # ApiKeyAuth security scheme
    comps = spec.get("components", {})
    sec = comps.get("securitySchemes", {})
    assert "ApiKeyAuth" in sec
    apikey = sec.get("ApiKeyAuth", {})
    assert apikey.get("type") == "apiKey"
    assert apikey.get("in") == "header"
    assert apikey.get("name") == "X-API-Key"

    # 429 response component
    resps = comps.get("responses", {})
    assert "TooManyRequests" in resps
    tmr = resps["TooManyRequests"]
    assert "headers" in tmr and "Retry-After" in tmr["headers"]
    # Enforce application/problem+json with Problem schema
    problem_ref = (
        tmr.get("content", {})
        .get("application/problem+json", {})
        .get("schema", {})
        .get("$ref", "")
    )
    assert problem_ref.endswith("#/components/schemas/Problem")


def test_openapi_paths_have_security_and_429_401_404_and_200_schemas():
    client, _ = get_client()
    resp = client.get("/openapi.json")
    assert resp.status_code == 200
    spec = resp.get_json()

    paths = spec.get("paths", {})
    analyze = paths.get("/api/analyze/{filename}", {}).get("get", {})
    export = paths.get("/api/export/{filename}", {}).get("get", {})

    # Both endpoints declare security (ApiKeyAuth)
    assert any("ApiKeyAuth" in d for d in analyze.get("security", []))
    assert any("ApiKeyAuth" in d for d in export.get("security", []))

    # Both include standard error responses
    for op in (analyze, export):
        responses = op.get("responses", {})
        assert "429" in responses, "Missing 429 TooManyRequests"
        assert "401" in responses, "Missing 401 Unauthorized"
        assert "404" in responses, "Missing 404 NotFound"

    # 200 response schemas
    a_content = (
        analyze.get("responses", {})
        .get("200", {})
        .get("content", {})
        .get("application/json", {})
    )
    e_content = (
        export.get("responses", {})
        .get("200", {})
        .get("content", {})
        .get("application/json", {})
    )

    a200 = a_content.get("schema", {})
    e200 = e_content.get("schema", {})
    assert a200.get("$ref", "").endswith("#/components/schemas/AnalysisSummary")
    assert e200.get("$ref", "").endswith("#/components/schemas/AnalysisResults")

    # Inline examples exist
    assert "examples" in a_content and "sample" in a_content["examples"]
    assert "examples" in e_content and "sample" in e_content["examples"]
