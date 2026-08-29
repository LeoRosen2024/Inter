from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    application = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST", "PUT", "PATCH", "OPTIONS"],
        allow_headers=["Accept", "Content-Type"],
    )
    application.include_router(api_router, prefix=settings.api_prefix)

    @application.get("/api", include_in_schema=False)
    def api_information() -> dict[str, str]:
        return {"name": settings.app_name, "docs": "/api/docs", "status": "ok"}

    return application


app = create_app()

