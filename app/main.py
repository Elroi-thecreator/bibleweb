import os
import sqlite3
import io
from typing import Optional
from fastapi import FastAPI, Request, Query, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from gtts import gTTS

app = FastAPI(title="Holy Bible | பரிசுத்த வேதாகமம்")

# Static assets & Jinja2 template setup
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

DB_PATH = os.path.join(os.path.dirname(__file__), "bible.db")


def get_db_connection():
    """Establishes an SQLite connection with optimized read concurrency."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# =====================================================================
# 1. Verification & PWA Offline Routes
# =====================================================================
@app.get("/google032292dfbea249aa.html", response_class=PlainTextResponse)
async def google_verification():
    """Google Search Console site verification token."""
    return "google-site-verification: google032292dfbea249aa.html"


@app.get("/sw.js")
async def service_worker():
    """Serves service worker from the root to ensure full application scope."""
    sw_path = os.path.join(os.path.dirname(__file__), "static", "sw.js")
    if os.path.exists(sw_path):
        with open(sw_path, "r", encoding="utf-8") as f:
            content = f.read()
        return HTMLResponse(content=content, media_type="application/javascript")
    raise HTTPException(status_code=404, detail="Service worker file not found")


# =====================================================================
# 2. Main View & Navigation Routes
# =====================================================================
@app.get("/", response_class=HTMLResponse)
async def home_index(request: Request):
    """Renders the canonical bookshelf and quick navigation dashboard."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Load canonical books partitioned by testament
    cursor.execute("""
        SELECT id, name_en, name_ta, total_chapters, testament 
        FROM books 
        ORDER BY id ASC
    """)
    books = [tuple(row) for row in cursor.fetchall()]
    conn.close()

    ot_books = [b for b in books if b[4] == "OT" or b[0] <= 39]
    nt_books = [b for b in books if b[4] == "NT" or b[0] > 39]

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "ot_books": ot_books,
            "nt_books": nt_books,
            "all_books": books,
        },
    )


