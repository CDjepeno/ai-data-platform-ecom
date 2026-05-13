from openai import AsyncOpenAI

from lang_graph.services.embedding_service import OpenAIEmbedderService
from fast_api.qdrant.indexer.metric_indexer import MetricIndexer
from fast_api.qdrant.indexer.semantic_model_indexer import SemanticModelsIndexer
from lang_graph.services.qdrant_service import QdrantService
from etl_ecom.utils.logger import get_logger


logger = get_logger(__name__)


async def run_semantic_indexing():

    logger.info(
        "🧠 Starting semantic indexing"
    )

    client = AsyncOpenAI()

    embedder = OpenAIEmbedderService(
        client
    )

    qdrant = QdrantService()

    qdrant.create_collection()

    semantic_indexer = SemanticModelsIndexer(
        embedder=embedder,
        qdrant=qdrant,
    )

    metric_indexer = MetricIndexer(
        embedder=embedder,
        qdrant=qdrant,
    )

    await semantic_indexer.index_semantic_models()

    await metric_indexer.index_metrics()

    logger.info(
        "✅ Semantic indexing completed"
    )
