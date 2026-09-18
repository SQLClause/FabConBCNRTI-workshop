"""Async client for the TMB developer APIs."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import aiohttp

logger = logging.getLogger(__name__)

DEFAULT_CONCURRENCY = 5
DEFAULT_TIMEOUT_SECONDS = 10
MAX_ATTEMPTS = 3
RETRYABLE_STATUS = {429, 500, 502, 503, 504}


class TmbApiError(RuntimeError):
    def __init__(self, status: int, path: str) -> None:
        super().__init__(f"TMB API returned {status} for {path}")
        self.status = status
        self.path = path


class TmbClient:
    def __init__(
        self,
        base_url: str,
        app_id: str,
        app_key: str,
        *,
        concurrency: int = DEFAULT_CONCURRENCY,
        timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    ) -> None:
        if not app_id or not app_key:
            raise ValueError("TMB_APP_ID and TMB_APP_KEY must be set")
        if not base_url.startswith("https://"):
            raise ValueError("TMB_API_BASE must be an https:// URL")

        self._base_url = base_url.rstrip("/")
        self._auth = {"app_id": app_id, "app_key": app_key}
        self._timeout = aiohttp.ClientTimeout(total=timeout_seconds)
        self._semaphore = asyncio.Semaphore(concurrency)
        self._session: aiohttp.ClientSession | None = None

    async def __aenter__(self) -> "TmbClient":
        self._session = aiohttp.ClientSession(timeout=self._timeout)
        return self

    async def __aexit__(self, *exc_info: Any) -> None:
        if self._session is not None:
            await self._session.close()
            self._session = None

    async def get(self, path: str, params: dict[str, str] | None = None) -> dict[str, Any]:
        if self._session is None:
            raise RuntimeError("TmbClient must be used as an async context manager")

        url = f"{self._base_url}/{path.lstrip('/')}"
        query = {**self._auth, **(params or {})}

        last_error: Exception | None = None
        for attempt in range(1, MAX_ATTEMPTS + 1):
            try:
                async with self._semaphore:
                    async with self._session.get(url, params=query) as response:
                        if response.status in RETRYABLE_STATUS:
                            raise TmbApiError(response.status, path)
                        response.raise_for_status()
                        return await response.json(content_type=None)
            except (aiohttp.ClientError, TmbApiError, asyncio.TimeoutError) as exc:
                last_error = exc
                if attempt == MAX_ATTEMPTS:
                    break
                await asyncio.sleep(2 ** (attempt - 1))

        raise TmbApiError(getattr(last_error, "status", 0), path) from last_error

    async def gather(
        self, requests: list[tuple[str, str, dict[str, str] | None]]
    ) -> list[tuple[str, dict[str, Any]]]:
        """Run requests concurrently and isolate individual failures."""

        async def one(key: str, path: str, params: dict[str, str] | None):
            try:
                return key, await self.get(path, params)
            except Exception:
                logger.warning("TMB request failed for %s (%s)", key, path, exc_info=True)
                return None

        results = await asyncio.gather(*(one(*request) for request in requests))
        return [result for result in results if result is not None]