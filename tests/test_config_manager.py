import pytest

from rabbitmirror.config_manager import ConfigManager


class TestConfigManager:
    """Test class for configuration management."""

    def test_set_and_get_local_config(self, tmp_path):
        """Test setting and getting local configuration values."""
        config_manager = ConfigManager(use_global=False)
        local_config_path = tmp_path / ".rabbitmirror_config.json"
        config_manager.config_path = local_config_path

        config_manager.set("test_key", "test_value")
        assert config_manager.get("test_key") == "test_value"

    def test_set_and_get_global_config(self, tmp_path):
        """Test setting and getting global configuration values."""
        config_manager = ConfigManager(use_global=True)
        global_config_path = tmp_path / ".rabbitmirror_config.json"
        config_manager.config_path = global_config_path

        config_manager.set("global_key", "global_value")
        assert config_manager.get("global_key") == "global_value"

    def test_list_config(self, tmp_path):
        """Test listing configuration values."""
        config_manager = ConfigManager(use_global=False)
        config_path = tmp_path / ".rabbitmirror_config.json"
        config_manager.config_path = config_path

        config_manager.set("key1", "value1")
        config_manager.set("key2", 123)
        config_manager.set("key3", True)

        listed_config = config_manager.list()
        assert isinstance(listed_config, dict)
        assert listed_config["key1"] == "value1"
        assert listed_config["key2"] == 123
        assert listed_config["key3"] is True

        json_list = config_manager.list(as_json=True)
        assert isinstance(json_list, str)
        assert '"key1": "value1"' in json_list

    def test_get_nonexistent_key(self, tmp_path):
        """Test retrieving a nonexistent key."""
        config_manager = ConfigManager(use_global=False)
        config_path = tmp_path / ".rabbitmirror_config.json"
        config_manager.config_path = config_path
        result = config_manager.get("nonexistent_key")
        assert result is None

    def test_handling_of_nonjson_config(self, tmp_path):
        """Test handling of non-JSON configuration file content."""
        config_manager = ConfigManager(use_global=False)
        config_path = tmp_path / ".rabbitmirror_config.json"
        config_manager.config_path = config_path

        # Write invalid JSON content
        with open(config_path, "w", encoding="utf-8") as f:
            f.write("Not a JSON content")

        # Should not raise exception, should return empty dict
        listed_config = config_manager.list()
        assert listed_config == {}
