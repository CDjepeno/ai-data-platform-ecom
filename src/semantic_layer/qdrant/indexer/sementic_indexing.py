from lang_graph.factory.factory_service import get_embedding_service
from qdrant.indexer.metric_indexer import MetricIndexer
from qdrant.indexer.semantic_model_indexer import SemanticModelsIndexer
from lang_graph.services import qdrant_service
from lang_graph.factory.factory_service import get_qdrant_service
from utils.logger import get_logger

logger = get_logger(__name__)


async def run_semantic_indexing():

    logger.info("🧠 Starting semantic indexing")

    qdrant = get_qdrant_service()
    qdrant.create_collection()

    semantic_indexer = SemanticModelsIndexer(
        embedder=get_embedding_service(),
        qdrant=qdrant,
    )

    metric_indexer = MetricIndexer(
        embedder=get_embedding_service(),
        qdrant=get_qdrant_service(),
    )

    await semantic_indexer.index_semantic_models()

    await metric_indexer.index_metrics()

    logger.info("✅ Semantic indexing completed")
