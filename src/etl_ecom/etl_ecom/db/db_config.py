from __future__ import annotations

from pathlib import Path

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):
    """ETL E-commerce configuration."""

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── PostgreSQL Source ───────────────────────────────────

    postgres_db: str = Field(
        description="PostgreSQL database name.",
    )

    postgres_user: str = Field(
        description="PostgreSQL username.",
    )

    postgres_password: str = Field(
        description="PostgreSQL password.",
    )

    postgres_host: str = Field(
        description="PostgreSQL hostname.",
    )

    postgres_port: int = Field(
        gt=0,
        alias="POSTGRES_PORT",
        description="PostgreSQL port.",
    )

    @computed_field
    @property
    def source_url(self) -> str:
        """
        PostgreSQL connection URL.
        """

        return (
            f"postgresql://{self.postgres_user}:"
            f"{self.postgres_password}@"
            f"{self.postgres_host}:"
            f"{self.postgres_port}/"
            f"{self.postgres_db}"
        )

    # ── DuckDB Warehouse ────────────────────────────────────

    dbt_duckdb_path_dev: Path = Field(
        default=Path("/app/warehouse/dev.duckdb"),
        description="DuckDB development database path.",
    )

    dbt_duckdb_path_prod: Path = Field(
        default=Path("/app/warehouse/prod.duckdb"),
        description="DuckDB production database path.",
    )

    # ── Iceberg / Nessie ────────────────────────────────────

    nessie_uri: str = Field(
        description="Nessie catalog URI.",
    )

    iceberg_warehouse: str = Field(
        description="Iceberg warehouse location.",
    )

    # ── MinIO / S3 ──────────────────────────────────────────

    minio_endpoint: str = Field(
        validation_alias="WAREHOUSE_ENDPOINT",
        description="MinIO endpoint URL.",
    )

    minio_root_user: str = Field(
        validation_alias="AWS_ACCESS_KEY_ID",
        description="MinIO root username.",
    )

    minio_root_password: str = Field(
        validation_alias="AWS_SECRET_ACCESS_KEY",
        description="MinIO root password.",
    )

    minio_bucket: str = Field(
        description="MinIO bucket name.",
    )

    minio_region: str = Field(
        default="gra",
        description="S3-compatible storage region.",
    )

    minio_secure: bool = Field(
        default=False,
        description="Enable HTTPS connection to MinIO.",
    )


# ── Singleton ───────────────────────────────────────────────

settings = Settings()  # type: ignore[call-arg]
