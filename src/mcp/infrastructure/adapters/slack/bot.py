from __future__ import annotations

import asyncio
import re

from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler

from domain.errors import StreamError
from infrastructure.config import settings
from application.use_cases.ask_question_usecase import AskQuestionUseCase
from infrastructure.adapters.fast_api.ask_gateway_adapter import FastApiAskGatewayAdapter
from infrastructure.adapters.fast_api.http_stream_reader import HttpStreamReader
from infrastructure.adapters.slack.slack_step_callback import SlackStepCallback
from infrastructure.factory.client_factory import create_http_client
from infrastructure.logging.setup import configure_logging
from utils import get_logger

# ── Logging — configured before anything else ──────────────────────────────────
configure_logging(
    log_level=settings.log_level,
    json_logs=settings.json_logs,
)

logger = get_logger(__name__)


# ── Slack app ──────────────────────────────────────────────────────────────────

def build_app() -> tuple[AsyncApp, HttpStreamReader]:

    app = AsyncApp(token=settings.slack_bot_token)

    http_client = create_http_client(settings)
    reader = HttpStreamReader(http_client=http_client)

    # ── Event handlers ─────────────────────────────────────────────────────────

    @app.event("app_mention")
    async def handle_mention(event: dict, say) -> None:  # type: ignore[type-arg]

        user_id: str = event.get("user", "unknown")
        channel: str = event["channel"]
        raw_text: str = event.get("text", "")

        question = _strip_mention(raw_text)

        if not question:
            await say(
                text="Please include a question. Example: _@bot What were sales last month?_",
                thread_ts=event.get("ts"),
            )
            return

        logger.info(
            "app_mention | user=%s | question=%r",
            user_id,
            question[:80],
        )

        # Post placeholder — user sees immediate feedback
        placeholder = await say(
            text="⏳ Thinking...",
            thread_ts=event["ts"],
        )
        placeholder_ts: str = placeholder["ts"]

        # Build use case with real SlackStepCallback for this event
        gateway  = FastApiAskGatewayAdapter(stream_reader=reader)
        callback = SlackStepCallback(
            app=app,
            channel=channel,
            placeholder_ts=placeholder_ts,
        )
        use_case = AskQuestionUseCase(gateway=gateway, callback=callback)

        try:
            answer = await use_case.execute(
                question=question,
                user_id=user_id,
            )
        except StreamError as exc:
            logger.error("Stream error | user=%s | %s", user_id, exc)
            answer = f"Sorry, something went wrong: {exc}"
        except Exception:
            logger.exception("Unexpected error | user=%s", user_id)
            answer = "Sorry, an unexpected error occurred. Please try again."

        # Replace placeholder with the final answer
        try:
            await app.client.chat_update(
                channel=channel,
                ts=placeholder_ts,
                text=answer,
            )
        except Exception:
            # Fallback — post new message if update fails
            logger.warning(
                "chat_update failed, posting new message | user=%s",
                user_id,
                exc_info=True,
            )
            await say(text=answer, thread_ts=event["ts"])

    @app.event("message")
    async def handle_message_events(body: dict, logger) -> None:  # type: ignore[type-arg]
        """
        Catch-all for non-mention message events.
        Without this, Slack Bolt logs a warning for every unhandled message.
        """
        pass

    return app, reader


# ── Helpers ────────────────────────────────────────────────────────────────────

def _strip_mention(text: str) -> str:
    """
    Remove the <@UXXX> bot mention prefix from a Slack message.

    Example:
        "<@U12345ABC> What were sales last month?"
        → "What were sales last month?"
    """
    return re.sub(r"^<@[A-Z0-9]+>\s*", "", text).strip()


# ── Entry points ───────────────────────────────────────────────────────────────

async def main() -> None:
    """
    Start the Slack bot in Socket Mode.

    Socket Mode: persistent WebSocket to Slack servers.
    No public URL needed — works behind any firewall.
    """
    logger.info("Starting Slack bot in Socket Mode")

    app, reader = build_app()
    handler = AsyncSocketModeHandler(
        app=app,
        app_token=settings.slack_app_token,
    )

    try:
        await handler.start_async()
    finally:
        await reader._client.aclose()  # type: ignore[attr-defined]
        logger.info("Slack bot stopped")


def main_sync() -> None:
    """Sync entry point for `poetry run slack-bot`."""
    asyncio.run(main())