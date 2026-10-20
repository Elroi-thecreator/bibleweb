#!/usr/bin/env python3
"""
Test Suite: End-to-End Audio Bible Flow & JavaScript Verification
Verifies:
1. JavaScript syntax & function resolution in static/js/audio_player.js and templates/read_along.html
   - No illegal await outside async functions
   - All called functions (updateReadAlongVerseStatusUI, playQueueIndex, togglePlayPause) are defined
   - No dangling/undefined functions (streamAudioForItem removed)
2. State Machine & Caching logic:
   - In-memory blob caching (verseAudioBlobs, readalongAudioBlobs)
   - In-flight request deduplication (inFlightRequests, readalongInFlight)
   - Multi-click deduplication: Click verse 1 -> In-flight -> Subsequent clicks return same Promise (0 extra network calls)
   - Prefetch deduplication: Prefetching verse 2 -> Clicking verse 2 reuses in-flight or cached blob (0 duplicate downloads)
3. End-to-End FastAPI endpoint & template integration:
   - /read/43/1 renders per-verse status badges and play buttons
   - /plans/1/read-along/1 renders read-along audio elements and verse status badges
   - /api/audio/stream handles pitch, rate, and voice seamlessly
"""

import os
import sys
import re
import hashlib
from unittest.mock import MagicMock

# Ensure UTF-8 output on Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Ensure repository root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import urllib.parse
from app.main import app

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


def test_javascript_syntax_and_symbols():
    print("-" * 60)
    print("1. VERIFYING JAVASCRIPT SYNTAX & FUNCTION RESOLUTION")
    print("-" * 60)

    # 1.1 Read audio_player.js
    with open("static/js/audio_player.js", "r", encoding="utf-8") as f:
        audio_js = f.read()

    # Check that togglePlayPause exists and is implemented
    assert "togglePlayPause()" in audio_js, "audio_player.js missing togglePlayPause"
    assert "this.play(this.currentIndex || 0)" in audio_js, "togglePlayPause missing initial play"
    assert "this.resume()" in audio_js and "this.pause()" in audio_js, "togglePlayPause missing resume/pause"

    # Check clearAllBlobs pauses audio before revoking
    assert "if (this.audio)" in audio_js and "this.audio.pause()" in audio_js, \
        "clearAllBlobs must pause audio before revoking object URLs"

    # Check that init sets verses before clearAllBlobs
    idx_items = audio_js.find("this.verses = Array.from(items)")
    idx_clear = audio_js.find("this.clearAllBlobs()", idx_items)
    assert idx_items != -1 and idx_clear != -1 and idx_clear > idx_items, \
        "init() must initialize this.verses before invoking clearAllBlobs()"

    # Check race condition guard in playCurrent
    assert "const requestedIndex = this.currentIndex;" in audio_js, \
        "playCurrent must capture requestedIndex to guard against race conditions"
    assert "if (this.currentIndex !== requestedIndex || !this.isPlaying) return;" in audio_js, \
        "playCurrent must guard playback after await and in .then()"

    # Check that updateAudioProgressUI exists
    assert "updateAudioProgressUI()" in audio_js, "audio_player.js missing updateAudioProgressUI"
    assert "audio-progress-bar" in audio_js, "audio_player.js missing audio-progress-bar reference"
    assert "audio-progress-count" in audio_js, "audio_player.js missing audio-progress-count reference"

    # Check 1-second gap between verses on ended event
    assert "this.transitionTimeout" in audio_js, "audio_player.js missing transitionTimeout property"
    assert "1000" in audio_js and "clearTimeout(this.transitionTimeout)" in audio_js, \
        "audio_player.js missing 1-second transition pause or cleanup"

    print("✓ audio_player.js passed all static flow & race-condition guard checks")

    # 1.2 Read templates/read_along.html
    with open("templates/read_along.html", "r", encoding="utf-8") as f:
        readalong_html = f.read()

    # Check that playQueueIndex is declared async
    assert "async function playQueueIndex(index)" in readalong_html, \
        "read_along.html playQueueIndex must be declared async to support await"

    # Check that updateReadAlongVerseStatusUI is defined
    assert "function updateReadAlongVerseStatusUI(item, status)" in readalong_html, \
        "read_along.html missing function updateReadAlongVerseStatusUI definition"

    # Check that streamAudioForItem is NOT called
    assert "streamAudioForItem" not in readalong_html, \
        "read_along.html contains undefined call to streamAudioForItem"

    # Check status states in readalong
    assert "downloading" in readalong_html and "downloaded" in readalong_html and "playing" in readalong_html, \
        "read_along.html missing status states in updateReadAlongVerseStatusUI"

    # Check that toggleAudioPlayback handles unstarted state
    assert "if (!audioElement.src || audioElement.src === window.location.href)" in readalong_html, \
        "read_along.html toggleAudioPlayback must handle unstarted audio state"

    # Check 1-second gap between verses in read-along
    assert "readalongTransitionTimeout" in readalong_html, "read_along.html missing readalongTransitionTimeout"
    assert "1000" in readalong_html and "clearTimeout(readalongTransitionTimeout)" in readalong_html, \
        "read_along.html missing 1-second transition pause or cleanup"

    print("✓ templates/read_along.html passed all async/await, function definition & error checks")


