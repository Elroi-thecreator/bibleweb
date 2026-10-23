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
from whatsapp_gateway.routes.webhook import get_client, get_session_store
from whatsapp_gateway.subscribers import get_subscriber_count, is_subscribed


async def run_tests():
    print("=" * 70)
    print("🧪 Running Decoupled WhatsApp Gateway Enhanced Verification Suite")
    print("=" * 70)

    client = get_client()
    client.simulation_mode = True
    session_store = get_session_store()

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
        print("  ✅ Web Hub UI rendered with 200 OK.")

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
        print("  ✅ 'Hi' auto-reply and available options menu verified.")

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

        # Devotional Push to Subscribers
        print("\n[10] Testing Devotional Broadcast Trigger...")
        push_res = await http.post("/api/whatsapp/push-devotional")
        assert push_res.status_code == 200
        p_data = push_res.json()
        assert p_data["success"] >= 1
        print(f"  ✅ Devotional broadcast successfully delivered to {p_data['success']} subscribers.")

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

        # 13. Test Reading Plan Command
        print("\n[13] Testing Reading Plan 'plan'...")
        outbox = await send_simulated_msg("plan")
        assert len(outbox) == 1
        assert "Daily Scripture Reading Plan" in outbox[0]["text"]
        print("  ✅ Reading plan information successfully displayed.")

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

        # 15. Test Administrative Broadcast Endpoint
        print("\n[15] Testing POST /api/whatsapp/broadcast...")
        broadcast_res = await http.post(
            "/api/whatsapp/broadcast",
            json={
                "recipients": ["919876543210@s.whatsapp.net", "919988776655@s.whatsapp.net"],
                "message": "🕊️ Blessed morning! Today's devotional is now available.",
            },
        )
        assert broadcast_res.status_code == 200
        b_data = broadcast_res.json()
        assert b_data["total"] == 2
        print(f"  ✅ Broadcast delivered to {b_data['total']} simulated recipients.")

    print("\n" + "=" * 70)
    print("🎉 ALL 15 VERIFICATION & ENHANCEMENT TESTS PASSED WITH 100% SUCCESS!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(run_tests())
