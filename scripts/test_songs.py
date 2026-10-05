import os
import sys
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from app.main import app
from app.db import get_song_books, get_song_volumes, get_songs_list, get_song_by_id

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


async def call_asgi(path: str, query_string: bytes = b""):
    scope = {
        "type": "http",
        "method": "GET",
        "path": path,
        "headers": [],
        "query_string": query_string,
    }
    status = None
    headers = {}
    body_chunks = []

    async def receive():
        return {"type": "http.request"}

    async def send(msg):
        nonlocal status
        if msg["type"] == "http.response.start":
            status = msg["status"]
            for k, v in msg.get("headers", []):
                headers[k.decode("latin1").lower()] = v.decode("latin1")
        elif msg["type"] == "http.response.body":
            body_chunks.append(msg.get("body", b""))

    await app(scope, receive, send)
    body = b"".join(body_chunks).decode("utf-8", errors="ignore")
    return status, headers, body


async def run_tests():
    print("=== 1. Testing Database Song Queries ===")
    books = get_song_books()
    assert len(books) >= 5, f"Expected at least 5 songbooks, got {len(books)}"
    print(f"[PASS] Retrieved {len(books)} songbooks.")

    vols = get_song_volumes("jebathota")
    assert len(vols) == 40, f"Expected 40 Jebathota volumes, got {len(vols)}"
    print(f"[PASS] Retrieved all 40 Jebathota Jeyageethangal volumes.")

    vol1_songs = get_songs_list(songbook_code="jebathota", volume=1)
    assert vol1_songs["total_count"] > 0, "Expected songs in Volume 1"
    print(f"[PASS] Volume 1 has {vol1_songs['total_count']} songs.")

    song = get_song_by_id(vol1_songs["songs"][0]["id"])
    assert song is not None, "Song should be found by ID"
    assert song["title_ta"], "Song should have Tamil title"
    assert song["title_en"], "Song should have English title"
    assert len(song["stanzas"]) > 0, "Song should have parsed stanzas"
    print(f"[PASS] Song #{song['song_number']} ('{song['title_en']}') has {len(song['stanzas'])} stanzas.")

    print("\n=== 2. Testing /songs Route (Directory Page) ===")
    status, headers, body = await call_asgi("/songs")
    assert status == 200, f"Expected 200, got {status}"
    assert "text/html" in headers.get("content-type", "")
    assert "Jebathota Jeyageethangal" in body
    assert "Vol 40" in body
    print("[PASS] /songs rendered 200 HTML with all volume pills.")

    print("\n=== 3. Testing /songs with Volume Filter ===")
    status, headers, body = await call_asgi("/songs", b"book=jebathota&vol=14")
    assert status == 200
    assert "Volume 14" in body
    print("[PASS] /songs?book=jebathota&vol=14 rendered 200 HTML with Volume 14 songs.")

    print("\n=== 4. Testing /songs/{id} Reader Page ===")
    song_id = song["id"]
    status, headers, body = await call_asgi(f"/songs/{song_id}")
    assert status == 200
    assert "text/html" in headers.get("content-type", "")
    assert song["title_en"] in body
    assert "copySongLyrics" in body
    assert "setSongScriptMode" in body
    print(f"[PASS] /songs/{song_id} rendered 200 HTML reader view.")

    print("\n=== 5. Testing /api/songs Search API ===")
    status, headers, body = await call_asgi("/api/songs", b"q=love")
    assert status == 200
    assert "application/json" in headers.get("content-type", "")
    assert "total_count" in body
    print("[PASS] /api/songs?q=love returned valid JSON response.")

    print("\n=======================================================")
    print("ALL 5 SONG LYRICS TEST SUITES PASSED (100% OPERATIONAL)!")
    print("=======================================================")


if __name__ == "__main__":
    asyncio.run(run_tests())
