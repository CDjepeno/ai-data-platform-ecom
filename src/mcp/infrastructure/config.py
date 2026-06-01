
from __future__ import annotations
 
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
 
 
class Settings(BaseSettings):
    """All configuration for the MCP gateway service."""
 
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
 
    # ── FastAPI target ─────────────────────────────────────────────────────────
 
    fastapi_base_url: str = Field(
        default="http://localhost:8000",
        description=(
            "Base URL of the FastAPI /ask service. "
            "In Docker Compose: use service name (http://fast_api:8000)."
        ),
    )
 
    mcp_http_timeout: float = Field(
        default=60.0,
        gt=0,
        description=(
            "Seconds before HTTP calls to FastAPI time out. "
            "Must be higher than your LLM stream duration."
        ),
    )
 
    # ── Slack credentials ──────────────────────────────────────────────────────
 
    slack_bot_token: str = Field(
        ...,
        description="Slack Bot OAuth token. Starts with xoxb-.",
    )
 
    slack_app_token: str = Field(
        ...,
        description=(
            "Slack App-level token for Socket Mode. "
            "Starts with xapp-."
        ),
    )
 
    # ── Observability ──────────────────────────────────────────────────────────
 
    log_level: str = Field(
        default="INFO",
        description="DEBUG | INFO | WARNING | ERROR | CRITICAL.",
    )
 
    json_logs: bool = Field(
        default=False,
        description=(
            "False → human-readable (dev). "
            "True  → JSON for Grafana/Loki (prod)."
        ),
    )
 
 
# ── Singleton ──────────────────────────────────────────────────────────────────
settings = Settings()  # type: ignore[call-arg]
 