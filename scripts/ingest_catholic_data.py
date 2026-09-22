import os
import sys
import json
import sqlite3
import re

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "bible.sqlite.db")
RAW_DIR = os.path.join(BASE_DIR, "data", "raw_catholic")

BOOK_MAPPING = [
    # (source_sql_id, source_json_file, target_book_id, code, name_en, name_ta, chapters, testament)
    (40, "tobias.json", 67, "TOB", "Tobit", "தோபித்து", 14, "OT"),
    (41, "judith.json", 68, "JDT", "Judith", "யூதித்து", 16, "OT"),
    (43, "wisdom.json", 69, "WIS", "Wisdom of Solomon", "சாலமோனின் ஞானம்", 19, "OT"),
    (44, "ecclesiasticus.json", 70, "SIR", "Sirach", "சீராக் (சீராக்கின் ஞானம்)", 51, "OT"),
    (45, "baruch.json", 71, "BAR", "Baruch", "பாரூக்", 6, "OT"),
    (47, "1-machabees.json", 72, "1MA", "1 Maccabees", "1 மக்கபேயர்", 16, "OT"),
    (48, "2-machabees.json", 73, "2MA", "2 Maccabees", "2 மக்கபேயர்", 15, "OT"),
]

def load_english_verses():
    """Loads English Douay-Rheims verses from JSON."""
    en_verses = {} # (target_id, chapter, verse) -> text
    for sql_id, json_file, target_id, code, name_en, name_ta, total_chs, testament in BOOK_MAPPING:
        json_path = os.path.join(RAW_DIR, json_file)
        if not os.path.exists(json_path):
            print(f"WARNING: Missing {json_path}")
            continue
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for ch in data.get('chapters', []):
                c_num = int(ch['chapter'])
                if c_num == 0:
                    continue # skip argument / prologue
                for v in ch.get('verses', []):
                    v_num = int(v['verse'])
                    text = v.get('text', '').strip()
                    en_verses[(target_id, c_num, v_num)] = text
    print(f"Loaded {len(en_verses)} English Douay-Rheims verses.")
    return en_verses

def parse_tamil_verses(t_verses_path):
    """Parses Tamil Catholic verses from t_verses.sql for target books."""
    target_source_ids = {m[0]: m[2] for m in BOOK_MAPPING} # source_id -> target_id
    ta_verses = {} # (target_id, chapter, verse) -> text

    print(f"Parsing Tamil verses from {t_verses_path}...")
    line_count = 0
    with open(t_verses_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            line_count += 1
            # Look for: (40001001, 'verse text')
            if not line.startswith('('):
                # Try finding in line
                m = re.search(r'\((\d{8}),\s*\'(.*?)\'\)[,;]', line)
                if not m:
                    continue
                v_id = m.group(1)
                v_text = m.group(2)
            else:
                parts = line.strip().rstrip(';,').strip('()').split(',', 1)
                if len(parts) < 2:
                    continue
                v_id = parts[0].strip()
                v_text = parts[1].strip().strip("'")

            if len(v_id) == 8 and v_id.isdigit():
                b_num = int(v_id[:2])
                c_num = int(v_id[2:5])
                verse_num = int(v_id[5:])
                if b_num in target_source_ids:
                    target_id = target_source_ids[b_num]
                    # Clean escaped quotes in sql
                    clean_text = v_text.replace("''", "'").replace("\\'", "'").strip()
                    # Remove trailing footnote markers if present
                    clean_text = re.sub(r'[⒫⒬⒭⒮⒯⒰⒱⒲⒳⒴]$', '', clean_text).strip()
                    ta_verses[(target_id, c_num, verse_num)] = clean_text

    print(f"Parsed {len(ta_verses)} Tamil Catholic verses across {len(target_source_ids)} books.")
    return ta_verses

def main():
    en_verses = load_english_verses()
    t_verses_path = os.path.join(RAW_DIR, "t_verses.sql")
    if not os.path.exists(t_verses_path):
        print(f"ERROR: {t_verses_path} does not exist yet. Please wait for download to finish.")
        sys.exit(1)

    ta_verses = parse_tamil_verses(t_verses_path)

    # Insert into database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("Adding Deuterocanonical books to 'books' table...")
    for sql_id, json_file, target_id, code, name_en, name_ta, total_chs, testament in BOOK_MAPPING:
        cursor.execute("""
            INSERT OR REPLACE INTO books (id, code, name_ta, testament)
            VALUES (?, ?, ?, ?)
        """, (target_id, code, name_ta, testament))
        print(f"  -> Book {target_id}: {name_en} ({name_ta}) - {total_chs} chapters")

    print("Inserting bilingual verses into 'verses' table...")
    # Gather all distinct (target_id, c_num, v_num) from either ta or en
    all_keys = sorted(set(list(en_verses.keys()) + list(ta_verses.keys())))
    inserted = 0

    # First delete existing verses for these book IDs to avoid duplication
    for _, _, target_id, _, _, _, _, _ in BOOK_MAPPING:
        cursor.execute("DELETE FROM verses WHERE book_id = ?", (target_id,))

    batch = []
    for (target_id, c_num, v_num) in all_keys:
        t_en = en_verses.get((target_id, c_num, v_num), "")
        t_ta = ta_verses.get((target_id, c_num, v_num), "")
        batch.append((target_id, c_num, v_num, t_ta, t_en))
        inserted += 1

    cursor.executemany("""
        INSERT INTO verses (book_id, chapter, verse, text_ta, text_en)
        VALUES (?, ?, ?, ?, ?)
    """, batch)

    conn.commit()
    conn.close()

    print(f"[SUCCESS] Ingested {inserted} bilingual Deuterocanonical verses into {DB_PATH}!")

if __name__ == "__main__":
    main()
