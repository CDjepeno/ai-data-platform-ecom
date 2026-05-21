"""
ports/step_callback.py

Port — abstract contract for notifying progress steps.

What this port solves:
  During the SSE stream, FastAPI sends [STEP] progress markers.
  The use case needs to forward them somewhere — but it must not
  know WHERE they go (Slack, logs, a WebSocket, a progress bar...).

  This port abstracts the "notify someone about progress" concern.

Why a port and not just a callable?
  A typed abstract class is:
    - Explicitly documented (docstring, type hints)
    - Mockable with standard ABC patterns
    - Extensible (add methods like on_complete, on_error later)
    - Visible in the architecture — ports/ is a map of all I/O contracts

  A raw Callable[[str], Awaitable[None]] works too but is invisible
  in the architecture — you'd never know it exists without reading
  the use case code.

Implementations:
  adapters/slack/step_callback.py  → updates Slack message placeholder
  adapters/logging/step_callback.py → logs steps (useful for testing)
  tests/fakes/step_callback.py     → records calls for assertions
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class StepCallbackPort(ABC):
    """
    Contract for notifying the caller about pipeline progress.

    The application layer calls this port on each [STEP] SSE line.
    The implementation decides how to surface the progress to the user.

    Current implementations:
      Slack  → edits a "thinking..." placeholder message in real time
      Silent → does nothing (useful for CLI or background jobs)
    """

    @abstractmethod
    async def on_step(self, message: str) -> None:
        """
        Called when the AI pipeline emits a [STEP] progress marker.

        Must not raise — if the notification fails (e.g. Slack rate limit),
        the implementation should log the error and return silently.
        The LLM stream must never be interrupted by a notification failure.

        Args:
            message: Human-readable step description from the pipeline.
                     Example: "🧠 Understanding your request..."
        """
        ...

    @abstractmethod
    async def on_complete(self) -> None:
        """
        Called when the full answer has been assembled and is ready.

        Implementations use this to finalize the UI state —
        e.g. Slack replaces the last step message with the final answer.

        Must not raise — same contract as on_step.
        """
        ...