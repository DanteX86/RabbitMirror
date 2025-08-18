import logging
import os
import sys
import tempfile
import traceback
from datetime import datetime
from pathlib import Path

from flask import (
    Flask,
    abort,
    flash,
    redirect,
    render_template,
    request,
    send_file,
    session,
    url_for,
)
from loguru import logger
from werkzeug.exceptions import RequestEntityTooLarge
from werkzeug.utils import secure_filename

# Add the parent directory to the Python path to import rabbitmirror modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from functools import wraps

from sqlalchemy.exc import IntegrityError

# Import rabbitmirror modules
from rabbitmirror.adversarial_profiler import AdversarialProfiler  # noqa: E402
from rabbitmirror.cluster_engine import ClusterEngine  # noqa: E402
from rabbitmirror.database import (  # noqa: E402
    YouTubeAnalysis,
    get_db_session,
    init_database,
)
from rabbitmirror.exceptions import SecurityError, ValidationError  # noqa: E402
from rabbitmirror.export_formatter import ExportFormatter  # noqa: E402
from rabbitmirror.parser import HistoryParser  # noqa: E402
from rabbitmirror.security import (  # noqa: E402
    input_validator,
    rate_limiter,
    secret_manager,
    security_auditor,
    security_config,
)
from rabbitmirror.simple_auth import simple_auth  # noqa: E402
from rabbitmirror.suppression_index import SuppressionIndex  # noqa: E402
from rabbitmirror.trend_analyzer import TrendAnalyzer  # noqa: E402

app = Flask(__name__)


def _setup_werkzeug_logging():
    """Route Werkzeug/Flask std logging to loguru (logs/rabbitmirror.log)."""

    class LoguruHandler(logging.Handler):
        LEVEL_MAP = {
            50: "CRITICAL",
            40: "ERROR",
            30: "WARNING",
            20: "INFO",
            10: "DEBUG",
            0: "TRACE",
        }

        def emit(self, record: logging.LogRecord) -> None:
            try:
                level = self.LEVEL_MAP.get(record.levelno, "INFO")
                # Keep original caller info with depth, include exception if any
                logger.opt(depth=6, exception=record.exc_info).log(
                    level, record.getMessage()
                )
            except Exception:
                # Never raise from logging
                pass

    handler = LoguruHandler()

    # Configure Werkzeug and Flask loggers
    for name in ("werkzeug", "flask.app"):
        log = logging.getLogger(name)
        log.handlers = [
            h for h in log.handlers if not isinstance(h, logging.StreamHandler)
        ]
        log.addHandler(handler)
        log.setLevel(logging.INFO)
        log.propagate = False


# Initialize logging bridge early so server logs are captured
_setup_werkzeug_logging()

# Initialize database
init_database()
db_session = get_db_session()

# Secure configuration
app.config["UPLOAD_FOLDER"] = "static/uploads"
app.config["MAX_CONTENT_LENGTH"] = security_config.max_file_size

# Generate or validate secret key
secret_key = os.environ.get("SECRET_KEY")
if not secret_key or not secret_manager.validate_secret_key(secret_key):
    # Generate a secure key if none provided or if weak key detected
    secret_key = secret_manager.generate_secret_key()
    if not os.environ.get("SECRET_KEY"):
        print(
            "⚠️  WARNING: Using generated secret key. Set SECRET_KEY environment variable for production."
        )
        print(f"Generated key: {secret_manager.mask_secret(secret_key)}")

app.secret_key = secret_key


# Security headers middleware
@app.after_request
def add_security_headers(response):
    """Add security headers to all responses."""
    for header, value in security_config.security_headers.items():
        response.headers[header] = value
    return response


# Rate limiting helper
def get_client_ip():
    """Get client IP address for rate limiting."""
    if request.environ.get("HTTP_X_FORWARDED_FOR"):
        return request.environ["HTTP_X_FORWARDED_FOR"].split(",")[0].strip()
    return request.environ.get("REMOTE_ADDR", "unknown")


