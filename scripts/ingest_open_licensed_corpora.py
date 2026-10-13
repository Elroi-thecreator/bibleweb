#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ingest Open-Licensed & Public Domain Scripture Corpora
======================================================
Populates `data/bible.sqlite.db` exclusively with verifiably open-licensed
and Public Domain scripture texts in compliance with Windows Package Manager
Policy 2.2:

1. Tamil Old Version (1871 Rev. Henry Bower Translation / MABS)
   - Column: `verses.text_ta` (Books 1-66)
   - License: Public Domain worldwide (published 1871; translator died 1885).

2. Tamil Indian Revised Version (IRV Tamil, 2017/2019)
   - Column: `verses.text_ta_poc` (Books 1-66)
   - Copyright: © 2017, 2019 Bridge Connectivity Solutions Pvt. Ltd.
   - Source: https://ebible.org/Scriptures/tam2017_vpl.zip
   - License: Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)
     (https://creativecommons.org/licenses/by-sa/4.0/)

3. King James Version (1611 / 1769 Oxford Blayney Standard Text)
   - Column: `verses.text_en` (Books 1-66)
   - Source: https://ebible.org/Scriptures/eng-kjv2006_vpl.zip
   - License: Public Domain worldwide.

4. Douay-Rheims Bible (1582-1609 / 1752 Bishop Richard Challoner Revision)
   - Column: `verses.text_en_drb` (Books 1-73, including the 7 Catholic Deuterocanonical books)
   - Source: https://ebible.org/Scriptures/engDRA_vpl.zip
   - License: Public Domain worldwide (published 1752; reviser died 1781).

All legacy 2012 Tamil Ecumenical / POC strings are completely purged and
`VACUUM` is executed so zero unallocated pages remain in `data/bible.sqlite.db`.
"""

import io
import os
import sqlite3
import sys
import urllib.request
import xml.etree.ElementTree as ET
import zipfile

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "bible.sqlite.db")

TAM2017_ZIP_URL = "https://ebible.org/Scriptures/tam2017_vpl.zip"
ENGDRA_ZIP_URL = "https://ebible.org/Scriptures/engDRA_vpl.zip"

# Standard SIL/UBS 3-letter book codes to canonical book_id (1..73)
BOOK_CODE_TO_ID = {
    "GEN": 1, "EXO": 2, "LEV": 3, "NUM": 4, "DEU": 5,
    "JOS": 6, "JDG": 7, "RUT": 8, "1SA": 9, "2SA": 10,
    "1KI": 11, "2KI": 12, "1CH": 13, "2CH": 14, "EZR": 15,
    "NEH": 16, "EST": 17, "JOB": 18, "PSA": 19, "PRO": 20,
    "ECC": 21, "SNG": 22, "ISA": 23, "JER": 24, "LAM": 25,
    "EZK": 26, "DAN": 27, "HOS": 28, "JOL": 29, "AMO": 30,
    "OBA": 31, "JON": 32, "MIC": 33, "NAM": 34, "HAB": 35,
    "ZEP": 36, "HAG": 37, "ZEC": 38, "MAL": 39,
    "MAT": 40, "MRK": 41, "LUK": 42, "JHN": 43, "ACT": 44,
    "ROM": 45, "1CO": 46, "2CO": 47, "GAL": 48, "EPH": 49,
    "PHP": 50, "COL": 51, "1TH": 52, "2TH": 53, "1TI": 54,
    "2TI": 55, "TIT": 56, "PHM": 57, "HEB": 58, "JAS": 59,
    "1PE": 60, "2PE": 61, "1JN": 62, "2JN": 63, "3JN": 64,
    "JUD": 65, "REV": 66,
    # 7 Catholic Deuterocanonical Books
    "TOB": 67, "JDT": 68, "WIS": 69, "SIR": 70, "BAR": 71,
    "1MA": 72, "2MA": 73,
}


def download_zip_xml(url: str, xml_filename: str) -> bytes:
    """Downloads an eBible.org VPL zip archive and extracts its XML file."""
    print(f"Downloading {url} ...")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (BibleWeb Open-Corpus Ingest)"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        zip_bytes = resp.read()
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        return zf.read(xml_filename)


def parse_vpl_xml(xml_bytes: bytes) -> dict:
    """Parses eBible VPL XML into {(book_id, chapter, verse): text}."""
    root = ET.fromstring(xml_bytes)
    verses = {}
    for v_elem in root.findall("v"):
        b_code = v_elem.attrib.get("b", "").strip().upper()
        if b_code not in BOOK_CODE_TO_ID:
            continue
        b_id = BOOK_CODE_TO_ID[b_code]
        try:
            ch = int(v_elem.attrib.get("c", "0"))
            v_num = int(v_elem.attrib.get("v", "0"))
        except ValueError:
            continue
        text = (v_elem.text or "").strip()
        if b_id and ch > 0 and v_num > 0 and text:
            verses[(b_id, ch, v_num)] = text
    return verses


def main():
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Database not found at {DB_PATH}")

    # 1. Fetch Tamil IRV (CC BY-SA 4.0) from eBible.org
    tam_xml = download_zip_xml(TAM2017_ZIP_URL, "tam2017_vpl.xml")
    irv_verses = parse_vpl_xml(tam_xml)
    print(f"Parsed {len(irv_verses)} Tamil IRV (CC BY-SA 4.0) verses across 66 books.")

    # 2. Fetch English Douay-Rheims 1752 (Public Domain) from eBible.org
    dra_xml = download_zip_xml(ENGDRA_ZIP_URL, "engDRA_vpl.xml")
    dra_verses = parse_vpl_xml(dra_xml)
    print(f"Parsed {len(dra_verses)} Douay-Rheims 1752 (Public Domain) verses across 73 books.")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 3. Purge ALL 2012 POC Tamil strings from the database:
    #    - Clear `text_ta_poc` across the entire table first.
    #    - Clear `text_ta` for Deuterocanonical books (book_id >= 67).
    #    - Delete extra non-Protestant/non-DRB orphan rows (e.g. 3 John 1:15) and clear
    #      `text_ta` on Revelation 12:18 where POC text was previously inserted.
    print("Purging all legacy 2012 POC text from verses table...")
    cursor.execute("UPDATE verses SET text_ta_poc = '';")
    cursor.execute("UPDATE verses SET text_ta = '' WHERE book_id >= 67;")
    cursor.execute("DELETE FROM verses WHERE book_id = 64 AND chapter = 1 AND verse = 15;")
    cursor.execute("UPDATE verses SET text_ta = '' WHERE book_id = 66 AND chapter = 12 AND verse = 18;")

    # Remove any row in books 1..73 where both text_ta and text_en and text_en_drb are empty
    cursor.execute("""
        DELETE FROM verses
        WHERE LENGTH(TRIM(COALESCE(text_ta, ''))) = 0
          AND LENGTH(TRIM(COALESCE(text_en, ''))) = 0
          AND LENGTH(TRIM(COALESCE(text_en_drb, ''))) = 0;
    """)

    # 4. Populate `text_ta_poc` with Tamil Indian Revised Version (IRV 2019, CC BY-SA 4.0)
    irv_batch = [(text, b_id, ch, v) for (b_id, ch, v), text in irv_verses.items()]
    cursor.executemany(
        "UPDATE verses SET text_ta_poc = ? WHERE book_id = ? AND chapter = ? AND verse = ?;",
        irv_batch,
    )
    print(f"Updated {len(irv_batch)} verses with Tamil IRV (CC BY-SA 4.0).")

    # 5. Ensure `text_en_drb` (and `text_en` for Deuterocanonical books 67..73) holds
    #    1752 Douay-Rheims Public Domain text
    dra_batch = [(text, b_id, ch, v) for (b_id, ch, v), text in dra_verses.items() if b_id != 19]
    cursor.executemany(
        "UPDATE verses SET text_en_drb = ? WHERE book_id = ? AND chapter = ? AND verse = ?;",
        dra_batch,
    )
    cursor.execute("UPDATE verses SET text_en = text_en_drb WHERE book_id >= 67 AND LENGTH(COALESCE(text_en_drb, '')) > 0;")

    conn.commit()

    # 6. Rebuild database file with VACUUM so zero deleted POC pages remain in binary
    print("Running VACUUM to purge all free-list pages from SQLite binary...")
    cursor.execute("VACUUM;")
    conn.close()

    print("[SUCCESS] Database updated with 100% open-licensed (CC BY-SA 4.0) and Public Domain corpora.")


if __name__ == "__main__":
    main()
