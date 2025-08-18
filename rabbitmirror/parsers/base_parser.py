#!/usr/bin/env python3

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from ..error_recovery import RetryConfig, monitor_errors, with_retry
from ..exceptions import InvalidFormatError, ParsingError


@dataclass
class ParserConfig:
    """Configuration for parsers."""

    # File handling
    file_path: Union[str, Path]
    encoding: Optional[str] = None
    fallback_encodings: List[str] = None

    # Error handling
    max_retries: int = 3
    retry_delay: float = 0.5
    skip_invalid_entries: bool = True
    log_errors: bool = True

    # Platform-specific options
    platform_options: Dict[str, Any] = None

    # Output formatting
    normalize_timestamps: bool = True
    include_metadata: bool = True

    def __post_init__(self):
        """Initialize default values after dataclass creation."""
        if self.fallback_encodings is None:
            self.fallback_encodings = ["utf-8", "utf-8-sig", "latin-1", "cp1252"]
        if self.platform_options is None:
            self.platform_options = {}


@dataclass
class ParserResult:
    """Standardized result from parser operations."""

    # Core data
    entries: List[Dict[str, Any]]

    # Metadata
    platform: str
    parser_version: str
    total_entries: int
    successful_entries: int
    failed_entries: int

    # Processing info
    processing_time: float
    file_size: int
    encoding_used: str

    # Additional metadata
    date_range: Optional[Dict[str, str]] = None
    categories: Optional[List[str]] = None
    warnings: Optional[List[str]] = None

    def __len__(self) -> int:
        """Number of parsed entries (for convenience in aggregations)."""
        return len(self.entries)

    @property
    def success_rate(self) -> float:
        """Calculate parsing success rate."""
        if self.total_entries == 0:
            return 1.0
        return self.successful_entries / self.total_entries


