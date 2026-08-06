"""Search watches API under the /api/v1/watches prefix."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Response, status

from app.api.deps import get_search_watch_service
from app.domain.search_watch import SearchWatch
from app.services.search_watch_service import (
    SearchWatchCreate,
    SearchWatchService,
    SearchWatchUpdate,
    WatchRunResult,
)

router = APIRouter(prefix="/watches", tags=["watches"])

SearchWatchServiceDep = Annotated[SearchWatchService, Depends(get_search_watch_service)]


@router.get("", response_model=list[SearchWatch])
def list_watches(service: SearchWatchServiceDep) -> list[SearchWatch]:
    """Return all watched trip searches."""
    return service.list_watches()


@router.post("", response_model=SearchWatch, status_code=status.HTTP_201_CREATED)
def create_watch(
    data: SearchWatchCreate,
    service: SearchWatchServiceDep,
) -> SearchWatch:
    """Create a new watched trip search."""
    return service.create(data)


@router.get("/{watch_id}", response_model=SearchWatch)
def get_watch(
    watch_id: uuid.UUID,
    service: SearchWatchServiceDep,
) -> SearchWatch:
    """Return a single watched search."""
    return service.get(watch_id)


@router.put("/{watch_id}", response_model=SearchWatch)
def update_watch(
    watch_id: uuid.UUID,
    data: SearchWatchUpdate,
    service: SearchWatchServiceDep,
) -> SearchWatch:
    """Update the mutable fields of a watched search."""
    return service.update(watch_id, data)


@router.delete("/{watch_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_watch(
    watch_id: uuid.UUID,
    service: SearchWatchServiceDep,
    response: Response,
) -> None:
    """Delete a watched search."""
    service.delete(watch_id)
    response.status_code = status.HTTP_204_NO_CONTENT


@router.post("/{watch_id}/run", response_model=WatchRunResult)
def run_watch(
    watch_id: uuid.UUID,
    service: SearchWatchServiceDep,
) -> WatchRunResult:
    """Run a watch: record price snapshots and evaluate configured alerts."""
    return service.run(watch_id)
