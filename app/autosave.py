"""
Auto-save manager — debounced save on every key press.
Unsaved new files are written to a recovery file.
"""

import os
from pathlib import Path

from PyQt6.QtCore import QObject, QTimer, pyqtSignal


class AutoSaveManager(QObject):
    saved = pyqtSignal(str)       # emits the path that was saved
    save_failed = pyqtSignal(str) # emits error message

    def __init__(self, parent=None, delay_ms: int = 0):
        super().__init__(parent)
        self._delay = delay_ms
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._do_save)

        self._get_content = None   # callable -> str
        self._get_path = None      # callable -> str | None
        self._encoding = "utf-8"
        self._recovery_path = self._make_recovery_path()

    @staticmethod
    def _make_recovery_path() -> Path:
        app_data = os.environ.get("APPDATA", str(Path.home()))
        rec_dir = Path(app_data) / "NotepadMinus" / "recovery"
        rec_dir.mkdir(parents=True, exist_ok=True)
        return rec_dir / "unsaved_recovery.txt"

    def setup(self, get_content_fn, get_path_fn):
        """
        get_content_fn: callable() -> str   (current editor text)
        get_path_fn:    callable() -> str|None (current file path)
        """
        self._get_content = get_content_fn
        self._get_path = get_path_fn

    def set_encoding(self, encoding: str):
        self._encoding = encoding

    def trigger(self):
        """Call this on every key press — starts/restarts the debounce timer or saves immediately if delay is 0."""
        if self._delay == 0:
            self._do_save()
        else:
            self._timer.start(self._delay)

    def flush(self):
        """Immediately save without waiting for debounce."""
        self._timer.stop()
        self._do_save()

    def _do_save(self):
        if self._get_content is None or self._get_path is None:
            return

        content = self._get_content()
        path = self._get_path()
        encoding = self._encoding.lower().replace("-", "")

        # Map common encoding names
        encoding_map = {"utf8": "utf-8", "utf16": "utf-16", "ansi": "cp1252"}
        encoding = encoding_map.get(encoding, encoding)

        save_path = path if path else str(self._recovery_path)

        try:
            with open(save_path, "w", encoding=encoding, newline="") as f:
                f.write(content)
            self.saved.emit(save_path)
        except Exception as e:
            self.save_failed.emit(str(e))