class BaseParser(ABC):
    """
    Abstract base class for all platform parsers.

    Provides a standardized interface for parsing data exports from various
    platforms (YouTube, Netflix, Spotify, etc.).
    """

    PLATFORM_NAME: str = "unknown"
    SUPPORTED_FORMATS: List[str] = []
    VERSION: str = "1.0.0"

    def __init__(self, config: ParserConfig):
        """Initialize parser with configuration."""
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

        # Set up retry configuration
        self.retry_config = RetryConfig(
            max_attempts=config.max_retries,
            base_delay=config.retry_delay,
            retryable_exceptions=[OSError, IOError, UnicodeDecodeError],
        )

    @abstractmethod
    def validate_format(self, file_path: Union[str, Path]) -> bool:
        """
        Validate that the file is in the expected format for this parser.

        Args:
            file_path: Path to the file to validate

        Returns:
            bool: True if format is valid, False otherwise
        """
        pass

    @abstractmethod
    def _extract_entries(self, content: Any) -> List[Dict[str, Any]]:
        """
        Extract entries from the parsed content.

        Args:
            content: Parsed content (HTML soup, JSON data, etc.)

        Returns:
            List of extracted entries
        """
        pass

    @abstractmethod
    def _parse_entry(self, raw_entry: Any) -> Optional[Dict[str, Any]]:
        """
        Parse a single entry into standardized format.

        Args:
            raw_entry: Raw entry data from the source

        Returns:
            Parsed entry or None if parsing failed
        """
        pass

    @with_retry(RetryConfig(max_attempts=3, base_delay=0.5))
    @monitor_errors
    def parse(self) -> ParserResult:
        """
        Parse the file and return structured data.

        Returns:
            ParserResult containing parsed data and metadata
        """
        start_time = datetime.now()
        file_path = Path(self.config.file_path)

        # Validate file exists
        if not file_path.exists():
            raise ParsingError(
                f"File not found: {file_path}",
                file_path=str(file_path),
                error_code="FILE_NOT_FOUND",
            )

        # Validate format if supported
        if not self.validate_format(file_path):
            raise InvalidFormatError(
                f"Invalid format for {self.PLATFORM_NAME} parser",
                file_path=str(file_path),
                error_code="INVALID_FORMAT",
            )

        try:
            # Parse with encoding fallback
            content = self._load_file_with_fallback(file_path)

            # Extract entries
            entries = self._extract_entries(content)

            # Process entries
            processed_entries = []
            failed_count = 0

            for i, raw_entry in enumerate(entries):
                try:
                    parsed_entry = self._parse_entry(raw_entry)
                    if parsed_entry:
                        # Normalize entry if configured
                        if self.config.normalize_timestamps:
                            parsed_entry = self._normalize_entry(parsed_entry)
                        processed_entries.append(parsed_entry)
                    else:
                        failed_count += 1
                        if self.config.log_errors:
                            self.logger.warning(
                                f"Failed to parse entry {i}: empty result"
                            )

                except Exception as e:
                    failed_count += 1
                    if self.config.log_errors:
                        self.logger.warning(f"Failed to parse entry {i}: {e}")
                    if not self.config.skip_invalid_entries:
                        raise ParsingError(
                            f"Failed to parse entry {i}: {e}",
                            file_path=str(file_path),
                            error_code="ENTRY_PARSE_ERROR",
                        ) from e

            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()

            # Create result
            result = ParserResult(
                entries=processed_entries,
                platform=self.PLATFORM_NAME,
                parser_version=self.VERSION,
                total_entries=len(entries),
                successful_entries=len(processed_entries),
                failed_entries=failed_count,
                processing_time=processing_time,
                file_size=file_path.stat().st_size,
                encoding_used=getattr(self, "_encoding_used", "utf-8"),
                date_range=self._calculate_date_range(processed_entries),
                categories=self._extract_categories(processed_entries),
            )

            return result

        except Exception as e:
            if isinstance(e, (ParsingError, InvalidFormatError)):
                raise
            raise ParsingError(
                f"Error parsing {self.PLATFORM_NAME} file: {str(e)}",
                file_path=str(file_path),
                error_code="PARSE_ERROR",
            ) from e

    def _load_file_with_fallback(self, file_path: Path) -> Any:
        """
        Load file with encoding fallback.

        Args:
            file_path: Path to the file

        Returns:
            Loaded content (implementation-specific)
        """
        encodings = [self.config.encoding] if self.config.encoding else []
        encodings.extend(self.config.fallback_encodings)

        for encoding in encodings:
            if encoding is None:
                continue

            try:
                with open(file_path, "r", encoding=encoding) as f:
                    content = self._parse_file_content(f.read())
                    self._encoding_used = encoding
                    return content
            except UnicodeDecodeError:
                continue

        # If all encodings fail
        raise ParsingError(
            f"Unable to decode file with any supported encoding: {encodings}",
            file_path=str(file_path),
            error_code="ENCODING_FAILED",
        )

    @abstractmethod
    def _parse_file_content(self, content: str) -> Any:
        """
        Parse raw file content into structured format.

        Args:
            content: Raw file content as string

        Returns:
            Parsed content (HTML soup, JSON data, etc.)
        """
        pass

    def _normalize_entry(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize entry timestamps and other fields.

        Args:
            entry: Entry to normalize

        Returns:
            Normalized entry
        """
        if "timestamp" in entry:
            entry["timestamp"] = self._normalize_timestamp(entry["timestamp"])
        return entry

    def _normalize_timestamp(self, timestamp: Union[str, datetime]) -> str:
        """
        Normalize timestamp to ISO format.

        Args:
            timestamp: Timestamp to normalize

        Returns:
            ISO format timestamp string
        """
        if isinstance(timestamp, datetime):
            return timestamp.isoformat()
        elif isinstance(timestamp, str):
            # Try to parse common formats
            formats = [
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%dT%H:%M:%SZ",
                "%m/%d/%Y %I:%M:%S %p",
                "%B %d, %Y, %I:%M:%S %p",
                "%b %d, %Y, %I:%M:%S %p",
            ]

            for fmt in formats:
                try:
                    dt = datetime.strptime(timestamp, fmt)
                    return dt.isoformat()
                except ValueError:
                    continue

            # If no format matches, return as-is
            return timestamp
        else:
            return str(timestamp)

    def _calculate_date_range(
        self, entries: List[Dict[str, Any]]
    ) -> Optional[Dict[str, str]]:
        """
        Calculate date range from entries.

        Args:
            entries: List of parsed entries

        Returns:
            Dict with start and end dates, or None if no timestamps found
        """
        if not entries:
            return None

        timestamps = []
        for entry in entries:
            if "timestamp" in entry:
                try:
                    if isinstance(entry["timestamp"], str):
                        dt = datetime.fromisoformat(
                            entry["timestamp"].replace("Z", "+00:00")
                        )
                    else:
                        dt = entry["timestamp"]
                    timestamps.append(dt)
                except (ValueError, TypeError):
                    continue

        if not timestamps:
            return None

        timestamps.sort()
        return {"start": timestamps[0].isoformat(), "end": timestamps[-1].isoformat()}

    def _extract_categories(self, entries: List[Dict[str, Any]]) -> Optional[List[str]]:
        """
        Extract unique categories from entries.

        Args:
            entries: List of parsed entries

        Returns:
            List of unique categories or None
        """
        categories = set()
        for entry in entries:
            if "category" in entry and entry["category"]:
                categories.add(entry["category"])

        return sorted(list(categories)) if categories else None

    def get_supported_formats(self) -> List[str]:
        """Get list of supported file formats."""
        return self.SUPPORTED_FORMATS.copy()

    def get_platform_name(self) -> str:
        """Get platform name."""
        return self.PLATFORM_NAME

    def get_version(self) -> str:
        """Get parser version."""
        return self.VERSION
