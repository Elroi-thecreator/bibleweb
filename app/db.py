import os
import sqlite3
from typing import Dict, List

# Absolute cross-platform path resolution
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "data", "bible.sqlite.db")
DB_PATH = os.getenv("DATABASE_PATH", DEFAULT_DB_PATH)


def get_connection():
    """Returns a connection, raising a clear diagnostic error if the DB file was omitted."""
    abs_path = os.path.abspath(DB_PATH)
    if not os.path.exists(abs_path):
        data_dir = os.path.join(BASE_DIR, "data")
        files_in_data = os.listdir(data_dir) if os.path.exists(data_dir) else "FOLDER NOT FOUND"
        files_in_root = os.listdir(BASE_DIR)
        raise FileNotFoundError(
            f"DB file not found at: '{abs_path}'\n"
            f"Files in root: {files_in_root}\n"
            f"Files in data/: {files_in_data}"
        )

    conn = sqlite3.connect(abs_path)
    conn.row_factory = sqlite3.Row
    return conn


# 66 Canon Books Metadata (ID, English Name, Protestant BSI Tamil Name, Chapter Count)
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

# 7 Catholic Deuterocanonical Books (73-Book Canon)
DEUTEROCANONICAL_BOOKS = [
    (67, "Tobit", "தோபித்து", 14),
    (68, "Judith", "யூதித்து", 16),
    (69, "Wisdom of Solomon", "சாலமோனின் ஞானம்", 19),
    (70, "Sirach", "சீராக் (சீராக்கின் ஞானம்)", 51),
    (71, "Baruch", "பாரூக்கு", 6),
    (72, "1 Maccabees", "1 மக்கபேயர்", 16),
    (73, "2 Maccabees", "2 மக்கபேயர்", 15),
]

# All 73 Catholic Books with Authentic Catholic POC (திருவிவிலியம்) Tamil Names
CATHOLIC_BOOKS = [
    (1, "Genesis", "தொடக்க நூல்", 50),
    (2, "Exodus", "விடுதலைப் பயணம்", 40),
    (3, "Leviticus", "லேவியர்", 27),
    (4, "Numbers", "எண்ணிக்கை", 36),
    (5, "Deuteronomy", "இணைச் சட்டம்", 34),
    (6, "Joshua", "யோசுவா", 24),
    (7, "Judges", "நீதித் தலைவர்கள்", 21),
    (8, "Ruth", "ரூத்து", 4),
    (9, "1 Samuel", "1 சாமுவேல்", 31),
    (10, "2 Samuel", "2 சாமுவேல்", 24),
    (11, "1 Kings", "1 அரசர்கள்", 22),
    (12, "2 Kings", "2 அரசர்கள்", 25),
    (13, "1 Chronicles", "1 குறிப்பேடு", 29),
    (14, "2 Chronicles", "2 குறிப்பேடு", 36),
    (15, "Ezra", "எஸ்ரா", 10),
    (16, "Nehemiah", "நெகேமியா", 13),
    (17, "Esther", "எஸ்தர்", 10),
    (18, "Job", "யோபு", 42),
    (19, "Psalms", "திருப்பாடல்கள்", 150),
    (20, "Proverbs", "நீதிமொழிகள்", 31),
    (21, "Ecclesiastes", "சபை உரையாளர்", 12),
    (22, "Song of Solomon", "இனிமைமிகு பாடல்", 8),
    (23, "Isaiah", "எசாயா", 66),
    (24, "Jeremiah", "எரேமியா", 52),
    (25, "Lamentations", "புலம்பல்", 5),
    (26, "Ezekiel", "எசேக்கியேல்", 48),
    (27, "Daniel", "தானியேல்", 12),
    (28, "Hosea", "ஒசேயா", 14),
    (29, "Joel", "யோவேல்", 3),
    (30, "Amos", "ஆமோஸ்", 9),
    (31, "Obadiah", "ஒபதியா", 1),
    (32, "Jonah", "யோனா", 4),
    (33, "Micah", "மீக்கா", 7),
    (34, "Nahum", "நாகூம்", 3),
    (35, "Habakkuk", "அபக்கூக்கு", 3),
    (36, "Zephaniah", "செப்பனியா", 3),
    (37, "Haggai", "ஆகாய்", 2),
    (38, "Zechariah", "செக்கரியா", 14),
    (39, "Malachi", "மலாக்கி", 4),
    (40, "Matthew", "மத்தேயு", 28),
    (41, "Mark", "மாற்கு", 16),
    (42, "Luke", "லூக்கா", 24),
    (43, "John", "யோவான்", 21),
    (44, "Acts", "திருத்தூதர் பணிகள்", 28),
    (45, "Romans", "உரோமையர்", 16),
    (46, "1 Corinthians", "1 கொரிந்தியர்", 16),
    (47, "2 Corinthians", "2 கொரிந்தியர்", 13),
    (48, "Galatians", "கலாத்தியர்", 6),
    (49, "Ephesians", "எபேசியர்", 6),
    (50, "Philippians", "பிலிப்பியர்", 4),
    (51, "Colossians", "கொலோசையர்", 4),
    (52, "1 Thessalonians", "1 தெசலோனிக்கர்", 5),
    (53, "2 Thessalonians", "2 தெசலோனிக்கர்", 3),
    (54, "1 Timothy", "1 திமொத்தேயு", 6),
    (55, "2 Timothy", "2 திமொத்தேயு", 4),
    (56, "Titus", "தீத்து", 3),
    (57, "Philemon", "பிலமோன்", 1),
    (58, "Hebrews", "எபிரேயர்", 13),
    (59, "James", "யாக்கோபு", 5),
    (60, "1 Peter", "1 பேதுரு", 5),
    (61, "2 Peter", "2 பேதுரு", 3),
    (62, "1 John", "1 யோவான்", 5),
    (63, "2 John", "2 யோவான்", 1),
    (64, "3 John", "3 யோவான்", 1),
    (65, "Jude", "யூதா", 1),
    (66, "Revelation", "திருவெளிப்பாடு", 22),
    (67, "Tobit", "தோபித்து", 14),
    (68, "Judith", "யூதித்து", 16),
    (69, "Wisdom of Solomon", "சாலமோனின் ஞானம்", 19),
    (70, "Sirach", "சீராக் (சீராக்கின் ஞானம்)", 51),
    (71, "Baruch", "பாரூக்கு", 6),
    (72, "1 Maccabees", "1 மக்கபேயர்", 16),
    (73, "2 Maccabees", "2 மக்கபேயர்", 15),
]

