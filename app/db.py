import os
import sqlite3
from typing import Dict, List

# Absolute cross-platform path resolution
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "data", "bible.sqlite.db")
FALLBACK_DB_PATH = os.path.join(BASE_DIR, "data", "bible.sqlite")

# Prefer env var if supplied, else check default and fallback locations
DB_PATH = os.getenv("DATABASE_PATH", DEFAULT_DB_PATH)


def get_connection():
    """Returns a connection, checking both .sqlite.db and .sqlite extensions."""
    target_path = os.path.abspath(DB_PATH)

    # Auto-resolve if extension differs between .sqlite.db and .sqlite
    if not os.path.exists(target_path):
        if os.path.exists(DEFAULT_DB_PATH):
            target_path = DEFAULT_DB_PATH
        elif os.path.exists(FALLBACK_DB_PATH):
            target_path = FALLBACK_DB_PATH
        else:
            data_dir = os.path.join(BASE_DIR, "data")
            files_in_data = os.listdir(data_dir) if os.path.exists(data_dir) else "FOLDER NOT FOUND"
            files_in_root = os.listdir(BASE_DIR)
            raise FileNotFoundError(
                f"DB file not found at '{target_path}'.\n"
                f"Files in root: {files_in_root}\n"
                f"Files in data/: {files_in_data}"
            )

    conn = sqlite3.connect(target_path)
    conn.row_factory = sqlite3.Row
    return conn


# 66 Canon Books Metadata (ID, English Name, Tamil Name, Chapter Count)
BIBLE_BOOKS = [
    (1, "Genesis", "ஆதியாகமம்", 50),
    (2, "Exodus", "யாத்திராகமம்", 40),
    (3, "Leviticus", "லேவியராகமம்", 27),
    (4, "Numbers", "எண்ணாகமம்", 36),
    (5, "Deuteronomy", "உபாகமம்", 34),
    (6, "Joshua", "யோசுவா", 24),
    (7, "Judges", "நியாயாதிபதிகள்", 21),
    (8, "Ruth", "ரூத்", 4),
    (9, "1 Samuel", "1 சாமுவேல்", 31),
    (10, "2 Samuel", "2 சாமுவேல்", 24),
    (11, "1 Kings", "1 இராஜாக்கள்", 22),
    (12, "2 Kings", "2 இராஜாக்கள்", 25),
    (13, "1 Chronicles", "1 நாளாகமம்", 29),
    (14, "2 Chronicles", "2 நாளாகமம்", 36),
    (15, "Ezra", "எஸ்றா", 10),
    (16, "Nehemiah", "நெகேமியா", 13),
    (17, "Esther", "எஸ்தர்", 10),
    (18, "Job", "யோபு", 42),
    (19, "Psalms", "சங்கீதம்", 150),
    (20, "Proverbs", "நீதிமொழிகள்", 31),
    (21, "Ecclesiastes", "பிரசங்கி", 12),
    (22, "Song of Solomon", "உன்னதப்பாட்டு", 8),
    (23, "Isaiah", "ஏசாயா", 66),
    (24, "Jeremiah", "எரேமியா", 52),
    (25, "Lamentations", "புலம்பல்", 5),
    (26, "Ezekiel", "எசேக்கியேல்", 48),
    (27, "Daniel", "தானியேல்", 12),
    (28, "Hosea", "ஓசியா", 14),
    (29, "Joel", "யோவேல்", 3),
    (30, "Amos", "ஆமோஸ்", 9),
    (31, "Obadiah", "ஒபதியா", 1),
    (32, "Jonah", "யோனா", 4),
    (33, "Micah", "மீகா", 7),
    (34, "Nahum", "நாகூம்", 3),
    (35, "Habakkuk", "ஆபகூக்", 3),
    (36, "Zephaniah", "செப்பனியா", 3),
    (37, "Haggai", "ஆகாய்", 2),
    (38, "Zechariah", "சகரியா", 14),
    (39, "Malachi", "மல்கியா", 4),
    (40, "Matthew", "மத்தேயு", 28),
    (41, "Mark", "மாற்கு", 16),
    (42, "Luke", "லூக்கா", 24),
    (43, "John", "யோவான்", 21),
    (44, "Acts", "அப்போஸ்தலர்", 28),
    (45, "Romans", "ரோமர்", 16),
    (46, "1 Corinthians", "1 கொரிந்தியர்", 16),
    (47, "2 Corinthians", "2 கொரிந்தியர்", 13),
    (48, "Galatians", "கலாத்தியர்", 6),
    (49, "Ephesians", "எபேசியர்", 6),
    (50, "Philippians", "பிலிப்பியர்", 4),
    (51, "Colossians", "கொலோசெயர்", 4),
    (52, "1 Thessalonians", "1 தெசலோனிக்கேயர்", 5),
    (53, "2 Thessalonians", "2 தெசலோனிக்கேயர்", 3),
    (54, "1 Timothy", "1 தீமோத்தேயு", 6),
    (55, "2 Timothy", "2 தீமோத்தேயு", 4),
    (56, "Titus", "தீத்து", 3),
    (57, "Philemon", "பிலேமோன்", 1),
    (58, "Hebrews", "எபிரெயர்", 13),
    (59, "James", "யாக்கோபு", 5),
    (60, "1 Peter", "1 பேதுரு", 5),
    (61, "2 Peter", "2 பேதுரு", 3),
    (62, "1 John", "1 யோவான்", 5),
    (63, "2 John", "2 யோவான்", 1),
    (64, "3 John", "3 யோவான்", 1),
    (65, "Jude", "யூதா", 1),
    (66, "Revelation", "வெளிப்படுத்தின விசேஷம்", 22),
]

