import asyncio
import os

from lang_graph.typing.analytics_state import AnalyticsState, SimpleResult
from lang_graph.utils.timer import async_timed_node
from utils.logger import get_logger

logger = get_logger(__name__)


@async_timed_node("execute_query")
async def execute_query(state: AnalyticsState) -> dict:
    
    logger.info(f"🔍 Intent: {state.get('intent')}")

    metricflow_query = state.get("metricflow_query")
    
    logger.info(f"🚀 Running: metricflow_query {metricflow_query}")

    if metricflow_query is None:
        raise ValueError("metricflow_query is required")


    process = await asyncio.create_subprocess_exec(
        *metricflow_query,
        cwd="/app/transformations",
        env={**os.environ, "DBT_PROFILES_DIR": "/app/.dbt"},
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    stdout, stderr = await process.communicate()
    
    # ← add logging here before the if
    logger.info(f"📄 stdout: {stdout.decode()}")
    logger.info(f"📄 stderr: {stderr.decode()}")
    logger.info(f"📄 returncode: {process.returncode}")

    if process.returncode != 0:
        logger.error(f"❌ mf query failed: {stderr.decode()}")
        raise RuntimeError(f"mf query failed: {stderr.decode()}")

    logger.info(f"✅ Query result: {stdout.decode()[:200]}")

    return {
        "results": SimpleResult(
            query_type="simple",
            stdout=stdout.decode(),
            stderr=stderr.decode(),
            returncode=process.returncode,
        )
    }