from functools import partial

from langgraph.graph import END, StateGraph
from langgraph.graph import START  # noqa: F401 — kept for clarity

from dependencies import get_embedder, get_qdrant_service
from lang_graph.nodes.build_metricsflow_query import build_metricflow_query
from lang_graph.nodes.check_cache import check_cache
from lang_graph.nodes.execute_query import execute_query
from lang_graph.nodes.format_response import format_response
from lang_graph.nodes.parse_intent import parse_intent
from lang_graph.nodes.retrieve_context import retrieve_context
from lang_graph.nodes.run_mf_query import execute_comparison
from lang_graph.nodes.store_cache import store_cache
from lang_graph.nodes.validate_metrics import validate_metrics
from lang_graph.typing.analytics_state import AnalyticsState
from langgraph.graph.state import CompiledStateGraph  




def route_by_cache(state: AnalyticsState) -> str:
    """Route after cache check — hit goes straight to format, miss continues pipeline."""
    if state.get("cache_hit"):
        return "format_response"

    query_type = state.get("intent", {}).get("query_type", "simple")
    return "execute_comparison" if query_type == "comparison" else "build_query"


_embedder = get_embedder()
_qdrant = get_qdrant_service()

_retrieve_context_node = partial(
    retrieve_context,
    embedder=_embedder,
    qdrant=_qdrant,
)


# ── Graph definition ─────────────────────────────────────────────────────────

def build_analytics_graph() -> CompiledStateGraph:
    """
    Build and compile the analytics LangGraph.
    Call this once at startup — the compiled graph is reused for every request.
    """
    graph = StateGraph(AnalyticsState)

    # Nodes — retrieve_context receives its dependencies via partial
    graph.add_node("retrieve_context", _retrieve_context_node)
    graph.add_node("parse_intent", parse_intent)
    graph.add_node("validate_metrics", validate_metrics)
    graph.add_node("check_cache", check_cache)
    graph.add_node("build_query", build_metricflow_query)
    graph.add_node("execute_query", execute_query)
    graph.add_node("execute_comparison", execute_comparison)
    graph.add_node("store_cache", store_cache)
    graph.add_node("format_response", format_response)

    # Sequential edges
    graph.set_entry_point("retrieve_context")
    graph.add_edge("retrieve_context", "parse_intent")
    graph.add_edge("parse_intent", "validate_metrics")
    graph.add_edge("validate_metrics", "check_cache")

    # Conditional routing after cache check
    graph.add_conditional_edges(
        "check_cache",
        route_by_cache,
        {
            "format_response": "format_response",
            "build_query": "build_query",
            "execute_comparison": "execute_comparison",
        },
    )

    # Convergence back to format
    graph.add_edge("build_query", "execute_query")
    graph.add_edge("execute_query", "store_cache")
    graph.add_edge("execute_comparison", "store_cache")
    graph.add_edge("store_cache", "format_response")
    graph.add_edge("format_response", END)

    return graph.compile()


# ── Compiled singleton — import this in your FastAPI app ─────────────────────
analytics_graph = build_analytics_graph()