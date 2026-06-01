"""
Core editor widget with:
- Line number gutter
- Current-line highlight
- Real-time spell check (red wavy underlines)
- Right-click spelling suggestions
- Zoom via Ctrl+Scroll
- Tab / indent helpers
"""

import re
from PyQt6.QtCore import (
    QPoint, QRect, QSize, Qt, pyqtSignal, QTimer,
)
from PyQt6.QtGui import (
    QColor, QFont, QFontMetrics, QPainter, QPen,
    QTextCursor, QTextOption, QKeySequence, QTextCharFormat,
    QPalette,
)
from PyQt6.QtWidgets import (
    QMenu, QPlainTextEdit, QTextEdit, QWidget, QApplication,
)

from .spellcheck import SpellCheckEngine, SpellHighlighter, WORD_RE


# ── Line-number gutter ────────────────────────────────────────────────────────

class _LineNumberArea(QWidget):
    def __init__(self, editor: "CodeEditor"):
        super().__init__(editor)
        self._editor = editor

    def sizeHint(self) -> QSize:
        return QSize(self._editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        self._editor.line_number_area_paint_event(event)


# ── Main editor ───────────────────────────────────────────────────────────────

class CodeEditor(QPlainTextEdit):
    """
    A QPlainTextEdit with line numbers, current-line highlight,
    spell-check underlines, and right-click suggestions.
    """

    zoom_changed = pyqtSignal(int)           # emits current font size
    spell_check_toggle = pyqtSignal(bool)

    def __init__(self, spell_engine: SpellCheckEngine, parent=None):
        super().__init__(parent)
        self._spell_engine = spell_engine
        self._spell_enabled = True
        self._base_font_size = 14
        self._current_zoom = 0  # steps

        # Line number area
        self._line_area = _LineNumberArea(self)

        # Spell highlighter
        self._highlighter = SpellHighlighter(self.document(), spell_engine)

        # Debounce timer for rehighlight after edits
        self._rehighlight_timer = QTimer(self)
        self._rehighlight_timer.setSingleShot(True)
        self._rehighlight_timer.setInterval(350)
        self._rehighlight_timer.timeout.connect(self._highlighter.rehighlight)

        # Connections
        self.blockCountChanged.connect(self._update_line_area_width)
        self.updateRequest.connect(self._update_line_area)
        self.cursorPositionChanged.connect(self._highlight_current_line)
        self.document().contentsChanged.connect(self._on_contents_changed)

        self._update_line_area_width(0)
        self._highlight_current_line()
        self._apply_font()

    # ── Font / Zoom ──────────────────────────────────────────────────────────

    def _apply_font(self):
        font = QFont("Consolas", self._base_font_size + self._current_zoom)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.setFont(font)
        self._update_line_area_width(0)

    def set_editor_font(self, family: str, size: int):
        self._base_font_size = size
        font = QFont(family, size + self._current_zoom)
        self.setFont(font)
        self._update_line_area_width(0)

    def zoom_in(self, steps: int = 1):
        self._current_zoom = min(self._current_zoom + steps, 40)
        self._apply_font()
        self.zoom_changed.emit(self._base_font_size + self._current_zoom)

    def zoom_out(self, steps: int = 1):
        self._current_zoom = max(self._current_zoom - steps, -8)
        self._apply_font()
        self.zoom_changed.emit(self._base_font_size + self._current_zoom)

    def zoom_reset(self):
        self._current_zoom = 0
        self._apply_font()
        self.zoom_changed.emit(self._base_font_size)

    def current_font_size(self) -> int:
        return self._base_font_size + self._current_zoom

    def wheelEvent(self, event):
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            delta = event.angleDelta().y()
            if delta > 0:
                self.zoom_in()
            else:
                self.zoom_out()
            event.accept()
            return
        super().wheelEvent(event)

    # ── Spell check ──────────────────────────────────────────────────────────

    def set_spell_check(self, enabled: bool):
        self._spell_enabled = enabled
        self._highlighter.setEnabled(enabled)

    def _on_contents_changed(self):
        self._rehighlight_timer.start()

    # ── Word under cursor helper ──────────────────────────────────────────────

    def _word_at_cursor(self, pos: QPoint) -> tuple[str, int, int] | None:
        """Return (word, start_pos, end_pos) for the word at viewport pos."""
        cursor = self.cursorForPosition(pos)
        cursor.select(QTextCursor.SelectionType.WordUnderCursor)
        word = cursor.selectedText()
        if not word or not re.match(r"[a-zA-Z']+", word):
            return None
        return word, cursor.selectionStart(), cursor.selectionEnd()

    # ── Context menu (spell suggestions) ─────────────────────────────────────

    def contextMenuEvent(self, event):
        std_menu = self.createStandardContextMenu()

        if self._spell_enabled and self._spell_engine.available:
            info = self._word_at_cursor(event.pos())
            if info:
                word, start, end = info
                if not self._spell_engine.check(word):
                    suggestions = self._spell_engine.suggestions(word)

                    spell_menu = QMenu("Spelling", self)
                    spell_menu.setTitle(f'"{word}" — Suggestions')

                    if suggestions:
                        for sug in suggestions:
                            act = spell_menu.addAction(sug)
                            # capture sug + positions in closure
                            act.triggered.connect(
                                lambda checked=False, s=sug, st=start, en=end:
                                self._replace_word(st, en, s)
                            )
                    else:
                        no_act = spell_menu.addAction("No suggestions")
                        no_act.setEnabled(False)

                    spell_menu.addSeparator()
                    ig_act = spell_menu.addAction(f'Ignore "{word}"')
                    ig_act.triggered.connect(
                        lambda: self._ignore_word(word)
                    )
                    add_act = spell_menu.addAction(f'Add "{word}" to Dictionary')
                    add_act.triggered.connect(
                        lambda: self._add_word(word)
                    )

                    # Prepend spell menu to standard menu
                    first = std_menu.actions()[0] if std_menu.actions() else None
                    std_menu.insertMenu(first, spell_menu)
                    std_menu.insertSeparator(first)

        std_menu.exec(event.globalPos())

    def _replace_word(self, start: int, end: int, replacement: str):
        cur = self.textCursor()
        cur.setPosition(start)
        cur.setPosition(end, QTextCursor.MoveMode.KeepAnchor)
        cur.insertText(replacement)

    def _ignore_word(self, word: str):
        self._spell_engine.ignore(word)
        self._highlighter.rehighlight()

    def _add_word(self, word: str):
        self._spell_engine.add_to_dictionary(word)
        self._highlighter.rehighlight()

    # ── Line number area ──────────────────────────────────────────────────────

    def line_number_area_width(self) -> int:
        digits = max(1, len(str(self.blockCount())))
        fm = QFontMetrics(self.font())
        space = 12 + fm.horizontalAdvance("9") * digits
        return space

    def _update_line_area_width(self, _):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def _update_line_area(self, rect: QRect, dy: int):
        if dy:
            self._line_area.scroll(0, dy)
        else:
            self._line_area.update(0, rect.y(),
                                   self._line_area.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self._update_line_area_width(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self._line_area.setGeometry(
            QRect(cr.left(), cr.top(),
                  self.line_number_area_width(), cr.height())
        )

    def line_number_area_paint_event(self, event):
        painter = QPainter(self._line_area)
        painter.fillRect(event.rect(), QColor("#13131A"))

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = round(
            self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        )
        bottom = top + round(self.blockBoundingRect(block).height())

        current_line = self.textCursor().blockNumber()

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                if block_number == current_line:
                    painter.setPen(QColor("#8888FF"))
                else:
                    painter.setPen(QColor("#44445A"))
                painter.setFont(self.font())
                painter.drawText(
                    0, top,
                    self._line_area.width() - 6,
                    self.fontMetrics().height(),
                    Qt.AlignmentFlag.AlignRight,
                    number,
                )
            block = block.next()
            top = bottom
            bottom = top + round(self.blockBoundingRect(block).height())
            block_number += 1

    # ── Current-line highlight ────────────────────────────────────────────────

    def _highlight_current_line(self):
        extra = []
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            line_color = QColor("#1E1E2E")
            selection.format.setBackground(line_color)
            selection.format.setProperty(
                QTextCharFormat.Property.FullWidthSelection, True
            )
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extra.append(selection)
        self.setExtraSelections(extra)

    # ── Key handling ─────────────────────────────────────────────────────────

    def keyPressEvent(self, event):
        # Smart tab: insert spaces
        if event.key() == Qt.Key.Key_Tab:
            cur = self.textCursor()
            if cur.hasSelection():
                self._indent_selection(cur)
            else:
                cur.insertText("    ")
            return

        # Smart back-tab (Shift+Tab): unindent
        if event.key() == Qt.Key.Key_Backtab:
            cur = self.textCursor()
            self._unindent_selection(cur)
            return

        super().keyPressEvent(event)

    def _indent_selection(self, cursor: QTextCursor):
        start = cursor.selectionStart()
        end = cursor.selectionEnd()
        cursor.setPosition(start)
        cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
        cursor.beginEditBlock()
        while cursor.position() <= end:
            cursor.insertText("    ")
            end += 4
            if not cursor.movePosition(QTextCursor.MoveOperation.NextBlock):
                break
        cursor.endEditBlock()

    def _unindent_selection(self, cursor: QTextCursor):
        start = cursor.selectionStart()
        end = cursor.selectionEnd()
        cursor.setPosition(start)
        cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
        cursor.beginEditBlock()
        while cursor.position() <= end:
            line_cursor = self.textCursor()
            line_cursor.setPosition(cursor.position())
            line_cursor.select(QTextCursor.SelectionType.LineUnderCursor)
            line_text = line_cursor.selectedText()
            spaces = len(line_text) - len(line_text.lstrip(" "))
            remove = min(spaces, 4)
            if remove:
                for _ in range(remove):
                    cursor.deleteChar()
                end -= remove
            if not cursor.movePosition(QTextCursor.MoveOperation.NextBlock):
                break
        cursor.endEditBlock()

    # ── Word wrap ─────────────────────────────────────────────────────────────

    def set_word_wrap(self, enabled: bool):
        if enabled:
            self.setWordWrapMode(QTextOption.WrapMode.WrapAtWordBoundaryOrAnywhere)
        else:
            self.setWordWrapMode(QTextOption.WrapMode.NoWrap)

    # ── Stat helpers ──────────────────────────────────────────────────────────

    def word_count(self) -> int:
        return len(self.toPlainText().split())

    def char_count(self) -> int:
        return len(self.toPlainText())

    def current_line_col(self) -> tuple[int, int]:
        cur = self.textCursor()
        return cur.blockNumber() + 1, cur.columnNumber() + 1
