#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build Standalone Thiruviviliam SQLite Database
==============================================
Creates a dedicated, decoupled database `data/thiruviviliam.sqlite.db` containing
all 73 books of the Catholic Tamil Bible (Thiruviviliam / POC), keeping the primary
`data/bible.sqlite.db` lean, open-licensed, and strictly under 50 MB.
"""

import os
import sys
import re
import sqlite3
import gzip
import shutil

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
RAW_PATH = os.path.join(DATA_DIR, "raw_catholic", "t_verses.sql")
DEST_DB = os.path.join(DATA_DIR, "thiruviviliam.sqlite.db")
GZ_DB = os.path.join(DATA_DIR, "thiruviviliam.sqlite.db.gz")

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
    t = re.sub(r'[\u249c-\u24af]', '', t)
    t = re.sub(r'\[[a-z0-9]+\]', '', t)
    t = t.replace('\u2422', ' ')
    t = re.sub(r'[\u207D\u207E\u208D\u208E]', '', t)
    t = re.sub(r'\*+', '', t)
    t = re.sub(r'\u276E(.*?)\u276F', r'[\1] ', t)
    t = re.sub(r'[\u2983\u2984]', '', t)
    t = re.sub(r'\s+', ' ', t).strip()
    return t


def build_thiruviviliam_database(raw_path: str = RAW_PATH, dest_db: str = DEST_DB) -> str:
    if not os.path.exists(raw_path):
        from scripts.ingest_thiruviviliam import download_t_verses
        download_t_verses(raw_path)

    print(f"Building standalone Thiruviviliam database at: {dest_db}")
    if os.path.exists(dest_db):
        os.remove(dest_db)

    raw_list = []
    with open(raw_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            m = re.search(r'\((\d{8}),\s*\'(.*?)\'\)[,;]', line)
            if m:
                raw_list.append((int(m.group(1)), m.group(2)))

    conn = sqlite3.connect(dest_db)
    conn.execute("PRAGMA page_size = 8192;")
    conn.execute("""
        CREATE TABLE verses (
            book_id INTEGER NOT NULL,
            chapter INTEGER NOT NULL,
            verse INTEGER NOT NULL,
            text_ta TEXT NOT NULL,
            PRIMARY KEY(book_id, chapter, verse)
        );
    """)

    rows = []
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
            rows.append((b_tgt, c_num, v_num, cleaned))

    conn.executemany("INSERT INTO verses (book_id, chapter, verse, text_ta) VALUES (?, ?, ?, ?);", rows)
    conn.commit()

    print("Building FTS5 search index on Thiruviviliam verses...")
    conn.execute("CREATE VIRTUAL TABLE IF NOT EXISTS verses_fts USING fts5(text_ta, content='verses', content_rowid='rowid');")
    conn.execute("INSERT INTO verses_fts(verses_fts) VALUES('rebuild');")
    conn.commit()

    conn.execute("VACUUM;")
    conn.close()

    size_mb = os.path.getsize(dest_db) / (1024 * 1024)
    print(f"[SUCCESS] Created {dest_db}: {len(rows)} verses across 73 books ({size_mb:.2f} MB).")

    # Also generate compressed .gz version
    with open(dest_db, "rb") as f_in, gzip.open(GZ_DB, "wb", compresslevel=9) as f_out:
        shutil.copyfileobj(f_in, f_out)
    gz_size_mb = os.path.getsize(GZ_DB) / (1024 * 1024)
    print(f"[SUCCESS] Created compressed bundle {GZ_DB} ({gz_size_mb:.2f} MB).")

    return dest_db


if __name__ == "__main__":
    build_thiruviviliam_database()
