from lang_graph.typing.analytics_state import AnalyticsState
from lang_graph.utils.timer import async_timed_node


@async_timed_node(
    "build_metricflow_query"
)
async def build_metricflow_query(state: AnalyticsState):

    intent = state.get("intent")

    if not intent:
        raise ValueError(
            "Intent missing from state"
        )

    metrics = intent.get("metrics")

    if not metrics:
        raise ValueError(
            "No metrics provided"
        )

    cmd = [
        "mf",
        "query",
        "--metrics",
        ",".join(metrics),
        "--csv", "/tmp/mf_result.csv",
    ]

    group_by = intent.get("group_by")

    if group_by:
        cmd.extend([
            "--group-by",
            ",".join(group_by)
        ])

    where = intent.get("where")

    if where:
        cmd.extend([
            "--where",
            where
        ])

    return {
        "metricflow_query": cmd
    }