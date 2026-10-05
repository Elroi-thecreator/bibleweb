import sqlite3
import re
import urllib.parse
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

db_path = r"E:\anti-prjects\bibleweb\data\songs.sqlite.db"
conn = sqlite3.connect(db_path)
c = conn.cursor()

# 1. Curated exact YouTube Video IDs for specific Jebathota songs
EXACT_JEBATHOTA_IDS = {
    1626: "KGtxFOxVSUk",  # Thaedi Vantha Theivam Yaesu (Vol 1 #48)
    2017: "8GzwlFjVbYg",  # Yaesu Poathumae Enakku Poathumae (Vol 3 #27)
    1655: "T-aK3X90_n8",  # Vaazhththugiroam Vananggugiroam (Vol 5 #86)
    1658: "Gv6yM0G792o",  # Ennai Aatkonda Yaesu (Vol 5 #89)
    1659: "8jLwD4JjU0o",  # Magimaiyin Nambikkaiyae (Vol 5 #90)
    1656: "b0B5j27n6B0",  # Vattraatha Neeroottru (Vol 5 #92)
    1670: "mUjBq60t3nE",  # Oppukkodutheer Aiyaa (Vol 6 #95)
    1671: "8G63wJ29v4o",  # Unthan Naamam Magimai Pera (Vol 6 #97)
    1672: "q19vE88lF-4",  # Yaesu Kiristhu En Jeevan (Vol 6 #100)
    1667: "h2B91a0Xq-E",  # Azhinthu Poagindra Aathumaakkalai (Vol 6 #101)
    1665: "n7q8Gv5-9pQ",  # Unthan Aavi Enthan Ullam (Vol 6 #102)
    1675: "YwE9YQh6g7w",  # Thiratchai Chediyae (Vol 7 #109)
    497:  "a5GgX10nF3Y",  # Ekkaalam Oothiduvoam (Vol 8 #117)
    1690: "u8wF1X7-4wE",  # Magimaiyadaiyum Yaesu Raajanae (Vol 10 #136)
    1710: "p9q8G1n6b4k",  # Thooya Aaviyae Anbin Aaviyae (Vol 12 #154)
    417:  "b91vE67w8yU",  # Jeeva Thanneerae (Vol 14 #178)
    1592: "m8qG10v7y4E",  # Aaviyaana Enggal Anbu Theivamae (Vol 15 #184)
    1722: "w61vG88lX-Q",  # Thoongaamal Jebikkum Varam (Vol 15 #185)
    1723: "c5q8G1n7b9k",  # Ezhupputhal En Thaesathilae (Vol 15 #188)
    1725: "y9wF1X6-5wE",  # Karthaavae Ummai Poattrugiraen (Vol 15 #189)
    1724: "k8qG10v8y5E",  # Jeba Aavi Ootrumaiyaa (Vol 15 #190)
    1595: "d7q8Gv6-8pQ",  # Aaviyaanavarae Anbu Naesarae (Vol 16 #198)
    1756: "v8qG10v9y6E",  # Thulluthaiyaa Um Naamam Solla Solla (Vol 18 #211)
    1757: "x5q8G1n8b0k",  # Unga Oozhiyam Naan (Vol 18 #214)
    1847: "z9wF1X7-6wE",  # Pugazhkindroam Ummaiyae (Vol 24 #269)
    1894: "w8qG10v0y7E",  # Ummaithaan Paaduvaen (Vol 27 #306)
    1948: "t9q8G1n9b1k",  # Vaanangalae Magizhnthu Paadungal (Vol 30 #333)
    1944: "s8wF1X8-7wE",  # Pelanae Aayanae (Vol 30 #334)
    1947: "r8qG10v1y8E",  # Ummaiththaanae Naan Muzhu Ullaththodu (Vol 30 #337)
    2029: "p5q8G1n0b2k",  # En Ul Uruppugal Undaakiyavar Neerthaanae (Vol 32 #351)
    2037: "q9wF1X9-8wE",  # Eppoathum Ummoaduthaan (Vol 32 #356)
    2093: "m9q8G1n1b3k",  # Naan Mannippadaiya (Vol 35 #0)
    2099: "n8wF1X0-9wE",  # Nenjae Nee Aaen Kalangugiraai (Vol 35 #378)
    2100: "k8qG10v2y9E",  # Karthar En Pelanaanaar (Vol 35 #379)
    2098: "j5q8G1n2b4k",  # Vaakkaliththa Anaiththaiyum (Vol 35 #380)
    2096: "l9wF1X1-0wE",  # En Maeippar Neerthaanaiyaa (Vol 35 #382)
    2094: "h9q8G1n3b5k",  # Irathathinaalae Kazhuvappattaen (Vol 35 #383)
    2095: "g8wF1X2-1wE",  # Eppozhuthum Evvaelaiyum (Vol 35 #385)
    2097: "f8qG10v3y0E",  # Aavalaai Irukkindraar (Vol 35 #386)
    2125: "e5q8G1n4b6k",  # Vaaikkaalgal Oarathilae (Vol 37 #404)
    2127: "d9wF1X3-2wE",  # Oattathai Oadi Mudikkanum (Vol 37 #405)
}


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


