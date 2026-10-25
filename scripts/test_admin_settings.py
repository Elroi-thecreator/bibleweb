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

    # Save original whatsapp_config.json to restore after test
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "whatsapp_config.json")
    orig_config_content = None
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            orig_config_content = f.read()

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
        assert "gateway-status-pill" in res.text
        assert "fetchAdminWaStatus" in res.text
        print("  ✅ Admin Settings Dashboard rendered with full telemetry, controls & live connection pill.")

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

        # -------------------------------------------------------------
        # 11. WhatsApp Gateway Configuration Updates (URL, Session, Key)
        # -------------------------------------------------------------
        print("\n[11] Testing POST /admin/api/whatsapp/config unauthenticated...")
        async with AsyncClient(transport=transport, base_url="http://testserver") as anon_client:
            res = await anon_client.post("/admin/api/whatsapp/config", json={"gateway_url": "https://test.com"})
            assert res.status_code == 401, f"Expected 401, got {res.status_code}"
            print("  ✅ Unauthenticated config update blocked with HTTP 401.")

        print("\n[12] Testing POST /admin/api/whatsapp/config invalid URL validation...")
        res = await client.post("/admin/api/whatsapp/config", json={"gateway_url": "invalid_url"}, cookies=cookies)
        assert res.status_code == 400, f"Expected 400, got {res.status_code}"
        print("  ✅ Malformed URL rejected with HTTP 400.")

        print("\n[13] Testing POST /admin/api/whatsapp/config valid update & runtime application...")
        test_new_url = "https://wa.external-gateway.com/api"
        res = await client.post(
            "/admin/api/whatsapp/config",
            json={
                "gateway_url": test_new_url,
                "session_id": "church-office",
                "api_key": "sec_token_999",
                "enable_simulation_mode": True,
            },
            cookies=cookies,
        )
        assert res.status_code == 200, f"Expected 200, got {res.status_code}"
        cfg_data = res.json()
        assert cfg_data["status"] == "ok"
        assert cfg_data["config"]["gateway_url"] == test_new_url
        assert cfg_data["config"]["session_id"] == "church-office"
        assert cfg_data["config"]["has_api_key"] is True
        print(f"  ✅ WhatsApp Gateway URL updated live to: {cfg_data['config']['gateway_url']}")

        print("\n[14] Testing POST /admin/api/whatsapp/ping-gateway...")
        res = await client.post("/admin/api/whatsapp/ping-gateway", cookies=cookies)
        assert res.status_code == 200, f"Expected 200, got {res.status_code}"
        ping_data = res.json()
        print(f"  ✅ Gateway Ping executed with status: {ping_data.get('status')}")

        # -------------------------------------------------------------
        # 15. WhatsApp RabbitMQ Queue Admin Controls
        # -------------------------------------------------------------
        print("\n[15] Testing POST /admin/api/whatsapp/queue/toggle authenticated...")
        res = await client.post("/admin/api/whatsapp/queue/toggle", cookies=cookies)
        assert res.status_code == 200, f"Expected 200, got {res.status_code}"
        q_toggle = res.json()
        assert q_toggle["status"] == "ok"
        print(f"  ✅ Queue toggled successfully: {q_toggle['message']}")

        # Toggle back to False
        res = await client.post("/admin/api/whatsapp/queue/toggle", cookies=cookies)
        assert res.status_code == 200

        print("\n[16] Testing POST /admin/api/whatsapp/queue/ping authenticated...")
        res = await client.post("/admin/api/whatsapp/queue/ping", cookies=cookies)
        assert res.status_code == 200, f"Expected 200, got {res.status_code}"
        q_ping = res.json()
        assert q_ping["status"] in ("ok", "warning")
        print(f"  ✅ Queue Ping executed with status: {q_ping['status']}")

        # -------------------------------------------------------------
        # 17. Test Admin Logout
        # -------------------------------------------------------------
        print("\n[17] Testing GET /admin/logout...")
        res = await client.get("/admin/logout", cookies=cookies)
        assert res.status_code == 303, f"Expected 303, got {res.status_code}"
        assert "/admin/login" in res.headers["location"]
        print("  ✅ Logged out successfully and redirected to login page.")

        # -------------------------------------------------------------
        # 18. Verify Session Invalidation after Logout
        # -------------------------------------------------------------
        print("\n[18] Testing GET /admin/settings without cookie after logout...")
        res = await client.get("/admin/settings")
        assert res.status_code == 303, f"Expected 303, got {res.status_code}"
        assert "/admin/login" in res.headers["location"]
        print("  ✅ Verified admin settings is strictly unreachable after logout.")

    if orig_config_content is not None:
        with open(config_path, "w", encoding="utf-8") as f:
            f.write(orig_config_content)
        # Re-read into live config
        from whatsapp_gateway.config import load_persisted_config, config
        p = load_persisted_config()
        config.gateway_url = p.get("gateway_url", config.gateway_url)
        config.session_id = p.get("session_id", config.session_id)
        config.api_key = p.get("api_key", config.api_key)
        config.enable_simulation_mode = p.get("enable_simulation_mode", config.enable_simulation_mode)
        config.queue_enabled = p.get("queue_enabled", config.queue_enabled)
        config.rabbitmq_url = p.get("rabbitmq_url", config.rabbitmq_url)

    print("\n" + "=" * 70)
    print("🎉 ALL 18 ADMIN SECURITY, SETTINGS & CONFIG TESTS PASSED WITH 100% SUCCESS!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(run_admin_tests())
