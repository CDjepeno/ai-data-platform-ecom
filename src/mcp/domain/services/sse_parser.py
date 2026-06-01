
from __future__ import annotations

from domain.errors.stream import StreamErrorSignal
from domain.tools.sse import (
    SSE_DATA_PREFIX,
    SSE_ERROR_PREFIX,
    SSE_STEP_PREFIX,
    SseEmpty,
    SseLine,
    SseStep,
    SseToken,
)


def parse_sse_line(line: str) -> SseLine:
    """
    Parse a single raw SSE line into a typed Value Object.

    This is a pure function — a core property of Domain Services:
      - No side effects
      - No external state
      - Same input always produces the same output
      - Trivially unit-testable with plain assert statements

    Parsing rules (SSE protocol as implemented by FastAPI /ask):
      ""              → SseEmpty  (heartbeat, part of SSE spec)
      "data: [STEP]"  → SseStep   (progress marker, UI feedback only)
      "data: [ERROR]" → raises StreamErrorSignal (pipeline failed)
      "data: <token>" → SseToken  (LLM token to accumulate)
      "event: ..."    → SseEmpty  (other SSE fields, ignored)

    Args:
        line: A single raw line from the SSE response stream,
              without trailing newline characters.

    Returns:
        SseEmpty  — heartbeat or unrecognized SSE field, caller skips it
        SseStep   — progress marker, caller forwards to on_step callback
        SseToken  — LLM token, caller accumulates into the final answer

    Raises:
        StreamErrorSignal: when the line contains a [ERROR] marker,
                           meaning the FastAPI pipeline explicitly failed.
                           Caller should stop consuming and surface the error.

    Examples:
        >>> parse_sse_line("")
        SseEmpty()

        >>> parse_sse_line("   ")
        SseEmpty()

        >>> parse_sse_line("data: [STEP] 🧠 Understanding your request...")
        SseStep('🧠 Understanding your request...')

        >>> parse_sse_line("data: Les ventes de mars")
        SseToken('Les ventes de mars')

        >>> parse_sse_line("data: [ERROR] LangGraph timeout after 30s")
        # raises StreamErrorSignal("LangGraph timeout after 30s")

        >>> parse_sse_line("event: ping")
        SseEmpty()
    """
    # Empty lines are SSE heartbeats — part of the protocol, always ignore
    if not line.strip():
        return SseEmpty()

    # [STEP] progress marker — extract the message after the prefix
    if line.startswith(SSE_STEP_PREFIX):
        message = line[len(SSE_STEP_PREFIX):].strip()
        return SseStep(message)

    # [ERROR] server-side failure — raise immediately, stop consuming
    if line.startswith(SSE_ERROR_PREFIX):
        error_msg = line[len(SSE_ERROR_PREFIX):].strip()
        raise StreamErrorSignal(error_msg)

    # Regular data line — strip "data: " prefix to get the raw token
    if line.startswith(SSE_DATA_PREFIX):
        return SseToken(line[len(SSE_DATA_PREFIX):])

    # Non-data SSE fields (event:, id:, retry:) — ignore silently
    return SseEmpty()