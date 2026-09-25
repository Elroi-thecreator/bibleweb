import hashlib
import io
import json
from pathlib import Path
import platform
import random
import re
import time
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
try:
    import edge_tts
    HAS_EDGE_TTS = True
except ImportError:
    HAS_EDGE_TTS = False

from app.db import (
    BIBLE_BOOKS,
    DEUTEROCANONICAL_BOOKS,
    CATHOLIC_BOOKS,
    BOOK_MAP,
    CATHOLIC_BOOK_MAP,
    get_book_info,
    get_book_map,
    get_books,
    get_chapter_verses,
    search_verses,
)
from app.plans_data import READING_PLANS
from app.quiz_data import QUIZ_CATEGORIES, QUIZ_QUESTIONS

app = FastAPI(title="Holy Bible - வேதம்")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

START_TIME = time.time()
AUDIO_CACHE = {}

DAILY_VERSE_PROTESTANT = {
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
    "link": "/read/43/1?mode=bilingual&canon=protestant",
}

DAILY_VERSE_CATHOLIC = {
    "ref_en": "John 3:16",
    "ref_ta": "யோவான் 3:16",
    "text_en": (
        "For God so loved the world, as to give his only begotten Son; "
        "that whosoever believeth in him, may not perish, but may have life everlasting."
    ),
    "text_ta": (
        "தம் ஒரே மகன் மீது நம்பிக்கை கொள்ளும் எவரும் அழியாமல் நிலைவாழ்வு பெறும் பொருட்டு, "
        "கடவுள் உலகத்தின் மேல் அந்த அளவுக்கு அன்பு கூர்ந்தார்."
    ),
    "link": "/read/43/1?mode=bilingual&canon=catholic",
}

def get_daily_verse(canon: str = "protestant"):
    if canon and str(canon).lower() == "catholic":
        return DAILY_VERSE_CATHOLIC
    return DAILY_VERSE_PROTESTANT

DAILY_VERSE = DAILY_VERSE_PROTESTANT


# ==========================================
# 1. Google Site Verification Route
# ==========================================

@app.get("/google032292dfbea249aa.html", response_class=PlainTextResponse)
async def google_site_verification():
    """Serves the Google Search Console / OAuth domain verification token."""
    return "google-site-verification: google032292dfbea249aa.html"


# ==========================================
# 2. PWA Service Worker Route
# ==========================================

@app.get("/sw.js")
async def service_worker():
    """Serves the Service Worker at root scope so it can cache all application paths."""
    return FileResponse("static/sw.js", media_type="application/javascript")


# ==========================================
# 3. Audio Streaming Engine (Microsoft Neural Edge-TTS + gTTS Fallback)
# ==========================================

VOICE_CONFIG = {
    "ta": {
        "default": "ta-IN-ValluvarNeural",
        "male": "ta-IN-ValluvarNeural",
        "valluvar": "ta-IN-ValluvarNeural",
        "female": "ta-IN-PallaviNeural",
        "pallavi": "ta-IN-PallaviNeural",
    },
    "en": {
        "default": "en-US-JennyNeural",
        "female": "en-US-JennyNeural",
        "jenny": "en-US-JennyNeural",
        "male": "en-US-GuyNeural",
        "guy": "en-US-GuyNeural",
        "neerja": "en-IN-NeerjaNeural",
    },
}


def normalize_speech_rate(raw_rate: str) -> str:
    """Normalizes playback rates for scripture reading into Edge-TTS rate string."""
    if not raw_rate:
        return "-4%"
    rate_str = str(raw_rate).strip()
    if rate_str.endswith("%"):
        return rate_str
    try:
        val = float(rate_str)
        # Slower by 4% relative to 1.0 for solemn scripture meditation
        pct_diff = int(round((val - 1.0) * 100)) - 4
        return f"+{pct_diff}%" if pct_diff >= 0 else f"{pct_diff}%"
    except (ValueError, TypeError):
        return "-4%"


