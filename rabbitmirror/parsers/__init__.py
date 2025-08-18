#!/usr/bin/env python3
"""
Multi-Platform Parser Framework

This module provides a standardized interface for parsing data exports from
various platforms (YouTube, Netflix, Spotify, etc.) with extensible plugin support.
"""

__version__ = "1.0.0"

from .base_parser import BaseParser, ParserConfig, ParserResult
from .factory import ParserFactory
from .plugin_manager import PluginManager
from .registry import ParserRegistry

__all__ = [
    "BaseParser",
    "ParserConfig",
    "ParserResult",
    "PluginManager",
    "ParserRegistry",
    "ParserFactory",
]
