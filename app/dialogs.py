from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QSpinBox, QWidget, QComboBox, QRadioButton,
    QButtonGroup, QFrame, QScrollArea
)
from PyQt6.QtPrintSupport import QPrinter, QPrinterInfo
from PyQt6.QtGui import QPageSize, QPageLayout

class _FramelessDialog(QDialog):
    def __init__(self, parent=None, title=""):
        super().__init__(parent, Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self._drag_pos = None
        self._title = title
        
    def _setup_header(self, layout):
        title_bar = QWidget()
        title_bar.setObjectName("DialogTitleBar")
        title_bar.setFixedHeight(32)
        title_bar.setStyleSheet("""
            QWidget#DialogTitleBar {
                background-color: #16161C;
                border-bottom: 1px solid #2D2D3F;
            }
        """)

        tb_layout = QHBoxLayout(title_bar)
        tb_layout.setContentsMargins(12, 0, 0, 0)
        tb_layout.setSpacing(0)

        title_lbl = QLabel(self._title)
        title_lbl.setStyleSheet("color: #CCCCDD;")
        tb_layout.addWidget(title_lbl)
        tb_layout.addStretch(1)

        close_btn = QPushButton("\u00D7")
        close_btn.setFixedSize(36, 32)
        close_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #8888A0;
            }
            QPushButton:hover {
                background-color: #C0392B;
                color: #FFFFFF;
            }
        """)
        close_btn.clicked.connect(self.reject)
        tb_layout.addWidget(close_btn)

        layout.addWidget(title_bar)

        # Drag handlers
        def tb_mousePress(event):
            if event.button() == Qt.MouseButton.LeftButton:
                self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

        def tb_mouseMove(event):
            if (event.buttons() & Qt.MouseButton.LeftButton) and self._drag_pos is not None:
                self.move(event.globalPosition().toPoint() - self._drag_pos)

        def tb_mouseRelease(event):
            self._drag_pos = None

        title_bar.mousePressEvent = tb_mousePress
        title_bar.mouseMoveEvent = tb_mouseMove
        title_bar.mouseReleaseEvent = tb_mouseRelease

class DarkMessageBox(_FramelessDialog):
    def __init__(self, parent=None, title="", text="", buttons=None, icon_color="#5B5BFF"):
        super().__init__(parent, title)
        self.setMinimumWidth(380)
        
        master_layout = QVBoxLayout(self)
        master_layout.setContentsMargins(0, 0, 0, 0)
        master_layout.setSpacing(0)
        
        self._setup_header(master_layout)
        
        body = QWidget()
        body.setStyleSheet("background-color: #1A1A24; border: 1px solid #2E2E3E; border-top: none;")
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(20, 20, 20, 16)
        body_layout.setSpacing(16)
        
        content_layout = QHBoxLayout()
        content_layout.setSpacing(16)
        
        # Icon
        self.icon_lbl = QLabel("ℹ")
        self.icon_lbl.setStyleSheet(f"color: {icon_color};")
        self.icon_lbl.setAlignment(Qt.AlignmentFlag.AlignTop)
        content_layout.addWidget(self.icon_lbl)
        
        # Text
        self.text_lbl = QLabel(text)
        self.text_lbl.setStyleSheet("color: #E0E0EE;")
        self.text_lbl.setWordWrap(True)
        content_layout.addWidget(self.text_lbl, 1)
        
        body_layout.addLayout(content_layout)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)
        btn_layout.addStretch(1)
        
        self.result_button = None
        
        if buttons is None:
            buttons = [("OK", QDialog.DialogCode.Accepted, True)]
            
        for text, code, is_default in buttons:
            btn = QPushButton(text)
            if is_default:
                btn.setDefault(True)
            # Apply styling
            btn.clicked.connect(lambda checked=False, c=code: self.finish_dialog(c))
            btn_layout.addWidget(btn)
            
        body_layout.addLayout(btn_layout)
        master_layout.addWidget(body)
        
    def finish_dialog(self, code):
        self.result_button = code
        self.done(code)
        
    @classmethod
    def question(cls, parent, title, text):
        dialog = cls(
            parent, title, text,
            buttons=[
                ("Save", 1, True),
                ("Don't Save", 2, False),
                ("Cancel", 0, False)
            ],
            icon_color="#FFAA44"
        )
        dialog.exec()
        return dialog.result_button
        
    @classmethod
    def critical(cls, parent, title, text):
        dialog = cls(
            parent, title, text,
            buttons=[("OK", 1, True)],
            icon_color="#FF4444"
        )
        dialog.exec()
        
    @classmethod
    def about(cls, parent, title, html_text):
        dialog = cls(
            parent, title, "",
            buttons=[("Close", 1, True)],
            icon_color="#8B5CF6"
        )
        # Use HTML for text label
        dialog.text_lbl.setText(html_text)
        dialog.exec()

class DarkInputDialog(_FramelessDialog):
    def __init__(self, parent=None, title="", label_text="", value=1, min_val=1, max_val=100):
        super().__init__(parent, title)
        self.setMinimumWidth(320)
        
        master_layout = QVBoxLayout(self)
        master_layout.setContentsMargins(0, 0, 0, 0)
        master_layout.setSpacing(0)
        
        self._setup_header(master_layout)
        
        body = QWidget()
        body.setStyleSheet("background-color: #1A1A24; border: 1px solid #2E2E3E; border-top: none;")
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(20, 20, 20, 16)
        body_layout.setSpacing(12)
        
        lbl = QLabel(label_text)
        lbl.setStyleSheet("color: #E0E0EE;")
        body_layout.addWidget(lbl)
        
        self.spin = QSpinBox()
        self.spin.setRange(min_val, max_val)
        self.spin.setValue(value)
        self.spin.setStyleSheet(_INPUT_STYLE)
        body_layout.addWidget(self.spin)
        
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)
        btn_layout.addStretch(1)
        
        ok_btn = QPushButton("OK")
        ok_btn.setDefault(True)
        ok_btn.clicked.connect(self.accept)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        body_layout.addLayout(btn_layout)
        
        master_layout.addWidget(body)
        
    @classmethod
    def getInt(cls, parent, title, label_text, value, min_val, max_val):
        dialog = cls(parent, title, label_text, value, min_val, max_val)
        res = dialog.exec()
        return dialog.spin.value(), (res == QDialog.DialogCode.Accepted)


_INPUT_STYLE = """
    QLineEdit, QSpinBox, QComboBox {
        background-color: #111118;
        border: 1px solid #3A3A50;
        border-radius: 5px;
        padding: 6px 10px;
        color: #E0E0EE;
    }
    QLineEdit:focus, QSpinBox:focus, QComboBox:focus {
        border-color: #5B5BFF;
    }
    QComboBox::drop-down {
        border: none;
    }
    QComboBox::down-arrow {
        image: none;
        border-left: 5px solid transparent;
        border-right: 5px solid transparent;
        border-top: 5px solid #8888A0;
        margin-right: 5px;
    }
