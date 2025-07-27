#!/usr/bin/env python3

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from ..exceptions import InvalidFormatError, ParsingError
from .base_parser import BaseParser, ParserConfig, ParserResult


class NetflixParser(BaseParser):
    """
    Parser for Netflix viewing history JSON exports.

    Supports parsing the JSON format provided by Netflix's account data export.
    """

    PLATFORM_NAME = "netflix"
    SUPPORTED_FORMATS = [".json"]
    VERSION = "1.0.0"

    def validate_format(self, file_path: Union[str, Path]) -> bool:
        """
        Validate that the file is a Netflix viewing history JSON file.

        Args:
            file_path: Path to the file to validate

        Returns:
            bool: True if format is valid, False otherwise
        """
        file_path = Path(file_path)

        # Check file extension
        if file_path.suffix.lower() not in self.SUPPORTED_FORMATS:
            return False

        # Check content for Netflix-specific markers
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                # Load JSON content
                data = json.load(f)

                # Check for Netflix-specific keys
                netflix_markers = ["History", "NetflixID"]

                # Verify one of the markers exists
                return any(marker in data for marker in netflix_markers)

        except (json.JSONDecodeError, IOError):
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
        Extract entries from Netflix viewing history

        Args:
            data: Parsed JSON data

        Returns:
            List of dictionary entries
        """
        return data.get("History", [])

    def _parse_entry(self, raw_entry: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Parse single Netflix entry

        Args:
            raw_entry: Raw dictionary of Netflix history entry

        Returns:
            Parsed dictionary or None if parse fails
        """
        try:
            title = raw_entry.get("Title", "").strip()
            if not title:
                return None

            url = raw_entry.get("Device Group", "").strip()
            timestamp_raw = raw_entry.get("Date", "").strip()

            # Convert timestamp
            try:
                timestamp = self._convert_netflix_timestamp(timestamp_raw)
            except InvalidFormatError:
                timestamp = datetime.now().isoformat()

            entry = {
                "title": title,
                "url": url,
                "timestamp": timestamp,
                "platform": self.PLATFORM_NAME,
                "entry_type": "viewing_history",
            }

            return entry

        except (AttributeError, ValueError, TypeError) as e:
            self.logger.warning(f"Failed to parse Netflix entry: {e}")
            return None

    def _convert_netflix_timestamp(self, timestamp_str: str) -> str:
        """
        Convert Netflix timestamps to ISO

        Args:
            timestamp_str: Raw timestamp string

        Returns:
            ISO format timestamp string
        """
        try:
            return datetime.strptime(timestamp_str, "%m/%d/%y").isoformat()
        except ValueError:
            raise InvalidFormatError(
                f"Invalid Netflix timestamp format: {timestamp_str}",
                file_path=str(self.config.file_path),
                error_code="INVALID_TIMESTAMP_FORMAT",
            )
