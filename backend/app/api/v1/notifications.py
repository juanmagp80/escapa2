"""Device registration API for push notifications."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from pydantic import BaseModel, Field

from app.api.deps import get_notification_service
from app.domain.notification import DeviceRegistration
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/devices", tags=["notifications"])

NotificationServiceDep = Annotated[NotificationService, Depends(get_notification_service)]


class RegisterDeviceRequest(BaseModel):
    """Body for POST /devices."""

    token: str = Field(..., min_length=10, max_length=500)
    platform: str = Field(default="android", min_length=1, max_length=30)


class DeviceResponse(BaseModel):
    """Registered device returned by the API."""

    id: str
    user_id: str
    token: str
    platform: str


def _user_key() -> str:
    """User identifier for quota and cache. Dev user until auth lands."""
    return "dev-user"


def _to_response(device: DeviceRegistration) -> DeviceResponse:
    return DeviceResponse(
        id=str(device.id),
        user_id=device.user_id,
        token=device.token,
        platform=device.platform,
    )


@router.post("", response_model=DeviceResponse, status_code=status.HTTP_201_CREATED)
def register_device(
    request: RegisterDeviceRequest,
    service: NotificationServiceDep,
) -> DeviceResponse:
    """Register (or refresh) a push token for the current user."""
    return _to_response(service.register_device(_user_key(), request.token, request.platform))


@router.delete("/{token}", status_code=status.HTTP_204_NO_CONTENT)
def unregister_device(
    token: str,
    service: NotificationServiceDep,
) -> Response:
    """Remove a push token for the current user."""
    service.unregister_device(_user_key(), token)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
