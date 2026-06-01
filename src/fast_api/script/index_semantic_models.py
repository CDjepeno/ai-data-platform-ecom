import asyncio

from dotenv import load_dotenv

from lang_graph.services import qdrant_service
from qdrant.indexer.factory_indexer import semantic_models_indexer

load_dotenv()


async def main():

    qdrant_service.create_collection()

    await semantic_models_indexer.index_semantic_models()


if __name__ == "__main__":
    asyncio.run(main())
