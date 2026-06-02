"""
Settings manager — persists user preferences to JSON.
"""

import json
import os
from pathlib import Path


DEFAULTS = {
    "word_wrap": True,
    "spell_check": True,
    "auto_save": True,
    "show_line_numbers": True,
    "tab_width": 4,
    "encoding": "UTF-8",
    "line_ending": "CRLF",
    "recent_files": [],
    "window_geometry": None,
    "window_maximized": False,
    "show_toolbar": False,
    "show_statusbar": True,
    "editor_zoom_size": None,
}


class Settings:
    def __init__(self):
        self._data = dict(DEFAULTS)
        self._path = self._config_path()
        self.load()

    @staticmethod
    def _config_path() -> Path:
        app_data = os.environ.get("APPDATA", str(Path.home()))
        config_dir = Path(app_data) / "NotepadMinus"
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir / "settings.json"

    def load(self):
        try:
            if self._path.exists():
                with open(self._path, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                self._data.update(saved)
        except Exception:
            pass

    def save(self):
        try:
            with open(self._path, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2)
        except Exception:
            pass

    def get(self, key, default=None):
        return self._data.get(key, DEFAULTS.get(key, default))

    def set(self, key, value):
        self._data[key] = value
        self.save()

    def add_recent_file(self, path: str):
        recent = self._data.get("recent_files", [])
        if path in recent:
            recent.remove(path)
        recent.insert(0, path)
        self._data["recent_files"] = recent[:10]
        self.save()

    @property
    def recent_files(self):
        return [p for p in self._data.get("recent_files", []) if os.path.exists(p)]
