#!/usr/bin/env python3
"""
Automated Build Script for Holy Bible (வேதம்) Portable Windows Executable
=========================================================================
Uses PyInstaller and `windows_app/holybible.spec` to bundle the complete application
(including the 46MB dual-corpus SQLite database, templates, and static assets)
into a single, standalone portable executable:

    windows_app/dist/HolyBible-Portable.exe
"""

import os
import sys
import subprocess
import shutil

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
SPEC_FILE = os.path.join(CURRENT_DIR, "holybible.spec")
DIST_DIR = os.path.join(CURRENT_DIR, "dist")
BUILD_DIR = os.path.join(CURRENT_DIR, "build")


def check_prerequisites():
    """Verifies Python 3 and PyInstaller are available."""
    if sys.version_info < (3, 8):
        print(f"Error: Python 3.8+ required. Current version is {sys.version}")
        sys.exit(1)

    try:
        import PyInstaller
        print(f"[OK] PyInstaller version: {PyInstaller.__version__}")
    except ImportError:
        print("PyInstaller not found. Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller>=6.5"])


def build_executable():
    """Runs PyInstaller with the spec file."""
    print("\n=======================================================")
    print("   Building Holy Bible Portable Windows Executable")
    print("=======================================================\n")
    print(f"Project Root : {PROJECT_ROOT}")
    print(f"Spec File    : {SPEC_FILE}")
    print(f"Output Dist  : {DIST_DIR}\n")

    os.makedirs(DIST_DIR, exist_ok=True)
    os.makedirs(BUILD_DIR, exist_ok=True)

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--clean",
        f"--distpath={DIST_DIR}",
        f"--workpath={BUILD_DIR}",
        SPEC_FILE,
    ]

    print("Executing command:")
    print(" ".join(cmd))
    print("\nCompiling... (this may take 1-2 minutes)...\n")

    result = subprocess.run(cmd, cwd=PROJECT_ROOT)

    if result.returncode != 0:
        print(f"\n[ERROR] Build failed with exit code: {result.returncode}")
        sys.exit(result.returncode)

    exe_path = os.path.join(DIST_DIR, "HolyBible-Portable.exe")
    if os.path.exists(exe_path):
        size_mb = os.path.getsize(exe_path) / (1024 * 1024)
        print("\n=======================================================")
        print("   [BUILD SUCCESSFUL]")
        print(f"   Portable Executable: {exe_path}")
        print(f"   Executable Size    : {size_mb:.2f} MB")
        print("=======================================================\n")
        print("You can distribute 'HolyBible-Portable.exe' to any Windows PC.")
        print("No installation or Python runtime is required!")
    else:
        print(f"\nWarning: Output file not found at expected path: {exe_path}")


if __name__ == "__main__":
    check_prerequisites()
    build_executable()
