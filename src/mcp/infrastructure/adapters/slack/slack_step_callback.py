from __future__ import annotations

from slack_bolt.async_app import AsyncApp

from domain.ports import StepCallbackPort
from utils import get_logger

logger = get_logger(__name__)


class SlackStepCallback(StepCallbackPort):
    """
    Implements StepCallbackPort by editing a Slack message placeholder.

    UX flow:
      1. Bot posts "⏳ Thinking..."           ← placeholder (done in bot.py)
      2. on_step("🧠 Understanding...")       ← edits the placeholder
      3. on_step("📊 Querying data...")       ← edits again
      4. on_complete()                        ← signals answer is ready
      5. Bot replaces with the final answer   ← done in bot.py after execute()

    Why on_complete() doesn't post the answer:
      The use case returns the answer string — the bot decides how to
      display it. The callback only manages the progress UX, not the result.

    Args:
        app:            Slack Bolt AsyncApp — used to call chat.update.
        channel:        Slack channel ID where the placeholder was posted.
        placeholder_ts: Timestamp of the placeholder message to edit.
                        Obtained from the initial say() call in bot.py.
    """

    def __init__(
        self,
        app: AsyncApp,
        channel: str,
        placeholder_ts: str,
    ) -> None:
        self._app = app
        self._channel = channel
        self._placeholder_ts = placeholder_ts

    async def on_step(self, message: str) -> None:

        try:
            await self._app.client.chat_update(
                channel=self._channel,
                ts=self._placeholder_ts,
                text=f"⏳ {message}",
            )
            logger.debug("Slack step updated | message=%r", message)

        except Exception:
            # Never let Slack failures interrupt the LLM stream
            logger.warning(
                "Slack chat_update failed on_step | channel=%s | ts=%s",
                self._channel,
                self._placeholder_ts,
                exc_info=True,
            )

    async def on_complete(self) -> None:

        try:
            await self._app.client.chat_update(
                channel=self._channel,
                ts=self._placeholder_ts,
                text="✅ Done",
            )
            logger.debug(
                "Slack on_complete | channel=%s | ts=%s",
                self._channel,
                self._placeholder_ts,
            )

        except Exception:
            logger.warning(
                "Slack chat_update failed on_complete | channel=%s | ts=%s",
                self._channel,
                self._placeholder_ts,
                exc_info=True,
            )