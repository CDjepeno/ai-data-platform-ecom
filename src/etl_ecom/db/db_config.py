from pathlib import Path

from dotenv import load_dotenv
import os


BASE_DIR = Path(__file__).resolve().parents[3]

env_path = BASE_DIR / "docker" / ".env"

load_dotenv(env_path)

# Validation après chargement
def get_env(var: str) -> str:
    value = os.getenv(var)
    if not value:
        raise ValueError(f"{var} is not set")
    return value


class Config:
    # =========================
    # SOURCE (Postgres)
    # =========================
    SOURCE_URL = (
        f"postgresql://{get_env('POSTGRES_USER')}:"
        f"{get_env('POSTGRES_PASSWORD')}@"
        f"{get_env('POSTGRES_HOST')}:"
        f"{get_env('POSTGRES_PORT')}/"
        f"{get_env('POSTGRES_DB')}"
    )

    # =========================
    # WAREHOUSE (DuckDB local)
    # =========================
    DUCKDB_PATH = os.getenv("DUCKDB_PATH", "warehouse.duckdb")

    # =========================
    # MINIO (S3 compatible)
    # =========================
    MINIO_ENDPOINT = get_env("MINIO_ENDPOINT")  # ex: http://localhost:9000
    MINIO_ROOT_USER = get_env("MINIO_ROOT_USER")
    MINIO_ROOT_PASSWORD = get_env("MINIO_ROOT_PASSWORD")
    MINIO_BUCKET = get_env("MINIO_BUCKET")

    # optionnel mais utile
    MINIO_SECURE = os.getenv("MINIO_SECURE", "false").lower() == "true"


# Debug (optionnel)
print("SOURCE_URL:", Config.SOURCE_URL)
print("DUCKDB_PATH:", Config.DUCKDB_PATH)
print("MINIO_ENDPOINT:", Config.MINIO_ENDPOINT)