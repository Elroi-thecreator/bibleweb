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

def extract_video_id(url: str):
    if not url:
        return None
    url = url.strip()
    m1 = re.search(r'youtu\.be/([a-zA-Z0-9_-]{11})', url, re.IGNORECASE)
    if m1:
        return m1.group(1)
    m2 = re.search(r'[?&]v=([a-zA-Z0-9_-]{11})', url, re.IGNORECASE)
    if m2:
        return m2.group(1)
    m3 = re.search(r'embed/([a-zA-Z0-9_-]{11})', url, re.IGNORECASE)
    if m3:
        return m3.group(1)
    return None

def check_video_health(vid: str):
    """Returns (is_healthy, status_code, title)"""
    if not vid or len(vid) != 11:
        return False, 400, "Invalid ID format"
    url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={vid}&format=json"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        resp = urllib.request.urlopen(req, timeout=7)
        if resp.status == 200:
            data = json.loads(resp.read().decode('utf-8'))
            return True, 200, data.get("title", "")
    except urllib.error.HTTPError as e:
        return False, e.code, str(e.reason)
    except Exception as e:
        return False, 500, str(e)
    return False, 500, "Unknown"

def clean_song_title(title: str) -> str:
    if not title:
        return ""
    t = re.sub(r'\(\s*\d+\s*\)', '', title)
    t = re.sub(r'[\(\)\[\]\{\}]', ' ', t)
    return re.sub(r'\s+', ' ', t).strip()

def search_youtube_for_working_video(song: dict):
    title_ta = clean_song_title(song.get("title_ta") or "")
    title_en = clean_song_title(song.get("title_en") or "")
    book = song.get("songbook_code") or ""
    author = song.get("author") or ""
    vol = song.get("volume")
    if "ஆசிரியர் தெரியவில்லை" in author or "Author Unknown" in author:
        author = ""

    queries = []
    if book == "jebathota":
        vol_str = f" Vol {vol}" if vol and vol > 0 else ""
        if title_ta:
            queries.append(f"Jebathota Jeyageethangal{vol_str} {title_ta} {title_en} Fr SJ Berchmans")
            queries.append(f"{title_ta} Fr SJ Berchmans Jebathota")
        if title_en:
            queries.append(f"{title_en} Fr SJ Berchmans Jebathotta Jeyageethangal")
    elif book == "keerthanai":
        queries.append(f"Tamil Christian Keerthanai {title_ta} {title_en}")
    elif book == "seyalveerar":
        queries.append(f"Seyalveerar Tamil Christian Song {title_ta} {title_en}")
    elif book == "tac":
        queries.append(f"Tamil Apostolic Church {title_ta} {title_en}")
    else:
        queries.append(f"{title_ta} {title_en} Tamil Christian Song")

    # Add fallback query
    queries.append(f"{title_ta or title_en} Tamil Christian Song")

    for q in queries:
        try:
            encoded = urllib.parse.quote_plus(re.sub(r'\s+', ' ', q).strip())
            search_url = f"https://www.youtube.com/results?search_query={encoded}"
            req = urllib.request.Request(search_url, headers=HEADERS)
            html = urllib.request.urlopen(req, timeout=8).read().decode('utf-8', errors='ignore')
            vids = re.findall(r'"videoId":"([a-zA-Z0-9_-]{11})"', html)
            for cand_vid in vids:
                healthy, status, title = check_video_health(cand_vid)
                if healthy:
                    return cand_vid, title, q
        except Exception:
            continue
    return None, None, None

