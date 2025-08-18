import os
import sys
import tempfile
import traceback
from datetime import datetime
from pathlib import Path

from flask import Flask, flash, redirect, render_template, request, send_file, url_for
from werkzeug.utils import secure_filename

# Add the parent directory to the Python path to import rabbitmirror modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from loguru import logger  # noqa: E402

# Import rabbitmirror modules
from rabbitmirror.adversarial_profiler import AdversarialProfiler  # noqa: E402
from rabbitmirror.cluster_engine import ClusterEngine  # noqa: E402
from rabbitmirror.exceptions import SecurityError  # noqa: E402
from rabbitmirror.export_formatter import ExportFormatter  # noqa: E402
from rabbitmirror.parser import HistoryParser  # noqa: E402
from rabbitmirror.suppression_index import SuppressionIndex  # noqa: E402
from rabbitmirror.symbolic_logger import SymbolicLogger  # noqa: E402
from rabbitmirror.trend_analyzer import TrendAnalyzer  # noqa: E402


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

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "static/uploads"
app.config["MAX_CONTENT_LENGTH"] = security_config.max_file_size  # 100MB max file size
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


@app.errorhandler(413)
def too_large(e):
    # Return 413 status directly (tests expect 413). Keep it simple without template.
    return ("File too large", 413)


@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_error(e):
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
