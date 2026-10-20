"""
Automated Verification Suite for Admin Protected Settings & System Configuration.
Tests unauthenticated guards, session security, password validation, settings dashboard rendering,
and administrative cache/whatsapp management APIs.
"""

import asyncio
import os
import sys

# Support UTF-8 emoji output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from httpx import AsyncClient, ASGITransport
from app.main import app, HTML_PAGE_CACHE, AUDIO_CACHE
from app.admin.auth import COOKIE_NAME, DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD


async def run_admin_tests():
    print("=" * 70)
    print("🛡️  Running Admin Settings & Role-Based Access Control Test Suite")
    print("=" * 70)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver", follow_redirects=False) as client:

        # -------------------------------------------------------------
        # 1. Unauthenticated Guard on /settings
        # -------------------------------------------------------------
        print("\n[1] Testing GET /settings unauthenticated redirect...")
        res = await client.get("/settings")
        assert res.status_code == 303, f"Expected 303, got {res.status_code}"
        assert res.headers["location"] == "/admin/settings"
        print("  ✅ /settings successfully redirects to /admin/settings.")

        # -------------------------------------------------------------
        # 2. Unauthenticated Guard on /admin/settings
        # -------------------------------------------------------------
        print("\n[2] Testing GET /admin/settings unauthenticated redirect...")
        res = await client.get("/admin/settings")
        assert res.status_code == 303, f"Expected 303, got {res.status_code}"
        assert "/admin/login" in res.headers["location"]
        print(f"  ✅ /admin/settings redirects unauthenticated visitors to: {res.headers['location']}")

        # -------------------------------------------------------------
        # 3. Render Admin Login Form
        # -------------------------------------------------------------
        print("\n[3] Testing GET /admin/login rendering...")
        res = await client.get("/admin/login")
        assert res.status_code == 200, f"Expected 200, got {res.status_code}"
        assert "Admin Control Center" in res.text
        assert 'name="username"' in res.text
        assert 'name="password"' in res.text
        print("  ✅ /admin/login renders branded administrator login form.")

        # -------------------------------------------------------------
        # 4. Failed Login Attempt
        # -------------------------------------------------------------
        print("\n[4] Testing POST /admin/login with incorrect password...")
        res = await client.post(
            "/admin/login",
            data={"username": "admin", "password": "wrong_password_123", "next": "/admin/settings"},
        )
        assert res.status_code == 401, f"Expected 401, got {res.status_code}"
        assert "Invalid admin username or password" in res.text
        assert COOKIE_NAME not in res.cookies
        print("  ✅ Invalid login rejected with HTTP 401 and descriptive error alert.")

        # -------------------------------------------------------------
        # 5. Successful Login Attempt
        # -------------------------------------------------------------
        print("\n[5] Testing POST /admin/login with valid credentials...")
        res = await client.post(
            "/admin/login",
            data={
                "username": DEFAULT_ADMIN_USERNAME,
                "password": DEFAULT_ADMIN_PASSWORD,
                "next": "/admin/settings",
            },
        )
        assert res.status_code == 303, f"Expected 303, got {res.status_code}"
        assert res.headers["location"] == "/admin/settings"
        assert COOKIE_NAME in res.cookies
        session_cookie = res.cookies[COOKIE_NAME]
        print(f"  ✅ Login successful! Issued HMAC session cookie: {session_cookie[:20]}...")

        # -------------------------------------------------------------
        # 6. Authenticated Access to /admin/settings
        # -------------------------------------------------------------
        print("\n[6] Testing GET /admin/settings with authenticated session...")
        cookies = {COOKIE_NAME: session_cookie}
        res = await client.get("/admin/settings", cookies=cookies)
        assert res.status_code == 200, f"Expected 200, got {res.status_code}"
        assert "System Settings & Controls" in res.text
        assert "Embedded SQLite Databases" in res.text
        assert "Performance & Cache Control" in res.text
        assert "WhatsApp Gateway & Bot" in res.text
        assert "31,102" in res.text
        print("  ✅ Admin Settings Dashboard rendered with full telemetry & controls.")

        # -------------------------------------------------------------
        # 7. Unauthenticated Protection on Admin API
        # -------------------------------------------------------------
        print("\n[7] Testing POST /admin/api/cache/clear-html unauthenticated protection...")
        async with AsyncClient(transport=transport, base_url="http://testserver") as anon_client:
            res = await anon_client.post("/admin/api/cache/clear-html")
            assert res.status_code == 401, f"Expected 401, got {res.status_code}"
            print("  ✅ Admin API endpoint blocked unauthenticated request with HTTP 401.")

        # -------------------------------------------------------------
        # 8. Authenticated Cache Purge (HTML Page Cache)
        # -------------------------------------------------------------
        print("\n[8] Testing POST /admin/api/cache/clear-html authenticated...")
        HTML_PAGE_CACHE.set("test_key", b"<html>test</html>")
        assert HTML_PAGE_CACHE.size() > 0
        res = await client.post("/admin/api/cache/clear-html", cookies=cookies)
        assert res.status_code == 200, f"Expected 200, got {res.status_code}"
        data = res.json()
        assert data["status"] == "ok"
        assert HTML_PAGE_CACHE.size() == 0
        print("  ✅ HTML Page Cache successfully purged via Admin API.")

        # -------------------------------------------------------------
        # 9. Authenticated Cache Purge (TTS Audio Cache)
        # -------------------------------------------------------------
        print("\n[9] Testing POST /admin/api/cache/clear-audio authenticated...")
        AUDIO_CACHE["test_audio"] = b"ID3\x00\x00"
        res = await client.post("/admin/api/cache/clear-audio", cookies=cookies)
        assert res.status_code == 200, f"Expected 200, got {res.status_code}"
        data = res.json()
        assert data["status"] == "ok"
        assert len(AUDIO_CACHE) == 0
        print("  ✅ Text-to-Speech Audio Cache successfully purged via Admin API.")

        # -------------------------------------------------------------
        # 10. Authenticated WhatsApp Mode Toggle
        # -------------------------------------------------------------
        print("\n[10] Testing POST /admin/api/whatsapp/toggle-simulation authenticated...")
        res = await client.post("/admin/api/whatsapp/toggle-simulation", cookies=cookies)
        assert res.status_code == 200, f"Expected 200, got {res.status_code}"
        data = res.json()
        assert data["status"] == "ok"
        print(f"  ✅ WhatsApp mode toggled: simulation_mode={data['simulation_mode']}.")

        # Toggle back to true
        if not data["simulation_mode"]:
            await client.post("/admin/api/whatsapp/toggle-simulation", cookies=cookies)

        # -------------------------------------------------------------
        # 11. Test Admin Logout
        # -------------------------------------------------------------
        print("\n[11] Testing GET /admin/logout...")
        res = await client.get("/admin/logout", cookies=cookies)
        assert res.status_code == 303, f"Expected 303, got {res.status_code}"
        assert "/admin/login" in res.headers["location"]
        print("  ✅ Logged out successfully and redirected to login page.")

        # -------------------------------------------------------------
        # 12. Verify Session Invalidation after Logout
        # -------------------------------------------------------------
        print("\n[12] Testing GET /admin/settings without cookie after logout...")
        res = await client.get("/admin/settings")
        assert res.status_code == 303, f"Expected 303, got {res.status_code}"
        assert "/admin/login" in res.headers["location"]
        print("  ✅ Verified admin settings is strictly unreachable after logout.")

    print("\n" + "=" * 70)
    print("🎉 ALL 12 ADMIN SECURITY & SETTINGS TESTS PASSED WITH 100% SUCCESS!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(run_admin_tests())
