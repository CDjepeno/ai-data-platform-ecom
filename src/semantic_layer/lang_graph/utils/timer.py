import time
from functools import wraps
from prometheus_client import Histogram
from utils.logger import get_logger

logger = get_logger(__name__)

# Declared once at module level
langgraph_node_duration = Histogram(
    "langgraph_node_duration_seconds",
    "Duration of LangGraph nodes in seconds",
    labelnames=["node_name"],
)


def async_timed_node(node_name: str):

    def decorator(func):

        @wraps(func)
        async def wrapper(*args, **kwargs):

            start = time.perf_counter()
            logger.info(f"⏳ START NODE: {node_name}")

            try:
                result = await func(*args, **kwargs)
                duration = time.perf_counter() - start

                # ✅ Log + Prometheus metric at the same time
                langgraph_node_duration.labels(
                    node_name=node_name
                ).observe(duration)

                logger.info(f"✅ END NODE: {node_name} ({duration:.2f}s)")
                return result

            except Exception as e:
                duration = time.perf_counter() - start
                logger.error(f"❌ ERROR NODE: {node_name} ({duration:.2f}s): {e}")
                raise

        return wrapper

    return decorator