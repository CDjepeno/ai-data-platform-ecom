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
  * "comparison" → compares two periods

- For time periods, use ONLY these values for "relative_period":
  * "last_7_days"   → last 7 days
  * "last_30_days"  → last 30 days
  * "last_90_days"  → last 90 days
  * "this_month"    → current month
  * "last_month"    → previous month
  * "this_year"     → current year
  * "last_year"     → previous year
  * "ytd"           → year to date
  * "custom_days"   → use with n_days (e.g. "last 40 days" → relative_period: "custom_days", n_days: 40)
  * "all_time"      → no filter (user says "total", "overall", "since beginning")
  * null            → use absolute dates (start_time/end_time provided directly)

- DEFAULT: if no period mentioned → use "this_month"
- NEVER calculate dates yourself — use relative_period instead
- Return ONLY valid JSON, no explanation, no markdown

For a SIMPLE query:
{{
    "query_type": "simple",
    "metrics": ["metric_name"],
    "group_by": [],
    "start_time": null,
    "end_time": null,
    "relative_period": "this_month",
    "n_days": null,
    "where": null,
    "period_1": null,
    "period_2": null
}}

For a SIMPLE query with custom days:
{{
    "query_type": "simple",
    "metrics": ["metric_name"],
    "group_by": [],
    "start_time": null,
    "end_time": null,
    "relative_period": "custom_days",
    "n_days": 40,
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
    "relative_period": null,
    "n_days": null,
    "where": null,
    "period_1": {{"start_time": "{first_day_current_month}", "end_time": "{today.strftime('%Y-%m-%d')}"}},
    "period_2": {{"start_time": "{first_day_last_month}", "end_time": "{last_day_last_month}"}}
}}
"""