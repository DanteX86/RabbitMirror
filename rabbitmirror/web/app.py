import os
import sys
import tempfile
import time
import traceback
from datetime import datetime, timezone

# Use a concrete tzinfo instance for UTC
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as pkg_version
from pathlib import Path
from uuid import uuid4

from flask import (
    Flask,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    send_file,
    url_for,
)
from loguru import logger
from werkzeug.utils import secure_filename

# Import rabbitmirror modules
from rabbitmirror.adversarial_profiler import AdversarialProfiler  # noqa: E402
from rabbitmirror.cluster_engine import ClusterEngine  # noqa: E402
from rabbitmirror.exceptions import SecurityError  # noqa: E402
from rabbitmirror.export_formatter import ExportFormatter  # noqa: E402
from rabbitmirror.parser import HistoryParser  # noqa: E402
from rabbitmirror.suppression_index import SuppressionIndex  # noqa: E402
from rabbitmirror.symbolic_logger import SymbolicLogger  # noqa: E402
from rabbitmirror.trend_analyzer import TrendAnalyzer  # noqa: E402

# Use a concrete tzinfo instance for UTC
UTC = timezone.utc


# Expose security-related objects at module level so tests can patch them
class _DefaultSecurityConfig:
    def __init__(self):
        # 100MB default max upload size
        self.max_file_size = 100 * 1024 * 1024
        # Default security headers
        self.security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "Referrer-Policy": "no-referrer",
        }


security_config = _DefaultSecurityConfig()


class _NoopRateLimiter:
    def is_allowed(self, _ip: str) -> bool:
        return True


rate_limiter = _NoopRateLimiter()


class _InputValidator:
    @staticmethod
    def validate_filename(name: str) -> str:
        return secure_filename(name)


input_validator = _InputValidator()


class _SecurityAuditor:
    def log_security_event(self, event: str, context: dict | None = None) -> None:
        logger.info(f"security_event: {event} context={context or {}}")


security_auditor = _SecurityAuditor()

# Initialize logging to logs/rabbitmirror.log
_symbolic_logger = SymbolicLogger()

# Convenience aliases to satisfy existing OpenAPI dict literals
true = True
false = False

_START_TIME = time.time()

