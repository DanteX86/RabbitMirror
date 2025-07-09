from bs4 import BeautifulSoup
from loguru import logger
from typing import List, Dict, Any
from datetime import datetime
import re

class HistoryParser:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def parse(self) -> List[Dict[str, Any]]:
        """Parse the YouTube watch history file and return structured data."""
        with open(self.file_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'lxml')
        return self._extract_entries(soup)

    def _extract_entries(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract individual entries from the parsed HTML."""
        entries = []
        for entry in soup.select('div.content-cell'):
            parsed_entry = self._parse_entry(entry)
            if parsed_entry:
                entries.append(parsed_entry)
        return entries

    def _parse_entry(self, entry) -> Dict[str, Any]:
        """Parse a single watch history entry."""
        title_tag = entry.find('a')
        timestamp_tag = entry.find('div', class_='mdl-typography--caption')

        if not title_tag:
            return None

        # Extract timestamp from the timestamp tag or use a default
        timestamp_raw = timestamp_tag.get_text(strip=True) if timestamp_tag else "Unknown"
        timestamp = self._convert_timestamp(timestamp_raw)
        
        return {
            'title': title_tag.get_text(strip=True),
            'url': title_tag.get('href', '').strip(),
            'timestamp': timestamp
        }
    
    def _convert_timestamp(self, timestamp_str: str) -> str:
        """Convert timestamp from YouTube format to ISO format."""
        if timestamp_str == "Unknown":
            return datetime.now().isoformat()
        
        try:
            # Parse YouTube format: "Dec 15, 2023, 2:30:45 PM PST"
            # Remove timezone for now and parse
            timestamp_clean = re.sub(r'\s+[A-Z]{3}$', '', timestamp_str)
            dt = datetime.strptime(timestamp_clean, '%b %d, %Y, %I:%M:%S %p')
            return dt.isoformat()
        except ValueError:
            # If parsing fails, return current time
            return datetime.now().isoformat()
