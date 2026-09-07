from fastapi import FastAPI, Request, Query
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from app.db import BIBLE_BOOKS, BOOK_MAP, get_chapter_verses, search_verses

app = FastAPI(title="Holy Bible - வேதம்")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Daily verse curator
DAILY_VERSE = {
    "ref_en": "John 3:16",
    "ref_ta": "யோவான் 3:16",
    "text_en": "For God so loved the world, that he gave his only begotten Son, that whosoever believeth in him should not perish, but have everlasting life.",
    "text_ta": "தேவன், தம்முடைய ஒரேபேறான குமாரனை விசுவாசிக்கிறவன் எவனோ அவன் கெட்டுப்போகாமல் நித்தியஜீவனை அடையும்படிக்கு, அவரைத் தந்தருளி, இவ்வளவாய் உலகத்தில் அன்புகூர்ந்தார்.",
    "link": "/read/43/1?mode=bilingual"
}

@app.get("/", response_class=HTMLResponse)
async def landing_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="landing.html",
        context={
            "books": BIBLE_BOOKS,
            "daily_verse": DAILY_VERSE,
            "ot_books": [b for b in BIBLE_BOOKS if b[0] <= 39],
            "nt_books": [b for b in BIBLE_BOOKS if b[0] > 39]
        }
    )

@app.get("/read/{book_id}/{chapter}", response_class=HTMLResponse)
async def reader(request: Request, book_id: int, chapter: int, mode: str = Query("bilingual")):
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
            "nt_books": [b for b in BIBLE_BOOKS if b[0] > 39]
        }
    )

@app.get("/search", response_class=HTMLResponse)
async def search_page(request: Request, q: str = Query("", min_length=1)):
    results = search_verses(q) if q.strip() else []
    return templates.TemplateResponse(
        request=request,
        name="search.html",
        context={"query": q, "results": results, "books": BIBLE_BOOKS}
    )

@app.get("/bookmarks", response_class=HTMLResponse)
async def bookmarks_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="bookmarks.html",
        context={"books": BIBLE_BOOKS}
    )