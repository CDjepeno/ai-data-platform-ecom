
from functools import lru_cache

from qdrant_client import QdrantClient

from lang_graph.services.embedding_service import OpenAIEmbedderAdapter, EmbedderPort
from lang_graph.services.qdrant_service import QdrantService
from config_env import settings



@lru_cache(maxsize=1)
def get_embedder() -> EmbedderPort:
    """
    Single embedder instance for the entire process.
    lru_cache guarantees the model is loaded exactly once —
    whether called from indexing, retrieval, or FastAPI routes.
    """
    return OpenAIEmbedderAdapter(
        model_name=settings.model_embedding,
        api_key=settings.openai_api_key
    )


@lru_cache(maxsize=1)
def get_qdrant_service() -> QdrantService:
    """Single QdrantService instance for the entire process."""
    return QdrantService(
        host=settings.qdrant_host,
        port=settings.qdrant_port,
        size=settings.qdrant_size,
        collection_name=settings.qdrant_collection,
        qdrant_client=QdrantClient(
            host=settings.qdrant_host,
            port=settings.qdrant_port,
        ),
    )