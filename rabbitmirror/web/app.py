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

# Import rabbitmirror modules
from rabbitmirror.adversarial_profiler import AdversarialProfiler  # noqa: E402
from rabbitmirror.cluster_engine import ClusterEngine  # noqa: E402
from rabbitmirror.export_formatter import ExportFormatter  # noqa: E402
from rabbitmirror.parser import HistoryParser  # noqa: E402
from rabbitmirror.suppression_index import SuppressionIndex  # noqa: E402
from rabbitmirror.trend_analyzer import TrendAnalyzer  # noqa: E402

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "static/uploads"
app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024  # 100MB max file size
app.secret_key = os.environ.get(
    "SECRET_KEY", "your-secret-key-here"
)  # Change this in production

ALLOWED_EXTENSIONS = {"json", "html"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        # check if the post request has the file part
        if "file" not in request.files:
            flash("No file selected")
            return redirect(request.url)
        file = request.files["file"]
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == "":
            flash("No file selected")
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(filepath)
            return redirect(url_for("analyze_file", filename=filename))
        else:
            flash("Invalid file type. Please upload a JSON or HTML file.")
    return render_template("index.html")


@app.route("/analyze/<filename>")
def analyze_file(filename):
    try:
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)

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
        pattern_results = adversarial_profiler.identify_patterns(watch_history)

        # Prepare data for visualization
        analysis_data = {
            "filename": filename,
            "total_videos": len(watch_history),
            "date_range": {
                "start": trend_results.get("date_range", {}).get("start", "N/A"),
                "end": trend_results.get("date_range", {}).get("end", "N/A"),
            },
            "trend_analysis": trend_results,
            "clusters": clusters,
            "suppression_results": suppression_results,
            "pattern_results": pattern_results,
            "raw_data": watch_history[:100],  # Show first 100 entries
        }

        return render_template("analysis.html", data=analysis_data)

    except Exception as e:
        error_msg = f"Error analyzing file: {str(e)}"
        traceback.print_exc()
        flash(error_msg)
        return redirect(url_for("upload_file"))


@app.route("/export/<filename>/<format>")
def export_analysis(filename, format):
    try:
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)

        # Parse the watch history file
        parser = HistoryParser(filepath)
        watch_history = parser.parse()

        # Perform analysis
        trend_analyzer = TrendAnalyzer()
        analysis_results = trend_analyzer.analyze_trends(watch_history)

        # Export the results
        export_formatter = ExportFormatter()

        # Create a temporary file for export
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=f".{format}", delete=False
        ) as tmp_file:
            if format == "json":
                export_formatter.export_data(analysis_results, tmp_file.name, "json")
            elif format == "csv":
                export_formatter.export_data(analysis_results, tmp_file.name, "csv")
            elif format == "yaml":
                export_formatter.export_data(analysis_results, tmp_file.name, "yaml")
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
    flash("File too large. Please upload a file smaller than 100MB.")
    return redirect(url_for("upload_file"))


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
