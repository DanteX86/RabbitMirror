import json
from pathlib import Path
from typing import Optional, Union


class ConfigManager:
    def __init__(self, use_global: bool = False):
        self.config_filename = ".rabbitmirror_config.json"
        self.config_dir = Path.home() if use_global else Path.cwd()
        self.config_path = self.config_dir / self.config_filename
        # Ensure directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def _load_config(self) -> dict:
        if not self.config_path.exists():
            return {}
        try:
            with open(self.config_path, "r", encoding="utf-8") as config_file:
                return json.load(config_file)
        except (json.JSONDecodeError, IOError):
            # If the file is corrupted or unreadable, return empty dict
            return {}

    def _save_config(self, config: dict):
        with open(self.config_path, "w", encoding="utf-8") as config_file:
            json.dump(config, config_file, indent=2)

    def set(self, key: str, value: Union[str, int, float, bool]):
        config = self._load_config()
        config[key] = value
        self._save_config(config)

    def get(self, key: str) -> Optional[Union[str, int, float, bool]]:
        config = self._load_config()
        return config.get(key)

    def list(self, as_json: bool = False) -> Union[dict, str]:
        config = self._load_config()
        return json.dumps(config, indent=2) if as_json else config
