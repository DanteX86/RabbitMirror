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

from .adversarial_profiler import AdversarialProfiler
from .cluster_engine import ClusterEngine
from .config_manager import ConfigManager
from .dashboard_generator import DashboardGenerator
from .export_formatter import ExportFormatter

# Core components
from .parser import HistoryParser
from .profile_simulator import ProfileSimulator
from .qr_generator import QRGenerator
from .report_generator import ReportGenerator
from .schema_validator import SchemaValidator
from .suppression_index import SuppressionIndex
from .symbolic_logger import SymbolicLogger

__all__ = [
    # Core analysis components
    "HistoryParser",
    "ClusterEngine",
    "AdversarialProfiler",
    "SuppressionIndex",
    "ProfileSimulator",
    # Export and reporting
    "ReportGenerator",
    "ExportFormatter",
    "QRGenerator",
    "DashboardGenerator",
    # Configuration and validation
    "ConfigManager",
    "SchemaValidator",
    # Utilities
    "SymbolicLogger",
    # Metadata
    "__version__",
    "__author__",
    "__email__",
    "__license__",
]
