#!/usr/bin/env python3

from typing import Optional, Type

from .base_parser import BaseParser, ParserConfig
from .netflix_parser import NetflixParser
from .spotify_parser import SpotifyParser
from .youtube_parser import YouTubeParser


class ParserFactory:
    """Factory class for creating platform-specific parsers."""

    _parsers = {
        "youtube": YouTubeParser,
        "netflix": NetflixParser,
        "spotify": SpotifyParser,
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
        parser_class = cls._parsers.get(platform.lower())
        if parser_class:
            return parser_class(config)
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
