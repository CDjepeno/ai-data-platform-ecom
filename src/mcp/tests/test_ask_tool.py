
from __future__ import annotations
 
from unittest.mock import AsyncMock
 
import httpx
import pytest
import respx
 
from adapters.ecom.ask_tool import (
    AskTool,
    AskToolInput,
    SseEmpty,
    SseStep,
    SseToken,
    StreamError,
    _parse_sse_line,
)
from mcp_gateway.tools.base import ToolInput
 
 
# ── Helpers ────────────────────────────────────────────────────────────────────
 
def _make_sse_body(*lines: str) -> bytes:
    """
    Build a fake SSE response body from a list of raw lines.
    Each line is joined with newline as the SSE protocol expects.
    """
    return "\n".join(lines).encode("utf-8")
 
 
def _text_from_result(result: object) -> str:
    """Extract text from the first content block of a CallToolResult."""
    content = getattr(result, "content", [])
    assert content
    return content[0].text
 
 
# ── Tests: _parse_sse_line (pure function) ─────────────────────────────────────
 
class TestParseSSELine:
 
    def test_empty_line_returns_sse_empty(self) -> None:
        assert isinstance(_parse_sse_line(""), SseEmpty)
 
    def test_whitespace_only_returns_sse_empty(self) -> None:
        assert isinstance(_parse_sse_line("   "), SseEmpty)
 
    def test_step_line_returns_sse_step(self) -> None:
        result = _parse_sse_line("data: [STEP] 🧠 Understanding...")
        assert isinstance(result, SseStep)
        assert result.message == "🧠 Understanding..."
 
    def test_token_line_returns_sse_token(self) -> None:
        result = _parse_sse_line("data: hello world")
        assert isinstance(result, SseToken)
        assert result.token == "hello world"
 
    def test_error_line_raises_stream_error(self) -> None:
        with pytest.raises(StreamError, match="something went wrong"):
            _parse_sse_line("data: [ERROR] something went wrong")
 
    def test_non_data_field_returns_sse_empty(self) -> None:
        # SSE fields like 'event:' or 'id:' are not data lines
        assert isinstance(_parse_sse_line("event: ping"), SseEmpty)
        assert isinstance(_parse_sse_line("id: 42"), SseEmpty)
        assert isinstance(_parse_sse_line("retry: 3000"), SseEmpty)
 
    def test_step_message_is_stripped(self) -> None:
        result = _parse_sse_line("data: [STEP]    padded message   ")
        assert isinstance(result, SseStep)
        assert result.message == "padded message"
 
    def test_empty_token_after_data_prefix(self) -> None:
        # "data: " with nothing after = empty token
        result = _parse_sse_line("data: ")
        assert isinstance(result, SseToken)
        assert result.token == ""
 
 
# ── Tests: AskTool via respx (HTTP mock) ──────────────────────────────────────
 