def resolve_voice_name(lang: str, voice_param: str = None) -> str:
    """Maps voice alias or parameter to valid neural voice name."""
    lang_key = "ta" if lang == "ta" else "en"
    cfg = VOICE_CONFIG.get(lang_key, VOICE_CONFIG["ta"])
    if not voice_param:
        return cfg["default"]
    clean_v = str(voice_param).strip().lower()
    if clean_v in cfg:
        return cfg[clean_v]
    if "neural" in str(voice_param).lower():
        return str(voice_param).strip()
    return cfg["default"]


def preprocess_scripture_text(text: str, lang: str = "ta") -> str:
    """Refines scripture text with natural breath pauses and pronunciation cleanups."""
    clean = text.strip()
    # Strip footnote markers
    clean = re.sub(r"[\*†‡]", "", clean)
    # Completely strip anything inside square brackets [] or curly braces {} (e.g. [1-2], [1], [notes], {annotations})
    clean = re.sub(r"\[[\s\S]*?\]", "", clean)
    clean = re.sub(r"\{[\s\S]*?\}", "", clean)
    clean = re.sub(r"[—–]", " - ", clean)
    # Clean up redundant whitespace and spaces before punctuation
    clean = re.sub(r"\s+", " ", clean).strip()
    clean = re.sub(r"\s+([.,;:!?])", r"\1", clean)
    if not clean:
        # Fallback to stripped raw text without bracket symbols if verse text was entirely enclosed in brackets
        clean = re.sub(r"[\[\]\{\}]", "", text).strip()

    if lang == "ta":
        # Expand common Tamil Bible book abbreviations
        abbrevs = {
            r"\bஆதி\.": "ஆதியாகமம்",
            r"\bயாத்\.": "யாத்திராகமம்",
            r"\bலேவி\.": "லேவியராகமம்",
            r"\bஎண்\.": "எண்ணாகமம்",
            r"\bஉபா\.": "உபாகமம்",
            r"\bயோசு\.": "யோசுவா",
            r"\bநியாயா\.": "நியாயாதிபதிகள்",
            r"\bசங்\.": "சங்கீதம்",
            r"\bநீதி\.": "நீதிமொழிகள்",
            r"\bஏசா\.": "ஏசாயா",
            r"\bமத்\.": "மத்தேயு",
            r"\bமாற்\.": "மாற்கு",
            r"\bலூக்\.": "லூக்கா",
            r"\bயோவா\.": "யோவான்",
            r"\bஅப்\.": "அப்போஸ்தலர் நடபடிகள்",
            r"\bரோம\.": "ரோமர்",
            r"\bவெளி\.": "வெளிப்படுத்தின விசேஷம்",
            r"\bதோபி\.": "தோபித்து",
            r"\bயூதி\.": "யூதித்து",
            r"\bசீரா\.": "சீராக்",
            r"\bபாரூ\.": "பாரூக்",
            r"\bமக்க\.": "மக்கபேயர்",
            r"\bதொ\.நூ\.": "தொடக்க நூல்",
            r"\bவி\.ப\.": "விடுதலைப் பயணம்",
            r"\bஇணை\.": "இணைச் சட்டம்",
            r"\bதி\.பா\.": "திருப்பாடல்கள்",
            r"\bதி\.பணி\.": "திருத்தூதர் பணிகள்",
            r"\bதி\.வெளி\.": "திருவெளிப்பாடு",
        }
        for pat, repl in abbrevs.items():
            clean = re.sub(pat, repl, clean)
        # Semicolons and colons create natural breathing pauses in Tamil
        clean = clean.replace(";", ", ").replace(":", ", ")
    return clean