def process_audit_item(song: dict):
    url = song.get("youtube_url") or ""
    vid = extract_video_id(url)
    
    if not vid:
        return {
            "id": song["id"],
            "title_ta": song["title_ta"],
            "title_en": song["title_en"],
            "book": song["songbook_code"],
            "volume": song["volume"],
            "status": "SEARCH_STREAM",
            "old_url": url,
            "new_url": None,
            "fixed": False
        }

    healthy, code, title = check_video_health(vid)
    if healthy:
        return {
            "id": song["id"],
            "title_ta": song["title_ta"],
            "title_en": song["title_en"],
            "book": song["songbook_code"],
            "volume": song["volume"],
            "status": "HEALTHY",
            "old_url": url,
            "new_url": None,
            "fixed": False,
            "video_title": title
        }
    
    # Broken link! Find working replacement
    new_vid, new_title, q_used = search_youtube_for_working_video(song)
    if new_vid:
        return {
            "id": song["id"],
            "title_ta": song["title_ta"],
            "title_en": song["title_en"],
            "book": song["songbook_code"],
            "volume": song["volume"],
            "status": f"BROKEN_{code}",
            "old_url": url,
            "new_url": f"https://www.youtube.com/watch?v={new_vid}",
            "fixed": True,
            "video_title": new_title,
            "query": q_used
        }
    else:
        # Fallback to high precision search query
        clean_q = f"{song['title_ta']} {song['title_en']} Fr SJ Berchmans" if song["songbook_code"] == "jebathota" else f"{song['title_ta']} {song['title_en']} Tamil Christian Song"
        stream_url = f"https://www.youtube.com/results?search_query={urllib.parse.quote_plus(clean_q.strip())}"
        return {
            "id": song["id"],
            "title_ta": song["title_ta"],
            "title_en": song["title_en"],
            "book": song["songbook_code"],
            "volume": song["volume"],
            "status": f"BROKEN_{code}",
            "old_url": url,
            "new_url": stream_url,
            "fixed": False,
            "video_title": None
        }

def main():
    db_path = r"E:\anti-prjects\bibleweb\data\songs.sqlite.db"
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    rows = c.execute("SELECT id, songbook_code, volume, song_number, title_ta, title_en, author, youtube_url FROM songs ORDER BY id").fetchall()
    songs = [dict(r) for r in rows]
    total = len(songs)

    print(f"Starting complete health audit & repair for all {total} songs...")

    healthy_count = 0
    search_stream_count = 0
    broken_and_fixed = []
    broken_unfixed = []

    # Use 10 concurrent threads for fast audit and repair
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(process_audit_item, s): s for s in songs}
        completed = 0
        for f in as_completed(futures):
            res = f.result()
            completed += 1
            
            if res["status"] == "HEALTHY":
                healthy_count += 1
            elif res["status"] == "SEARCH_STREAM":
                search_stream_count += 1
            elif res["fixed"]:
                broken_and_fixed.append(res)
                # Update DB immediately
                c.execute("UPDATE songs SET youtube_url = ? WHERE id = ?", (res["new_url"], res["id"]))
            else:
                broken_unfixed.append(res)
                c.execute("UPDATE songs SET youtube_url = ? WHERE id = ?", (res["new_url"], res["id"]))

            if completed % 50 == 0 or completed == total:
                conn.commit()
                print(f"Audit Progress: {completed}/{total} | Healthy: {healthy_count} | Fixed: {len(broken_and_fixed)} | Broken Unfixed: {len(broken_unfixed)}")

    conn.commit()
    conn.close()

    print("\n" + "=" * 65)
    print("COMPLETE YOUTUBE AUDIT & REPAIR REPORT")
    print("=" * 65)
    print(f"Total songs audited: {total}")
    print(f"Already healthy (200 OK) videos: {healthy_count}")
    print(f"Search streams: {search_stream_count}")
    print(f"Broken links detected & REPAIRED to active videos: {len(broken_and_fixed)}")
    print(f"Broken links converted to official stream cards: {len(broken_unfixed)}")

    # Save detailed JSON report
    with open(r"E:\anti-prjects\bibleweb\scripts\audit_report.json", "w", encoding="utf-8") as out:
        json.dump({
            "repaired": broken_and_fixed,
            "unfixed": broken_unfixed
        }, out, indent=2, ensure_ascii=False)

    if broken_and_fixed:
        print("\n--- SAMPLE OF REPAIRED BROKEN LINKS (First 20) ---")
        for b in broken_and_fixed[:20]:
            print(f"ID {b['id']} (Vol {b['volume']}): {b['title_ta']} | Old: {b['old_url']} -> New: {b['new_url']}")

if __name__ == "__main__":
    main()
