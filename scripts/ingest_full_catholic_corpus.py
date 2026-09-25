import os
import sys
import json
import sqlite3
import re

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "bible.sqlite.db")
RAW_DIR = os.path.join(BASE_DIR, "data", "raw_catholic")

SQL_TO_BOOK_ID = {
    # OT 1..39 -> target 1..39
    **{i: i for i in range(1, 40)},
    # Deuterocanonical Books (7 books)
    40: 67, # Tobit
    41: 68, # Judith
    43: 69, # Wisdom of Solomon
    44: 70, # Sirach
    45: 71, # Baruch
    47: 72, # 1 Maccabees
    48: 73, # 2 Maccabees
    # NT 49..75 -> target 40..66 (Matthew to Revelation)
    **{i: i - 9 for i in range(49, 76)}
}

DR_TO_BOOK_ID = {
    'Genesis': 1, 'Exodus': 2, 'Leviticus': 3, 'Numbers': 4, 'Deuteronomy': 5,
    'Joshua': 6, 'Judges': 7, 'Ruth': 8, '1-Samuel': 9, '2-Samuel': 10,
    '1-Kings': 11, '2-Kings': 12, '1-Chronicles': 13, '2-Chronicles': 14,
    'Ezra': 15, 'Nehemiah': 16, 'Esther': 17, 'Job': 18, 'Psalms': 19,
    'Proverbs': 20, 'Ecclesiastes': 21, 'SongOfSongs': 22, 'Isaiah': 23,
    'Jeremiah': 24, 'Lamentations': 25, 'Ezekiel': 26, 'Daniel': 27,
    'Hosea': 28, 'Joel': 29, 'Amos': 30, 'Obadiah': 31, 'Jonah': 32,
    'Micah': 33, 'Nahum': 34, 'Habakkuk': 35, 'Zephaniah': 36,
    'Haggai': 37, 'Zechariah': 38, 'Malachi': 39, 'Matthew': 40,
    'Mark': 41, 'Luke': 42, 'John': 43, 'Acts': 44, 'Romans': 45,
    '1-Corinthians': 46, '2-Corinthians': 47, 'Galatians': 48,
    'Ephesians': 49, 'Philippians': 50, 'Colossians': 51,
    '1-Thessalonians': 52, '2-Thessalonians': 53, '1-Timothy': 54,
    '2-Timothy': 55, 'Titus': 56, 'Philemon': 57, 'Hebrews': 58,
    'James': 59, '1-Peter': 60, '2-Peter': 61, '1-John': 62,
    '2-John': 63, '3-John': 64, 'Jude': 65, 'Revelation': 66,
    # 7 Catholic Deuterocanonical books
    'Tobit': 67, 'Judith': 68, 'Wisdom': 69, 'Sirach': 70,
    'Baruch': 71, '1-Maccabees': 72, '2-Maccabees': 73
}

def clean_poc_tamil(text: str) -> str:
    """Cleans raw Tamil POC database text for natural reading and TTS."""
    t = text.replace("''", "'").replace("\\'", "'")
    t = re.sub(r'[\u249c-\u24af]', '', t) # Enclosed alphanumeric footnote letters
    t = re.sub(r'\[[a-z0-9]+\]', '', t)    # [a], [b], etc.
    t = t.replace('\u2422', ' ')           # Poetic line break symbol
    t = re.sub(r'[\u207D\u207E\u208D\u208E]', '', t) # Superscript/subscript parentheses
    t = re.sub(r'\*+', '', t)              # Asterisk footnote indicators
    t = re.sub(r'\u276E.*?\u276F', '', t)  # ❮1-2❯ merged verse prefixes
    t = re.sub(r'[\u2983\u2984]', '', t)  # Double brackets
    t = re.sub(r'\s+', ' ', t).strip()
    return t

def map_vulgate_psalm_to_hebrew(v_ch: int, v_v: int):
    """Maps Vulgate/Douay-Rheims Psalm chapters/verses to Hebrew numbering."""
    if 1 <= v_ch <= 8:
        return (v_ch, v_v)
    elif v_ch == 9:
        if v_v <= 21:
            return (9, v_v)
        else:
            return (10, v_v - 21)
    elif 10 <= v_ch <= 112:
        return (v_ch + 1, v_v)
    elif v_ch == 113:
        if v_v <= 8:
            return (114, v_v)
        else:
            return (115, v_v - 8)
    elif v_ch == 114:
        return (116, v_v)
    elif v_ch == 115:
        return (116, v_v + 9)
    elif 116 <= v_ch <= 145:
        return (v_ch + 1, v_v)
    elif v_ch == 146:
        return (147, v_v)
    elif v_ch == 147:
        return (147, v_v + 11)
    elif 148 <= v_ch <= 150:
        return (v_ch, v_v)
    return (v_ch, v_v)