# File validation
def validate_uploaded_file(file):
    """Validate uploaded file for security."""
    if not file or not file.filename:
        raise ValidationError("No file selected", field_name="file")

    # Validate filename
    filename = input_validator.validate_filename(file.filename)

    # Check file size
    file.seek(0, 2)  # Seek to end
    size = file.tell()
    file.seek(0)  # Reset to beginning

    if size > security_config.max_file_size:
        raise ValidationError(
            f"File size ({size} bytes) exceeds maximum allowed size ({security_config.max_file_size} bytes)",
            field_name="file_size",
        )

    return filename


# Simple authentication setup for single-user mode
def require_simple_auth(f):
    """Decorator to require simple authentication."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if authentication is enabled
        if simple_auth.is_enabled():
            # Check if user is already authenticated in session
            if not session.get("authenticated"):
                return redirect(url_for("simple_login"))
        return f(*args, **kwargs)

    return decorated_function


@app.route("/", methods=["GET", "POST"])
@require_simple_auth
def upload_file():
    # Rate limiting
    client_ip = get_client_ip()
    if not rate_limiter.is_allowed(client_ip):
        security_auditor.log_security_event(
            "rate_limit_exceeded", {"client_ip": client_ip, "endpoint": "/"}
        )
        flash("Too many requests. Please try again later.")
        return render_template("index.html"), 429

    if request.method == "POST":
        try:
            # Validate file upload
            if "file" not in request.files:
                raise ValidationError("No file selected", field_name="file")

            file = request.files["file"]
            filename = validate_uploaded_file(file)

            # Validate and secure file path
            secure_path = input_validator.validate_path(
                os.path.join(app.config["UPLOAD_FOLDER"], filename)
            )

            # Ensure upload directory exists securely
            upload_dir = Path(app.config["UPLOAD_FOLDER"])
            upload_dir.mkdir(parents=True, exist_ok=True, mode=0o755)

            # Save file securely
            file.save(str(secure_path))

            security_auditor.log_security_event(
                "file_upload_success",
                {
                    "filename": filename,
                    "client_ip": client_ip,
                    "file_size": secure_path.stat().st_size,
                },
            )

            return redirect(url_for("analyze_file", filename=filename))

        except (SecurityError, ValidationError) as e:
            security_auditor.log_security_event(
                "file_upload_violation",
                {
                    "error": str(e),
                    "client_ip": client_ip,
                    "filename": getattr(file, "filename", "unknown")
                    if "file" in locals()
                    else "unknown",
                },
            )
            flash(f"Security error: {str(e)}")

        except RequestEntityTooLarge:
            # Re-raise the 413 exception to be handled by the error handler
            raise

        except Exception as e:
            security_auditor.log_security_event(
                "file_upload_error", {"error": str(e), "client_ip": client_ip}
            )
            flash(f"Upload failed: {str(e)}")

    return render_template("index.html")


# Simple authentication routes for single-user mode
@app.route("/simple_login", methods=["GET", "POST"])
def simple_login():
    if request.method == "POST":
        password = request.form.get("password", "")

        if simple_auth.verify_password(password):
            session["authenticated"] = True
            flash("Login successful!", "success")
            next_page = request.args.get("next")
            return (
                redirect(next_page) if next_page else redirect(url_for("upload_file"))
            )
        else:
            flash("Invalid password", "danger")

    return render_template("simple_login.html")


@app.route("/logout")
def logout():
    session.pop("authenticated", None)
    flash("Logged out successfully!", "success")
    return redirect(url_for("simple_login"))


@app.route("/analyze/<filename>")
@require_simple_auth
def analyze_file(filename):
    # Rate limiting
    client_ip = get_client_ip()
    if not rate_limiter.is_allowed(client_ip):
        security_auditor.log_security_event(
            "rate_limit_exceeded",
            {"client_ip": client_ip, "endpoint": f"/analyze/{filename}"},
        )
        abort(429)

    try:
        # Validate filename for security
        secure_filename_validated = input_validator.validate_filename(filename)

        # Validate and secure file path
        filepath = input_validator.validate_path(
            os.path.join(app.config["UPLOAD_FOLDER"], secure_filename_validated)
        )

        # Check if file exists
        if not filepath.exists():
            security_auditor.log_security_event(
                "file_not_found", {"filename": filename, "client_ip": client_ip}
            )
            flash("File not found")
            return redirect(url_for("upload_file"))

        # Parse the watch history file
        parser = HistoryParser(str(filepath), "youtube")
        parse_result = parser.parse()

        # Extract entries from ParserResult and validate parsed data
        validated_history = input_validator.validate_json_data(parse_result.entries)

        # Perform trend analysis
        trend_analyzer = TrendAnalyzer()
        trend_results = trend_analyzer.analyze_trends(validated_history)

        # Perform clustering
        cluster_engine = ClusterEngine()
        cluster_results = cluster_engine.cluster_videos(validated_history)
        # Extract just the clusters dict for the template
        clusters = cluster_results.get("clusters", {})

        # Calculate suppression index
        suppression_calc = SuppressionIndex()
        suppression_results = suppression_calc.calculate_suppression(validated_history)

        # Perform adversarial pattern detection
        adversarial_profiler = AdversarialProfiler()
        pattern_results = adversarial_profiler.identify_adversarial_patterns(
            validated_history
        )

        # Prepare data for visualization (sanitize output)
        # Ensure validated_history is a list before slicing
        raw_data_sample = []
        if isinstance(validated_history, list) and len(validated_history) > 0:
            raw_data_sample = validated_history[:100]  # Show first 100 entries

        analysis_data = {
            "filename": secure_filename_validated,
            "total_videos": len(validated_history)
            if isinstance(validated_history, list)
            else 0,
            "date_range": {
                "start": input_validator.validate_string(
                    str(trend_results.get("date_range", {}).get("start", "N/A"))
                ),
                "end": input_validator.validate_string(
                    str(trend_results.get("date_range", {}).get("end", "N/A"))
                ),
            },
            "trend_analysis": trend_results,
            "clusters": clusters,
            "suppression_results": suppression_results,
            "pattern_results": pattern_results,
            "raw_data": raw_data_sample,
        }

        security_auditor.log_security_event(
            "file_analysis_success",
            {
                "filename": secure_filename_validated,
                "client_ip": client_ip,
                "data_points": len(validated_history)
                if isinstance(validated_history, (list, dict))
                else 0,
            },
        )

        return render_template("analysis.html", data=analysis_data)

    except (SecurityError, ValidationError) as e:
        security_auditor.log_security_event(
            "analysis_security_violation",
            {"error": str(e), "filename": filename, "client_ip": client_ip},
        )
        flash(f"Security error: {str(e)}")
        return redirect(url_for("upload_file"))

    except Exception as e:
        security_auditor.log_security_event(
            "analysis_error",
            {"error": str(e), "filename": filename, "client_ip": client_ip},
        )
        # Don't expose internal error details
        flash("Analysis failed. Please try with a different file.")
        return redirect(url_for("upload_file"))


@app.route("/export/<filename>/<format>")
@require_simple_auth
def export_analysis(filename, format):
    try:
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)

        # Parse the watch history file
        parser = HistoryParser(filepath, "youtube")
        parse_result = parser.parse()

        # Perform analysis
        trend_analyzer = TrendAnalyzer()
        analysis_results = trend_analyzer.analyze_trends(parse_result.entries)

        # Export the results
        export_formatter = ExportFormatter()

        # Create a temporary file for export
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=f".{format}", delete=False
        ) as tmp_file:
            # The export_data method signature is (data, format, filename)
            if format == "json":
                export_formatter.export_data(analysis_results, "json", tmp_file.name)
            elif format == "csv":
                export_formatter.export_data(analysis_results, "csv", tmp_file.name)
            elif format == "yaml":
                export_formatter.export_data(analysis_results, "yaml", tmp_file.name)
            else:
                flash(f"Unsupported export format: {format}")
                return redirect(url_for("analyze_file", filename=filename))

            return send_file(
                tmp_file.name,
                as_attachment=True,
                download_name=f'analysis_{filename}_{format}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.{format}',
            )

    except Exception as e:
        error_msg = f"Error exporting analysis: {str(e)}"
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
    return "File too large. Please upload a file smaller than 100MB.", 413


@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_error(e):
    return render_template("500.html"), 500


if __name__ == "__main__":
    # Ensure upload directory exists
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    app.run(
        debug=os.getenv("FLASK_DEBUG", "False") == "True", host="127.0.0.1", port=5001
    )