# Standard Protestant Book Map (with Deuterocanon fallback)
BOOK_MAP = {
    b[0]: {
        "id": b[0],
        "name_en": b[1],
        "name_ta": b[2],
        "total_chapters": b[3]
    }
    for b in (BIBLE_BOOKS + DEUTEROCANONICAL_BOOKS)
}

# Authentic Catholic Book Map (POC திருவிவிலியம்)
CATHOLIC_BOOK_MAP = {
    b[0]: {
        "id": b[0],
        "name_en": b[1],
        "name_ta": b[2],
        "total_chapters": b[3]
    }
    for b in CATHOLIC_BOOKS
}


def get_books(canon: str = "protestant") -> List:
    """Returns list of books based on canon preference."""
    if canon and str(canon).lower() == "catholic":
        return CATHOLIC_BOOKS
    return BIBLE_BOOKS


def get_book_map(canon: str = "protestant") -> Dict:
    """Returns book map based on canon preference."""
    if canon and str(canon).lower() == "catholic":
        return CATHOLIC_BOOK_MAP
    return BOOK_MAP


def get_book_info(book_id: int, canon: str = "protestant") -> Dict:
    """Returns metadata dictionary for a book according to active canon."""
    bmap = get_book_map(canon)
    if book_id in bmap:
        return bmap[book_id]
    return BOOK_MAP.get(book_id, {"id": book_id, "name_en": f"Book {book_id}", "name_ta": "", "total_chapters": 1})


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

        has_poc = "text_ta_poc" in cols_l
        has_drb = "text_en_drb" in cols_l

        if ta_col_match and en_col_match:
            return {
                "type": "single",
                "table": matched_single,
                "book": b_col,
                "chapter": c_col,
                "verse": v_col,
                "text_ta": cols[cols_l.index(ta_col_match)],
                "text_en": cols[cols_l.index(en_col_match)],
                "has_poc": has_poc,
                "has_drb": has_drb,
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
        "text_en": en_cols[en_cols_l.index(next(c for c in ["text", "verse_text", "words"] if c in en_cols_l))],
        "has_poc": False,
        "has_drb": False,
    }


def group_merged_verses(verses: List[Dict]) -> List[Dict]:
    """Groups consecutive verses that share a combined dynamic-equivalence range in Tamil (e.g. [1-2])."""
    if not verses:
        return []

    import re
    grouped = []
    i = 0
    n = len(verses)

    while i < n:
        curr = verses[i]
        ta_text = curr.get("text_ta", "").strip()
        m = re.match(r"^\[(\d+)-(\d+)\]", ta_text)

        if m:
            range_start = int(m.group(1))
            range_end = int(m.group(2))

            if range_start <= curr["verse"] <= range_end:
                group_members = [curr]
                j = i + 1
                while j < n:
                    nxt = verses[j]
                    nxt_ta = nxt.get("text_ta", "").strip()
                    if nxt_ta == ta_text and nxt["verse"] <= range_end:
                        group_members.append(nxt)
                        j += 1
                    else:
                        break

                verse_span = f"{range_start}-{range_end}"
                combined_en_parts = []
                for g in group_members:
                    en_part = g.get("text_en", "").strip()
                    if en_part:
                        combined_en_parts.append(f"[{g['verse']}] {en_part}")
                combined_en = " ".join(combined_en_parts) if combined_en_parts else curr.get("text_en", "")

                grouped.append({
                    "verse": curr["verse"],
                    "verse_display": verse_span,
                    "verse_start": range_start,
                    "verse_end": range_end,
                    "verse_list": [g["verse"] for g in group_members],
                    "text_en": combined_en,
                    "text_ta": curr.get("text_ta", ""),
                })
                i = j
                continue

        # Normal single verse
        grouped.append({
            "verse": curr["verse"],
            "verse_display": str(curr["verse"]),
            "verse_start": curr["verse"],
            "verse_end": curr["verse"],
            "verse_list": [curr["verse"]],
            "text_en": curr.get("text_en", ""),
            "text_ta": curr.get("text_ta", ""),
        })
        i += 1

    return grouped


