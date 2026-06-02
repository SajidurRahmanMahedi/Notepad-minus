"""
Editor text font — uses standard system monospace font.
UI chrome uses the system default font.
"""

from PyQt6.QtGui import QFont

EDITOR_FONT_DEFAULT_SIZE = 14
EDITOR_FONT_FAMILY = "Consolas"  # Standard Windows monospace font
FALLBACK_FONT_FAMILY = "Courier New"  # Cross-platform fallback


def editor_font_family() -> str:
    """Return the editor font family name."""
    return EDITOR_FONT_FAMILY


def editor_font(point_size: int) -> QFont:
    """Create a QFont for the editor with the given point size."""
    font = QFont(EDITOR_FONT_FAMILY, point_size)
    font.setStyleHint(QFont.StyleHint.Monospace)
    return font