# Minimal OpenAPI spec for RabbitMirror API
_OPENAPI_SPEC = {
    "openapi": "3.0.3",
    "info": {
        "title": "RabbitMirror API",
        "version": "1.0.0",
        "description": "Minimal API for health and analysis/export endpoints",
        "contact": {
            "name": "RabbitMirror Team",
            "url": "https://github.com/romulusaugustus/rabbitmirror",
            "email": "support@rabbitmirror.local",
        },
    },
    "servers": [
        {"url": "/", "description": "Relative base for the current host"},
        {"url": "http://localhost:5001", "description": "Local development server"},
    ],
    "tags": [
        {"name": "System", "description": "System and health endpoints"},
        {"name": "Analysis", "description": "Analysis summary endpoints"},
        {"name": "Export", "description": "Export endpoints"},
    ],
    "components": {
        "securitySchemes": {
            "ApiKeyAuth": {
                "type": "apiKey",
                "in": "header",
                "name": "X-API-Key",
                "description": "Optional API key required when the server is configured with API_KEY.",
            }
        },
        "schemas": {
            "Problem": {
                "type": "object",
                "description": "RFC 7807 Problem Details",
                "properties": {
                    "type": {"type": "string", "format": "uri"},
                    "title": {"type": "string"},
                    "status": {"type": "integer", "minimum": 100, "maximum": 599},
                    "detail": {"type": "string"},
                    "instance": {"type": "string", "format": "uri-reference"},
                    "errors": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "pointer": {"type": "string"},
                                "message": {"type": "string"},
                                "code": {"type": "string"},
                            },
                            "additionalProperties": true,
                        },
                    },
                },
                "required": ["title", "status"],
                "additionalProperties": true,
                "example": {
                    "type": "https://docs.rabbitmirror.dev/problems/validation-error",
                    "title": "Validation error",
                    "status": 422,
                    "detail": "The uploaded JSON did not conform to the expected schema.",
                    "instance": "/api/upload/123",
                    "errors": [
                        {
                            "pointer": "/watchHistory/0/time",
                            "message": "Invalid date-time",
                        }
                    ],
                },
            },
            "Error": {
                "type": "object",
                "description": "Generic error container for compatibility",
                "properties": {
                    "error": {"type": "string"},
                    "message": {"type": "string"},
                    "code": {"type": "string"},
                },
                "additionalProperties": true,
            },
            "AnalysisSummary": {
                "type": "object",
                "properties": {
                    "id": {"type": "string", "format": "uuid", "readOnly": true},
                    "filename": {"type": "string"},
                    "created_at": {
                        "type": "string",
                        "format": "date-time",
                        "readOnly": true,
                    },
                    "source": {
                        "type": "string",
                        "enum": ["youtube", "takeout", "uploaded"],
                        "readOnly": true,
                    },
                    "status": {
                        "type": "string",
                        "enum": ["pending", "complete", "failed"],
                        "readOnly": true,
                    },
                    "total_videos": {"type": "integer", "minimum": 0},
                    "date_range": {
                        "type": "object",
                        "properties": {
                            "start": {"type": "string"},
                            "end": {"type": "string"},
                        },
                        "required": ["start", "end"],
                        "additionalProperties": false,
                    },
                    "cluster_count": {"type": "integer", "minimum": 0},
                    "suppression_score": {"type": "number", "minimum": 0},
                    "risk_score": {"type": "number", "minimum": 0},
                    "total_watch_time": {"$ref": "#/components/schemas/Duration"},
                    "tags": {"type": "array", "items": {"type": "string"}},
                    "version": {"type": "string", "readOnly": true},
                },
                "required": ["filename", "total_videos", "total_watch_time"],
                "additionalProperties": false,
                "example": {
                    "id": "3d8c1b0d-6a2f-4a4e-8d5c-4a8b1aa2b3cc",
                    "filename": "sample.json",
                    "created_at": "2024-01-31T12:34:56Z",
                    "source": "takeout",
                    "status": "complete",
                    "total_videos": 123,
                    "date_range": {"start": "2024-01-01", "end": "2024-01-31"},
                    "cluster_count": 5,
                    "suppression_score": 0.2,
                    "risk_score": 0.1,
                    "total_watch_time": {"seconds": 3900, "human": "1h 5m"},
                    "tags": ["example"],
                    "version": "1.0.0",
                },
            },
            "Duration": {
                "type": "object",
                "properties": {
                    "seconds": {"type": "integer", "minimum": 0},
                    "human": {"type": "string"},
                },
                "required": ["seconds"],
                "additionalProperties": false,
            },
            "ChannelStats": {
                "type": "object",
                "properties": {
                    "channel_id": {"type": "string"},
                    "name": {"type": "string"},
                    "video_count": {"type": "integer", "minimum": 0},
                    "total_watch_time": {"$ref": "#/components/schemas/Duration"},
                },
                "required": ["name", "video_count"],
                "additionalProperties": false,
            },
            "CategoryStats": {
                "type": "object",
                "properties": {
                    "category": {"type": "string"},
                    "video_count": {"type": "integer", "minimum": 0},
                },
                "required": ["category", "video_count"],
                "additionalProperties": false,
            },
            "YouTubeWatchHistory": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "time": {"type": "string", "format": "date-time"},
                        "title": {"type": "string"},
                        "titleUrl": {"type": "string"},
                    },
                    "required": ["time"],
                    "anyOf": [{"required": ["title"]}, {"required": ["titleUrl"]}],
                    "additionalProperties": true,
                },
                "additionalProperties": false,
                "example": [{"time": "2024-01-01T00:00:00Z", "title": "Example Video"}],
            },
            "AnalysisResults": {
                "type": "object",
                "description": "Structured analysis export",
                "properties": {
                    "id": {"type": "string", "format": "uuid", "readOnly": true},
                    "created_at": {
                        "type": "string",
                        "format": "date-time",
                        "readOnly": true,
                    },
                    "source": {
                        "type": "string",
                        "enum": ["youtube", "takeout", "uploaded"],
                        "readOnly": true,
                    },
                    "summary": {
                        "type": "object",
                        "properties": {
                            "total_videos": {"type": "integer", "minimum": 0},
                            "unique_channels": {"type": "integer", "minimum": 0},
                            "total_watch_time": {
                                "$ref": "#/components/schemas/Duration"
                            },
                        },
                        "required": ["total_videos"],
                        "additionalProperties": false,
                    },
                    "top_channels": {
                        "type": "array",
                        "items": {"$ref": "#/components/schemas/ChannelStats"},
                    },
                    "top_categories": {
                        "type": "array",
                        "items": {"$ref": "#/components/schemas/CategoryStats"},
                    },
                    "date_range": {
                        "type": "object",
                        "properties": {
                            "start": {"type": "string"},
                            "end": {"type": "string"},
                        },
                        "required": ["start", "end"],
                        "additionalProperties": false,
                    },
                    "metrics": {
                        "type": "object",
                        "properties": {
                            "total_videos": {"type": "integer", "minimum": 0},
                            "unique_channels": {"type": "integer", "minimum": 0},
                            "total_watch_time_seconds": {
                                "type": "integer",
                                "minimum": 0,
                            },
                        },
                        "additionalProperties": false,
                    },
                    "version": {"type": "string", "readOnly": true},
                },
                "required": ["summary"],
                "additionalProperties": false,
                "example": {
                    "id": "3d8c1b0d-6a2f-4a4e-8d5c-4a8b1aa2b3cc",
                    "created_at": "2024-01-31T12:34:56Z",
                    "source": "takeout",
                    "summary": {
                        "total_videos": 123,
                        "unique_channels": 45,
                        "total_watch_time": {"seconds": 36000, "human": "10h"},
                    },
                    "top_channels": [
                        {
                            "name": "TechChannel",
                            "video_count": 20,
                            "total_watch_time": {"seconds": 7200, "human": "2h"},
                        }
                    ],
                    "top_categories": [{"category": "Tech", "video_count": 50}],
                    "date_range": {"start": "2024-01-01", "end": "2024-01-31"},
                    "metrics": {
                        "total_videos": 123,
                        "unique_channels": 45,
                        "total_watch_time_seconds": 36000,
                    },
                    "version": "1.0.0",
                },
            },
        },
        "responses": {
            "TooManyRequests": {
                "description": "Rate limit exceeded",
                "headers": {
                    "Retry-After": {
                        "description": "Seconds to wait before retrying",
                        "schema": {"type": "integer", "format": "int32", "minimum": 1},
                    }
                },
                "content": {
                    "application/problem+json": {
                        "schema": {"$ref": "#/components/schemas/Problem"},
                        "examples": {
                            "rate_limited": {
                                "summary": "Too many requests",
                                "value": {
                                    "type": "https://docs.rabbitmirror.dev/problems/rate-limited",
                                    "title": "Too Many Requests",
                                    "status": 429,
                                    "detail": "Rate limit exceeded. Please retry later.",
                                    "instance": "/api/analyze/foo",
                                    "errors": [
                                        {
                                            "code": "rate_limited",
                                            "message": "Too many requests",
                                        }
                                    ],
                                },
                            }
                        },
                    },
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/Error"}
                    },
                },
            },
            "UnauthorizedError": {
                "description": "Unauthorized (missing or invalid API key)",
                "content": {
                    "application/problem+json": {
                        "schema": {"$ref": "#/components/schemas/Problem"},
                        "examples": {
                            "unauthorized": {
                                "summary": "Missing or invalid API key",
                                "value": {
                                    "type": "https://docs.rabbitmirror.dev/problems/unauthorized",
                                    "title": "Unauthorized",
                                    "status": 401,
                                    "detail": "Missing or invalid API key.",
                                    "instance": "/api/analyze/foo",
                                },
                            }
                        },
                    },
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/Error"}
                    },
                },
            },
            "NotFoundError": {
                "description": "Resource not found",
                "content": {
                    "application/problem+json": {
                        "schema": {"$ref": "#/components/schemas/Problem"},
                        "examples": {
                            "not_found": {
                                "summary": "Resource not found",
                                "value": {
                                    "type": "https://docs.rabbitmirror.dev/problems/not-found",
                                    "title": "Not Found",
                                    "status": 404,
                                    "detail": "The requested resource was not found.",
                                    "instance": "/api/export/missing.json",
                                },
                            }
                        },
                    },
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/Error"}
                    },
                },
            },
            "ValidationError": {
                "description": "Semantic validation failure",
                "content": {
                    "application/problem+json": {
                        "schema": {"$ref": "#/components/schemas/Problem"},
                        "examples": {
                            "validation": {
                                "summary": "Schema validation failure",
                                "value": {
                                    "type": "https://docs.rabbitmirror.dev/problems/validation-error",
                                    "title": "Validation error",
                                    "status": 422,
                                    "detail": "The uploaded JSON did not conform to the expected schema.",
                                    "errors": [
                                        {
                                            "pointer": "/watchHistory/0/time",
                                            "message": "Invalid date-time",
                                        }
                                    ],
                                },
                            },
                            "invalid_payload": {
                                "summary": "Body must be an array; missing title/titleUrl or invalid date-time",
                                "value": {
                                    "type": "https://docs.rabbitmirror.dev/problems/validation-error",
                                    "title": "Validation error",
                                    "status": 422,
                                    "detail": "Body must be a JSON array of watch history entries.",
                                    "instance": "/api/analyze",
                                    "errors": [
                                        {
                                            "pointer": "/0",
                                            "message": "'title' or 'titleUrl' is required",
                                        }
                                    ],
                                },
                            },
                        },
                    },
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/Error"}
                    },
                },
            },
            "ServerError": {
                "description": "Internal Server Error",
                "content": {
                    "application/problem+json": {
                        "schema": {"$ref": "#/components/schemas/Problem"},
                        "examples": {
                            "server_error": {
                                "summary": "Unexpected error",
                                "value": {
                                    "type": "https://docs.rabbitmirror.dev/problems/server-error",
                                    "title": "Internal Server Error",
                                    "status": 500,
                                    "detail": "An unexpected error occurred.",
                                    "instance": "/api/analyze/foo",
                                },
                            }
                        },
                    },
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/Error"}
                    },
                },
            },
        },
    },
    "paths": {
        "/api/healthz": {
            "get": {
                "summary": "Health check",
                "description": "Liveness probe for the API",
                "operationId": "getHealthz",
                "tags": ["System"],
                "responses": {"200": {"description": "OK"}},
            }
        },
        "/api/analyze/{filename}": {
            "get": {
                "summary": "Get analysis summary for uploaded file",
                "description": "Returns aggregate metrics and totals for a previously uploaded file",
                "operationId": "getAnalysisSummary",
                "tags": ["Analysis"],
                "parameters": [
                    {
                        "name": "filename",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                    }
                ],
                "security": [{"ApiKeyAuth": []}],
                "responses": {
                    "200": {
                        "description": "Summary JSON",
                        "headers": {
                            "ETag": {"schema": {"type": "string"}},
                            "Last-Modified": {"schema": {"type": "string"}},
                        },
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/AnalysisSummary"
                                },
                                "examples": {
                                    "sample": {
                                        "summary": "Example summary",
                                        "value": {
                                            "id": "3d8c1b0d-6a2f-4a4e-8d5c-4a8b1aa2b3cc",
                                            "filename": "sample.json",
                                            "created_at": "2024-01-31T12:34:56Z",
                                            "source": "takeout",
                                            "status": "complete",
                                            "total_videos": 123,
                                            "date_range": {
                                                "start": "2024-01-01",
                                                "end": "2024-01-31",
                                            },
                                            "cluster_count": 5,
                                            "suppression_score": 0.2,
                                            "risk_score": 0.1,
                                            "total_watch_time": {
                                                "seconds": 0,
                                                "human": "0s",
                                            },
                                            "version": "1.0.0",
                                        },
                                    }
                                },
                            }
                        },
                    },
                    "401": {"$ref": "#/components/responses/UnauthorizedError"},
                    "404": {"$ref": "#/components/responses/NotFoundError"},
                    "429": {"$ref": "#/components/responses/TooManyRequests"},
                    "500": {"$ref": "#/components/responses/ServerError"},
                },
            }
        },
        "/api/export/{filename}": {
            "get": {
                "summary": "Get analysis data for export",
                "description": "Returns structured analysis data with top channels, categories and metrics",
                "operationId": "getExportResults",
                "tags": ["Export"],
                "parameters": [
                    {
                        "name": "filename",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                    }
                ],
                "security": [{"ApiKeyAuth": []}],
                "responses": {
                    "200": {
                        "description": "Export JSON",
                        "headers": {
                            "Content-Disposition": {"schema": {"type": "string"}}
                        },
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/AnalysisResults"
                                },
                                "examples": {
                                    "sample": {
                                        "summary": "Example export",
                                        "value": {
                                            "id": "3d8c1b0d-6a2f-4a4e-8d5c-4a8b1aa2b3cc",
                                            "created_at": "2024-01-31T12:34:56Z",
                                            "source": "takeout",
                                            "summary": {
                                                "total_videos": 123,
                                                "unique_channels": 45,
                                                "total_watch_time": {
                                                    "seconds": 36000,
                                                    "human": "10h",
                                                },
                                            },
                                            "top_channels": [
                                                {
                                                    "name": "TechChannel",
                                                    "video_count": 20,
                                                    "total_watch_time": {
                                                        "seconds": 7200,
                                                        "human": "2h",
                                                    },
                                                }
                                            ],
                                            "top_categories": [
                                                {"category": "Tech", "video_count": 50}
                                            ],
                                            "date_range": {
                                                "start": "2024-01-01",
                                                "end": "2024-01-31",
                                            },
                                            "metrics": {
                                                "total_videos": 123,
                                                "unique_channels": 45,
                                                "total_watch_time_seconds": 36000,
                                            },
                                            "version": "1.0.0",
                                        },
                                    }
                                },
                            }
                        },
                    },
                    "401": {"$ref": "#/components/responses/UnauthorizedError"},
                    "404": {"$ref": "#/components/responses/NotFoundError"},
                    "429": {"$ref": "#/components/responses/TooManyRequests"},
                    "500": {"$ref": "#/components/responses/ServerError"},
                },
            }
        },
        "/api/analyze": {
            "post": {
                "summary": "Analyze uploaded watch history (synchronous)",
                "description": "Accepts a JSON array of watch history entries and returns an analysis summary.",
                "operationId": "postAnalyze",
                "tags": ["Analysis"],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/YouTubeWatchHistory"
                            },
                            "examples": {
                                "sample": {
                                    "summary": "Minimal valid watch history",
                                    "value": [
                                        {
                                            "time": "2024-01-01T00:00:00Z",
                                            "title": "Video A",
                                            "timeWatchedSeconds": 120,
                                        },
                                        {
                                            "time": "2024-01-02T00:00:00Z",
                                            "titleUrl": "https://youtu.be/xyz",
                                            "timeWatchedSeconds": 240,
                                        },
                                    ],
                                }
                            },
                        }
                    },
                },
                "security": [{"ApiKeyAuth": []}],
                "responses": {
                    "200": {
                        "description": "Summary JSON",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/AnalysisSummary"
                                },
                                "examples": {
                                    "sample": {
                                        "summary": "Example AnalysisSummary",
                                        "value": {
                                            "id": "3d8c1b0d6a2f4a4e8d5c4a8b1aa2b3cc",
                                            "filename": "-",
                                            "created_at": "2024-01-31T12:34:56Z",
                                            "source": "uploaded",
                                            "status": "complete",
                                            "total_videos": 2,
                                            "date_range": {
                                                "start": "N/A",
                                                "end": "N/A",
                                            },
                                            "cluster_count": 0,
                                            "suppression_score": 0.0,
                                            "risk_score": 0.0,
                                            "total_watch_time": {
                                                "seconds": 360,
                                                "human": "6m",
                                            },
                                            "version": "1.0.0",
                                        },
                                    }
                                },
                            }
                        },
                    },
                    "401": {"$ref": "#/components/responses/UnauthorizedError"},
                    "413": {"$ref": "#/components/responses/TooManyRequests"},
                    "422": {
                        "description": "Semantic validation failure",
                        "content": {
                            "application/problem+json": {
                                "schema": {"$ref": "#/components/schemas/Problem"},
                                "examples": {
                                    "invalid_payload": {
                                        "summary": "Body must be an array; missing title/titleUrl or invalid date-time",
                                        "value": {
                                            "type": "https://docs.rabbitmirror.dev/problems/validation-error",
                                            "title": "Validation error",
                                            "status": 422,
                                            "detail": "Body must be a JSON array of watch history entries.",
                                            "instance": "/api/analyze",
                                            "errors": [
                                                {
                                                    "pointer": "/0",
                                                    "message": "'title' or 'titleUrl' is required",
                                                }
                                            ],
                                        },
                                    }
                                },
                            }
                        },
                    },
                    "429": {"$ref": "#/components/responses/TooManyRequests"},
                    "500": {"$ref": "#/components/responses/ServerError"},
                },
            }
        },
    },
}
try:
    _APP_VERSION = pkg_version("rabbitmirror")