@app.get("/api/audio/stream")
async def stream_audio(
    text: str = Query(..., min_length=1),
    lang: str = Query("ta"),
    voice: str = Query(None),
    rate: str = Query(None),
):
    target_lang = "ta" if lang == "ta" else "en"
    clean_text = preprocess_scripture_text(text, target_lang)
    target_voice = resolve_voice_name(target_lang, voice)
    target_rate = normalize_speech_rate(rate)

    cache_key = hashlib.md5(f"{target_voice}:{target_rate}:{clean_text}".encode("utf-8")).hexdigest()

    if cache_key in AUDIO_CACHE:
        return Response(
            content=AUDIO_CACHE[cache_key],
            media_type="audio/mpeg",
            headers={"X-TTS-Engine": "cache", "X-TTS-Voice": target_voice},
        )

    # 1. Primary Engine: Microsoft Neural Edge-TTS (Natural Human Cadence)
    if HAS_EDGE_TTS:
        try:
            communicate = edge_tts.Communicate(
                text=clean_text,
                voice=target_voice,
                rate=target_rate,
            )
            fp = io.BytesIO()
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    fp.write(chunk["data"])
            audio_bytes = fp.getvalue()
            if len(audio_bytes) > 0:
                if len(AUDIO_CACHE) > 500:
                    AUDIO_CACHE.pop(next(iter(AUDIO_CACHE)))
                AUDIO_CACHE[cache_key] = audio_bytes
                return Response(
                    content=audio_bytes,
                    media_type="audio/mpeg",
                    headers={"X-TTS-Engine": "edge-neural", "X-TTS-Voice": target_voice},
                )
        except Exception as neural_err:
            print(f"[Audio Stream] Edge-TTS error, falling back to gTTS: {neural_err}")

    # 2. Fallback Engine: gTTS (Ensures zero interruption)
    try:
        tts = gTTS(text=clean_text, lang=target_lang, slow=False)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        audio_bytes = fp.getvalue()

        if len(AUDIO_CACHE) > 500:
            AUDIO_CACHE.pop(next(iter(AUDIO_CACHE)))
        AUDIO_CACHE[cache_key] = audio_bytes

        return Response(
            content=audio_bytes,
            media_type="audio/mpeg",
            headers={"X-TTS-Engine": "gtts-fallback", "X-TTS-Voice": target_voice},
        )
    except Exception as fallback_err:
        return JSONResponse(content={"error": str(fallback_err)}, status_code=500)


# ==========================================
# 4. Status & Health (Zero-DB Touch)
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
# 5. Canon Helpers & Main Bible Pages
# ==========================================

def resolve_canon(request: Request, canon: str = None, book_id: int = None) -> str:
    """Resolves active canon ('protestant' or 'catholic') from query, current book, or cookie."""
    if canon and canon.lower() in ("catholic", "protestant"):
        return canon.lower()
    if book_id is not None and book_id >= 67:
        return "catholic"
    cookie_canon = request.cookies.get("bible_canon")
    if cookie_canon and cookie_canon.lower() in ("catholic", "protestant"):
        return cookie_canon.lower()
    return "protestant"


def get_canon_context(canon: str = "protestant"):
    """Returns standardized book lists and chapter counts for template contexts."""
    is_catholic = (canon and str(canon).lower() == "catholic")
    canon_name = "catholic" if is_catholic else "protestant"
    books = CATHOLIC_BOOKS if is_catholic else BIBLE_BOOKS
    ot_books = [b for b in books if b[0] <= 39]
    nt_books = [b for b in books if 40 <= b[0] <= 66]
    dc_books = [b for b in books if b[0] >= 67] if is_catholic else DEUTEROCANONICAL_BOOKS
    
    total_chapters = 1326 if is_catholic else 1189
    ot_chapters = 1066 if is_catholic else 929
    dc_chapters = 137
    nt_chapters = 260

    return {
        "canon": canon_name,
        "is_catholic": is_catholic,
        "books": books,
        "all_books": CATHOLIC_BOOKS,
        "ot_books": ot_books,
        "nt_books": nt_books,
        "deuterocanon_books": dc_books,
        "total_chapters": total_chapters,
        "ot_chapters": ot_chapters,
        "dc_chapters": dc_chapters,
        "nt_chapters": nt_chapters,
    }


@app.get("/", response_class=HTMLResponse)
async def landing_page(request: Request, canon: str = Query(None)):
    active_canon = resolve_canon(request, canon)
    canon_ctx = get_canon_context(active_canon)
    return templates.TemplateResponse(
        request=request,
        name="landing.html",
        context={
            **canon_ctx,
            "daily_verse": get_daily_verse(active_canon),
        },
    )


