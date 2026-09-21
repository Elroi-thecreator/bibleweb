import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Optional

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "bible.sqlite.db"


def get_db_connection():
    """Create and return a row-mapped SQLite connection."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def get_books() -> List[Dict[str, Any]]:
    """Retrieve list of books from the database."""
    if not DB_PATH.exists():
        return []
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Check if a dedicated 'books' table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='books'")
        if cursor.fetchone():
            cursor.execute("SELECT * FROM books ORDER BY id ASC")
            rows = cursor.fetchall()
            return [dict(r) for r in rows]

        # Fallback: Query distinct book names from verses
        cursor.execute("SELECT DISTINCT book FROM verses ORDER BY rowid ASC")
        rows = cursor.fetchall()
        return [{"name": r["book"]} for r in rows]
    except sqlite3.Error as e:
        print(f"DB Error in get_books: {e}")
        return []
    finally:
        conn.close()


def get_chapter_verses(book: str, chapter: int) -> List[Dict[str, Any]]:
    """Retrieve all verses for a given book and chapter number."""
    if not DB_PATH.exists():
        return []

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT verse, text 
            FROM verses 
            WHERE LOWER(book) = LOWER(?) AND chapter = ? 
            ORDER BY verse ASC
            """,
            (book, chapter)
        )
        rows = cursor.fetchall()
        return [{"verse": r["verse"], "text": r["text"]} for r in rows]
    except sqlite3.Error as e:
        print(f"DB Error in get_chapter_verses: {e}")
        return []
    finally:
        conn.close()


def search_verses(query: str, limit: int = 50) -> List[Dict[str, Any]]:
    """Search for verses matching a text query."""
    if not DB_PATH.exists() or not query.strip():
        return []

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        wildcard_query = f"%{query.strip()}%"
        cursor.execute(
            """
            SELECT book, chapter, verse, text 
            FROM verses 
            WHERE text LIKE ? 
            ORDER BY rowid ASC 
            LIMIT ?
            """,
            (wildcard_query, limit)
        )
        rows = cursor.fetchall()
        return [dict(r) for r in rows]
    except sqlite3.Error as e:
        print(f"DB Error in search_verses: {e}")
        return []
    finally:
        conn.close()


def get_verse_count_by_book() -> Dict[str, int]:
    """Retrieve count of verses per book."""
    if not DB_PATH.exists():
        return {}

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT book, COUNT(*) as count FROM verses GROUP BY book"
        )
        rows = cursor.fetchall()
        return {r["book"]: r["count"] for r in rows}
    except sqlite3.Error as e:
        print(f"DB Error in get_verse_count_by_book: {e}")
        return {}
    finally:
        conn.close()


# Backward-compatibility aliases
get_all_books = get_books
get_verses = get_chapter_verses
search = search_verses