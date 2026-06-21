"""
VS Code-style inline Find & Replace widget.

Overlays the top-right corner of the editor pane.  Features:
  • Live match highlighting as-you-type with "N of M" counter
  • Enter / Shift+Enter  →  next / previous match
  • Toggle buttons: Match Case, Whole Word, Regex
  • Collapsible Replace row
  • Escape to close
  • No separate floating window — widget is a child of the editor
"""

import re
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import (
    QColor, QTextCharFormat, QTextCursor,
)
from PyQt6.QtWidgets import (
    QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QToolButton, QVBoxLayout, QWidget, QFrame,
)


# ── Highlight colours ─────────────────────────────────────────────────────────

_FMT_ALL = QTextCharFormat()
_FMT_ALL.setBackground(QColor("#4E4000"))       # dimmed yellow for all matches
_FMT_ALL.setForeground(QColor("#FFE082"))

_FMT_CURRENT = QTextCharFormat()
_FMT_CURRENT.setBackground(QColor("#FFB300"))   # vivid amber for current match
_FMT_CURRENT.setForeground(QColor("#1A1A1A"))


# ── Small icon-style toggle button ────────────────────────────────────────────

_TOGGLE_SS = """
    QToolButton {{
        background: {bg};
        border: 1px solid {border};
        border-radius: 4px;
        color: {fg};
        font-size: 11px;
        padding: 0 5px;
        min-width: 22px;
        min-height: 22px;
        max-height: 22px;
    }}
    QToolButton:hover {{
        background: #2E2E4A;
        border-color: #5555AA;
        color: #FFFFFF;
    }}
"""

def _toggle_btn(label: str, tooltip: str) -> QToolButton:
    btn = QToolButton()
    btn.setText(label)
    btn.setToolTip(tooltip)
    btn.setCheckable(True)
    btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
    btn.toggled.connect(lambda checked, b=btn: b.setStyleSheet(
        _TOGGLE_SS.format(
            bg="#3A3A6A" if checked else "transparent",
            border="#5555AA" if checked else "#3A3A50",
            fg="#CCCCFF" if checked else "#888899",
        )
    ))
    btn.setStyleSheet(_TOGGLE_SS.format(
        bg="transparent", border="#3A3A50", fg="#888899",
    ))
    return btn


def _icon_btn(label: str, tooltip: str) -> QToolButton:
    """Small flat action button (non-toggle)."""
    btn = QToolButton()
    btn.setText(label)
    btn.setToolTip(tooltip)
    btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
    btn.setStyleSheet("""
        QToolButton {
            background: transparent;
            border: 1px solid transparent;
            border-radius: 4px;
            color: #888899;
            font-size: 13px;
            min-width: 22px;
            min-height: 22px;
            max-height: 22px;
            padding: 0 3px;
        }
        QToolButton:hover {
            background: #2A2A3E;
            border-color: #4A4A70;
            color: #DDDDFF;
        }
        QToolButton:pressed {
            background: #22223A;
        }
        QToolButton:disabled {
            color: #3A3A50;
        }
    """)
    return btn


# ── Single-line editor that catches Enter / Shift+Enter / Escape ──────────────

class _SearchEdit(QLineEdit):
    def __init__(self, placeholder: str, parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setStyleSheet("""
            QLineEdit {
                background-color: #0E0E16;
                border: 1px solid #3A3A50;
                border-radius: 4px;
                padding: 3px 8px;
                color: #E0E0EE;
                font-size: 13px;
                min-height: 24px;
                max-height: 24px;
            }
            QLineEdit:focus {
                border-color: #5555CC;
                background-color: #111120;
            }
        """)

    def keyPressEvent(self, event):
        # Let parent widget intercept Enter / Escape
        key = event.key()
        if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter,
                   Qt.Key.Key_Escape, Qt.Key.Key_Tab):
            self.parent().keyPressEvent(event)
            return
        super().keyPressEvent(event)


# ══════════════════════════════════════════════════════════════════════════════
#  Main widget
# ══════════════════════════════════════════════════════════════════════════════