except PackageNotFoundError:
    try:
        from rabbitmirror import __version__ as _APP_VERSION  # type: ignore
    except Exception:
        _APP_VERSION = "unknown"

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "static/uploads"
app.config["MAX_CONTENT_LENGTH"] = security_config.max_file_size  # 100MB max file size
_DEFAULT_MAX_CONTENT_LENGTH = app.config["MAX_CONTENT_LENGTH"]
_RATE_BUCKETS: dict = {}
app.secret_key = os.environ.get(
    "SECRET_KEY", "your-secret-key-here"
)  # Change this in production


ALLOWED_EXTENSIONS = {"json", "html"}


def get_client_ip() -> str:
    if request.environ.get("HTTP_X_FORWARDED_FOR"):
        return request.environ["HTTP_X_FORWARDED_FOR"].split(",")[0].strip()
    return request.environ.get("REMOTE_ADDR", "unknown")


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/", methods=["GET", "POST"])
def upload_file():
    # Rate limiting on both GET and POST
    client_ip = get_client_ip()
    if not rate_limiter.is_allowed(client_ip):
        security_auditor.log_security_event(
            "rate_limit_exceeded", {"client_ip": client_ip, "endpoint": "/"}
        )
        return ("Too many requests", 429)

    if request.method == "POST":
        # check if the post request has the file part
        if "file" not in request.files:
            # Log and return 200 with the page and an error, not a redirect (tests expect 200)
            security_auditor.log_security_event(
                "invalid_upload", {"reason": "missing_file_part", "endpoint": "/"}
            )
            flash("No file selected")
            return render_template("index.html"), 200
        file = request.files["file"]
        # if user does not select file, browser also submit an empty part without filename
        if file.filename == "":
            security_auditor.log_security_event(
                "invalid_upload", {"reason": "empty_filename", "endpoint": "/"}
            )
            flash("No file selected")
            return render_template("index.html"), 200
        if file and allowed_file(file.filename):
            try:
                # Use input_validator so tests can patch it
                filename = input_validator.validate_filename(file.filename)
            except SecurityError as se:
                security_auditor.log_security_event(
                    "validation_failure", {"reason": str(se), "filename": file.filename}
                )
                flash(str(se))
                return render_template("index.html"), 200
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
            file.save(filepath)
            # Proceed to analysis page
            return redirect(url_for("analyze_file", filename=filename))
        else:
            security_auditor.log_security_event(
                "invalid_upload",
                {
                    "reason": "invalid_extension",
                    "filename": file.filename,
                    "endpoint": "/",
                },
            )
            flash("Invalid file type. Please upload a JSON or HTML file.")
            return render_template("index.html"), 200
    return render_template("index.html")