class TestAskTool:
    """
    Tests for AskTool using respx to intercept httpx calls.
 
    respx works at the httpx transport level — no real network,
    no monkey-patching, fully async-compatible.
    """
 
    FASTAPI_URL = "http://fast_api:8000"
 
    def _make_tool(self, on_step=None) -> tuple[AskTool, httpx.AsyncClient]:
        """Create an AskTool with an injected AsyncClient."""
        client = httpx.AsyncClient(base_url=self.FASTAPI_URL)
        tool = AskTool(http_client=client, on_step=on_step)
        return tool, client
 
    # ── Happy path ─────────────────────────────────────────────────────────────
 
    @respx.mock
    async def test_happy_path_assembles_tokens(self) -> None:
        """
        Full happy path: [STEP] lines are ignored,
        token lines are assembled into the final answer.
        """
        sse_body = _make_sse_body(
            "data: [STEP] 🧠 Understanding your request...",
            "data: [STEP] 📊 Query completed, generating insights...",
            "data: Les ventes ",
            "data: de mars ",
            "data: sont 142k€",
            "data: [STEP] ✅ Response completed",
        )
 
        respx.post(f"{self.FASTAPI_URL}/ask").mock(
            return_value=httpx.Response(200, content=sse_body)
        )
 
        tool, client = self._make_tool()
        async with client:
            result = await tool.execute({
                "question": "Quelles sont les ventes de mars ?",
                "user_id": "U12345",
            })
 
        assert result.isError is False
        answer = _text_from_result(result)
        assert "Les ventes" in answer
        assert "142k€" in answer
        # [STEP] markers must NOT appear in the answer
        assert "[STEP]" not in answer
        assert "Understanding" not in answer
 
    # ── on_step callback ───────────────────────────────────────────────────────
 
    @respx.mock
    async def test_on_step_called_for_each_step(self) -> None:
        """
        The on_step callback must be called once per [STEP] line,
        with the step message prefixed by ⏳.
        """
        sse_body = _make_sse_body(
            "data: [STEP] 🧠 Understanding your request...",
            "data: [STEP] 📊 Querying data...",
            "data: final answer",
        )
 
        respx.post(f"{self.FASTAPI_URL}/ask").mock(
            return_value=httpx.Response(200, content=sse_body)
        )
 
        # AsyncMock acts as an async spy — records every call
        on_step = AsyncMock()
 
        tool, client = self._make_tool(on_step=on_step)
        async with client:
            await tool.execute({
                "question": "Test question",
                "user_id": "U99",
            })
 
        # on_step called twice — once per [STEP]
        assert on_step.call_count == 2
        calls = [call.args[0] for call in on_step.call_args_list]
        assert any("Understanding" in c for c in calls)
        assert any("Querying" in c for c in calls)
 
    @respx.mock
    async def test_on_step_failure_does_not_cancel_stream(self) -> None:
        """
        If on_step raises (e.g. Slack rate limit), the stream must continue
        and the final answer must still be returned.
        """
        sse_body = _make_sse_body(
            "data: [STEP] 🧠 Step one",
            "data: the answer",
        )
 
        respx.post(f"{self.FASTAPI_URL}/ask").mock(
            return_value=httpx.Response(200, content=sse_body)
        )
 
        # on_step always raises — simulates Slack API failure
        async def failing_on_step(msg: str) -> None:
            raise RuntimeError("Slack rate limited")
 
        tool, client = self._make_tool(on_step=failing_on_step)
        async with client:
            result = await tool.execute({
                "question": "Test",
                "user_id": "U1",
            })
 
        # Answer is still returned despite on_step failure
        assert result.isError is False
        assert "the answer" in _text_from_result(result)
 
    # ── Error cases ────────────────────────────────────────────────────────────
 
    @respx.mock
    async def test_fastapi_500_returns_error_result(self) -> None:
        """HTTP 500 from FastAPI → error_result, not an exception."""
        respx.post(f"{self.FASTAPI_URL}/ask").mock(
            return_value=httpx.Response(500, text="Internal Server Error")
        )
 
        tool, client = self._make_tool()
        async with client:
            result = await tool.execute({
                "question": "Test",
                "user_id": "U1",
            })
 
        assert result.isError is True
        assert "500" in _text_from_result(result)
 
    @respx.mock
    async def test_fastapi_unreachable_returns_error_result(self) -> None:
        """Network error (FastAPI down) → error_result, not an exception."""
        respx.post(f"{self.FASTAPI_URL}/ask").mock(
            side_effect=httpx.ConnectError("Connection refused")
        )
 
        tool, client = self._make_tool()
        async with client:
            result = await tool.execute({
                "question": "Test",
                "user_id": "U1",
            })
 
        assert result.isError is True
        assert "Could not reach" in _text_from_result(result)
 
    @respx.mock
    async def test_stream_with_error_marker_returns_error_result(self) -> None:
        """[ERROR] in the SSE stream → error_result with the server message."""
        sse_body = _make_sse_body(
            "data: [STEP] 🧠 Understanding...",
            "data: [ERROR] LangGraph timeout after 30s",
        )
 
        respx.post(f"{self.FASTAPI_URL}/ask").mock(
            return_value=httpx.Response(200, content=sse_body)
        )
 
        tool, client = self._make_tool()
        async with client:
            result = await tool.execute({
                "question": "Test",
                "user_id": "U1",
            })
 
        assert result.isError is True
        assert "LangGraph timeout" in _text_from_result(result)
 
    @respx.mock
    async def test_empty_stream_returns_error_result(self) -> None:
        """Stream that closes with zero tokens → error_result."""
        sse_body = _make_sse_body(
            "data: [STEP] 🧠 Understanding...",
            # no tokens — stream ends here
        )
 
        respx.post(f"{self.FASTAPI_URL}/ask").mock(
            return_value=httpx.Response(200, content=sse_body)
        )
 
        tool, client = self._make_tool()
        async with client:
            result = await tool.execute({
                "question": "Test",
                "user_id": "U1",
            })
 
        assert result.isError is True
        assert "no answer tokens" in _text_from_result(result).lower()
 
    # ── Input validation ───────────────────────────────────────────────────────
 
    async def test_question_too_short_returns_error(self) -> None:
        """question min_length=3 — 'ab' must be rejected before hitting FastAPI."""
        tool, client = self._make_tool()
        async with client:
            result = await tool.execute({
                "question": "ab",  # 2 chars < min_length=3
                "user_id": "U1",
            })
 
        assert result.isError is True
        # No HTTP call should have been made
        assert "Invalid input" in _text_from_result(result)
 
    async def test_missing_user_id_returns_error(self) -> None:
        """user_id is required — missing it must be caught by Pydantic."""
        tool, client = self._make_tool()
        async with client:
            result = await tool.execute({"question": "What are sales?"})
 
        assert result.isError is True
        assert "Invalid input" in _text_from_result(result)
 