def parse_tamil_poc(t_verses_path: str):
    print(f"Loading Tamil Catholic (POC) verses from {t_verses_path}...")
    ta_verses = {} # (target_book_id, chapter, verse) -> clean_text
    with open(t_verses_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            m = re.search(r'\((\d{8}),\s*\'(.*?)\'\)[,;]', line)
            if not m:
                continue
            v_id = m.group(1)
            b_src = int(v_id[:2])
            if b_src in SQL_TO_BOOK_ID:
                b_tgt = SQL_TO_BOOK_ID[b_src]
                c_num = int(v_id[2:5])
                v_num = int(v_id[5:])
                raw_text = m.group(2)
                cleaned = clean_poc_tamil(raw_text)
                if cleaned:
                    ta_verses[(b_tgt, c_num, v_num)] = cleaned
    print(f"Loaded {len(ta_verses)} Tamil POC verses across 73 books.")
    return ta_verses

def parse_douay_rheims(dr_json_path: str):
    print(f"Loading English Douay-Rheims verses from {dr_json_path}...")
    with open(dr_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    en_verses = {} # (target_book_id, chapter, verse) -> text
    for b_name, b_id in DR_TO_BOOK_ID.items():
        chs = data.get(b_name, {})
        if not isinstance(chs, dict):
            continue
        for ch_str, v_dict in chs.items():
            if not ch_str.isdigit():
                continue
            ch = int(ch_str)
            if not isinstance(v_dict, dict):
                continue
            for v_str, text in v_dict.items():
                if not v_str.isdigit() or not isinstance(text, str):
                    continue
                v = int(v_str)
                clean_text = text.strip()
                if not clean_text:
                    continue
                
                # Apply Hebrew psalm numbering mapping if Psalms (book 19)
                if b_id == 19:
                    target_ch, target_v = map_vulgate_psalm_to_hebrew(ch, v)
                    en_verses[(b_id, target_ch, target_v)] = clean_text
                else:
                    en_verses[(b_id, ch, v)] = clean_text

    print(f"Loaded {len(en_verses)} English Douay-Rheims verses across 73 books.")
    return en_verses

def main():
    t_verses_path = os.path.join(RAW_DIR, "t_verses.sql")
    dr_json_path = os.path.join(RAW_DIR, "EntireBible-DOUAYRHEIMS.json")

    if not os.path.exists(t_verses_path):
        print(f"ERROR: {t_verses_path} not found.")
        sys.exit(1)
    if not os.path.exists(dr_json_path):
        print(f"ERROR: {dr_json_path} not found.")
        sys.exit(1)

    ta_poc = parse_tamil_poc(t_verses_path)
    en_drb = parse_douay_rheims(dr_json_path)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Check & Add columns if not existing
    cols = [c[1] for c in cursor.execute("PRAGMA table_info(verses)").fetchall()]
    if "text_ta_poc" not in cols:
        print("Adding column 'text_ta_poc' to 'verses' table...")
        cursor.execute("ALTER TABLE verses ADD COLUMN text_ta_poc TEXT;")
    if "text_en_drb" not in cols:
        print("Adding column 'text_en_drb' to 'verses' table...")
        cursor.execute("ALTER TABLE verses ADD COLUMN text_en_drb TEXT;")

    # 2. Gather existing verses in DB
    existing_keys = set(cursor.execute("SELECT book_id, chapter, verse FROM verses").fetchall())
    print(f"Found {len(existing_keys)} existing rows in 'verses'.")

    # 3. Update existing verses with POC Tamil and Douay-Rheims English
    print("Updating existing verses with Catholic translations...")
    update_batch = []
    for (b_id, ch, v) in existing_keys:
        poc_text = ta_poc.get((b_id, ch, v))
        drb_text = en_drb.get((b_id, ch, v))
        
        # For Deuterocanonical books (67-73), if poc_text or drb_text not in maps, keep existing text_ta / text_en
        if b_id >= 67:
            if not poc_text:
                row = cursor.execute("SELECT text_ta FROM verses WHERE book_id=? AND chapter=? AND verse=?", (b_id, ch, v)).fetchone()
                poc_text = row[0] if row else ""
            if not drb_text:
                row = cursor.execute("SELECT text_en FROM verses WHERE book_id=? AND chapter=? AND verse=?", (b_id, ch, v)).fetchone()
                drb_text = row[0] if row else ""

        if poc_text or drb_text:
            update_batch.append((poc_text, drb_text, b_id, ch, v))

    cursor.executemany("""
        UPDATE verses
        SET text_ta_poc = ?, text_en_drb = ?
        WHERE book_id = ? AND chapter = ? AND verse = ?
    """, update_batch)
    print(f"Updated {len(update_batch)} existing verses.")

    # 4. Insert any Catholic verses that were not already in the 66-canon Protestant database
    all_catholic_keys = set(ta_poc.keys()) | set(en_drb.keys())
    missing_keys = all_catholic_keys - existing_keys
    print(f"Found {len(missing_keys)} verses present in Catholic corpus not in base schema.")

    insert_batch = []
    for (b_id, ch, v) in sorted(missing_keys):
        t_poc = ta_poc.get((b_id, ch, v), "")
        t_drb = en_drb.get((b_id, ch, v), "")
        # Insert with fallback base text populated as well so no query ever returns NULL
        insert_batch.append((b_id, ch, v, t_poc, t_drb, t_poc, t_drb))

    if insert_batch:
        cursor.executemany("""
            INSERT INTO verses (book_id, chapter, verse, text_ta, text_en, text_ta_poc, text_en_drb)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, insert_batch)
        print(f"Inserted {len(insert_batch)} additional verses.")

    # 5. Create index for fast lookups
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_verses_lookup ON verses(book_id, chapter, verse);")

    conn.commit()
    conn.close()

    print("[SUCCESS] Catholic dual-corpus data ingested successfully!")

if __name__ == "__main__":
    main()
