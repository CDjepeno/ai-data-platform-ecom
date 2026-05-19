
import time

from utils.logger import get_logger
from lang_graph.factory.factory_service import qdrant_service
from lang_graph.factory.factory_service import embedding_service
from lang_graph.typing.analytics_state import AnalyticsState
from qdrant.mapper.qdrant_mapper import QdrantMapper
from lang_graph.utils.timer import async_timed_node

logger = get_logger(__name__)


@async_timed_node(
    "retrieve_context"
)
async def retrieve_context(state: AnalyticsState):

    question = state.get("question")
    
    if not question:

        raise ValueError(
            "Question missing from state"
        ) 

    t0 = time.perf_counter()
    embedding = await embedding_service.embed(question)
    
    t1 = time.perf_counter()
    context = qdrant_service.search(embedding)
    
    t2 = time.perf_counter()
    logger.info(f"embed={t1-t0:.3f}s  qdrant={t2-t1:.3f}s")
    
    results = QdrantMapper.to_semantic_context(
        context
    )

    return {
        "semantic_context": results
    }