#!/bin/bash
# Release script for RabbitMirror
# Usage: ./scripts/release.sh [version] [--test-pypi]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Parse arguments
VERSION=$1
TEST_PYPI=false

if [[ "$2" == "--test-pypi" ]]; then
    TEST_PYPI=true
fi

# Check if version is provided
if [[ -z "$VERSION" ]]; then
    print_error "Version number is required"
    echo "Usage: $0 [version] [--test-pypi]"
    echo "Example: $0 1.0.0"
    echo "Example: $0 1.0.0 --test-pypi"
    exit 1
fi

# Validate version format (semantic versioning)
if [[ ! "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    print_error "Invalid version format. Use semantic versioning (e.g., 1.0.0)"
    exit 1
fi

print_status "Starting release process for version $VERSION"

# Check if we're in the right directory
if [[ ! -f "setup.py" ]] || [[ ! -f "pyproject.toml" ]]; then
    print_error "This script must be run from the RabbitMirror root directory"
    exit 1
fi

# Check if git is clean
if [[ -n $(git status --porcelain) ]]; then
    print_error "Git working directory is not clean. Please commit or stash changes."
    exit 1
fi

# Check if we're on main branch
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [[ "$CURRENT_BRANCH" != "main" ]]; then
    print_warning "Not on main branch (currently on $CURRENT_BRANCH)"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Update version in pyproject.toml
print_status "Updating version in pyproject.toml"
sed -i.bak "s/version = \".*\"/version = \"$VERSION\"/" pyproject.toml
rm pyproject.toml.bak

# Update version in setup.py
print_status "Updating version in setup.py"
sed -i.bak "s/version=\".*\"/version=\"$VERSION\"/" setup.py
rm setup.py.bak

# Update version in __init__.py
print_status "Updating version in __init__.py"
sed -i.bak "s/__version__ = \".*\"/__version__ = \"$VERSION\"/" rabbitmirror/__init__.py
rm rabbitmirror/__init__.py.bak

# Run tests
print_status "Running test suite"
python -m pytest tests/ -v --cov=rabbitmirror --cov-report=term-missing

# Run code quality checks
print_status "Running code quality checks"
python -m mypy rabbitmirror/
python -m flake8 rabbitmirror/
python -m bandit -r rabbitmirror/

# Clean previous builds
print_status "Cleaning previous builds"
rm -rf dist/ build/ *.egg-info/

# Build package
print_status "Building package"
python -m build

# Check package
print_status "Checking package"
python -m twine check dist/*

# Test installation
print_status "Testing package installation"
python -m pip install dist/*.whl --force-reinstall

# Test CLI
print_status "Testing CLI functionality"
rabbitmirror --help > /dev/null
print_success "CLI test passed"

# Commit version changes
print_status "Committing version changes"
git add -A
git commit -m "chore: bump version to $VERSION"

# Create git tag
print_status "Creating git tag"
git tag -a "v$VERSION" -m "Release version $VERSION"

# Push changes and tag
print_status "Pushing changes and tag to origin"
git push origin main
git push origin "v$VERSION"

# Upload to PyPI
if [[ "$TEST_PYPI" == true ]]; then
    print_status "Uploading to Test PyPI"
    python -m twine upload --repository testpypi dist/*
    print_success "Package uploaded to Test PyPI"
    echo "Install with: pip install -i https://test.pypi.org/simple/ rabbitmirror==$VERSION"
else
    print_status "Uploading to PyPI"
    python -m twine upload dist/*
    print_success "Package uploaded to PyPI"
    echo "Install with: pip install rabbitmirror==$VERSION"
fi

# Create GitHub release
print_status "Creating GitHub release"
if command -v gh &> /dev/null; then
    gh release create "v$VERSION" dist/*.tar.gz dist/*.whl \
        --title "Release $VERSION" \
        --notes "See [CHANGELOG.md](https://github.com/romulusaugustus/RabbitMirror/blob/main/CHANGELOG.md) for detailed changes."
    print_success "GitHub release created"
else
    print_warning "GitHub CLI not found. Please create release manually at:"
    echo "https://github.com/romulusaugustus/RabbitMirror/releases/new"
fi

print_success "Release $VERSION completed successfully!"
print_status "Next steps:"
echo "1. Verify the package on PyPI: https://pypi.org/project/rabbitmirror/"
echo "2. Test installation: pip install rabbitmirror==$VERSION"
echo "3. Update documentation if needed"
echo "4. Announce the release"

# Clean up
rm -rf build/
