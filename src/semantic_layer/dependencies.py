
from functools import lru_cache

from qdrant_client import QdrantClient

from lang_graph.services.embedding_service import BGEFrEnEmbedderAdapter, EmbedderPort
from lang_graph.services.qdrant_service import QdrantService
from config_env import Config


@lru_cache(maxsize=1)
def get_embedder() -> EmbedderPort:
    """
    Single embedder instance for the entire process.
    lru_cache guarantees the model is loaded exactly once —
    whether called from indexing, retrieval, or FastAPI routes.
    """
    return BGEFrEnEmbedderAdapter(
        model_name=Config.MODEL_EMBEDDING,
        device="cpu",
    )


@lru_cache(maxsize=1)
def get_qdrant_service() -> QdrantService:
    """Single QdrantService instance for the entire process."""
    return QdrantService(
        host=Config.QDRANT_HOST,
        port=Config.QDRANT_PORT,
        size=Config.QDRANT_SIZE,
        collection_name=Config.QDRANT_COLLECTION,
        qdrant_client=QdrantClient(
            host=Config.QDRANT_HOST,
            port=Config.QDRANT_PORT,
        ),
    )