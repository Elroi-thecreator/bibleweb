import hashlib
import io
import platform
import time
from fastapi import FastAPI, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from gtts import gTTS

from app.db import BIBLE_BOOKS, BOOK_MAP, get_chapter_verses, search_verses

app = FastAPI(title="Holy Bible - வேதம்")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

START_TIME = time.time()
AUDIO_CACHE = {}

DAILY_VERSE = {
    "ref_en": "John 3:16",
    "ref_ta": "யோவான் 3:16",
    "text_en": (
        "For God so loved the world, that he gave his only begotten Son, "
        "that whosoever believeth in him should not perish, but have everlasting life."
    ),
    "text_ta": (
        "தேவன், தம்முடைய ஒரேபேறான குமாரனை விசுவாசிக்கிறவன் எவனோ அவன் கெட்டுப்போகாமல் "
        "நித்தியஜீவனை அடையும்படிக்கு, அவரைத் தந்தருளி, இவ்வளவாய் உலகத்தில் அன்புகூர்ந்தார்."
    ),
    "link": "/read/43/1?mode=bilingual",
}


# ==========================================
# 1. Server-Side Audio Streaming Engine (gTTS)
# ==========================================

@app.get("/api/audio/stream")
async def stream_audio(text: str = Query(..., min_length=1), lang: str = Query("ta")):
    """Generates and streams high-clarity MP3 audio for Tamil or English.

    Bypasses missing offline OS voice packs completely.
    """
    clean_text = text.strip()
    target_lang = "ta" if lang == "ta" else "en"
    cache_key = hashlib.md5(f"{target_lang}:{clean_text}".encode("utf-8")).hexdigest()

    if cache_key in AUDIO_CACHE:
        return Response(content=AUDIO_CACHE[cache_key], media_type="audio/mpeg")

    try:
        tts = gTTS(text=clean_text, lang=target_lang, slow=False)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        audio_bytes = fp.read()

        # Cache up to 300 verses in memory for rapid instant playback
        if len(AUDIO_CACHE) > 300:
            AUDIO_CACHE.pop(next(iter(AUDIO_CACHE)))
        AUDIO_CACHE[cache_key] = audio_bytes

        return Response(content=audio_bytes, media_type="audio/mpeg")
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


# ==========================================
# 2. Status & Health Endpoints (Zero-DB Touch)
# ==========================================

@app.get("/api/health")
async def api_health():
    """Lightweight JSON health check for Render and external uptime pingers."""
    uptime_sec = int(time.time() - START_TIME)
    return JSONResponse(
        content={
            "status": "ok",
            "uptime_seconds": uptime_sec,
            "version": "1.0.0",
        },
        status_code=200,
    )


