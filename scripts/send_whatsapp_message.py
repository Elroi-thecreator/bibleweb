#!/usr/bin/env python3
"""
Interactive & Automated WhatsApp Message Dispatcher and Verification CLI.
Sends real or simulated messages via WA-AKG Gateway and checks delivery diagnostics.

Usage:
  Interactive Mode:
    py -3 scripts/send_whatsapp_message.py

  CLI Arguments Mode:
    py -3 scripts/send_whatsapp_message.py --to 919876543210 --message "Hello from Holy Bible App!"
    py -3 scripts/send_whatsapp_message.py --to 919876543210 --message "John 3:16" --api-key "akg_..."
"""

import argparse
import asyncio
import os
import sys
import time

# Ensure UTF-8 output on Windows terminals
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Ensure repository root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from whatsapp_gateway.client.client import WAClient
from whatsapp_gateway.config import config as default_config


async def send_message_cli(
    recipient: str,
    message_text: str,
    gateway_url: str,
    session_id: str,
    api_key: str | None = None,
    simulate: bool = False,
    audio_passage: str | None = None,
):
    print("\n" + "=" * 70)
    print("📤 WhatsApp Dispatcher & Gateway Verification")
    print("=" * 70)
    print(f"  🌐 Gateway URL : {gateway_url}")
    print(f"  📱 Session ID  : {session_id}")
    print(f"  🔑 API Key     : {'••••••••' if api_key else '(None configured)'}")
    print(f"  🧪 Mode        : {'SIMULATION (Mock)' if simulate else 'LIVE GATEWAY'}")
    print(f"  🎯 Recipient   : {recipient}")
    if audio_passage:
        print(f"  🎧 Audio Bible : {audio_passage}")
    else:
        print(f"  💬 Message     : {message_text}")
    print("-" * 70)

    client = WAClient(
        base_url=gateway_url,
        default_session_id=session_id,
        api_key=api_key,
        simulation_mode=simulate,
        timeout=25.0,
    )

    t0 = time.time()

    # Pre-flight check (if not in simulation mode)
    if not simulate:
        print("[1/2] 📡 Checking Gateway reachability & session status...")
        try:
            status = await client.get_session_status(session_id=session_id)
            print(f"      Gateway Status Response: {status}")
        except Exception as e:
            print(f"      ⚠️ Warning checking session status: {e}")
    else:
        print("[1/2] 🧪 Simulation active: Skipping live gateway ping.")

    # Dispatch Message or Audio
    if audio_passage:
        print(f"\n[2/2] 🎙️ Synthesizing & dispatching Audio Bible voice note for '{audio_passage}'...")
        try:
            from gtts import gTTS
            import io
            audio_bytes = b""
            try:
                import edge_tts
                comm = edge_tts.Communicate(f"Reading from {audio_passage}. In the beginning was the Word, and the Word was with God, and the Word was God.", "en-US-ChristopherNeural")
                async for chunk in comm.stream():
                    if chunk["type"] == "audio":
                        audio_bytes += chunk["data"]
            except Exception:
                pass

            if not audio_bytes:
                fp = io.BytesIO()
                tts = gTTS(text=f"Reading from {audio_passage}. In the beginning was the Word, and the Word was with God, and the Word was God.", lang="en")
                tts.write_to_fp(fp)
                audio_bytes = fp.getvalue()

            res = await client.send_media(
                to=recipient,
                media_type="audio",
                file_bytes=audio_bytes,
                caption=f"🎧 Audio Bible: {audio_passage}",
                file_name=f"{audio_passage.replace(' ', '_')}.mp3",
                ptt=True,
                session_id=session_id,
            )
            latency = round((time.time() - t0) * 1000, 1)

            if res.success:
                print(f"\n🎉 SUCCESS! Audio voice note delivered in {latency}ms.")
                print(f"  • Message ID  : {res.message_id}")
                print(f"  • Recipient   : {res.to}")
                return True
            else:
                print(f"\n❌ AUDIO DELIVERY FAILED ({latency}ms).")
                print(f"  • Error Details: {res.error}")
                return False
        except Exception as exc:
            latency = round((time.time() - t0) * 1000, 1)
            print(f"\n❌ EXCEPTION DURING AUDIO DISPATCH ({latency}ms): {exc}")
            return False
        finally:
            await client.close()

    print("\n[2/2] 🚀 Sending WhatsApp message...")
    try:
        res = await client.send_text(
            to=recipient,
            text=message_text,
            session_id=session_id,
        )
        latency = round((time.time() - t0) * 1000, 1)

        if res.success:
            print(f"\n🎉 SUCCESS! Message delivered in {latency}ms.")
            print(f"  • Message ID  : {res.message_id}")
            print(f"  • Recipient   : {res.to}")
            if res.raw:
                print(f"  • Raw Response: {res.raw}")
            return True
        else:
            print(f"\n❌ DELIVERY FAILED ({latency}ms).")
            print(f"  • Error Details: {res.error}")
            return False

    except Exception as exc:
        latency = round((time.time() - t0) * 1000, 1)
        print(f"\n❌ EXCEPTION DURING DISPATCH ({latency}ms): {exc}")
        return False
    finally:
        await client.close()