BOOK_MAP = {
    b[0]: {
        "id": b[0],
        "name_en": b[1],
        "name_ta": b[2],
        "total_chapters": b[3]
    }
    for b in BIBLE_BOOKS
}


def _resolve_schema(cursor: sqlite3.Cursor):
    """Detects table and column arrangements."""
    tables = [
        r[0] for r in cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';"
        ).fetchall()
    ]

    single_candidates = ["verses", "bible", "scripture", "tamil_english", "bilingual"]
    matched_single = next((t for t in tables if t.lower() in single_candidates), None)
    if not matched_single and len(tables) == 1:
        matched_single = tables[0]

    if matched_single:
        cols = [c[1] for c in cursor.execute(f"PRAGMA table_info({matched_single})").fetchall()]
        cols_l = [c.lower() for c in cols]
        
        b_col = cols[cols_l.index(next(c for c in ["book_id", "book", "b", "book_number"] if c in cols_l))]
        c_col = cols[cols_l.index(next(c for c in ["chapter", "c", "chapter_number"] if c in cols_l))]
        v_col = cols[cols_l.index(next(c for c in ["verse", "v", "verse_number"] if c in cols_l))]
        
        ta_col_match = next((c for c in ["text_ta", "tamil", "verse_ta", "word_ta", "tamil_text", "ta"] if c in cols_l), None)
        en_col_match = next((c for c in ["text_en", "english", "verse_en", "word_en", "kjv", "web", "en"] if c in cols_l), None)

        if ta_col_match and en_col_match:
            return {
                "type": "single",
                "table": matched_single,
                "book": b_col,
                "chapter": c_col,
                "verse": v_col,
                "text_ta": cols[cols_l.index(ta_col_match)],
                "text_en": cols[cols_l.index(en_col_match)]
            }

    ta_table = next((t for t in tables if any(k in t.lower() for k in ["tam", "_ta", "tamil"])), tables[0])
    en_table = next((t for t in tables if any(k in t.lower() for k in ["eng", "_en", "kjv", "web"])), tables[-1])

    ta_cols = [c[1] for c in cursor.execute(f"PRAGMA table_info({ta_table})").fetchall()]
    en_cols = [c[1] for c in cursor.execute(f"PRAGMA table_info({en_table})").fetchall()]

    ta_cols_l = [c.lower() for c in ta_cols]
    en_cols_l = [c.lower() for c in en_cols]

    return {
        "type": "dual",
        "table_ta": ta_table,
        "table_en": en_table,
        "book": ta_cols[ta_cols_l.index(next(c for c in ["book_id", "book", "b"] if c in ta_cols_l))],
        "chapter": ta_cols[ta_cols_l.index(next(c for c in ["chapter", "c"] if c in ta_cols_l))],
        "verse": ta_cols[ta_cols_l.index(next(c for c in ["verse", "v"] if c in ta_cols_l))],
        "text_ta": ta_cols[ta_cols_l.index(next(c for c in ["text", "verse_text", "words"] if c in ta_cols_l))],
        "text_en": en_cols[en_cols_l.index(next(c for c in ["text", "verse_text", "words"] if c in en_cols_l))]
    }


