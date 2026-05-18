import time
from functools import wraps
from utils.logger import get_logger

logger = get_logger(__name__)


def async_timed_node(node_name: str):

    def decorator(func):

        @wraps(func)
        async def wrapper(*args, **kwargs):

            start = time.perf_counter()

            logger.info(
                f"⏳ START NODE: {node_name}"
            )

            result = await func(
                *args,
                **kwargs
            )

            duration = (
                time.perf_counter()
                - start
            )

            logger.info(
                f"✅ END NODE: {node_name} "
                f"({duration:.2f}s)"
            )

            return result

        return wrapper

    return decorator