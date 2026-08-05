"""Tests for the AI provider factory."""

from __future__ import annotations

import pytest
from app.ai.factory import build_ai_provider
from app.ai.fake import FakeAiProvider
from app.ai.gemini import GeminiAiProvider
from app.core.config import Settings


def test_factory_returns_fake_when_gemini_disabled() -> None:
    provider = build_ai_provider(Settings(gemini_enabled=False))
    assert isinstance(provider, FakeAiProvider)


def test_factory_raises_when_enabled_without_key() -> None:
    with pytest.raises(RuntimeError, match="GEMINI_API_KEY"):
        build_ai_provider(Settings(gemini_enabled=True, gemini_api_key=""))


def test_factory_returns_gemini_when_enabled() -> None:
    provider = build_ai_provider(Settings(gemini_enabled=True, gemini_api_key="fake"))
    assert isinstance(provider, GeminiAiProvider)
