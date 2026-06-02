# Notepad Minus

A dark-themed Notepad-style text editor for Windows, built with **Python** and **PyQt6**. Frameless window, spell check, auto-save, and a custom-styled editing area.

---

## Features

| Feature | Detail |
|---|---|
| Custom dark title bar | Frameless window with minimize / maximize / close |
| Editor font | Bundled **Flexi IBM VGA** (`font/Flexi_IBM_VGA_True.ttf`) — no install required |
| Zoom | **Ctrl + mouse wheel** in the editor (6–72 pt), saved between sessions |
| Auto-scroll | **Middle-click** toggles scroll mode; move mouse up/down to scroll |
| Real-time spell check | Red wavy underlines; toggle in **View → Spell Check** |
| Spelling menu | Right-click a misspelled word for suggestions, ignore, or add to dictionary |
| Auto-save | Saves after each edit when a file path is set |
| Recovery file | New/unsaved documents backed up to `%APPDATA%\NotepadMinus\recovery\` |
| Line numbers | Gutter with current-line highlight; toggle in **View → Line Numbers** |
| Find & Replace | Regex, case-sensitive, whole word, wrap-around (**Ctrl+F**) |
| Undo / Redo | Native Qt undo stack |
| Encoding | UTF-8, UTF-16, or ANSI — **Format → Encoding** and status bar |
| Line endings | CRLF, LF, or CR — **Format → Line Ending** and status bar |
| Go to line | **Ctrl+G** |
| Print | **Ctrl+P** |
| Date/time insert | **F5** |
| Recent files | Last 10 paths under **File → Recent Files** |
| Word wrap | **View → Word Wrap** |
| Smart indent | Tab indents; **Shift+Tab** unindents selection (4 spaces) |
| Toolbar & status bar | Optional; toggles under **View** |
| Dark dialogs | Custom-styled message boxes, Go to Line, and Find & Replace |
| Window layout | Size, maximized state, and preferences stored in `settings.json` |

---

## Requirements

- **Python 3.10+**
- **Windows** (taskbar icon integration uses Win32 APIs)
- Dependencies:

```bash
pip install -r requirements.txt
```

| Package | Purpose |
|---|---|
| PyQt6 | GUI |
| pyspellchecker | Spell checking |
| pywin32 | Windows taskbar / AppUserModelID |
| pyinstaller | Optional — build a standalone `.exe` |

---

## Running

From the project folder:

```bash
python main.py
```

Open a file on launch:

```bash
python main.py path\to\notes.txt
```

### Build executable (optional)

```bash
pyinstaller Notepad_minus.spec
```

The built app expects `icon.ico` beside the executable (same as `main.py` uses in development).

---

## Keyboard shortcuts

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
| Cut | Ctrl+X |
| Copy | Ctrl+C |
| Paste | Ctrl+V |
| Delete | Del |
| Select All | Ctrl+A |
| Insert date/time | F5 |
| Toggle maximize | F11 |
| Zoom in / out | Ctrl + mouse wheel (in editor) |
| Auto-scroll | Middle-click toggle; move mouse up/down |
| Exit | Alt+F4 |

---

## Configuration

### Editor font

The editor loads `font/RobotoSlab-Regular.ttf` at startup via Qt (no Windows font install). Default size is set in `app/fonts.py` (`EDITOR_FONT_DEFAULT_SIZE`). Replace the `.ttf` in `font/` and adjust `FONT_FILENAME` if you switch fonts.

Only the main text area uses this font. Menus, dialogs, and line-number gutter use the system default.

### User settings

Stored at `%APPDATA%\NotepadMinus\settings.json`:

| Key | Description |
|---|---|
| `editor_zoom_size` | Last editor zoom level (point size) |
| `word_wrap` | Word wrap on/off |
| `spell_check` | Spell check on/off |
| `show_line_numbers` | Line number gutter |
| `show_toolbar` / `show_statusbar` | Chrome visibility |
| `encoding` | Default encoding (UTF-8, UTF-16, ANSI) |
| `line_ending` | Default line ending (CRLF, LF, CR) |
| `recent_files` | Up to 10 recent paths |
| `window_geometry` / `window_maximized` | Window size and state |

---

## Project layout

```
Notepad-minus-main/
├── main.py                  # Entry point, theme, taskbar icon
├── icon.ico                 # App / taskbar icon (Windows)
├── font/
│   └── Flexi_IBM_VGA_True.ttf
├── requirements.txt
├── Notepad_minus.spec       # PyInstaller spec
├── README.md
└── app/
    ├── window.py            # Main window, menus, title bar, I/O
    ├── editor.py            # Text editor, line numbers, zoom, spell UI
    ├── fonts.py             # Editor font family and default size
    ├── theme.py             # Global dark Qt stylesheet
    ├── dialogs.py           # Dark message box & Go to Line dialogs
    ├── find_replace.py      # Find & Replace dialog
    ├── spellcheck.py        # Spell engine and highlighter
    ├── autosave.py          # Auto-save and recovery file
    └── settings.py          # JSON settings load/save
```

---

## Data on disk

| Path | Purpose |
|---|---|
| `%APPDATA%\NotepadMinus\settings.json` | Preferences |
| `%APPDATA%\NotepadMinus\recovery\unsaved_recovery.txt` | Backup while editing unsaved content |

---

## License

MIT License — see [LICENSE](LICENSE).
