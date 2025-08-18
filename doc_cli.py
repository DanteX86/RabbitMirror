#!/usr/bin/env python3
"""
RabbitMirror Documentation CLI

A simple command-line interface for managing documentation tasks.
"""

import argparse
import os
import subprocess  # nosec B404 - subprocess used for controlled local commands
import sys
from pathlib import Path


def build_docs():
    """Build the Sphinx documentation."""
    docs_dir = Path("docs")
    if not docs_dir.exists():
        print("❌ Error: docs directory not found")
        return False

    print("📚 Building documentation...")
    try:
        # Build HTML documentation using sphinx-build directly
        cmd = ["sphinx-build", "-b", "html", "docs/source", "docs/build/html"]

        result = subprocess.run(
            cmd, capture_output=True, text=True
        )  # nosec B603 - args are controlled

        if result.returncode == 0:
            print("✅ Documentation built successfully!")
            print("📖 Open docs/build/html/index.html in your browser")
            return True
        else:
            print("❌ Error building documentation:")
            print(result.stderr)
            return False

    except FileNotFoundError:
        print("❌ Error: sphinx-build not found. Please install sphinx:")
        print("   pip install sphinx sphinx-rtd-theme")
        return False


def serve_docs(port=8000):
    """Serve the documentation locally."""
    docs_html = Path("docs/build/html")

    if not docs_html.exists():
        print("📚 Documentation not found. Building first...")
        if not build_docs():
            return False

    print(f"🚀 Starting documentation server on port {port}...")
    print(f"📖 Open http://localhost:{port} in your browser")
    print("   Press Ctrl+C to stop")

    try:
        os.chdir(docs_html)
        subprocess.run(
            [sys.executable, "-m", "http.server", str(port)]
        )  # nosec B603 - serving local docs
    except KeyboardInterrupt:
        print("\n👋 Documentation server stopped")
        return True


def clean_docs():
    """Clean built documentation."""
    build_dir = Path("docs/build")
    if build_dir.exists():
        import shutil

        shutil.rmtree(build_dir)
        print("🧹 Documentation build directory cleaned")
    else:
        print("ℹ️  No build directory to clean")
    return True


def check_docs():
    """Check documentation for issues."""
    print("🔍 Checking documentation...")

    # Check if key files exist
    required_files = ["docs/source/conf.py", "docs/source/index.rst", "README.md"]

    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)

    if missing_files:
        print("❌ Missing required files:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        return False

    # Try to build docs with warnings
    print("📚 Testing documentation build...")
    try:
        cmd = [
            "sphinx-build",
            "-b",
            "html",
            "docs/source",
            "docs/build/html-check",
            "-q",  # Quiet mode
        ]

        result = subprocess.run(
            cmd, capture_output=True, text=True
        )  # nosec B603 - args are controlled

        if result.returncode == 0:
            print("✅ Documentation check passed!")
            # Clean up test build
            import shutil

            build_check = Path("docs/build/html-check")
            if build_check.exists():
                shutil.rmtree(build_check)
            return True
        else:
            print("⚠️  Documentation has issues:")
            print(result.stderr)
            return False

    except FileNotFoundError:
        print("❌ Error: sphinx-build not found")
        return False


def init_docs():
    """Initialize documentation structure."""
    print("🚀 Initializing documentation...")

    docs_dir = Path("docs")
    if docs_dir.exists():
        print("ℹ️  Documentation already exists")
        return True

    # Create basic structure
    docs_dir.mkdir()
    (docs_dir / "source").mkdir()
    (docs_dir / "source" / "_static").mkdir()
    (docs_dir / "source" / "_templates").mkdir()

    print("✅ Documentation structure created!")
    print("   Next steps:")
    print("   1. Configure docs/source/conf.py")
    print("   2. Create docs/source/index.rst")
    print("   3. Run: python doc_cli.py build")

    return True


def main():
    parser = argparse.ArgumentParser(
        description="RabbitMirror Documentation CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python doc_cli.py build          # Build documentation
  python doc_cli.py serve          # Serve documentation locally
  python doc_cli.py serve --port 9000  # Serve on custom port
  python doc_cli.py clean          # Clean build files
  python doc_cli.py check          # Check for issues
  python doc_cli.py init           # Initialize docs structure
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Build command
    subparsers.add_parser("build", help="Build documentation")

    # Serve command
    serve_parser = subparsers.add_parser("serve", help="Serve documentation locally")
    serve_parser.add_argument(
        "--port", type=int, default=8000, help="Port to serve on (default: 8000)"
    )

    # Clean command
    subparsers.add_parser("clean", help="Clean build files")

    # Check command
    subparsers.add_parser("check", help="Check documentation")

    # Init command
    subparsers.add_parser("init", help="Initialize documentation")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Execute command
    success = True

    if args.command == "build":
        success = build_docs()
    elif args.command == "serve":
        success = serve_docs(args.port)
    elif args.command == "clean":
        success = clean_docs()
    elif args.command == "check":
        success = check_docs()
    elif args.command == "init":
        success = init_docs()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
