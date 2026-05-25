import json
import os
from threading import Lock
from typing import Any, Self, cast


class ConfigManager:
    _instance: "ConfigManager | None" = None
    _config: dict[str, Any] = {}
    _lock = Lock()

    def __new__(cls) -> Self:
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._load_config()
        return cast(Self, cls._instance)

    def _load_config(self) -> None:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(base_dir, "data", "dane_wejsciowe_kalkulator.json")

        try:
            with open(config_path, encoding="utf-8") as f:
                self._config = cast(dict[str, Any], json.load(f))
        except Exception as e:
            # Fallback or error logging could go here
            raise RuntimeError(f"Failed to load configuration from {config_path}: {e}") from e

    def get_config(self) -> dict[str, Any]:
        """Returns the entire configuration dictionary."""
        return self._config


# Pre-instantiate the singleton
config_manager = ConfigManager()
