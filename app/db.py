import os
import sqlite3
from typing import Dict, List, Optional

DB_PATH = os.getenv("DATABASE_PATH", "./data/bible.sqlite")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# 66 Canon Books Metadata (En + Ta) for clean navigation
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

BOOK_MAP = {b[0]: {"id": b[0], "name_en": b[1], "name_ta": b[2], "total_chapters": b[3]} for b in BIBLE_BOOKS}

def get_chapter_verses(book_id: int, chapter: int) -> List[Dict]:
    """
    Fetches verses matching book and chapter.
    Adapts to either single unified table or dual tables.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        tables = [r[0].lower() for r in cursor.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()]
        
        # Scenario 1: Single unified table named 'verses' or 'bible'
        target_table = "verses" if "verses" in tables else ("bible" if "bible" in tables else tables[0])
        cols = [c[1].lower() for c in cursor.execute(f"PRAGMA table_info({target_table})").fetchall()]

        b_col = next((c for c in cols if c in ["book_id", "book", "b", "book_number"]), "book_id")
        c_col = next((c for c in cols if c in ["chapter", "c", "chapter_number"]), "chapter")
        v_col = next((c for c in cols if c in ["verse", "v", "verse_number"]), "verse")
        ta_col = next((c for c in cols if c in ["text_ta", "tamil", "verse_ta", "word_ta", "tamil_text"]), None)
        en_col = next((c for c in cols if c in ["text_en", "english", "verse_en", "word_en", "kjv", "web"]), None)

        if ta_col and en_col:
            query = f"""
                SELECT {v_col} as verse, {en_col} as text_en, {ta_col} as text_ta 
                FROM {target_table}
                WHERE {b_col} = ? AND {c_col} = ?
                ORDER BY {v_col} ASC
            """
            rows = cursor.execute(query, (book_id, chapter)).fetchall()
            return [dict(r) for r in rows]

        # Scenario 2: Separate tables for English and Tamil
        ta_tbl = next((t for t in tables if "tam" in t or "_ta" in t), tables[0])
        en_tbl = next((t for t in tables if "eng" in t or "_en" in t or "kjv" in t), tables[1] if len(tables) > 1 else tables[0])

        query = f"""
            SELECT e.{v_col} as verse, e.text as text_en, t.text as text_ta
            FROM {en_tbl} e
            JOIN {ta_tbl} t ON e.{b_col} = t.{b_col} AND e.{c_col} = t.{c_col} AND e.{v_col} = t.{v_col}
            WHERE e.{b_col} = ? AND e.{c_col} = ?
            ORDER BY e.{v_col} ASC
        """
        rows = cursor.execute(query, (book_id, chapter)).fetchall()
        return [dict(r) for r in rows]

def search_verses(query_str: str, limit: int = 50) -> List[Dict]:
    """Case-insensitive bilingual search."""
    with get_connection() as conn:
        cursor = conn.cursor()
        tables = [r[0].lower() for r in cursor.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()]
        target_table = "verses" if "verses" in tables else ("bible" if "bible" in tables else tables[0])
        cols = [c[1].lower() for c in cursor.execute(f"PRAGMA table_info({target_table})").fetchall()]

        b_col = next((c for c in cols if c in ["book_id", "book", "b"]), "book_id")
        c_col = next((c for c in cols if c in ["chapter", "c"]), "chapter")
        v_col = next((c for c in cols if c in ["verse", "v"]), "verse")
        ta_col = next((c for c in cols if c in ["text_ta", "tamil", "verse_ta"]), "text_ta")
        en_col = next((c for c in cols if c in ["text_en", "english", "verse_en"]), "text_en")

        sql = f"""
            SELECT {b_col} as book_id, {c_col} as chapter, {v_col} as verse, 
                   {en_col} as text_en, {ta_col} as text_ta
            FROM {target_table}
            WHERE {en_col} LIKE ? OR {ta_col} LIKE ?
            LIMIT ?
        """
        q = f"%{query_str}%"
        rows = cursor.execute(sql, (q, q, limit)).fetchall()
        
        results = []
        for r in rows:
            b_info = BOOK_MAP.get(r["book_id"], {"name_en": f"Book {r['book_id']}", "name_ta": ""})
            results.append({
                "book_id": r["book_id"],
                "book_name_en": b_info["name_en"],
                "book_name_ta": b_info["name_ta"],
                "chapter": r["chapter"],
                "verse": r["verse"],
                "text_en": r["text_en"],
                "text_ta": r["text_ta"]
            })
        return results