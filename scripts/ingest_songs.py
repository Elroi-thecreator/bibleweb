#!/usr/bin/env python3
"""
Ingestion script for Tamil Christian Song Lyrics & Jebathota Jeyageethangal (All Volumes)
========================================================================================
Extracts 1,510 songs (headlined by 439 Jebathota Jeyageethangal songs across Volumes 1–40,
plus traditional Tamil hymns and Christian praise collections) into data/bible.sqlite.db.
"""

import os
import sys
import sqlite3
import xml.etree.ElementTree as ET
import re
import json

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGET_DB = os.path.join(BASE_DIR, "data", "songs.sqlite.db")
SOURCE_DB = r"C:\Users\GOD\.gemini\antigravity\brain\bfefba25-d6e6-4a68-9bad-2e177047aac6\scratch\temp_songs.sqlite"


def parse_song_lyrics(xml_str):
    """
    Parses OpenLP song XML containing {y}Tamil{/y} and Romanised English lines.
    Returns: (lyrics_ta, lyrics_en, lyrics_bilingual_json)
    """
    stanzas = []
    pure_ta = []
    pure_en = []

    if not xml_str or not xml_str.strip():
        return "", "", "[]"

    try:
        root = ET.fromstring(xml_str)
        for verse in root.findall(".//verse"):
            vtype = verse.get("type", "v")
            vlabel = verse.get("label", "")
            text = verse.text or ""

            type_names = {
                "c": "பல்லவி / Chorus",
                "v": f"சரணம் {vlabel} / Verse {vlabel}" if vlabel else "சரணம் / Verse",
                "p": "முன்னுரை / Pre-Chorus",
                "b": "இடைப்பகுதி / Bridge",
                "e": "முடிவுரை / Outro",
                "o": "பகுதி / Other",
            }
            stanza_title = type_names.get(vtype, "சரணம் / Verse")

            lines = text.strip().split("\n")
            st_ta = []
            st_en = []
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                ta_matches = re.findall(r"\{y\}(.*?)\{/y\}", line)
                if ta_matches:
                    clean_ta = " ".join(ta_matches).strip()
                    # Strip leading numbering like '1.   ' from lyrics text
                    clean_ta = re.sub(r"^\d+\.\s*", "", clean_ta)
                    st_ta.append(clean_ta)
                    pure_ta.append(clean_ta)
                else:
                    # Strip font or formatting tags if any
                    clean_en = re.sub(r"\{.*?\}", "", line).strip()
                    clean_en = re.sub(r"^\d+\.\s*", "", clean_en)
                    st_en.append(clean_en)
                    pure_en.append(clean_en)

            if st_ta or st_en:
                stanzas.append({
                    "type": vtype,
                    "label": stanza_title,
                    "lines_ta": st_ta,
                    "lines_en": st_en,
                })
    except Exception as e:
        # Fallback for plain text
        pure_lines = [l.strip() for l in xml_str.split("\n") if l.strip()]
        return "\n".join(pure_lines), "", "[]"

    return "\n".join(pure_ta), "\n".join(pure_en), json.dumps(stanzas, ensure_ascii=False)


def parse_comments(comment_str):
    """Parses i18nTitle, album, mediaUrl from comments key-value pairs."""
    meta = {"title_ta": "", "album": "", "youtube_url": ""}
    if not comment_str:
        return meta

    for line in comment_str.strip().split("\n"):
        if "=" in line:
            k, v = line.split("=", 1)
            k = k.strip()
            v = v.strip()
            if k == "i18nTitle":
                meta["title_ta"] = v
            elif k == "album":
                meta["album"] = v
            elif k == "mediaUrl":
                meta["youtube_url"] = v
    return meta


