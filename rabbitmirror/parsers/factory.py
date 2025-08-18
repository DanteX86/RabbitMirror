#!/usr/bin/env python3

import importlib
from typing import Dict, Optional, Type

from .base_parser import BaseParser, ParserConfig


class ParserFactory:
    """Factory class for creating platform-specific parsers."""

    _parsers: Dict[str, str] = {
        "youtube": "rabbitmirror.parsers.youtube_parser.YouTubeParser",
        "netflix": "rabbitmirror.parsers.netflix_parser.NetflixParser",
        "spotify": "rabbitmirror.parsers.spotify_parser.SpotifyParser",
    }

    @classmethod
    def get_parser(cls, platform: str, config: ParserConfig) -> Optional[BaseParser]:
        """
        Get a parser instance for the specified platform.

        Args:
            platform: Platform name (youtube, netflix, spotify)
            config: Parser configuration

        Returns:
            Parser instance or None if platform not supported
        """
        target = cls._parsers.get(platform.lower())
        if not target:
            return None
        module_name, class_name = target.rsplit(".", 1)
        try:
            module = importlib.import_module(module_name)
            parser_cls: Type[BaseParser] = getattr(module, class_name)
            return parser_cls(config)
        except Exception:  # If optional deps missing (e.g., bs4), defer to caller
            return None

    @classmethod
    def get_supported_platforms(cls) -> list[str]:
        """Get list of supported platforms."""
        return list(cls._parsers.keys())

    @classmethod
    def register_parser(cls, platform: str, parser_class: Type[BaseParser]) -> None:
        """
        Register a new parser for a platform.

        Args:
            platform: Platform name
            parser_class: Parser class implementing BaseParser
        """
        cls._parsers[platform.lower()] = parser_class
