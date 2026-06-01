import json
from lang_graph.typing.analytics_state import AnalyticsState
from lang_graph.utils.timer import async_timed_node
from shared.factory.factory_shared import redis_service
from utils.logger import get_logger

logger = get_logger(__name__)


@async_timed_node("check_cache")
async def check_cache(state: AnalyticsState) -> dict:

    intent = state.get("intent")

    if not intent:
        return {"cache_hit": False}

    key = redis_service.build_intent_key(dict(intent))
    cached = await redis_service.get(key)
    if cached:
        return {"cache_hit": True, "results": json.loads(cached)}

    return {"cache_hit": False}