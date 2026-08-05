"""In-memory cache for AI responses keyed by request data and prompt version."""

from __future__ import annotations

import hashlib
import json
from typing import Any, TypeVar, cast

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)

PROMPT_VERSION = "1"


def cache_key(model: str, request: BaseModel) -> str:
    """Stable key for a prompt version plus the canonical request payload."""
    payload = json.dumps(
        request.model_dump(mode="json", exclude_none=True),
        sort_keys=True,
        separators=(",", ":"),
    )
    raw = f"{model}|{PROMPT_VERSION}|{payload}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


class AiResponseCache[T]:
    """Small in-memory LRU-style cache for validated AI responses."""

    def __init__(self, model: str, max_entries: int = 200) -> None:
        self._model = model
        self._max_entries = max_entries
        self._store: dict[str, dict[str, Any]] = {}

    def get(self, request: BaseModel) -> T | None:
        key = cache_key(self._model, request)
        entry = self._store.get(key)
        if entry is None:
            return None
        entry["_last_used"] += 1
        return cast("T", entry["response"])

    def set(self, request: BaseModel, response: BaseModel) -> None:
        key = cache_key(self._model, request)
        self._store[key] = {"response": response, "_last_used": 0}
        if len(self._store) > self._max_entries:
            self._evict()

    def _evict(self) -> None:
        if not self._store:
            return
        least_used = min(self._store, key=lambda key: self._store[key]["_last_used"])
        del self._store[least_used]

    def clear(self) -> None:
        self._store.clear()

    def __len__(self) -> int:
        return len(self._store)
