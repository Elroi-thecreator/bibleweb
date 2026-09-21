import os
import json
import sqlite3
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Request, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# ---------------------------------------------------------------------------
# Directory Paths & App Setup
# ---------------------------------------------------------------------------
CURRENT_FILE_DIR = Path(__file__).resolve().parent          # app/
PROJECT_ROOT = CURRENT_FILE_DIR.parent                      # repository root

# Database Path Detection: points to data/bible.sqlite.db
DB_PATH = PROJECT_ROOT / "data" / "bible.sqlite.db"
if not DB_PATH.exists():
    alt_db = CURRENT_FILE_DIR / "data" / "bible.sqlite.db"
    if alt_db.exists():
        DB_PATH = alt_db

# Static & Template Directories
STATIC_DIR = PROJECT_ROOT / "static"
if not STATIC_DIR.exists():
    STATIC_DIR = CURRENT_FILE_DIR / "static"

TEMPLATES_DIR = PROJECT_ROOT / "templates"
if not TEMPLATES_DIR.exists():
    TEMPLATES_DIR = CURRENT_FILE_DIR / "templates"

app = FastAPI(title="Bilingual Holy Bible")

# Mount Static Files
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# ---------------------------------------------------------------------------
# Database Helper
# ---------------------------------------------------------------------------
def get_db_connection():
    if not DB_PATH.exists() or DB_PATH.stat().st_size == 0:
        raise FileNotFoundError(f"SQLite database not found or empty at {DB_PATH}")
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

