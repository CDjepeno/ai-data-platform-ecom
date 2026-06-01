from __future__ import annotations

from collections.abc import AsyncIterator

import httpx

from utils import get_logger

logger = get_logger(__name__)


class HttpStreamReader:

    def __init__(self, http_client: httpx.AsyncClient) -> None:
        self._client = http_client

    async def stream_lines(
        self,
        path: str,
        payload: dict,
    ) -> AsyncIterator[str]:

        logger.debug("HttpStreamReader.stream_lines | path=%s", path)

        try:
            async with self._client.stream(
                "POST",
                path,
                json=payload,
            ) as response:

                # Check status INSIDE the context manager —
                # stream is still open here so aread() works.
                if response.status_code >= 400:
                    await response.aread()
                    logger.error(
                        "HTTP error | path=%s | status=%d | body=%s",
                        path,
                        response.status_code,
                        response.text[:200],
                    )
                    raise RuntimeError(
                        f"HTTP {response.status_code} from {path}."
                    )

                async for line in response.aiter_lines():
                    yield line

        except httpx.RequestError as exc:
            logger.error("HTTP unreachable | path=%s | %s", path, exc)
            raise RuntimeError(
                f"Could not reach {path}: {exc}"
            ) from exc