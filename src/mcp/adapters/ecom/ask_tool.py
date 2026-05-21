"""
adapters/ecom/ask_tool.py

Concrete MCP tool that calls the FastAPI /ask SSE endpoint,
consumes the full stream, and returns the assembled answer.

Stream protocol (from FastAPI):
  data: [STEP] <message>   → progress indicator, forwarded via on_step callback
  data: [ERROR] <message>  → server-side error, raises StreamError
  data: <token>            → LLM token, accumulated into the final answer

The on_step callback is optional — when provided (by the Slack bot),
it updates the "thinking..." placeholder message in real time.
When absent (e.g. in tests), steps are just logged.
"""

from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable
from typing import cast

import httpx
from mcp.types import CallToolResult, Tool
from pydantic import Field

from mcp_gateway.tools.base import AbstractTool, ToolInput, error_result, success_result

logger = logging.getLogger(__name__)

# ── SSE line prefixes ──────────────────────────────────────────────────────────

_SSE_DATA_PREFIX  = "data: "
_SSE_STEP_PREFIX  = "data: [STEP]"
_SSE_ERROR_PREFIX = "data: [ERROR]"

# Type alias — async callable that receives a step message and updates Slack
StepCallback = Callable[[str], Awaitable[None]]


# ── Custom exceptions ──────────────────────────────────────────────────────────

class StreamError(Exception):
    """Raised when FastAPI signals [ERROR] inside the SSE stream."""


# ── Input schema ───────────────────────────────────────────────────────────────

class AskToolInput(ToolInput):
    """Validated input for the ask_question tool."""

    question: str = Field(
        ...,
        min_length=3,
        max_length=2000,
        description="Natural language business question.",
    )
    user_id: str = Field(
        ...,
        description="Slack user ID — used for audit trail in logs.",
    )


# ── SSE parsing (pure function — easy to unit test) ───────────────────────────

class SseLine:
    """Typed result of parsing one SSE line."""
    __slots__ = ()

class SseStep(SseLine):
    def __init__(self, message: str) -> None:
        self.message = message

class SseToken(SseLine):
    def __init__(self, token: str) -> None:
        self.token = token

class SseEmpty(SseLine):
    pass


def _parse_sse_line(line: str) -> SseLine:
    """
    Parse a single raw SSE line into a typed result.

    Returns:
        SseEmpty  — heartbeat or non-data field (skip)
        SseStep   — [STEP] progress marker
        SseToken  — LLM token to accumulate
        raises StreamError if the line is an [ERROR] marker
    """
    if not line.strip():
        return SseEmpty()

    if line.startswith(_SSE_STEP_PREFIX):
        message = line[len(_SSE_STEP_PREFIX):].strip()
        return SseStep(message)

    if line.startswith(_SSE_ERROR_PREFIX):
        error_msg = line[len(_SSE_ERROR_PREFIX):].strip()
        raise StreamError(f"FastAPI stream error: {error_msg}")

    if line.startswith(_SSE_DATA_PREFIX):
        return SseToken(line[len(_SSE_DATA_PREFIX):])

    return SseEmpty()


async def _consume_sse_stream(
    response: httpx.Response,
    on_step: StepCallback | None = None,
) -> str:
    """
    Consume the full SSE stream and assemble LLM tokens into a single string.

    Args:
        response: httpx.Response in streaming mode.
        on_step:  Optional async callback — called with each [STEP] message.
                  Use this to update a Slack "thinking..." placeholder in real time.

    Returns:
        The full assembled answer from the LLM tokens.

    Raises:
        StreamError: if [ERROR] appears in the stream, or stream is empty.
    """
    tokens: list[str] = []

    async for raw_line in response.aiter_lines():
        parsed = _parse_sse_line(raw_line)

        if isinstance(parsed, SseStep):
            logger.debug("SSE step: %s", parsed.message)
            if on_step is not None:
                # Update the Slack placeholder — fire and forget errors
                try:
                    await on_step(f"⏳ {parsed.message}")
                except Exception:
                    logger.warning("on_step callback failed", exc_info=True)

        elif isinstance(parsed, SseToken):
            tokens.append(parsed.token)

        # SseEmpty → skip silently

    answer = "".join(tokens).strip()

    if not answer:
        raise StreamError("Stream completed but no answer tokens were received.")

    return answer


# ── Concrete tool ──────────────────────────────────────────────────────────────

class AskTool(AbstractTool):
    """
    MCP tool: forwards the user's question to FastAPI /ask (SSE),
    collects all LLM tokens, and returns the assembled answer.

    The on_step callback is optional — inject it from the Slack bot
    to update a "thinking..." message in real time during the stream.

    Args:
        http_client: Shared httpx.AsyncClient — injected by the server.
        on_step:     Optional async callback(message: str) called on each
                     [STEP] event. When None, steps are only logged.
    """

    def __init__(
        self,
        http_client: httpx.AsyncClient,
        on_step: StepCallback | None = None,
    ) -> None:
        self._client = http_client
        self._on_step = on_step

    # ── AbstractTool interface ─────────────────────────────────────────────────

    @property
    def input_schema(self) -> type[ToolInput]:
        return AskToolInput

    @property
    def definition(self) -> Tool:
        return Tool(
            name="ask_question",
            description=(
                "Ask a natural language business question about ecom data. "
                "The AI pipeline queries the semantic layer (dbt MetricFlow), "
                "retrieves context from Qdrant, and runs Trino queries if needed. "
                "Returns a complete answer assembled from the LLM stream."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "Business question in natural language.",
                        "minLength": 3,
                        "maxLength": 2000,
                    },
                    "user_id": {
                        "type": "string",
                        "description": "Slack user ID for audit.",
                    },
                },
                "required": ["question", "user_id"],
            },
        )

    async def _execute(self, validated: ToolInput) -> CallToolResult:
        inp = cast(AskToolInput, validated)

        logger.info(
            "Calling FastAPI /ask | user=%s | question=%r",
            inp.user_id,
            inp.question[:80],
        )

        try:
            async with self._client.stream(
                "POST",
                "/ask",
                json={"question": inp.question},
            ) as response:

                # Check status BEFORE consuming the stream.
                # Inside stream(), raise_for_status() raises HTTPStatusError but
                # the response body stream is already open — we can still read it.
                # Checking status_code directly avoids the raise/catch dance
                # and lets us aread() cleanly while the stream is still open.
                if response.status_code >= 400:
                    await response.aread()
                    logger.error(
                        "FastAPI HTTP error | status=%s | body=%s",
                        response.status_code,
                        response.text[:200],
                    )
                    return error_result(
                        f"FastAPI returned HTTP {response.status_code}."
                    )

                try:
                    answer = await _consume_sse_stream(
                        response,
                        on_step=self._on_step,
                    )
                except StreamError as exc:
                    logger.error("SSE stream error | user=%s | %s", inp.user_id, exc)
                    return error_result(str(exc))

        except httpx.RequestError as exc:
            logger.error("FastAPI unreachable | %s", exc)
            return error_result(f"Could not reach FastAPI: {exc}")

        logger.info(
            "Answer assembled | user=%s | length=%d chars",
            inp.user_id,
            len(answer),
        )

        return success_result(answer)