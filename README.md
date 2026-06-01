# Notepad Minus

> A professional, fully dark-themed Notepad replacement built with **Python + PyQt6**.

---

## Features

| Feature | Detail |
|---|---|
| Custom dark title bar | Fully frameless window — no white Windows chrome |
| Real-time spell check | Red wavy underlines on misspelled words |
| Spelling suggestions | Right-click any misspelled word for suggestions |
| Auto-save | Saves after each key press |
| Line numbers | Gutter with current-line highlight |
| Find & Replace | Regex, case-sensitive, whole-word, wrap-around |
| Unlimited undo/redo | Qt's native undo stack |
| Font chooser | Pick any installed font + size |
| Encoding | UTF-8 / UTF-16 / ANSI — switchable in status bar |
| Line endings | CRLF / LF / CR — switchable in status bar |
| Go to Line | Ctrl+G |
| Print | Full print dialog |
| Date/Time insert | F5 |
| Recent files | Last 10 files in File menu |
| Zoom | Ctrl+Scroll, Ctrl+= / Ctrl+-, Ctrl+0 to reset |
| Word wrap | Toggle from View menu |
| Smart Tab | Tab indents, Shift+Tab unindents selection |
| Recovery | Unsaved files backed up to `%APPDATA%\NotepadMinus\recovery\` |
| Persistent settings | Font, wrap, spell, encoding — remembered across sessions |

---

## Requirements

- Python 3.10+
- PyQt6
- pyspellchecker
- pywin32

```bash
pip install -r requirements.txt
```

---

## Running

**Double-click launcher (no console window):**
```
Notepad Minus.bat
```

**Or from terminal:**
```bash
python main.py
```

**Open a file directly:**
```bash
python main.py path\to\file.txt
```

**Pyinstaller:**
```bash
pyinstaller Notepad_minus.spec
```
---

## Keyboard Shortcuts

| Action | Shortcut |
|---|---|
| New | Ctrl+N |
| Open | Ctrl+O |
| Save | Ctrl+S |
| Save As | Ctrl+Shift+S |
| Print | Ctrl+P |
| Find / Replace | Ctrl+F |
| Go to Line | Ctrl+G |
| Undo | Ctrl+Z |
| Redo | Ctrl+Y |
| Select All | Ctrl+A |
| Zoom In | Ctrl+= |
| Zoom Out | Ctrl+- |
| Reset Zoom | Ctrl+0 |
| Date/Time | F5 |
| Fullscreen | F11 |

---

## File Structure

```
notepad-minus/
├── main.py                  # Entry point
├── requirements.txt
├── README.md
└── app/
    ├── __init__.py
    ├── window.py            # Main window + custom title bar
    ├── editor.py            # Editor + line numbers + zoom
    ├── spellcheck.py        # Spell check engine + highlighter
    ├── autosave.py          # Debounced auto-save
    ├── find_replace.py      # Find & Replace dialog
    ├── settings.py          # Persistent JSON settings
    └── theme.py             # Global dark stylesheet
```

---

## Settings & Data

| Path | Purpose |
|---|---|
| `%APPDATA%\NotepadMinus\settings.json` | User preferences |
| `%APPDATA%\NotepadMinus\recovery\unsaved_recovery.txt` | Unsaved file recovery |
