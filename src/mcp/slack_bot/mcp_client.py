

from __future__ import annotations

import asyncio
import logging
from collections.abc import Awaitable, Callable

from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler

from mcp_gateway.config import Settings
from slack_bot.mcp_client import MCPClient

logger = logging.getLogger(__name__)


# ── Slack app factory ──────────────────────────────────────────────────────────

def build_app(settings: Settings) -> tuple[AsyncApp, MCPClient]:

    app = AsyncApp(token=settings.slack_bot_token)

    mcp_client = MCPClient(
        server_command=["python", "-m", "mcp_gateway.server"],
    )

    # ── Event handlers ─────────────────────────────────────────────────────────

    @app.event("app_mention")
    async def handle_mention(event: dict, say: Callable) -> None:  # type: ignore[type-arg]

        user_id: str = event.get("user", "unknown")
        channel: str = event["channel"]
        raw_text: str = event.get("text", "")

        # Remove the <@BOT_ID> mention prefix from the message
        question = _strip_mention(raw_text)

        if not question:
            await say(
                text="Please include a question after mentioning me. "
                     "Example: _@bot What were total sales last month?_",
                thread_ts=event.get("ts"),
            )
            return

        logger.info("app_mention | user=%s | question=%r", user_id, question[:80])

        # Step 1 — Post the placeholder immediately so the user sees a reaction
        # thread_ts=event["ts"] posts the answer as a thread reply,
        # keeping the channel clean.
        placeholder = await say(
            text="⏳ Thinking...",
            thread_ts=event["ts"],
        )
        placeholder_ts: str = placeholder["ts"]

        # Step 2 — Build the on_step callback that edits the placeholder
        # This closure captures channel + placeholder_ts — no globals needed.
        async def on_step(step_message: str) -> None:
            """Update the Slack placeholder with the current [STEP] message."""
            try:
                await app.client.chat_update(
                    channel=channel,
                    ts=placeholder_ts,
                    text=step_message,
                )
            except Exception:
                # Never let a Slack API hiccup cancel the LLM stream
                logger.warning(
                    "chat_update failed during step | user=%s",
                    user_id,
                    exc_info=True,
                )

        # Step 3 — Call MCP → FastAPI /ask SSE
        # on_step fires on each [STEP] event during the stream
        answer = await mcp_client.ask(
            question=question,
            user_id=user_id,
            on_step=on_step,
        )

        # Step 4 — Replace the placeholder with the final answer
        try:
            await app.client.chat_update(
                channel=channel,
                ts=placeholder_ts,
                text=answer,
            )
        except Exception:
            # Fallback: if update fails, post a new message
            logger.warning(
                "Final chat_update failed, posting new message | user=%s",
                user_id,
                exc_info=True,
            )
            await say(text=answer, thread_ts=event["ts"])

    @app.event("message")
    async def handle_message_events(body: dict, logger: logging.Logger) -> None:  # type: ignore[type-arg]

        pass  # intentionally empty

    return app, mcp_client


# ── Helpers ────────────────────────────────────────────────────────────────────

def _strip_mention(text: str) -> str:

    import re
    return re.sub(r"^<@[A-Z0-9]+>\s*", "", text).strip()


# ── Entry points ───────────────────────────────────────────────────────────────

async def main() -> None:

    settings = Settings()

    app, _ = build_app(settings)

    handler = AsyncSocketModeHandler(
        app=app,
        app_token=settings.slack_app_token,
    )

    logger.info("Starting Slack bot in Socket Mode")
    await handler.start_async()


def main_sync() -> None:

    asyncio.run(main())