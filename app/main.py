import json
import os
from pathlib import Path
from fastapi import FastAPI, Request, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.db import (
    get_db_connection,
    get_books,
    get_chapter_verses,
    search_verses,
    get_verse_count_by_book
)
from app.plans_data import DEFAULT_PLANS

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"
PLANS_DIR = STATIC_DIR / "plans"

app = FastAPI(title="BibleWeb")

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    books = get_books()
    return templates.TemplateResponse(
        "landing.html",
        {"request": request, "books": books}
    )


@app.get("/read", response_class=HTMLResponse)
async def read_view(
    request: Request,
    book: str = Query(default="Genesis"),
    chapter: int = Query(default=1)
):
    books = get_books()
    verses = get_chapter_verses(book, chapter)
    return templates.TemplateResponse(
        "read.html",
        {
            "request": request,
            "books": books,
            "book_name": book,
            "chapter_num": chapter,
            "verses": verses
        }
    )


@app.get("/search", response_class=HTMLResponse)
async def search_view(request: Request, q: str = Query(default="")):
    results = search_verses(q) if q.strip() else []
    return templates.TemplateResponse(
        "search.html",
        {"request": request, "query": q, "results": results}
    )


@app.get("/bookmarks", response_class=HTMLResponse)
async def bookmarks_view(request: Request):
    return templates.TemplateResponse("bookmarks.html", {"request": request})


@app.get("/plans", response_class=HTMLResponse)
async def plans_view(request: Request):
    return templates.TemplateResponse("plans.html", {"request": request})


@app.get("/progress", response_class=HTMLResponse)
async def progress_view(request: Request):
    return templates.TemplateResponse("progress.html", {"request": request})


@app.get("/presenter", response_class=HTMLResponse)
async def presenter_view(
    request: Request,
    book: str = Query(default="Genesis"),
    chapter: int = Query(default=1)
):
    verses = get_chapter_verses(book, chapter)
    return templates.TemplateResponse(
        "presenter.html",
        {
            "request": request,
            "book_name": book,
            "chapter_num": chapter,
            "verses": verses
        }
    )


# --- API Routes ---

@app.get("/api/plans")
async def list_available_plans():
    """List available static plans and built-in defaults."""
    plans = []
    if PLANS_DIR.exists():
        for f in PLANS_DIR.glob("*.json"):
            plan_id = f.stem.replace("plan_", "")
            try:
                with open(f, "r", encoding="utf-8") as pf:
                    data = json.load(pf)
                    plans.append({
                        "id": plan_id,
                        "title": data.get("title", plan_id.replace("_", " ").title()),
                        "days_count": len(data.get("days", []))
                    })
            except Exception:
                continue

    if not plans:
        plans = [
            {"id": "100_whole_bible", "title": "100 Days Through the Whole Bible", "days_count": 100},
            {"id": "100_new_testament", "title": "100 Days Through the New Testament", "days_count": 100}
        ]

    return JSONResponse(content=plans)


@app.get("/api/plans/{plan_id}")
async def get_plan_details(plan_id: str):
    """Retrieve schedule items for a specific reading plan."""
    candidate_names = [f"{plan_id}.json", f"plan_{plan_id}.json"]
    target_file = None

    for name in candidate_names:
        candidate_path = PLANS_DIR / name
        if candidate_path.is_file():
            target_file = candidate_path
            break

    if target_file and target_file.exists():
        try:
            with open(target_file, "r", encoding="utf-8") as f:
                return JSONResponse(content=json.load(f))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to read plan: {str(e)}")

    if plan_id in DEFAULT_PLANS:
        return JSONResponse(content=DEFAULT_PLANS[plan_id])

    raise HTTPException(status_code=404, detail=f"Plan '{plan_id}' not found")