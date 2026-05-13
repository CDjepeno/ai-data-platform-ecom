import asyncio
import os

from dotenv import load_dotenv
from openai import AsyncOpenAI

from etl_ecom.db.db_config import Config
from lang_graph.services.embedding_service import OpenAIEmbedderService
from lang_graph.services.qdrant_service import QdrantService
from fast_api.qdrant.indexer.semantic_model_indexer import SemanticModelsIndexer

load_dotenv()

async def main():

    client = AsyncOpenAI()

    embedder = OpenAIEmbedderService(client)

    qdrant = QdrantService()

    qdrant.create_collection()

    indexer = SemanticModelsIndexer(
        embedder=embedder,
        qdrant=qdrant,
    )

    await indexer.index_semantic_models()


if __name__ == "__main__":
    asyncio.run(main())