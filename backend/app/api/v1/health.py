"""System health endpoints (liveness and readiness)."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Response
from sqlalchemy import text

from app.core.config import get_settings
from app.db.session import engine

logger = logging.getLogger(__name__)

router = APIRouter(tags=["system"])


@router.get("/health")
async def health() -> dict[str, str]:
    settings = get_settings()
    return {
        "status": "ok",
        "app": settings.app_name,
        "version": settings.app_version,
    }


@router.get("/ready")
async def ready(response: Response) -> dict[str, object]:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except Exception:  # noqa: BLE001 - readiness must not crash
        logger.warning("Readiness check failed: database unreachable")
        response.status_code = 503
        return {
            "status": "degraded",
            "checks": {"database": "down"},
        }
    return {
        "status": "ok",
        "checks": {"database": "up"},
    }
