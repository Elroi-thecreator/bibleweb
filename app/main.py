import hashlib
import io
import json
import os
import platform
import time
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import (
    FileResponse,
    HTMLResponse,
    JSONResponse,
    PlainTextResponse,
    RedirectResponse,
    Response,
)
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from gtts import gTTS

from app.db import BIBLE_BOOKS, BOOK_MAP, get_chapter_verses, search_verses
from app.plans_data import READING_PLANS

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
# 1. Google Site Verification & PWA
# ==========================================

@app.get("/google032292dfbea249aa.html", response_class=PlainTextResponse)
async def google_site_verification():
    """Serves the Google Search Console / OAuth domain verification token."""
    return "google-site-verification: google032292dfbea249aa.html"


@app.get("/sw.js")
async def service_worker():
    """Serves the Service Worker at root scope so it can cache all application paths."""
    return FileResponse("static/sw.js", media_type="application/javascript")


# ==========================================
# 2. Audio Streaming Engine (gTTS)
# ==========================================

@app.get("/api/audio/stream")
async def stream_audio(text: str = Query(..., min_length=1), lang: str = Query("ta")):
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

        if len(AUDIO_CACHE) > 300:
            AUDIO_CACHE.pop(next(iter(AUDIO_CACHE)))
        AUDIO_CACHE[cache_key] = audio_bytes

        return Response(content=audio_bytes, media_type="audio/mpeg")
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


# ==========================================
# 3. Status & Health (Zero-DB Touch)
# ==========================================

@app.get("/api/health")
async def api_health():
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
            <span class="val" style="color: #22c55e;">gTTS Streaming</span>
        </div>
        <div class="row">
            <span class="label">PWA / Offline</span>
            <span class="val" style="color: #38bdf8;">Service Worker Active</span>
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
# 4. Main Bible Pages
# ==========================================

@app.get("/", response_class=HTMLResponse)
async def landing_page(request: Request):
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
    if book_id not in BOOK_MAP:
        book_id = 1
    current_book = BOOK_MAP[book_id]
    if chapter < 1 or chapter > current_book["total_chapters"]:
        chapter = 1

    try:
        verses = get_chapter_verses(book_id, chapter) or []
    except Exception as e:
        print(f"Error fetching verses: {e}")
        verses = []

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


@app.get("/present/{book_id}/{chapter}", response_class=HTMLResponse)
async def presenter_mode(request: Request, book_id: int, chapter: int):
    """Church / TV / Projector presentation mode with extra-large bilingual slides."""
    if book_id not in BOOK_MAP:
        book_id = 1
    current_book = BOOK_MAP[book_id]
    if chapter < 1 or chapter > current_book["total_chapters"]:
        chapter = 1

    verses = get_chapter_verses(book_id, chapter)

    return templates.TemplateResponse(
        request=request,
        name="presenter.html",
        context={
            "books": BIBLE_BOOKS,
            "book": current_book,
            "chapter": chapter,
            "verses": verses,
        },
    )


@app.get("/plans", response_class=HTMLResponse)
async def plans_page(
    request: Request,
    completed_day: Optional[int] = None,
    plan_id: Optional[str] = None
):
    """Loads reading plans safely regardless of whether READING_PLANS is a list or dict."""
    all_plans = []

    # Safely convert READING_PLANS into a list of dicts
    if isinstance(READING_PLANS, dict):
        for pid, pdata in READING_PLANS.items():
            if isinstance(pdata, dict):
                p_copy = dict(pdata)
                p_copy.setdefault("id", pid)
                all_plans.append(p_copy)
            else:
                all_plans.append({"id": pid, "title": str(pdata), "title_en": str(pdata)})
    elif isinstance(READING_PLANS, list):
        for p in READING_PLANS:
            if isinstance(p, dict):
                all_plans.append(dict(p))
            else:
                all_plans.append({"id": str(p), "title": str(p), "title_en": str(p)})

    # Load 100-day read-along plans from static/plans/
    plans_dir = Path("static/plans")
    if plans_dir.exists():
        for file in sorted(plans_dir.glob("*.json")):
            try:
                with open(file, "r", encoding="utf-8") as f:
                    plan_json = json.load(f)
                    all_plans.append({
                        "id": plan_json.get("id", file.stem),
                        "title": plan_json.get("name_ta", file.stem),
                        "title_en": plan_json.get("name_en", file.stem),
                        "total_days": plan_json.get("total_days", len(plan_json.get("days", []))),
                        "total_words": plan_json.get("total_words", 0),
                        "is_read_along": True
                    })
            except Exception:
                continue

    return templates.TemplateResponse(
        request=request,
        name="plans.html",
        context={
            "plans": all_plans,
            "books": BIBLE_BOOKS,
            "completed_day": completed_day,
            "active_plan_id": plan_id
        },
    )


@app.get("/plans/read-along/{plan_id}/{day}", response_class=HTMLResponse)
async def read_along_player(request: Request, plan_id: str, day: int):
    """3-Phase Read Along: 5s Intro Screen -> Chapters Reading -> 5s Outro Blessing."""
    json_path = Path("static/plans") / f"{plan_id}.json"
    if not json_path.exists():
        raise HTTPException(status_code=404, detail="Plan file not found")

    with open(json_path, "r", encoding="utf-8") as f:
        plan_data = json.load(f)

    day_entry = next((d for d in plan_data.get("days", []) if d["day"] == day), None)
    if not day_entry:
        raise HTTPException(status_code=404, detail=f"Day {day} not found in this plan")

    loaded_chapters = []
    for ch in day_entry.get("chapters", []):
        b_id = ch["book_id"]
        c_num = ch["chapter"]
        book_meta = BOOK_MAP.get(b_id, {})
        verses = get_chapter_verses(b_id, c_num) or []

        loaded_chapters.append({
            "book_id": b_id,
            "chapter": c_num,
            "book_name_ta": book_meta.get("name_ta", f"Book {b_id}"),
            "book_name_en": book_meta.get("name_en", f"Book {b_id}"),
            "verses": verses
        })

    return templates.TemplateResponse(
        request=request,
        name="read_along.html",
        context={
            "plan": plan_data,
            "day": day_entry,
            "chapters": loaded_chapters,
            "books": BIBLE_BOOKS,
        }
    )


@app.get("/progress", response_class=HTMLResponse)
async def progress_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="progress.html",
        context={
            "books": BIBLE_BOOKS,
            "ot_books": [b for b in BIBLE_BOOKS if b[0] <= 39],
            "nt_books": [b for b in BIBLE_BOOKS if b[0] > 39],
            "total_chapters": 1189,
            "ot_chapters": 929,
            "nt_chapters": 260,
        },
    )


@app.get("/search", response_class=HTMLResponse)
async def search_page(request: Request, q: str = Query("", min_length=1)):
    results = search_verses(q) if q.strip() else []
    return templates.TemplateResponse(
        request=request,
        name="search.html",
        context={"query": q, "results": results, "books": BIBLE_BOOKS},
    )


@app.get("/bookmarks", response_class=HTMLResponse)
async def bookmarks_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="bookmarks.html",
        context={"books": BIBLE_BOOKS},
    )


@app.get("/book/{book_id}/chapter/{chapter}")
async def legacy_redirect(book_id: int, chapter: int):
    return RedirectResponse(url=f"/read/{book_id}/{chapter}?mode=bilingual")