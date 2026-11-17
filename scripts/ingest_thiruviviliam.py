#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ingest Thiruviviliam (திருவிவிலியம் — Catholic POC Translation)
==============================================================
Populates `data/bible.sqlite.db` with the complete 73-book Catholic Tamil text
(Thiruviviliam / POC) while preserving the open-licensed Indian Revised Version (IRV)
in `verses.text_ta_irv`.

Source: https://raw.githubusercontent.com/jayarathina/Tamil-Bible-Database/master/MySQL/archive/t_verses.sql
"""

import os
import sys
import re
import sqlite3
import urllib.request

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "bible.sqlite.db")
RAW_DIR = os.path.join(BASE_DIR, "data", "raw_catholic")
T_VERSES_PATH = os.path.join(RAW_DIR, "t_verses.sql")
T_VERSES_URL = "https://raw.githubusercontent.com/jayarathina/Tamil-Bible-Database/master/MySQL/archive/t_verses.sql"

SQL_TO_BOOK_ID = {
    # OT 1..39 -> target 1..39
    **{i: i for i in range(1, 40)},
    # Deuterocanonical Books (7 books)
    40: 67,  # Tobit
    41: 68,  # Judith
    43: 69,  # Wisdom of Solomon
    44: 70,  # Sirach
    45: 71,  # Baruch
    47: 72,  # 1 Maccabees
    48: 73,  # 2 Maccabees
    # NT 49..75 -> target 40..66 (Matthew to Revelation)
    **{i: i - 9 for i in range(49, 76)}
}


def clean_poc_tamil(text: str) -> str:
    """Cleans raw Tamil POC database text while preserving merged verse tags as [X-Y]."""
    t = text.replace("''", "'").replace("\\'", "'")
    t = re.sub(r'[\u249c-\u24af]', '', t)  # Enclosed alphanumeric footnote letters
    t = re.sub(r'\[[a-z0-9]+\]', '', t)     # [a], [b], etc.
    t = t.replace('\u2422', ' ')            # Poetic line break symbol
    t = re.sub(r'[\u207D\u207E\u208D\u208E]', '', t)  # Superscript/subscript parentheses
    t = re.sub(r'\*+', '', t)               # Asterisk footnote indicators
    # Convert ❮1-2❯ or ❮10-11❯ to [1-2] or [10-11]
    t = re.sub(r'\u276E(.*?)\u276F', r'[\1] ', t)
    t = re.sub(r'[\u2983\u2984]', '', t)   # Double brackets
    t = re.sub(r'\s+', ' ', t).strip()
    return t


def download_t_verses(dest_path: str = T_VERSES_PATH) -> str:
    """Downloads t_verses.sql if not already present."""
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    if os.path.exists(dest_path) and os.path.getsize(dest_path) > 10000000:
        print(f"[EXISTS] {dest_path} ({os.path.getsize(dest_path)} bytes)")
        return dest_path

    print(f"Downloading t_verses.sql from {T_VERSES_URL} ...")
    req = urllib.request.Request(T_VERSES_URL, headers={"User-Agent": "Mozilla/5.0 (BibleWeb Thiruviviliam Ingest)"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        content = resp.read()
    with open(dest_path, "wb") as f:
        f.write(content)
    print(f"[DOWNLOADED] Saved {dest_path} ({len(content)} bytes)")
    return dest_path


def parse_tamil_poc(t_verses_path: str) -> dict:
    """Parses t_verses.sql into {(target_book_id, chapter, verse): text}."""
    print(f"Parsing Thiruviviliam from {t_verses_path} ...")
    raw_list = []
    with open(t_verses_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            m = re.search(r'\((\d{8}),\s*\'(.*?)\'\)[,;]', line)
            if not m:
                continue
            raw_list.append((int(m.group(1)), m.group(2)))

    # Two-pass resolution: resolve "Same as above" to the head verse of the merged group
    ta_verses = {}
    for i, (v_id, raw_text) in enumerate(raw_list):
        b_src = v_id // 1000000
        if b_src not in SQL_TO_BOOK_ID:
            continue
        b_tgt = SQL_TO_BOOK_ID[b_src]
        c_num = (v_id // 1000) % 1000
        v_num = v_id % 1000

        if raw_text.strip().lower() == "same as above":
            head_text = ""
            for j in range(i - 1, max(-1, i - 15), -1):
                prev_id, prev_text = raw_list[j]
                if prev_id // 1000 == v_id // 1000 and prev_text.strip().lower() != "same as above":
                    head_text = prev_text
                    break
            cleaned = clean_poc_tamil(head_text) if head_text else ""
        else:
            cleaned = clean_poc_tamil(raw_text)

        if cleaned:
            ta_verses[(b_tgt, c_num, v_num)] = cleaned

    print(f"Parsed {len(ta_verses)} Thiruviviliam verses across 73 books.")
    return ta_verses


def ingest_thiruviviliam(db_path: str = DB_PATH) -> dict:
    """Ingests Thiruviviliam verses into target SQLite database."""
    t_verses_file = download_t_verses()
    ta_poc = parse_tamil_poc(t_verses_file)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 1. Ensure columns exist
    cols = [c[1] for c in cursor.execute("PRAGMA table_info(verses)").fetchall()]
    if "text_ta_irv" not in cols:
        print("Adding column 'text_ta_irv' to preserve Indian Revised Version...")
        cursor.execute("ALTER TABLE verses ADD COLUMN text_ta_irv TEXT;")
        # Back up existing text_ta_poc (which currently holds IRV) into text_ta_irv
        cursor.execute("UPDATE verses SET text_ta_irv = text_ta_poc WHERE text_ta_poc IS NOT NULL;")

    if "text_ta_poc" not in cols:
        print("Adding column 'text_ta_poc' for Thiruviviliam...")
        cursor.execute("ALTER TABLE verses ADD COLUMN text_ta_poc TEXT;")

    # 2. Gather existing verses in DB
    existing_rows = cursor.execute("SELECT book_id, chapter, verse FROM verses").fetchall()
    existing_keys = set(existing_rows)
    print(f"Found {len(existing_keys)} existing rows in 'verses'.")

    # 3. Update existing verses with POC Tamil
    print("Updating verses with Thiruviviliam (POC) text ...")
    update_batch = []
    for (b_id, ch, v) in existing_keys:
        poc_text = ta_poc.get((b_id, ch, v))
        if poc_text:
            update_batch.append((poc_text, b_id, ch, v))

    cursor.executemany("""
        UPDATE verses
        SET text_ta_poc = ?
        WHERE book_id = ? AND chapter = ? AND verse = ?
    """, update_batch)
    print(f"Updated {len(update_batch)} existing verses with Thiruviviliam.")

    # 4. Insert any verses that were in ta_poc but not in base DB
    missing_keys = set(ta_poc.keys()) - existing_keys
    print(f"Found {len(missing_keys)} verses present in Thiruviviliam not in base table.")
    insert_batch = []
    for (b_id, ch, v) in sorted(missing_keys):
        t_poc = ta_poc.get((b_id, ch, v), "")
        insert_batch.append((b_id, ch, v, t_poc, "", t_poc, ""))

    if insert_batch:
        cursor.executemany("""
            INSERT OR REPLACE INTO verses (book_id, chapter, verse, text_ta, text_en, text_ta_poc, text_ta_irv)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, insert_batch)
        print(f"Inserted {len(insert_batch)} missing verses.")

    # 5. Verify Deuterocanon (books 67..73) non-empty count
    dc_count = cursor.execute(
        "SELECT COUNT(*) FROM verses WHERE book_id >= 67 AND LENGTH(TRIM(COALESCE(text_ta_poc, ''))) > 0"
    ).fetchone()[0]
    print(f"Verification: {dc_count} Deuterocanonical verses have full Tamil Thiruviviliam text!")

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_verses_lookup ON verses(book_id, chapter, verse);")
    conn.commit()
    conn.close()

    return {
        "status": "success",
        "updated_verses": len(update_batch),
        "inserted_verses": len(insert_batch),
        "deuterocanon_verses": dc_count,
    }


if __name__ == "__main__":
    result = ingest_thiruviviliam()
    print("INGEST COMPLETE:", result)
