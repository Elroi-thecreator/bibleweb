"""
Automated Verification Suite for WhatsApp Gateway Rate Limiting & User Quotas.
Tests:
1. WhatsAppRateLimiter sliding-window evaluation and cooldown calculation.
2. Whitelist normalization and bypass logic.
3. Daily Edge-TTS / FFmpeg audio synthesis quotas.
4. Dispatcher middleware rate limit interception and bilingual warning delivery.
5. Audio command daily quota enforcement in BibleAdapter.
6. Webhook and Admin API rate limiter endpoints and persistence.
"""

import asyncio
import os
import sys
import time

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

import httpx
from app.main import app
from app.admin.auth import COOKIE_NAME, DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD, create_session_token
from whatsapp_gateway.config import config as wa_config, save_persisted_config, load_persisted_config
from whatsapp_gateway.rate_limiter import (
    WhatsAppRateLimiter,
    get_rate_limiter,
    build_cooldown_message,
    build_audio_quota_message,
)
from whatsapp_gateway.routes.webhook import get_client


async def run_rate_limiter_tests():
    print("=" * 70)
    print("⏳ Running WhatsApp Rate Limiter & User Quota Verification Suite")
    print("=" * 70)

    # Save original config to restore at the end
    config_path = os.path.join(PROJECT_ROOT, "data", "whatsapp_config.json")
    orig_config_content = None
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            orig_config_content = f.read()

    try:
        # Configure test thresholds
        wa_config.rate_limit_enabled = True
        wa_config.rate_limit_requests_per_minute = 5
        wa_config.rate_limit_audio_per_day = 3
        wa_config.rate_limit_cooldown_seconds = 10
        wa_config.rate_limit_whitelist = ["919876543210"]

        limiter = WhatsAppRateLimiter()
        limiter.clear_all()

        user_jid = "919999888877@s.whatsapp.net"
        admin_jid = "919876543210@s.whatsapp.net"

        # -------------------------------------------------------------
        # 1. Standalone WhatsAppRateLimiter Unit Testing
        # -------------------------------------------------------------
        print("\n[1] Testing WhatsAppRateLimiter unit sliding-window logic...")

        # Under limit: 5 requests should all be allowed
        for i in range(5):
            allowed, retry_after, reason = limiter.check_rate_limit(user_jid)
            assert allowed is True, f"Request {i+1} should be allowed"

        # 6th request: should be throttled
        allowed, retry_after, reason = limiter.check_rate_limit(user_jid)
        assert allowed is False, "6th request within 60s window must be throttled"
        assert retry_after > 0, "retry_after must be positive"
        assert reason == "rate_limit_exceeded"
        print(f"  ✅ Burst throttled correctly: retry_after={retry_after}s, reason={reason}")

        # Bilingual cooldown message formatting
        warning_msg_en = limiter.build_cooldown_message(retry_after, is_tamil=False)
        assert "Too Many Requests" in warning_msg_en
        assert str(retry_after) in warning_msg_en

        warning_msg_ta = limiter.build_cooldown_message(retry_after, is_tamil=True)
        assert "அதிக கோரிக்கைகள்" in warning_msg_ta
        assert str(retry_after) in warning_msg_ta
        print("  ✅ Cooldown warning messages verified in English and Tamil.")

        # -------------------------------------------------------------
        # 2. Whitelist Normalization & Bypass
        # -------------------------------------------------------------
        print("\n[2] Testing Whitelist normalization and bypass...")
        for i in range(15):
            allowed, retry_after, reason = limiter.check_rate_limit(admin_jid)
            assert allowed is True, f"Admin request {i+1} must be allowed unconditionally"
        assert limiter.is_whitelisted(admin_jid) is True
        assert limiter.is_whitelisted("+91 98765 43210") is True
        assert limiter.is_whitelisted(user_jid) is False
        print("  ✅ Whitelist normalization (+91 / @s.whatsapp.net) verified.")

        # -------------------------------------------------------------
        # 3. Audio Synthesis Daily Quota
        # -------------------------------------------------------------
        print("\n[3] Testing Daily Edge-TTS Audio synthesis quotas...")
        audio_user = "918888777766@s.whatsapp.net"
        # Allowed up to 3
        for i in range(3):
            allowed, used, limit = limiter.check_audio_quota(audio_user)
            assert allowed is True, f"Audio #{i+1} should be allowed"
            assert used == i + 1

        # 4th audio attempt should be blocked
        allowed, used, limit = limiter.check_audio_quota(audio_user)
        assert allowed is False, "4th audio request should exceed daily limit of 3"
        assert used == 3
        assert limit == 3

        quota_msg_en = limiter.build_audio_quota_message(limit, is_tamil=False)
        assert "Daily Audio Limit Reached" in quota_msg_en
        quota_msg_ta = limiter.build_audio_quota_message(limit, is_tamil=True)
        assert "தினசரி ஆடியோ வரம்பு முடிந்தது" in quota_msg_ta
        print(f"  ✅ Audio quota enforced: used={used}/{limit}, quota warning generated.")

        # Whitelist bypass on audio quota
        for i in range(5):
            allowed, used, limit = limiter.check_audio_quota(admin_jid)
            assert allowed is True, "Whitelisted admin must have unlimited audio requests"
        print("  ✅ Admin audio quota bypass verified.")

        # -------------------------------------------------------------
        # 4. Telemetry and State Reset
        # -------------------------------------------------------------
        print("\n[4] Testing rate limiter telemetry and state reset...")
        stats = limiter.get_stats()
        assert stats["total_requests_evaluated"] > 0
        assert stats["total_throttled_requests"] >= 1
        assert stats["total_audio_quota_blocks"] >= 1
        assert stats["active_window_users"] >= 1
        print(f"  ✅ Telemetry captured: {stats['total_requests_evaluated']} requests evaluated, {stats['total_throttled_requests']} throttled.")

        limiter.clear_all()
        reset_stats = limiter.get_stats()
        assert reset_stats["active_window_users"] == 0
        assert reset_stats["total_requests_evaluated"] == 0
        print("  ✅ Limiter state and daily quotas reset successfully.")

        # -------------------------------------------------------------
        # 5. Integration with Webhook & Dispatcher Middleware
        # -------------------------------------------------------------
        print("\n[5] Testing Webhook & Dispatcher Middleware rate limiting...")
        client = get_client()
        client.simulation_mode = True
        client.simulated_outbox.clear()

        # Update global limiter to small window for testing
        wa_config.rate_limit_enabled = True
        wa_config.rate_limit_requests_per_minute = 3
        wa_config.rate_limit_audio_per_day = 2
        wa_config.rate_limit_cooldown_seconds = 15
        wa_config.rate_limit_whitelist = ["919876543210"]

        global_limiter = get_rate_limiter()
        global_limiter.clear_all()

        test_sender = "917777666655@s.whatsapp.net"
        transport = httpx.ASGITransport(app=app)

        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as http:
            # Send 3 rapid messages -> should be processed normally
            for i in range(3):
                client.simulated_outbox.clear()
                payload = {
                    "event": "messages.upsert",
                    "data": {
                        "key": {"remoteJid": test_sender, "fromMe": False, "id": f"RL_TEST_{i}"},
                        "message": {"conversation": "John 3:16"},
                    },
                }
                res = await http.post("/api/whatsapp/webhook", json=payload)
                assert res.status_code == 200
                assert len(client.simulated_outbox) >= 1
                msg_txt = client.simulated_outbox[0].get("text", "")
                assert "John 3:16" in msg_txt or "யோவான் 3:16" in msg_txt

            print("  ✅ First 3 requests processed normally.")

            # 4th rapid message -> should trigger Rate Limiter guard middleware
            client.simulated_outbox.clear()
            payload = {
                "event": "messages.upsert",
                "data": {
                    "key": {"remoteJid": test_sender, "fromMe": False, "id": "RL_TEST_4"},
                    "message": {"conversation": "Genesis 1:1"},
                },
            }
            res = await http.post("/api/whatsapp/webhook", json=payload)
            assert res.status_code == 200
            assert len(client.simulated_outbox) == 1
            out_msg = client.simulated_outbox[0].get("text", "")
            assert "Too Many Requests" in out_msg
            print("  ✅ 4th request intercepted by rate limit middleware with bilingual warning.")

            # Reset limiter for audio test
            global_limiter.clear_all()

            # -------------------------------------------------------------
            # 6. Audio Quota Integration in BibleAdapter
            # -------------------------------------------------------------
            print("\n[6] Testing Audio command quota enforcement in BibleAdapter...")
            wa_config.rate_limit_requests_per_minute = 20
            wa_config.rate_limit_audio_per_day = 2
            global_limiter.clear_all()
            audio_test_sender = "916666555544@s.whatsapp.net"

            # 1st audio request (allowed)
            client.simulated_outbox.clear()
            payload = {
                "event": "messages.upsert",
                "data": {
                    "key": {"remoteJid": audio_test_sender, "fromMe": False, "id": "AUDIO_1"},
                    "message": {"conversation": "audio John 3:16"},
                },
            }
            res = await http.post("/api/whatsapp/webhook", json=payload)
            assert res.status_code == 200
            # 2 replies: "Processing audio..." then audio voice note
            assert len(client.simulated_outbox) == 2
            assert client.simulated_outbox[1].get("media_type") == "audio"
            print("  ✅ Audio request 1 synthesized successfully.")

            # 2nd audio request (allowed)
            client.simulated_outbox.clear()
            payload["data"]["key"]["id"] = "AUDIO_2"
            res = await http.post("/api/whatsapp/webhook", json=payload)
            assert res.status_code == 200
            assert len(client.simulated_outbox) == 2
            assert client.simulated_outbox[1].get("media_type") == "audio"
            print("  ✅ Audio request 2 synthesized successfully.")

            # 3rd audio request -> Exceeds daily_audio_limit of 2!
            client.simulated_outbox.clear()
            payload["data"]["key"]["id"] = "AUDIO_3"
            res = await http.post("/api/whatsapp/webhook", json=payload)
            assert res.status_code == 200
            assert len(client.simulated_outbox) == 1
            blocked_reply = client.simulated_outbox[0].get("text", "")
            assert "Daily Audio Limit Reached" in blocked_reply
            assert client.simulated_outbox[0].get("media_type") is None
            print("  ✅ 3rd audio request blocked by daily quota guard without calling Edge-TTS.")

            # Text requests should STILL WORK for this user even after audio quota is reached
            client.simulated_outbox.clear()
            text_payload = {
                "event": "messages.upsert",
                "data": {
                    "key": {"remoteJid": audio_test_sender, "fromMe": False, "id": "TEXT_AFTER_AUDIO"},
                    "message": {"conversation": "Psalm 23:1"},
                },
            }
            res = await http.post("/api/whatsapp/webhook", json=text_payload)
            assert res.status_code == 200
            assert len(client.simulated_outbox) >= 1
            t_msg = client.simulated_outbox[0].get("text", "")
            assert "Psalm" in t_msg or "சங்கீதம்" in t_msg
            print("  ✅ Text scripture lookups continue to work after audio quota is exhausted.")

            # -------------------------------------------------------------
            # 7. Webhook Rate Limiter Endpoints
            # -------------------------------------------------------------
            print("\n[7] Testing Webhook Rate Limiter API endpoints...")
            res = await http.get("/api/whatsapp/rate-limiter/status")
            assert res.status_code == 200
            data = res.json()
            assert data["status"] == "ok"
            assert "rate_limiter" in data
            print(f"  ✅ GET /api/whatsapp/rate-limiter/status returned: {data['rate_limiter']['total_requests_evaluated']} requests evaluated.")

            # POST /api/whatsapp/rate-limiter/config (Protected by require_admin)
            admin_cookie = {COOKIE_NAME: create_session_token(DEFAULT_ADMIN_USERNAME)}
            res = await http.post(
                "/api/whatsapp/rate-limiter/config",
                json={"requests_per_minute": 30, "daily_audio_limit": 20, "cooldown_seconds": 45},
                cookies=admin_cookie,
            )
            assert res.status_code == 200
            cfg_res = res.json()
            assert cfg_res["rate_limiter"]["requests_per_minute"] == 30
            assert cfg_res["rate_limiter"]["daily_audio_limit"] == 20
            print("  ✅ POST /api/whatsapp/rate-limiter/config updated thresholds live.")

            # POST /api/whatsapp/rate-limiter/reset (Protected by require_admin)
            res = await http.post("/api/whatsapp/rate-limiter/reset", cookies=admin_cookie)
            assert res.status_code == 200
            assert res.json()["rate_limiter"]["active_window_users"] == 0
            print("  ✅ POST /api/whatsapp/rate-limiter/reset cleared telemetry.")

        # -------------------------------------------------------------
        # 8. Admin Controls & Role-Based Security
        # -------------------------------------------------------------
        print("\n[8] Testing Admin Protected Rate Limiter Endpoints...")
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as anon_http:
            # Unauthenticated calls must return 401
            res = await anon_http.post("/admin/api/whatsapp/rate-limiter/toggle")
            assert res.status_code == 401
            res = await anon_http.post("/admin/api/whatsapp/rate-limiter/config", json={"requests_per_minute": 10})
            assert res.status_code == 401
            res = await anon_http.post("/admin/api/whatsapp/rate-limiter/reset")
            assert res.status_code == 401
            print("  ✅ Unauthenticated admin rate limiter endpoints protected with HTTP 401.")

        # Authenticate as Admin
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as auth_http:
            login_res = await auth_http.post(
                "/admin/login",
                data={"username": DEFAULT_ADMIN_USERNAME, "password": DEFAULT_ADMIN_PASSWORD},
                follow_redirects=False,
            )
            assert login_res.status_code == 303
            cookies = login_res.cookies

            # Test Admin Toggle
            res = await auth_http.post("/admin/api/whatsapp/rate-limiter/toggle", cookies=cookies)
            assert res.status_code == 200
            toggle_data = res.json()
            assert toggle_data["status"] == "ok"
            print(f"  ✅ Admin toggled rate limiter state to: {toggle_data['enabled']}")

            # Toggle back to True
            res = await auth_http.post("/admin/api/whatsapp/rate-limiter/toggle", cookies=cookies)
            assert res.status_code == 200
            assert res.json()["enabled"] is True

            # Test Admin Config Update & Whitelist Persistence
            res = await auth_http.post(
                "/admin/api/whatsapp/rate-limiter/config",
                json={
                    "requests_per_minute": 25,
                    "daily_audio_limit": 10,
                    "cooldown_seconds": 20,
                    "whitelist": "919876543210, 919988776655",
                },
                cookies=cookies,
            )
            assert res.status_code == 200
            admin_cfg = res.json()
            assert admin_cfg["rate_limiter"]["requests_per_minute"] == 25
            assert admin_cfg["rate_limiter"]["daily_audio_limit"] == 10
            assert "919988776655" in admin_cfg["rate_limiter"]["whitelist"]
            print("  ✅ Admin updated rate limiter thresholds & whitelist successfully.")

            # Test Admin Reset
            res = await auth_http.post("/admin/api/whatsapp/rate-limiter/reset", cookies=cookies)
            assert res.status_code == 200
            assert res.json()["rate_limiter"]["total_requests_evaluated"] == 0
            print("  ✅ Admin reset rate limiter metrics.")

            # Test Admin Settings HTML contains Rate Limiting card
            res = await auth_http.get("/admin/settings", cookies=cookies)
            assert res.status_code == 200
            assert "WhatsApp Rate Limiting" in res.text
            assert "rl_requests_per_minute" in res.text
            assert "rl_daily_audio_limit" in res.text
            assert "saveRateLimiterConfig" in res.text
            print("  ✅ /admin/settings template renders Rate Limiting controls and script.")

        print("\n" + "=" * 70)
        print("🎉 ALL 8 RATE LIMITER & USER QUOTA TEST SUITES PASSED (100% SUCCESS)!")
        print("=" * 70)

    finally:
        # Restore original config
        if orig_config_content is not None:
            with open(config_path, "w", encoding="utf-8") as f:
                f.write(orig_config_content)
            load_persisted_config()
            print("  [Teardown] Original whatsapp_config.json restored.")


if __name__ == "__main__":
    asyncio.run(run_rate_limiter_tests())
