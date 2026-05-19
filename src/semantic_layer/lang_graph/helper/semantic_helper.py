


from lang_graph.typing.analytics_state import SemanticContext


def extract_metric_names(context: SemanticContext) -> list[str]:
    """
    Extracts metric names from the semantic context.
    Reads from context["metrics"] which contains MetricPayloadDTO dicts.
    """
    return [
        metric["metric_name"]
        for metric in context.get("metrics", [])
        if metric.get("metric_name")
    ]


def extract_dimension_names(context: SemanticContext) -> list[str]:
    """
    Extracts dimension names from the semantic context.
    Reads from context["models"] which contains SemanticModelPayloadDTO dicts.
    """
    names = []
    for model in context.get("models", []):
        for dimension in model.get("dimensions", []):
            name = dimension.get("name", "")
            if name:
                names.append(name)
    return names
