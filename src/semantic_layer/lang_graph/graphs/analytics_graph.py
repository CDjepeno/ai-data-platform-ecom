from langgraph.graph import END, START
from langgraph.graph import StateGraph

from lang_graph.nodes.build_metricsflow_query import build_metricflow_query
from lang_graph.nodes.execute_query import execute_query
from lang_graph.nodes.format_response import format_response
from lang_graph.nodes.parse_intent import parse_intent
from lang_graph.nodes.retrieve_context import retrieve_context
from lang_graph.nodes.validate_metrics import validate_metrics
from lang_graph.typing.analytics_state import AnalyticsState
from lang_graph.nodes.run_mf_query import execute_comparison


def route_by_query_type(state: AnalyticsState) -> str:
    intent = state.get("intent", {})
    query_type = intent.get("query_type", "simple")

    if query_type == "comparison":
        return "execute_comparison"
    return "build_query"



graph = StateGraph(
    AnalyticsState
)
graph.add_node("retrieve_context", retrieve_context)
graph.add_node("parse_intent", parse_intent)
graph.add_node("validate_metrics", validate_metrics)
graph.add_node("build_query", build_metricflow_query)
graph.add_node("execute_query", execute_query)
graph.add_node("execute_comparison", execute_comparison)
graph.add_node("format_response", format_response)

# ✅ Sequential
graph.set_entry_point("retrieve_context")
graph.add_edge("retrieve_context", "parse_intent")
graph.add_edge("parse_intent", "validate_metrics")
graph.add_conditional_edges(
    "validate_metrics",
    route_by_query_type,
    {
        "build_query": "build_query",
        "execute_comparison": "execute_comparison",
    }
)

graph.add_edge("build_query", "execute_query")
graph.add_edge("execute_query", "format_response")
graph.add_edge("execute_comparison", "format_response")
graph.add_edge("format_response", END)

analytics_graph = graph.compile()