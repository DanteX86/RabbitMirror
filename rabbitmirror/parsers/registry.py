#!/usr/bin/env python3

from typing import Dict, List, Optional, Type

from .base_parser import BaseParser


class ParserRegistry:
    """Registry for managing parser plugins and extensions."""

    def __init__(self):
        self._registered_parsers: Dict[str, Type[BaseParser]] = {}

    def register(self, platform: str, parser_class: Type[BaseParser]) -> None:
        """
        Register a parser for a platform.

        Args:
            platform: Platform identifier
            parser_class: Parser class implementing BaseParser
        """
        if not issubclass(parser_class, BaseParser):
            raise ValueError("Parser class must inherit from BaseParser")

        self._registered_parsers[platform.lower()] = parser_class

    def unregister(self, platform: str) -> bool:
        """
        Unregister a parser for a platform.

        Args:
            platform: Platform identifier

        Returns:
            True if parser was unregistered, False if not found
        """
        return self._registered_parsers.pop(platform.lower(), None) is not None

    def get_parser_class(self, platform: str) -> Optional[Type[BaseParser]]:
        """
        Get the parser class for a platform.

        Args:
            platform: Platform identifier

        Returns:
            Parser class or None if not found
        """
        return self._registered_parsers.get(platform.lower())

    def get_registered_platforms(self) -> List[str]:
        """Get list of all registered platforms."""
        return list(self._registered_parsers.keys())

    def is_registered(self, platform: str) -> bool:
        """
        Check if a platform has a registered parser.

        Args:
            platform: Platform identifier

        Returns:
            True if registered, False otherwise
        """
        return platform.lower() in self._registered_parsers

    def clear(self) -> None:
        """Clear all registered parsers."""
        self._registered_parsers.clear()


# Global registry instance
_global_registry = ParserRegistry()


def get_global_registry() -> ParserRegistry:
    """Get the global parser registry instance."""
    return _global_registry