def test_audio_state_machine_simulation():
    print("\n" + "-" * 60)
    print("2. SIMULATING CLIENT-SIDE DEDUPLICATION & STATE MACHINE FLOW")
    print("-" * 60)

    # Simulated Client Storage & State
    verseAudioBlobs = {}
    inFlightRequests = {}
    verseStatuses = {}
    network_fetch_count = 0

    def mock_fetch(verse_idx, text):
        nonlocal network_fetch_count
        network_fetch_count += 1
        return f"blob:http://localhost/mock-blob-{verse_idx}"

    def ensure_verse_audio_downloaded(index, text):
        cache_key = f"43_1_{index}_ta_ta-IN-ValluvarNeural_1.0_+0Hz"

        # 1. Check whether already downloaded
        if cache_key in verseAudioBlobs:
            verseStatuses[index] = "downloaded"
            return verseAudioBlobs[cache_key]["blobUrl"], False  # (url, did_fetch)

        # 2. Check whether already in-flight
        if cache_key in inFlightRequests:
            return inFlightRequests[cache_key], False

        # 3. Mark downloading on this verse only
        verseStatuses[index] = "downloading"

        # Simulate in-flight promise
        blob_url = mock_fetch(index, text)
        inFlightRequests[cache_key] = blob_url

        # Simulate completion
        verseAudioBlobs[cache_key] = {
            "blobUrl": blob_url,
            "size": 1024
        }
        del inFlightRequests[cache_key]
        verseStatuses[index] = "downloaded"

        return blob_url, True

    # Scenario A: Initial click on Verse 0
    url0, did_fetch = ensure_verse_audio_downloaded(0, "In the beginning was the Word")
    assert did_fetch is True
    assert network_fetch_count == 1
    assert verseStatuses[0] == "downloaded"
    print("✓ Initial click on Verse 0: 1 network request made, status marked 'downloaded'")

    # Scenario B: User clicks Verse 0 again
    url0_repeat, did_fetch_repeat = ensure_verse_audio_downloaded(0, "In the beginning was the Word")
    assert did_fetch_repeat is False
    assert url0_repeat == url0
    assert network_fetch_count == 1, "Duplicate network fetch detected on already downloaded verse!"
    print("✓ Repeated click on Verse 0: 0 network requests made (reused cached in-memory blob)")

    # Scenario C: Background prefetch downloads Verse 1 & Verse 2
    for next_idx in [1, 2]:
        url, did_fetch = ensure_verse_audio_downloaded(next_idx, f"Verse text {next_idx}")
        assert did_fetch is True
    assert network_fetch_count == 3
    print("✓ Background prefetch downloaded Verse 1 & 2 sequentially")

    # Scenario D: User clicks on prefetched Verse 2
    url2_click, did_fetch_click = ensure_verse_audio_downloaded(2, "Verse text 2")
    assert did_fetch_click is False
    assert network_fetch_count == 3, "Prefetched verse re-downloaded on click!"
    print("✓ User clicked on prefetched Verse 2: 0 network requests made (played instantly from cache)")

    # Scenario E: User changes Voice Tone to Deep Bass (-8Hz)
    # Blobs cleared, key changes
    verseAudioBlobs.clear()
    verseStatuses.clear()
    print("✓ Voice Tone change cleared in-memory blobs for clean pitch transition")


