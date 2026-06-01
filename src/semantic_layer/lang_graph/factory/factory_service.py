
import httpx
from numpy import size
from openai import AsyncOpenAI
from qdrant_client import QdrantClient

from lang_graph.services.embedding_service import BGEFrEnEmbedderAdapter
from lang_graph.services.http_service import HttpxClient
from lang_graph.services.llm_service import LlmService
from lang_graph.services.qdrant_service import (
    QdrantService,
)
from config_env import Config


qdrant_service = QdrantService(
    host=Config.QDRANT_HOST,
    port=Config.QDRANT_PORT,
    size= Config.QDRANT_SIZE,
    collection_name=Config.QDRANT_COLLECTION,
    qdrant_client= QdrantClient(
        port= Config.QDRANT_PORT,
        host=Config.QDRANT_HOST
    )
)

embedding_service = BGEFrEnEmbedderAdapter(
    model_name=Config.MODEL_EMBEDDING,
)

llm_service = LlmService(
    http_client=HttpxClient(),
    model=Config.MODEL_DEEP_SEEK,
    api_key=Config.DEEP_SEEK_API,
    base_url=Config.BASE_URL_DEEP_SEEK_API,
)
