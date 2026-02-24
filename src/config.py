import json
import os
from threading import Lock

class ConfigManager:
    _instance = None
    _config = None
    _lock = Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(ConfigManager, cls).__new__(cls)
                cls._instance._load_config()
        return cls._instance

    def _load_config(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(base_dir, 'dane_wejsciowe_kalkulator.json')
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self._config = json.load(f)
        except Exception as e:
            # Fallback or error logging could go here
            raise RuntimeError(f"Failed to load configuration from {config_path}: {e}")

    def get_config(self) -> dict:
        """Returns the entire configuration dictionary."""
        return self._config

# Pre-instantiate the singleton
config_manager = ConfigManager()
