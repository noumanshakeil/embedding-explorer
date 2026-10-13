"""Embedding Explorer — FastAPI backend + Jinja UI."""
from __future__ import annotations

import json
import uuid
from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .config import settings
from .llm import complete

ROOT = Path(__file__).resolve().parent
DATA = ROOT.parent / "data" / "store.json"
FIELDS = ['text', 'label']

app = FastAPI(title="Embedding Explorer", version="1.0.0")
app.mount("/static", StaticFiles(directory=str(ROOT / "static")), name="static")
templates = Jinja2Templates(directory=str(ROOT / "templates"))


def load_store() -> dict:
    if not DATA.exists():
        DATA.parent.mkdir(parents=True, exist_ok=True)
        payload = {"vectors": [
  {
    "id": "em1",
    "text": "refund policy",
    "label": "support"
  }
]}
        DATA.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return json.loads(DATA.read_text(encoding="utf-8"))


def save_store(store: dict) -> None:
    DATA.parent.mkdir(parents=True, exist_ok=True)
    DATA.write_text(json.dumps(store, indent=2), encoding="utf-8")


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "embedding-explorer", "llm_mode": settings.llm_mode}


@app.get("/api/vectors")
def list_items() -> dict:
    store = load_store()
    return {"vectors": store.get("vectors", [])}


@app.post("/api/vectors")
def create_item(payload: dict) -> dict:
    store = load_store()
    item = {"id": uuid.uuid4().hex[:8]}
    for key in FIELDS:
        item[key] = payload.get(key)
    store.setdefault("vectors", []).insert(0, item)
    save_store(store)
    return item


@app.post("/api/neighbors")
def run_action(payload: dict) -> dict:
    """Find nearest neighbor texts."""
    prompt = (
        "You are the AI engine for Embedding Explorer.\n"
        "Task: Find nearest neighbor texts.\n"
        f"Input JSON: {json.dumps(payload)[:4000]}"
    )
    text = complete(prompt)
    return {"ok": True, "action": "neighbors", "result": text, "mode": settings.llm_mode}


@app.get("/", response_class=HTMLResponse)
def home(request: Request, last_result: str | None = None) -> HTMLResponse:
    store = load_store()
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "title": "Embedding Explorer",
            "description": "Embedding explorer with nearest neighbors, clusters, and query UI.",
            "resource": "vectors",
            "action": "neighbors",
            "action_desc": "Find nearest neighbor texts",
            "items": store.get("vectors", []),
            "llm_mode": settings.llm_mode,
            "last_result": last_result,
        },
    )


@app.post("/ui/create", response_class=HTMLResponse)
async def ui_create(request: Request) -> HTMLResponse:
    form = await request.form()
    data = {k: form.get(k) for k in FIELDS}
    create_item(data)
    return home(request)


@app.post("/ui/action", response_class=HTMLResponse)
async def ui_action(request: Request, prompt: str = Form("demo")) -> HTMLResponse:
    result = run_action({"prompt": prompt})
    store = load_store()
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "title": "Embedding Explorer",
            "description": "Embedding explorer with nearest neighbors, clusters, and query UI.",
            "resource": "vectors",
            "action": "neighbors",
            "action_desc": "Find nearest neighbor texts",
            "items": store.get("vectors", []),
            "llm_mode": settings.llm_mode,
            "last_result": result.get("result"),
        },
    )
