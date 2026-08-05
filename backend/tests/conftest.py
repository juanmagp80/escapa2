"""Shared pytest fixtures."""

from __future__ import annotations

import os

os.environ.setdefault("GEMINI_ENABLED", "false")
os.environ.setdefault("APP_ENV", "test")

import pytest
from app.main import app
from fastapi.testclient import TestClient


@pytest.fixture
def client() -> TestClient:
    with TestClient(app) as test_client:
        yield test_client
