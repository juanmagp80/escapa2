"""In-memory device token registry for development and tests."""

from __future__ import annotations

from datetime import UTC, datetime

from app.domain.notification import DeviceRegistration


class MockDeviceRepository:
    """Keeps device tokens in memory, idempotent by token."""

    def __init__(self) -> None:
        self._devices: list[DeviceRegistration] = []

    def list_tokens(self, user_id: str) -> list[str]:
        return [device.token for device in self._devices if device.user_id == user_id]

    def register(self, device: DeviceRegistration) -> DeviceRegistration:
        now = datetime.now(UTC).replace(microsecond=0)
        for index, existing in enumerate(self._devices):
            if existing.token == device.token:
                updated = device.model_copy(update={"updated_at": now})
                self._devices[index] = updated
                return updated
        self._devices.append(device.model_copy(update={"updated_at": now}))
        return self._devices[-1]

    def unregister(self, user_id: str, token: str) -> bool:
        before = len(self._devices)
        self._devices = [
            device
            for device in self._devices
            if not (device.user_id == user_id and device.token == token)
        ]
        return len(self._devices) < before