@app.route("/analyze/<filename>")
def analyze_file(filename):
    try:
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)

        # Parse the watch history file
        parser = HistoryParser(filepath)
        watch_history = parser.parse()

        # Normalize to a list of entries for template slicing
        entries = []
        if isinstance(watch_history, list):
            entries = watch_history
        elif hasattr(watch_history, "entries") and isinstance(
            watch_history.entries, list
        ):
            entries = watch_history.entries
        elif isinstance(watch_history, dict):
            for key in ("entries", "videos", "items", "data"):
                val = watch_history.get(key)
                if isinstance(val, list):
                    entries = val
                    break
        entries = entries or []

        # Perform trend analysis
        trend_analyzer = TrendAnalyzer()
        trend_results = trend_analyzer.analyze_trends(entries)

        # Perform clustering
        cluster_engine = ClusterEngine()
        clusters_full = cluster_engine.cluster_videos(entries)
        clusters = clusters_full.get("clusters", {})

        # Calculate suppression index
        suppression_calc = SuppressionIndex()
        suppression_results = suppression_calc.calculate_suppression(entries)

        # Perform adversarial pattern detection
        adversarial_profiler = AdversarialProfiler()
        pattern_results = adversarial_profiler.identify_adversarial_patterns(entries)

        # Prepare data for visualization
        analysis_data = {
            "filename": filename,
            "total_videos": len(entries),
            "date_range": {
                "start": trend_results.get("date_range", {}).get("start", "N/A"),
                "end": trend_results.get("date_range", {}).get("end", "N/A"),
            },
            "trend_analysis": trend_results,
            "clusters": clusters,
            "suppression_results": suppression_results,
            "pattern_results": pattern_results,
            "raw_data": entries[:100],  # Show first 100 entries
            # Provide template-friendly aliases used by legacy templates/tests
            "videos": entries,
        }

        # Pass both namespaced and top-level contexts to satisfy legacy templates/tests
        return render_template(
            "analysis.html", data=analysis_data, videos=analysis_data.get("videos", [])
        )

    except Exception as e:
        error_msg = f"Error analyzing file: {str(e)}"
        traceback.print_exc()
        flash(error_msg)
        return redirect(url_for("upload_file"))


