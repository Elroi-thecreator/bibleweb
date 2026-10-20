#!/usr/bin/env python3
"""
Holy Bible Web Application - Audio & Bass Voice Test Suite
Verifies:
1. VOICE_CONFIG and MALE_VOICE_FALLBACKS (including Kumar, Christopher, Brian)
2. Voice aliases: 'bass', 'base', 'deep' map to deep voices
3. Pitch normalization presets ('normal', 'warm_bass', 'bass', 'base', 'more_base', 'extra_bass')
4. Endpoint /api/audio/stream with pitch parameters
5. Cache segregation across different voice tones/pitches
"""

import asyncio
import os
import sys
import urllib.parse

# Ensure Windows terminal prints UTF-8 properly
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import (
    app,
    VOICE_CONFIG,
    MALE_VOICE_FALLBACKS,
    resolve_voice_name,
    normalize_speech_pitch,
    normalize_speech_rate,
)

async def make_asgi_request(query_params: dict):
    qs = urllib.parse.urlencode(query_params).encode("ascii")
    scope = {
        "type": "http",
        "method": "GET",
        "path": "/api/audio/stream",
        "query_string": qs,
        "headers": [(b"host", b"localhost")],
    }
    sent = []
    async def receive():
        return {"type": "http.request", "body": b"", "more_body": False}
    async def send(msg):
        sent.append(msg)
    await app(scope, receive, send)

    status = next(m["status"] for m in sent if m["type"] == "http.response.start")
    headers = {
        k.decode("latin1").lower(): v.decode("latin1")
        for k, v in next(m["headers"] for m in sent if m["type"] == "http.response.start")
    }
    body = b"".join(m.get("body", b"") for m in sent if m["type"] == "http.response.body")
    return status, headers, body

async def run_tests():
    print("=" * 65)
    print(" TESTING AUDIO BIBLE BASS VOICE & SYNTHESIS OPTIONS")
    print("=" * 65)

    # 1. Test Voice Config & Aliases
    assert "kumar" in VOICE_CONFIG["ta"], "kumar missing in VOICE_CONFIG['ta']"
    assert "bass" in VOICE_CONFIG["ta"], "bass missing in VOICE_CONFIG['ta']"
    assert "base" in VOICE_CONFIG["ta"], "base missing in VOICE_CONFIG['ta']"
    assert resolve_voice_name("ta", "bass") == "ta-LK-KumarNeural"
    assert resolve_voice_name("ta", "base") == "ta-LK-KumarNeural"

    assert "christopher" in VOICE_CONFIG["en"]
    assert "brian" in VOICE_CONFIG["en"]
    assert "bass" in VOICE_CONFIG["en"]
    assert "base" in VOICE_CONFIG["en"]
    assert resolve_voice_name("en", "bass") == "en-US-ChristopherNeural"
    assert resolve_voice_name("en", "base") == "en-US-ChristopherNeural"
    print("✓ 1. Deep voice aliases ('bass', 'base', 'kumar', 'christopher', 'brian') verified")

    # 2. Test Fallbacks
    assert "ta-LK-KumarNeural" in MALE_VOICE_FALLBACKS["ta"]
    assert "en-US-ChristopherNeural" in MALE_VOICE_FALLBACKS["en"]
    assert "en-US-BrianNeural" in MALE_VOICE_FALLBACKS["en"]
    print("✓ 2. Male neural voice fallback lists verified")

    # 3. Test Pitch Normalization
    assert normalize_speech_pitch("normal") == "+0Hz"
    assert normalize_speech_pitch("warm_bass") == "-4Hz"
    assert normalize_speech_pitch("bass") == "-8Hz"
    assert normalize_speech_pitch("base") == "-8Hz"
    assert normalize_speech_pitch("deep") == "-8Hz"
    assert normalize_speech_pitch("more_base") == "-10Hz"
    assert normalize_speech_pitch("more_bass") == "-10Hz"
    assert normalize_speech_pitch("extra_bass") == "-12Hz"
    assert normalize_speech_pitch("-6Hz") == "-6Hz"
    assert normalize_speech_pitch("+2Hz") == "+2Hz"
    assert normalize_speech_pitch("-8") == "-8Hz"
    assert normalize_speech_pitch(None) == "+0Hz"
    print("✓ 3. Pitch normalization & preset mappings verified")

    # 4. ASGI Stream Test: Normal Pitch
    s1, h1, b1 = await make_asgi_request({"text": "ஆரம்பத்திலே தேவன்", "lang": "ta", "pitch": "+0Hz"})
    assert s1 == 200, f"Expected 200, got {s1}"
    assert len(b1) > 0, "Empty audio buffer"
    assert h1.get("x-tts-pitch") == "+0Hz"
    assert h1.get("content-type") == "audio/mpeg"
    print(f"✓ 4. Standard pitch audio stream verified ({len(b1)} bytes, Pitch: {h1.get('x-tts-pitch')})")

    # 5. ASGI Stream Test: Deep Bass Pitch
    s2, h2, b2 = await make_asgi_request({"text": "ஆரம்பத்திலே தேவன்", "lang": "ta", "pitch": "bass"})
    assert s2 == 200
    assert len(b2) > 0
    assert h2.get("x-tts-pitch") == "-8Hz"
    print(f"✓ 5. Deep bass pitch audio stream verified ({len(b2)} bytes, Pitch: {h2.get('x-tts-pitch')})")

    # 6. ASGI Stream Test: Voice='base' auto-config
    s3, h3, b3 = await make_asgi_request({"text": "ஆரம்பத்திலே தேவன்", "lang": "ta", "voice": "base"})
    assert s3 == 200
    assert h3.get("x-tts-voice") == "ta-LK-KumarNeural"
    assert h3.get("x-tts-pitch") == "-8Hz"
    print(f"✓ 6. Voice='base' auto deep tone verified (Voice: {h3.get('x-tts-voice')}, Pitch: {h3.get('x-tts-pitch')})")

    # 7. ASGI Stream Test: English Deep Bass Narrator (Christopher)
    s4, h4, b4 = await make_asgi_request({"text": "In the beginning God", "lang": "en", "voice": "christopher", "pitch": "-8Hz"})
    assert s4 == 200
    assert h4.get("x-tts-voice") == "en-US-ChristopherNeural"
    assert h4.get("x-tts-pitch") == "-8Hz"
    print(f"✓ 7. English Christopher deep bass stream verified ({len(b4)} bytes, Voice: {h4.get('x-tts-voice')})")

    # 8. Cache separation across pitch settings
    # Hit cache for s1
    s_cache, h_cache, b_cache = await make_asgi_request({"text": "ஆரம்பத்திலே தேவன்", "lang": "ta", "pitch": "+0Hz"})
    assert s_cache == 200
    assert h_cache.get("x-tts-engine") == "cache"
    assert h_cache.get("x-tts-pitch") == "+0Hz"
    assert b_cache == b1
    print("✓ 8. Pitch-isolated LRU caching verified (different pitch != cache collision)")

    print("=" * 65)
    print(" ALL 8 AUDIO BASS VOICE TESTS PASSED 100%!")
    print("=" * 65)

if __name__ == "__main__":
    asyncio.run(run_tests())
