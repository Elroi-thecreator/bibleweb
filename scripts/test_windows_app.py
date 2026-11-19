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
        ("/songs?book=johnjebaraj", "Pastor John Jebaraj Hymnal"),
        ("/songs/2560", "Song Lyrics Reader (Pradhana Aasariyarae)"),
        ("/songs/2607", "Song Lyrics Reader (Ejamaananae Um Saevaikkaai)"),
        ("/privacy", "Privacy Policy & Scripture Licenses Page"),
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

    # 6. Verify WinGet In-App Upgrade & Exit Trigger
    # 6a. Check update endpoint
    update_url = f"{base_url}/api/app/check-update"
    with urllib.request.urlopen(update_url) as resp:
        assert resp.status == 200
        up_data = json.loads(resp.read().decode("utf-8"))
        assert "current_version" in up_data
        print(f"✓ In-App Update API verified: current={up_data['current_version']}, has_update={up_data.get('has_update')}")

    # 6b. Post to winget-upgrade from local desktop server
    winget_req = urllib.request.Request(
        f"{base_url}/api/app/winget-upgrade",
        data=b"{}",
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(winget_req) as resp:
        assert resp.status == 200
        upgrade_data = json.loads(resp.read().decode("utf-8"))
        assert upgrade_data["status"] in ("upgrading", "simulated")
        print(f"✓ WinGet Upgrade Endpoint verified from desktop loopback: status={upgrade_data['status']}")

    # 6c. Verify Landing page contains WinGet upgrading overlay, desktop isolation & trigger script
    landing_url = f"{base_url}/"
    with urllib.request.urlopen(landing_url) as resp:
        landing_html = resp.read().decode("utf-8")
        assert "winget-upgrading-overlay" in landing_html, "winget-upgrading-overlay missing in base template"
        assert "triggerWinGetUpgrade" in landing_html, "triggerWinGetUpgrade function missing"
        assert "isWindowsDesktopApp" in landing_html, "isWindowsDesktopApp function missing"
        assert "desktop-only-update" in landing_html, "desktop-only-update CSS class missing"
        assert "btn-settings-winget" in landing_html, "btn-settings-winget missing"
        assert "update-modal-winget-btn" in landing_html, "update-modal-winget-btn missing"
        assert "IS_DESKTOP_HOST" in landing_html, "IS_DESKTOP_HOST missing"
        print("✓ WinGet Desktop UI overlay, desktop-only guards, buttons, and triggerWinGetUpgrade verified in landing page HTML")

    # 6d. Verify Remote access to /api/app/winget-upgrade is rejected (HTTP 403)
    from fastapi.testclient import TestClient
    client = TestClient(fastapi_app, client=("198.51.100.24", 54321))
    remote_resp = client.post("/api/app/winget-upgrade")
    assert remote_resp.status_code == 403, f"Expected 403 for remote caller, got {remote_resp.status_code}"
    print("✓ WinGet Upgrade Endpoint security verified: remote callers strictly rejected with HTTP 403 Forbidden")

    # 7. Stop server
    server.stop()
    print("✓ Desktop server cleanly stopped")
    print("\n🎉 ALL WINDOWS DESKTOP HOST VERIFICATION TESTS PASSED!\n")


if __name__ == "__main__":
    run_desktop_host_tests()
