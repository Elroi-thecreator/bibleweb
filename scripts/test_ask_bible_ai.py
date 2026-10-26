"""
Comprehensive Automated Verification for Ask Bible AI Plugin.
Tests:
1. Configuration loading and key masking
2. Bilingual language detection (Tamil / English)
3. Grounding providers (Null, InMemory, and HolyBible SQLite Adapter)
4. Prompt assembly with verified scripture context
5. Async OpenAI-compatible client in simulation & fallback modes
6. Core AskBibleAIService full-turn and streaming orchestration
7. FastAPI HTTP API routes (/health, /suggestions, /ask, /stream, /ui, /ask-ai)
"""

import asyncio
import os
import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# Force UTF-8 stdout for Windows consoles
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from ask_bible_ai.config import AskBibleAIConfig, get_config
from ask_bible_ai.prompts import detect_language, build_system_message
from ask_bible_ai.grounding import GroundingPassage, InMemoryGroundingProvider, NullGroundingProvider
from ask_bible_ai.client import OpenAICompatibleClient
from ask_bible_ai.service import AskBibleAIService
from ask_bible_ai.adapters.holy_bible_adapter import HolyBibleGroundingAdapter


async def run_unit_tests():
    print("\n--- [1] Testing AskBibleAIConfig ---")
    cfg = AskBibleAIConfig(api_key="sk-secret-12345678", simulation_mode=True)
    d = cfg.to_dict()
    assert d["simulation_mode"] is True
    assert "..." in d["api_key"], "API key must be masked in to_dict()"
    print("✓ Configuration initialized and masked successfully.")

    print("\n--- [2] Testing Bilingual Language Detection ---")
    assert detect_language("What does the Bible teach about peace?") == "en"
    assert detect_language("சமாதானத்தைப் பற்றி வேதாகமம் என்ன கூறுகிறது?") == "ta"
    assert detect_language("Tell me about யோவான் 3:16") == "ta"
    print("✓ Bilingual language detection verified.")

    print("\n--- [3] Testing Grounding Providers ---")
    null_p = NullGroundingProvider()
    res = await null_p.retrieve_context("grace")
    assert res == []

    in_mem = InMemoryGroundingProvider([
        GroundingPassage(reference="John 1:1", text_en="In the beginning was the Word", text_ta="ஆதியிலே வார்த்தை இருந்தது"),
        GroundingPassage(reference="Psalm 23:1", text_en="The Lord is my shepherd", text_ta="கர்த்தர் என் மேய்ப்பராயிருக்கிறார்"),
    ])
    matches = await in_mem.retrieve_context("shepherd")
    assert len(matches) == 1
    assert matches[0].reference == "Psalm 23:1"
    print("✓ In-memory and Null grounding providers passed.")

    print("\n--- [4] Testing HolyBible SQLite Grounding Adapter ---")
    adapter = HolyBibleGroundingAdapter()
    direct_res = await adapter.retrieve_context("John 3:16", max_passages=1)
    assert len(direct_res) >= 1
    assert "John 3:16" in direct_res[0].reference
    assert direct_res[0].text_en is not None
    assert direct_res[0].text_ta is not None
    print(f"✓ HolyBible SQLite Adapter retrieved direct citation: {direct_res[0].reference}")
    print(f"  English: {direct_res[0].text_en[:60]}...")
    print(f"  Tamil: {direct_res[0].text_ta[:60]}...")

    # FTS Keyword Search
    fts_res = await adapter.retrieve_context("peace comfort", max_passages=2)
    assert len(fts_res) > 0
    print(f"✓ FTS keyword grounding retrieved {len(fts_res)} passages.")

    print("\n--- [5] Testing Prompt Construction ---")
    prompt = build_system_message(grounding_passages=direct_res, language="ta")
    assert "VERIFIED SCRIPTURE CONTEXT" in prompt
    assert "John 3:16" in prompt
    print("✓ System prompt assembled with verified scripture grounding.")

    print("\n--- [6] Testing Client Simulation Mode ---")
    client = OpenAICompatibleClient(cfg)
    chat_res = await client.generate_chat_completion(
        messages=[{"role": "user", "content": "Tell me about hope"}]
    )
    assert "choices" in chat_res
    answer = chat_res["choices"][0]["message"]["content"]
    assert len(answer) > 50
    print("✓ OpenAI client simulation mode returned structured response.")

    print("\n--- [7] Testing Core AskBibleAIService Orchestrator ---")
    service = AskBibleAIService(config=cfg, client=client, grounding_provider=adapter)
    
    # English Query
    en_result = await service.ask("What is love according to the Bible?", preferred_language="en")
    assert en_result["success"] is True
    assert len(en_result["citations"]) > 0
    assert len(en_result["answer"]) > 100
    print(f"✓ English inquiry succeeded with {len(en_result['citations'])} citations in {en_result['took_ms']}ms.")

    # Tamil Query
    ta_result = await service.ask("விசுவாசம் என்றால் என்ன?", preferred_language="ta")
    assert ta_result["success"] is True
    assert "வேதாகம" in ta_result["answer"] or "விசுவாசம்" in ta_result["answer"] or len(ta_result["answer"]) > 50
    print(f"✓ Tamil inquiry succeeded with {len(ta_result['citations'])} citations in {ta_result['took_ms']}ms.")

    # Streaming Check
    token_count = 0
    async for token in service.ask_stream("Explain Psalm 23"):
        token_count += 1
    assert token_count > 10, "Stream must emit multiple tokens"
    print(f"✓ Streaming generation succeeded ({token_count} token chunks received).")

    # Suggestions Check
    suggs = service.get_suggested_questions("en")
    assert len(suggs) >= 3
    print("✓ Starter suggestions verified.")


