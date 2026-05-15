from pathlib import Path

from dotenv import load_dotenv
import os

load_dotenv()


class Config:

    # =========================
    # DeepSeek
    # =========================
    DEEP_SEEK_API = os.getenv("DEEP_SEEK_API", "xxxx")
    BASE_URL_DEEP_SEEK_API = os.getenv("BASE_URL_DEEP_SEEK_API", "https://api.deepseek.com")
    MODEL_DEEP_SEEK = os.getenv("MODEL_DEEP_SEEK", "deepseek-v4-pro")
    
    # =========================
    # Embedding
    # =========================
    MODEL_EMBEDDING = os.getenv("MODEL_EMBEDDING", "text-embedding-3-small")

    # =========================
    # dbt
    # =========================
    DBT_PROJECT_DIR = Path(os.getenv("DBT_PROJECT_DIR", "app/transformation"))
    DBT_PROFILES_DIR = DBT_PROJECT_DIR / ".dbt"
    
    # =========================
    # qdrant
    # =========================
    QDRANT_HOST = os.getenv("QDRANT_HOST", "qdrant")    
    QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6334"))
    QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "semantic_models")
    
    # =========================
    # Trino
    # =========================
    TRINO_HOST = os.getenv("TRINO_HOST")  
    TRINO_USER = os.getenv("TRINO_USER")
    TRINO_CATALOG = os.getenv("TRINO_CATALOG")
    TRINO_SCHEMA = os.getenv("TRINO_SCHEMA")  
    TRINO_PORT = os.getenv("TRINO_PORT")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    