import sqlite3
import urllib.request
import urllib.parse
import re
import json
import time
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9,ta;q=0.8'
}

TAMIL_PATTERN = re.compile(r'[\u0B80-\u0BFF]')

def clean_song_title(title: str) -> str:
    if not title:
        return ""
    # Remove things like (3), (2), (Medley 1), etc.
    t = re.sub(r'\(\s*\d+\s*\)', '', title)
    t = re.sub(r'[\(\)\[\]\{\}]', ' ', t)
    t = re.sub(r'\s+', ' ', t).strip()
    return t

def build_query(song: dict) -> str:
    title_ta = clean_song_title(song.get("title_ta") or "")
    title_en = clean_song_title(song.get("title_en") or "")
    author = song.get("author") or ""
    if "ஆசிரியர் தெரியவில்லை" in author or "Author Unknown" in author:
        author = ""

    has_tamil = bool(TAMIL_PATTERN.search(title_ta)) or bool(TAMIL_PATTERN.search(song.get("lyrics_ta") or ""))

    if has_tamil:
        # Tamil song query
        if author:
            query = f"{title_ta} {title_en} {author} Tamil Christian Song"
        else:
            query = f"Tamil Christian Song {title_ta} {title_en} Fr SJ Berchmans Jebathota"
    else:
        # English song query
        if author:
            query = f"{title_en} {author} worship song"
        else:
            query = f"{title_en} Christian worship song"

    return re.sub(r'\s+', ' ', query).strip()

def search_youtube_videos(query: str):
    encoded = urllib.parse.quote_plus(query)
    url = f"https://www.youtube.com/results?search_query={encoded}"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        html = urllib.request.urlopen(req, timeout=12).read().decode('utf-8', errors='ignore')
        vids = re.findall(r'"videoId":"([a-zA-Z0-9_-]{11})"', html)
        unique = []
        for v in vids:
            if v not in unique:
                unique.append(v)
        return unique[:5]
    except Exception as e:
        return []

def verify_video_id(vid: str):
    try:
        url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={vid}&format=json"
        req = urllib.request.Request(url, headers=HEADERS)
        resp = urllib.request.urlopen(req, timeout=8)
        if resp.status == 200:
            data = json.loads(resp.read().decode('utf-8'))
            return True, data.get("title", "")
    except Exception:
        pass
    return False, ""

def process_song(song):
    query = build_query(song)
    vids = search_youtube_videos(query)
    
    # Try candidate video IDs
    for vid in vids:
        valid, title = verify_video_id(vid)
        if valid:
            return {
                "id": song["id"],
                "success": True,
                "vid": vid,
                "video_title": title,
                "query": query,
                "title_ta": song["title_ta"],
                "title_en": song["title_en"]
            }
            
    # Fallback: simpler search without extra tags
    simple_title = clean_song_title(song.get("title_en") or song.get("title_ta"))
    fallback_query = f"{simple_title} Christian Song"
    vids2 = search_youtube_videos(fallback_query)
    for vid in vids2:
        valid, title = verify_video_id(vid)
        if valid:
            return {
                "id": song["id"],
                "success": True,
                "vid": vid,
                "video_title": title,
                "query": fallback_query,
                "title_ta": song["title_ta"],
                "title_en": song["title_en"]
            }

    return {
        "id": song["id"],
        "success": False,
        "vid": None,
        "video_title": None,
        "query": query,
        "title_ta": song["title_ta"],
        "title_en": song["title_en"]
    }

def main():
    db_path = r"E:\anti-prjects\bibleweb\data\songs.sqlite.db"
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    rows = c.execute("""
        SELECT id, songbook_code, volume, song_number, title_ta, title_en, author, lyrics_ta, youtube_url 
        FROM songs 
        WHERE songbook_code = 'jebathota' AND youtube_url NOT LIKE '%watch?v=%'
        ORDER BY id
    """).fetchall()

    songs = [dict(r) for r in rows]
    total = len(songs)
    print(f"Starting YouTube video resolution for {total} Jebathota songs...")

    found = []
    not_found = []

    # Use 4 threads for concurrency while respecting YouTube rate limits
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(process_song, s): s for s in songs}
        completed = 0
        for f in as_completed(futures):
            res = f.result()
            completed += 1
            if res["success"]:
                found.append(res)
                # Update in DB
                c.execute("UPDATE songs SET youtube_url = ? WHERE id = ?", 
                          (f"https://www.youtube.com/watch?v={res['vid']}", res["id"]))
            else:
                not_found.append(res)

            if completed % 20 == 0 or completed == total:
                conn.commit()
                print(f"Progress: {completed}/{total} | Found: {len(found)} | Not Found: {len(not_found)}")

    conn.commit()
    conn.close()

    print("\n" + "=" * 60)
    print("FINAL RESOLUTION REPORT")
    print("=" * 60)
    print(f"Total songs processed: {total}")
    print(f"Successfully linked with direct YouTube videos: {len(found)} ({len(found)/total*100:.1f}%)")
    print(f"Songs not found: {len(not_found)} ({len(not_found)/total*100:.1f}%)")

    # Save detailed report to file
    with open(r"E:\anti-prjects\bibleweb\scripts\yt_resolution_results.json", "w", encoding="utf-8") as out:
        json.dump({"found": found, "not_found": not_found}, out, indent=2, ensure_ascii=False)

    if not_found:
        print("\n--- SONGS NOT ABLE TO BE FOUND ---")
        for nf in not_found:
            print(f"ID {nf['id']:<5} | {nf['title_ta'][:30]:<30} | {nf['title_en'][:30]}")

if __name__ == "__main__":
    main()
