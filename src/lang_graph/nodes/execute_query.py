import os
import subprocess

from dotenv import load_dotenv

from etl_ecom.db.db_config import Config
from lang_graph.typing.analytics_state import AnalyticsState
from etl_ecom.utils.logger import get_logger


logger = get_logger(__name__)

load_dotenv()


def execute_query(state: AnalyticsState):
    
    metric_flow_query = state.get("metricflow_query")
    
    if not metric_flow_query:
        raise ValueError(
            "Metricflow query missing from state"
        )
    
    logger.info(
        f"🚀 Running MetricFlow from: {Config.DBT_PROJECT_DIR}"
    )
    
    env = os.environ.copy()
    
    env["DBT_PROFILES_DIR"] = os.path.expanduser(
        Config.DBT_PROFILES_DIR
    )

    result = subprocess.run(
        metric_flow_query,
        capture_output=True,
        text=True,
        cwd=Config.DBT_PROJECT_DIR,
        env=env
    )
    
    logger.info(
        f"📊 MetricFlow stdout:\n{result.stdout}"
    )

    if result.stderr:
        logger.error(
            f"❌ MetricFlow stderr:\n{result.stderr}"
        )

    if result.returncode != 0:
        raise Exception(result.stderr)

    return {
        "results": result.stdout
    }