from typing import AsyncIterator, Mapping, TypedDict, Any

import httpx

from utils.logger import get_logger

logger = get_logger(__name__)


class HttpResponse(TypedDict):
    status_code: int
    text: str


class HttpxClient:

    def __init__(self):

        limits = httpx.Limits(
            max_connections=100,
            max_keepalive_connections=20,
            keepalive_expiry=30.0,
        )

        timeout = httpx.Timeout(
            connect=10.0,
            read=300.0,
            write=30.0,
            pool=30.0,
        )

        self.client = httpx.AsyncClient(
            timeout=timeout,
            limits=limits,
            http2=True,
        )

    async def get(
        self,
        url: str,
        headers: dict[str, str],
        params: dict[str, Any],
    ) -> dict[str, object]:

        response = await self.client.get(
            url,
            headers=headers,
            params=params,
        )

        response.raise_for_status()

        return response.json()

    async def post(
        self,
        url: str,
        headers: Mapping[str, str],
        json_body: dict[str, object],
    ) -> HttpResponse:

        response = await self.client.post(
            url,
            headers=headers,
            json=json_body,
        )

        response.raise_for_status()

        return {
            "status_code": response.status_code,
            "text": response.text,
        }

    async def stream(
        self,
        url: str,
        headers: Mapping[str, str],
        json_body: dict[str, object],
    ) -> AsyncIterator[str]:

        async with self.client.stream(
            "POST",
            url,
            headers=headers,
            json=json_body,
        ) as response:

            logger.info(f"📡 Streaming started: {response.status_code}")

            response.raise_for_status()

            async for chunk in response.aiter_text():

                if chunk:
                    yield chunk

    async def close(self):

        await self.client.aclose()