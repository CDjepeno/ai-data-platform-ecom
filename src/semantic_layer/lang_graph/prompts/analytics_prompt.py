from lang_graph.typing.analytics_state import SemanticContext
from lang_graph.helper.semantic_helper import extract_dimension_names, extract_metric_names

def build_analytics_prompt(
    question: str,
    context: SemanticContext,
) -> str:
    
    # ✅ Extrait depuis context["models"] via le DTO
    metrics = extract_metric_names(context)
    dimensions = extract_dimension_names(context)

    return f"""
    You are an analytics assistant for an ecommerce platform.

    Available metrics:
    {", ".join(metrics) if metrics else "none"}

    Available dimensions:
    {", ".join(dimensions) if dimensions else "none"}

    User question:
    {question}

    Instructions:
    - Choose ONLY metrics from the available metrics list above
    - Choose ONLY dimensions from the available dimensions list above  
    - If no dimension is needed, return an empty list
    - Return ONLY valid JSON, no explanation

    Expected format:
    {{
        "metrics": ["metric_name"],
        "dimensions": ["dimension_name"],
        "time_dimension": null
    }}
    """