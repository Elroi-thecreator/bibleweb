#!/usr/bin/env python3
"""
Holy Bible (வேதம்) - Windows Desktop Application Host
======================================================
Single Source of Truth Architecture:
Directly imports the core FastAPI application from `app.main`.
All changes in `app/`, `templates/`, and `static/` immediately reflect
in both the Web and Windows versions without duplicate code.

Runs a local lightweight Uvicorn server in a background thread and presents
the application inside a native Windows desktop window via Microsoft Edge WebView2.
"""

import os
import sys
import time
import socket
import threading
import urllib.request

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# 1. Ensure the project root is in sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)

# Handle PyInstaller frozen bundle path
if getattr(sys, "frozen", False):
    BUNDLE_DIR = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
    if BUNDLE_DIR not in sys.path:
        sys.path.insert(0, BUNDLE_DIR)
else:
    if PROJECT_ROOT not in sys.path:
        sys.path.insert(0, PROJECT_ROOT)

# 2. Import the exact same FastAPI app
try:
    from app.main import app as fastapi_app
except ImportError as err:
    print(f"Error importing core application: {err}")
    print(f"sys.path: {sys.path}")
    sys.exit(1)

# 3. Locate icon asset
if getattr(sys, "frozen", False):
    ICON_PATH = os.path.join(BUNDLE_DIR, "assets", "app.ico")
    if not os.path.exists(ICON_PATH):
        ICON_PATH = os.path.join(BUNDLE_DIR, "windows_app", "assets", "app.ico")
else:
    ICON_PATH = os.path.join(CURRENT_DIR, "assets", "app.ico")


def find_available_port(preferred_port=8000, max_attempts=50):
    """Finds an available local port starting with preferred_port."""
    for port in range(preferred_port, preferred_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    # Fallback to system-assigned ephemeral port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class UvicornServerThread(threading.Thread):
    """Runs Uvicorn in a daemon thread so the GUI remains non-blocking."""
    def __init__(self, app, host, port):
        super().__init__(daemon=True)
        import uvicorn
        self.config = uvicorn.Config(
            app=app,
            host=host,
            port=port,
            log_level="warning",
            access_log=False,
            timeout_keep_alive=30,
        )
        self.server = uvicorn.Server(config=self.config)

    def run(self):
        self.server.run()

    def stop(self):
        self.server.should_exit = True


def wait_for_server(url, timeout=12.0):
    """Waits for the local server to start responding to HTTP requests."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            with urllib.request.urlopen(url, timeout=1.0) as resp:
                if resp.status in (200, 302, 307):
                    return True
        except Exception:
            time.sleep(0.15)
    return False


def main():
    """Main desktop entry point."""
    host = "127.0.0.1"
    port = find_available_port(8000)
    app_url = f"http://{host}:{port}/"

    print("==================================================")
    print("   Holy Bible (வேதம்) - Windows Desktop App")
    print(f"   Local Server: {app_url}")
    print("==================================================")

    # Start background Uvicorn server
    server_thread = UvicornServerThread(fastapi_app, host, port)
    server_thread.start()

    # Wait for server readiness
    if not wait_for_server(app_url, timeout=12.0):
        print("Warning: Local server taking longer than expected to respond, continuing launch...")

    # Check for pywebview
    has_webview = False
    try:
        import webview
        has_webview = True
    except ImportError:
        has_webview = False

    if has_webview:
        print("Launching native Windows desktop window (Edge WebView2)...")
        try:
            window = webview.create_window(
                title="Holy Bible - வேதம்",
                url=app_url,
                width=1280,
                height=840,
                min_size=(850, 600),
                confirm_close=False,
                text_select=True,
                zoomable=True,
            )
            # Start GUI with Edge WebView2
            webview.start(
                gui="edgechromium",
                icon=ICON_PATH if os.path.exists(ICON_PATH) else None,
                debug=False,
            )
        except Exception as e:
            print(f"Error launching webview window ({e}). Falling back to system browser...")
            has_webview = False

    if not has_webview:
        # Fallback to default browser
        import webbrowser
        print(f"Opening Holy Bible in your default browser at {app_url}")
        webbrowser.open(app_url)
        print("Desktop server running. Press Ctrl+C in this terminal to exit.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nShutting down desktop server...")

    # Clean shutdown
    server_thread.stop()
    print("Holy Bible desktop application closed.")


if __name__ == "__main__":
    main()
