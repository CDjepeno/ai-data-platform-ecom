from langgraph.graph import END
from langgraph.graph import StateGraph

from lang_graph.nodes.build_metricsflow_query import build_metricflow_query
from lang_graph.nodes.execute_query import execute_query
from lang_graph.nodes.format_response import format_response
from lang_graph.nodes.parse_intent import parse_intent
from lang_graph.nodes.retrieve_context import retrieve_context
from lang_graph.nodes.validate_metrics import validate_metrics
from lang_graph.typing.analytics_state import AnalyticsState
from lang_graph.nodes.generate_response import generate_response


graph = StateGraph(AnalyticsState)

graph.add_node(
    "retrieve_context",
    retrieve_context,
)

graph.add_node(
    "parse_intent",
    parse_intent,
)

graph.add_node(
    "validate_metrics",
    validate_metrics,
)

graph.add_node(
    "build_query",
    build_metricflow_query,
)

graph.add_node(
    "execute_query",
    execute_query,
)

graph.add_node(
    "format_response",
    format_response,
)

graph.add_node(
    "generate_response",
    generate_response,
)

graph.set_entry_point(
    "retrieve_context"
)

graph.add_edge(
    "retrieve_context",
    "parse_intent",
)

graph.add_edge(
    "parse_intent",
    "validate_metrics",
)

graph.add_edge(
    "validate_metrics",
    "build_query",
)

graph.add_edge(
    "build_query",
    "execute_query",
)

graph.add_edge(
    "execute_query",
    "format_response",
)

graph.add_edge(
    "format_response",
    "generate_response",
)

graph.add_edge(
    "generate_response",
    END
)

analytics_graph = graph.compile()