class FindReplaceWidget(QWidget):
    """
    Inline VS Code-style find/replace overlay.
    Parent must be the editor (QPlainTextEdit).
    Call show_and_focus() / hide_widget() to control visibility.
    """

    _WIDGET_WIDTH  = 430
    _FIND_HEIGHT   = 42   # single-row height (with padding)
    _TOTAL_HEIGHT  = 82   # two-row height

    def __init__(self, editor, parent=None):
        super().__init__(parent)
        self._editor = editor
        self._matches: list[tuple[int, int]] = []
        self._current_idx: int = -1
        self._replace_visible = False

        # Debounce re-search so we don't hammer on every keystroke
        self._search_timer = QTimer(self)
        self._search_timer.setSingleShot(True)
        self._search_timer.setInterval(80)
        self._search_timer.timeout.connect(self._run_search)

        self._build_ui()
        self.hide()

    # ── UI construction ───────────────────────────────────────────────────────

    def _build_ui(self):
        self.setObjectName("FindReplaceWidget")
        self.setStyleSheet("""
            QWidget#FindReplaceWidget {
                background-color: #16161E;
                border: 1px solid #2E2E48;
                border-top: none;
                border-radius: 0 0 6px 6px;
            }
        """)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(8, 6, 8, 6)
        outer.setSpacing(4)

        # ── Find row ──────────────────────────────────────────────────────────
        find_row = QHBoxLayout()
        find_row.setSpacing(4)

        # Expand/collapse replace
        self._btn_expand = _icon_btn("›", "Toggle Replace (Alt+R)")
        self._btn_expand.setStyleSheet(self._btn_expand.styleSheet() + """
            QToolButton { font-size: 16px; font-weight: bold; }
        """)
        self._btn_expand.clicked.connect(self._toggle_replace)
        find_row.addWidget(self._btn_expand)

        # Search input
        self._find_edit = _SearchEdit("Find")
        self._find_edit.setParent(self)  # needed so key events bubble correctly
        self._find_edit.textChanged.connect(self._on_text_changed)
        find_row.addWidget(self._find_edit, 1)

        # Match counter label
        self._lbl_count = QLabel("")
        self._lbl_count.setStyleSheet("color: #666680; font-size: 11px; min-width: 50px;")
        self._lbl_count.setAlignment(Qt.AlignmentFlag.AlignCenter)
        find_row.addWidget(self._lbl_count)

        # Option toggles
        self._btn_case  = _toggle_btn("Aa", "Match Case (Alt+C)")
        self._btn_word  = _toggle_btn("ab", "Whole Word (Alt+W)")
        self._btn_regex = _toggle_btn(".*", "Use Regular Expression (Alt+E)")
        for b in (self._btn_case, self._btn_word, self._btn_regex):
            b.toggled.connect(lambda _: self._on_text_changed())
            find_row.addWidget(b)

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.VLine)
        sep.setStyleSheet("color: #2E2E48; max-width: 1px;")
        find_row.addWidget(sep)

        # Navigation buttons
        self._btn_prev = _icon_btn("↑", "Previous Match (Shift+Enter)")
        self._btn_next = _icon_btn("↓", "Next Match (Enter)")
        self._btn_prev.clicked.connect(self._find_prev)
        self._btn_next.clicked.connect(self._find_next)
        find_row.addWidget(self._btn_prev)
        find_row.addWidget(self._btn_next)

        # Close
        self._btn_close = _icon_btn("✕", "Close (Escape)")
        self._btn_close.clicked.connect(self.hide_widget)
        find_row.addWidget(self._btn_close)

        outer.addLayout(find_row)

        # ── Replace row (hidden by default) ───────────────────────────────────
        self._replace_row_widget = QWidget()
        self._replace_row_widget.setStyleSheet("background: transparent;")
        replace_row = QHBoxLayout(self._replace_row_widget)
        replace_row.setContentsMargins(26, 0, 0, 0)   # indent to align under search field
        replace_row.setSpacing(4)

        self._replace_edit = _SearchEdit("Replace")
        self._replace_edit.setParent(self)
        replace_row.addWidget(self._replace_edit, 1)

        _replace_btn_ss = """
            QPushButton {
                background: #222238;
                border: 1px solid #3A3A58;
                border-radius: 4px;
                color: #AAAACC;
                font-size: 11px;
                padding: 0 10px;
            }
            QPushButton:hover {
                background: #2E2E50;
                border-color: #5555AA;
                color: #DDDDFF;
            }
            QPushButton:pressed { background: #1A1A30; }
        """
        self._btn_replace_one = QPushButton("Replace")
        self._btn_replace_all = QPushButton("All")
        for btn in (self._btn_replace_one, self._btn_replace_all):
            btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            btn.setFixedHeight(24)
            btn.setStyleSheet(_replace_btn_ss)
        self._btn_replace_one.clicked.connect(self._replace_once)
        self._btn_replace_all.clicked.connect(self._replace_all)
        replace_row.addWidget(self._btn_replace_one)
        replace_row.addWidget(self._btn_replace_all)
        replace_row.addStretch()

        self._replace_row_widget.setVisible(False)
        outer.addWidget(self._replace_row_widget)

    # ── Geometry management ───────────────────────────────────────────────────

    def _reposition(self):
        """Anchor to the top-right of the editor's viewport."""
        if self.parentWidget() is None:
            return
        pw = self.parentWidget()
        # Account for scrollbar width if visible
        vbar = self._editor.verticalScrollBar()
        sb_w = vbar.width() if vbar.isVisible() else 0
        w = min(self._WIDGET_WIDTH, pw.width() - 20)
        h = self._TOTAL_HEIGHT if self._replace_visible else self._FIND_HEIGHT
        x = pw.width() - w - sb_w - 2
        self.setGeometry(x, 0, w, h)

    def resizeEvent(self, event):
        super().resizeEvent(event)

    # ── Show / hide ───────────────────────────────────────────────────────────

    def show_and_focus(self, selected_text: str = ""):
        self._reposition()
        self.show()
        self.raise_()
        self._find_edit.setFocus()
        if selected_text:
            self._find_edit.setText(selected_text)
            self._find_edit.selectAll()
        else:
            self._find_edit.selectAll()
        self._run_search()

    def hide_widget(self):
        self._clear_highlights()
        self.hide()
        self._editor.setFocus()

    # ── Replace row toggle ────────────────────────────────────────────────────

    def _toggle_replace(self):
        self._replace_visible = not self._replace_visible
        self._replace_row_widget.setVisible(self._replace_visible)
        self._btn_expand.setText("⌄" if self._replace_visible else "›")
        self._reposition()
        if self._replace_visible:
            self._replace_edit.setFocus()

    # ── Key handling ─────────────────────────────────────────────────────────

    def keyPressEvent(self, event):
        key = event.key()
        mods = event.modifiers()

        if key == Qt.Key.Key_Escape:
            self.hide_widget()
        elif key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            if mods & Qt.KeyboardModifier.ShiftModifier:
                self._find_prev()
            else:
                self._find_next()
        elif key == Qt.Key.Key_Tab:
            # cycle between find and replace fields
            if self._replace_visible:
                if self._find_edit.hasFocus():
                    self._replace_edit.setFocus()
                else:
                    self._find_edit.setFocus()
        else:
            super().keyPressEvent(event)

    # ── Search logic ─────────────────────────────────────────────────────────

    def _on_text_changed(self):
        self._search_timer.start()

    def _build_flags(self) -> re.RegexFlag:
        flags = re.MULTILINE
        if not self._btn_case.isChecked():
            flags |= re.IGNORECASE
        return flags

    def _make_pattern(self, text: str) -> re.Pattern | None:
        if not text:
            return None
        try:
            if self._btn_regex.isChecked():
                pat = text
            else:
                pat = re.escape(text)
            if self._btn_word.isChecked():
                pat = r"\b" + pat + r"\b"
            return re.compile(pat, self._build_flags())
        except re.error:
            return None

    def _run_search(self):
        """Rebuild match list and redraw all highlights."""
        self._clear_highlights()
        query = self._find_edit.text()
        pattern = self._make_pattern(query)

        # Visual feedback for invalid state
        if query and pattern is None:
            self._find_edit.setStyleSheet(self._find_edit.styleSheet().replace(
                "border: 1px solid #3A3A50", "border: 1px solid #AA3333"
            ))
            self._lbl_count.setText("!")
            return
        else:
            self._find_edit.setStyleSheet("""
                QLineEdit {
                    background-color: #0E0E16;
                    border: 1px solid #3A3A50;
                    border-radius: 4px;
                    padding: 3px 8px;
                    color: #E0E0EE;
                    font-size: 13px;
                    min-height: 24px;
                    max-height: 24px;
                }
                QLineEdit:focus {
                    border-color: #5555CC;
                    background-color: #111120;
                }
            """)

        if not pattern:
            self._matches = []
            self._current_idx = -1
            self._lbl_count.setText("")
            self._btn_prev.setEnabled(False)
            self._btn_next.setEnabled(False)
            return

        text = self._editor.toPlainText()
        self._matches = [(m.start(), m.end()) for m in pattern.finditer(text)]

        if not self._matches:
            self._lbl_count.setText("No results")
            self._lbl_count.setStyleSheet("color: #AA4444; font-size: 11px; min-width: 70px;")
            self._btn_prev.setEnabled(False)
            self._btn_next.setEnabled(False)
            return

        self._lbl_count.setStyleSheet("color: #666680; font-size: 11px; min-width: 50px;")
        self._btn_prev.setEnabled(True)
        self._btn_next.setEnabled(True)

        # Find nearest match to current cursor
        cursor_pos = self._editor.textCursor().position()
        best = 0
        for i, (s, e) in enumerate(self._matches):
            if s >= cursor_pos:
                best = i
                break
        else:
            best = 0
        self._current_idx = best

        self._apply_highlights()

    def _apply_highlights(self):
        """Paint all matches (dim) and the current match (bright)."""
        from PyQt6.QtWidgets import QTextEdit
        selections = []

        for i, (start, end) in enumerate(self._matches):
            fmt = _FMT_CURRENT if i == self._current_idx else _FMT_ALL
            selections.append(self._make_extra_selection(start, end, fmt))

        self._editor.setExtraSelections(selections)

        # Scroll to current match
        if self._matches and 0 <= self._current_idx < len(self._matches):
            s, e = self._matches[self._current_idx]
            cur = self._editor.textCursor()
            cur.setPosition(s)
            cur.setPosition(e, QTextCursor.MoveMode.KeepAnchor)
            self._editor.setTextCursor(cur)
            self._editor.ensureCursorVisible()
            n = len(self._matches)
            self._lbl_count.setText(f"{self._current_idx + 1} of {n}")

    def _make_extra_selection(self, start: int, end: int, fmt: QTextCharFormat):
        from PyQt6.QtWidgets import QTextEdit
        sel = QTextEdit.ExtraSelection()
        cur = self._editor.textCursor()
        cur.setPosition(start)
        cur.setPosition(end, QTextCursor.MoveMode.KeepAnchor)
        sel.cursor = cur
        sel.format = fmt
        return sel

    def _clear_highlights(self):
        """Remove find highlights and restore the editor's current-line highlight."""
        self._editor.setExtraSelections([])
        # Trigger the editor's own current-line highlighter to restore its selection
        if hasattr(self._editor, '_highlight_current_line'):
            self._editor._highlight_current_line()

    # ── Navigation ────────────────────────────────────────────────────────────

    def _find_next(self):
        if not self._matches:
            self._run_search()
            return
        self._current_idx = (self._current_idx + 1) % len(self._matches)
        self._apply_highlights()

    def _find_prev(self):
        if not self._matches:
            self._run_search()
            return
        self._current_idx = (self._current_idx - 1) % len(self._matches)
        self._apply_highlights()

    # ── Replace ───────────────────────────────────────────────────────────────

    def _replace_once(self):
        if not self._matches or self._current_idx < 0:
            return
        pattern = self._make_pattern(self._find_edit.text())
        if not pattern:
            return
        s, e = self._matches[self._current_idx]
        text = self._editor.toPlainText()
        match_text = text[s:e]
        replacement = pattern.sub(self._replace_edit.text(), match_text, count=1)
        cur = self._editor.textCursor()
        cur.setPosition(s)
        cur.setPosition(e, QTextCursor.MoveMode.KeepAnchor)
        cur.insertText(replacement)
        # Re-search after modification
        QTimer.singleShot(0, self._run_search)

    def _replace_all(self):
        pattern = self._make_pattern(self._find_edit.text())
        if not pattern:
            return
        text = self._editor.toPlainText()
        new_text, count = pattern.subn(self._replace_edit.text(), text)
        if count:
            cur = self._editor.textCursor()
            cur.select(QTextCursor.SelectionType.Document)
            cur.insertText(new_text)
            self._lbl_count.setText(f"Replaced {count}")
            QTimer.singleShot(1500, lambda: self._lbl_count.setText(""))
            QTimer.singleShot(0, self._run_search)

    # ── Public API (compatibility shim for window.py) ─────────────────────────

    def set_search_term(self, text: str):
        self._find_edit.setText(text)

    def show_replace(self):
        if not self._replace_visible:
            self._toggle_replace()


# ── Backwards-compat alias kept so old imports still work ────────────────────

FindReplaceDialog = FindReplaceWidget
