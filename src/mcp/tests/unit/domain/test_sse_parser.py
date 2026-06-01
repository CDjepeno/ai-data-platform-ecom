from __future__ import annotations

import pytest

from domain.errors.stream import StreamErrorSignal
from domain.services.sse_parser import parse_sse_line
from domain.tools.sse import SseEmpty, SseStep, SseToken

# ── SseEmpty cases ─────────────────────────────────────────────────────────────

class TestSseEmpty:

    def test_empty_string_returns_sse_empty(self) -> None:
        assert isinstance(parse_sse_line(""), SseEmpty)

    def test_whitespace_only_returns_sse_empty(self) -> None:
        assert isinstance(parse_sse_line("   "), SseEmpty)

    def test_newline_only_returns_sse_empty(self) -> None:
        assert isinstance(parse_sse_line("\n"), SseEmpty)

    def test_event_field_returns_sse_empty(self) -> None:
        # SSE fields other than 'data:' are ignored
        assert isinstance(parse_sse_line("event: ping"), SseEmpty)

    def test_id_field_returns_sse_empty(self) -> None:
        assert isinstance(parse_sse_line("id: 42"), SseEmpty)

    def test_retry_field_returns_sse_empty(self) -> None:
        assert isinstance(parse_sse_line("retry: 3000"), SseEmpty)


# ── SseStep cases ──────────────────────────────────────────────────────────────

class TestSseStep:

    def test_step_line_returns_sse_step(self) -> None:
        result = parse_sse_line("data: [STEP] 🧠 Understanding your request...")
        assert isinstance(result, SseStep)

    def test_step_message_is_extracted(self) -> None:
        result = parse_sse_line("data: [STEP] 🧠 Understanding your request...")
        assert isinstance(result, SseStep)
        assert result.message == "🧠 Understanding your request..."

    def test_step_message_is_stripped(self) -> None:
        result = parse_sse_line("data: [STEP]    padded message   ")
        assert isinstance(result, SseStep)
        assert result.message == "padded message"

    def test_step_with_emoji(self) -> None:
        result = parse_sse_line("data: [STEP] 📊 Query completed")
        assert isinstance(result, SseStep)
        assert result.message == "📊 Query completed"

    def test_step_completed(self) -> None:
        result = parse_sse_line("data: [STEP] ✅ Response completed")
        assert isinstance(result, SseStep)
        assert result.message == "✅ Response completed"


# ── SseToken cases ─────────────────────────────────────────────────────────────

class TestSseToken:

    def test_data_line_returns_sse_token(self) -> None:
        result = parse_sse_line("data: hello world")
        assert isinstance(result, SseToken)

    def test_token_content_is_extracted(self) -> None:
        result = parse_sse_line("data: Les ventes de mars")
        assert isinstance(result, SseToken)
        assert result.token == "Les ventes de mars"

    def test_empty_data_prefix_returns_empty_token(self) -> None:
        # "data: " with nothing after = empty token — valid SSE
        result = parse_sse_line("data: ")
        assert isinstance(result, SseToken)
        assert result.token == ""

    def test_token_with_special_chars(self) -> None:
        result = parse_sse_line("data: 142 350€ (+12%)")
        assert isinstance(result, SseToken)
        assert result.token == "142 350€ (+12%)"

    def test_token_preserves_whitespace(self) -> None:
        # Whitespace in tokens is meaningful — don't strip
        result = parse_sse_line("data:  leading space")
        assert isinstance(result, SseToken)
        assert result.token == " leading space"


# ── StreamErrorSignal cases ────────────────────────────────────────────────────

class TestStreamErrorSignal:

    def test_error_line_raises_stream_error_signal(self) -> None:
        with pytest.raises(StreamErrorSignal):
            parse_sse_line("data: [ERROR] LangGraph timeout after 30s")

    def test_error_message_is_preserved(self) -> None:
        with pytest.raises(StreamErrorSignal) as exc_info:
            parse_sse_line("data: [ERROR] LangGraph timeout after 30s")
        assert exc_info.value.server_message == "LangGraph timeout after 30s"

    def test_error_str_representation(self) -> None:
        with pytest.raises(StreamErrorSignal) as exc_info:
            parse_sse_line("data: [ERROR] timeout")
        assert "timeout" in str(exc_info.value)

    def test_empty_error_message(self) -> None:
        with pytest.raises(StreamErrorSignal) as exc_info:
            parse_sse_line("data: [ERROR]")
        assert exc_info.value.server_message == ""