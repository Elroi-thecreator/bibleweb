# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller Specification File for Holy Bible (வேதம்) Desktop App
Compiles into a single-file standalone portable executable: HolyBible-Portable.exe
"""

import os
import sys

block_cipher = None

# Base directory (project root)
ROOT_DIR = os.path.abspath(os.path.join(SPECPATH, ".."))

datas = [
    (os.path.join(ROOT_DIR, "data", "bible.sqlite.db"), "data"),
    (os.path.join(ROOT_DIR, "templates"), "templates"),
    (os.path.join(ROOT_DIR, "static"), "static"),
    (os.path.join(ROOT_DIR, "windows_app", "assets", "app.ico"), "assets"),
]

hidden_imports = [
    "uvicorn",
    "uvicorn.logging",
    "uvicorn.loops",
    "uvicorn.loops.auto",
    "uvicorn.protocols",
    "uvicorn.protocols.http",
    "uvicorn.protocols.http.auto",
    "uvicorn.protocols.http.h11_impl",
    "uvicorn.protocols.http.httptools_impl",
    "uvicorn.protocols.websockets",
    "uvicorn.protocols.websockets.auto",
    "uvicorn.lifespans",
    "uvicorn.lifespans.on",
    "fastapi",
    "jinja2",
    "starlette",
    "starlette.routing",
    "starlette.responses",
    "starlette.staticfiles",
    "starlette.templating",
    "sqlite3",
    "edge_tts",
    "gtts",
    "webview",
    "webview.platforms.edgechromium",
    "webview.platforms.winforms",
    "clr",
    "pythonnet",
    "clr_loader",
    "app",
    "app.main",
    "app.db",
    "app.quiz_data",
    "app.plans_data",
]

a = Analysis(
    [os.path.join(ROOT_DIR, "windows_app", "app.py")],
    pathex=[ROOT_DIR],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter", "matplotlib", "scipy", "numpy", "pandas"],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher,
)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="HolyBible-Portable",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(ROOT_DIR, "windows_app", "assets", "app.ico"),
)
