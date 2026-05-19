import asyncio

from lang_graph.typing.analytics_state import AnalyticsState
from lang_graph.utils.timer import async_timed_node
from trino.dbapi import connect

_trino_conn = connect(
    host="trino",
    port=8080,
    http_scheme="http",
)


@async_timed_node(
    "execute_query"
)
@async_timed_node("execute_query")
async def execute_query(state: AnalyticsState):
    
    sql = state.get("metricflow_query_sql")  # SQL généré directement
    
    cursor = await asyncio.to_thread(
        lambda: _trino_conn.cursor()
    )
    
    await asyncio.to_thread(cursor.execute, sql)
    rows = await asyncio.to_thread(cursor.fetchall)
    
    return {"results": rows}
    
    
    
    