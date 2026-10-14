from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db import get_db
from backend.services import embeddings as svc

class DocIn(BaseModel):
    title: str = Field(min_length=1)
    text: str = Field(min_length=5)

router = APIRouter()

@router.get("/docs")
async def docs(db: AsyncSession = Depends(get_db)):
    rows = await svc.list_docs(db)
    return {"docs": [{"id": d.id, "title": d.title, "chars": len(d.text)} for d in rows]}

@router.post("/docs")
async def add(payload: DocIn, db: AsyncSession = Depends(get_db)):
    d = await svc.add_doc(db, payload.title, payload.text); return {"id": d.id}

@router.get("/search")
async def search(q: str = Query(min_length=2), k: int = 5, db: AsyncSession = Depends(get_db)):
    return {"hits": await svc.search(db, q, k)}