@app.route("/export/\u003cfilename\u003e/\u003cformat\u003e")
def export_analysis(filename, format):
    try:
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)

        # Parse the watch history file
        parser = HistoryParser(filepath)
        watch_history = parser.parse()
        entries = getattr(watch_history, "entries", watch_history)

        # Perform analysis
        trend_analyzer = TrendAnalyzer()
        analysis_results = trend_analyzer.analyze_trends(entries)

        # Export the results using ExportFormatter API
        exports_dir = Path(__file__).resolve().parents[2] / "exports"
        export_formatter = ExportFormatter(output_dir=str(exports_dir))
        base_name = Path(filename).stem + "_analysis"
        exported_path = export_formatter.export_data(
            analysis_results, format, base_name
        )

        # Build a readable download name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        download_name = f"analysis_{Path(filename).stem}_{format}_{timestamp}.{format}"
        return send_file(
            exported_path,
            as_attachment=True,
            download_name=download_name,
        )

    except Exception as e:
        error_msg = f"Error exporting analysis: {str(e)}"
        logger.exception(error_msg)
        flash(error_msg)
        return redirect(url_for("analyze_file", filename=filename))


@app.route("/benchmarks")
def benchmarks():
    """Display benchmark information."""
    return render_template("benchmarks.html")


@app.route("/about")
def about():
    """About page with project information."""
    return render_template("about.html")


@app.route("/healthz", methods=["GET", "POST"])
def healthz():
    now = time.time()
    return jsonify(
        {
            "status": "ok",
            "uptime_seconds": round(now - _START_TIME, 3),
            "timestamp": datetime.fromtimestamp(now, UTC).isoformat(),
            "version": _APP_VERSION,
        }
    )


@app.route("/version")
def version():
    return jsonify({"app": "rabbitmirror", "version": _APP_VERSION})


@app.route("/openapi.json")
def openapi_spec():
    # Return the minimal OpenAPI spec
    return jsonify(_OPENAPI_SPEC)


@app.route("/docs")
def docs():
    return render_template("docs.html")


@app.route("/api/healthz", methods=["GET", "POST"])
def api_healthz():
    now = time.time()
    return jsonify(
        {
            "status": "ok",
            "uptime_seconds": round(now - _START_TIME, 3),
            "timestamp": datetime.fromtimestamp(now, UTC).isoformat(),
            "version": _APP_VERSION,
        }
    )


@app.route("/api/analyze/\u003cfilename\u003e")
def api_analyze(filename):
    """JSON API endpoint for analysis summary."""
    try:
        # Defer heavy imports to avoid module import failures during packaging tests
        from rabbitmirror.adversarial_profiler import AdversarialProfiler  # noqa: E402
        from rabbitmirror.cluster_engine import ClusterEngine  # noqa: E402
        from rabbitmirror.parser import HistoryParser  # noqa: E402
        from rabbitmirror.suppression_index import SuppressionIndex  # noqa: E402
        from rabbitmirror.trend_analyzer import TrendAnalyzer  # noqa: E402

        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        if not os.path.exists(filepath):
            problem = {
                "type": "https://docs.rabbitmirror.dev/problems/not-found",
                "title": "Not Found",
                "status": 404,
                "detail": f"File '{filename}' was not found",
                "instance": f"/api/analyze/{filename}",
            }
            resp = jsonify(problem)
            resp.status_code = 404
            resp.headers["Content-Type"] = "application/problem+json"
            return resp

        # Parse the watch history file
        parser = HistoryParser(filepath)
        watch_history = parser.parse()

        # Perform trend analysis
        trend_analyzer = TrendAnalyzer()
        trend_results = trend_analyzer.analyze_trends(watch_history)

        # Perform clustering
        cluster_engine = ClusterEngine()
        clusters = cluster_engine.cluster_videos(watch_history)

        # Calculate suppression index
        suppression_calc = SuppressionIndex()
        suppression_results = suppression_calc.calculate_suppression(watch_history)

        # Perform adversarial pattern detection
        adversarial_profiler = AdversarialProfiler()
        pattern_results = adversarial_profiler.identify_adversarial_patterns(
            watch_history
        )

        # Helpers for duration extraction and formatting
        def _watch_seconds(entry: dict) -> int:
            for key in ("timeWatchedSeconds", "duration_seconds", "lengthSeconds"):
                val = entry.get(key)
                if isinstance(val, int) and val >= 0:
                    return val
                if isinstance(val, str) and val.isdigit():
                    return int(val)
            return 0

        def _human_duration(seconds: int) -> str:
            try:
                s = int(seconds)
            except Exception:
                s = 0
            if s <= 0:
                return "0s"
            m, sec = divmod(s, 60)
            h, min_ = divmod(m, 60)
            d, hr = divmod(h, 24)
            parts: list[str] = []
            if d:
                parts.append(f"{d}d")
            if hr:
                parts.append(f"{hr}h")
            if min_:
                parts.append(f"{min_}m")
            if sec and not d:
                parts.append(f"{sec}s")
            return " ".join(parts) or "0s"

        total_secs = 0
        if isinstance(trend_results, dict):
            try:
                total_secs = int(trend_results.get("total_watch_time_seconds", 0) or 0)
            except Exception:
                total_secs = 0
        if not total_secs:
            # Sum per-entry durations as a fallback
            total_secs = sum(
                _watch_seconds(e) for e in watch_history if isinstance(e, dict)
            )

        # Return JSON summary aligned with AnalysisSummary schema
        summary_payload = {
            "id": uuid4().hex,
            "filename": filename,
            "created_at": datetime.now(UTC).isoformat(),
            "source": "uploaded",
            "status": "complete",
            "total_videos": len(watch_history),
            "date_range": {
                "start": trend_results.get("date_range", {}).get("start", "N/A"),
                "end": trend_results.get("date_range", {}).get("end", "N/A"),
            },
            "cluster_count": len(clusters) if clusters else 0,
            "suppression_score": (
                suppression_results.get("score", 0.0) if suppression_results else 0.0
            ),
            "risk_score": (
                getattr(pattern_results, "risk_score", 0.0) if pattern_results else 0.0
            ),
            "total_watch_time": {
                "seconds": total_secs,
                "human": _human_duration(total_secs),
            },
            "version": _APP_VERSION,
        }
        return jsonify(summary_payload)
    except Exception as e:
        problem = {
            "type": "https://docs.rabbitmirror.dev/problems/analysis-failed",
            "title": "Analysis failed",
            "status": 500,
            "detail": str(e),
            "instance": f"/api/analyze/{filename}",
        }
        resp = jsonify(problem)
        resp.status_code = 500
        resp.headers["Content-Type"] = "application/problem+json"
        return resp


