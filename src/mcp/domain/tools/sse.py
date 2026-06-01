from __future__ import annotations

# ── SSE protocol constants ─────────────────────────────────────────────────────
# Exported so sse_parser.py can import them without circular dependency.

SSE_DATA_PREFIX  = "data: "
SSE_STEP_PREFIX  = "data: [STEP]"
SSE_ERROR_PREFIX = "data: [ERROR]"


# ── Value Objects ──────────────────────────────────────────────────────────────

class SseLine:
    """
    Base class for all SSE line Value Objects.

    Value Object rules applied here:
      - Immutable  : __slots__ prevents adding attributes after creation
      - No identity: two SseToken("hello") are conceptually equal
      - Descriptive: each subclass describes what an SSE line IS
    """
    __slots__ = ()


class SseEmpty(SseLine):
    """
    An empty line or SSE heartbeat.

    The SSE spec requires servers to send periodic empty lines
    to keep the connection alive. These carry no business meaning
    and must be silently ignored by consumers.
    """
    __slots__ = ()

    def __repr__(self) -> str:
        return "SseEmpty()"


class SseStep(SseLine):
    """
    A [STEP] progress marker sent by the FastAPI pipeline.

    Represents UI feedback from the server — the pipeline is alive
    and processing. Must NOT appear in the final answer to the user.

    Attributes:
        message: Human-readable step description.
                 Example: "🧠 Understanding your request..."
    """
    __slots__ = ("message",)

    def __init__(self, message: str) -> None:
        self.message = message

    def __repr__(self) -> str:
        return f"SseStep({self.message!r})"


class SseToken(SseLine):
    """
    A single LLM response token from the stream.

    Tokens arrive one by one and must be accumulated in order
    to reconstruct the full answer.

    Attributes:
        token: The raw token string.
               May be a word fragment, punctuation, or whitespace.
    """
    __slots__ = ("token",)

    def __init__(self, token: str) -> None:
        self.token = token

    def __repr__(self) -> str:
        return f"SseToken({self.token!r})"