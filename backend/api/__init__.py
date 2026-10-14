from fastapi import APIRouter
from backend.api import health, embed, ui
api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(embed.router, prefix="/api", tags=["embed"])
api_router.include_router(ui.router, tags=["ui"])
