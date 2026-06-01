from lang_graph.typing.analytics_state import AnalyticsState
from lang_graph.validator.dimension_exists_validator import DimensionExistsValidator
from lang_graph.validator.duplicate_metric_validator import DuplicateMetricValidator
from lang_graph.validator.empty_metric_validator import EmptyMetricValidator
from lang_graph.validator.fuzzy_metric_validator import FuzzyMetricValidator
from lang_graph.validator.metric_exists_validator import MetricExistsValidator
from lang_graph.validator.metrics_type_validator import MetricsTypeValidator
from lang_graph.validator.required_fields_validator import RequiredFieldsValidator
from lang_graph.utils.timer import async_timed_node


@async_timed_node(
    "validate_metrics"
)
async def validate_metrics(
    state: AnalyticsState,
):

    intent = state.get("intent")

    context = state.get("semantic_context")

    validators = [
        RequiredFieldsValidator(),
        MetricsTypeValidator(),
        DuplicateMetricValidator(),
        EmptyMetricValidator(),
        FuzzyMetricValidator(),
        MetricExistsValidator(),
        DimensionExistsValidator(),
    ]

    for validator in validators:

        intent = validator.validate(
            intent,
            context,
        )

    return {
        "intent": intent
    }