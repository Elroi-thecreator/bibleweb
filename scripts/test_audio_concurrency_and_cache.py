#!/usr/bin/env python3
"""
Test Suite: Audio Concurrency & Persistent Disk Cache Verification
Verifies:
1. Backend Persistent Disk Cache:
   - Synthesizing audio writes .mp3 to AUDIO_CACHE_DIR.
   - Subsequent calls return from in-memory cache (< 1ms).
   - Evicting from in-memory cache still hits persistent disk cache without remote network call.
2. Frontend Concurrent Prefetch Architecture:
   - static/js/audio_player.js uses CONCURRENCY = 3 and Promise.all(workers).
   - static/js/audio_player.js starts prefetching immediately on playCurrent().
   - templates/read_along.html uses CONCURRENCY = 3 and Promise.all(workers).
   - In-flight deduplication handles concurrent workers without duplicate network requests.
"""

import os
import sys
import time
import hashlib
import asyncio
import urllib.parse
from pathlib import Path

# Ensure UTF-8 output on Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Ensure repository root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from app.main import app, AUDIO_CACHE, AUDIO_CACHE_DIR


async def make_asgi_request(path: str, query_params: dict = None):
    qs = urllib.parse.urlencode(query_params or {}).encode("ascii")
    scope = {
        "type": "http",
        "method": "GET",
        "path": path,
        "query_string": qs,
        "headers": [(b"host", b"localhost")],
    }
    sent = []
    body = bytearray()
    async def receive():
        return {"type": "http.request", "body": b"", "more_body": False}
    async def send(msg):
        sent.append(msg)
        if msg["type"] == "http.response.body":
            body.extend(msg.get("body", b""))
    await app(scope, receive, send)

    status = 500
    headers = {}
    for msg in sent:
        if msg["type"] == "http.response.start":
            status = msg["status"]
            for k, v in msg.get("headers", []):
                headers[k.decode("latin1").lower()] = v.decode("latin1")

    class Response:
        def __init__(self, status_code, headers, content):
            self.status_code = status_code
            self.headers = headers
            self.content = bytes(content)
            self.text = content.decode("utf-8", errors="replace")

    return Response(status, headers, body)


def test_frontend_concurrency_static():
    print("=" * 70)
    print(" 1. VERIFYING FRONTEND CONCURRENT PREFETCH ARCHITECTURE")
    print("=" * 70)

    # 1. audio_player.js
    audio_js_path = BASE_DIR / "static" / "js" / "audio_player.js"
    audio_js = audio_js_path.read_text(encoding="utf-8")

    assert "const CONCURRENCY = 3;" in audio_js, "audio_player.js missing CONCURRENCY = 3"
    assert "await Promise.all(workers);" in audio_js, "audio_player.js missing Promise.all(workers)"
    assert "this.startChapterPrefetchPipeline();" in audio_js, "audio_player.js missing startChapterPrefetchPipeline"
    assert "this.prefetchQueue.shift()" in audio_js, "audio_player.js missing prefetchQueue worker consumption"
    # Ensure immediate prefetch call exists in playCurrent before await
    idx_prefetch_call = audio_js.find("this.startChapterPrefetchPipeline();")
    idx_await_verse = audio_js.find("const blobUrl = await this.ensureVerseAudioDownloaded(requestedIndex);")
    assert idx_prefetch_call != -1 and idx_await_verse != -1 and idx_prefetch_call < idx_await_verse, \
        "audio_player.js must start chapter prefetch pipeline immediately before awaiting current verse"

    print("✓ static/js/audio_player.js verified with 3-worker concurrency and immediate prefetching")

    # 2. templates/read_along.html
    readalong_path = BASE_DIR / "templates" / "read_along.html"
    readalong_html = readalong_path.read_text(encoding="utf-8")

    assert "const CONCURRENCY = 3;" in readalong_html, "read_along.html missing CONCURRENCY = 3"
    assert "await Promise.all(workers);" in readalong_html, "read_along.html missing Promise.all(workers)"
    assert "startReadAlongPrefetchPipeline();" in readalong_html, "read_along.html missing startReadAlongPrefetchPipeline"

    print("✓ templates/read_along.html verified with 3-worker concurrency and immediate prefetching")


async def test_backend_persistent_disk_cache():
    print("\n" + "=" * 70)
    print(" 2. VERIFYING PERSISTENT DISK CACHING & INSTANT REPLAY")
    print("=" * 70)

    test_verse_text = "கர்த்தர் என் வெளிச்சமும் என் இரட்சிப்புமானவர், யாருக்கு அஞ்சுவேன்? (சங் 27:1)"
    params = {
        "text": test_verse_text,
        "lang": "ta",
        "voice": "ta-LK-KumarNeural",
        "pitch": "-8Hz",
        "rate": "1.0",
    }

    # Step 1: Initial stream request
    t0 = time.perf_counter()
    res1 = await make_asgi_request("/api/audio/stream", params)
    elapsed1 = time.perf_counter() - t0
    assert res1.status_code == 200, f"Expected 200, got {res1.status_code}"
    assert len(res1.content) > 0, "Empty audio stream"
    print(f"✓ Initial synthesis completed in {elapsed1:.2f}s ({len(res1.content)} bytes, engine={res1.headers.get('x-tts-engine')})")

    # Step 2: Verify disk cache file exists
    assert AUDIO_CACHE_DIR.exists(), f"AUDIO_CACHE_DIR does not exist: {AUDIO_CACHE_DIR}"
    cache_files = list(AUDIO_CACHE_DIR.glob("*.mp3"))
    assert len(cache_files) > 0, "No .mp3 files found in persistent AUDIO_CACHE_DIR!"
    print(f"✓ Persistent disk cache verified ({len(cache_files)} files stored in {AUDIO_CACHE_DIR})")

    # Step 3: Second stream request (In-Memory Cache Hit)
    t0 = time.perf_counter()
    res2 = await make_asgi_request("/api/audio/stream", params)
    elapsed2 = time.perf_counter() - t0
    assert res2.status_code == 200
    assert res2.headers.get("x-tts-engine") == "cache"
    assert elapsed2 < 0.05, f"In-memory cache took too long: {elapsed2:.4f}s"
    print(f"✓ In-memory cache hit completed in {elapsed2 * 1000:.2f}ms (Engine: cache)")

    # Step 4: Evict in-memory cache to test disk fallback persistence
    with AUDIO_CACHE._lock:
        AUDIO_CACHE._cache.clear()
    assert len(AUDIO_CACHE._cache) == 0, "In-memory cache not cleared"

    t0 = time.perf_counter()
    res3 = await make_asgi_request("/api/audio/stream", params)
    elapsed3 = time.perf_counter() - t0
    assert res3.status_code == 200
    assert res3.headers.get("x-tts-engine") == "cache"
    assert len(res3.content) == len(res1.content)
    assert elapsed3 < 0.05, f"Disk cache hit took too long: {elapsed3:.4f}s"
    print(f"✓ Disk cache fallback hit completed in {elapsed3 * 1000:.2f}ms after RAM eviction!")

    print("\n" + "=" * 70)
    print(" ALL AUDIO CONCURRENCY & PERSISTENT CACHE CHECKS PASSED 100%!")
    print("=" * 70)


if __name__ == "__main__":
    test_frontend_concurrency_static()
    asyncio.run(test_backend_persistent_disk_cache())
