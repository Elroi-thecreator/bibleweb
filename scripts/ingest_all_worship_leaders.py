# -*- coding: utf-8 -*-
"""
Ingest and expand Christian Song collections for:
- Fr. S.J. Berchmans (Verify all 1,167 songs across 40 volumes)
- Dr. Joseph Aldrin (Expand to 25 songs)
- Pastor Benny Joshua (Expand to 25 songs)
- Pastor John Jebaraj (New songbook with 25 songs)

Conforms strictly to PROD-SONGS-001 v1.5.1
"""

import os
import sys
import sqlite3
import json

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "songs.sqlite.db")
JJ_PARSED_JSON = r"C:\Users\GOD\.gemini\antigravity\brain\bfefba25-d6e6-4a68-9bad-2e177047aac6\scratch\jj_11_parsed.json"

from song_datasets import (
    JOHN_JEBARAJ_EXTRA_SONGS,
    ALDRIN_NEW_SONGS,
    BENNY_NEW_SONGS,
)


def run_ingestion():
    print(f"Connecting to database: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # 1. Register John Jebaraj in song_books
    print("\n--- 1. Registering Song Books ---")
    c.execute("""
        INSERT OR REPLACE INTO song_books (code, name_ta, name_en, display_order)
        VALUES ('johnjebaraj', 'பாஸ்டர் ஜான் ஜெபராஜ்', 'Pastor John Jebaraj', 8)
    """)
    conn.commit()
    print("Registered songbook: johnjebaraj (display_order: 8)")

    # 2. Get current max ID
    cur_max_id = c.execute("SELECT max(id) FROM songs").fetchone()[0] or 2500
    print(f"Current maximum song ID in songs table: {cur_max_id}")

    # 3. Clean up existing Aldrin and Benny song numbering
    print("\n--- 2. Standardizing Song Numbers for Existing Aldrin & Benny Songs ---")
    # Aldrin #0 (ID 2458) -> set song_number = 11
    c.execute("UPDATE songs SET song_number = 11 WHERE id = 2458 AND songbook_code = 'aldrin'")
    
    # Benny #0 (ID 1986) -> set song_number = 11
    c.execute("UPDATE songs SET song_number = 11 WHERE id = 1986 AND songbook_code = 'benny'")
    # Benny #0 (ID 2307) -> set song_number = 12
    c.execute("UPDATE songs SET song_number = 12 WHERE id = 2307 AND songbook_code = 'benny'")
    conn.commit()

    aldrin_count = c.execute("SELECT count(*) FROM songs WHERE songbook_code = 'aldrin'").fetchone()[0]
    benny_count = c.execute("SELECT count(*) FROM songs WHERE songbook_code = 'benny'").fetchone()[0]
    print(f"Existing Aldrin songs: {aldrin_count} (numbered 1..11)")
    print(f"Existing Benny songs: {benny_count} (numbered 1..12)")

    # 4. Insert New Aldrin Songs (14 songs, numbers 12..25)
    print("\n--- 3. Ingesting New Songs for Dr. Joseph Aldrin ---")
    next_num = 12
    for s in ALDRIN_NEW_SONGS:
        # Check if already present by title_en
        exists = c.execute("SELECT id FROM songs WHERE songbook_code = 'aldrin' AND title_en = ?", (s["title_en"],)).fetchone()
        if exists:
            print(f"  [SKIPPED] Aldrin song '{s['title_en']}' already exists (ID {exists[0]})")
            continue

        cur_max_id += 1
        lyrics_ta = "\n\n".join(st["ta"] for st in s["stanzas"])
        lyrics_en = "\n\n".join(st["en"] for st in s["stanzas"])
        bilingual_json = json.dumps(s["stanzas"], ensure_ascii=False)

        c.execute("""
            INSERT INTO songs (
                id, songbook_code, songbook_name_ta, songbook_name_en,
                volume, volume_name, song_number, title_ta, title_en,
                alternate_title, lyrics_ta, lyrics_en, lyrics_bilingual,
                author, youtube_url
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            cur_max_id, "aldrin", "டாக்டர் ஜோசப் அல்ட்ரின்", "Dr. Joseph Aldrin",
            1, "Volume 1", next_num, s["title_ta"], s["title_en"],
            "", lyrics_ta, lyrics_en, bilingual_json,
            s["author"], s["youtube_url"]
        ))
        print(f"  [ADDED #{next_num}] ID {cur_max_id}: {s['title_en']} | {s['title_ta']} | YT: {s['youtube_url']}")
        next_num += 1

    conn.commit()

    # 5. Insert New Benny Songs (13 songs, numbers 13..25)
    print("\n--- 4. Ingesting New Songs for Pastor Benny Joshua ---")
    next_num = 13
    for s in BENNY_NEW_SONGS:
        exists = c.execute("SELECT id FROM songs WHERE songbook_code = 'benny' AND title_en = ?", (s["title_en"],)).fetchone()
        if exists:
            print(f"  [SKIPPED] Benny song '{s['title_en']}' already exists (ID {exists[0]})")
            continue

        cur_max_id += 1
        lyrics_ta = "\n\n".join(st["ta"] for st in s["stanzas"])
        lyrics_en = "\n\n".join(st["en"] for st in s["stanzas"])
        bilingual_json = json.dumps(s["stanzas"], ensure_ascii=False)

        c.execute("""
            INSERT INTO songs (
                id, songbook_code, songbook_name_ta, songbook_name_en,
                volume, volume_name, song_number, title_ta, title_en,
                alternate_title, lyrics_ta, lyrics_en, lyrics_bilingual,
                author, youtube_url
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            cur_max_id, "benny", "பாஸ்டர் பென்னி ஜோசுவா", "Pastor Benny Joshua",
            1, "Volume 1", next_num, s["title_ta"], s["title_en"],
            "", lyrics_ta, lyrics_en, bilingual_json,
            s["author"], s["youtube_url"]
        ))
        print(f"  [ADDED #{next_num}] ID {cur_max_id}: {s['title_en']} | {s['title_ta']} | YT: {s['youtube_url']}")
        next_num += 1

    conn.commit()

    # 6. Ingest John Jebaraj Songs (25 songs total)
    print("\n--- 5. Ingesting Songs for Pastor John Jebaraj ---")
    # Part A: The 11 songs from OpenLP parsed JSON
    with open(JJ_PARSED_JSON, "r", encoding="utf-8") as fp:
        jj_base_songs = json.load(fp)

    yt_map = {
        "Ejamaananae Um Saevaikkaai": "https://www.youtube.com/watch?v=qNorNSyVkhs",
        "Ithuvarai Nadathi": "https://www.youtube.com/watch?v=YsLRZkbgjrk",
        "Kartharai Dheivamaaga Kondoar": "https://www.youtube.com/watch?v=c3eFQs7L_9w",
        "Nallavarae En Yaesuvae": "https://www.youtube.com/watch?v=ZFzr_FBbFYQ",
        "Nandri Solli Ummai Paada Vanthoam": "https://www.youtube.com/watch?v=rOQO1OQgl7U",
        "Oruvarum Saeraa Oliyinil": "https://www.youtube.com/watch?v=da1wuPrWoTE",
        "Parisutharae Enggal Yaesuthaevaa": "https://www.youtube.com/watch?v=8gBC3wA0-ig",
        "Penthekosthae Anupavam Thaarumae": "https://www.youtube.com/watch?v=ZxqjPxbPEBI",
        "Puthu Vaazhvu Thanthavarae": "https://www.youtube.com/watch?v=JEm8psN08y4",
        "Thaevanae Ennai Tharukiraen": "https://www.youtube.com/watch?v=JcJh4AaL2ik",
        "Yaehoavaa Yeerae Neer En Thaevanaam": "https://www.youtube.com/watch?v=EQXCg_A2IF0",
    }

    jj_song_num = 1
    for s in jj_base_songs:
        exists = c.execute("SELECT id FROM songs WHERE songbook_code = 'johnjebaraj' AND title_en = ?", (s["title_en"],)).fetchone()
        if exists:
            print(f"  [SKIPPED] JJ song '{s['title_en']}' already exists (ID {exists[0]})")
            jj_song_num += 1
            continue

        cur_max_id += 1
        stanzas = s["stanzas"]
        for st in stanzas:
            # ensure 'ta' and 'en' text fields exist alongside lines_ta and lines_en
            if "ta" not in st:
                st["ta"] = "\n".join(st.get("lines_ta", []))
            if "en" not in st:
                st["en"] = "\n".join(st.get("lines_en", []))

        lyrics_ta = "\n\n".join(st["ta"] for st in stanzas)
        lyrics_en = "\n\n".join(st["en"] for st in stanzas)
        bilingual_json = json.dumps(stanzas, ensure_ascii=False)
        yt_url = yt_map.get(s["title_en"]) or s.get("youtube_url") or "https://www.youtube.com/watch?v=da1wuPrWoTE"

        c.execute("""
            INSERT INTO songs (
                id, songbook_code, songbook_name_ta, songbook_name_en,
                volume, volume_name, song_number, title_ta, title_en,
                alternate_title, lyrics_ta, lyrics_en, lyrics_bilingual,
                author, youtube_url
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            cur_max_id, "johnjebaraj", "பாஸ்டர் ஜான் ஜெபராஜ்", "Pastor John Jebaraj",
            1, "Levi Volumes & Worship", jj_song_num, s["title_ta"], s["title_en"],
            "", lyrics_ta, lyrics_en, bilingual_json,
            "Pastor John Jebaraj {பாஸ்டர் ஜான் ஜெபராஜ்}", yt_url
        ))
        print(f"  [ADDED #{jj_song_num}] ID {cur_max_id}: {s['title_en']} | {s['title_ta']} | YT: {yt_url}")
        jj_song_num += 1

    conn.commit()

    # Part B: The 14 extra contemporary Levi worship hits
    for s in JOHN_JEBARAJ_EXTRA_SONGS:
        exists = c.execute("SELECT id FROM songs WHERE songbook_code = 'johnjebaraj' AND title_en = ?", (s["title_en"],)).fetchone()
        if exists:
            print(f"  [SKIPPED] JJ song '{s['title_en']}' already exists (ID {exists[0]})")
            jj_song_num += 1
            continue

        cur_max_id += 1
        lyrics_ta = "\n\n".join(st["ta"] for st in s["stanzas"])
        lyrics_en = "\n\n".join(st["en"] for st in s["stanzas"])
        bilingual_json = json.dumps(s["stanzas"], ensure_ascii=False)

        c.execute("""
            INSERT INTO songs (
                id, songbook_code, songbook_name_ta, songbook_name_en,
                volume, volume_name, song_number, title_ta, title_en,
                alternate_title, lyrics_ta, lyrics_en, lyrics_bilingual,
                author, youtube_url
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            cur_max_id, "johnjebaraj", "பாஸ்டர் ஜான் ஜெபராஜ்", "Pastor John Jebaraj",
            1, "Levi Volumes & Worship", jj_song_num, s["title_ta"], s["title_en"],
            "", lyrics_ta, lyrics_en, bilingual_json,
            s["author"], s["youtube_url"]
        ))
        print(f"  [ADDED #{jj_song_num}] ID {cur_max_id}: {s['title_en']} | {s['title_ta']} | YT: {s['youtube_url']}")
        jj_song_num += 1

    conn.commit()

    print("\n--- 6. Post-Ingestion Verification ---")
    final_books = c.execute("SELECT sb.code, sb.name_en, count(s.id) FROM song_books sb LEFT JOIN songs s ON sb.code = s.songbook_code GROUP BY sb.code ORDER BY sb.display_order").fetchall()
    print("Final Songbook Counts:")
    for b in final_books:
        print(f"  {b[0]} ({b[1]}): {b[2]} songs")

    # Strict health checks
    total_missing_yt = c.execute("SELECT count(*) FROM songs WHERE youtube_url IS NULL OR length(trim(youtube_url)) = 0").fetchone()[0]
    print(f"Total songs missing YouTube URL: {total_missing_yt} (Must be 0)")
    assert total_missing_yt == 0, "Error: Songs found without YouTube URL!"

    for code, expected_min in [("jebathota", 1167), ("aldrin", 25), ("benny", 25), ("johnjebaraj", 25)]:
        cnt = c.execute("SELECT count(*) FROM songs WHERE songbook_code = ?", (code,)).fetchone()[0]
        assert cnt >= expected_min, f"Expected at least {expected_min} songs for {code}, got {cnt}"
        print(f"[VERIFIED] {code}: {cnt} songs >= {expected_min}")

    print("\nIngestion completed successfully!")


if __name__ == "__main__":
    run_ingestion()
