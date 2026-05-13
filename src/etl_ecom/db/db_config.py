from pathlib import Path

from dotenv import load_dotenv
import os


BASE_DIR = Path(__file__).resolve().parents[3]

env_path = BASE_DIR / "docker" / ".env"

load_dotenv(env_path)

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
    
      
    POSTGRES_DB= os.getenv("POSTGRES_DB")
    POSTGRES_USER = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_HOST = os.getenv("POSTGRES_HOST")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT")

    # =========================
    # WAREHOUSE (DuckDB local)
    # =========================
    DBT_DUCKDB_PATH_DEV = os.getenv("DBT_DUCKDB_PATH_DEV", "warehouse.duckdb")
    
    # =========================
    # Iceberg / Nessie
    # =========================

    NESSIE_URI = get_env("NESSIE_URI")
    ICEBERG_WAREHOUSE = get_env("ICEBERG_WAREHOUSE")

    # =========================
    # MINIO (S3 compatible)
    # =========================
    MINIO_ENDPOINT = get_env("MINIO_ENDPOINT")  
    MINIO_ROOT_USER = get_env("MINIO_ROOT_USER")
    MINIO_ROOT_PASSWORD = get_env("MINIO_ROOT_PASSWORD")
    MINIO_BUCKET = get_env("MINIO_BUCKET")

    # optional but useful
    MINIO_SECURE = os.getenv("MINIO_SECURE", "false").lower() == "true"

    # =========================
    # Trino
    # =========================
    TRINO_HOST = get_env("TRINO_HOST")  
    TRINO_USER = get_env("TRINO_USER")
    TRINO_CATALOG = get_env("TRINO_CATALOG")
    TRINO_SCHEMA = get_env("TRINO_SCHEMA")  
    TRINO_PORT = get_env("TRINO_PORT")
    OPENAI_API_KEY = get_env("OPENAI_API_KEY")
    
    
    # =========================
    # DeepSeek
    # =========================
    DEEP_SEEK_API = os.getenv("DEEP_SEEK_API")
    BASE_URL_DEEP_SEEK_API = os.getenv("BASE_URL_DEEP_SEEK_API")
    MODEL_DEEP_SEEK = os.getenv("MODEL_DEEP_SEEK", "deepseek-v4-pro")
    
    DBT_PROJECT_DIR = os.getenv("DBT_PROJECT_DIR")
    
    # =========================
    # dbt
    # =========================
    BASE_DIR = Path(__file__).resolve().parents[2]
    DBT_PROJECT_DIR = BASE_DIR / os.getenv("DBT_PROJECT_DIR", "src/etl_ecom/transformation")
    DBT_PROFILES_DIR = DBT_PROJECT_DIR / ".dbt"
    
    
# Debug (optional)
# print("SOURCE_URL:", Config.SOURCE_URL)
# print("DBT_DUCKDB_PATH_DEV:", Config.DBT_DUCKDB_PATH_DEV)
# print("MINIO_ENDPOINT:", Config.MINIO_ENDPOINT)