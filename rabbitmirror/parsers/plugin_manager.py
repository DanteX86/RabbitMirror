#!/usr/bin/env python3

import importlib
import importlib.util
import inspect
from pathlib import Path
from typing import Dict, List, Optional

from .base_parser import BaseParser
from .registry import get_global_registry


class PluginManager:
    """Manager for dynamically loading and managing parser plugins."""

    def __init__(self):
        self.registry = get_global_registry()
        self._loaded_plugins: Dict[str, str] = {}

    def load_plugin_from_file(self, plugin_path: Path) -> Optional[str]:
        """
        Load a parser plugin from a Python file.

        Args:
            plugin_path: Path to the plugin file

        Returns:
            Platform name if loaded successfully, None otherwise
        """
        if not plugin_path.exists() or plugin_path.suffix != ".py":
            return None

        try:
            # Import the module
            spec = importlib.util.spec_from_file_location(plugin_path.stem, plugin_path)
            if not spec or not spec.loader:
                return None

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Find parser classes in the module
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if (
                    issubclass(obj, BaseParser)
                    and obj != BaseParser
                    and hasattr(obj, "PLATFORM_NAME")
                ):
                    platform = obj.PLATFORM_NAME
                    self.registry.register(platform, obj)
                    self._loaded_plugins[platform] = str(plugin_path)
                    return platform

        except Exception as e:
            print(f"Error loading plugin from {plugin_path}: {e}")

        return None

    def load_plugins_from_directory(self, plugin_dir: Path) -> List[str]:
        """
        Load all parser plugins from a directory.

        Args:
            plugin_dir: Directory containing plugin files

        Returns:
            List of loaded platform names
        """
        loaded_platforms = []

        if not plugin_dir.exists() or not plugin_dir.is_dir():
            return loaded_platforms

        for plugin_file in plugin_dir.glob("*_parser.py"):
            platform = self.load_plugin_from_file(plugin_file)
            if platform:
                loaded_platforms.append(platform)

        return loaded_platforms

    def unload_plugin(self, platform: str) -> bool:
        """
        Unload a plugin.

        Args:
            platform: Platform identifier

        Returns:
            True if unloaded successfully, False otherwise
        """
        if self.registry.unregister(platform):
            self._loaded_plugins.pop(platform, None)
            return True
        return False

    def get_loaded_plugins(self) -> Dict[str, str]:
        """Get dictionary of loaded plugins and their file paths."""
        return self._loaded_plugins.copy()

    def reload_plugin(self, platform: str) -> bool:
        """
        Reload a plugin.

        Args:
            platform: Platform identifier

        Returns:
            True if reloaded successfully, False otherwise
        """
        if platform in self._loaded_plugins:
            plugin_path = Path(self._loaded_plugins[platform])
            self.unload_plugin(platform)
            return self.load_plugin_from_file(plugin_path) is not None
        return False

    def get_plugin_info(self, platform: str) -> Optional[dict]:
        """
        Get information about a loaded plugin.

        Args:
            platform: Platform identifier

        Returns:
            Dictionary with plugin info or None if not found
        """
        parser_class = self.registry.get_parser_class(platform)
        if not parser_class:
            return None

        return {
            "platform": platform,
            "class_name": parser_class.__name__,
            "version": getattr(parser_class, "VERSION", "unknown"),
            "supported_formats": getattr(parser_class, "SUPPORTED_FORMATS", []),
            "file_path": self._loaded_plugins.get(platform),
        }


# Global plugin manager instance
_global_plugin_manager = PluginManager()


def get_global_plugin_manager() -> PluginManager:
    """Get the global plugin manager instance."""
    return _global_plugin_manager