# English book name fallback mapping (for schema with books: id, code, name_ta, testament)
BOOK_NAMES_EN = {
    1: "Genesis", 2: "Exodus", 3: "Leviticus", 4: "Numbers", 5: "Deuteronomy",
    6: "Joshua", 7: "Judges", 8: "Ruth", 9: "1 Samuel", 10: "2 Samuel",
    11: "1 Kings", 12: "2 Kings", 13: "1 Chronicles", 14: "2 Chronicles", 15: "Ezra",
    16: "Nehemiah", 17: "Esther", 18: "Job", 19: "Psalms", 20: "Proverbs",
    21: "Ecclesiastes", 22: "Song of Solomon", 23: "Isaiah", 24: "Jeremiah", 25: "Lamentations",
    26: "Ezekiel", 27: "Daniel", 28: "Hosea", 29: "Joel", 30: "Amos",
    31: "Obadiah", 32: "Jonah", 33: "Micah", 34: "Nahum", 35: "Habakkuk",
    36: "Zephaniah", 37: "Haggai", 38: "Zechariah", 39: "Malachi",
    40: "Matthew", 41: "Mark", 42: "Luke", 43: "John", 44: "Acts",
    45: "Romans", 46: "1 Corinthians", 47: "2 Corinthians", 48: "Galatians", 49: "Ephesians",
    50: "Philippians", 51: "Colossians", 52: "1 Thessalonians", 53: "2 Thessalonians", 54: "1 Timothy",
    55: "2 Timothy", 56: "Titus", 57: "Philemon", 58: "Hebrews", 59: "James",
    60: "1 Peter", 61: "2 Peter", 62: "1 John", 63: "2 John", 64: "3 John",
    65: "Jude", 66: "Revelation"
}

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
async def home_index(request: Request):
    """Home landing page listing books grouped by testament."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, code, name_ta, testament FROM books ORDER BY id ASC")
    raw_books = cur.fetchall()
    conn.close()

    books = []
    for b in raw_books:
        books.append({
            "id": b["id"],
            "code": b["code"],
            "name_ta": b["name_ta"],
            "name_en": BOOK_NAMES_EN.get(b["id"], b["code"]),
            "testament": b["testament"]
        })

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"books": books}
    )

@app.get("/read/{book_id}/{chapter}", response_class=HTMLResponse)
async def read_chapter(request: Request, book_id: int, chapter: int):
    """Chapter reader view targeting reader.html."""
    conn = get_db_connection()
    cur = conn.cursor()

    # Fetch book info
    cur.execute("SELECT id, code, name_ta, testament FROM books WHERE id = ?", (book_id,))
    book_row = cur.fetchone()
    if not book_row:
        conn.close()
        raise HTTPException(status_code=404, detail="Book not found")

    book = {
        "id": book_row["id"],
        "code": book_row["code"],
        "name_ta": book_row["name_ta"],
        "name_en": BOOK_NAMES_EN.get(book_row["id"], book_row["code"]),
        "testament": book_row["testament"]
    }

    # Fetch total chapters count for current book
    cur.execute("SELECT MAX(chapter) as total_chapters FROM verses WHERE book_id = ?", (book_id,))
    total_chapters_row = cur.fetchone()
    total_chapters = total_chapters_row["total_chapters"] if total_chapters_row else 1

    # Fetch verses
    cur.execute("""
        SELECT verse, text_ta, text_en
        FROM verses
        WHERE book_id = ? AND chapter = ?
        ORDER BY verse ASC
    """, (book_id, chapter))
    verses = [dict(v) for v in cur.fetchall()]
    conn.close()

    if not verses:
        raise HTTPException(status_code=404, detail="Chapter not found")

    return templates.TemplateResponse(
        request=request,
        name="reader.html",
        context={
            "book": book,
            "chapter": chapter,
            "total_chapters": total_chapters,
            "verses": verses
        }
    )

@app.get("/plans", response_class=HTMLResponse)
async def view_reading_plans(request: Request, completed_day: Optional[int] = None, plan_id: Optional[str] = None):
    """Reading plans overview page."""
    plans_dir = STATIC_DIR / "plans"
    available_plans = []

    if plans_dir.exists():
        for file in sorted(plans_dir.glob("*.json")):
            try:
                with open(file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    available_plans.append({
                        "id": data.get("id", file.stem),
                        "name_en": data.get("name_en", file.stem),
                        "name_ta": data.get("name_ta", file.stem),
                        "total_days": data.get("total_days", len(data.get("days", []))),
                        "total_words": data.get("total_words", 0)
                    })
            except Exception:
                continue

    return templates.TemplateResponse(
        request=request,
        name="plans.html",
        context={
            "plans": available_plans,
            "completed_day": completed_day,
            "active_plan_id": plan_id
        }
    )

@app.get("/plans/read-along/{plan_id}/{day}", response_class=HTMLResponse)
async def read_along_player(request: Request, plan_id: str, day: int):
    """Read-along player supporting 5s intro, stream, and 5s blessing outro."""
    json_file = STATIC_DIR / "plans" / f"{plan_id}.json"
    if not json_file.exists():
        raise HTTPException(status_code=404, detail="Plan file not found")

    with open(json_file, "r", encoding="utf-8") as f:
        plan_data = json.load(f)

    day_entry = next((d for d in plan_data.get("days", []) if d["day"] == day), None)
    if not day_entry:
        raise HTTPException(status_code=404, detail=f"Day {day} not found in this plan")

    conn = get_db_connection()
    cur = conn.cursor()

    loaded_chapters = []
    for ch in day_entry.get("chapters", []):
        cur.execute("""
            SELECT v.verse, v.text_ta, v.text_en, b.name_ta, b.code
            FROM verses v
            JOIN books b ON v.book_id = b.id
            WHERE v.book_id = ? AND v.chapter = ?
            ORDER BY v.verse ASC
        """, (ch["book_id"], ch["chapter"]))
        verses = cur.fetchall()

        if verses:
            loaded_chapters.append({
                "book_id": ch["book_id"],
                "chapter": ch["chapter"],
                "book_name_ta": verses[0]["name_ta"],
                "book_name_en": BOOK_NAMES_EN.get(ch["book_id"], verses[0]["code"]),
                "verses": [dict(v) for v in verses]
            })
    conn.close()

    return templates.TemplateResponse(
        request=request,
        name="read_along.html",
        context={
            "plan": plan_data,
            "day": day_entry,
            "chapters": loaded_chapters
        }
    )