"""

_BUTTON_STYLE = """
    QPushButton {
        background-color: #2D2D3F;
        border: 1px solid #3A3A50;
        border-radius: 5px;
        padding: 8px 16px;
        color: #E0E0EE;
        min-width: 80px;
    }
    QPushButton:hover {
        background-color: #3D3D4F;
        border-color: #5B5BFF;
    }
    QPushButton:pressed {
        background-color: #1D1D2F;
    }
    QPushButton:default {
        background-color: #5B5BFF;
        border-color: #7B7BFF;
    }
    QPushButton:default:hover {
        background-color: #6B6BFF;
    }
"""

_RADIO_STYLE = """
    QRadioButton {
        color: #E0E0EE;
        spacing: 8px;
    }
    QRadioButton::indicator {
        width: 16px;
        height: 16px;
        border: 2px solid #3A3A50;
        border-radius: 8px;
        background-color: #111118;
    }
    QRadioButton::indicator:checked {
        background-color: #5B5BFF;
        border-color: #5B5BFF;
    }
    QRadioButton::indicator:hover {
        border-color: #7B7BFF;
    }
"""


class CustomPrintDialog(_FramelessDialog):
    """Custom dark-themed print dialog with preview."""

    def __init__(self, parent=None, document=None):
        super().__init__(parent, "Print")
        self.setMinimumSize(900, 600)
        self._document = document
        self._printer = QPrinter()

        master_layout = QVBoxLayout(self)
        master_layout.setContentsMargins(0, 0, 0, 0)
        master_layout.setSpacing(0)

        self._setup_header(master_layout)

        # Main content
        content = QWidget()
        content.setStyleSheet("background-color: #1A1A24; border: 1px solid #2E2E3E; border-top: none;")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(16, 16, 16, 16)
        content_layout.setSpacing(16)

        # Control panel
        control_panel = self._create_control_panel()
        content_layout.addWidget(control_panel)

        master_layout.addWidget(content)

        # Initialize
        self._load_printers()

    def _create_control_panel(self):
        panel = QFrame()
        panel.setStyleSheet("background-color: #13131A; border-radius: 8px;")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        # Printer selector
        layout.addWidget(QLabel("Printer:", styleSheet="color: #E0E0EE; font-weight: bold;"))
        self.printer_combo = QComboBox()
        self.printer_combo.setStyleSheet(_INPUT_STYLE)
        self.printer_combo.currentIndexChanged.connect(self._on_printer_changed)
        layout.addWidget(self.printer_combo)

        # Copies
        layout.addWidget(QLabel("Copies:", styleSheet="color: #E0E0EE; font-weight: bold;"))
        self.copies_spin = QSpinBox()
        self.copies_spin.setRange(1, 100)
        self.copies_spin.setValue(1)
        self.copies_spin.setStyleSheet(_INPUT_STYLE)
        layout.addWidget(self.copies_spin)

        # Paper size
        layout.addWidget(QLabel("Paper Size:", styleSheet="color: #E0E0EE; font-weight: bold;"))
        self.paper_combo = QComboBox()
        self.paper_combo.setStyleSheet(_INPUT_STYLE)
        self._populate_paper_sizes()
        self.paper_combo.currentIndexChanged.connect(self._on_paper_changed)
        layout.addWidget(self.paper_combo)

        # Orientation
        layout.addWidget(QLabel("Orientation:", styleSheet="color: #E0E0EE; font-weight: bold;"))
        orientation_layout = QHBoxLayout()
        self.portrait_radio = QRadioButton("Portrait")
        self.landscape_radio = QRadioButton("Landscape")
        self.portrait_radio.setStyleSheet(_RADIO_STYLE)
        self.landscape_radio.setStyleSheet(_RADIO_STYLE)
        self.portrait_radio.setChecked(True)
        self.orientation_group = QButtonGroup(self)
        self.orientation_group.addButton(self.portrait_radio)
        self.orientation_group.addButton(self.landscape_radio)
        self.orientation_group.buttonClicked.connect(self._on_orientation_changed)
        orientation_layout.addWidget(self.portrait_radio)
        orientation_layout.addWidget(self.landscape_radio)
        layout.addLayout(orientation_layout)

        layout.addStretch(1)

        # Action buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)

        self.print_btn = QPushButton("Print")
        self.print_btn.setStyleSheet(_BUTTON_STYLE)
        self.print_btn.setDefault(True)
        self.print_btn.clicked.connect(self._on_print)
        btn_layout.addWidget(self.print_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet(_BUTTON_STYLE)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)

        return panel

    def _populate_paper_sizes(self):
        paper_sizes = [
            ("A4", QPageSize.PageSizeId.A4),
            ("Letter", QPageSize.PageSizeId.Letter),
            ("Legal", QPageSize.PageSizeId.Legal),
            ("A3", QPageSize.PageSizeId.A3),
            ("A5", QPageSize.PageSizeId.A5),
        ]
        for name, size in paper_sizes:
            self.paper_combo.addItem(name, size)

    def _load_printers(self):
        self.printer_combo.clear()
        printers = QPrinterInfo.availablePrinters()
        for printer_info in printers:
            self.printer_combo.addItem(printer_info.printerName())

    def _on_printer_changed(self, index):
        if index >= 0:
            self._printer.setPrinterName(self.printer_combo.currentText())

    def _on_paper_changed(self, index):
        if index >= 0:
            paper_size_id = self.paper_combo.currentData()
            page_size = QPageSize(paper_size_id)
            self._printer.setPageSize(page_size)

    def _on_orientation_changed(self, button):
        if button == self.portrait_radio:
            self._printer.setPageOrientation(QPageLayout.Orientation.Portrait)
        else:
            self._printer.setPageOrientation(QPageLayout.Orientation.Landscape)

    def _on_print(self):
        if not self.printer_combo.currentText():
            DarkMessageBox.critical(self, "Error", "No printer selected.")
            return

        self._printer.setCopyCount(self.copies_spin.value())

        # Print the document
        if self._document:
            self._document.print(self._printer)

        DarkMessageBox.about(self, "Print", "Document sent to printer successfully.")
        self.accept()

    def set_document(self, document):
        """Set the document to print."""
        self._document = document
        self._update_preview()

