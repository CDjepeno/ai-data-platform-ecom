from typing import AsyncIterator, Mapping, TypedDict

import httpx
from sympy import primitive

from utils.logger import get_logger

logger = get_logger(__name__)


class HttpResponse(TypedDict):
    status_code: int
    text: str


class HttpxClient:

    def __init__(self):
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(
                connect=20.0,
                read=60.0,
                write=20.0,
                pool=10.0,
            )
        )

    async def get(
        self, url: str, headers: dict[str, str], params: dict[str, primitive]
    ) -> dict[str, object]:
        response = await self.client.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()

    async def post(
        self,
        url: str,
        headers: Mapping[str, str],
        body: str,
    ) -> HttpResponse:

        response = await self.client.post(url, headers=headers, content=body)
        logger.info(f"📡 Status code: {response.status_code}")

        logger.info(f"📦 Response body: {response.text}")
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

            async for line in response.aiter_lines():
                yield line