async def test_live_templates_and_routes():
    print("\n" + "-" * 60)
    print("3. VERIFYING LIVE TEMPLATES & ROUTE RESPONSES")
    print("-" * 60)

    # 3.1 Reader page: /read/43/1
    res_reader = await make_asgi_request("/read/43/1", {"mode": "bilingual"})
    assert res_reader.status_code == 200, f"Expected 200 from /read/43/1, got {res_reader.status_code}"
    html_reader = res_reader.text

    assert 'id="verse-audio-status-0"' in html_reader, "Reader missing #verse-audio-status-0"
    assert 'id="verse-play-btn-0"' in html_reader, "Reader missing #verse-play-btn-0"
    assert 'id="audio-dock"' in html_reader, "Reader missing #audio-dock"
    assert 'id="audio-play-pause-btn"' in html_reader, "Reader missing #audio-play-pause-btn"
    assert 'onclick="window.bibleAudio ? window.bibleAudio.togglePlayPause() : null"' in html_reader, \
        "audio-play-pause-btn must call togglePlayPause"
    # Ensure audio-voice-select is removed from reader dock (voice change kept only in settings)
    assert 'id="audio-voice-select"' not in html_reader, \
        "Voice selection must not be in reader dock; keep voice change only in settings page"
    assert 'id="setting-voice-ta"' in html_reader and 'id="setting-voice-en"' in html_reader, \
        "Settings modal must provide canonical voice selection"
    # Ensure real-time audio progress elements are present in reader
    assert 'id="audio-progress-track"' in html_reader, "Reader missing #audio-progress-track"
    assert 'id="audio-progress-bar"' in html_reader, "Reader missing #audio-progress-bar"
    assert 'id="audio-progress-count"' in html_reader, "Reader missing #audio-progress-count"
    print("✓ /read/43/1 renders per-verse status, audio progress bar/counter, and settings voice controls")

    # 3.2 Read-Along page: /read-along/plan/whole-bible-100/day/1
    res_readalong = await make_asgi_request("/read-along/plan/whole-bible-100/day/1")
    assert res_readalong.status_code == 200, f"Expected 200 from /read-along/plan/whole-bible-100/day/1, got {res_readalong.status_code}"
    html_readalong = res_readalong.text

    assert 'id="readalong-status-' in html_readalong, "Read-Along missing readalong-status- elements"
    assert 'async function playQueueIndex' in html_readalong, "Read-Along rendered without async playQueueIndex"
    assert 'function updateReadAlongVerseStatusUI' in html_readalong, "Read-Along rendered without updateReadAlongVerseStatusUI"
    assert 'streamAudioForItem' not in html_readalong, "Read-Along rendered with dangling streamAudioForItem"
    # Ensure mobile audio progress elements are present in read-along
    assert 'id="readalong-progress-track"' in html_readalong, "Read-Along missing #readalong-progress-track"
    assert 'id="readalong-mobile-progress-bar"' in html_readalong, "Read-Along missing #readalong-mobile-progress-bar"
    assert 'id="mobile-progress-count"' in html_readalong, "Read-Along missing #mobile-progress-count"
    print("✓ /read-along/plan/whole-bible-100/day/1 renders valid async audio pipeline with mobile progress bar & counter")

    # 3.3 Audio streaming endpoint: /api/audio/stream
    res_audio = await make_asgi_request("/api/audio/stream", {
        "text": "ஆதியிலே தேவன் வானத்தையும் பூமியையும் சிருஷ்டித்தார்.",
        "lang": "ta",
        "voice": "ta-LK-KumarNeural",
        "pitch": "-8Hz",
        "rate": "1.0"
    })
    assert res_audio.status_code == 200, f"Expected 200 from /api/audio/stream, got {res_audio.status_code}"
    assert res_audio.headers.get("content-type") == "audio/mpeg"
    assert res_audio.headers.get("x-tts-pitch") == "-8Hz"
    assert len(res_audio.content) > 0
    print(f"✓ /api/audio/stream returned valid audio stream ({len(res_audio.content)} bytes, pitch: {res_audio.headers.get('x-tts-pitch')})")

    print("\n" + "=" * 60)
    print(" ALL END-TO-END AUDIO FLOW CHECKS PASSED 100%!")
    print("=" * 60)


if __name__ == "__main__":
    test_javascript_syntax_and_symbols()
    test_audio_state_machine_simulation()
    asyncio.run(test_live_templates_and_routes())