@app.get("/read/{book_id}/{chapter}", response_class=HTMLResponse)
async def reader(
    request: Request,
    book_id: int,
    chapter: int,
    mode: str = Query("bilingual"),
    canon: str = Query(None),
):
    active_canon = resolve_canon(request, canon, book_id)
    if book_id not in BOOK_MAP and book_id not in CATHOLIC_BOOK_MAP:
        book_id = 1
    current_book = get_book_info(book_id, canon=active_canon)
    if chapter < 1 or chapter > current_book["total_chapters"]:
        chapter = 1

    try:
        verses = get_chapter_verses(book_id, chapter, canon=active_canon) or []
    except Exception as e:
        print(f"Error fetching verses: {e}")
        verses = []

    prev_ch = chapter - 1 if chapter > 1 else None
    next_ch = chapter + 1 if chapter < current_book["total_chapters"] else None
    canon_ctx = get_canon_context(active_canon)

    return templates.TemplateResponse(
        request=request,
        name="reader.html",
        context={
            **canon_ctx,
            "book": current_book,
            "chapter": chapter,
            "verses": verses,
            "mode": mode,
            "prev_ch": prev_ch,
            "next_ch": next_ch,
        },
    )


@app.get("/present/{book_id}/{chapter}", response_class=HTMLResponse)
async def presenter_mode(request: Request, book_id: int, chapter: int, canon: str = Query(None)):
    """Church / TV / Projector presentation mode with extra-large bilingual slides."""
    active_canon = resolve_canon(request, canon, book_id)
    if book_id not in BOOK_MAP and book_id not in CATHOLIC_BOOK_MAP:
        book_id = 1
    current_book = get_book_info(book_id, canon=active_canon)
    if chapter < 1 or chapter > current_book["total_chapters"]:
        chapter = 1

    verses = get_chapter_verses(book_id, chapter, canon=active_canon)
    canon_ctx = get_canon_context(active_canon)

    return templates.TemplateResponse(
        request=request,
        name="presenter.html",
        context={
            **canon_ctx,
            "book": current_book,
            "chapter": chapter,
            "verses": verses,
        },
    )


@app.get("/plans", response_class=HTMLResponse)
async def plans_page(request: Request, canon: str = Query(None)):
    """Daily habit reading tracks with day-by-day progress checkoffs."""
    active_canon = resolve_canon(request, canon)
    canon_ctx = get_canon_context(active_canon)
    return templates.TemplateResponse(
        request=request,
        name="plans.html",
        context={
            **canon_ctx,
            "plans": READING_PLANS,
        },
    )


@app.get("/progress", response_class=HTMLResponse)
async def progress_page(request: Request, canon: str = Query(None)):
    active_canon = resolve_canon(request, canon)
    canon_ctx = get_canon_context(active_canon)
    return templates.TemplateResponse(
        request=request,
        name="progress.html",
        context=canon_ctx,
    )


@app.get("/search", response_class=HTMLResponse)
async def search_page(request: Request, q: str = Query("", min_length=1), canon: str = Query(None)):
    active_canon = resolve_canon(request, canon)
    canon_ctx = get_canon_context(active_canon)
    results = search_verses(q, canon=active_canon) if q.strip() else []
    # If Protestant mode, filter out Deuterocanonical results (IDs > 66)
    if not canon_ctx["is_catholic"]:
        results = [r for r in results if r["book_id"] <= 66]

    return templates.TemplateResponse(
        request=request,
        name="search.html",
        context={
            **canon_ctx,
            "query": q,
            "results": results,
        },
    )


@app.get("/bookmarks", response_class=HTMLResponse)
async def bookmarks_page(request: Request, canon: str = Query(None)):
    active_canon = resolve_canon(request, canon)
    canon_ctx = get_canon_context(active_canon)
    return templates.TemplateResponse(
        request=request,
        name="bookmarks.html",
        context=canon_ctx,
    )


@app.get("/quiz", response_class=HTMLResponse)
async def quiz_page(request: Request, canon: str = Query(None)):
    """Interactive Bible Quiz / Trivia game page."""
    active_canon = resolve_canon(request, canon)
    canon_ctx = get_canon_context(active_canon)
    return templates.TemplateResponse(
        request=request,
        name="quiz.html",
        context={
            **canon_ctx,
            "categories": QUIZ_CATEGORIES,
            "total_questions": len(QUIZ_QUESTIONS),
        },
    )


