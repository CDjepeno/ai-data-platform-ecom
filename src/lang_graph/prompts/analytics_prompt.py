from lang_graph.typing.analytics_state import SemanticContext


def build_analytics_prompt(
    question: str,
    context: SemanticContext,
) -> str:
    
    metrics = context.get("metrics", [])

    dimensions = context.get("dimensions", [])

    return f"""
    You are an analytics assistant.

    Available metrics:
    {metrics}

    Available dimensions:
    {dimensions}

    User question:
    {question}

    Return ONLY valid JSON. 

    Expected format:

    {{
    "metrics": ["metric_name"],
    "dimensions": ["dimension_name"],
    "time_dimension": null
    }}
    """