@app.get("/status", response_class=HTMLResponse)
async def status_page():
    """Minimalist dark-mode system monitor card (< 1.5 KB, 0 external assets)."""
    uptime_sec = int(time.time() - START_TIME)
    hours, remainder = divmod(uptime_sec, 3600)
    minutes, seconds = divmod(remainder, 60)
    uptime_str = f"{hours}h {minutes}m {seconds}s"

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>System Status</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace;
            background: #0f172a;
            color: #e2e8f0;
            display: flex;
            align-items: center;
            justify-content: center;
            height: 100vh;
            margin: 0;
        }}
        .card {{
            background: #1e293b;
            border: 1px solid #334155;
            border-radius: 10px;
            padding: 24px;
            width: 320px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        }}
        .header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 16px;
            padding-bottom: 10px;
            border-bottom: 1px solid #334155;
        }}
        .pulse {{
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #22c55e;
            display: inline-block;
            margin-right: 6px;
        }}
        .badge {{
            font-size: 11px;
            font-weight: bold;
            color: #22c55e;
            background: rgba(34, 197, 94, 0.15);
            padding: 2px 8px;
            border-radius: 99px;
        }}
        .row {{
            display: flex;
            justify-content: space-between;
            font-size: 13px;
            padding: 6px 0;
        }}
        .label {{ color: #94a3b8; }}
        .val {{ font-weight: 600; font-family: monospace; }}
        .actions {{
            margin-top: 16px;
            display: flex;
            gap: 8px;
        }}
        .btn {{
            flex: 1;
            text-align: center;
            padding: 6px 0;
            font-size: 12px;
            color: #38bdf8;
            background: #0f172a;
            border: 1px solid #334155;
            border-radius: 6px;
            text-decoration: none;
        }}
        .btn:hover {{ background: #1e293b; border-color: #38bdf8; }}
    </style>
</head>
<body>
    <div class="card">
        <div class="header">
            <span style="font-weight: bold; font-size: 14px;"><span class="pulse"></span>Service Active</span>
            <span class="badge">ONLINE</span>
        </div>
        <div class="row">
            <span class="label">Uptime</span>
            <span class="val">{uptime_str}</span>
        </div>
        <div class="row">
            <span class="label">Audio Engine</span>
            <span class="val" style="color: #22c55e;">gTTS Server-Side</span>
        </div>
        <div class="row">
            <span class="label">Runtime</span>
            <span class="val">Python {platform.python_version()}</span>
        </div>
        <div class="row">
            <span class="label">Host</span>
            <span class="val">Render / Web</span>
        </div>
        <div class="actions">
            <a href="/api/health" class="btn" target="_blank">JSON</a>
            <a href="/" class="btn">Open Bible →</a>
        </div>
    </div>
</body>
</html>"""
    return HTMLResponse(content=html_content)


# ==========================================
# 3. Main Bible Pages
# ==========================================

@app.get("/", response_class=HTMLResponse)
async def landing_page(request: Request):
    """Editorial landing page with language gateways and book indexes."""
    return templates.TemplateResponse(
        request=request,
        name="landing.html",
        context={
            "books": BIBLE_BOOKS,
            "daily_verse": DAILY_VERSE,
            "ot_books": [b for b in BIBLE_BOOKS if b[0] <= 39],
            "nt_books": [b for b in BIBLE_BOOKS if b[0] > 39],
        },
    )


@app.get("/read/{book_id}/{chapter}", response_class=HTMLResponse)
async def reader(
    request: Request,
    book_id: int,
    chapter: int,
    mode: str = Query("bilingual"),
):
    """Reader interface with continuous audio narration, multi-mode views, and direct chapter selectors."""
    if book_id not in BOOK_MAP:
        book_id = 1
    current_book = BOOK_MAP[book_id]
    if chapter < 1 or chapter > current_book["total_chapters"]:
        chapter = 1

    verses = get_chapter_verses(book_id, chapter)
    prev_ch = chapter - 1 if chapter > 1 else None
    next_ch = chapter + 1 if chapter < current_book["total_chapters"] else None

    return templates.TemplateResponse(
        request=request,
        name="reader.html",
        context={
            "books": BIBLE_BOOKS,
            "book": current_book,
            "chapter": chapter,
            "verses": verses,
            "mode": mode,
            "prev_ch": prev_ch,
            "next_ch": next_ch,
            "ot_books": [b for b in BIBLE_BOOKS if b[0] <= 39],
            "nt_books": [b for b in BIBLE_BOOKS if b[0] > 39],
        },
    )


@app.get("/search", response_class=HTMLResponse)
async def search_page(request: Request, q: str = Query("", min_length=1)):
    """Case-insensitive bilingual full-text search."""
    results = search_verses(q) if q.strip() else []
    return templates.TemplateResponse(
        request=request,
        name="search.html",
        context={"query": q, "results": results, "books": BIBLE_BOOKS},
    )


@app.get("/bookmarks", response_class=HTMLResponse)
async def bookmarks_page(request: Request):
    """Client-side saved bookmarks view."""
    return templates.TemplateResponse(
        request=request,
        name="bookmarks.html",
        context={"books": BIBLE_BOOKS},
    )


@app.get("/book/{book_id}/chapter/{chapter}")
async def legacy_redirect(book_id: int, chapter: int):
    """Backward-compatible redirect for legacy book routes."""
    return RedirectResponse(url=f"/read/{book_id}/{chapter}?mode=bilingual")