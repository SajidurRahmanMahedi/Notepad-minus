"""
Notepad Minus — Entry point.
"""

import ctypes
import sys
import os

# Ensure the project root is on the path
sys.path.insert(0, os.path.dirname(__file__))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

from app.theme import DARK_THEME
from app.window import MainWindow


def set_taskbar_icon(icon_path: str, app_id: str = "note.pad.minus.1.0", force_window: bool = False):
    """
    Sets the taskbar icon for Windows apps using the provided .ico file.
    Works with GUI frameworks and CLI apps (with optional hidden window).

    Args:
        icon_path (str): Path to the .ico file
        app_id (str): Custom AppUserModelID for taskbar grouping
        force_window (bool): If True, creates a hidden window for CLI apps
    """
    if not os.path.exists(icon_path):
        raise FileNotFoundError(f"Icon file not found: {icon_path}")

    if sys.platform != "win32":
        return  # Only relevant on Windows

    # Set AppUserModelID for taskbar icon grouping
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)

    if force_window:
        try:
            import win32gui
            import win32con
            import win32api

            hInstance = win32api.GetModuleHandle()
            className = "HiddenWindow"

            wndClass = win32gui.WNDCLASS()
            wndClass.lpfnWndProc = win32gui.DefWindowProc
            wndClass.hInstance = hInstance
            wndClass.lpszClassName = className
            wndClass.hIcon = win32gui.LoadImage(
                hInstance, icon_path, win32con.IMAGE_ICON, 0, 0,
                win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE
            )

            atom = win32gui.RegisterClass(wndClass)
            hwnd = win32gui.CreateWindowEx(
                0, atom, None, 0, 0, 0, 0, 0, 0, 0, hInstance, None
            )
        except ImportError:
            print("pywin32 is required for CLI taskbar icon support. Install with: pip install pywin32")



# Set up base directory for all resources
if getattr(sys, 'frozen', False):
    # If we're running as a PyInstaller bundle
    base_dir = os.path.dirname(sys.executable)
else:
    # If we're running as a normal Python script
    base_dir = os.path.dirname(os.path.abspath(__file__))


ico = os.path.join(base_dir, "icon.ico")
set_taskbar_icon(ico)

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Notepad Minus")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("NotepadMinus")

    # Apply global dark stylesheet
    app.setStyleSheet(DARK_THEME)

    app.setWindowIcon(QIcon(ico))

    # Create and show the main window
    win = MainWindow()

    # If a file path was passed as argument, open it
    if len(sys.argv) > 1:
        file_arg = sys.argv[1]
        if os.path.isfile(file_arg):
            win._open_file(file_arg)

    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
