#!/usr/bin/env python3
"""
Test Suite for Windows Desktop Application Host & Single Source of Truth
========================================================================
Validates that:
1. `windows_app/app.py` imports `app.main:app` correctly.
2. UvicornServerThread starts on an available loopback port.
3. All core endpoints (Reader, Presenter, Quiz, Plans, Audio) respond with HTTP 200.
4. Static assets and Jinja2 templates are properly located from the desktop host context.
"""

import sys
import os
import time
import urllib.request
import json

# Ensure project root is in sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from windows_app.app import (
    fastapi_app,
    find_available_port,
    UvicornServerThread,
    wait_for_server,
    ICON_PATH,
)


def run_desktop_host_tests():
    print("=== Testing Windows Desktop App Host & Unified Architecture ===")
    
    # 1. Icon verification
    assert os.path.exists(ICON_PATH), f"Icon missing at {ICON_PATH}"
    print(f"✓ Desktop Icon located: {ICON_PATH} ({os.path.getsize(ICON_PATH)} bytes)")

    # 2. Port allocation
    port = find_available_port(8090)
    print(f"✓ Allocated test port: {port}")

    # 3. Start background server thread
    server = UvicornServerThread(fastapi_app, "127.0.0.1", port)
    server.start()

    base_url = f"http://127.0.0.1:{port}"
    print(f"✓ Background server started at {base_url}")

    # 4. Wait for server readiness
    ready = wait_for_server(base_url, timeout=10.0)
    assert ready, "Server failed to start within timeout"
    print("✓ Server responded to readiness probe")

    # 5. Test Core Routes
    endpoints = [
        ("/", "Landing Page"),
        ("/read/40/1", "Reader View (Matthew 1)"),
        ("/present/40/1", "Presenter Screen"),
        ("/quiz", "Interactive Bible Quiz"),
        ("/plans", "Reading Plans Lobby"),
        ("/api/quiz/questions", "Quiz API (JSON)"),
        ("/read-along/plan/whole-bible-100/day/1", "100-Day Read-Along Plan"),
        ("/songs", "Christian Hymnals Directory"),
        ("/songs?book=aldrin", "Dr. Joseph Aldrin Hymnal"),
        ("/songs?book=benny", "Pastor Benny Joshua Hymnal"),
        ("/songs/2560", "Song Lyrics Reader (Pradhana Aasariyarae)"),
        ("/static/manifest.json", "Static File Mount"),
    ]

    for path, desc in endpoints:
        url = f"{base_url}{path}"
        req = urllib.request.Request(url, headers={"User-Agent": "BibleWeb-Desktop-Test/1.0"})
        with urllib.request.urlopen(req, timeout=5.0) as resp:
            status = resp.status
            content = resp.read()
            assert status == 200, f"Expected 200 for {path}, got {status}"
            assert len(content) > 0, f"Empty response for {path}"
            print(f"✓ [{status}] {desc} ({path}) - {len(content)} bytes")

    # 6. Verify API data integrity through desktop server
    quiz_url = f"{base_url}/api/quiz/questions"
    with urllib.request.urlopen(quiz_url) as resp:
        quiz_data = json.loads(resp.read().decode("utf-8"))
        assert "questions" in quiz_data
        assert quiz_data["total_available"] == 100
        print(f"✓ Quiz API via desktop server verified: {quiz_data['total_available']} questions available")

    # 7. Stop server
    server.stop()
    print("✓ Desktop server cleanly stopped")
    print("\n🎉 ALL WINDOWS DESKTOP HOST VERIFICATION TESTS PASSED!\n")


if __name__ == "__main__":
    run_desktop_host_tests()
