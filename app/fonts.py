"""
Editor text font — bundled TTF loaded at startup (no system install).
UI chrome uses the system default font.
"""

import sys
from pathlib import Path

from PyQt6.QtGui import QFont, QFontDatabase

FONT_FILENAME = "RobotoSlab-Regular.ttf"
EDITOR_FONT_DEFAULT_SIZE = 14
FALLBACK_FONT_FAMILY = "Times New Roman"

_editor_family: str | None = None


def project_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent


def font_file_path() -> Path:
    return project_base_dir() / "font" / FONT_FILENAME


def load_editor_font() -> str:
    """Register the bundled font with Qt. Call once after QApplication exists."""
    global _editor_family
    if _editor_family is not None:
        return _editor_family

    path = font_file_path()
    if path.is_file():
        font_id = QFontDatabase.addApplicationFont(str(path))
        if font_id != -1:
            families = QFontDatabase.applicationFontFamilies(font_id)
            if families:
                _editor_family = families[0]
                return _editor_family

    _editor_family = FALLBACK_FONT_FAMILY
    return _editor_family


def editor_font_family() -> str:
    if _editor_family is None:
        load_editor_font()
    return _editor_family or FALLBACK_FONT_FAMILY


def editor_font(point_size: int) -> QFont:
    font = QFont(editor_font_family(), point_size)
    font.setStyleHint(QFont.StyleHint.Monospace)
    return font