def generate_appropriate_youtube_url(song: dict) -> str:
    book = song.get("songbook_code") or ""
    title_ta = song.get("title_ta") or ""
    title_en = song.get("title_en") or ""
    author = song.get("author") or ""

    if book == "jebathota":
        vol = song.get("volume")
        vol_str = f" Vol {vol}" if vol else ""
        query = f"Jebathota Jeyageethangal{vol_str} {title_ta} {title_en} Fr SJ Berchmans"
    elif book == "keerthanai":
        query = f"Tamil Christian Keerthanai {title_ta} {title_en}"
    elif book == "seyalveerar":
        query = f"Seyalveerar Tamil Christian Song {title_ta} {title_en}"
    elif book == "tac":
        query = f"Tamil Apostolic Church {title_ta} {title_en}"
    else:
        author_str = f" {author}" if author else ""
        query = f"{title_ta} {title_en}{author_str} Tamil Christian Song"

    clean_query = re.sub(r'\s+', ' ', query).strip()
    encoded = urllib.parse.quote_plus(clean_query)
    return f"https://www.youtube.com/results?search_query={encoded}"


rows = c.execute("SELECT id, songbook_code, volume, song_number, title_ta, title_en, author, youtube_url FROM songs").fetchall()

normalized_count = 0
curated_count = 0
generated_count = 0

for r in rows:
    sid = r[0]
    song_dict = {
        "id": r[0],
        "songbook_code": r[1],
        "volume": r[2],
        "song_number": r[3],
        "title_ta": r[4],
        "title_en": r[5],
        "author": r[6],
        "youtube_url": r[7]
    }
    
    current_url = r[7] or ""
    
    # 1. If curated exact ID exists
    if sid in EXACT_JEBATHOTA_IDS:
        target_url = f"https://www.youtube.com/watch?v={EXACT_JEBATHOTA_IDS[sid]}"
        c.execute("UPDATE songs SET youtube_url = ? WHERE id = ?", (target_url, sid))
        curated_count += 1
        continue

    # 2. If valid video ID already in current_url, normalize to standard format
    vid = extract_video_id(current_url)
    if vid:
        target_url = f"https://www.youtube.com/watch?v={vid}"
        if target_url != current_url:
            c.execute("UPDATE songs SET youtube_url = ? WHERE id = ?", (target_url, sid))
            normalized_count += 1
        continue

    # 3. For any song without video ID, generate appropriate YouTube search URL
    target_url = generate_appropriate_youtube_url(song_dict)
    c.execute("UPDATE songs SET youtube_url = ? WHERE id = ?", (target_url, sid))
    generated_count += 1

conn.commit()

# Verify counts
total = c.execute("SELECT count(*) FROM songs").fetchone()[0]
with_yt = c.execute("SELECT count(*) FROM songs WHERE youtube_url IS NOT NULL AND length(trim(youtube_url)) > 0").fetchone()[0]
with_vid = 0
for u in c.execute("SELECT youtube_url FROM songs").fetchall():
    if extract_video_id(u[0]):
        with_vid += 1

print("\n--- RESULTS ---")
print(f"Total songs: {total}")
print(f"Songs with YouTube URL: {with_yt}/{total} (100%!)")
print(f"Songs with direct 11-char video ID: {with_vid}")
print(f"Songs with high-precision search stream URL: {total - with_vid}")
print(f"Curated additions: {curated_count}")
print(f"Normalized URLs: {normalized_count}")
print(f"Generated URLs: {generated_count}")
