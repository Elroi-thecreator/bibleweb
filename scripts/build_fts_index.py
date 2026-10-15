#!/usr/bin/env python3
"""
Builds SQLite FTS5 Full-Text Search Virtual Table into data/bible.sqlite.db.
Indexes bilingual Scripture corpora (Tamil & English) for sub-millisecond keyword queries.
Optimizes storage and vacuums the database to remain strictly under the 50 MB threshold.
"""

import os
import sqlite3
import sys
import time

def build_fts():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(base_dir, "data", "bible.sqlite.db")

    if not os.path.exists(db_path):
        print(f"Error: Database not found at {db_path}")
        sys.exit(1)

    initial_size_mb = os.path.getsize(db_path) / (1024 * 1024)
    print(f"Initial bible.sqlite.db size: {initial_size_mb:.2f} MB")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 1. Drop existing FTS table if any to ensure clean rebuild
    cursor.execute("DROP TABLE IF EXISTS verses_fts;")

    # 2. Create FTS5 external content virtual table
    print("Creating FTS5 virtual table 'verses_fts'...")
    cursor.execute("""
        CREATE VIRTUAL TABLE verses_fts USING fts5(
            text_ta,
            text_en,
            content='verses',
            content_rowid='id',
            columnsize=0,
            tokenize='unicode61'
        );
    """)

    # 3. Populate FTS5 index from verses table
    print("Populating FTS5 index across all Scripture verses...")
    t0 = time.time()
    cursor.execute("""
        INSERT INTO verses_fts(rowid, text_ta, text_en)
        SELECT id,
               TRIM(COALESCE(text_ta, '') || ' ' || COALESCE(text_ta_poc, '')),
               TRIM(COALESCE(text_en, '') || ' ' || COALESCE(text_en_drb, ''))
        FROM verses;
    """)
    conn.commit()
    t1 = time.time()
    print(f"Populated {cursor.rowcount} verses in {t1 - t0:.2f}s.")

    # 4. Optimize FTS index structure and VACUUM
    print("Optimizing FTS index doclists...")
    cursor.execute("INSERT INTO verses_fts(verses_fts) VALUES('optimize');")
    conn.commit()
    conn.close()

    print("Running VACUUM with 8KB page size to optimize storage under 50 MB...")
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA page_size = 8192;")
    conn.execute("VACUUM;")
    conn.close()

    final_size_mb = os.path.getsize(db_path) / (1024 * 1024)
    print("=" * 65)
    print(" FTS5 INDEX BUILD COMPLETED")
    print(f" Final Database Size: {final_size_mb:.2f} MB (Delta: +{final_size_mb - initial_size_mb:.2f} MB)")
    print(f" GitHub 50MB Limit:   {'PASSED (< 50 MB)' if final_size_mb < 50.0 else 'EXCEEDED'}")
    print("=" * 65)

if __name__ == "__main__":
    build_fts()