def get_chapter_verses(book_id: int, chapter: int) -> List[Dict]:
    with get_connection() as conn:
        cursor = conn.cursor()
        schema = _resolve_schema(cursor)

        if schema["type"] == "single":
            sql = f"""
                SELECT {schema['verse']} AS verse,
                       {schema['text_en']} AS text_en,
                       {schema['text_ta']} AS text_ta
                FROM {schema['table']}
                WHERE {schema['book']} = ? AND {schema['chapter']} = ?
                ORDER BY {schema['verse']} ASC
            """
            rows = cursor.execute(sql, (book_id, chapter)).fetchall()
        else:
            sql = f"""
                SELECT e.{schema['verse']} AS verse,
                       e.{schema['text_en']} AS text_en,
                       t.{schema['text_ta']} AS text_ta
                FROM {schema['table_en']} e
                JOIN {schema['table_ta']} t 
                  ON e.{schema['book']} = t.{schema['book']}
                 AND e.{schema['chapter']} = t.{schema['chapter']}
                 AND e.{schema['verse']} = t.{schema['verse']}
                WHERE e.{schema['book']} = ? AND e.{schema['chapter']} = ?
                ORDER BY e.{schema['verse']} ASC
            """
            rows = cursor.execute(sql, (book_id, chapter)).fetchall()

        return [
            {
                "verse": row["verse"],
                "text_en": row["text_en"] or "",
                "text_ta": row["text_ta"] or ""
            }
            for row in rows
        ]


def search_verses(query_str: str, limit: int = 60) -> List[Dict]:
    with get_connection() as conn:
        cursor = conn.cursor()
        schema = _resolve_schema(cursor)
        pattern = f"%{query_str.strip()}%"

        if schema["type"] == "single":
            sql = f"""
                SELECT {schema['book']} AS book_id,
                       {schema['chapter']} AS chapter,
                       {schema['verse']} AS verse,
                       {schema['text_en']} AS text_en,
                       {schema['text_ta']} AS text_ta
                FROM {schema['table']}
                WHERE {schema['text_en']} LIKE ? OR {schema['text_ta']} LIKE ?
                ORDER BY {schema['book']}, {schema['chapter']}, {schema['verse']}
                LIMIT ?
            """
            rows = cursor.execute(sql, (pattern, pattern, limit)).fetchall()
        else:
            sql = f"""
                SELECT e.{schema['book']} AS book_id,
                       e.{schema['chapter']} AS chapter,
                       e.{schema['verse']} AS verse,
                       e.{schema['text_en']} AS text_en,
                       t.{schema['text_ta']} AS text_ta
                FROM {schema['table_en']} e
                JOIN {schema['table_ta']} t 
                  ON e.{schema['book']} = t.{schema['book']}
                 AND e.{schema['chapter']} = t.{schema['chapter']}
                 AND e.{schema['verse']} = t.{schema['verse']}
                WHERE e.{schema['text_en']} LIKE ? OR t.{schema['text_ta']} LIKE ?
                ORDER BY e.{schema['book']}, e.{schema['chapter']}, e.{schema['verse']}
                LIMIT ?
            """
            rows = cursor.execute(sql, (pattern, pattern, limit)).fetchall()

        results = []
        for r in rows:
            b_info = BOOK_MAP.get(r["book_id"], {"name_en": f"Book {r['book_id']}", "name_ta": ""})
            results.append({
                "book_id": r["book_id"],
                "book_name_en": b_info["name_en"],
                "book_name_ta": b_info["name_ta"],
                "chapter": r["chapter"],
                "verse": r["verse"],
                "text_en": r["text_en"] or "",
                "text_ta": r["text_ta"] or ""
            })
        return results
