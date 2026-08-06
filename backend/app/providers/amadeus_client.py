"""Thin httpx client for the Amadeus Self-Service API.

Only used when ``AMADEUS_ENABLED=true`` and valid credentials are configured.
It obtains an OAuth2 client-credentials token, caches it until it expires and
exposes typed HTTP helpers with strict timeouts. The domain never sees the raw
responses: providers map them into normalized domain models.
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime, timedelta

import httpx

from app.core.errors import ProviderUnavailableError

logger = logging.getLogger(__name__)

_DEFAULT_BASE_URL = "https://test.api.amadeus.com"


class AmadeusClient:
    """Authenticated httpx client for Amadeus Self-Service endpoints.

    A single ``httpx.Client`` is reused and a transport can be injected for
    tests (e.g. ``httpx.MockTransport``), so the provider is testable without
    network access.
    """

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        *,
        base_url: str = _DEFAULT_BASE_URL,
        timeout_seconds: float = 15.0,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self._client_id = client_id
        self._client_secret = client_secret
        self._base_url = base_url.rstrip("/")
        self._access_token: str | None = None
        self._token_expires_at: datetime | None = None
        self._client = httpx.Client(timeout=timeout_seconds, transport=transport)

    def get(self, path: str, params: dict[str, str | int]) -> httpx.Response:
        """Perform an authenticated GET, refreshing the token when needed."""
        if self._access_token is None or self._is_expired():
            self._refresh_token()
        request = httpx.Request(
            method="GET",
            url=f"{self._base_url}{path}",
            params=params,
            headers={"Authorization": f"Bearer {self._access_token}"},
        )
        response = self._client.send(request)
        return self._raise_for_status(response)

    def close(self) -> None:
        self._client.close()

    def _refresh_token(self) -> None:
        request = httpx.Request(
            method="POST",
            url=f"{self._base_url}/v1/security/oauth2/token",
            data={
                "grant_type": "client_credentials",
                "client_id": self._client_id,
                "client_secret": self._client_secret,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        try:
            response = self._client.send(request)
            response.raise_for_status()
            payload = response.json()
            self._access_token = str(payload["access_token"])
            expires_in = int(payload.get("expires_in", 1800))
            self._token_expires_at = datetime.now(UTC) + timedelta(seconds=expires_in)
        except (httpx.HTTPError, KeyError, ValueError) as exc:
            logger.warning("Amadeus token request failed: %s", exc)
            raise ProviderUnavailableError() from exc

    def _is_expired(self) -> bool:
        return self._token_expires_at is None or datetime.now(UTC) >= self._token_expires_at

    def _raise_for_status(self, response: httpx.Response) -> httpx.Response:
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code in (401, 403):
                self._access_token = None
            logger.warning(
                "Amadeus request failed status=%s path=%s",
                exc.response.status_code,
                exc.request.url.path if exc.request is not None else "unknown",
            )
            raise ProviderUnavailableError() from exc
        return response