def main():
    parser = argparse.ArgumentParser(description="Send WhatsApp message via WA-AKG Gateway")
    parser.add_argument("--to", help="Recipient phone number (e.g. 919876543210)")
    parser.add_argument("-m", "--message", help="Message text to send")
    parser.add_argument(
        "--gateway-url",
        default=os.getenv("WA_GATEWAY_URL", default_config.gateway_url),
        help="WA-AKG Gateway Base URL (e.g. https://wa-akg-gateway-7rh9.onrender.com/api)",
    )
    parser.add_argument(
        "--session-id",
        default=os.getenv("WA_SESSION_ID", default_config.session_id),
        help="WhatsApp Session ID (default: 'default')",
    )
    parser.add_argument(
        "--api-key",
        default=os.getenv("WA_API_KEY", default_config.api_key),
        help="WA-AKG Gateway API Key",
    )
    parser.add_argument(
        "--audio",
        default=None,
        help="Audio Bible passage to synthesize and dispatch as voice note (e.g. 'John 1', 'Psalm 23')",
    )
    parser.add_argument(
        "--simulate",
        action="store_true",
        help="Run in local simulation mode without hitting external network",
    )

    args = parser.parse_args()

    # Interactive prompt if arguments are omitted
    to_phone = args.to
    if not to_phone:
        print("\n=== WhatsApp Message Interactive Setup ===")
        to_phone = input("Enter recipient phone number with country code (e.g. 919876543210): ").strip()
        while not to_phone:
            to_phone = input("Phone number cannot be empty. Enter phone number: ").strip()

    audio_pass = args.audio
    msg = args.message
    if not msg and not audio_pass:
        default_verse = '📖 "For God so loved the world that He gave His only begotten Son, that whoever believes in Him should not perish but have everlasting life." — John 3:16'
        prompt = f"Enter message text (Press Enter for default John 3:16 Scripture):\n> "
        entered = input(prompt).strip()
        msg = entered if entered else default_verse

    gw_url = args.gateway_url
    sess_id = args.session_id
    key = args.api_key
    sim = args.simulate

    # If gateway URL is default localhost and user didn't specify --gateway-url, use hosted Render gateway
    if "localhost" in gw_url and not args.gateway_url:
        gw_url = "https://wa-akg-gateway-ub6a.onrender.com/api"

    asyncio.run(
        send_message_cli(
            recipient=to_phone,
            message_text=msg or "",
            gateway_url=gw_url,
            session_id=sess_id,
            api_key=key,
            simulate=sim,
            audio_passage=audio_pass,
        )
    )


if __name__ == "__main__":
    main()
