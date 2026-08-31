"""Configuration management for CoomerTool."""

import json
import os
from pathlib import Path
from typing import Any

DEFAULT_CONFIG = {
    "output": "./downloads",
    "threads": 32,
    "timeout": 30,
    "retries": 5,
    "metadata": "md",
    "proxy": None,
    "include": [],
    "exclude": [],
    "min_size": None,
    "max_size": None,
    "user_agent": None,
    "db_path": "./coomertool.db",
    "rate_limit": 0.0,
    "chunk_size": 8192,
}


class Config:
    """Load and merge CLI args with JSON config file."""

    def __init__(self, path: str = "./config.json"):
        self.path = Path(path)
        self._data = dict(DEFAULT_CONFIG)
        if self.path.exists():
            self._load()

    def _load(self) -> None:
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    self._data.update(data)
        except (json.JSONDecodeError, OSError) as e:
            print(f"[WARN] Could not load config: {e}")

    def save(self) -> None:
        """Write current config to disk."""
        try:
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2, ensure_ascii=False)
            print(f"[INFO] Config saved to {self.path}")
        except OSError as e:
            print(f"[ERROR] Could not save config: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._data[key] = value

    def merge_args(self, args: Any) -> None:
        """Override config values with non-None CLI arguments."""
        mapping = {
            "output": "output",
            "threads": "threads",
            "timeout": "timeout",
            "retries": "retries",
            "metadata": "metadata",
            "proxy": "proxy",
            "include": "include",
            "exclude": "exclude",
            "min_size": "min_size",
            "max_size": "max_size",
            "db": "db_path",
            "user_agent": "user_agent",
        }
        for arg_key, cfg_key in mapping.items():
            val = getattr(args, arg_key, None)
            if val is not None:
                self._data[cfg_key] = val

    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    def __repr__(self) -> str:
        return f"Config({self._data})"