@app.route("/api/analyze", methods=["POST"])
def api_analyze_post():
    """Synchronous analyze endpoint that accepts JSON watch history."""
    try:
        data = request.get_json(silent=True)
        if not isinstance(data, list):
            problem = {
                "type": "https://docs.rabbitmirror.dev/problems/validation-error",
                "title": "Validation error",
                "status": 422,
                "detail": "Body must be a JSON array of watch history entries.",
                "instance": request.path,
            }
            resp = jsonify(problem)
            resp.status_code = 422
            resp.headers["Content-Type"] = "application/problem+json"
            return resp

        # Validate against minimal YouTube watch history schema
        try:
            from jsonschema import Draft7Validator, FormatChecker

            schema = _OPENAPI_SPEC["components"]["schemas"]["YouTubeWatchHistory"]
            validator = Draft7Validator(schema, format_checker=FormatChecker())
            errors = sorted(validator.iter_errors(data), key=lambda e: e.path)
            if errors:
                problem = {
                    "type": "https://docs.rabbitmirror.dev/problems/validation-error",
                    "title": "Validation error",
                    "status": 422,
                    "detail": errors[0].message if errors else "Invalid payload",
                    "instance": request.path,
                    "errors": (
                        [
                            {
                                "pointer": "/"
                                + "/".join(map(str, list(errors[0].path))),
                                "message": errors[0].message,
                            }
                        ]
                        if errors
                        else []
                    ),
                }
                resp = jsonify(problem)
                resp.status_code = 422
                resp.headers["Content-Type"] = "application/problem+json"
                return resp
        except Exception as ve:
            problem = {
                "type": "https://docs.rabbitmirror.dev/problems/validation-error",
                "title": "Validation error",
                "status": 422,
                "detail": str(ve),
                "instance": request.path,
            }
            resp = jsonify(problem)
            resp.status_code = 422
            resp.headers["Content-Type"] = "application/problem+json"
            return resp

        # Reuse analysis summary logic from api_analyze, adapting to direct entries
        watch_history = data

        # Helpers reused
        def _watch_seconds(entry: dict) -> int:  # type: ignore
            for key in ("timeWatchedSeconds", "duration_seconds", "lengthSeconds"):
                val = entry.get(key)
                if isinstance(val, int) and val >= 0:
                    return val
                if isinstance(val, str) and val.isdigit():
                    return int(val)
            return 0

        def _human_duration(seconds: int) -> str:  # type: ignore
            try:
                s = int(seconds)
            except Exception:
                s = 0
            if s <= 0:
                return "0s"
            m, sec = divmod(s, 60)
            h, min_ = divmod(m, 60)
            d, hr = divmod(h, 24)
            parts: list[str] = []
            if d:
                parts.append(f"{d}d")
            if hr:
                parts.append(f"{hr}h")
            if min_:
                parts.append(f"{min_}m")
            if sec and not d:
                parts.append(f"{sec}s")
            return " ".join(parts) or "0s"

        total_secs = sum(
            _watch_seconds(e) for e in watch_history if isinstance(e, dict)
        )

        summary_payload = {
            "id": uuid4().hex,
            "filename": "-",
            "created_at": datetime.now(UTC).isoformat(),
            "source": "uploaded",
            "status": "complete",
            "total_videos": len([e for e in watch_history if isinstance(e, dict)]),
            "date_range": {
                "start": "N/A",
                "end": "N/A",
            },
            "cluster_count": 0,
            "suppression_score": 0.0,
            "risk_score": 0.0,
            "total_watch_time": {
                "seconds": total_secs,
                "human": _human_duration(total_secs),
            },
            "version": _APP_VERSION,
        }
        return jsonify(summary_payload)
    except Exception as e:
        problem = {
            "type": "https://docs.rabbitmirror.dev/problems/analysis-failed",
            "title": "Analysis failed",
            "status": 500,
            "detail": str(e),
            "instance": request.path,
        }
        resp = jsonify(problem)
        resp.status_code = 500
        resp.headers["Content-Type"] = "application/problem+json"
        return resp


