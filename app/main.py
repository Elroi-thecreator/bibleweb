from fastapi import FastAPI, Request, Query
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from app.db import BIBLE_BOOKS, BOOK_MAP, get_chapter_verses, search_verses

app = FastAPI(title="Bilingual Tamil-English Bible")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home():
    # Redirect to Genesis 1 by default (or book 43 for John)
    return RedirectResponse(url="/book/1/chapter/1")

@app.get("/book/{book_id}/chapter/{chapter}", response_class=HTMLResponse)
async def read_chapter(request: Request, book_id: int, chapter: int):
    if book_id not in BOOK_MAP:
        book_id = 1
    current_book = BOOK_MAP[book_id]
    if chapter < 1 or chapter > current_book["total_chapters"]:
        chapter = 1

    verses = get_chapter_verses(book_id, chapter)
    
    prev_chapter = chapter - 1 if chapter > 1 else None
    next_chapter = chapter + 1 if chapter < current_book["total_chapters"] else None

    return templates.TemplateResponse(
        request=request,
        name="chapter.html",
        context={
            "books": BIBLE_BOOKS,
            "book": current_book,
            "chapter": chapter,
            "verses": verses,
            "prev_chapter": prev_chapter,
            "next_chapter": next_chapter
        }
    )

@app.get("/search", response_class=HTMLResponse)
async def search_page(request: Request, q: str = Query("", min_length=1)):
    results = search_verses(q) if q.strip() else []
    return templates.TemplateResponse(
        request=request,
        name="search.html",
        context={
            "query": q,
            "results": results,
            "books": BIBLE_BOOKS
        }
    )

@app.get("/bookmarks", response_class=HTMLResponse)
async def bookmarks_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="bookmarks.html",
        context={"books": BIBLE_BOOKS}
    )