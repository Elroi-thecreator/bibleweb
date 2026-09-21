import json
import os
from pathlib import Path
from fastapi import FastAPI, Request, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.db import (
    get_books,
    get_chapter_verses,
    search_verses,
    get_verse_count_by_book
)
import app.plans_data as plans_data

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


# --- Plan Endpoints (Separated) ---

@app.get("/api/plans/default")
async def get_default_plans():
    """Returns the default plan data from app.plans_data."""
    for attr in ["PLANS", "DEFAULT_PLANS", "plans", "default_plans"]:
        if hasattr(plans_data, attr):
            return JSONResponse(content=getattr(plans_data, attr))
    # Return any public dictionary defined in plans_data
    for k, v in vars(plans_data).items():
        if not k.startswith("_") and isinstance(v, (dict, list)):
            return JSONResponse(content={k: v})
    return JSONResponse(content={})


@app.get("/api/plans/100-days/{plan_id}")
async def get_100_day_plan(plan_id: str):
    """Returns specific 100-day plans from static/plans directory."""
    clean_id = plan_id.replace("plan_", "")
    candidate_files = [
        PLANS_DIR / f"{plan_id}.json",
        PLANS_DIR / f"plan_{plan_id}.json",
        PLANS_DIR / f"plan_{clean_id}.json"
    ]

    for file_path in candidate_files:
        if file_path.is_file():
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    return JSONResponse(content=json.load(f))
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error reading plan: {str(e)}")

    raise HTTPException(status_code=404, detail="100-day plan not found")