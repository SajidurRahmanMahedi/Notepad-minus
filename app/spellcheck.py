"""
Real-time spell checker using pyspellchecker.
Produces red wavy underlines via QSyntaxHighlighter.
"""

import re
import time
from typing import Set

from PyQt6.QtCore import QObject, QTimer, pyqtSignal
from PyQt6.QtGui import (
    QColor,
    QSyntaxHighlighter,
    QTextCharFormat,
    QTextDocument,
)

try:
    from spellchecker import SpellChecker
    _SPELL_AVAILABLE = True
except ImportError:
    _SPELL_AVAILABLE = False


WORD_RE = re.compile(r"\b[a-zA-Z']+\b")


def _make_squiggle_format() -> QTextCharFormat:
    """Red wavy underline character format."""
    fmt = QTextCharFormat()
    fmt.setUnderlineStyle(QTextCharFormat.UnderlineStyle.SpellCheckUnderline)
    fmt.setUnderlineColor(QColor("#FF4444"))
    return fmt


class SpellHighlighter(QSyntaxHighlighter):
    """Highlights misspelled words with a red wavy underline."""

    def __init__(self, document: QTextDocument, checker: "SpellCheckEngine"):
        super().__init__(document)
        self._checker = checker
        self._enabled = True
        self._squiggle = _make_squiggle_format()

    def setEnabled(self, enabled: bool):
        self._enabled = enabled
        self.rehighlight()

    def highlightBlock(self, text: str):
        if not self._enabled or not self._checker.available:
            return
        for m in WORD_RE.finditer(text):
            word = m.group()
            if len(word) < 2:
                continue
            if not self._checker.check(word):
                self.setFormat(m.start(), len(word), self._squiggle)


class SpellCheckEngine(QObject):
    """Wraps pyspellchecker; provides word checking and suggestions."""

    ready = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._checker = None
        self._ignored: Set[str] = set()
        self._user_words: Set[str] = set()
        self.available = False
        self._init_checker()

    def _init_checker(self):
        if not _SPELL_AVAILABLE:
            return
        try:
            self._checker = SpellChecker()
            self.available = True
            self.ready.emit()
        except Exception:
            self.available = False

    def check(self, word: str) -> bool:
        """Return True if word is correctly spelled."""
        if not self.available:
            return True
        w = word.lower().strip("'")
        if w in self._ignored or w in self._user_words:
            return True
        if len(w) <= 1:
            return True
        misspelled = self._checker.unknown([w])
        return len(misspelled) == 0

    def suggestions(self, word: str) -> list[str]:
        """Return list of spelling suggestions."""
        if not self.available:
            return []
        candidates = self._checker.candidates(word.lower())
        if not candidates:
            return []
        return sorted(candidates)[:8]

    def ignore(self, word: str):
        self._ignored.add(word.lower())

    def add_to_dictionary(self, word: str):
        self._user_words.add(word.lower())
        if self._checker:
            self._checker.word_frequency.add(word.lower())
