#!/usr/bin/env python3
"""Setup script for RabbitMirror."""

from pathlib import Path

from setuptools import find_packages, setup

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

# Read requirements from requirements.txt
requirements = []
requirements_path = this_directory / "requirements.txt"
if requirements_path.exists():
    with open(requirements_path, encoding="utf-8") as f:
        requirements = [
            line.strip() for line in f if line.strip() and not line.startswith("#")
        ]

setup(
    name="rabbitmirror",
    version="1.0.0",
    author="RabbitMirror Development Team",
    author_email="dev@rabbitmirror.com",
    description="Advanced YouTube Watch History Analysis Tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/romulusaugustus/RabbitMirror",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Data Scientists",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Multimedia :: Video",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-mock>=3.10.0",
            "pre-commit>=3.0.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "flake8>=6.0.0",
            "pylint>=3.0.0",
            "bandit>=1.7.0",
        ],
        "docs": [
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.2.0",
            "sphinx-autodoc-typehints>=1.19.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "rabbitmirror=rabbitmirror.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "rabbitmirror": ["templates/*.html", "templates/*.md"],
    },
    keywords="youtube, data-analysis, privacy, watch-history, clustering, profiling",
    project_urls={
        "Bug Reports": "https://github.com/romulusaugustus/RabbitMirror/issues",
        "Source": "https://github.com/romulusaugustus/RabbitMirror",
        "Documentation": "https://romulusaugustus.github.io/RabbitMirror/",
    },
)