def ingest():
    if not os.path.exists(SOURCE_DB):
        raise FileNotFoundError(f"Source database not found at {SOURCE_DB}")
    os.makedirs(os.path.dirname(TARGET_DB), exist_ok=True)

    src_conn = sqlite3.connect(SOURCE_DB)
    src_conn.row_factory = sqlite3.Row
    src_cur = src_conn.cursor()

    tgt_conn = sqlite3.connect(TARGET_DB)
    tgt_cur = tgt_conn.cursor()

    print(f"Connecting to target database: {TARGET_DB}")

    # 1. Create Song Tables
    tgt_cur.executescript("""
        CREATE TABLE IF NOT EXISTS song_books (
            code TEXT PRIMARY KEY,
            name_ta TEXT NOT NULL,
            name_en TEXT NOT NULL,
            display_order INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS songs (
            id INTEGER PRIMARY KEY,
            songbook_code TEXT NOT NULL,
            songbook_name_ta TEXT,
            songbook_name_en TEXT,
            volume INTEGER DEFAULT 0,
            volume_name TEXT,
            song_number INTEGER DEFAULT 0,
            title_ta TEXT NOT NULL,
            title_en TEXT NOT NULL,
            alternate_title TEXT,
            lyrics_ta TEXT,
            lyrics_en TEXT,
            lyrics_bilingual TEXT,
            author TEXT,
            youtube_url TEXT
        );

        CREATE INDEX IF NOT EXISTS idx_songs_book_vol ON songs(songbook_code, volume, song_number);
        CREATE INDEX IF NOT EXISTS idx_songs_title_ta ON songs(title_ta);
        CREATE INDEX IF NOT EXISTS idx_songs_title_en ON songs(title_en);
    """)

    # Populate Song Books metadata
    songbooks_meta = [
        ("jebathota", "ஜெபத்தோட்ட ஜெயகீதங்கள்", "Jebathota Jeyageethangal", 1),
        ("keerthanai", "கீதங்களும் கீர்த்தனைகளும்", "Geethangalum Keerthanaigalum", 2),
        ("seyalveerar", "செயல்வீரர் கீதங்கள்", "Seyalveerar Geethanggal", 3),
        ("tac", "த.வ.மா பாடல் புத்தகம்", "TAC Song Book", 4),
        ("aikkiya", "கிறிஸ்தவ ஐக்கிய கீதங்கள்", "Kristhava Aikkiya Geethanggal", 5),
    ]
    tgt_cur.executemany("""
        INSERT OR REPLACE INTO song_books (code, name_ta, name_en, display_order)
        VALUES (?, ?, ?, ?)
    """, songbooks_meta)

    # 2. Fetch and categorize all songs
    src_songs = src_cur.execute("""
        SELECT s.id, s.title, s.alternate_title, s.lyrics, s.comments,
               ssb.songbook_id, ssb.entry as song_number,
               sb.name as songbook_name,
               a.display_name as author_name
        FROM songs s
        LEFT JOIN songs_songbooks ssb ON s.id = ssb.song_id
        LEFT JOIN song_books sb ON ssb.songbook_id = sb.id
        LEFT JOIN authors_songs a_rel ON s.id = a_rel.song_id
        LEFT JOIN authors a ON a_rel.author_id = a.id
    """).fetchall()

    print(f"Total songs read from source: {len(src_songs)}")

    # Clear existing songs
    tgt_cur.execute("DELETE FROM songs")

    count_jebathota = 0
    count_other = 0

    inserted_ids = set()

    for r in src_songs:
        s_id = r["id"]
        if s_id in inserted_ids:
            continue
        inserted_ids.add(s_id)

        comments_meta = parse_comments(r["comments"])
        title_ta = comments_meta["title_ta"]
        album = comments_meta["album"]
        youtube_url = comments_meta["youtube_url"]

        lyrics_ta, lyrics_en, lyrics_bilingual = parse_song_lyrics(r["lyrics"])

        # If title_ta was empty in comments, try to get from first line of lyrics_ta
        if not title_ta and lyrics_ta:
            first_line = lyrics_ta.split("\n")[0].strip()
            title_ta = first_line[:50]
        if not title_ta:
            title_ta = r["title"]

        title_en = r["title"]
        alt_title = r["alternate_title"] or ""
        author = r["author_name"] or "Fr. S. J. Berchmans"

        # Determine songbook code and volume
        sb_id = r["songbook_id"]
        sb_code = "jebathota"
        sb_name_ta = "ஜெபத்தோட்ட ஜெயகீதங்கள்"
        sb_name_en = "Jebathota Jeyageethangal"
        vol_num = 0
        vol_name = ""

        # Parse volume from album or songbook
        if album:
            m_jj = re.search(r"Jebathoatta\s*Jeyageethanggal\s*(\d+)", album, re.IGNORECASE)
            if m_jj:
                vol_num = int(m_jj.group(1))
                vol_name = f"Volume {vol_num}"
                sb_code = "jebathota"
                sb_name_ta = "ஜெபத்தோட்ட ஜெயகீதங்கள்"
                sb_name_en = "Jebathota Jeyageethangal"
            elif "Visuvaasa" in album:
                m_vg = re.search(r"Visuvaasa\s*Geethanggal\s*(\d+)", album, re.IGNORECASE)
                vol_num = int(m_vg.group(1)) if m_vg else 1
                vol_name = f"Visuvaasam {vol_num}"
                sb_code = "jebathota"
                sb_name_ta = "ஜெபத்தோட்ட ஜெயகீதங்கள்"
                sb_name_en = "Jebathota Jeyageethangal"
        elif sb_id == 3 or (r["author_name"] and "Berchmans" in r["author_name"]):
            sb_code = "jebathota"
            sb_name_ta = "ஜெபத்தோட்ட ஜெயகீதங்கள்"
            sb_name_en = "Jebathota Jeyageethangal"

        if sb_id == 8:
            sb_code = "keerthanai"
            sb_name_ta = "கீதங்களும் கீர்த்தனைகளும்"
            sb_name_en = "Geethangalum Keerthanaigalum"
            vol_name = "Traditional Hymns"
        elif sb_id == 5:
            sb_code = "seyalveerar"
            sb_name_ta = "செயல்வீரர் கீதங்கள்"
            sb_name_en = "Seyalveerar Geethanggal"
            vol_name = "Seyalveerar"
        elif sb_id == 6:
            sb_code = "tac"
            sb_name_ta = "த.வ.மா பாடல் புத்தகம்"
            sb_name_en = "TAC Song Book"
        elif sb_id == 9:
            sb_code = "aikkiya"
            sb_name_ta = "கிறிஸ்தவ ஐக்கிய கீதங்கள்"
            sb_name_en = "Kristhava Aikkiya Geethanggal"

        # Song entry number
        raw_num = str(r["song_number"] or "0").strip()
        num_match = re.search(r"(\d+)", raw_num)
        song_num = int(num_match.group(1)) if num_match else 0

        if sb_code == "jebathota":
            count_jebathota += 1
        else:
            count_other += 1

        tgt_cur.execute("""
            INSERT INTO songs (
                id, songbook_code, songbook_name_ta, songbook_name_en,
                volume, volume_name, song_number,
                title_ta, title_en, alternate_title,
                lyrics_ta, lyrics_en, lyrics_bilingual,
                author, youtube_url
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            s_id, sb_code, sb_name_ta, sb_name_en,
            vol_num, vol_name, song_num,
            title_ta, title_en, alt_title,
            lyrics_ta, lyrics_en, lyrics_bilingual,
            author, youtube_url
        ))

    tgt_conn.commit()

    total_inserted = tgt_cur.execute("SELECT count(*) FROM songs").fetchone()[0]
    jj_count = tgt_cur.execute("SELECT count(*) FROM songs WHERE songbook_code = 'jebathota'").fetchone()[0]
    vols = tgt_cur.execute("SELECT DISTINCT volume FROM songs WHERE songbook_code = 'jebathota' AND volume > 0 ORDER BY volume").fetchall()

    print("\n================ INGESTION SUMMARY ================")
    print(f"Total songs inserted: {total_inserted}")
    print(f"Jebathota Jeyageethangal songs: {jj_count}")
    print(f"Total volumes identified in Jebathota: {len(vols)} (Vols: {[v[0] for v in vols]})")
    print(f"Other Christian songs / Hymns inserted: {count_other}")
    print("===================================================")

    tgt_conn.close()
    src_conn.close()


if __name__ == "__main__":
    ingest()
