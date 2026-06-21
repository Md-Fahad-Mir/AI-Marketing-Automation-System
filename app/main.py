"""FastAPI application entry point."""

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.campaigns import router as campaigns_router
from app.config import get_settings
from app.core.logging_config import configure_logging
from app.database.database import SessionLocal, init_db
from app.services.providers.image_base import IMAGE_URL_PATH
from app.services.scheduler_service import SchedulerService

configure_logging()
logger = logging.getLogger(__name__)

scheduler = SchedulerService(session_factory=SessionLocal)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize the database and run the scheduler for the app lifetime."""
    init_db()
    logger.info("Database initialized")
    scheduler.start()
    try:
        yield
    finally:
        await scheduler.stop()


app = FastAPI(title="AI Marketing Automation System", lifespan=lifespan)
app.include_router(campaigns_router)


@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    """Lightweight liveness probe for container / orchestrator health checks."""
    return {"status": "ok"}

# Serve locally generated marketing images (OpenAI / Gemini providers write here).
_image_dir = get_settings().image_storage_dir
os.makedirs(_image_dir, exist_ok=True)
app.mount(IMAGE_URL_PATH, StaticFiles(directory=_image_dir), name="generated-images")
