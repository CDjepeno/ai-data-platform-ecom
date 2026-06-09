from __future__ import annotations

from pathlib import Path

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[4]



_env_local = BASE_DIR / "docker" / ".env.local"
_env_default = BASE_DIR / "docker" / ".env"
ENV_FILE = _env_local if _env_local.exists() else _env_default

print(f"BASE_DIR: {BASE_DIR}")
print(f"env_local: {_env_local}")
print(f"env_local exists: {_env_local.exists()}")
print(f"env_default: {_env_default}")
print(f"env_default exists: {_env_default.exists()}")
print(f"Using ENV_FILE: {ENV_FILE}")

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

    postgres_sslmode: str = Field(
        default="disable",
        description="PostgreSQL SSL mode (disable for local, require for preprod).",
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

    # ── Semantic Layer ────────────────────────────────────
    semantic_layer_url: str = Field(
        description="Semantic layer base URL (e.g. http://semantic-layer:8001).",
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
        validation_alias="MINIO_ENDPOINT",
        description="MinIO endpoint URL.",
    )

    minio_root_user: str = Field(
        validation_alias="MINIO_ROOT_USER",
        description="MinIO root username.",
    )

    minio_root_password: str = Field(
        validation_alias="MINIO_ROOT_PASSWORD",
        description="MinIO root password.",
    )

    # Bucket-user credentials used by Nessie / pyiceberg for catalog S3 access.
    # These are distinct from the MinIO admin credentials above.
    aws_access_key_id: str = Field(
        validation_alias="AWS_ACCESS_KEY_ID",
        description="S3 access key for Iceberg catalog (Nessie → MinIO).",
    )

    aws_secret_access_key: str = Field(
        validation_alias="AWS_SECRET_ACCESS_KEY",
        description="S3 secret key for Iceberg catalog (Nessie → MinIO).",
    )

    minio_bucket: str = Field(
        description="MinIO bucket name.",
    )

    minio_region: str = Field(
        description="S3-compatible storage region.",
    )

    minio_secure: bool = Field(
        default=False,
        description="Enable HTTPS connection to MinIO.",
    )


# ── Singleton ───────────────────────────────────────────────

settings = Settings()  # type: ignore[call-arg]
