# src/semantic_layer/lang_graph/nodes/retrieve_context.py

from lang_graph.typing.analytics_state import AnalyticsState
from lang_graph.services.embedding_service import EmbedderPort
from lang_graph.services.qdrant_service import QdrantService
from lang_graph.utils.timer import async_timed_node
from shared.mapper.qdrant_mapper import QdrantMapper
from utils.logger import get_logger

logger = get_logger(__name__)


@async_timed_node("retrieve_context")
async def retrieve_context(
    state: AnalyticsState,
    embedder: EmbedderPort,
    qdrant: QdrantService,
) -> dict:
    """
    Retrieve semantic context for the given question.
    Raises explicitly typed exceptions so LangGraph can handle
    each failure mode differently upstream.
    """
    question = state.get("question")

    if not question:
        raise ValueError("Question is missing from state")

    # ── Step 1: embed the question ───────────────────────────────────────────
    try:
        embedding = await embedder.embed(question)
    except Exception as exc:
        # Wraps any SentenceTransformer / model failure with context
        logger.exception("Embedding step failed for question: %r", question[:80])
        raise RuntimeError("retrieve_context failed at embedding step") from exc

    if not embedding:
        raise ValueError(
            "Embedder returned an empty vector for question: %r" % question
        )

    logger.info("Embedding done — dimension=%d", len(embedding))

    # ── Step 2: search Qdrant ────────────────────────────────────────────────
    try:
        context = qdrant.search(embedding)
    except Exception as exc:
        logger.exception("Qdrant search failed — embedding dimension=%d", len(embedding))
        raise RuntimeError("retrieve_context failed at Qdrant search step") from exc

    logger.info("Qdrant returned %d points", len(context.points))

    # ── Step 3: map results ──────────────────────────────────────────────────
    try:
        results = QdrantMapper.to_semantic_context(context)
    except Exception as exc:
        logger.exception("Mapping failed — raw context: %s", context)
        raise RuntimeError("retrieve_context failed at mapping step") from exc

    logger.debug("Semantic context mapped successfully: %s", results)

    return {"semantic_context": results}