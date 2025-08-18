import importlib
import logging
import re
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from .exceptions import DependencyError, InvalidFormatError, ParsingError
from .parsers import BaseParser, ParserConfig, ParserFactory, ParserResult

if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from bs4 import BeautifulSoup  # noqa: F401


class HistoryParser:
    def __init__(self, file_path: str, platform: str = "youtube"):
        """Initialize a HistoryParser.

        Args:
            file_path: Path to the history export file to parse.
            platform: Platform identifier (e.g., "youtube", "netflix", "spotify").
                Defaults to "youtube" for backward compatibility with callers
                that only pass the file path.
        """
        self.file_path = file_path
        self.platform = platform

    def _get_parser(self) -> BaseParser:
        config = ParserConfig(file_path=self.file_path)
        parser = ParserFactory.get_parser(self.platform, config)
        if not parser:
            raise ParsingError(f"Unsupported platform: {self.platform}")
        return parser

    def parse(self) -> ParserResult:
        """Parse file using appropriate platform parser and return structured data."""
        parser = self._get_parser()
        return parser.parse()

    def _parse_with_fallback(self) -> List[Dict[str, Any]]:
        """Parse file with multiple encoding fallbacks."""
        encodings = ["utf-8", "utf-8-sig", "latin-1", "cp1252"]

        for encoding in encodings:
            try:
                with open(self.file_path, "r", encoding=encoding) as f:
                    try:
                        bs4 = importlib.import_module("bs4")
                    except ImportError as e:
                        raise DependencyError(
                            (
                                "BeautifulSoup (bs4) is required to parse HTML. "
                                "Install with 'pip install beautifulsoup4'."
                            )
                        ) from e
                    soup = bs4.BeautifulSoup(f, "lxml")
                return self._extract_entries(soup)
            except UnicodeDecodeError:
                continue

        # If all encodings fail
        raise ParsingError(
            f"Unable to decode file with any supported encoding: {encodings}",
            file_path=self.file_path,
            error_code="ENCODING_FAILED",
        )

    def _extract_entries(self, soup: Any) -> List[Dict[str, Any]]:
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
            logging.getLogger().warning("Failed to parse entry: %s", e)
            return None

    def _convert_timestamp(self, timestamp_str: str) -> str:
        """Convert timestamp from YouTube format to ISO with multiple format support."""
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
