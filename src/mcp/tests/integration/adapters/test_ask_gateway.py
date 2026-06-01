
from __future__ import annotations

from collections.abc import AsyncIterator

import httpx
import pytest
import respx

from domain.errors import StreamErrorSignal
from domain.tools.sse import SseEmpty, SseStep, SseToken
from infrastructure.adapters.fast_api.ask_gateway_adapter import (
    FastApiAskGatewayAdapter,
)
from infrastructure.adapters.fast_api.http_stream_reader import HttpStreamReader

FASTAPI_URL = "http://fast_api:8000"


# ── Helpers ────────────────────────────────────────────────────────────────────

def _make_sse_body(*lines: str) -> bytes:
    """Build a fake SSE response body from raw lines."""
    return "\n".join(lines).encode("utf-8")


async def _collect(iterator: AsyncIterator) -> list:
    """Collect all items from an async iterator into a list."""
    return [item async for item in iterator]


def _make_gateway() -> tuple[FastApiAskGatewayAdapter, httpx.AsyncClient]:
    client = httpx.AsyncClient(base_url=FASTAPI_URL)
    reader = HttpStreamReader(http_client=client)
    gateway = FastApiAskGatewayAdapter(stream_reader=reader)
    return gateway, client


# ── Happy path ─────────────────────────────────────────────────────────────────

class TestHappyPath:

    @respx.mock
    async def test_yields_sse_step_for_step_lines(self) -> None:
        sse_body = _make_sse_body(
            "data: [STEP] 🧠 Understanding your request...",
            "data: answer token",
        )
        respx.post(f"{FASTAPI_URL}/ask").mock(
            return_value=httpx.Response(200, content=sse_body)
        )

        gateway, client = _make_gateway()
        async with client:
            lines = await _collect(gateway.stream("test question"))

        steps = [line for line in  lines if isinstance(line, SseStep)]
        assert len(steps) == 1
        assert steps[0].message == "🧠 Understanding your request..."

    @respx.mock
    async def test_yields_sse_token_for_data_lines(self) -> None:
        sse_body = _make_sse_body(
            "data: Les ventes ",
            "data: de mars",
        )
        respx.post(f"{FASTAPI_URL}/ask").mock(
            return_value=httpx.Response(200, content=sse_body)
        )

        gateway, client = _make_gateway()
        async with client:
            lines = await _collect(gateway.stream("test"))

        tokens = [line for line in lines if isinstance(line, SseToken)]
        assert len(tokens) == 2
        assert tokens[0].token == "Les ventes "
        assert tokens[1].token == "de mars"

    @respx.mock
    async def test_yields_sse_empty_for_blank_lines(self) -> None:
        sse_body = _make_sse_body(
            "",
            "data: answer",
            "",
        )
        respx.post(f"{FASTAPI_URL}/ask").mock(
            return_value=httpx.Response(200, content=sse_body)
        )

        gateway, client = _make_gateway()
        async with client:
            lines = await _collect(gateway.stream("test"))

        empty_lines = [line for line in lines if isinstance(line, SseEmpty)]
        assert len(empty_lines) == 1

    @respx.mock
    async def test_full_stream_sequence(self) -> None:
        """Verify the complete SSE stream from FastAPI /ask."""
        sse_body = _make_sse_body(
            "data: [STEP] 🧠 Understanding...",
            "data: [STEP] 📊 Querying...",
            "data: Les ventes ",
            "data: sont 142k€",
            "data: [STEP] ✅ Done",
        )
        respx.post(f"{FASTAPI_URL}/ask").mock(
            return_value=httpx.Response(200, content=sse_body)
        )

        gateway, client = _make_gateway()
        async with client:
            lines = await _collect(gateway.stream("Quelles sont les ventes ?"))

        steps  = [line for line in lines if isinstance(line, SseStep)]
        tokens = [line for line in lines if isinstance(line, SseToken)]

        assert len(steps) == 3
        assert len(tokens) == 2
        assert "".join(t.token for t in tokens) == "Les ventes sont 142k€"


# ── Error cases ────────────────────────────────────────────────────────────────

class TestErrorCases:

    @respx.mock
    async def test_error_line_raises_stream_error_signal(self) -> None:
        sse_body = _make_sse_body(
            "data: [STEP] 🧠 Understanding...",
            "data: [ERROR] LangGraph timeout after 30s",
        )
        respx.post(f"{FASTAPI_URL}/ask").mock(
            return_value=httpx.Response(200, content=sse_body)
        )

        gateway, client = _make_gateway()
        async with client:
            with pytest.raises(StreamErrorSignal) as exc_info:
                await _collect(gateway.stream("test"))

        assert "LangGraph timeout" in exc_info.value.server_message

    @respx.mock
    async def test_http_500_raises_runtime_error(self) -> None:
        respx.post(f"{FASTAPI_URL}/ask").mock(
            return_value=httpx.Response(500, text="Internal Server Error")
        )

        gateway, client = _make_gateway()
        async with client:
            with pytest.raises(RuntimeError) as exc_info:
                await _collect(gateway.stream("test"))

        assert "500" in str(exc_info.value)

    @respx.mock
    async def test_network_error_raises_runtime_error(self) -> None:
        respx.post(f"{FASTAPI_URL}/ask").mock(
            side_effect=httpx.ConnectError("Connection refused")
        )

        gateway, client = _make_gateway()
        async with client:
            with pytest.raises(RuntimeError) as exc_info:
                await _collect(gateway.stream("test"))

        assert "Could not reach" in str(exc_info.value)

    @respx.mock
    async def test_http_404_raises_runtime_error(self) -> None:
        respx.post(f"{FASTAPI_URL}/ask").mock(
            return_value=httpx.Response(404, text="Not Found")
        )

        gateway, client = _make_gateway()
        async with client:
            with pytest.raises(RuntimeError) as exc_info:
                await _collect(gateway.stream("test"))

        assert "404" in str(exc_info.value)