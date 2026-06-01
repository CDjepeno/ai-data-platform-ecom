import asyncio
import os

from lang_graph.typing.analytics_state import AnalyticsState, ComparisonResult, PeriodResult
from lang_graph.utils.timer import async_timed_node
from config_env import Config
from utils.logger import get_logger

logger = get_logger(__name__)


async def _run_mf_query(
    metrics: list[str],
    start_time: str,
    end_time: str,
    group_by: list[str] | None = None,
) -> str:
    """Runs a single mf query and returns stdout."""

    cmd = [
        "mf", "query",
        "--metrics", ",".join(metrics),
        "--start-time", start_time,
        "--end-time", end_time,
    ]

    if group_by:
        cmd.extend(["--group-by", ",".join(group_by)])

    process = await asyncio.create_subprocess_exec(
        *cmd,
        cwd=str(Config.DBT_PROJECT_DIR),
        env={**os.environ, "DBT_PROFILES_DIR": str(Config.DBT_PROFILES_DIR)},
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        raise RuntimeError(f"mf query failed: {stdout.decode()}")

    return stdout.decode()


@async_timed_node("execute_comparison")
async def execute_comparison(state: AnalyticsState) -> dict:

    intent = state.get("intent")

    if not intent:
        raise ValueError("Intent missing from state")

    metrics = intent.get("metrics", [])
    group_by = intent.get("group_by", [])
    period_1 = intent.get("period_1")
    period_2 = intent.get("period_2")

    if not period_1 or not period_2:
        raise ValueError("period_1 and period_2 are required for comparison")

    logger.info(
        f"🔄 Comparing {metrics} | "
        f"period_1: {period_1} | "
        f"period_2: {period_2}"
    )

    result_1, result_2 = await asyncio.gather(
        _run_mf_query(metrics, period_1["start_time"], period_1["end_time"], group_by),
        _run_mf_query(metrics, period_2["start_time"], period_2["end_time"], group_by),
    )

    logger.info(f"✅ Period 1 result: {result_1[:100]}")
    logger.info(f"✅ Period 2 result: {result_2[:100]}")

    return {
        "results": ComparisonResult(
            query_type="comparison",
            period_1=PeriodResult(range=period_1, data=result_1),
            period_2=PeriodResult(range=period_2, data=result_2),
        )
    }