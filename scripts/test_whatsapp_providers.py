"""
Automated Verification Suite for Pluggable WhatsApp Provider Architecture.
Tests Meta WhatsApp Business Cloud API Provider, WA-AKG Provider, Simulation Provider,
Provider Registry, Webhook Handlers (GET verification & POST parsing), and Admin Dashboard Configuration.
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
from app.main import app
from app.admin.auth import create_session_token, COOKIE_NAME
from whatsapp_gateway.config import config, save_persisted_config
from whatsapp_gateway.providers import (
    BaseWhatsAppProvider,
    MetaCloudApiProvider,
    SimulationProvider,
    WaAkgProvider,
    get_active_provider,
    get_provider_registry,
    normalize_meta_phone,
    provider_registry,
)
from whatsapp_gateway.routes.webhook import get_client


async def run_provider_tests():
    print("=" * 75)
    print("📱 Running WhatsApp Pluggable Provider Architecture & Admin Test Suite")
    print("=" * 75)

    # Backup original config to restore in teardown
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "whatsapp_config.json")
    orig_config = None
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            orig_config = f.read()

    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver", follow_redirects=False) as http:

            # -------------------------------------------------------------
            # 1. Provider Registry Inspection
            # -------------------------------------------------------------
            print("\n[1] Testing Provider Registry & Provider Discovery...")
            registry = get_provider_registry()
            providers = registry.list_providers()
            prov_names = [p["name"] for p in providers]
            assert "meta_cloud_api" in prov_names, "Meta Cloud API provider missing from registry"
            assert "wa_akg" in prov_names, "WA-AKG provider missing from registry"
            assert "simulation" in prov_names, "Simulation provider missing from registry"
            print(f"  ✅ Registry correctly enumerated {len(providers)} providers: {prov_names}")

            # -------------------------------------------------------------
            # 2. Phone Number Normalization
            # -------------------------------------------------------------
            print("\n[2] Testing Meta Phone Number Normalization...")
            assert normalize_meta_phone("+91 98765-43210") == "919876543210"
            assert normalize_meta_phone("919876543210@s.whatsapp.net") == "919876543210"
            assert normalize_meta_phone("  +1 (555) 123-4567  ") == "15551234567"
            print("  ✅ Meta international phone digits normalization passed all formats.")

            # -------------------------------------------------------------
            # 3. Meta Webhook GET Verification (hub.challenge / hub.verify_token)
            # -------------------------------------------------------------
            print("\n[3] Testing Meta Webhook GET Subscription Verification...")
            # Valid verify token
            res = await http.get(
                "/api/whatsapp/meta-webhook",
                params={
                    "hub.mode": "subscribe",
                    "hub.verify_token": config.meta_verify_token,
                    "hub.challenge": "1158201236",
                },
            )
            assert res.status_code == 200, f"Expected 200, got {res.status_code}"
            assert res.text == "1158201236", f"Expected '1158201236', got {res.text}"
            print("  ✅ Meta Webhook GET verification returned hub.challenge on matching token.")

            # Invalid verify token -> 403 Forbidden
            res_bad = await http.get(
                "/api/whatsapp/meta-webhook",
                params={
                    "hub.mode": "subscribe",
                    "hub.verify_token": "wrong_token_here",
                    "hub.challenge": "1158201236",
                },
            )
            assert res_bad.status_code == 403, f"Expected 403, got {res_bad.status_code}"
            print("  ✅ Meta Webhook rejected invalid verify token with HTTP 403.")

            # Test fallback on primary /api/whatsapp/webhook endpoint
            res_primary = await http.get(
                "/api/whatsapp/webhook",
                params={
                    "hub.mode": "subscribe",
                    "hub.verify_token": config.meta_verify_token,
                    "hub.challenge": "99887766",
                },
            )
            assert res_primary.status_code == 200
            assert res_primary.text == "99887766"
            print("  ✅ Primary /webhook endpoint also supports Meta GET verification.")

            # -------------------------------------------------------------
            # 4. Meta Webhook POST Ingestion (Incoming User Message)
            # -------------------------------------------------------------
            print("\n[4] Testing Meta Webhook POST Ingestion & Dispatcher Routing...")
            meta_incoming_payload = {
                "object": "whatsapp_business_account",
                "entry": [
                    {
                        "id": "WABA_TEST_123",
                        "changes": [
                            {
                                "value": {
                                    "messaging_product": "whatsapp",
                                    "metadata": {
                                        "display_phone_number": "15550001234",
                                        "phone_number_id": "PHONE_NUM_9988",
                                    },
                                    "contacts": [
                                        {"profile": {"name": "Grace Hopper"}, "wa_id": "919876543210"}
                                    ],
                                    "messages": [
                                        {
                                            "from": "919876543210",
                                            "id": "wamid.HBgLM...",
                                            "timestamp": "1730000000",
                                            "type": "text",
                                            "text": {"body": "John 3:16"},
                                        }
                                    ],
                                },
                                "field": "messages",
                            }
                        ],
                    }
                ],
            }

            res = await http.post("/api/whatsapp/meta-webhook", json=meta_incoming_payload)
            assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
            data = res.json()
            assert data.get("sender") == "919876543210@s.whatsapp.net"
            assert "John 3:16" in data.get("text_preview", "")
            print(f"  ✅ Meta Cloud API message parsed and dispatched: {data.get('text_preview')}")

            # -------------------------------------------------------------
            # 5. Meta Webhook POST Delivery Status Receipt (Acknowledge cleanly)
            # -------------------------------------------------------------
            print("\n[5] Testing Meta Webhook Delivery Status Receipt (Statuses event)...")
            meta_status_payload = {
                "object": "whatsapp_business_account",
                "entry": [
                    {
                        "id": "WABA_TEST_123",
                        "changes": [
                            {
                                "value": {
                                    "messaging_product": "whatsapp",
                                    "statuses": [
                                        {
                                            "id": "wamid.HBgLM...",
                                            "status": "delivered",
                                            "timestamp": "1730000050",
                                            "recipient_id": "919876543210",
                                        }
                                    ],
                                },
                                "field": "messages",
                            }
                        ],
                    }
                ],
            }
            res_status = await http.post("/api/whatsapp/meta-webhook", json=meta_status_payload)
            assert res_status.status_code == 200
            assert res_status.json().get("type") == "status_update_or_unsupported"
            print("  ✅ Meta delivery status update handled gracefully with HTTP 200.")

            # -------------------------------------------------------------
            # 6. GET /api/whatsapp/providers API
            # -------------------------------------------------------------
            print("\n[6] Testing GET /api/whatsapp/providers listing...")
            res = await http.get("/api/whatsapp/providers")
            assert res.status_code == 200
            data = res.json()
            assert data["status"] == "ok"
            assert len(data["providers"]) >= 3
            print(f"  ✅ Providers API returned {len(data['providers'])} plugins; active: {data['active_provider']}")

            # -------------------------------------------------------------
            # 7. Admin Settings Dashboard Provider Configuration
            # -------------------------------------------------------------
            print("\n[7] Testing Admin Settings Dashboard & Runtime Provider Hot-Swapping...")
            token = create_session_token("admin")
            cookies = {COOKIE_NAME: token}

            # Switch to Meta Cloud API via Admin API
            meta_config_payload = {
                "provider": "meta_cloud_api",
                "enable_simulation_mode": False,
                "meta_phone_number_id": "104928372819283",
                "meta_waba_id": "192837465019283",
                "meta_access_token": "EAAG_TEST_TOKEN_XYZ",
                "meta_verify_token": "custom_bible_verify_secret",
                "meta_api_version": "v21.0",
            }
            res = await http.post("/admin/api/whatsapp/config", json=meta_config_payload, cookies=cookies)
            assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
            res_json = res.json()
            assert res_json["config"]["provider"] == "meta_cloud_api"
            assert res_json["config"]["meta_phone_number_id"] == "104928372819283"
            assert res_json["config"]["has_meta_access_token"] is True
            print("  ✅ Switched active provider to 'meta_cloud_api' via Admin API.")

            client = get_client()
            assert client.provider == "meta_cloud_api"
            assert client.meta_provider.phone_number_id == "104928372819283"
            assert client.meta_provider.verify_token == "custom_bible_verify_secret"
            print("  ✅ Runtime WAClient singleton and Meta provider successfully updated live.")

            # Verify GET /api/whatsapp/status reflects Meta Cloud API
            res_st = await http.get("/api/whatsapp/status")
            assert res_st.status_code == 200
            st_data = res_st.json()
            assert st_data["provider"] == "meta_cloud_api"
            print("  ✅ /api/whatsapp/status reports active provider as 'meta_cloud_api'.")

            # -------------------------------------------------------------
            # 8. Admin Settings Page HTML Rendering
            # -------------------------------------------------------------
            print("\n[8] Testing Admin Settings Page HTML UI for Provider Controls...")
            res_html = await http.get("/admin/settings", cookies=cookies)
            assert res_html.status_code == 200
            html_text = res_html.text
            assert "WhatsApp Gateway & Provider Plugins" in html_text
            assert "Meta Cloud API" in html_text
            assert "wa_meta_phone_number_id" in html_text
            assert "wa_meta_webhook_full_url" in html_text
            assert "tab-btn-meta_cloud_api" in html_text
            assert "tab-btn-wa_akg" in html_text
            assert "tab-btn-simulation" in html_text
            print("  ✅ Admin Settings HTML rendered with 3 provider tabs and Meta Cloud input fields.")

            # -------------------------------------------------------------
            # 9. Ping Active Provider via Admin API
            # -------------------------------------------------------------
            print("\n[9] Testing POST /admin/api/whatsapp/ping-gateway with active provider...")
            res_ping = await http.post("/admin/api/whatsapp/ping-gateway", cookies=cookies)
            assert res_ping.status_code == 200
            ping_data = res_ping.json()
            assert ping_data["provider"] == "meta_cloud_api"
            print(f"  ✅ Provider ping executed with status '{ping_data['status']}' ({ping_data.get('latency_ms')}ms).")

            # -------------------------------------------------------------
            # 10. Switch Back to Simulation Provider
            # -------------------------------------------------------------
            print("\n[10] Testing Switch to Simulation Provider...")
            sim_payload = {"provider": "simulation", "enable_simulation_mode": True}
            res_sim = await http.post("/admin/api/whatsapp/config", json=sim_payload, cookies=cookies)
            assert res_sim.status_code == 200
            assert client.simulation_mode is True
            print("  ✅ Successfully toggled back to Simulation Provider.")

    finally:
        # Restore original config file
        if orig_config is not None:
            with open(config_path, "w", encoding="utf-8") as f:
                f.write(orig_config)
            print("\n[Teardown] Original whatsapp_config.json restored.")

    print("\n" + "=" * 75)
    print("🎉 ALL 10 PLUGGABLE WHATSAPP PROVIDER TESTS PASSED WITH 100% SUCCESS!")
    print("=" * 75)


if __name__ == "__main__":
    asyncio.run(run_provider_tests())
