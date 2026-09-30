from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.errors.handlers import register_exception_handlers
from app.middleware.request_id import RequestIdMiddleware
from app.routers.links import analytics_router, public_router, router as links_router


app = FastAPI(title="URL Shortener API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.cors_allowed_origins),
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestIdMiddleware)
register_exception_handlers(app)
app.include_router(links_router, prefix="/api/v1")
app.include_router(analytics_router, prefix="/api/v1")


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(public_router)