
from openai import AsyncOpenAI

from lang_graph.services.embedding_service import OpenAIEmbedderService
from lang_graph.services.http_service import HttpxClient
from lang_graph.services.llm_service import LlmService
from lang_graph.services.qdrant_service import (
    QdrantService,
)
from config_env import Config

qdrant_service = QdrantService(
    host=Config.QDRANT_HOST,
    port=Config.QDRANT_PORT,
    collection_name=Config.QDRANT_COLLECTION,
)

embedding_service = OpenAIEmbedderService(
    model=Config.MODEL_EMBEDDING, client=AsyncOpenAI(api_key=Config.OPENAI_API_KEY)
)

llm_service = LlmService(
    http_client=HttpxClient(),
    model=Config.MODEL_DEEP_SEEK,
    api_key=Config.DEEP_SEEK_API,
    base_url=Config.BASE_URL_DEEP_SEEK_API,
)
