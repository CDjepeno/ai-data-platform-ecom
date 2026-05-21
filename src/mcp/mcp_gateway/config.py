"""
mcp_gateway/config.py

Centralized settings loaded from environment variables and .env file.

Why pydantic-settings?
  - All config is validated and typed at startup — fail fast, fail loud
  - No os.getenv() scattered across modules — single source of truth
  - .env file support out of the box — no extra libraries needed
  - AnyHttpUrl validates the URL format before we even try to connect

Singleton pattern:
  The `settings` object at the bottom of this file is imported everywhere.
  It is instantiated once when the module is first imported.
  If any required variable is missing, the process exits immediately
  with a clear ValidationError — not a cryptic AttributeError later.
"""

from __future__ import annotations

from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    All configuration for the MCP gateway service.

    Priority order (highest to lowest):
      1. Environment variables       (e.g. export FASTAPI_BASE_URL=...)
      2. .env file at project root   (src/mcp/.env)
      3. Default values defined here

    Required fields (no default) will raise ValidationError if missing.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        # Case-insensitive: FASTAPI_BASE_URL and fastapi_base_url both work
        case_sensitive=False,
        # Ignore extra env vars — don't crash on unrelated system variables
        extra="ignore",
    )

    # ── FastAPI target ─────────────────────────────────────────────────────────

    fastapi_base_url: AnyHttpUrl = Field(
        default="http://localhost:8000",
        description=(
            "Base URL of the FastAPI /ask service. "
            "In Docker: use the service name (e.g. http://fast_api:8000)."
        ),
    )

    mcp_http_timeout: float = Field(
        default=60.0,
        gt=0,
        description=(
            "Seconds before HTTP calls to FastAPI time out. "
            "Set higher than your LLM stream duration to avoid premature cuts."
        ),
    )

    # ── Slack credentials ──────────────────────────────────────────────────────

    slack_bot_token: str = Field(
        ...,  # required — no default
        description="Slack Bot OAuth token. Starts with xoxb-.",
    )

    slack_app_token: str = Field(
        ...,  # required — no default
        description=(
            "Slack App-level token for Socket Mode. "
            "Starts with xapp-. Generate at api.slack.com/apps → Socket Mode."
        ),
    )

    # ── Observability ──────────────────────────────────────────────────────────

    log_level: str = Field(
        default="INFO",
        description="Logging level: DEBUG | INFO | WARNING | ERROR | CRITICAL.",
    )


# ── Singleton ──────────────────────────────────────────────────────────────────
# Imported by server.py and bot.py.
# Instantiated once — ValidationError at import time if config is invalid.
settings = Settings()