@app.get("/api/quiz/questions")
async def get_quiz_questions(
    category: str = Query("all"),
    difficulty: str = Query("all"),
    limit: int = Query(10, ge=1, le=50),
    randomize: bool = Query(True),
):
    """Returns filtered and optionally shuffled quiz questions."""
    filtered = QUIZ_QUESTIONS
    if category != "all":
        filtered = [q for q in filtered if q.get("category") == category]
    if difficulty != "all":
        filtered = [q for q in filtered if q.get("difficulty") == difficulty]

    results = list(filtered)
    if randomize:
        random.shuffle(results)

    return JSONResponse(
        content={
            "category": category,
            "difficulty": difficulty,
            "total_available": len(filtered),
            "questions": results[:limit],
        }
    )


@app.get("/book/{book_id}/chapter/{chapter}")
async def legacy_redirect(book_id: int, chapter: int):
    return RedirectResponse(url=f"/read/{book_id}/{chapter}?mode=bilingual")

# ==========================================
# 6. 100-Day Read-Along Plan Routes
# ==========================================

PLANS_DIR = Path(__file__).resolve().parent.parent / "static" / "plans"


def _lookup_book_id(book_str: str):
    """Maps book name, ID, or slug to integer book_id in BOOK_MAP or CATHOLIC_BOOK_MAP."""
    if not book_str:
        return None
    try:
        val = int(book_str)
        if val in BOOK_MAP or val in CATHOLIC_BOOK_MAP:
            return val
    except (ValueError, TypeError):
        pass

    clean = str(book_str).strip().lower()
    for bid, binfo in CATHOLIC_BOOK_MAP.items():
        if (
            binfo.get("name_en", "").lower() == clean
            or binfo.get("name_ta", "").strip() == str(book_str).strip()
            or binfo.get("name_ta", "").strip().lower() == clean
        ):
            return bid

    for bid, binfo in BOOK_MAP.items():
        if (
            binfo.get("name_en", "").lower() == clean
            or binfo.get("name_ta", "").strip() == str(book_str).strip()
            or binfo.get("name_ta", "").strip().lower() == clean
            or binfo.get("abbrev", "").lower() == clean
            or binfo.get("slug", "").lower() == clean
        ):
            return bid
    return None


@app.get("/read-along/plan/{plan_type}")
async def redirect_plan_to_day(plan_type: str, day: int = 1):
    return RedirectResponse(url=f"/read-along/plan/{plan_type}/day/{day}")


