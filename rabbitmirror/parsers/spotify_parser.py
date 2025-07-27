#!/usr/bin/env python3

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from ..exceptions import InvalidFormatError
from .base_parser import BaseParser


class SpotifyParser(BaseParser):
    """
    Parser for Spotify listening history JSON exports.

    Supports parsing the JSON format provided by Spotify's account data export.
    """

    PLATFORM_NAME = "spotify"
    SUPPORTED_FORMATS = [".json"]
    VERSION = "1.0.0"

    def validate_format(self, file_path: Union[str, Path]) -> bool:
        """
        Validate that the file is a Spotify listening history JSON file.

        Args:
            file_path: Path to the file to validate

        Returns:
            bool: True if format is valid, False otherwise
        """
        file_path = Path(file_path)

        # Check file extension
        if file_path.suffix.lower() not in self.SUPPORTED_FORMATS:
            return False

        # Check content for Spotify-specific markers
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                # Load JSON content
                data = json.load(f)

                # Check for Spotify-specific keys
                spotify_markers = ["endTime", "artistName", "trackName"]

                # Verify all markers exist
                if isinstance(data, list) and all(
                    all(marker in entry for marker in spotify_markers) for entry in data
                ):
                    return True

        except (json.JSONDecodeError, IOError):
            return False

        return False

    def _parse_file_content(self, content: str) -> Any:
        """
        Parse raw JSON content

        Args:
            content: Raw JSON content as string

        Returns:
            Parsed JSON data
        """
        return json.loads(content)

    def _extract_entries(self, data: Any) -> List[Dict[str, Any]]:
        """
        Extract entries from Spotify listening history

        Args:
            data: Parsed JSON data

        Returns:
            List of dictionary entries
        """
        return data

    def _parse_entry(self, raw_entry: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Parse single Spotify entry

        Args:
            raw_entry: Raw dictionary of Spotify history entry

        Returns:
            Parsed dictionary or None if parse fails
        """
        try:
            track_name = raw_entry.get("trackName", "").strip()
            if not track_name:
                return None

            artist_name = raw_entry.get("artistName", "").strip()
            timestamp_raw = raw_entry.get("endTime", "").strip()

            # Convert timestamp
            try:
                timestamp = self._convert_spotify_timestamp(timestamp_raw)
            except InvalidFormatError:
                timestamp = datetime.now().isoformat()

            entry = {
                "track_name": track_name,
                "artist_name": artist_name,
                "timestamp": timestamp,
                "platform": self.PLATFORM_NAME,
                "entry_type": "listening_history",
            }

            return entry

        except (AttributeError, ValueError, TypeError) as e:
            self.logger.warning(f"Failed to parse Spotify entry: {e}")
            return None

    def _convert_spotify_timestamp(self, timestamp_str: str) -> str:
        """
        Convert Spotify timestamps to ISO

        Args:
            timestamp_str: Raw timestamp string

        Returns:
            ISO format timestamp string
        """
        try:
            return datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M").isoformat()
        except ValueError:
            raise InvalidFormatError(
                f"Invalid Spotify timestamp format: {timestamp_str}",
                file_path=str(self.config.file_path),
                error_code="INVALID_TIMESTAMP_FORMAT",
            )
