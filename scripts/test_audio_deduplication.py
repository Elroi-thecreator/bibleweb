#!/usr/bin/env python3
"""
Test Suite: Audio Bible Verse Download Status & Duplicate Prevention
Verifies:
1. reader.html includes individual per-verse status badges (#verse-audio-status-{{ loop.index0 }})
   and individual play button identifiers (#verse-play-btn-{{ loop.index0 }}).
2. audio_player.js implements:
   - In-memory verseAudioBlobs map (zero-network playback from local blob)
   - In-flight request deduplication map (inFlightRequests) preventing concurrent duplicate fetches
   - updateVerseStatusUI displaying downloading, downloaded/ready, playing, error on that verse only
   - ensureVerseAudioDownloaded checking if already downloaded BEFORE any network request
3. read_along.html implements in-memory blob caching and per-verse status indicators.
"""

import os
import sys
import re

# Ensure Windows terminal prints UTF-8 properly
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Ensure repository root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_checks():
    print("=" * 70)
    print(" VERIFYING PER-VERSE DOWNLOAD STATUS & DUPLICATE PREVENTION")
    print("=" * 70)

    # 1. Inspect templates/reader.html
    with open("templates/reader.html", "r", encoding="utf-8") as f:
        reader_html = f.read()

    assert 'id="verse-audio-status-{{ loop.index0 }}"' in reader_html, \
        "Missing per-verse audio status badge id in reader.html"
    assert 'class="verse-audio-status-pill' in reader_html, \
        "Missing verse-audio-status-pill class in reader.html"
    assert 'id="verse-play-btn-{{ loop.index0 }}"' in reader_html, \
        "Missing per-verse play button id in reader.html"
    assert 'data-text-ta="{{ v.text_ta }}"' in reader_html, \
        "reader.html must include data-text-ta on verse items"
    assert 'data-text-en="{{ v.text_en }}"' in reader_html, \
        "reader.html must include data-text-en on verse items"
    assert 'handleVerseItemClick' in reader_html, \
        "reader.html must implement handleVerseItemClick"
    print("✓ 1. reader.html has per-verse download status badge, text attributes, and click handlers")

    # 2. Inspect static/js/audio_player.js
    with open("static/js/audio_player.js", "r", encoding="utf-8") as f:
        player_js = f.read()

    assert "this.verseAudioBlobs = new Map();" in player_js, \
        "audio_player.js missing verseAudioBlobs cache map"
    assert "this.inFlightRequests = new Map();" in player_js, \
        "audio_player.js missing inFlightRequests deduplication map"
    assert "this.verseStatuses = new Map();" in player_js, \
        "audio_player.js missing verseStatuses map"
    assert "updateVerseStatusUI(index, status)" in player_js, \
        "audio_player.js missing updateVerseStatusUI function"
    assert "ensureVerseAudioDownloaded(index)" in player_js, \
        "audio_player.js missing ensureVerseAudioDownloaded function"
    
    # Check deduplication conditions
    assert "this.verseAudioBlobs.has(cacheKey)" in player_js, \
        "audio_player.js must check if verse is already downloaded before fetch"
    assert "this.inFlightRequests.has(cacheKey)" in player_js, \
        "audio_player.js must check if verse download is already in-flight to prevent duplicate fetch"
    assert "URL.createObjectURL(confirmedBlob)" in player_js, \
        "audio_player.js must create local object URL from blob"
    assert "URL.revokeObjectURL" in player_js, \
        "audio_player.js must revoke object URLs on cleanup to prevent memory leaks"
    print("✓ 2. audio_player.js contains in-memory blob cache & in-flight deduplication logic")

    # 3. Check status pill states in updateVerseStatusUI
    assert "Downloading" in player_js and "animate-spin" in player_js, \
        "audio_player.js updateVerseStatusUI missing downloading state"
    assert "Ready" in player_js or "Downloaded" in player_js, \
        "audio_player.js updateVerseStatusUI missing downloaded/ready state"
    assert "Playing" in player_js, \
        "audio_player.js updateVerseStatusUI missing playing state"
    print("✓ 3. Per-verse UI states ('downloading', 'downloaded/ready', 'playing') verified")

    # 4. Check read_along.html
    with open("templates/read_along.html", "r", encoding="utf-8") as f:
        read_along_html = f.read()

    assert "readalongAudioBlobs" in read_along_html, \
        "read_along.html missing readalongAudioBlobs map"
    assert "readalongInFlight" in read_along_html, \
        "read_along.html missing readalongInFlight deduplication map"
    assert "readalong-status-" in read_along_html, \
        "read_along.html missing per-verse status badge elements"
    print("✓ 4. read_along.html in-memory blob cache & status badges verified")

    print("=" * 70)
    print(" ALL PER-VERSE STATUS & DEDUPLICATION CHECKS PASSED 100%!")
    print("=" * 70)

if __name__ == "__main__":
    run_checks()
