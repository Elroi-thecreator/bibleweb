#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ingest Thiruviviliam (திருவிவிலியம் — Catholic POC Translation)
==============================================================
Populates the standalone Catholic Tamil database `data/thiruviviliam.sqlite.db`
(all 73 books, 35,248 verses) keeping the primary `data/bible.sqlite.db` lean (<50 MB)
and 100% open-licensed for WinGet Policy 2.2 distribution.
"""

import os
import sys
import re
import gzip
import shutil
import sqlite3
import urllib.request

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
DEST_DB = os.path.join(DATA_DIR, "thiruviviliam.sqlite.db")
GZ_DB = os.path.join(DATA_DIR, "thiruviviliam.sqlite.db.gz")
RAW_DIR = os.path.join(DATA_DIR, "raw_catholic")
T_VERSES_PATH = os.path.join(RAW_DIR, "t_verses.sql")
T_VERSES_URL = "https://raw.githubusercontent.com/jayarathina/Tamil-Bible-Database/master/MySQL/archive/t_verses.sql"


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


def ingest_thiruviviliam(dest_db: str = DEST_DB) -> dict:
    """Ensures standalone Thiruviviliam database is created and verified."""
    # 1. Check if already present and healthy
    if os.path.exists(dest_db) and os.path.getsize(dest_db) > 10000000:
        try:
            conn = sqlite3.connect(dest_db)
            c = conn.execute("SELECT count(*) FROM verses WHERE book_id = 67;").fetchone()[0]
            conn.close()
            if c > 0:
                print(f"[EXISTS] Thiruviviliam already installed at {dest_db} ({c} Tobit verses verified).")
                return {
                    "status": "success",
                    "action": "already_installed",
                    "database": dest_db,
                    "deuterocanon_verified": True
                }
        except Exception:
            pass

    # 2. Fast Path: Decompress pre-bundled .gz if available
    if os.path.exists(GZ_DB) and os.path.getsize(GZ_DB) > 1000000:
        print(f"Decompressing {GZ_DB} -> {dest_db} ...")
        with gzip.open(GZ_DB, "rb") as f_in, open(dest_db, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)
        size_mb = os.path.getsize(dest_db) / (1024 * 1024)
        print(f"[SUCCESS] Decompressed {dest_db} ({size_mb:.2f} MB).")
        return {
            "status": "success",
            "action": "decompressed_from_gz",
            "database": dest_db,
            "size_mb": round(size_mb, 2)
        }

    # 3. Fallback Path: Build database from t_verses.sql
    from scripts.build_thiruviviliam_db import build_thiruviviliam_database
    download_t_verses(T_VERSES_PATH)
    built_path = build_thiruviviliam_database(T_VERSES_PATH, dest_db)
    size_mb = os.path.getsize(built_path) / (1024 * 1024)

    return {
        "status": "success",
        "action": "built_from_source",
        "database": built_path,
        "size_mb": round(size_mb, 2)
    }


if __name__ == "__main__":
    result = ingest_thiruviviliam()
    print("INGEST COMPLETE:", result)
