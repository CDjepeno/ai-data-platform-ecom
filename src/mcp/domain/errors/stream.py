from __future__ import annotations


class StreamError(Exception):
    """
    Base class for all SSE stream domain errors.

    Catching StreamError catches any stream-related failure —
    useful at the application layer when you don't need to
    distinguish between subtypes.

    Example:
        try:
            answer = await consume_sse_stream(response)
        except StreamError as exc:
            return error_result(str(exc))
    """


class StreamErrorSignal(StreamError):
    """
    Raised when the FastAPI SSE stream explicitly signals a failure
    via a 'data: [ERROR] <message>' line.

    This means the server-side pipeline (LangGraph, Trino, LLM) failed
    and communicated it through the stream protocol.

    Attributes:
        server_message: The raw error message sent by FastAPI.

    Example:
        # Stream contained: "data: [ERROR] LangGraph timeout after 30s"
        raise StreamErrorSignal("LangGraph timeout after 30s")
    """

    def __init__(self, server_message: str) -> None:
        self.server_message = server_message
        super().__init__(f"FastAPI stream error: {server_message}")


class EmptyStreamError(StreamError):
    """
    Raised when the SSE stream closes without producing any LLM tokens.

    This can happen when:
      - The pipeline completed but the LLM produced no output
      - All stream lines were [STEP] markers with no actual tokens
      - The stream was cut before any tokens arrived

    Attributes:
        step_count: Number of [STEP] markers received before stream closed.
                    Useful for diagnosing where the pipeline stopped.

    Example:
        # Stream had 2 [STEP] markers but zero tokens
        raise EmptyStreamError(step_count=2)
    """

    def __init__(self, step_count: int = 0) -> None:
        self.step_count = step_count
        super().__init__(
            f"Stream closed with no LLM tokens "
            f"({step_count} step marker{'s' if step_count != 1 else ''} received)."
        )