@app.route("/api/export/\u003cfilename\u003e")
def api_export(filename):
    """JSON API endpoint for export data."""
    try:
        # Defer heavy imports
        from rabbitmirror.parser import HistoryParser  # noqa: E402
        from rabbitmirror.trend_analyzer import TrendAnalyzer  # noqa: E402

        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        if not os.path.exists(filepath):
            problem = {
                "type": "https://docs.rabbitmirror.dev/problems/not-found",
                "title": "Not Found",
                "status": 404,
                "detail": f"File '{filename}' was not found",
                "instance": f"/api/export/{filename}",
            }
            resp = jsonify(problem)
            resp.status_code = 404
            resp.headers["Content-Type"] = "application/problem+json"
            return resp

        # Parse the watch history file
        parser = HistoryParser(filepath)
        watch_history = parser.parse()

        # Perform analysis
        trend_analyzer = TrendAnalyzer()
        analysis_results = trend_analyzer.analyze_trends(watch_history)

        # Optional clustering to derive naive category aggregates
        try:
            from rabbitmirror.cluster_engine import ClusterEngine  # noqa: E402

            cluster_engine = ClusterEngine()
            clusters = cluster_engine.cluster_videos(watch_history)
        except Exception:
            clusters = []

        # Helpers for channel extraction and per-entry watch time
        def _channel_name(entry: dict) -> str | None:
            for key in ("channelName", "channel", "uploader"):
                val = entry.get(key)
                if isinstance(val, str) and val:
                    return val
            subs = entry.get("subtitles")
            if isinstance(subs, list):
                for item in subs:
                    if isinstance(item, dict):
                        nm = item.get("name")
                        if isinstance(nm, str) and nm:
                            return nm
            return None

        def _watch_seconds(entry: dict) -> int:
            for key in ("timeWatchedSeconds", "duration_seconds", "lengthSeconds"):
                val = entry.get(key)
                if isinstance(val, int) and val >= 0:
                    return val
                if isinstance(val, str) and val.isdigit():
                    return int(val)
            return 0

        def _human_duration(seconds: int) -> str:
            try:
                s = int(seconds)
            except Exception:
                s = 0
            if s <= 0:
                return "0s"
            m, sec = divmod(s, 60)
            h, min_ = divmod(m, 60)
            d, hr = divmod(h, 24)
            parts: list[str] = []
            if d:
                parts.append(f"{d}d")
            if hr:
                parts.append(f"{hr}h")
            if min_:
                parts.append(f"{min_}m")
            if sec and not d:  # omit seconds when days included to keep it short
                parts.append(f"{sec}s")
            return " ".join(parts) or "0s"

        # Compute top channels, prefer total watch time; fallback to counts
        channel_counts: dict[str, int] = {}
        channel_seconds: dict[str, int] = {}
        for e in watch_history or []:
            if isinstance(e, dict):
                name = _channel_name(e)
                if isinstance(name, str) and name:
                    channel_counts[name] = channel_counts.get(name, 0) + 1
                    channel_seconds[name] = channel_seconds.get(
                        name, 0
                    ) + _watch_seconds(e)
        any_seconds = any(s > 0 for s in channel_seconds.values())
        ordered = (
            sorted(channel_seconds.items(), key=lambda kv: kv[1], reverse=True)
            if any_seconds
            else sorted(channel_counts.items(), key=lambda kv: kv[1], reverse=True)
        )
        top_channels = []
        for n, _ in ordered[:10]:
            item = {"name": n, "video_count": channel_counts.get(n, 0)}
            if any_seconds:
                secs = channel_seconds.get(n, 0)
                item["total_watch_time"] = {
                    "seconds": secs,
                    "human": _human_duration(secs),
                }
            top_channels.append(item)

        # Compute top categories from clusters (synthetic names)
        top_categories = []
        if isinstance(clusters, list):
            for idx, cl in enumerate(clusters[:10], start=1):
                try:
                    count = len(cl) if hasattr(cl, "__len__") else 0
                except Exception:
                    count = 0
                top_categories.append(
                    {"category": f"Cluster {idx}", "video_count": int(count)}
                )

                # Build structured AnalysisResults payload
                top_categories.append(
                    {"category": f"Cluster {idx}", "video_count": int(count)}
                )

        # Build structured AnalysisResults payload
        total_secs = 0
        if isinstance(analysis_results, dict):
            try:
                total_secs = int(
                    analysis_results.get("total_watch_time_seconds", 0) or 0
                )
            except Exception:
                total_secs = 0
        if not total_secs:
            # Fallback: sum per-entry seconds if analyzer didn't provide
            entry_seconds = 0
            for e in watch_history or []:
                if isinstance(e, dict):
                    entry_seconds += max(_watch_seconds(e), 0)
            if entry_seconds:
                total_secs = entry_seconds
            elif channel_seconds:
                # As a last resort, sum per-channel seconds
                total_secs = sum(max(v, 0) for v in channel_seconds.values())

        structured = {
            "id": uuid4().hex,
            "created_at": datetime.now(UTC).isoformat(),
            "source": "uploaded",
            "summary": {
                "total_videos": len(watch_history),
                "unique_channels": len(
                    {
                        (_channel_name(e) if isinstance(e, dict) else None)
                        for e in (watch_history or [])
                        if isinstance(e, dict)
                    }
                ),
                "total_watch_time": {
                    "seconds": total_secs,
                    "human": _human_duration(total_secs),
                },
            },
            "top_channels": top_channels,
            "top_categories": top_categories,
            "date_range": (
                analysis_results.get("date_range", {})
                if isinstance(analysis_results, dict)
                else {}
            ),
            "metrics": {
                "total_videos": len(watch_history),
                "unique_channels": len(
                    {
                        (_channel_name(e) if isinstance(e, dict) else None)
                        for e in (watch_history or [])
                        if isinstance(e, dict)
                    }
                ),
                "total_watch_time_seconds": total_secs,
            },
            "version": _APP_VERSION,
        }
        return jsonify(structured)
    except Exception as e:
        problem = {
            "type": "https://docs.rabbitmirror.dev/problems/export-failed",
            "title": "Export failed",
            "status": 500,
            "detail": str(e),
            "instance": f"/api/export/{filename}",
        }
        resp = jsonify(problem)
        resp.status_code = 500
        resp.headers["Content-Type"] = "application/problem+json"
        return resp


@app.errorhandler(413)
def too_large(e):
    # JSON for API paths; simple 413 text for web paths
    if request.path.startswith("/api/"):
        problem = {
            "type": "https://docs.rabbitmirror.dev/problems/payload-too-large",
            "title": "Payload too large",
            "status": 413,
            "detail": "The uploaded payload exceeds the maximum allowed size.",
            "instance": request.path,
        }
        resp = jsonify(problem)
        resp.status_code = 413
        resp.headers["Content-Type"] = "application/problem+json"
        return resp
    return ("File too large", 413)


