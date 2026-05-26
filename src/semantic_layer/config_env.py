from __future__ import annotations

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):
    """Application configuration."""

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── DeepSeek ─────────────────────────────────────────────

    deep_seek_api: str = Field(
        description="DeepSeek API key.",
    )

    base_url_deep_seek_api: str = Field(
        default="https://api.deepseek.com",
        description="DeepSeek API base URL.",
    )

    model_deep_seek: str = Field(
        default="deepseek-v4-flash",
        description="LLM model name.",
    )

    # ── Embedding ────────────────────────────────────────────

    model_embedding: str = Field(
        default="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        description="Embedding model name.",
    )

    # ── dbt ──────────────────────────────────────────────────

    dbt_project_dir: Path = Field(
        default=Path("/app/transformations"),
        description="dbt project directory.",
    )

    dbt_profiles_dir: Path = Field(
        default=Path("/app/.dbt"),
        description="dbt profiles directory.",
    )

    semantic_models_path: Path = Field(
        default=Path(
            "/app/transformations/mart/semantic_models"
        ),
        description="Semantic models directory.",
    )

    metrics_path: Path = Field(
        default=Path(
            "/app/transformations/models/metrics"
        ),
        description="dbt metrics directory.",
    )

    # ── Qdrant ───────────────────────────────────────────────

    qdrant_host: str = Field(
        default="qdrant",
        description="Qdrant hostname.",
    )

    qdrant_port: int = Field(
        default=6333,
        gt=0,
        description="Qdrant port.",
    )

    qdrant_collection: str = Field(
        default="semantic_models",
        description="Qdrant collection name.",
    )

    qdrant_size: int = Field(
        default=1536,
        gt=0,
        description=(
            "Vector embedding dimension stored in Qdrant. "
            "Must match the embedding model output size."
        ),
    )

    # ── Trino ────────────────────────────────────────────────

    trino_host: str = Field(
        description="Trino hostname.",
    )

    trino_user: str = Field(
        description="Trino username.",
    )

    trino_catalog: str = Field(
        description="Trino catalog.",
    )

    trino_schema: str = Field(
        description="Trino schema.",
    )

    trino_port: int = Field(
        default=8080,
        gt=0,
        description="Trino port.",
    )

    # ── OpenAI ───────────────────────────────────────────────

    openai_api_key: str = Field(
        description="OpenAI API key.",
    )

    # ── Valkey ───────────────────────────────────────────────

    valkey_host: str = Field(
        default="valkey",
        description="Valkey hostname.",
    )

    valkey_port: int = Field(
        default=6379,
        gt=0,
        description="Valkey port.",
    )

    valkey_ttl: int = Field(
        default=3600,
        gt=0,
        description="Valkey cache TTL in seconds.",
    )


# ── Singleton ───────────────────────────────────────────────

settings = Settings()  # type: ignore[call-arg]