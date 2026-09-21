import json
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app import db
from app.plans_data import PLANS

app = FastAPI(title="BibleWeb")

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"
PLANS_DIR = STATIC_DIR / "plans"

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("landing.html", {"request": request})


@app.get("/read", response_class=HTMLResponse)
async def read_view(request: Request, book: Optional[str] = "GEN", chapter: int = 1):
    books = db.get_books()
    verses = db.get_chapter_verses(book, chapter)
    total_chapters = db.get_chapter_count(book)
    return templates.TemplateResponse(
        "read.html",
        {
            "request": request,
            "books": books,
            "current_book": book,
            "chapter": chapter,
            "verses": verses,
            "total_chapters": total_chapters,
        },
    )


@app.get("/plans", response_class=HTMLResponse)
async def plans_view(request: Request):
    return templates.TemplateResponse(
        "plans.html",
        {
            "request": request,
            "plans": PLANS,
        },
    )


@app.get("/read-along", response_class=HTMLResponse)
async def read_along_default(
    request: Request,
    plan: Optional[str] = None,
    day: Optional[int] = 1,
    book: Optional[str] = None,
    chapter: Optional[int] = 1,
):
    """
    Redirects or serves standard single-chapter or day-based read-along.
    """
    if plan in ["whole-bible-100", "new-testament-100"]:
        return RedirectResponse(url=f"/read-along/plan/{plan}/day/{day or 1}")

    target_book = book or "GEN"
    target_chapter = chapter or 1
    verses = db.get_chapter_verses(target_book, target_chapter)
    books = db.get_books()

    return templates.TemplateResponse(
        "read_along.html",
        {
            "request": request,
            "is_plan_mode": False,
            "plan_type": None,
            "plan_title": None,
            "day": None,
            "prev_day": None,
            "next_day": None,
            "readings": [
                {
                    "book_id": target_book,
                    "book_name": db.get_book_name(target_book),
                    "chapter": target_chapter,
                    "verses": verses,
                }
            ],
            "books": books,
            "current_book": target_book,
            "current_chapter": target_chapter,
        },
    )


@app.get("/read-along/plan/{plan_type}/day/{day}", response_class=HTMLResponse)
async def read_along_plan_day(request: Request, plan_type: str, day: int):
    """
    Renders all chapters assigned to a single day on one page for read-along.
    """
    plan_mapping = {
        "whole-bible-100": {
            "file": "plan_100_whole_bible.json",
            "title": "Whole Bible in 100 Days",
        },
        "new-testament-100": {
            "file": "plan_100_new_testament.json",
            "title": "New Testament in 100 Days",
        },
    }

    if plan_type not in plan_mapping:
        raise HTTPException(status_code=404, detail="Plan not found")

    plan_info = plan_mapping[plan_type]
    file_path = PLANS_DIR / plan_info["file"]

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Plan schedule file not found")

    with open(file_path, "r", encoding="utf-8") as f:
        plan_data = json.load(f)

    # Resolve schedule by day index (handles list of days or object keyed by day number)
    day_entry = None
    if isinstance(plan_data, list):
        for item in plan_data:
            if item.get("day") == day:
                day_entry = item
                break
    elif isinstance(plan_data, dict):
        day_entry = plan_data.get(str(day)) or plan_data.get(day)

    if not day_entry:
        raise HTTPException(status_code=404, detail=f"Day {day} not found in plan")

    # Extract all chapters or passages assigned to this day
    items = (
        day_entry.get("readings")
        or day_entry.get("chapters")
        or day_entry.get("passages")
        or []
    )

    readings = []
    for item in items:
        book_id = item.get("book") or item.get("book_id") or item.get("b")
        ch = item.get("chapter") or item.get("ch") or item.get("c")
        if book_id and ch:
            verses = db.get_chapter_verses(book_id, int(ch))
            book_name = db.get_book_name(book_id) if hasattr(db, "get_book_name") else book_id
            readings.append(
                {
                    "book_id": book_id,
                    "book_name": book_name,
                    "chapter": int(ch),
                    "verses": verses,
                }
            )

    return templates.TemplateResponse(
        "read_along.html",
        {
            "request": request,
            "is_plan_mode": True,
            "plan_type": plan_type,
            "plan_title": plan_info["title"],
            "day": day,
            "total_days": 100,
            "prev_day": day - 1 if day > 1 else None,
            "next_day": day + 1 if day < 100 else None,
            "readings": readings,
            "books": db.get_books(),
        },
    )


@app.get("/bookmarks", response_class=HTMLResponse)
async def bookmarks_view(request: Request):
    return templates.TemplateResponse("bookmarks.html", {"request": request})


@app.get("/progress", response_class=HTMLResponse)
async def progress_view(request: Request):
    return templates.TemplateResponse("progress.html", {"request": request})


@app.get("/presenter", response_class=HTMLResponse)
async def presenter_view(request: Request, book: Optional[str] = "GEN", chapter: int = 1):
    verses = db.get_chapter_verses(book, chapter)
    return templates.TemplateResponse(
        "presenter.html",
        {
            "request": request,
            "book": book,
            "chapter": chapter,
            "verses": verses,
        },
    )


@app.get("/search", response_class=HTMLResponse)
async def search_view(request: Request, q: Optional[str] = ""):
    results = db.search_verses(q) if q else []
    return templates.TemplateResponse(
        "search.html",
        {
            "request": request,
            "query": q,
            "results": results,
        },
    )