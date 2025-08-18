#!/usr/bin/env python3
"""
RabbitMirror - Advanced YouTube Watch History Analysis Tool

A powerful Python-based command-line tool designed to analyze and understand
YouTube watch history patterns. It provides deep insights into viewing behavior,
detects potential algorithmic manipulation, and offers comprehensive analysis
capabilities for researchers, content creators, and curious users.
"""

__version__ = "1.0.0"
__author__ = "RabbitMirror Development Team"
__email__ = "dev@rabbitmirror.com"
__license__ = "MIT"

# Keep package __init__ lightweight to avoid hard dependencies during import.
# Import submodules directly where needed, e.g.
# `from rabbitmirror.parser import HistoryParser`.

__all__ = [
    # Metadata only; submodules should be imported directly by consumers
    "__version__",
    "__author__",
    "__email__",
    "__license__",
]