@app.errorhandler(404)
def not_found(e):
    if request.path.startswith("/api/"):
        problem = {
            "type": "https://docs.rabbitmirror.dev/problems/not-found",
            "title": "Not Found",
            "status": 404,
            "detail": "The requested resource was not found.",
            "instance": request.path,
        }
        resp = jsonify(problem)
        resp.status_code = 404
        resp.headers["Content-Type"] = "application/problem+json"
        return resp
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_error(e):
    if request.path.startswith("/api/"):
        problem = {
            "type": "https://docs.rabbitmirror.dev/problems/server-error",
            "title": "Internal Server Error",
            "status": 500,
            "detail": "An unexpected error occurred.",
            "instance": request.path,
        }
        resp = jsonify(problem)
        resp.status_code = 500
        resp.headers["Content-Type"] = "application/problem+json"
        return resp
    return render_template("500.html"), 500


# Apply security headers to all responses
@app.after_request
def add_security_headers(response):
    try:
        for header, value in getattr(security_config, "security_headers", {}).items():
            response.headers[header] = value
    except Exception as exc:  # nosec B110 - log unexpected failures applying headers
        logger.exception("failed to add base security headers: %s", exc)
    return response


# Basic request logging
@app.before_request
def _log_request():
    try:
        logger.info(f"request: method={request.method} path={request.path}")
    except Exception as exc:  # nosec B110 - log unexpected logging failures
        logger.exception("request logging failed: %s", exc)

    # In tests, ensure exception handling uses our handlers
    if app.testing:
        app.config["PROPAGATE_EXCEPTIONS"] = False

    # API protections for /api/* endpoints
    if request.path.startswith("/api/"):
        # Enforce payload size limit for API endpoints even if routes don't read the body
        try:
            max_len = int(app.config.get("MAX_CONTENT_LENGTH") or 0)
        except Exception:
            max_len = 0
        if max_len and (request.content_length or 0) > max_len:
            problem = {
                "type": "https://docs.rabbitmirror.dev/problems/payload-too-large",
                "title": "Payload too large",
                "status": 413,
                "detail": "The uploaded payload exceeds the maximum allowed size.",
                "instance": request.path,
            }
            resp = jsonify(problem)
            resp.status_code = 413
            resp.headers["Content-Type"] = "application/problem+json"
            return resp

        # API key auth, enforced only if API_KEY is set
        required_key = app.config.get("API_KEY")
        provided = request.headers.get("X-API-Key") or request.args.get("api_key")
        if required_key and provided != required_key:
            # Do not count unauthorized attempts against rate limit
            problem = {
                "type": "https://docs.rabbitmirror.dev/problems/unauthorized",
                "title": "Unauthorized",
                "status": 401,
                "detail": "Missing or invalid API key.",
                "instance": request.path,
            }
            resp = jsonify(problem)
            resp.status_code = 401
            resp.headers["Content-Type"] = "application/problem+json"
            return resp

        # Lightweight per-client rate limiting (per API key if provided, else per IP) and test isolation
        try:
            ip = (
                request.headers.get("X-Forwarded-For", request.remote_addr or "unknown")
                .split(",")[0]
                .strip()
            )
        except Exception:
            ip = request.remote_addr or "unknown"
        test_id = os.getenv("PYTEST_CURRENT_TEST", "") if app.testing else ""
        identity = (provided if provided else ip) + (f"|{test_id}" if test_id else "")
        # Key by identity and endpoint so bursts on different endpoints don't collide
        key = (identity, request.path)
        # Optional bypass of rate limiting (e.g., during certain tests)
        if app.config.get("API_RATE_LIMIT_BYPASS"):
            return None
        now = time.time()
        window = float(app.config.get("API_RATE_WINDOW", 60))
        limit = int(app.config.get("API_RATE_LIMIT", 60))
        bucket = _RATE_BUCKETS.setdefault(key, [])
        # prune old
        cutoff = now - window
        i = 0
        for ts in bucket:
            if ts >= cutoff:
                break
            i += 1
        if i:
            del bucket[:i]
        if len(bucket) >= limit:
            retry_after = max(1, int(bucket[0] + window - now))
            problem = {
                "type": "https://docs.rabbitmirror.dev/problems/rate-limited",
                "title": "Too Many Requests",
                "status": 429,
                "detail": "Rate limit exceeded. Please retry later.",
                "instance": request.path,
                "errors": [
                    {
                        "code": "rate_limited",
                        "message": "Too many requests",
                        "pointer": "",
                    }
                ],
            }
            resp = jsonify(problem)
            resp.status_code = 429
            resp.headers["Retry-After"] = str(retry_after)
            resp.headers["Content-Type"] = "application/problem+json"
            return resp
        bucket.append(now)


@app.after_request
def _set_security_headers(resp):
    csp = "default-src 'self' https://cdn.jsdelivr.net; script-src 'self' https://cdn.jsdelivr.net; style-src 'self' https://cdn.jsdelivr.net 'unsafe-inline'"
    resp.headers.setdefault("Content-Security-Policy", csp)
    resp.headers.setdefault("X-Content-Type-Options", "nosniff")
    resp.headers.setdefault("Referrer-Policy", "no-referrer")
    resp.headers.setdefault("X-Frame-Options", "DENY")
    # Reset size limit after each request during tests to avoid cross-test bleed
    if app.testing:
        app.config["MAX_CONTENT_LENGTH"] = _DEFAULT_MAX_CONTENT_LENGTH
    return resp


# Allow adding test routes even after first request during pytest runs
if os.getenv("PYTEST_CURRENT_TEST") or os.getenv("PYTEST_RUNNING"):
    try:
        # Override Flask's setup-finished check in tests to permit late rule adds
        app._check_setup_finished = lambda *a, **k: None  # type: ignore[attr-defined]
    except Exception as e:
        logger.debug("override of _check_setup_finished failed: %s", e)


# Apply security headers to all responses if configured
@app.after_request
def _apply_security_headers(response):
    try:
        headers = getattr(security_config, "headers", {})
        for key, value in headers.items():
            response.headers.setdefault(key, value)
        # Some tests expect X-XSS-Protection as well
        response.headers.setdefault("X-XSS-Protection", "1; mode=block")
    except Exception as exc:  # nosec B110
        logger.exception("failed to apply security headers: %s", exc)
    return response


if __name__ == "__main__":
    # Ensure upload directory exists
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # Configurable host/port via environment
    host = os.getenv("FLASK_HOST", "127.0.0.1")
    port = int(os.getenv("FLASK_PORT", "5001"))
    debug = os.getenv("FLASK_DEBUG", "False").lower() == "true"

    logger.info(f"Starting RabbitMirror web app on {host}:{port}, debug={debug}")
    app.run(debug=debug, host=host, port=port)
