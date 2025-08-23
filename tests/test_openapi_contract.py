import json
import os

import pytest
import schemathesis as st

# Import the Flask app & in-memory OpenAPI spec
from rabbitmirror.web.app import _OPENAPI_SPEC
from rabbitmirror.web.app import app as flask_app


@pytest.fixture(scope="module")
def app():
    # Configure app for testing with no rate limiting & no API key required
    flask_app.testing = True
    flask_app.config["API_RATE_LIMIT_BYPASS"] = True
    flask_app.config["API_KEY"] = None
    yield flask_app


def test_openapi_is_well_formed():
    # Basic structural checks on the in-memory spec
    assert isinstance(_OPENAPI_SPEC, dict)
    assert _OPENAPI_SPEC.get("openapi", "").startswith("3.")
    assert "/api/healthz" in _OPENAPI_SPEC.get("paths", {})


def test_contract_with_schemathesis_wsgi(app):
    schema = st.from_wsgi("/openapi.json", app)

    # Run generated tests against the WSGI app without network I/O
    @schema.parametrize()
    def test_api(case):
        # Bypass rate limiting during contract tests
        response = case.call_wsgi(app)
        case.validate_response(response)

    # The above decorator integrates with pytest; no direct call is needed.
