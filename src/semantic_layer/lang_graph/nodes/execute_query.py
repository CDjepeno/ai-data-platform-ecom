import os
import subprocess

from lang_graph.typing.analytics_state import AnalyticsState


async def execute_query(state: AnalyticsState):

    metricflow_query = state.get("metricflow_query")
    
    if metricflow_query is None:
        raise ValueError("metricflow_query is required")

    result = subprocess.run(
        metricflow_query,
        cwd="/app/transformation",
        env={
            **os.environ,
            "DBT_PROFILES_DIR": "/app/.dbt"
        },
        capture_output=True,
        text=True
    )

    return {
        "results": {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }
    }
    
    
    
    