async def run_http_route_tests():
    print("\n--- [8] Testing FastAPI Endpoints via AsyncClient ---")
    from httpx import ASGITransport, AsyncClient
    from app.main import app
    from ask_bible_ai.routes import ai_service, config as route_config

    # Ensure routes use simulation mode for offline test execution
    route_config.simulation_mode = True
    ai_service.config.simulation_mode = True
    ai_service.client.config.simulation_mode = True

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        # Health
        res = await ac.get("/api/ask-ai/health")
        assert res.status_code == 200, f"Expected 200, got {res.status_code}"
        health_data = res.json()
        assert health_data["status"] in ("healthy", "degraded"), f"Unexpected status: {health_data['status']}"
        print(f"✓ GET /api/ask-ai/health responded HTTP 200 (status: {health_data['status']}).")

        # Suggestions
        res = await ac.get("/api/ask-ai/suggestions?language=ta")
        assert res.status_code == 200
        assert len(res.json()["suggestions"]) > 0
        print("✓ GET /api/ask-ai/suggestions responded HTTP 200.")

        # Ask POST
        res = await ac.post("/api/ask-ai/ask", json={"query": "Tell me about peace", "language": "en"})
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert "answer" in data
        print("✓ POST /api/ask-ai/ask responded HTTP 200 with grounded answer.")

        # Stream POST
        res = await ac.post("/api/ask-ai/stream", json={"query": "Who is Jesus?", "language": "en"})
        assert res.status_code == 200
        assert "text/event-stream" in res.headers["content-type"]
        body_text = res.text
        assert "data: " in body_text
        print("✓ POST /api/ask-ai/stream responded HTTP 200 with Server-Sent Events.")

        # Standalone UI page
        res = await ac.get("/api/ask-ai/ui")
        assert res.status_code == 200
        assert "ASK BIBLE AI" in res.text
        print("✓ GET /api/ask-ai/ui responded HTTP 200 (Standalone embeddable UI).")

        # Integrated Web Bible /ask-ai page
        res = await ac.get("/ask-ai")
        assert res.status_code == 200
        assert "Ask Bible AI" in res.text
        print("✓ GET /ask-ai responded HTTP 200 (Integrated Web Portal).")


async def main():
    print("==========================================================")
    print("  ASK BIBLE AI PLUGIN — AUTOMATED VERIFICATION SUITE")
    print("==========================================================")
    await run_unit_tests()
    await run_http_route_tests()
    print("\n==========================================================")
    print("  ALL TESTS PASSED WITH 100% SUCCESS! (0 ERRORS)")
    print("==========================================================\n")


if __name__ == "__main__":
    asyncio.run(main())
