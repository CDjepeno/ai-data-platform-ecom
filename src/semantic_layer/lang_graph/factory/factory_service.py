# lang_graph/factory/factory_service.py

from functools import lru_cache
import logging

from qdrant_client import QdrantClient

from lang_graph.services.embedding_service import OpenAIEmbedderAdapter
from lang_graph.services.http_service import HttpxClient
from lang_graph.services.llm_service import LlmService
from lang_graph.services.qdrant_service import QdrantService
from config_env import settings

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_qdrant_service() -> QdrantService:
    logger.info("Initializing QdrantService host=%s", settings.qdrant_host)
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


@lru_cache(maxsize=1)
def get_embedding_service() -> OpenAIEmbedderAdapter:
    # No model download — just instantiates the OpenAI async client
    logger.info("Initializing OpenAIEmbedderAdapter model=%s", settings.model_embedding)
    return OpenAIEmbedderAdapter(
        model_name=settings.model_embedding,
        api_key=settings.openai_api_key,
    )


@lru_cache(maxsize=1)
def get_llm_service() -> LlmService:
    logger.info("Initializing LlmService model=%s", settings.model_deep_seek)
    return LlmService(
        http_client=HttpxClient(),
        model=settings.model_deep_seek,
        api_key=settings.deep_seek_api,
        base_url=settings.base_url_deep_seek_api,
    )