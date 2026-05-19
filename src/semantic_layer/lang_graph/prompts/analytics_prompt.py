from datetime import datetime, timedelta

from lang_graph.typing.analytics_state import SemanticContext
from lang_graph.helper.semantic_helper import extract_dimension_names, extract_metric_names

def build_analytics_prompt(
    question: str,
    context: SemanticContext,
) -> str:

    metrics = extract_metric_names(context)
    dimensions = extract_dimension_names(context)
    today = datetime.now()
    first_day_current_month = today.replace(day=1).strftime('%Y-%m-%d')
    first_day_last_month = (today.replace(day=1) - timedelta(days=1)).replace(day=1).strftime('%Y-%m-%d')
    last_day_last_month = (today.replace(day=1) - timedelta(days=1)).strftime('%Y-%m-%d')

    return f"""
You are an analytics assistant for an ecommerce platform.
Today's date is {today.strftime('%Y-%m-%d')}.

Available metrics:
{", ".join(metrics) if metrics else "none"}

Available dimensions:
{", ".join(dimensions) if dimensions else "none"}

User question:
{question}

Instructions:
- Choose ONLY metrics from the available metrics list above
- Choose ONLY dimensions from the available dimensions list above
- Detect the query type:
  * "simple"     → single time period or no time filter
  * "comparison" → compares two periods ("more than last month", "vs last year", "did we grow")

- Convert natural language dates to ISO format:
  * "this month"  → start_time: {first_day_current_month}, end_time: {today.strftime('%Y-%m-%d')}
  * "last month"  → start_time: {first_day_last_month}, end_time: {last_day_last_month}
  * "this year"   → start_time: {today.strftime('%Y')}-01-01, end_time: {today.strftime('%Y-%m-%d')}

- Return ONLY valid JSON, no explanation, no markdown

For a SIMPLE query:
{{
    "query_type": "simple",
    "metrics": ["metric_name"],
    "group_by": [],
    "start_time": "2026-05-01",
    "end_time": "2026-05-19",
    "where": null,
    "period_1": null,
    "period_2": null
}}

For a COMPARISON query:
{{
    "query_type": "comparison",
    "metrics": ["metric_name"],
    "group_by": [],
    "start_time": null,
    "end_time": null,
    "where": null,
    "period_1": {{"start_time": "{first_day_current_month}", "end_time": "{today.strftime('%Y-%m-%d')}"}},
    "period_2": {{"start_time": "{first_day_last_month}", "end_time": "{last_day_last_month}"}}
}}
"""