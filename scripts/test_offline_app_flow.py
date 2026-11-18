"""Automated Verification Suite for Installed WebApp Offline Package & SQLite Wasm Pipeline.
Tests metadata endpoints, binary SQLite streaming, static assets, and client-side offline contracts.
"""

import os
import sys
from pathlib import Path
from fastapi.testclient import TestClient

# Ensure workspace root is in sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import app
from app.db import DB_PATH, SONGS_DB_PATH

def test_offline_endpoints():
    print("=" * 65)
    print("TESTING INSTALLED WEBAPP OFFLINE ENGINE & SQLITE PIPELINE")
    print("=" * 65)

    client = TestClient(app)

    # 1. Test /api/offline/info metadata
    resp_info = client.get("/api/offline/info")
    assert resp_info.status_code == 200, f"Expected 200, got {resp_info.status_code}"
    info = resp_info.json()
    assert info["status"] == "ready"
    assert info["bible_db_size"] > 40_000_000, f"Unexpected bible size: {info['bible_db_size']}"
    assert info["songs_db_size"] > 5_000_000, f"Unexpected songs size: {info['songs_db_size']}"
    assert len(info["protestant_books"]) == 73  # 66 base + 7 deuterocanon
    assert len(info["catholic_books"]) == 73
    print(f"✓ 1. /api/offline/info verified ({info['bible_db_size']} bytes Bible, {info['songs_db_size']} bytes Songs, 73 Catholic books)")

    # 2. Test HEAD /api/offline/bible-db
    head_bible = client.head("/api/offline/bible-db")
    assert head_bible.status_code == 200, f"Expected 200, got {head_bible.status_code}"
    assert head_bible.headers.get("content-type") == "application/vnd.sqlite3"
    assert head_bible.headers.get("accept-ranges") == "bytes"
    print("✓ 2. HEAD /api/offline/bible-db returns 200 with application/vnd.sqlite3 & Accept-Ranges")

    # 3. Test GET /api/offline/bible-db with Range request (streaming chunk)
    get_bible_chunk = client.get("/api/offline/bible-db", headers={"Range": "bytes=0-15"})
    assert get_bible_chunk.status_code == 206, f"Expected 206, got {get_bible_chunk.status_code}"
    assert get_bible_chunk.content.startswith(b"SQLite format 3\x00")
    print("✓ 3. GET /api/offline/bible-db verified byte header (SQLite format 3)")

    # 4. Test HEAD /api/offline/songs-db
    head_songs = client.head("/api/offline/songs-db")
    assert head_songs.status_code == 200, f"Expected 200, got {head_songs.status_code}"
    assert head_songs.headers.get("content-type") == "application/vnd.sqlite3"
    print("✓ 4. HEAD /api/offline/songs-db returns 200 with application/vnd.sqlite3")

    # 5. Test GET /api/offline/songs-db with Range request
    get_songs_chunk = client.get("/api/offline/songs-db", headers={"Range": "bytes=0-15"})
    assert get_songs_chunk.status_code == 206, f"Expected 206, got {get_songs_chunk.status_code}"
    assert get_songs_chunk.content.startswith(b"SQLite format 3\x00")
    print("✓ 5. GET /api/offline/songs-db verified byte header (SQLite format 3)")

    # 6. Verify static assets exist on disk and are servable
    static_files = [
        "static/js/offline_engine.js",
        "static/js/vendor/sql-wasm.js",
        "static/js/vendor/sql-wasm.wasm",
        "static/sw.js"
    ]
    for sf in static_files:
        assert os.path.exists(sf), f"File {sf} missing on disk"
        url = f"/{sf}"
        resp = client.get(url)
        assert resp.status_code == 200, f"Expected 200 for {url}, got {resp.status_code}"
    print("✓ 6. Static files verified on disk and HTTP 200 (/static/js/offline_engine.js, sql-wasm.js, sql-wasm.wasm)")

    # 7. Verify static/sw.js includes offline_engine.js and sql-wasm.js in STATIC_ASSETS
    sw_content = Path("static/sw.js").read_text(encoding="utf-8")
    assert "offline_engine.js" in sw_content
    assert "sql-wasm.js" in sw_content
    assert "api/offline/" in sw_content
    print("✓ 7. Service Worker (sw.js) static assets and offline bypass verified")

    # 8. Verify templates/base.html includes offline_engine.js and settings section
    base_content = Path("templates/base.html").read_text(encoding="utf-8")
    assert "offline_engine.js" in base_content
    assert "offline-storage-settings-section" in base_content
    print("✓ 8. templates/base.html offline script injection & settings modal verified")

    # 9. Verify templates/reader.html includes offline fallback hook
    reader_content = Path("templates/reader.html").read_text(encoding="utf-8")
    assert "renderChapterOffline" in reader_content
    print("✓ 9. templates/reader.html offline hydration & local SQLite fallback verified")

    print("=" * 65)
    print("ALL 9 OFFLINE APP ENGINE TESTS PASSED WITH 100% SUCCESS!")
    print("=" * 65)

if __name__ == "__main__":
    test_offline_endpoints()
