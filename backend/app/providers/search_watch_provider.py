"""Search watch provider contract."""

from __future__ import annotations

import uuid
from typing import Protocol

from app.domain.search_watch import SearchWatch


class SearchWatchProvider(Protocol):
    """Contract for sources that persist watched trip searches."""

    def list_watches(self) -> list[SearchWatch]:
        """Return all watches."""
        ...

    def get_watch(self, watch_id: uuid.UUID) -> SearchWatch | None:
        """Return a single watch or None when unknown."""
        ...

    def create_watch(self, watch: SearchWatch) -> SearchWatch:
        """Store a new watch and return the stored value."""
        ...

    def update_watch(self, watch: SearchWatch) -> SearchWatch:
        """Store an updated watch and return the stored value."""
        ...

    def delete_watch(self, watch_id: uuid.UUID) -> bool:
        """Delete a watch; return True when it existed."""
        ...