@app.get("/read/{book_id}/{chapter}", response_class=HTMLResponse)
async def read_chapter(
    request: Request,
    book_id: int,
    chapter: int,
    mode: str = Query("bilingual", regex="^(bilingual|tamil|english)$"),
):
    """
    Renders scripture text with parallel bilingual verses,
    matching the context keys expected by reader.html / read.html.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Retrieve selected book
    cursor.execute(
        "SELECT id, name_en, name_ta, total_chapters FROM books WHERE id = ?",
        (book_id,),
    )
    book_row = cursor.fetchone()
    if not book_row:
        conn.close()
        raise HTTPException(status_code=404, detail="Book not found")

    book = tuple(book_row)
    total_chapters = book[3]

    if chapter < 1 or chapter > total_chapters:
        conn.close()
        raise HTTPException(status_code=404, detail="Chapter out of bounds")

    # Retrieve all books for dropdown selector
    cursor.execute(
        "SELECT id, name_en, name_ta, total_chapters FROM books ORDER BY id ASC"
    )
    all_books = [tuple(r) for r in cursor.fetchall()]

    # Retrieve verses for this chapter
    cursor.execute(
        """
        SELECT verse, text_en, text_ta 
        FROM verses 
        WHERE book_id = ? AND chapter = ? 
        ORDER BY verse ASC
        """,
        (book_id, chapter),
    )
    verses = [tuple(r) for r in cursor.fetchall()]
    conn.close()

    # Chooses between 'reader.html' or 'read.html' depending on naming
    template_name = (
        "reader.html"
        if os.path.exists(os.path.join("templates", "reader.html"))
        else "read.html"
    )

    return templates.TemplateResponse(
        template_name,
        {
            "request": request,
            "book": book,
            "chapter": int(chapter),
            "total_chapters": total_chapters,
            "all_books": all_books,
            "verses": verses,
            "mode": mode,
        },
    )


@app.get("/progress", response_class=HTMLResponse)
async def reading_progress(request: Request):
    """Displays user reading progress, canonical breakdown, and chapter matrix."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, name_en, name_ta, total_chapters, testament 
        FROM books 
        ORDER BY id ASC
    """)
    books = [tuple(row) for row in cursor.fetchall()]
    conn.close()

    ot_books = [b for b in books if b[4] == "OT" or b[0] <= 39]
    nt_books = [b for b in books if b[4] == "NT" or b[0] > 39]

    return templates.TemplateResponse(
        "progress.html",
        {
            "request": request,
            "ot_books": ot_books,
            "nt_books": nt_books,
            "all_books": books,
        },
    )


@app.get("/plans", response_class=HTMLResponse)
async def reading_plans(request: Request):
    """Renders daily structured reading habits (e.g., 365-day, New Testament in 90 days)."""
    return templates.TemplateResponse("plans.html", {"request": request})


@app.get("/bookmarks", response_class=HTMLResponse)
async def saved_bookmarks(request: Request):
    """Renders client-side saved bookmarks and highlights screen."""
    return templates.TemplateResponse("bookmarks.html", {"request": request})


@app.get("/search", response_class=HTMLResponse)
async def search_verses(
    request: Request,
    q: Optional[str] = Query(None),
    limit: int = Query(50, le=100),
):
    """Performs full-text search across Tamil and English scripture verses."""
    results = []
    search_query = q.strip() if q else ""

    if search_query:
        conn = get_db_connection()
        cursor = conn.cursor()
        query_pattern = f"%{search_query}%"

        cursor.execute(
            """
            SELECT v.book_id, b.name_en, b.name_ta, v.chapter, v.verse, v.text_en, v.text_ta
            FROM verses v
            JOIN books b ON v.book_id = b.id
            WHERE v.text_en LIKE ? OR v.text_ta LIKE ?
            ORDER BY v.book_id ASC, v.chapter ASC, v.verse ASC
            LIMIT ?
            """,
            (query_pattern, query_pattern, limit),
        )
        results = [tuple(r) for r in cursor.fetchall()]
        conn.close()

    return templates.TemplateResponse(
        "search.html",
        {
            "request": request,
            "query": search_query,
            "results": results,
            "count": len(results),
        },
    )

# =====================================================================
# 3. Read along 
# =====================================================================
@app.get("/plans/read-along/{plan_id}/{day}")
async def read_along_player(request: Request, plan_id: str, day: int):
    json_path = f"static/plans/{plan_id}.json"
    if not os.path.exists(json_path):
        raise HTTPException(status_code=404, detail="Reading plan not found")
        
    with open(json_path, "r", encoding="utf-8") as f:
        plan_data = json.load(f)

    day_entry = next((d for d in plan_data["days"] if d["day"] == day), None)
    if not day_entry:
        raise HTTPException(status_code=404, detail="Day not found in plan")

    # Fetch verses for all chapters scheduled for this day
    conn = get_db_connection()
    cur = conn.cursor()
    
    loaded_chapters = []
    for ch in day_entry["chapters"]:
        cur.execute("""
            SELECT v.verse, v.text_ta, v.text_en, b.name_ta, b.name_en, b.id, v.chapter
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
                "book_name_en": verses[0]["name_en"],
                "verses": [dict(v) for v in verses]
            })
    conn.close()

    return templates.TemplateResponse("read_along.html", {
        "request": request,
        "plan": plan_data,
        "day": day_entry,
        "chapters": loaded_chapters
    })
# =====================================================================
# 4. Audio Streaming API (gTTS)
# =====================================================================
@app.get("/api/audio/stream")
async def stream_chapter_audio(
    book_id: int = Query(...),
    chapter: int = Query(...),
    lang: str = Query("ta", regex="^(ta|en)$"),
):
    """
    Synthesizes and streams chapter audio using server-side gTTS.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    text_column = "text_ta" if lang == "ta" else "text_en"
    cursor.execute(
        f"SELECT {text_column} FROM verses WHERE book_id = ? AND chapter = ? ORDER BY verse ASC",
        (book_id, chapter),
    )
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        raise HTTPException(
            status_code=404, detail="Verses not found for audio synthesis"
        )

    # Combine chapter verses into fluent speech text
    chapter_text = " ".join([r[0] for r in rows if r[0]])
    if not chapter_text.strip():
        raise HTTPException(status_code=400, detail="Empty text for audio synthesis")

    try:
        mp3_fp = io.BytesIO()
        tts = gTTS(text=chapter_text, lang=lang, slow=False)
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)

        return StreamingResponse(
            mp3_fp,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": f"inline; filename=bible_{book_id}_{chapter}_{lang}.mp3",
                "Cache-Control": "public, max-age=86400",
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audio synthesis error: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)