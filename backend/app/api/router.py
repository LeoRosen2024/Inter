from fastapi import APIRouter

from app.api.routes import competitors, health, imports, reels, settings


api_router = APIRouter()
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(reels.router, prefix="/reels", tags=["reels"])
api_router.include_router(competitors.router, prefix="/competitors", tags=["competitors"])
api_router.include_router(settings.router, prefix="/settings", tags=["settings"])
api_router.include_router(imports.router, prefix="/imports", tags=["imports"])

