#!/usr/bin/env python3

import importlib
import re
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

from ..exceptions import InvalidFormatError
from .base_parser import BaseParser

if TYPE_CHECKING:  # pragma: no cover
    from bs4 import BeautifulSoup  # noqa: F401


class YouTubeParser(BaseParser):
    """
    Parser for YouTube watch history files exported from Google Takeout.

    Supports the HTML format provided by YouTube's data export feature.
    """

    PLATFORM_NAME = "youtube"
    SUPPORTED_FORMATS = [".html", ".htm"]
    VERSION = "1.0.0"

    def validate_format(self, file_path: Union[str, Path]) -> bool:
        """
        Validate that the file is a YouTube watch history HTML file.

        Args:
            file_path: Path to the file to validate

        Returns:
            bool: True if format is valid, False otherwise
        """
        file_path = Path(file_path)

        # Check file extension
        if file_path.suffix.lower() not in self.SUPPORTED_FORMATS:
            return False

        # Check file content for YouTube-specific markers
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                # Read first few KB to check for YouTube markers
                content = f.read(8192)

                # Look for YouTube-specific patterns
                youtube_markers = [
                    "youtube.com",
                    "Watch History",
                    "content-cell",
                    "mdl-typography--caption",
                ]

                return any(marker in content for marker in youtube_markers)

        except (IOError, UnicodeDecodeError):
            return False

    def _parse_file_content(self, content: str) -> "BeautifulSoup":
        """
        Parse YouTube HTML content using BeautifulSoup.

        Args:
            content: Raw HTML content as string

        Returns:
            BeautifulSoup object for parsing
        """
        bs4 = importlib.import_module("bs4")
        return bs4.BeautifulSoup(content, "lxml")

    def _extract_entries(self, soup: "BeautifulSoup") -> List[Any]:
        """
        Extract video entries from YouTube HTML.

        Args:
            soup: BeautifulSoup object containing parsed HTML

        Returns:
            List of raw entry elements
        """
        # YouTube uses div.content-cell for each video entry
        entries = soup.select("div.content-cell")

        if not entries:
            # Try alternative selectors for different YouTube export formats
            alt_selectors = ["div.outer-cell", ".activity-record", "[data-target-id]"]

            for selector in alt_selectors:
                entries = soup.select(selector)
                if entries:
                    break

        return entries

    def _parse_entry(self, raw_entry: Any) -> Optional[Dict[str, Any]]:
        """
        Parse a single YouTube video entry.

        Args:
            raw_entry: Raw BeautifulSoup entry element

        Returns:
            Parsed entry dictionary or None if parsing failed
        """
        try:
            # Extract title and URL
            title_link = raw_entry.find("a")
            if not title_link:
                return None

            title = title_link.get_text(strip=True)
            if not title:
                return None

            url = title_link.get("href", "").strip()

            # Extract video ID from URL
            video_id = self._extract_video_id(url)

            # Extract timestamp
            timestamp_element = raw_entry.find("div", class_="mdl-typography--caption")
            timestamp_raw = (
                timestamp_element.get_text(strip=True)
                if timestamp_element
                else "Unknown"
            )

            # Convert timestamp
            try:
                timestamp = self._convert_youtube_timestamp(timestamp_raw)
            except InvalidFormatError:
                timestamp = datetime.now().isoformat()

            # Extract channel name if available
            channel_name = self._extract_channel_name(raw_entry)

            # Extract additional metadata
            metadata = self._extract_metadata(raw_entry)

            entry = {
                "title": title,
                "url": url,
                "video_id": video_id,
                "timestamp": timestamp,
                "platform": self.PLATFORM_NAME,
                "entry_type": "watch_history",
            }

            # Add optional fields
            if channel_name:
                entry["channel"] = channel_name

            if metadata:
                entry.update(metadata)

            return entry

        except (AttributeError, ValueError, TypeError) as e:
            self.logger.warning("Failed to parse YouTube entry: %s", e)
            return None

    def _extract_video_id(self, url: str) -> Optional[str]:
        """
        Extract YouTube video ID from URL.

        Args:
            url: YouTube video URL

        Returns:
            Video ID or None if not found
        """
        if not url:
            return None

        # Common YouTube URL patterns
        patterns = [
            r"(?:v=|/)([a-zA-Z0-9_-]{11})",  # Standard format
            r"youtu\.be/([a-zA-Z0-9_-]{11})",  # Short format
            r"embed/([a-zA-Z0-9_-]{11})",  # Embed format
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)

        return None

    def _extract_channel_name(self, entry_element: Any) -> Optional[str]:
        """
        Extract channel name from entry element.

        Args:
            entry_element: BeautifulSoup entry element

        Returns:
            Channel name or None if not found
        """
        # Try different selectors for channel name
        channel_selectors = [
            ".channel-name",
            ".content-cell a[href*='channel']",
            ".content-cell a[href*='user']",
        ]

        for selector in channel_selectors:
            channel_element = entry_element.select_one(selector)
            if channel_element:
                channel_name = channel_element.get_text(strip=True)
                if channel_name and channel_name != "YouTube":
                    return channel_name

        return None

    def _extract_metadata(self, entry_element: Any) -> Dict[str, Any]:
        """
        Extract additional metadata from entry.

        Args:
            entry_element: BeautifulSoup entry element

        Returns:
            Dictionary of metadata
        """
        metadata = {}

        # Look for watched/removed indicators
        text_content = entry_element.get_text().lower()

        if "watched" in text_content:
            metadata["status"] = "watched"
        elif "removed" in text_content or "deleted" in text_content:
            metadata["status"] = "removed"

        # Extract duration if available
        duration_pattern = r"(\d+):(\d+)"
        match = re.search(duration_pattern, entry_element.get_text())
        if match:
            minutes, seconds = match.groups()
            metadata["duration"] = f"{minutes}:{seconds}"
            metadata["duration_seconds"] = int(minutes) * 60 + int(seconds)

        return metadata

    def _convert_youtube_timestamp(self, timestamp_str: str) -> str:
        """
        Convert YouTube timestamp to ISO format.

        Args:
            timestamp_str: Raw timestamp string

        Returns:
            ISO format timestamp string
        """
        if timestamp_str == "Unknown" or not timestamp_str.strip():
            return datetime.now().isoformat()

        # YouTube timestamp formats
        formats = [
            "%b %d, %Y, %I:%M:%S %p",  # Dec 15, 2023, 2:30:45 PM
            "%b %d, %Y %I:%M:%S %p",  # Dec 15, 2023 2:30:45 PM (no comma)
            "%B %d, %Y, %I:%M:%S %p",  # December 15, 2023, 2:30:45 PM
            "%B %d, %Y %I:%M:%S %p",  # December 15, 2023 2:30:45 PM
            "%m/%d/%Y %I:%M:%S %p",  # 12/15/2023 2:30:45 PM
            "%Y-%m-%d %H:%M:%S",  # 2023-12-15 14:30:45
            "%Y-%m-%dT%H:%M:%S",  # 2023-12-15T14:30:45
            "%Y-%m-%d",  # 2023-12-15
        ]

        # Clean timestamp string (remove timezone abbreviations)
        timestamp_clean = re.sub(r"\s+[A-Z]{3}$", "", timestamp_str)

        for fmt in formats:
            try:
                dt = datetime.strptime(timestamp_clean, fmt)
                return dt.isoformat()
            except ValueError:
                continue

        # If all formats fail, raise error
        raise InvalidFormatError(
            f"Invalid YouTube timestamp format: {timestamp_str}",
            file_path=str(self.config.file_path),
            error_code="INVALID_TIMESTAMP_FORMAT",
        )

    def get_format_info(self) -> Dict[str, Any]:
        """
        Get information about the YouTube export format.

        Returns:
            Dictionary with format information
        """
        return {
            "platform": self.PLATFORM_NAME,
            "formats": self.SUPPORTED_FORMATS,
            "description": "YouTube watch history HTML export from Google Takeout",
            "source_instructions": [
                "1. Go to https://takeout.google.com/",
                "2. Select 'YouTube and YouTube Music'",
                "3. Choose 'history' > 'watch-history.html'",
                "4. Download and extract the file",
            ],
            "common_issues": [
                "File must be the HTML export, not JSON",
                "Ensure file encoding is UTF-8",
                "Large files may take time to process",
            ],
        }