@app.get("/read-along/plan/{plan_type}/day/{day}", response_class=HTMLResponse)
async def read_along_plan_day(request: Request, plan_type: str, day: int):
    plan_files = {
        "whole-bible-100": ("plan_100_whole_bible.json", "Whole Bible in 100 Days"),
        "new-testament-100": ("plan_100_new_testament.json", "New Testament in 100 Days"),
        "deuterocanon-30": ("plan_30_deuterocanon.json", "Deuterocanon in 30 Days"),
        "deuterocanonical-30": ("plan_30_deuterocanon.json", "Deuterocanon in 30 Days"),
        "catholic-100": ("plan_100_catholic_bible.json", "Catholic Bible in 100 Days"),
        "catholic-bible-100": ("plan_100_catholic_bible.json", "Catholic Bible in 100 Days"),
    }

    if plan_type not in plan_files:
        raise HTTPException(status_code=404, detail="Plan not found")

    filename, default_title = plan_files[plan_type]
    file_path = PLANS_DIR / filename
    if not file_path.exists():
        file_path = Path("static/plans") / filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"File {filename} not found")

    with open(file_path, "r", encoding="utf-8") as f:
        plan_json = json.load(f)

    # 1. Extract days list from JSON
    raw_days = []
    if isinstance(plan_json, list):
        raw_days = plan_json
    elif isinstance(plan_json, dict):
        if isinstance(plan_json.get("days"), list):
            raw_days = plan_json["days"]
        elif isinstance(plan_json.get("days"), dict):
            raw_days = list(plan_json["days"].values())
        else:
            raw_days = [v for k, v in plan_json.items() if isinstance(v, dict)]

    # 2. Locate target day
    target_entry = None
    for entry in raw_days:
        if isinstance(entry, dict) and entry.get("day") == day:
            target_entry = dict(entry)
            break

    if not target_entry and raw_days and (1 <= day <= len(raw_days)):
        target_entry = dict(raw_days[day - 1])

    if not target_entry:
        raise HTTPException(status_code=404, detail=f"Day {day} not found in {plan_type}")

    # 3. Read chapter portions (e.g. ["Matthew 1", "Matthew 2", ...])
    portions = (
        target_entry.get("portions")
        or target_entry.get("chapters")
        or target_entry.get("readings")
        or target_entry.get("passages")
        or []
    )

    active_canon = "catholic" if any(k in plan_type for k in ("catholic", "deuterocanon")) else resolve_canon(request)

    chapters_data = []
    for item in portions:
        book_id = None
        chapter = None

        if isinstance(item, str):
            # Parse strings like "Matthew 1", "1 John 2", "மத்தேயு 1"
            match = re.match(r"^(.*?)\s*(\d+)$", item.strip())
            if match:
                book_str, ch_str = match.groups()
                book_id = _lookup_book_id(book_str)
                chapter = int(ch_str)
        elif isinstance(item, dict):
            raw_book = item.get("book_id") or item.get("book") or item.get("b")
            raw_ch = item.get("chapter") or item.get("ch") or item.get("c")
            book_id = _lookup_book_id(raw_book)
            if raw_ch is not None:
                chapter = int(raw_ch)

        if book_id and chapter:
            # Query the database with active_canon
            raw_verses = get_chapter_verses(book_id, chapter, canon=active_canon) or []
            book_info = get_book_info(book_id, canon=active_canon)

            # Normalize verse fields to support whatever keys your template/audio uses
            verses = []
            for v in raw_verses:
                if isinstance(v, dict):
                    verses.append({
                        "verse": v.get("verse") or v.get("verse_num") or v.get("v"),
                        "verse_num": v.get("verse_num") or v.get("verse") or v.get("v"),
                        "verse_display": v.get("verse_display") or str(v.get("verse") or v.get("verse_num") or ""),
                        "text_ta": v.get("text_ta") or v.get("text", ""),
                        "text_en": v.get("text_en") or v.get("text", ""),
                        "text": v.get("text_ta") or v.get("text_en") or v.get("text", ""),
                    })

            chapter_dict = {
                "book_id": book_id,
                "book": book_info,
                "book_name": book_info.get("name_ta", "") or book_info.get("name_en", ""),
                "book_name_en": book_info.get("name_en", ""),
                "book_name_ta": book_info.get("name_ta", ""),
                "chapter": chapter,
                "verses": verses,
            }
            chapters_data.append(chapter_dict)

    # 4. Prepare data matching your original template's exact keys
    day_obj = dict(target_entry)
    day_obj["day"] = day
    day_obj["chapters"] = chapters_data
    day_obj["readings"] = chapters_data
    day_obj["portions"] = chapters_data

    # Ensure intro fields exist safely
    if "intro" not in day_obj or not isinstance(day_obj["intro"], dict):
        day_obj["intro"] = {}
    day_obj["intro"].setdefault("display_ta", f"{default_title} - நாள் {day}")
    day_obj["intro"].setdefault("display_en", f"{default_title} - Day {day}")

    plan_obj = {
        "id": plan_type,
        "title": default_title,
        "name": default_title,
        "total_days": len(raw_days) or 100,
    }

    active_canon = resolve_canon(request)
    canon_ctx = get_canon_context(active_canon)

    return templates.TemplateResponse(
        request=request,
        name="read_along.html",
        context={
            **canon_ctx,
            "is_plan_mode": True,
            "plan": plan_obj,
            "plan_type": plan_type,
            "plan_title": default_title,
            "day": day_obj,
            "chapters": chapters_data,
            "readings": chapters_data,
            "total_days": plan_obj["total_days"],
            "prev_day": day - 1 if day > 1 else None,
            "next_day": day + 1 if day < plan_obj["total_days"] else None,
        },
    )
