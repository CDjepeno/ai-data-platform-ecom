


from lang_graph.typing.analytics_state import SemanticContext


def extract_metric_names(
    context: SemanticContext,
) -> list[str]:

    return [
        metric["metric_name"]
        for metric in context["metrics"]
    ]


def extract_dimension_names(
    context: SemanticContext,
) -> list[str]:

    return [
        dimension["name"]
        for dimension in context["dimensions"]
    ]