from __future__ import annotations
import json, math, uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.models import EmbeddingDoc
from backend.utils.text import token_set

def embed(text: str, dims: int = 32) -> list[float]:
    toks = sorted(token_set(text))
    vec = [0.0] * dims
    for t in toks:
        h = abs(hash(t))
        vec[h % dims] += 1.0 + (h % 7) * 0.01
    n = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [round(v / n, 6) for v in vec]

def cosine(a: list[float], b: list[float]) -> float:
    return round(sum(x * y for x, y in zip(a, b)), 6)

async def add_doc(session: AsyncSession, title: str, text: str) -> EmbeddingDoc:
    vec = embed(text)
    row = EmbeddingDoc(id=uuid.uuid4().hex[:10], title=title.strip()[:200], text=text.strip(), vector_json=json.dumps(vec))
    session.add(row); await session.commit(); await session.refresh(row); return row

async def list_docs(session: AsyncSession) -> list[EmbeddingDoc]:
    return list((await session.execute(select(EmbeddingDoc).order_by(EmbeddingDoc.created_at.desc()))).scalars())

async def search(session: AsyncSession, query: str, k: int = 5) -> list[dict]:
    qv = embed(query)
    hits = []
    for d in await list_docs(session):
        score = cosine(qv, json.loads(d.vector_json or "[]"))
        hits.append({"id": d.id, "title": d.title, "score": score, "snippet": d.text[:180]})
    hits.sort(key=lambda h: h["score"], reverse=True)
    return hits[:k]
