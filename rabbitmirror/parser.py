import logging
import re
from datetime import datetime
from typing import Any, Dict, List, Optional

from bs4 import BeautifulSoup

from .error_recovery import (
    RetryConfig,
    monitor_errors,
    with_retry,
)
from .exceptions import InvalidFormatError, ParsingError


class HistoryParser:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.retry_config = RetryConfig(
            max_attempts=3,
            base_delay=0.5,
            retryable_exceptions=[OSError, IOError],
        )

    @with_retry(RetryConfig(max_attempts=3, base_delay=0.5))
    @monitor_errors
    def parse(self) -> List[Dict[str, Any]]:
        """Parse the YouTube watch history file and return structured data."""
        try:
            return self._parse_with_fallback()
        except FileNotFoundError as e:
            raise ParsingError(
                f"File not found: {self.file_path}",
                file_path=self.file_path,
                error_code="FILE_NOT_FOUND",
            ) from e
        except UnicodeDecodeError as e:
            raise ParsingError(
                f"File encoding error: {str(e)}",
                file_path=self.file_path,
                error_code="ENCODING_ERROR",
            ) from e
        except Exception as e:
            raise ParsingError(
                f"Error parsing file: {str(e)}",
                file_path=self.file_path,
                error_code="PARSE_ERROR",
            ) from e

    def _parse_with_fallback(self) -> List[Dict[str, Any]]:
        """Parse file with multiple encoding fallbacks."""
        encodings = ["utf-8", "utf-8-sig", "latin-1", "cp1252"]

        for encoding in encodings:
            try:
                with open(self.file_path, "r", encoding=encoding) as f:
                    soup = BeautifulSoup(f, "lxml")
                return self._extract_entries(soup)
            except UnicodeDecodeError:
                continue

        # If all encodings fail
        raise ParsingError(
            f"Unable to decode file with any supported encoding: {encodings}",
            file_path=self.file_path,
            error_code="ENCODING_FAILED",
        )

    def _extract_entries(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract individual entries from the parsed HTML."""
        entries = []
        failed_entries = 0

        for i, entry in enumerate(soup.select("div.content-cell")):
            try:
                parsed_entry = self._parse_entry(entry)
                if parsed_entry:
                    entries.append(parsed_entry)
            except (AttributeError, ValueError, TypeError) as e:
                failed_entries += 1
                # Log but don't fail the entire operation
                logging.warning("Failed to parse entry %s: %s", i, e)

        if failed_entries > 0:
            logging.info(
                "Successfully parsed %s entries, failed: %s",
                len(entries),
                failed_entries,
            )

        return entries

    def _parse_entry(self, entry) -> Optional[Dict[str, Any]]:
        """Parse a single watch history entry with error recovery."""
        try:
            title_tag = entry.find("a")
            if not title_tag:
                return None

            title = title_tag.get_text(strip=True)
            if not title:
                return None

            url = title_tag.get("href", "").strip()

            # Extract timestamp with fallback
            timestamp_tag = entry.find("div", class_="mdl-typography--caption")
            timestamp_raw = (
                timestamp_tag.get_text(strip=True) if timestamp_tag else "Unknown"
            )

            try:
                timestamp = self._convert_timestamp(timestamp_raw)
            except InvalidFormatError:
                # Use current time as fallback for invalid timestamps
                timestamp = datetime.now().isoformat()

            return {
                "title": title,
                "url": url,
                "timestamp": timestamp,
            }
        except (AttributeError, ValueError, TypeError) as e:
            # Log but don't fail - return None to skip this entry
            logging.warning("Failed to parse entry: %s", e)
            return None

    def _convert_timestamp(self, timestamp_str: str) -> str:
        """Convert timestamp from YouTube format to ISO format with multiple format support."""
        if timestamp_str == "Unknown" or not timestamp_str.strip():
            return datetime.now().isoformat()

        # Try multiple timestamp formats
        formats = [
            "%b %d, %Y, %I:%M:%S %p",  # Dec 15, 2023, 2:30:45 PM
            "%b %d, %Y %I:%M:%S %p",  # Dec 15, 2023 2:30:45 PM
            "%Y-%m-%d %H:%M:%S",  # 2023-12-15 14:30:45
            "%Y-%m-%dT%H:%M:%S",  # 2023-12-15T14:30:45
            "%Y-%m-%d",  # 2023-12-15
        ]

        timestamp_clean = re.sub(r"\s+[A-Z]{3}$", "", timestamp_str)

        for fmt in formats:
            try:
                dt = datetime.strptime(timestamp_clean, fmt)
                return dt.isoformat()
            except ValueError:
                continue

        # If all formats fail, raise error
        raise InvalidFormatError(
            f"Invalid timestamp format: {timestamp_str}",
            file_path=self.file_path,
            error_code="INVALID_TIMESTAMP_FORMAT",
        )
