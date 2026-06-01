"""
Dark theme stylesheet for Notepad Minus.
"""

DARK_THEME = """
/* ── Global ──────────────────────────────────────────────── */
* {
    font-family: "Segoe UI", "Inter", sans-serif;
    font-size: 13px;
    color: #E0E0E0;
    outline: none;
}

QWidget {
    background-color: #1A1A1F;
    color: #E0E0E0;
}

/* ── Menu Bar ─────────────────────────────────────────────── */
QMenuBar {
    background-color: #16161A;
    border-bottom: 1px solid #2A2A35;
    padding: 2px 4px;
    spacing: 2px;
}

QMenuBar::item {
    background: transparent;
    padding: 5px 10px;
    border-radius: 4px;
    color: #C0C0CC;
}

QMenuBar::item:selected,
QMenuBar::item:pressed {
    background-color: #2A2A3A;
    color: #FFFFFF;
}

QMenu {
    background-color: #1E1E28;
    border: 1px solid #2E2E3E;
    border-radius: 6px;
    padding: 4px 0px;
}

QMenu::item {
    padding: 7px 28px 7px 16px;
    border-radius: 3px;
    margin: 1px 4px;
    color: #D0D0E0;
}

QMenu::item:selected {
    background-color: #3A3A55;
    color: #FFFFFF;
}

QMenu::item:disabled {
    color: #555560;
}

QMenu::separator {
    height: 1px;
    background: #2E2E3E;
    margin: 4px 10px;
}

QMenu::indicator {
    width: 14px;
    height: 14px;
    margin-left: 4px;
}

/* ── Tool Bar ─────────────────────────────────────────────── */
QToolBar {
    background-color: #16161A;
    border-bottom: 1px solid #2A2A35;
    padding: 3px 6px;
    spacing: 2px;
}

QToolBar::separator {
    width: 1px;
    background: #2E2E3E;
    margin: 3px 4px;
}

QToolButton {
    background: transparent;
    border: 1px solid transparent;
    border-radius: 5px;
    padding: 5px 7px;
    color: #C0C0CC;
    font-size: 13px;
}

QToolButton:hover {
    background-color: #2A2A3A;
    border-color: #3A3A55;
    color: #FFFFFF;
}

QToolButton:pressed {
    background-color: #35355A;
}

QToolButton:checked {
    background-color: #2E2E50;
    border-color: #5555AA;
    color: #AAAAFF;
}

/* ── Status Bar ───────────────────────────────────────────── */
QStatusBar {
    background-color: #111116;
    border-top: 1px solid #2A2A35;
    color: #888899;
    padding: 2px 8px;
    font-size: 12px;
}

QStatusBar::item {
    border: none;
}

QStatusBar QLabel {
    color: #888899;
    font-size: 12px;
    padding: 0 8px;
}

/* ── Main Editor ──────────────────────────────────────────── */
QPlainTextEdit, QTextEdit {
    background-color: #12121A;
    color: #DCDCE8;
    border: none;
    selection-background-color: #3A3A6A;
    selection-color: #FFFFFF;
    font-family: "Cascadia Code", "Consolas", "Courier New", monospace;
    font-size: 14px;
    line-height: 1.6;
    padding: 8px 4px;
}

/* ── Scrollbars ───────────────────────────────────────────── */
QScrollBar:vertical {
    background: #13131A;
    width: 12px;
    margin: 0px;
    border-radius: 6px;
    border: none;
}

QScrollBar::handle:vertical {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #3A3A55, stop:1 #454565);
    min-height: 30px;
    border-radius: 6px;
    margin: 2px;
    border: 1px solid #2A2A40;
}

QScrollBar::handle:vertical:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #5555AA, stop:1 #6666BB);
    border: 1px solid #5555CC;
}

QScrollBar::handle:vertical:pressed {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #444488, stop:1 #555599);
    border: 1px solid #4444AA;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: none;
}

QScrollBar:horizontal {
    background: #13131A;
    height: 12px;
    margin: 0px;
    border-radius: 6px;
    border: none;
}

QScrollBar::handle:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #3A3A55, stop:1 #454565);
    min-width: 30px;
    border-radius: 6px;
    margin: 2px;
    border: 1px solid #2A2A40;
}

QScrollBar::handle:horizontal:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #5555AA, stop:1 #6666BB);
    border: 1px solid #5555CC;
}

QScrollBar::handle:horizontal:pressed {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #444488, stop:1 #555599);
    border: 1px solid #4444AA;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
    background: none;
}

/* ── Dialogs ──────────────────────────────────────────────── */
QDialog {
    background-color: #1A1A24;
    border: 1px solid #2E2E3E;
    border-radius: 8px;
}

QLabel {
    color: #C0C0CC;
    background: transparent;
}

QLineEdit {
    background-color: #111118;
    border: 1px solid #3A3A50;
    border-radius: 5px;
    padding: 6px 10px;
    color: #E0E0EE;
    selection-background-color: #4444AA;
}

QLineEdit:focus {
    border-color: #6666CC;
    background-color: #13131E;
}

QPushButton {
    background-color: #2E2E48;
    border: 1px solid #4444AA;
    border-radius: 5px;
    padding: 7px 16px;
    color: #CCCCFF;
    font-weight: 500;
}

QPushButton:hover {
    background-color: #3A3A60;
    border-color: #6666CC;
    color: #FFFFFF;
}

QPushButton:pressed {
    background-color: #22224A;
}

QPushButton:default {
    background-color: #3333AA;
    border-color: #5555CC;
    color: #FFFFFF;
}

QPushButton:default:hover {
    background-color: #4444BB;
}

QPushButton:disabled {
    background-color: #202030;
    border-color: #2A2A40;
    color: #555566;
}

QCheckBox {
    color: #C0C0CC;
    spacing: 8px;
}

QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border: 1px solid #4444AA;
    border-radius: 3px;
    background: #111118;
}

QCheckBox::indicator:checked {
    background: #4444AA;
    border-color: #6666CC;
}

QCheckBox::indicator:hover {
    border-color: #6666CC;
}

QComboBox {
    background-color: #111118;
    border: 1px solid #3A3A50;
    border-radius: 5px;
    padding: 5px 10px;
    color: #E0E0EE;
}

QComboBox::drop-down {
    border: none;
    width: 20px;
}

QComboBox QAbstractItemView {
    background-color: #1E1E28;
    border: 1px solid #3A3A50;
    selection-background-color: #3A3A6A;
    color: #E0E0EE;
}

/* ── Splitter ─────────────────────────────────────────────── */
QSplitter::handle {
    background: #2A2A35;
}

/* ── Tab Widget ───────────────────────────────────────────── */
QTabWidget::pane {
    border: 1px solid #2A2A35;
    background: #1A1A1F;
}

QTabBar::tab {
    background: #16161A;
    border: 1px solid #2A2A35;
    padding: 6px 14px;
    color: #888899;
    border-bottom: none;
    border-top-left-radius: 5px;
    border-top-right-radius: 5px;
}

QTabBar::tab:selected {
    background: #1A1A1F;
    color: #E0E0EE;
    border-color: #3A3A55;
}

/* ── Spin Box ─────────────────────────────────────────────── */
QSpinBox {
    background-color: #111118;
    border: 1px solid #3A3A50;
    border-radius: 5px;
    padding: 5px 8px;
    color: #E0E0EE;
}

QSpinBox::up-button, QSpinBox::down-button {
    background: #2A2A40;
    border: none;
    width: 16px;
}

QSpinBox::up-button:hover, QSpinBox::down-button:hover {
    background: #3A3A55;
}

/* ── Tooltip ──────────────────────────────────────────────── */
QToolTip {
    background-color: #1E1E2E;
    border: 1px solid #4444AA;
    color: #E0E0EE;
    padding: 5px 8px;
    border-radius: 4px;
}
"""


TITLE_BAR_STYLE = """
QWidget#TitleBar {
    background-color: #111116;
    border-bottom: 1px solid #2A2A35;
}
"""
