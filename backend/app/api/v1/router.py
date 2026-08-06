"""API v1 router aggregation."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.ai import router as ai_router
from app.api.v1.availability import router as availability_router
from app.api.v1.health import router as health_router
from app.api.v1.opportunities import router as opportunities_router
from app.api.v1.profile import router as profile_router
from app.api.v1.watches import router as watches_router

api_router = APIRouter()
api_router.include_router(ai_router)
api_router.include_router(availability_router)
api_router.include_router(health_router)
api_router.include_router(opportunities_router)
api_router.include_router(profile_router)
api_router.include_router(watches_router)
