from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db import get_db
from backend.services import embeddings as svc

router = APIRouter()
templates = Jinja2Templates(directory="backend/templates")

@router.get("/", response_class=HTMLResponse)
async def home(request: Request, q: str = "", db: AsyncSession = Depends(get_db)):
    hits = await svc.search(db, q) if q else []
    return templates.TemplateResponse("index.html", {"request": request, "title": "Embedding Explorer",
        "docs": await svc.list_docs(db), "hits": hits, "q": q})

@router.post("/ui/docs")
async def ui_d(title: str = Form(...), text: str = Form(...), db: AsyncSession = Depends(get_db)):
    await svc.add_doc(db, title, text); return RedirectResponse("/", status_code=303)

@router.get("/ui/search")
async def ui_s(q: str = "", db: AsyncSession = Depends(get_db)):
    return RedirectResponse(f"/?q={q}", status_code=303)
