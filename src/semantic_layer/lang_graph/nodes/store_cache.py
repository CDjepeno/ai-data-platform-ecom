# lang_graph/nodes/store_cache.py

import json
from lang_graph.typing.analytics_state import AnalyticsState
from lang_graph.utils.timer import async_timed_node
from shared.factory.factory_shared import redis_service
from utils.logger import get_logger

logger = get_logger(__name__)


@async_timed_node("store_cache")
async def store_cache(state: AnalyticsState) -> dict:
    """
    Stores the query result in Valkey after a successful execution.
    Keyed by intent so identical intents hit the cache next time.
    """

    intent = state.get("intent")
    results = state.get("results")

    if not intent or not results:
        logger.warning("⚠️ Cannot cache — missing intent or results")
        return {}

    key = redis_service.build_intent_key(dict(intent))

    await redis_service.set(
        key=key,
        value=json.dumps(results),
    )

    logger.info(f"💾 Cached result for key: {key}")
    return {}