def get_chapter_verses(book_id: int, chapter: int, canon: str = "protestant", group_merged: bool = True) -> List[Dict]:
    """Retrieves all verses for a given book and chapter based on canon (Protestant or Catholic), optionally grouping merged thought units."""
    with get_connection() as conn:
        cursor = conn.cursor()
        schema = _resolve_schema(cursor)
        is_catholic = (canon and str(canon).lower() == "catholic")

        if schema["type"] == "single":
            if is_catholic and schema.get("has_poc"):
                sql = f"""
                    SELECT {schema['verse']} AS verse,
                           COALESCE(NULLIF(text_en_drb, ''), {schema['text_en']}) AS text_en,
                           COALESCE(NULLIF(text_ta_poc, ''), {schema['text_ta']}) AS text_ta
                    FROM {schema['table']}
                    WHERE {schema['book']} = ? AND {schema['chapter']} = ?
                    ORDER BY {schema['verse']} ASC
                """
            else:
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

        raw_verses = [
            {
                "verse": row["verse"],
                "text_en": row["text_en"] or "",
                "text_ta": row["text_ta"] or ""
            }
            for row in rows
        ]

        if group_merged and is_catholic:
            return group_merged_verses(raw_verses)

        # Standard representation for unmerged / Protestant
        return [
            {
                "verse": v["verse"],
                "verse_display": str(v["verse"]),
                "verse_start": v["verse"],
                "verse_end": v["verse"],
                "verse_list": [v["verse"]],
                "text_en": v["text_en"],
                "text_ta": v["text_ta"],
            }
            for v in raw_verses
        ]


def search_verses(query_str: str, canon: str = "protestant", limit: int = 60) -> List[Dict]:
    """Performs full-text search across active translation corpora, collapsing merged verse duplicates."""
    import re
    with get_connection() as conn:
        cursor = conn.cursor()
        schema = _resolve_schema(cursor)
        pattern = f"%{query_str.strip()}%"
        is_catholic = (canon and str(canon).lower() == "catholic")
        book_map = CATHOLIC_BOOK_MAP if is_catholic else BOOK_MAP

        if schema["type"] == "single":
            if is_catholic and schema.get("has_poc"):
                sql = f"""
                    SELECT {schema['book']} AS book_id,
                           {schema['chapter']} AS chapter,
                           {schema['verse']} AS verse,
                           COALESCE(NULLIF(text_en_drb, ''), {schema['text_en']}) AS text_en,
                           COALESCE(NULLIF(text_ta_poc, ''), {schema['text_ta']}) AS text_ta
                    FROM {schema['table']}
                    WHERE (COALESCE(NULLIF(text_en_drb, ''), {schema['text_en']}) LIKE ? 
                           OR COALESCE(NULLIF(text_ta_poc, ''), {schema['text_ta']}) LIKE ?)
                    ORDER BY {schema['book']}, {schema['chapter']}, {schema['verse']}
                    LIMIT ?
                """
            else:
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
        seen_ranges = set()

        for r in rows:
            book_id = r["book_id"]
            chapter = r["chapter"]
            verse = r["verse"]
            text_en = r["text_en"] or ""
            text_ta = r["text_ta"] or ""

            # Check if this hit is part of a merged unit
            m = re.match(r"^\[(\d+)-(\d+)\]", text_ta.strip())
            if m and is_catholic:
                r_start, r_end = int(m.group(1)), int(m.group(2))
                range_key = (book_id, chapter, r_start, r_end)
                if range_key in seen_ranges:
                    continue
                seen_ranges.add(range_key)
                verse_display = f"{r_start}-{r_end}"
            else:
                verse_display = str(verse)

            b_info = book_map.get(book_id, {"name_en": f"Book {book_id}", "name_ta": ""})
            results.append({
                "book_id": book_id,
                "book_name_en": b_info["name_en"],
                "book_name_ta": b_info["name_ta"],
                "chapter": chapter,
                "verse": verse,
                "verse_display": verse_display,
                "text_en": text_en,
                "text_ta": text_ta
            })
        return results