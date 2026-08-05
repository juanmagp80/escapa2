"""AI provider factory resolved from settings."""

from __future__ import annotations

from app.ai.fake import FakeAiProvider
from app.ai.gemini import GeminiAiProvider
from app.ai.protocol import AiProvider
from app.core.config import Settings


def build_ai_provider(settings: Settings) -> AiProvider:
    """Build the active AI provider.

    Raises RuntimeError if a provider is enabled but its credentials are missing.
    """
    if settings.gemini_enabled:
        if not settings.gemini_api_key:
            raise RuntimeError("GEMINI_ENABLED is true but GEMINI_API_KEY is not set.")
        return GeminiAiProvider(settings)
    return FakeAiProvider()
