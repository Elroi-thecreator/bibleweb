"""
Automated Verification & Simulation Test Suite for Decoupled WhatsApp Gateway.
Simulates incoming webhook payloads, browser chat simulator, subscriber management,
and bilingual Tamil/English operations without requiring live WhatsApp hardware.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Safe UTF-8 console output for Windows terminals
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import httpx
from app.main import app
from app.admin.auth import COOKIE_NAME, create_session_token
from whatsapp_gateway.routes.webhook import get_client, get_session_store
from whatsapp_gateway.subscribers import get_subscriber_count, is_subscribed
from whatsapp_gateway.rate_limiter import get_rate_limiter
from whatsapp_gateway.config import config as wa_config, load_persisted_config


async def run_tests():
    print("=" * 70)
    print("🧪 Running Decoupled WhatsApp Gateway Enhanced Verification Suite")
    print("=" * 70)

    load_persisted_config()
    client = get_client()
    client.simulation_mode = True
    session_store = get_session_store()
    rate_limiter = get_rate_limiter()
    rate_limiter.clear_all()
    if "919876543210" not in wa_config.rate_limit_whitelist:
        wa_config.rate_limit_whitelist.append("919876543210")

    sender_jid = "919876543210@s.whatsapp.net"
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as http:
        # 1. Health & Status Check
        print("\n[1] Testing GET /api/whatsapp/status...")
        res = await http.get("/api/whatsapp/status")
        assert res.status_code == 200, f"Expected 200, got {res.status_code}"
        data = res.json()
        assert data["simulation_mode"] is True
        print(f"  ✅ Status OK: Gateway={data['gateway_url']}, Subscribers={data.get('subscriber_count', 0)}")

        # 2. Web Hub Page /whatsapp
        print("\n[2] Testing HTML Dashboard GET /whatsapp...")
        hub_res = await http.get("/whatsapp")
        assert hub_res.status_code == 200
        assert "WhatsApp Bible Assistant" in hub_res.text
        assert "Interactive WhatsApp Chat Simulator" in hub_res.text
        assert "toggleSimulationMode" not in hub_res.text
        assert "sendCustomBroadcast" not in hub_res.text
        assert "triggerDevotionalPush" not in hub_res.text
        assert "Admin Announcement Broadcast" not in hub_res.text
        print("  ✅ Web Hub UI rendered with 200 OK and sanitized of all admin controls.")

        # Helper to simulate sending a WhatsApp message
        async def send_simulated_msg(text: str):
            client.simulated_outbox.clear()
            payload = {
                "event": "messages.upsert",
                "sessionId": "default",
                "data": {
                    "key": {
                        "remoteJid": sender_jid,
                        "fromMe": False,
                        "id": "MSG_SIM_001",
                    },
                    "pushName": "Dev Tester",
                    "message": {
                        "conversation": text,
                    },
                },
            }
            res = await http.post("/api/whatsapp/webhook", json=payload)
            assert res.status_code == 200, f"Webhook failed: {res.text}"
            return client.simulated_outbox

        # 3. Test Help, Hi & Menu Auto-Reply Commands
        print("\n[3] Testing 'help' and 'Hi' auto-reply with available options...")
        outbox = await send_simulated_msg("help")
        assert len(outbox) == 1
        assert "Welcome to Holy Bible WhatsApp Assistant" in outbox[0]["text"]
        assert "options available" in outbox[0]["text"].lower()

        # Test "Hi" greeting auto-reply
        outbox_hi = await send_simulated_msg("Hi")
        assert len(outbox_hi) == 1
        assert "Welcome to Holy Bible WhatsApp Assistant" in outbox_hi[0]["text"]
        assert "options available" in outbox_hi[0]["text"].lower()
        assert "1️⃣" in outbox_hi[0]["text"]

        # Test selecting option "1"
        outbox_opt1 = await send_simulated_msg("1")
        assert len(outbox_opt1) == 1
        assert "Option 1: Scripture Reading" in outbox_opt1[0]["text"]

        # Test selecting new options 8, 9, 10, 11
        outbox_opt8 = await send_simulated_msg("8")
        assert len(outbox_opt8) == 1
        assert "Option 8: Habit Streak" in outbox_opt8[0]["text"]

        outbox_opt9 = await send_simulated_msg("9")
        assert len(outbox_opt9) == 1
        assert "Option 9: Status Image Card" in outbox_opt9[0]["text"]

        outbox_opt10 = await send_simulated_msg("10")
        assert len(outbox_opt10) == 1
        assert "Option 10: Bilingual Parallel" in outbox_opt10[0]["text"]

        outbox_opt11 = await send_simulated_msg("11")
        assert len(outbox_opt11) == 1
        assert "Option 11: Web Bible" in outbox_opt11[0]["text"]
        print("  ✅ 'Hi' auto-reply and available options menu (1-11) verified.")

        # 4. Test Scripture Citation: John 3:16
        print("\n[4] Testing Scripture Citation 'John 3:16'...")
        outbox = await send_simulated_msg("John 3:16")
        assert len(outbox) == 1
        reply = outbox[0]["text"]
        assert "John 3:16" in reply
        print("  ✅ John 3:16 citation successfully verified.")

        # 5. Test Tamil Scripture Citation: யோவான் 3:16
        print("\n[5] Testing Tamil Scripture Citation 'யோவான் 3:16'...")
        outbox = await send_simulated_msg("யோவான் 3:16")
        assert len(outbox) == 1
        reply = outbox[0]["text"]
        assert "யோவான்" in reply or "John" in reply
        print("  ✅ Tamil Scripture citation verified with bilingual priority.")

        # 6. Test Catholic Canon Scripture Lookup: Tobit 4:7
        print("\n[6] Testing Deuterocanonical Scripture 'Tobit 4:7'...")
        outbox = await send_simulated_msg("Tobit 4:7")
        assert len(outbox) == 1
        reply = outbox[0]["text"]
        assert "Tobit 4:7" in reply
        print("  ✅ Tobit 4:7 (Catholic Canon) citation successfully verified.")

        # 7. Test Scripture Keyword Search
        print("\n[7] Testing Keyword Search 'search grace'...")
        outbox = await send_simulated_msg("search grace")
        assert len(outbox) == 1
        reply = outbox[0]["text"]
        assert "Scripture Search Results" in reply
        print("  ✅ Keyword Search successfully returned matching verses.")

        # 8. Test Interactive Daily Bible Quiz (Multi-Turn Dialogue)
        print("\n[8] Testing Interactive Bible Quiz Multi-Turn Flow...")
        outbox = await send_simulated_msg("quiz")
        assert len(outbox) == 1
        assert "Bible Trivia" in outbox[0]["text"] or "வேதாகம" in outbox[0]["text"]
        print("  ✅ Quiz question generated and state set.")

        state_record = await session_store.get_session(sender_jid)
        assert state_record is not None
        assert state_record["state"] == "QUIZ_WAITING_ANSWER"

        outbox = await send_simulated_msg("2")
        assert len(outbox) == 1
        assert "Reference:" in outbox[0]["text"] or "வசன ஆதாரம்:" in outbox[0]["text"]
        print("  ✅ Quiz answer evaluated and state cleared.")

        state_after = await session_store.get_session(sender_jid)
        assert state_after is None

        # 9. Test Subscription Flow: 'subscribe' and 'stop'
        print("\n[9] Testing Subscription Flow ('subscribe' -> 'stop')...")
        outbox = await send_simulated_msg("subscribe")
        assert len(outbox) == 1
        assert "Subscribed to Daily Scripture" in outbox[0]["text"]
        assert await is_subscribed(sender_jid) is True
        print("  ✅ User successfully subscribed to daily devotionals.")

        # Devotional Push to Subscribers & RBAC Security
        print("\n[10] Testing Devotional Broadcast Trigger RBAC Security & Execution...")
        # 10a. Unauthenticated attempt MUST fail with 401
        unauth_push = await http.post("/api/whatsapp/push-devotional")
        assert unauth_push.status_code == 401, f"Expected 401 Unauthorized, got {unauth_push.status_code}"
        print("  ✅ Unauthenticated call to /api/whatsapp/push-devotional blocked with 401 Unauthorized.")

        # 10b. Unauthenticated call to toggle-simulation MUST fail with 401
        unauth_sim = await http.post("/api/whatsapp/toggle-simulation")
        assert unauth_sim.status_code == 401, f"Expected 401 Unauthorized, got {unauth_sim.status_code}"
        print("  ✅ Unauthenticated call to /api/whatsapp/toggle-simulation blocked with 401 Unauthorized.")

        # 10c. Authenticated admin call succeeds
        admin_cookies = {COOKIE_NAME: create_session_token("admin")}
        push_res = await http.post("/api/whatsapp/push-devotional", cookies=admin_cookies)
        assert push_res.status_code == 200
        p_data = push_res.json()
        assert p_data["success"] >= 1
        print(f"  ✅ Authenticated admin devotional broadcast successfully delivered to {p_data['success']} subscribers.")

        # Now Unsubscribe via 'stop'
        outbox = await send_simulated_msg("stop")
        assert len(outbox) == 1
        assert "unsubscribed" in outbox[0]["text"].lower()
        assert await is_subscribed(sender_jid) is False
        print("  ✅ User successfully unsubscribed via 'stop' command.")

        # 11. Test Browser Live Chat Simulator API
        print("\n[11] Testing POST /api/whatsapp/simulate...")
        sim_res = await http.post(
            "/api/whatsapp/simulate",
            json={"text": "Genesis 1:1", "sender": "web-test@s.whatsapp.net"},
        )
        assert sim_res.status_code == 200
        sim_data = sim_res.json()
        assert sim_data["success"] is True
        assert len(sim_data["replies"]) >= 1
        assert "Genesis 1:1" in sim_data["replies"][0]["text"]
        print("  ✅ Browser Live Chat Simulator API returned instant responses.")

        # 12. Test Song Lyrics Lookup
        print("\n[12] Testing Song Lyrics Lookup 'song 2281'...")
        outbox = await send_simulated_msg("song 2281")
        assert len(outbox) == 1
        assert "🎵" in outbox[0]["text"]
        print("  ✅ Song lyrics successfully retrieved.")

        # 13. Test Reading Plan Command & Plan Switching
        print("\n[13] Testing Reading Plans in WhatsApp (Full Bible 365, NT 90, Switching, Starting at Day 1)...")
        from datetime import date
        from whatsapp_gateway.subscribers import update_subscriber_plan
        await update_subscriber_plan(sender_jid, "full-bible-365", plan_start_date=date.today().isoformat())
        outbox = await send_simulated_msg("plan")
        assert len(outbox) == 1
        assert "Daily Scripture Reading Plan" in outbox[0]["text"]
        assert "Full Bible in 365 Days" in outbox[0]["text"]
        assert "New Testament in 90 Days" in outbox[0]["text"]
        assert "Day 1" in outbox[0]["text"]
        print("  ✅ Default 365-day reading plan starts at Day 1 and options displayed successfully.")

        # Test switching to New Testament 90 days plan
        outbox_switch_nt = await send_simulated_msg("plan nt")
        assert len(outbox_switch_nt) == 1
        assert "New Testament in 90 Days" in outbox_switch_nt[0]["text"]
        assert "Switched Successfully" in outbox_switch_nt[0]["text"]
        assert "Day 1" in outbox_switch_nt[0]["text"]
        print("  ✅ Switched reading plan to 'plan nt' successfully (starts at Day 1).")

        # Test switching back to Full Bible in 365 days
        outbox_switch_full = await send_simulated_msg("plan full")
        assert len(outbox_switch_full) == 1
        assert "Full Bible in 365 Days" in outbox_switch_full[0]["text"]
        assert "Day 1" in outbox_switch_full[0]["text"]
        print("  ✅ Switched reading plan to 'plan full' (365 days) successfully (starts at Day 1).")

        # Test inspecting specific day reading
        outbox_day50 = await send_simulated_msg("plan 50")
        assert len(outbox_day50) == 1
        assert "Day 50" in outbox_day50[0]["text"]
        print("  ✅ Inspected specific day reading ('plan 50') successfully.")

        # Test Tamil plan command
        outbox_plan_ta = await send_simulated_msg("திட்டம்")
        assert len(outbox_plan_ta) == 1
        assert "வாசிப்புத் திட்டம்" in outbox_plan_ta[0]["text"]
        print("  ✅ Tamil reading plan command ('திட்டம்') verified.")

        # 14. Test Audio Bible Generation across English, Tamil & Numbered Books with Processing Notice
        print("\n[14] Testing Audio Bible 'audio John 1' with processing notice...")
        outbox = await send_simulated_msg("audio John 1")
        assert len(outbox) == 2, f"Expected 2 messages (processing + audio), got {len(outbox)}"
        assert "processing" in outbox[0]["text"].lower(), f"Expected processing message, got: {outbox[0]['text']}"
        assert outbox[1].get("media_type") == "audio" or "Audio" in outbox[1].get("caption", "") or "Audio" in outbox[1].get("text", "")
        print("  ✅ 'audio John 1' sent processing notice and audio payload successfully.")

        print("     Testing Audio Bible with Numbered Book 'audio 1 John 1'...")
        outbox_num = await send_simulated_msg("audio 1 John 1")
        assert len(outbox_num) == 2
        assert "processing" in outbox_num[0]["text"].lower()
        assert outbox_num[1].get("media_type") == "audio" or "1 John" in outbox_num[1].get("caption", "")
        print("  ✅ 'audio 1 John 1' (numbered book) sent processing notice and audio successfully.")

        print("     Testing Audio Bible with Verse Range 'audio John 1:1-5'...")
        outbox_range = await send_simulated_msg("audio John 1:1-5")
        assert len(outbox_range) == 2
        assert "processing" in outbox_range[0]["text"].lower()
        assert outbox_range[1].get("media_type") == "audio" or "1:1-5" in outbox_range[1].get("caption", "")
        print("  ✅ 'audio John 1:1-5' (verse range) sent processing notice and audio successfully.")

        print("     Testing Audio Bible in Tamil 'audio யோவான் 1'...")
        outbox_ta = await send_simulated_msg("audio யோவான் 1")
        assert len(outbox_ta) == 2
        assert "தயாராகிறது" in outbox_ta[0]["text"] or "ஆடியோ" in outbox_ta[0]["text"]
        assert outbox_ta[1].get("media_type") == "audio" or "வேத ஆடியோ" in outbox_ta[1].get("caption", "")
        print("  ✅ 'audio யோவான் 1' (Tamil scripture audio) sent processing notice and audio successfully.")

        # 15. Test Administrative Broadcast Endpoint RBAC Security & Execution
        print("\n[15] Testing POST /api/whatsapp/broadcast RBAC Security & Execution...")
        # 15a. Unauthenticated attempt MUST fail with 401
        unauth_bc = await http.post(
            "/api/whatsapp/broadcast",
            json={"recipients": ["919876543210@s.whatsapp.net"], "message": "unauth test"},
        )
        assert unauth_bc.status_code == 401, f"Expected 401 Unauthorized, got {unauth_bc.status_code}"
        print("  ✅ Unauthenticated call to /api/whatsapp/broadcast blocked with 401 Unauthorized.")

        # 15b. Authenticated admin attempt succeeds
        broadcast_res = await http.post(
            "/api/whatsapp/broadcast",
            json={
                "recipients": ["919876543210@s.whatsapp.net", "919988776655@s.whatsapp.net"],
                "message": "🕊️ Blessed morning! Today's devotional is now available.",
            },
            cookies=admin_cookies,
        )
        assert broadcast_res.status_code == 200
        b_data = broadcast_res.json()
        assert b_data["total"] == 2
        print(f"  ✅ Authenticated admin broadcast delivered to {b_data['total']} simulated recipients.")

        # 16. Test WhatsApp Reminder Setting (Default morning 5 AM) & Time Customization
        print("\n[16] Testing Daily Reminder Command & Configurable Dispatch Time (Default: 5:00 AM)...")
        # Check current status
        outbox_remind_status = await send_simulated_msg("remind")
        assert len(outbox_remind_status) == 1
        assert "5:00 AM" in outbox_remind_status[0]["text"]
        print("  ✅ Default 5:00 AM reminder status displayed successfully.")

        # Set reminder to 5:00 AM explicitly
        outbox_set_5am = await send_simulated_msg("remind 5 AM")
        assert len(outbox_set_5am) == 1
        assert "5:00 AM" in outbox_set_5am[0]["text"]
        assert "05:00" in outbox_set_5am[0]["text"]
        print("  ✅ Configured reminder to morning 5 AM ('remind 5 AM').")

        # Set custom reminder to 6:30 AM
        outbox_set_630am = await send_simulated_msg("remind 6:30 AM")
        assert len(outbox_set_630am) == 1
        assert "6:30 AM" in outbox_set_630am[0]["text"]
        assert "06:30" in outbox_set_630am[0]["text"]
        print("  ✅ Updated reminder time to 6:30 AM ('remind 6:30 AM').")

        # Set evening reminder 6:30 PM (18:30)
        outbox_set_1830 = await send_simulated_msg("remind 18:30")
        assert len(outbox_set_1830) == 1
        assert "6:30 PM" in outbox_set_1830[0]["text"]
        assert "18:30" in outbox_set_1830[0]["text"]
        print("  ✅ Updated reminder time to 24-hr format ('remind 18:30' -> 6:30 PM).")

        # Set reminder via Tamil command
        outbox_remind_ta = await send_simulated_msg("நேரம் காலை 5")
        assert len(outbox_remind_ta) == 1
        assert "05:00" in outbox_remind_ta[0]["text"]
        print("  ✅ Configured reminder in Tamil ('நேரம் காலை 5').")

        # 17. Test Target-Time Devotional Push Filtering
        print("\n[17] Testing Target-Time Devotional Push (5:00 AM)...")
        from whatsapp_gateway.scheduler.devotional_push import push_daily_devotional
        # With target_time="05:00", sender who just set 05:00 will receive devotional
        push_res = await push_daily_devotional(client=client, target_time="05:00")
        assert push_res["delivered"] >= 1
        print(f"  ✅ Time-targeted devotional push successfully delivered to {push_res['delivered']} subscriber(s) due at 05:00.")

        # Test disabling reminders
        outbox_off = await send_simulated_msg("remind off")
        assert len(outbox_off) == 1
        assert "stopped" in outbox_off[0]["text"].lower() or "நிறுத்தப்பட்டது" in outbox_off[0]["text"]
        print("  ✅ Successfully stopped reminders via 'remind off'.")

        # 18. Feature 1: Reading Plan "Mark as Done" & Habit Streak Tracker
        print("\n[18] Testing Feature 1: Reading Plan 'done' and 'streak' commands...")
        outbox_done = await send_simulated_msg("done")
        assert len(outbox_done) == 1
        assert "🔥" in outbox_done[0]["text"]
        assert "streak" in outbox_done[0]["text"].lower() or "தொடர்" in outbox_done[0]["text"]
        print(f"  ✅ 'done' command successfully recorded progress: {outbox_done[0]['text'][:60]}...")

        outbox_streak = await send_simulated_msg("streak")
        assert len(outbox_streak) == 1
        assert "🔥" in outbox_streak[0]["text"]
        assert "Streak" in outbox_streak[0]["text"] or "தொடர்" in outbox_streak[0]["text"]
        print(f"  ✅ 'streak' command returned habit dashboard: {outbox_streak[0]['text'][:60]}...")

        # 19. Feature 3: Shareable "Verse of the Day" WhatsApp Status Image Card Generator
        print("\n[19] Testing Feature 3: Verse of the Day Status Card Generator ('card')...")
        outbox_card = await send_simulated_msg("card")
        assert len(outbox_card) == 1
        assert outbox_card[0].get("media_type") == "image"
        assert "Status Card" in outbox_card[0].get("caption", "") or "படம்" in outbox_card[0].get("caption", "")
        card_bytes_len = outbox_card[0].get("bytes_len") or len(outbox_card[0].get("file_bytes") or b"")
        assert card_bytes_len > 5000
        print(f"  ✅ 'card' command generated {card_bytes_len} bytes JPEG image card with caption: {outbox_card[0]['caption'][:40]}...")

        # 20. Feature 4: Bilingual Parallel Mode
        print("\n[20] Testing Feature 4: Bilingual Parallel Mode ('lang both')...")
        outbox_lang_both = await send_simulated_msg("lang both")
        assert len(outbox_lang_both) == 1
        assert "Bilingual Parallel" in outbox_lang_both[0]["text"]
        print("  ✅ 'lang both' updated language preference to bilingual parallel.")

        # Test scripture lookup under bilingual parallel mode
        outbox_parallel_scripture = await send_simulated_msg("John 3:16")
        assert len(outbox_parallel_scripture) == 1
        parallel_text = outbox_parallel_scripture[0]["text"]
        assert "யோவான்" in parallel_text or "John" in parallel_text
        # Both Tamil and English scriptures should be present
        assert "Tamil" in parallel_text or "தமிழ்" in parallel_text or "தேவன்" in parallel_text
        assert "English" in parallel_text or "God" in parallel_text or "world" in parallel_text
        print("  ✅ Scripture lookup under 'lang both' output bilingual parallel text successfully.")

        # 21. Feature 6: Web Bible & WhatsApp 15-Minute Magic Linking Sync
        print("\n[21] Testing Feature 6: Web Bible Sync ('sync' command & verification)...")
        outbox_sync = await send_simulated_msg("sync")
        assert len(outbox_sync) == 1
        sync_text = outbox_sync[0]["text"]
        assert "BIBLE-" in sync_text
        assert "/sync" in sync_text
        print(f"  ✅ 'sync' command produced magic link code: {sync_text[:60]}...")

        # Extract the code from the response (BIBLE-XXXX)
        import re
        code_match = re.search(r"BIBLE-\d{4}", sync_text)
        assert code_match, f"Could not find BIBLE-XXXX in {sync_text}"
        sync_code = code_match.group(0)

        # Test GET /sync HTML page
        sync_page_res = await http.get("/sync")
        assert sync_page_res.status_code == 200
        assert "WhatsApp & Web Bible Sync" in sync_page_res.text or "WhatsApp &amp; Web Bible Sync" in sync_page_res.text
        print("  ✅ GET /sync rendered HTML successfully.")

        # Test POST /api/whatsapp/sync/verify with extracted code
        verify_res = await http.post("/api/whatsapp/sync/verify", json={"code": sync_code})
        assert verify_res.status_code == 200
        verify_data = verify_res.json()
        assert verify_data["success"] is True
        assert verify_data["phone_number"] == "919876543210"
        assert verify_data["streak_count"] >= 1
        print(f"  ✅ /api/whatsapp/sync/verify linked user {verify_data['phone_number']} with streak {verify_data['streak_count']}.")

        # Test POST /api/whatsapp/sync/push-progress
        progress_res = await http.post(
            "/api/whatsapp/sync/push-progress",
            json={"phone_number": "919876543210", "day": 10},
        )
        assert progress_res.status_code == 200
        prog_data = progress_res.json()
        assert prog_data["success"] is True
        print(f"  ✅ /api/whatsapp/sync/push-progress updated streak: {prog_data}.")

        # 22. Feature 6: Web requesting a sync code dispatched to WhatsApp
        print("\n[22] Testing Feature 6: POST /api/whatsapp/sync/request-code...")
        req_code_res = await http.post(
            "/api/whatsapp/sync/request-code",
            json={"phone_number": "919876543210"},
        )
        assert req_code_res.status_code == 200
        req_data = req_code_res.json()
        assert req_data["success"] is True
        assert req_data.get("code_preview") is not None
        print(f"  ✅ Web requested sync code generated and sent: {req_data.get('code_preview')}.")

    print("\n" + "=" * 70)
    print("🎉 ALL 22 VERIFICATION & ENHANCEMENT TESTS PASSED WITH 100% SUCCESS!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(run_tests())
