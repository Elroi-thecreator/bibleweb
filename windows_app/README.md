# Holy Bible (வேதம்) - Windows Desktop App & Portable Exe

A dedicated native Windows desktop application and standalone portable executable (`.exe`) sharing the exact same codebase as the web version.

---

## 🌟 Architecture: Single Source of Truth

**No code is duplicated between Web and Windows.**

- The Windows app directly mounts the core FastAPI backend:
  ```python
  from app.main import app
  ```
- Any edits to:
  - `app/main.py` (API routes, canon switching, neural audio TTS)
  - `app/db.py` (SQLite verse queries, Catholic merged-verse grouping, search)
  - `app/quiz_data.py` (Trivia dataset)
  - `app/plans_data.py` (Reading plans & scopes)
  - `templates/` (Jinja2 HTML layouts, reader, presenter, quiz)
  - `static/` (CSS styles, JS storage, Web Audio)
  - `data/bible.sqlite.db` (Dual-corpus database)

  **instantly reflect in BOTH the web app and the Windows desktop app.**

---

## 🚀 Running the Windows Desktop App in Development

### Quick Start (Double-Click)
In the project root, simply double-click:
```cmd
run_desktop.bat
```

### Or Via Command Line
From the project root:
```cmd
py -3 windows_app/app.py
```

### Features:
1. **Native Window**: Runs in a native Windows desktop window powered by Microsoft Edge WebView2.
2. **Audio & TTS**: Full support for Microsoft Neural TTS and gTTS audio streams.
3. **Presenter & Church Projection**: Full F11 fullscreen presenter support.
4. **Smart Fallback**: If Edge WebView2 is not detected, it automatically opens in your default web browser while managing the local background server.

---

## 📦 Building the Portable Standalone Executable (.exe)

To compile the entire application (including the 46MB dual-corpus database, all templates, and all static assets) into a single, portable executable:

```cmd
py -3 windows_app/build_exe.py
```

### Output:
```
windows_app/dist/HolyBible-Portable.exe
```

### Portability:
- **Zero Dependencies**: Can be copied to any Windows 10 or Windows 11 PC (even on a USB drive).
- **No Python Required**: The user does not need Python, Git, or pip installed.
- **Double-Click & Run**: Simply double-click `HolyBible-Portable.exe` to launch the application.

---

## 📂 Folder Structure

```
windows_app/
├── app.py             # Desktop GUI launcher (WebView2 + Background Uvicorn)
├── build_exe.py       # Automated PyInstaller compilation script
├── holybible.spec     # PyInstaller spec configuration
├── requirements.txt   # Desktop dependencies (pywebview, pyinstaller, pillow)
├── assets/
│   ├── app.ico        # Multi-size Windows app icon
│   └── icon-192.png   # Source icon
├── dist/              # Output directory for compiled HolyBible-Portable.exe
└── README.md          # This documentation
```
