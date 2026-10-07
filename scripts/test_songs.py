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
    assert song.get("youtube_url"), "Song must have an appropriate YouTube URL"
    assert song.get("youtube_video_id") is not None, "Song #1 should have direct YouTube video ID"
    print(f"[PASS] Song #{song['song_number']} ('{song['title_en']}') has {len(song['stanzas'])} stanzas and YouTube video: {song['youtube_url']}")

    # Verify that 100% of songs have an appropriate YouTube link in the database
    from app.db import get_songs_connection
    with get_songs_connection() as conn:
        missing_yt = conn.execute("SELECT count(*) FROM songs WHERE youtube_url IS NULL OR length(trim(youtube_url)) = 0").fetchone()[0]
        total_songs = conn.execute("SELECT count(*) FROM songs").fetchone()[0]
        assert missing_yt == 0, f"Found {missing_yt} songs without YouTube link! All songs must be linked."
        print(f"[PASS] 100% of songs ({total_songs}/{total_songs}) have appropriate YouTube video/streaming links.")

    print("\n=== 2. Testing /songs Route (Directory Page) ===")
    status, headers, body = await call_asgi("/songs")
    assert status == 200, f"Expected 200, got {status}"
    assert "text/html" in headers.get("content-type", "")
    assert "Jebathota Jeyageethangal" in body
    assert "Vol 40" in body
    assert "song-search-suggestions" in body, "Should have live search suggestions container"
    assert "scope_option" in body, "Should have search scope options"
    print("[PASS] /songs rendered 200 HTML with all volume pills, search scopes, and live autocomplete container.")

    print("\n=== 3. Testing /songs with Volume Filter ===")
    status, headers, body = await call_asgi("/songs", b"book=jebathota&vol=14")
    assert status == 200
    assert "Volume 14" in body
    print("[PASS] /songs?book=jebathota&vol=14 rendered 200 HTML with Volume 14 songs.")

    print("\n=== 3b. Testing Contemporary Worship Books (Aldrin, Benny, John Jebaraj) ===")
    status, headers, body = await call_asgi("/songs", b"book=aldrin")
    assert status == 200
    assert "Dr. Joseph Aldrin" in body or "ஜோசப் அல்ட்ரின்" in body
    aldrin_res = get_songs_list(songbook_code="aldrin")
    assert aldrin_res["total_count"] >= 25, f"Expected >= 25 songs for aldrin, got {aldrin_res['total_count']}"
    print(f"[PASS] /songs?book=aldrin rendered 200 HTML with {aldrin_res['total_count']} songs.")

    status, headers, body = await call_asgi("/songs", b"book=benny")
    assert status == 200
    assert "Pastor Benny Joshua" in body or "பென்னி ஜோசுவா" in body
    benny_res = get_songs_list(songbook_code="benny")
    assert benny_res["total_count"] >= 25, f"Expected >= 25 songs for benny, got {benny_res['total_count']}"
    print(f"[PASS] /songs?book=benny rendered 200 HTML with {benny_res['total_count']} songs.")

    status, headers, body = await call_asgi("/songs", b"book=johnjebaraj")
    assert status == 200
    assert "Pastor John Jebaraj" in body or "ஜான் ஜெபராஜ்" in body
    jj_res = get_songs_list(songbook_code="johnjebaraj")
    assert jj_res["total_count"] >= 25, f"Expected >= 25 songs for johnjebaraj, got {jj_res['total_count']}"
    print(f"[PASS] /songs?book=johnjebaraj rendered 200 HTML with {jj_res['total_count']} songs.")

    print("\n=== 4. Testing /songs/{id} Reader Page ===")
    song_id = song["id"]
    status, headers, body = await call_asgi(f"/songs/{song_id}")
    assert status == 200
    assert "text/html" in headers.get("content-type", "")
    assert song["title_en"] in body
    assert "copySongLyrics" in body
    assert "setSongScriptMode" in body
    assert "detail-search-input" in body, "Should have dedicated in-page song search bar"
    assert "detail_search_scope" in body, "Should have in-page search scope selector"
    assert "quick-song-jump" in body, "Should have in-volume quick song picker"
    assert "stanza-block" in body, "Should have liturgical hymnal stanzas"
    print(f"[PASS] /songs/{song_id} rendered 200 HTML with dedicated search, in-volume jump, and liturgical hymnal UI.")

    # Test Aldrin, Benny & John Jebaraj song reader page renders lines
    for aid in [2458, 2560, 2580]:
        status, headers, body = await call_asgi(f"/songs/{aid}")
        assert status == 200
        assert "lyrics-line-ta" in body, f"Aldrin song {aid} must have rendered Tamil lyric lines"
        assert "lyrics-line-en" in body, f"Aldrin song {aid} must have rendered English lyric lines"
    print("[PASS] Dr. Joseph Aldrin song pages (including #2560 Pradhana Aasariyarae, #2580 En Hakkore) rendered full bilingual lyrics lines successfully.")

    for bid in [1986, 2570, 2594]:
        status, headers, body = await call_asgi(f"/songs/{bid}")
        assert status == 200
        assert "lyrics-line-ta" in body, f"Benny song {bid} must have rendered Tamil lyric lines"
        assert "lyrics-line-en" in body, f"Benny song {bid} must have rendered English lyric lines"
    print("[PASS] Pastor Benny Joshua song pages (including #2570 Appa Pithavae, #2594 Seerpaduthuvaar) rendered full bilingual lyrics lines successfully.")

    for jid in [2607, 2618]:
        status, headers, body = await call_asgi(f"/songs/{jid}")
        assert status == 200
        assert "lyrics-line-ta" in body, f"John Jebaraj song {jid} must have rendered Tamil lyric lines"
        assert "lyrics-line-en" in body, f"John Jebaraj song {jid} must have rendered English lyric lines"
    print("[PASS] Pastor John Jebaraj song pages (including #2607 Ejamaananae, #2618 Isravelin Thuthigalil) rendered full bilingual lyrics lines successfully.")

    print("\n=== 5. Testing /api/songs Search API ===")
    status, headers, body = await call_asgi("/api/songs", b"q=love&book=all")
    assert status == 200
    assert "application/json" in headers.get("content-type", "")
    assert "total_count" in body
    
    status, headers, body = await call_asgi("/api/songs", b"q=1&vol=1")
    assert status == 200
    assert "songs" in body
    print("[PASS] /api/songs returned valid JSON responses across global and volume-filtered queries.")

    print("\n=======================================================")
    print("ALL 5 SONG LYRICS TEST SUITES PASSED (100% OPERATIONAL)!")
    print("=======================================================")


if __name__ == "__main__":
    asyncio.run(run_tests())
