from openai import AsyncOpenAI

from qdrant.indexer.semantic_model_indexer import SemanticModelsIndexer
from lang_graph.factory.factory_service import qdrant_service
from lang_graph.services.embedding_service import OpenAIEmbedderService


client = AsyncOpenAI()

embedder = OpenAIEmbedderService(client)

semantic_models_indexer = SemanticModelsIndexer(
        embedder=embedder,
        qdrant=qdrant_service,
    )