from bs4 import BeautifulSoup
from loguru import logger
from typing import List, Dict, Any

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
        timestamp_tag = entry.find_next_sibling('div', class_='mdl-typography--caption')

        if not (title_tag and timestamp_tag):
            return None

        return {
            'title': title_tag.get_text(strip=True),
            'url': title_tag.get('href', '').strip(),
            'timestamp': timestamp_tag.get_text(strip=True)
        }
